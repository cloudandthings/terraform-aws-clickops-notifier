import glob
import json

import pytest

import clickops
from main import get_account_alias

ADDITIONAL_METADATA = {
    'accounts': {
        '123456789012': {
            'alias': 'test_account'
        }
    }
}

IGNORED_SCOPED_EVENTS_DEFAULT = [
    "cognito-idp.amazonaws.com:InitiateAuth",
    "cognito-idp.amazonaws.com:RespondToAuthChallenge",

    "sso.amazonaws.com:Federate",
    "sso.amazonaws.com:Authenticate",
    "sso.amazonaws.com:Logout",
    "sso.amazonaws.com:SearchUsers",
    "sso.amazonaws.com:SearchGroups",
    "sso.amazonaws.com:CreateToken",

    "signin.amazonaws.com:UserAuthentication",
    "signin.amazonaws.com:SwitchRole",
    "signin.amazonaws.com:RenewRole",
    "signin.amazonaws.com:ExternalIdPDirectoryLogin",
    "signin.amazonaws.com:CredentialVerification",
    "signin.amazonaws.com:CredentialChallenge",

    "logs.amazonaws.com:StartQuery",
    "cloudtrail.amazonaws.com:StartQuery",

    "iam.amazonaws.com:SimulatePrincipalPolicy",
    "iam.amazonaws.com:GenerateServiceLastAccessedDetails",

    "glue.amazonaws.com:BatchGetJobs",
    "glue.amazonaws.com:BatchGetCrawlers",
    "glue.amazonaws.com:StartJobRun",
    "glue.amazonaws.com:StartCrawler",

    "athena.amazonaws.com:StartQueryExecution",

    "servicecatalog.amazonaws.com:SearchProductsAsAdmin",
    "servicecatalog.amazonaws.com:SearchProducts",
    "servicecatalog.amazonaws.com:SearchProvisionedProducts",
    "servicecatalog.amazonaws.com:TerminateProvisionedProduct",

    "cloudshell.amazonaws.com:CreateSession",
    "cloudshell.amazonaws.com:PutCredentials",
    "cloudshell.amazonaws.com:SendHeartBeat",
    "cloudshell.amazonaws.com:CreateEnvironment",

    "kms.amazonaws.com:Decrypt",
    "kms.amazonaws.com:RetireGrant",
  ]


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
    is_clickops, reason = clickops.\
        ClickOpsEventChecker(event, IGNORED_SCOPED_EVENTS_DEFAULT).\
        is_clickops()

    assert event.read_only == test_event['expect']['readonly']
    assert event.user_email == test_event['expect']['user_email']

    assert test_event['expect']['reason_contains'] in reason
    assert is_clickops == test_event['expect']['is_clickops']

    account_alias = get_account_alias(test_event['event']['recipientAccountId'])
    assert account_alias == test_event['expect']['account_alias']
