import glob
import json

import pytest

import clickops


def get_data():
    tests = []
    for filename in glob.glob("../tests/*.json"):
        with open(filename, 'r') as file:
            test = json.load(file)
            tests.append((json.dumps(test), filename))
    return tests


@pytest.mark.parametrize("test,file", get_data())
def test_mapping(test, file):
    test_event = json.loads(test)
    assert 'event' in test_event
    assert 'expect' in test_event

    event = clickops.CloudTrailEvent(test_event['event'])
    is_clickops, reason = clickops.ClickOpsEventChecker(event).is_clickops()

    assert event.read_only == test_event['expect']['readonly']
    assert event.user_email == test_event['expect']['user_email']

    assert test_event['expect']['reason_contains'] in reason
    assert is_clickops == test_event['expect']['is_clickops']
