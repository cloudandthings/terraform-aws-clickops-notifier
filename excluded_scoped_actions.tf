locals {
  ignored_scoped_events_built_in = [
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
    "signin.amazonaws.com:CheckMfa",

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
    
    "trustedadvisor.amazonaws.com:RefreshCheck",
  ]
}
