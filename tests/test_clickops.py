from clickopsnotifier.clickops import CloudTrailEvent, ClickOpsEventChecker


def _make_event(event_source, event_name):
    return {
        "eventSource": event_source,
        "eventName": event_name,
        "readOnly": False,
        "sessionCredentialFromConsole": True,
        "userIdentity": {},
    }


def _is_clickops(event_source, event_name, ignored_scoped_events):
    event = CloudTrailEvent(_make_event(event_source, event_name))
    return ClickOpsEventChecker(event, ignored_scoped_events).is_clickops()


class TestIgnoredScopedEventsMatching:
    def test_exact_match_is_ignored(self):
        is_clickops, reason = _is_clickops(
            "ssm.amazonaws.com",
            "StartSession",
            ["ssm.amazonaws.com:StartSession"],
        )
        assert is_clickops is False
        assert "COEC_Rule5" in reason

    def test_wildcard_action_matches(self):
        is_clickops, reason = _is_clickops(
            "logs.amazonaws.com",
            "FilterLogEvents",
            ["logs.amazonaws.com:*"],
        )
        assert is_clickops is False
        assert "COEC_Rule5" in reason

    def test_wildcard_does_not_cross_services(self):
        is_clickops, reason = _is_clickops(
            "s3.amazonaws.com",
            "FilterLogEvents",
            ["logs.amazonaws.com:*"],
        )
        assert is_clickops is True
        assert "COEC_Rule6" in reason

    def test_non_matching_action_is_not_ignored(self):
        is_clickops, reason = _is_clickops(
            "ec2.amazonaws.com",
            "TerminateInstances",
            ["ssm.amazonaws.com:StartSession"],
        )
        assert is_clickops is True
        assert "COEC_Rule6" in reason

    def test_partial_action_prefix_wildcard(self):
        is_clickops, reason = _is_clickops(
            "cloudshell.amazonaws.com",
            "DeleteEnvironment",
            ["cloudshell.amazonaws.com:*Environment"],
        )
        assert is_clickops is False
        assert "COEC_Rule5" in reason
