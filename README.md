# AWS ClickOps Notifier

Get notified when users are taking actions in the AWS Console. More [here](https://medium.com/cloudandthings/aws-clickoops-1b8cabc9b8e3)
## 🏗️ Module Usage

It is not strictly a requirement, that you use this with AWS ControlTower. The module has only been tested in the Log Archive account that ships with AWS ControTower. Setup your AWS credentails such that `aws sts get-caller-identity | grep Account` gives you your ControlTower Log Archive account id.


## Excluded scoped actions
The following actions will not be alerted, these are eithe:
- actions that are commonly performed in the AWS Console and we think they are okay
- actions that can only be performed in the AWS Console

This functionality an be overriden with the `excluded_scoped_actions` and `excluded_scoped_actions_effect` variables. The list of excluded actions availabe in the terraform docs below.


## Contributing

Report issues/questions/feature requests on in the [issues](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/new) section.

Full contributing [guidelines are covered here](.github/contributing.md).


<!-- BEGIN_TF_DOCS -->
## Module Docs
### Examples

```hcl
terraform {
  required_version = ">= 0.13.1"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.9.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "clickops_notifications" {
  source = "../../"

  cloudtrail_bucket_name = var.cloudtrail_bucket_name
  webhook                = var.webhook
  message_format         = "slack"
}
```
----
### Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_additional_iam_policy_statements"></a> [additional\_iam\_policy\_statements](#input\_additional\_iam\_policy\_statements) | Map of dynamic policy statements to attach to Lambda Function role | `any` | `{}` | no |
| <a name="input_cloudtrail_bucket_name"></a> [cloudtrail\_bucket\_name](#input\_cloudtrail\_bucket\_name) | Bucket containing the Cloudtrail logs that you want to process. ControlTower bucket name follows this naming convention `aws-controltower-logs-{{account_id}}-{{region}}` | `string` | n/a | yes |
| <a name="input_event_batch_size"></a> [event\_batch\_size](#input\_event\_batch\_size) | Batch events into chunks of `event_batch_size` | `number` | `10` | no |
| <a name="input_event_maximum_batching_window"></a> [event\_maximum\_batching\_window](#input\_event\_maximum\_batching\_window) | Maximum batching window in seconds. | `number` | `300` | no |
| <a name="input_event_processing_timeout"></a> [event\_processing\_timeout](#input\_event\_processing\_timeout) | Maximum number of seconds the lambda is allowed to run and number of seconds events should be hidden in SQS after being picked up my Lambda. | `number` | `60` | no |
| <a name="input_excluded_accounts"></a> [excluded\_accounts](#input\_excluded\_accounts) | List of accounts that be excluded for scans on manual actions. These take precidence over `included_accounts` | `list(string)` | `[]` | no |
| <a name="input_excluded_scoped_actions"></a> [excluded\_scoped\_actions](#input\_excluded\_scoped\_actions) | A list of service scoped actions that will not be alerted on. Format {{service}}.amazonaws.com:{{action}} | `list(string)` | `[]` | no |
| <a name="input_excluded_scoped_actions_effect"></a> [excluded\_scoped\_actions\_effect](#input\_excluded\_scoped\_actions\_effect) | Should the existing exluded actions be replaces or appended to. By default it will append to the list, valid values: APPEND, REPLACE | `string` | `"APPEND"` | no |
| <a name="input_excluded_users"></a> [excluded\_users](#input\_excluded\_users) | List of email addresses will not be reported on when practicing ClickOps. | `list(string)` | `[]` | no |
| <a name="input_included_accounts"></a> [included\_accounts](#input\_included\_accounts) | List of accounts that be scanned to manual actions. If empty will scan all accounts. | `list(string)` | `[]` | no |
| <a name="input_included_users"></a> [included\_users](#input\_included\_users) | List of emails that be scanned to manual actions. If empty will scan all emails. | `list(string)` | `[]` | no |
| <a name="input_lambda_runtime"></a> [lambda\_runtime](#input\_lambda\_runtime) | The lambda runtime to use | `string` | `"python3.8"` | no |
| <a name="input_log_retention_in_days"></a> [log\_retention\_in\_days](#input\_log\_retention\_in\_days) | Number of days to keep CloudWatch logs | `number` | `14` | no |
| <a name="input_message_format"></a> [message\_format](#input\_message\_format) | Where do you want to send this message? Only slack, for now. | `string` | `"slack"` | no |
| <a name="input_naming_prefix"></a> [naming\_prefix](#input\_naming\_prefix) | Resources will be prefixed with this | `string` | `"clickops-notifier"` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags to add to resources in addition to the default\_tags for the provider | `map(string)` | `{}` | no |
| <a name="input_webhook"></a> [webhook](#input\_webhook) | The webhook URL for notifications. https://api.slack.com/messaging/webhooks | `string` | n/a | yes |
----
### Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_clickops_notifier_lambda"></a> [clickops\_notifier\_lambda](#module\_clickops\_notifier\_lambda) | terraform-aws-modules/lambda/aws | 3.2.1 |
----
### Outputs

| Name | Description |
|------|-------------|
| <a name="output_clickops_notifier_lambda"></a> [clickops\_notifier\_lambda](#output\_clickops\_notifier\_lambda) | Expose all the outputs from the lambda module |
| <a name="output_sqs_queue"></a> [sqs\_queue](#output\_sqs\_queue) | Expose the bucket notification SQS details |
----
### Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 4.23.0 |
----
### Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.13.1 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.9 |
----
### Resources

| Name | Type |
|------|------|
| [aws_s3_bucket_notification.bucket_notification](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_notification) | resource |
| [aws_sqs_queue.bucket_notifications](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue) | resource |
| [aws_sqs_queue_policy.bucket_notifications](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue_policy) | resource |
| [aws_ssm_parameter.slack_webhook](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_iam_policy_document.lambda_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_s3_bucket.cloudtrail_bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/s3_bucket) | data source |
----
### Default excluded scoped actions
```hcl
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
}
```
<!-- END_TF_DOCS -->    

----
