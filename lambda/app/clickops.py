import re
import json
from typing import Tuple


class CloudTrailEvent:
    def __init__(self, event) -> None:

        self.user_agent = event.get('userAgent', 'Unknown User Agent')
        self.event_name = event['eventName']
        self.event_source = event['eventSource']
        self.request_id = event.get('requestID', "NA")
        self.read_only = self.__readonly_event(event)
        self.user_email = self.__user_email(event)

    @staticmethod
    def __user_email(event) -> str:
        if 'userIdentity' in event:
            match = re.search(
                r'[\w.+-]+@[\w-]+\.[\w.-]+',
                json.dumps(event['userIdentity']))
            if match is None:
                return 'Unknown'
            else:
                return match.group(0)
        else:
            return 'Unknown'

    @staticmethod
    def __readonly_event(event) -> bool:
        if 'readOnly' in event:
            if event['readOnly'] == 'true' or event['readOnly'] or event['readOnly'] == 1:
                return True
            else:
                return False
        else:
            return False


class ClickOpsEventChecker:
    def __init__(self, event: CloudTrailEvent) -> None:
        self.READONLY_EVENTS_RE = [
            "^Get",
            "^Describe",
            "^List",
            "^Head",
        ]

        self.IGNORED_SCOPED_EVENTS = [
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

        self.IGNORED_EVENTS = {
            "DownloadDBLogFilePortion",
            "TestScheduleExpression",
            "TestEventPattern",
            "LookupEvents",
            "listDnssec",
            "Decrypt",
            "REST.GET.OBJECT_LOCK_CONFIGURATION",
            "ConsoleLogin"
        }

        self.USER_AGENTS_RE = [
            "signin.amazonaws.com(.*)",
            "^S3Console",
            "^\[S3Console",  # noqa: W605
            "^Mozilla/",
            "^console(.*)amazonaws.com(.*)",
            "^aws-internal(.*)AWSLambdaConsole(.*)",
        ]

        self.USER_AGENTS = {
            "console.amazonaws.com",
            "Coral/Jakarta",
            "Coral/Netty4"
        }

        self.event = event

    @staticmethod
    def check_regex(expr, txt) -> bool:
        match = re.search(expr, txt)
        return match is not None

    def __match_readonly_event_name_pattern(self) -> bool:
        for expression in self.READONLY_EVENTS_RE:
            if self.check_regex(expression, self.event.event_name):
                return True

        return False

    def __match_ignored_event_names(self) -> bool:
        return self.event.event_name in self.IGNORED_EVENTS

    def __match_ignored_scoped_events(self) -> bool:
        return f'{self.event.event_source}:{self.event.event_name}' in self.IGNORED_SCOPED_EVENTS  # noqa: E501

    def __user_agent_console(self) -> bool:

        user_agent = self.event.user_agent

        if user_agent in self.USER_AGENTS:
            return True

        for expresion in self.USER_AGENTS_RE:
            if self.check_regex(expresion, user_agent):
                return True

        return False

    def is_clickops(self) -> Tuple[bool, str]:

        if self.event.read_only:
            return False, "[COEC_Rule1] Readonly Event"

        if not self.__user_agent_console():
            return False, "[COEC_Rule2] User agent does not match console"

        if self.__match_readonly_event_name_pattern():
            return False, "[COEC_Rule3] Match readonly event name pattern"

        if self.__match_ignored_event_names():
            return False, "[COEC_Rule4] Match ignored ignored event names"

        if self.__match_ignored_scoped_events():
            return False, "[COEC_Rule5] Match ignored ignored event names"

        return True, "[COEC_Rule6] Could not match any exclusions"
