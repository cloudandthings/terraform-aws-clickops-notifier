
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

    def __send_msteams_message(self, user, event, s3_bucket, s3_key) -> bool:

        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "ClickOps Alert",
            "sections": [{
                "activityTitle": "Someone is practicing ClickOps in your AWS Account!",
                "facts": [{
                    "name": "Account Id",
                    "value": event['recipientAccountId']
                }, {
                    "name": "Region",
                    "value": event['awsRegion']
                }, {
                    "name": "User",
                    "value": user
                }, {
                    "name": "IAM Action",
                    "value": f"{event['eventSource'].split('.')[0]}:{event['eventName']}"
                }, {
                    "name": "Cloudtrail Bucket",
                    "value": s3_bucket
                }, {
                    "name": "Key",
                    "value": s3_key
                }, {
                    "name": "Event",
                    "value": f"```{json.dumps(event, indent=2)}"
                }],
                "markdown": True
            }]
        }

        response = requests.post(self.webhook, json=payload)
        if response.status_code != 200:
            return False
        return True

    def __send_slack_message(self, user, event, s3_bucket, s3_key) -> bool:
        payload = {
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
                            "text": f"*Principal*\n{user}"
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

        response = requests.post(self.webhook, json=payload)
        if response.status_code != 200:
            return False
        return True
