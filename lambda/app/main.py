import json
import urllib.parse
import urllib.request
import boto3
import io
import gzip
import base64
import os
from typing import Tuple

from clickops import ClickOpsEventChecker, CloudTrailEvent
from messenger import Messenger
from delivery_stream import DeliveryStream

s3 = boto3.client("s3")
ssm = boto3.client("ssm")

WEBHOOK_PARAMETER = os.environ["WEBHOOK_PARAMETER"]

DELIVERY_STREAM_NAME = os.environ["DELIVERY_STREAM_NAME"]

EXCLUDED_ACCOUNTS = json.loads(os.environ["EXCLUDED_ACCOUNTS"])
INCLUDED_ACCOUNTS = json.loads(os.environ["INCLUDED_ACCOUNTS"])
EXCLUDED_USERS = json.loads(os.environ["EXCLUDED_USERS"])
INCLUDED_USERS = json.loads(os.environ["INCLUDED_USERS"])
EXCLUDED_SCOPED_ACTIONS = json.loads(os.environ["EXCLUDED_SCOPED_ACTIONS"])
MESSAGE_FORMAT = os.environ["MESSAGE_FORMAT"]
LOG_LEVEL = os.environ["LOG_LEVEL"]

WEBHOOK_URL = None


def get_webhook() -> str:
    global WEBHOOK_URL
    if WEBHOOK_URL is None:
        response = ssm.get_parameter(Name=WEBHOOK_PARAMETER, WithDecryption=True)
        WEBHOOK_URL = response["Parameter"]["Value"]

    return WEBHOOK_URL


def valid_account(key) -> Tuple[bool, str]:
    if len(EXCLUDED_ACCOUNTS) == 0 and len(INCLUDED_ACCOUNTS) == 0:
        return True, f"[VA_ALLOWALL] {key}"

    if any(acc for acc in EXCLUDED_ACCOUNTS if acc in key):
        return False, f"[VA_EXPLICIT_EXCLUDE] {key} in {json.dumps(EXCLUDED_ACCOUNTS)}"

    if len(INCLUDED_ACCOUNTS) == 0:
        return True, f"[VA_IMPLICIT_INCLUDE] {key}"

    if any(acc for acc in INCLUDED_ACCOUNTS if acc in key):
        return True, f"[VA_EXPLICIT_INCLUDE] {key} in {json.dumps(INCLUDED_ACCOUNTS)}"

    return False, f"[VA_IMPLICIT_EXCLUDE] {key} not in {json.dumps(INCLUDED_ACCOUNTS)}"


def valid_user(email) -> Tuple[bool, str]:
    """
    Corey Quinn:billie: 10:21 PM
    Feature idea: ignore ClickOps actions not only by account,
    but also by user identity. "Clicky Pete" probably becomes
    noisy but he also can fire the rest of us...
    """
    if email == "Unknown":
        return True, "[VU_UNKNOWN]"

    if len(EXCLUDED_USERS) == 0 and len(INCLUDED_USERS) == 0:
        return True, f"[VU_ALLOWALL] {email}"

    if email in EXCLUDED_USERS:
        return False, f"[VU_EXPLICIT_EXCLUDE] {email} in {json.dumps(EXCLUDED_USERS)}"

    if len(INCLUDED_USERS) == 0:
        return True, f"[VU_IMPLICIT_INCLUDE] {email}"

    if email in INCLUDED_USERS:
        return True, f"[VU_EXPLICIT_INCLUDE] {email} in {json.dumps(INCLUDED_USERS)}"

    print(f"[VU_IMPLICIT_EXCLUDE] {email} not in {json.dumps(INCLUDED_USERS)}")
    return False


def handler_organizational(event, context) -> None:  # noqa: C901
    """
    This functions processes CloudTrail logs from S3, filters events from the AWS
    Console, and publishes to SNS
    :param event: List of S3 Events
    :param context: AWS Lambda Context Object
    :return: None
    """

    webhook_url = get_webhook()

    messenger = Messenger(format=MESSAGE_FORMAT, webhook=webhook_url)

    delivery_stream = DeliveryStream(
        delivery_stream_name=DELIVERY_STREAM_NAME, fake=True
    )

    for sqs_record in event["Records"]:
        s3_events = json.loads(sqs_record["body"])

        records = s3_events.get("Records", [])

        for record in records:

            # Get the object from the event and show its content type
            bucket = record["s3"]["bucket"]["name"]
            key = urllib.parse.unquote_plus(
                record["s3"]["object"]["key"], encoding="utf-8"
            )

            key_elements = key.split("/")
            if "CloudTrail" not in key_elements:
                continue

            is_valid_account, reason = valid_account(key)

            if not is_valid_account:
                continue

            try:
                response = s3.get_object(Bucket=bucket, Key=key)
                content = response["Body"].read()

                with gzip.GzipFile(fileobj=io.BytesIO(content), mode="rb") as fh:
                    event_json = json.load(fh)

                    for event in event_json["Records"]:

                        event_origin = f"{bucket}/{key}"

                        __handle_event(
                            messenger=messenger,
                            delivery_stream=delivery_stream,
                            event=event,
                            event_origin=event_origin,
                            standalone=False,
                        )

            except Exception as e:
                print(e)
                raise e

    return "Completed"


def handler_standalone(event, context) -> None:
    webhook_url = get_webhook()

    messenger = Messenger(format=MESSAGE_FORMAT, webhook=webhook_url)

    delivery_stream = DeliveryStream(
        delivery_stream_name=DELIVERY_STREAM_NAME, fake=True
    )

    # print(json.dumps(event))

    event_decoded_compressed = base64.b64decode(event["awslogs"]["data"])
    event_uncompressed = gzip.decompress(event_decoded_compressed)
    event_json = json.loads(event_uncompressed)

    for e in event_json["logEvents"]:

        event_origin = f"{event_json['logGroup']}:{event_json['logStream']}\n{event_json['subscriptionFilters']}"  # noqa: E501

        __handle_event(
            messenger=messenger,
            delivery_stream=delivery_stream,
            event=json.loads(e["message"]),
            event_origin=event_origin,
            standalone=True,
        )

    # print(json.dumps(event_json))
    return "Completed"


def __handle_event(
    messenger, delivery_stream, event, event_origin: str, standalone: bool
) -> bool:
    cloudtrail_event = CloudTrailEvent(event)

    is_valid_user, reason = valid_user(cloudtrail_event.user_email)

    if not is_valid_user:
        return

    clickops_checker = ClickOpsEventChecker(cloudtrail_event, EXCLUDED_SCOPED_ACTIONS)

    is_clickops, reason = clickops_checker.is_clickops()

    if is_clickops:
        # TODO exceptions?
        result1 = messenger.send(
            cloudtrail_event.user_email,
            event,
            event_origin=event_origin,
            standalone=standalone,
        )
        if not result1:
            print(f"[ERROR] Message not sent\n\n{json.dumps(event)}")  # noqa: E501
        result2 = delivery_stream.send(event)
        # TODO exceptions?:
        if not result2:
            print(f"[ERROR] Message not delivered\n\n{json.dumps(event)}")  # noqa: E501
        return result1 and result2
    return True
