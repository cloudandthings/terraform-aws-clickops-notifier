import json
import urllib.parse
import urllib.request
import boto3
import io
import gzip
import os
from botocore.vendored import requests
from typing import Tuple

from clickops import ClickOpsEventChecker, CloudTrailEvent


s3 = boto3.client('s3')
ssm = boto3.client('ssm')

WEBHOOK_PARAMETER = os.environ['WEBHOOK_PARAMETER']
EXCLUDED_ACCOUNTS = json.loads(os.environ['EXCLUDED_ACCOUNTS'])
INCLUDED_ACCOUNTS = json.loads(os.environ['INCLUDED_ACCOUNTS'])
EXCLUDED_USERS = json.loads(os.environ['EXCLUDED_USERS'])
INCLUDED_USERS = json.loads(os.environ['INCLUDED_USERS'])
LOG_LEVEL = os.environ['LOG_LEVEL']

WEBHOOK_URL = None


def get_wekbhook() -> str:
    global WEBHOOK_URL
    if WEBHOOK_URL is None:
        response = ssm.get_parameter(Name=WEBHOOK_PARAMETER, WithDecryption=True)
        WEBHOOK_URL = response['Parameter']['Value']

    return WEBHOOK_URL


def send_slack_message(user, event, s3_bucket, s3_key, webhook) -> bool:
    slack_payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":bell: ClickOps Alert :bell:",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Someone is practicing ClickOps in your AWS Account!"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Account Id*\n{event['recipientAccountId']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Region*\n{event['awsRegion']}"
                    }
                ]
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*IAM Action*\n{event['eventSource'].split('.')[0]}:{event['eventName']}"  # noqa: E501
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Principle*\n{user}"
                    }
                ]
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Cloudtrail Bucket*\n{s3_bucket}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Key*\n{s3_key}"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Event*\n```{json.dumps(event, indent=2)}```"
                }
            },
        ]
    }

    response = requests.post(webhook, json=slack_payload)
    if response.status_code != 200:
        return False
    return True


def valid_account(key) -> Tuple[bool, str]:
    if len(EXCLUDED_ACCOUNTS) == 0 and len(INCLUDED_ACCOUNTS) == 0:
        return True, f'[VA_ALLOWALL] {key}'

    if any(acc for acc in EXCLUDED_ACCOUNTS if acc in key):
        return False, f'[VA_EXPLICIT_EXCLUDE] {key} in {json.dumps(EXCLUDED_ACCOUNTS)}'

    if len(INCLUDED_ACCOUNTS) == 0:
        return True, f'[VA_IMPLICIT_INCLUDE] {key}'

    if any(acc for acc in INCLUDED_ACCOUNTS if acc in key):
        return True, f'[VA_EXPLICIT_INCLUDE] {key} in {json.dumps(INCLUDED_ACCOUNTS)}'

    return False, f'[VA_IMPLICIT_EXCLUDE] {key} not in {json.dumps(INCLUDED_ACCOUNTS)}'


def valid_user(email) -> Tuple[bool, str]:
    """
    Corey Quinn:billie: 10:21 PM
    Feature idea: ignore ClickOps actions not only by account,
    but also by user identity. "Clicky Pete" probably becomes
    noisy but he also can fire the rest of us...
    """
    if email == "Unknown":
        return True, '[VU_UNKNOWN]'

    if len(EXCLUDED_USERS) == 0 and len(INCLUDED_USERS) == 0:
        return True, f'[VU_ALLOWALL] {email}'

    if email in EXCLUDED_USERS:
        return False, f'[VU_EXPLICIT_EXCLUDE] {email} in {json.dumps(EXCLUDED_USERS)}'

    if len(INCLUDED_USERS) == 0:
        return True, f'[VU_IMPLICIT_INCLUDE] {email}'

    if email in INCLUDED_USERS:
        return True, f'[VU_EXPLICIT_INCLUDE] {email} in {json.dumps(INCLUDED_USERS)}'

    print(f'[VU_IMPLICIT_EXCLUDE] {email} not in {json.dumps(INCLUDED_USERS)}')
    return False


def handler(event, context) -> None:  # noqa: C901
    """
    This functions processes CloudTrail logs from S3, filters events from the AWS
    Console, and publishes to SNS
    :param event: List of S3 Events
    :param context: AWS Lambda Context Object
    :return: None
    """

    webhook_url = get_wekbhook()

    for sqs_record in event['Records']:
        s3_events = json.loads(sqs_record['body'])

        records = s3_events.get("Records", [])

        for record in records:

            # Get the object from the event and show its content type
            bucket = record['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(
                record['s3']['object']['key'],
                encoding='utf-8')

            key_elements = key.split("/")
            if "CloudTrail" not in key_elements:
                continue

            is_valid_account, reason = valid_account(key)

            if not is_valid_account:
                continue

            try:
                response = s3.get_object(Bucket=bucket, Key=key)
                content = response['Body'].read()

                with gzip.GzipFile(fileobj=io.BytesIO(content), mode='rb') as fh:
                    event_json = json.load(fh)

                    for event in event_json['Records']:
                        cloudtrail_event = CloudTrailEvent(event)

                        is_valid_user, reason = valid_user(cloudtrail_event.user_email)

                        if not is_valid_user:
                            continue

                        clickops_checker = ClickOpsEventChecker(cloudtrail_event)

                        is_clickops, reason = clickops_checker.is_clickops()

                        if is_clickops:
                            if not send_slack_message(
                                    cloudtrail_event.user_email,
                                    event,
                                    s3_bucket=bucket,
                                    s3_key=key,
                                    webhook=webhook_url):
                                print(f"[ERROR] Slack Message not sent\n\n{json.dumps(record)}")  # noqa: E501

                # return response['ContentType']
            except Exception as e:
                print(e)
                raise e

    return "Completed"
