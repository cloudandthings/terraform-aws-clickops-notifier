from clickopsnotifier.messenger import _summarize_event


class TestSummarizeEvent:
    def test_returns_only_allowlisted_fields(self):
        event = {
            "eventTime": "2026-04-15T16:01:06Z",
            "eventSource": "kms.amazonaws.com",
            "eventName": "CreateGrant",
            "awsRegion": "us-east-1",
            "sourceIPAddress": "lambda.amazonaws.com",
            "userAgent": "lambda.amazonaws.com",
            "recipientAccountId": "123456789012",
            "resources": [{"type": "AWS::KMS::Key"}],
            "requestParameters": {"keyId": "abc"},
            "responseElements": {"grantId": "xyz"},
            "eventID": "some-id",
            "requestID": "some-request",
            "userIdentity": {"type": "IAMUser"},
        }
        result = _summarize_event(event)
        assert "eventTime" in result
        assert "eventSource" in result
        assert "eventName" in result
        assert "awsRegion" in result
        assert "sourceIPAddress" in result
        assert "userAgent" in result
        assert "recipientAccountId" in result
        assert "resources" in result
        assert "requestParameters" not in result
        assert "responseElements" not in result
        assert "eventID" not in result
        assert "requestID" not in result
        assert "userIdentity" not in result

    def test_missing_fields_are_omitted(self):
        event = {
            "eventTime": "2026-04-15T16:01:06Z",
            "eventName": "CreateGrant",
        }
        result = _summarize_event(event)
        assert result == {
            "eventTime": "2026-04-15T16:01:06Z",
            "eventName": "CreateGrant",
        }

    def test_empty_event_returns_empty_dict(self):
        result = _summarize_event({})
        assert result == {}

    def test_preserves_resources_array(self):
        resources = [
            {
                "accountId": "123456789012",
                "type": "AWS::KMS::Key",
                "ARN": "arn:aws:kms:us-east-1:123:key/abc",
            },
            {
                "accountId": "123456789012",
                "type": "AWS::S3::Bucket",
                "ARN": "arn:aws:s3:::my-bucket",
            },
        ]
        event = {"resources": resources}
        result = _summarize_event(event)
        assert result["resources"] == resources
