import json
import urllib.parse
import urllib.request
import boto3
import io
import gzip
import base64
import os
from typing import Tuple
import logging

from clickops import ClickOpsEventChecker, CloudTrailEvent
from messenger import Messenger
from delivery_stream import DeliveryStream

LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARN")
logging.getLogger().setLevel(LOG_LEVEL)

WEBHOOK_PARAMETER = os.environ.get("WEBHOOK_PARAMETER", "")
EXCLUDED_ACCOUNTS = json.loads(os.environ.get("EXCLUDED_ACCOUNTS", "[]"))
INCLUDED_ACCOUNTS = json.loads(os.environ.get("INCLUDED_ACCOUNTS", "[]"))
EXCLUDED_USERS = json.loads(os.environ.get("EXCLUDED_USERS", "[]"))
INCLUDED_USERS = json.loads(os.environ.get("INCLUDED_USERS", "[]"))
EXCLUDED_SCOPED_ACTIONS = json.loads(os.environ.get("EXCLUDED_SCOPED_ACTIONS", "[]"))
MESSAGE_FORMAT = os.environ.get("MESSAGE_FORMAT", "slack")

FIREHOSE_DELIVERY_STREAM_NAME = os.environ.get("FIREHOSE_DELIVERY_STREAM_NAME")
if FIREHOSE_DELIVERY_STREAM_NAME == "__NONE__":
    FIREHOSE_DELIVERY_STREAM_NAME = None

s3 = boto3.client("s3")
ssm = boto3.client("ssm")

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

    logging.info(f"[VU_IMPLICIT_EXCLUDE] {email} not in {json.dumps(INCLUDED_USERS)}")
    return False


def handler_organizational(event, context) -> None:  # noqa: C901
    """
    This functions processes CloudTrail logs from S3, filters events from the AWS
    Console, and publishes to SNS
    :param event: List of S3 Events
    :param context: AWS Lambda Context Object
    :return: None
    """
    logging.info(f"event={event}")
    if event is None:
        raise KeyError("event is None")
    sqs_records = event["Records"]

    webhook_url = get_webhook()

    messenger = Messenger(format=MESSAGE_FORMAT, webhook=webhook_url)

    delivery_stream = DeliveryStream(delivery_stream_name=FIREHOSE_DELIVERY_STREAM_NAME)

    success = True

    for sqs_record in sqs_records:
        logging.info(f"{sqs_record=}")
        sqs_record_body = json.loads(sqs_record["body"])
        s3_event_records = sqs_record_body.get("Records", [])
        for s3_event_record in s3_event_records:
            logging.info(f"{s3_event_record=}")
            # Get the object from the event and show its content type
            bucket = s3_event_record["s3"]["bucket"]["name"]

            key = urllib.parse.unquote_plus(
                s3_event_record["s3"]["object"]["key"], encoding="utf-8"
            )
            key_elements = key.split("/")
            if "CloudTrail" not in key_elements:
                logging.info("Skipping record; CloudTrail is not in the S3 key.")
                continue

            is_valid_account, reason = valid_account(key)

            if not is_valid_account:
                logging.info("Skipping record; Not a valid account.")
                continue

            response = s3.get_object(Bucket=bucket, Key=key)
            content = response["Body"].read()

            trail_event_origin = f"{bucket}/{key}"
            with gzip.GzipFile(fileobj=io.BytesIO(content), mode="rb") as fh:
                trail_event_json = json.load(fh)
                logging.info(f"{trail_event_json=}")
                for trail_event in trail_event_json["Records"]:
                    success = success and __handle_event(
                        messenger=messenger,
                        delivery_stream=delivery_stream,
                        trail_event=trail_event,
                        trail_event_origin=trail_event_origin,
                        standalone=False,
                    )
                    logging.info(f"{success=}")

    if not success:
        logging.error(f"event={json.dumps(event)}")
        raise Exception("A problem occurred, please review error logs.")

    return "Completed"


def handler_standalone(event, context) -> None:
    if event is None:
        raise KeyError("event is None")

    webhook_url = get_webhook()

    messenger = Messenger(format=MESSAGE_FORMAT, webhook=webhook_url)

    delivery_stream = DeliveryStream(delivery_stream_name=FIREHOSE_DELIVERY_STREAM_NAME)

    event_decoded_compressed = base64.b64decode(event["awslogs"]["data"])
    event_uncompressed = gzip.decompress(event_decoded_compressed)
    event_json = json.loads(event_uncompressed)

    # logging.info(event_uncompressed)

    success = True
    for e in event_json["logEvents"]:
        trail_event_origin = (
            event_json["logGroup"]
            + ":"
            + {event_json["logStream"]}
            + "\n"
            + {event_json["subscriptionFilters"]}
        )

        success = success and __handle_event(
            messenger=messenger,
            delivery_stream=delivery_stream,
            trail_event=json.loads(e["message"]),
            trail_event_origin=trail_event_origin,
            standalone=True,
        )

    if not success:
        logging.info("event_uncompressed:\n\n" + event_uncompressed)
        raise Exception("A problem occurred, please review error logs.")

    return "Completed"


def __handle_event(
    messenger, delivery_stream, trail_event, trail_event_origin: str, standalone: bool
) -> bool:
    cloudtrail_event = CloudTrailEvent(trail_event)

    is_valid_user, reason = valid_user(cloudtrail_event.user_email)

    if not is_valid_user:
        logging.info("Skipping; Is not valid user.")
        return True

    clickops_checker = ClickOpsEventChecker(cloudtrail_event, EXCLUDED_SCOPED_ACTIONS)

    is_clickops, reason = clickops_checker.is_clickops()
    logging.info(f"{is_clickops=}")

    if is_clickops:
        result1 = messenger.send(
            cloudtrail_event.user_email,
            trail_event,
            trail_event_origin=trail_event_origin,
            standalone=standalone,
        )
        if not result1:
            logging.error(
                "Message not sent to webhook.\n\n"
                f"trail_event={json.dumps(trail_event)}"
            )
        result2 = delivery_stream.send(trail_event)
        if not result2:
            logging.error(
                "Message not delivered to delivery stream.\n\n"
                f"trail_event={json.dumps(trail_event)}"
            )
        return result1 and result2

    return True
