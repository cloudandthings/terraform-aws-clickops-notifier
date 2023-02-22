import json
import requests


class Messenger:
    def __init__(self, format: str, webhook: str) -> None:
        self.webhook = webhook
        self.format = format

        if format == "slack":
            self.send = self.__send_slack_message
        elif format == "msteams":
            self.send = self.__send_msteams_message
        else:
            raise ValueError("Invalid format, must be ['slack', 'msteams']")

    def __send_msteams_message(
        self, user, trail_event, trail_event_origin: str, standalone: str
    ) -> bool:
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "ClickOps Alert",
            "sections": [
                {
                    "activityTitle": f"{'[std]' if standalone else '[org]'} Someone is practicing ClickOps in your AWS Account!",  # noqa: E501
                    "facts": [
                        {
                            "name": "Account Id",
                            "value": trail_event["recipientAccountId"],
                        },
                        {"name": "Region", "value": trail_event["awsRegion"]},
                        {"name": "User", "value": user},
                        {
                            "name": "IAM Action",
                            "value": f"{trail_event['eventSource'].split('.')[0]}:{trail_event['eventName']}",  # noqa: E501
                        },
                        {"name": "Event Log Origin", "value": trail_event_origin},
                        {
                            "name": "Event",
                            "value": f"```{json.dumps(trail_event, indent=2)}",
                        },
                    ],
                    "markdown": True,
                }
            ],
        }

        response = requests.post(self.webhook, json=payload)
        if response.status_code != 200:
            return False
        return True

    def __send_slack_message(
        self, user, trail_event, trail_event_origin: str, standalone: bool
    ) -> bool:
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
                        "text": f"*Event*\n```{json.dumps(trail_event, indent=2)}```",
                    },
                },
            ]
        }

        response = requests.post(self.webhook, json=payload)
        if response.status_code != 200:
            print(response.content)
            return False
        return True
