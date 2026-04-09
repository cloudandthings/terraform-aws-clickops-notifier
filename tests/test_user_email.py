from clickopsnotifier.clickops import CloudTrailEvent


def _make_event(user_identity):
    return {
        "eventName": "CreateBucket",
        "eventSource": "s3.amazonaws.com",
        "userIdentity": user_identity,
    }


class TestUserEmailExtraction:
    def test_principal_id_with_email(self):
        event = _make_event(
            {
                "principalId": "AROAXK4KVD27BINQTHSKU:paul@cloudandthings.io",
            }
        )
        assert CloudTrailEvent(event).user_email == "paul@cloudandthings.io"

    def test_principal_id_without_email_falls_through(self):
        event = _make_event(
            {
                "principalId": "AROAXK4KVD27BINQTHSKU:my-session-name",
            }
        )
        assert CloudTrailEvent(event).user_email == "Unknown"

    def test_principal_id_no_colon(self):
        event = _make_event(
            {
                "principalId": "AIDAXK4KVD27BINQTHSKU",
            }
        )
        assert CloudTrailEvent(event).user_email == "Unknown"

    def test_username_with_email(self):
        event = _make_event(
            {
                "userName": "paul@cloudandthings.io",
            }
        )
        assert CloudTrailEvent(event).user_email == "paul@cloudandthings.io"

    def test_username_without_email_used_as_fallback(self):
        event = _make_event(
            {
                "userName": "admin-role",
            }
        )
        assert CloudTrailEvent(event).user_email == "admin-role"

    def test_arn_with_email(self):
        arn = (
            "arn:aws:sts::123456789012:"
            "assumed-role/AWSReservedSSO_Admin/"
            "paul@cloudandthings.io"
        )
        event = _make_event(
            {
                "arn": arn,
            }
        )
        assert CloudTrailEvent(event).user_email == "paul@cloudandthings.io"

    def test_fallback_to_full_identity_scan(self):
        event = _make_event(
            {
                "someOtherField": "paul@cloudandthings.io",
            }
        )
        assert CloudTrailEvent(event).user_email == "paul@cloudandthings.io"

    def test_no_user_identity(self):
        event = {"eventName": "CreateBucket", "eventSource": "s3.amazonaws.com"}
        assert CloudTrailEvent(event).user_email == "Unknown"

    def test_empty_user_identity(self):
        event = _make_event({})
        assert CloudTrailEvent(event).user_email == "Unknown"

    def test_principal_id_non_email_falls_to_username_email(self):
        event = _make_event(
            {
                "principalId": "AROAXK4KVD27BINQTHSKU:my-session",
                "userName": "paul@cloudandthings.io",
            }
        )
        assert CloudTrailEvent(event).user_email == "paul@cloudandthings.io"

    def test_principal_id_non_email_username_non_email_falls_to_arn(self):
        arn = (
            "arn:aws:sts::123456789012:"
            "assumed-role/AWSReservedSSO_Admin/"
            "paul@cloudandthings.io"
        )
        event = _make_event(
            {
                "principalId": "AROAXK4KVD27BINQTHSKU:my-session",
                "userName": "admin-role",
                "arn": arn,
            }
        )
        assert CloudTrailEvent(event).user_email == "paul@cloudandthings.io"

    def test_no_email_anywhere_falls_back_to_non_email_username(self):
        event = _make_event(
            {
                "principalId": "AROAXK4KVD27BINQTHSKU:my-session",
                "userName": "admin-role",
                "arn": "arn:aws:iam::123456789012:role/AdminRole",
            }
        )
        assert CloudTrailEvent(event).user_email == "admin-role"
