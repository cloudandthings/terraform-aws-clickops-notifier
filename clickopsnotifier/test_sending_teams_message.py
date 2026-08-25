#!/usr/bin/env python3
import os
import sys

from clickopsnotifier.messenger import Messenger

WEBHOOK_URL = "https://your-webhook-url.com/webhook"  # Replace with your actual webhook URL


def main() -> int:
    webhook_url = os.environ.get("WEBHOOK_URL") or WEBHOOK_URL
    if not webhook_url:
        print("Usage: WEBHOOK_URL='https://.../webhook' python send_teams_test.py")
        print("       or: python send_teams_test.py 'https://.../webhook'")
        return 1

    sample_event = {
        "eventTime": "2026-08-25T12:00:00Z",
        "eventSource": "ec2.amazonaws.com",
        "eventName": "RunInstances",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "203.0.113.10",
        "userAgent": "Mozilla/5.0",
        "recipientAccountId": "123456789012",
        "resources": [{"ARN": "arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0"}],
    }

    messenger = Messenger(
        webhook_type="msteams",
        webhook_url=webhook_url,
        parameter_name="/local-test/webhooks-for-msteams/local-test",
    )

    ok = messenger.send(
        user="tester@example.com",
        trail_event=sample_event,
        trail_event_origin="local-test-script",
        standalone=True,
    )

    if ok:
        print("Teams message sent successfully.")
        return 0

    print("Teams message failed to send.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
