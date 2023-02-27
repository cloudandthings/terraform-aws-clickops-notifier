import json
import urllib.parse
import urllib.request
import boto3
import io
import gzip
import base64
import os
from typing import Tuple, List
import logging

from clickops import ClickOpsEventChecker, CloudTrailEvent
from messenger import Messenger
from delivery_stream import DeliveryStream

LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARN")
logging.getLogger().setLevel(LOG_LEVEL)

WEBHOOKS_FOR_SLACK = json.loads(os.environ.get("WEBHOOKS_FOR_SLACK", "[]"))
WEBHOOKS_FOR_MSTEAMS = json.loads(os.environ.get("WEBHOOKS_FOR_MSTEAMS", "[]"))

EXCLUDED_ACCOUNTS = json.loads(os.environ.get("EXCLUDED_ACCOUNTS", "[]"))
INCLUDED_ACCOUNTS = json.loads(os.environ.get("INCLUDED_ACCOUNTS", "[]"))

EXCLUDED_USERS = json.loads(os.environ.get("EXCLUDED_USERS", "[]"))
INCLUDED_USERS = json.loads(os.environ.get("INCLUDED_USERS", "[]"))

EXCLUDED_SCOPED_ACTIONS = json.loads(os.environ.get("EXCLUDED_SCOPED_ACTIONS", "[]"))

FIREHOSE_DELIVERY_STREAM_NAME = os.environ.get("FIREHOSE_DELIVERY_STREAM_NAME")
if FIREHOSE_DELIVERY_STREAM_NAME == "__NONE__":
    FIREHOSE_DELIVERY_STREAM_NAME = None

s3 = boto3.client("s3")
ssm = boto3.client("ssm")


def get_webhook(name) -> str:
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    value = response["Parameter"]["Value"]
    return value


_MESSENGERS = None


def get_messengers() -> List[Messenger]:
    global _MESSENGERS
    if _MESSENGERS is not None:
        return _MESSENGERS
    _MESSENGERS = []

    logging.info("Configuring Slack messengers...")
    for webhook_for_slack in WEBHOOKS_FOR_SLACK:
        webhook = get_webhook(webhook_for_slack)
        messenger = Messenger("slack", webhook)
        _MESSENGERS.append(messenger)

    logging.info("Configuring MSTeams messengers...")
    for webhook_for_msteams in WEBHOOKS_FOR_MSTEAMS:
        webhook = get_webhook(webhook_for_msteams)
        messenger = Messenger("msteams", webhook)
        _MESSENGERS.append(messenger)

    logging.info(f"There are {len(_MESSENGERS)} messengers configured.")
    return _MESSENGERS


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

    delivery_stream = DeliveryStream(delivery_stream_name=FIREHOSE_DELIVERY_STREAM_NAME)

    success = True

    for sqs_record in sqs_records:
        logging.debug(f"{sqs_record=}")
        sqs_body = json.loads(sqs_record["body"])
        sqs_body_message = json.loads(sqs_body["Message"])
        s3_event_records = sqs_body_message["Records"]
        for s3_event_record in s3_event_records:
            logging.debug(f"{s3_event_record=}")
            # Get the object from the event and show its content type
            bucket = s3_event_record["s3"]["bucket"]["name"]

            key = urllib.parse.unquote_plus(
                s3_event_record["s3"]["object"]["key"], encoding="utf-8"
            )
            key_elements = key.split("/")
            if "CloudTrail" not in key_elements:
                logging.info("Skipping; CloudTrail is not in the S3 key.")
                continue

            is_valid_account, reason = valid_account(key)

            if not is_valid_account:
                logging.info(f"Skipping; Not a valid account. {reason=}.")
                continue
            logging.debug(f"Not skipping {key=}.")

            response = s3.get_object(Bucket=bucket, Key=key)
            content = response["Body"].read()

            trail_event_origin = f"{bucket}/{key}"
            with gzip.GzipFile(fileobj=io.BytesIO(content), mode="rb") as fh:
                trail_event_json = json.load(fh)
                logging.debug(f"{trail_event_json=}")
                for trail_event in trail_event_json["Records"]:
                    success = success and __handle_event(
                        delivery_stream=delivery_stream,
                        trail_event=trail_event,
                        trail_event_origin=trail_event_origin,
                        standalone=False,
                    )

    if not success:
        logging.error(f"event={json.dumps(event)}")
        raise Exception("A problem occurred, please review error logs.")

    return "Completed"


def handler_standalone(event, context) -> None:
    if event is None:
        raise KeyError("event is None")

    delivery_stream = DeliveryStream(delivery_stream_name=FIREHOSE_DELIVERY_STREAM_NAME)

    event_decoded_compressed = base64.b64decode(event["awslogs"]["data"])
    event_uncompressed = gzip.decompress(event_decoded_compressed)
    event_json = json.loads(event_uncompressed)

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
    delivery_stream, trail_event, trail_event_origin: str, standalone: bool
) -> bool:
    cloudtrail_event = CloudTrailEvent(trail_event)

    is_valid_user, reason = valid_user(cloudtrail_event.user_email)

    if not is_valid_user:
        logging.info(f"Skipping; Not a valid user. {reason=}")
        return True

    clickops_checker = ClickOpsEventChecker(cloudtrail_event, EXCLUDED_SCOPED_ACTIONS)

    is_clickops, reason = clickops_checker.is_clickops()

    if not is_clickops:
        return True

    # AT LEAST ONCE SEMANTICS on delivery stream
    #
    # Raising an Exception ensures the Lambda is retried by SQS.
    #
    # So only raise an Exception if DeliveryStream delivery fails
    #
    # Duplicate (or missed) warm-body notifications are OK

    result = delivery_stream.send(trail_event)
    if not result:
        logging.error("Message NOT delivered to delivery stream.")

    # Attempt to send messages as well
    messengers = get_messengers()
    for i, messenger in enumerate(messengers):
        result_messenger = messenger.send(
            cloudtrail_event.user_email,
            trail_event,
            trail_event_origin=trail_event_origin,
            standalone=standalone,
        )
        if not result_messenger:
            logging.error(f"Message NOT sent to webhook {i}.")

    if not result:
        logging.error(f"trail_event={json.dumps(trail_event)}")

    return result
