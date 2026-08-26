import json
import requests
import logging
import re

WEBHOOK_NAME_REGEXP = r".*webhooks-for-.*?\/(.*)"

# Fields to include in notification event output.
# Everything else (requestParameters, responseElements, sessionContext,
# eventId, requestId, etc.) is stripped to reduce noise.
EVENT_SUMMARY_FIELDS = [
    "eventTime",
    "eventSource",
    "eventName",
    "awsRegion",
    "sourceIPAddress",
    "userAgent",
    "recipientAccountId",
    "resources",
]

logger = logging.getLogger(__name__)


def _summarize_event(trail_event: dict) -> dict:
    """Return only the allowlisted fields from a CloudTrail event."""
    summary = {k: trail_event[k] for k in EVENT_SUMMARY_FIELDS if k in trail_event}
    if not summary:
        logger.warning("No allowlisted fields found in event")
    return summary


class Messenger:
    def __init__(
        self, webhook_type: str, webhook_url: str, parameter_name: str
    ) -> None:
        self.webhook_url = webhook_url
        if self.webhook_url is None:
            raise ValueError("webhook_url cannot be None")

        self.webhook_type = webhook_type
        if webhook_type == "slack":
            self.send = self.__send_slack_message
        elif webhook_type == "msteams":
            self.send = self.__send_msteams_message
        else:
            raise ValueError("Invalid webhook_type, must be ['slack', 'msteams']")

        m = re.match(WEBHOOK_NAME_REGEXP, parameter_name)
        self.webhook_name = m.group(1)

    def __str__(self) -> str:
        return self.webhook_name

    def __send_msteams_message(
        self, user, trail_event, trail_event_origin: str, standalone: str
    ) -> bool:
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "version": "1.4",
                        "msteams": {"width": "Full"},
                        "body": [
                            {
                                "type": "Container",
                                "style": "attention",
                                "bleed": True,
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": f"{'[std]' if standalone else '[org]'} 🫆 Someone is practicing ClickOps in your AWS Account!",
                                        "weight": "Bolder",
                                        "size": "Medium",
                                        "wrap": True,
                                    }
                                ],
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {
                                        "title": "Account ID",
                                        "value": trail_event["recipientAccountId"],
                                    },
                                    {
                                        "title": "Region",
                                        "value": trail_event["awsRegion"],
                                    },
                                    {"title": "User", "value": user},
                                    {
                                        "title": "IAM Action",
                                        "value": f"{trail_event['eventSource'].split('.')[0]}:{trail_event['eventName']}",
                                    },
                                    {
                                        "title": "Event Log Origin",
                                        "value": trail_event_origin,
                                    },
                                ],
                            },
                            {
                                "type": "TextBlock",
                                "text": f"```{json.dumps(_summarize_event(trail_event), indent=2)}",
                                "wrap": True,
                                "isSubtle": True,
                                "spacing": "Medium",
                            },
                        ],
                    },
                }
            ],
        }

        response = requests.post(self.webhook_url, json=payload)
        if response.status_code not in [200, 201, 202]:
            logging.info(f"{self.webhook_name} json payload:\n\n{json.dumps(payload)}")
            logging.error(
                f"{self.webhook_name} response.content:\n\n{response.content}"
            )
            return False
        return True

    def __send_slack_message(
        self, user, trail_event, trail_event_origin: str, standalone: bool
    ) -> bool:
        formatted_event = json.dumps(_summarize_event(trail_event), indent=2)
        if len(formatted_event) > 2900:
            formatted_event = f"*Event (truncated)*\n```{formatted_event[:2900]}```"
        else:
            formatted_event = f"*Event*\n```{formatted_event}```"
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": ":bell: ClickOps Alert :bell:",
                        "emoji": True,
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{'[std]' if standalone else '[org]'} Someone is practicing ClickOps in your AWS Account!",  # noqa: E501
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Account Id*\n{trail_event['recipientAccountId']}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Region*\n{trail_event['awsRegion']}",
                        },
                    ],
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*IAM Action*\n{trail_event['eventSource'].split('.')[0]}:{trail_event['eventName']}",  # noqa: E501
                        },
                        {"type": "mrkdwn", "text": f"*Principal*\n{user}"},
                    ],
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Event Log Origin*\n{trail_event_origin}",
                        }
                    ],
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": formatted_event,
                    },
                },
            ]
        }
        response = requests.post(self.webhook_url, json=payload)
        if response.status_code != 200:
            logging.info(f"{self.webhook_name} json payload:\n\n{json.dumps(payload)}")
            logging.error(
                f"{self.webhook_name} response.content:\n\n{response.content}"
            )
            return False
        return True
