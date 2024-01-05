[![Tests](https://github.com/cloudandthings/terraform-aws-clickops-notifier/actions/workflows/tests.yml/badge.svg)](https://github.com/cloudandthings/terraform-aws-clickops-notifier/actions/workflows/tests.yml)

# AWS ClickOps Notifier
Get notified when users are taking actions in the AWS Console. More [here](https://medium.com/cloudandthings/aws-clickoops-1b8cabc9b8e3)

## 🏗️ Module Usage
It is not strictly a requirement, that you use this with AWS ControlTower. The module has only been tested in the Log Archive account that ships with AWS ControlTower. Setup your AWS credentails such that `aws sts get-caller-identity | grep Account` gives you your ControlTower Log Archive account id.

### Organizational Mode vs Standalone Mode
If your account is part of an AWS Organization that does not use centralized CloudTrail logging or that does not want to monitor ClickOps at an organizational level, you can deploy ClickOps in `standalone` mode in a single account. For standalone mode you need CloudTrail enabled in your account, have it configured to write logs to a CloudWatch Log Group and have sufficient permission to create a subscription filter on the log group.

## Excluded scoped actions
The following actions will not be alerted, these are either:
- actions that are commonly performed in the AWS Console and we think they are okay
- actions that can only be performed in the AWS Console

This functionality can be overriden with the `excluded_scoped_actions` and `excluded_scoped_actions_effect` variables. The list of excluded actions is available in the terraform docs below.

<!-- Test -->

## Contributing

Report issues/questions/feature requests on in the [issues](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/new) section.

Full contributing [guidelines are covered here](.github/contributing.md).


<!-- BEGIN_TF_DOCS -->
----
## Documentation

----
### Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_additional_iam_policy_statements"></a> [additional\_iam\_policy\_statements](#input\_additional\_iam\_policy\_statements) | Map of dynamic policy statements to attach to Lambda Function role | `any` | `{}` | no |
| <a name="input_allowed_aws_principals_for_sns_subscribe"></a> [allowed\_aws\_principals\_for\_sns\_subscribe](#input\_allowed\_aws\_principals\_for\_sns\_subscribe) | List of AWS principals allowed to subscribe to the SNS topic (only applicable to org deployments). | `list(string)` | `[]` | no |
| <a name="input_cloudtrail_bucket_name"></a> [cloudtrail\_bucket\_name](#input\_cloudtrail\_bucket\_name) | Bucket containing the Cloudtrail logs that you want to process. ControlTower bucket name follows this naming convention `aws-controltower-logs-{{account_id}}-{{region}}` | `string` | `""` | no |
| <a name="input_cloudtrail_log_group"></a> [cloudtrail\_log\_group](#input\_cloudtrail\_log\_group) | CloudWatch Log group for CloudTrail events. | `string` | `""` | no |
| <a name="input_create_iam_role"></a> [create\_iam\_role](#input\_create\_iam\_role) | Determines whether a an IAM role is created or to use an existing IAM role | `bool` | `true` | no |
| <a name="input_event_batch_size"></a> [event\_batch\_size](#input\_event\_batch\_size) | Batch events into chunks of `event_batch_size` | `number` | `100` | no |
| <a name="input_event_maximum_batching_window"></a> [event\_maximum\_batching\_window](#input\_event\_maximum\_batching\_window) | Maximum batching window in seconds. | `number` | `300` | no |
| <a name="input_event_processing_timeout"></a> [event\_processing\_timeout](#input\_event\_processing\_timeout) | Maximum number of seconds the lambda is allowed to run and number of seconds events should be hidden in SQS after being picked up my Lambda. | `number` | `60` | no |
| <a name="input_excluded_accounts"></a> [excluded\_accounts](#input\_excluded\_accounts) | List of accounts that be excluded for scans on manual actions. These take precidence over `included_accounts` | `list(string)` | `[]` | no |
| <a name="input_excluded_scoped_actions"></a> [excluded\_scoped\_actions](#input\_excluded\_scoped\_actions) | A list of service scoped actions that will not be alerted on. Format {{service}}.amazonaws.com:{{action}} | `list(string)` | `[]` | no |
| <a name="input_excluded_scoped_actions_effect"></a> [excluded\_scoped\_actions\_effect](#input\_excluded\_scoped\_actions\_effect) | Should the existing exluded actions be replaces or appended to. By default it will append to the list, valid values: APPEND, REPLACE | `string` | `"APPEND"` | no |
| <a name="input_excluded_users"></a> [excluded\_users](#input\_excluded\_users) | List of email addresses will not be reported on when practicing ClickOps. | `list(string)` | `[]` | no |
| <a name="input_firehose_delivery_stream_name"></a> [firehose\_delivery\_stream\_name](#input\_firehose\_delivery\_stream\_name) | Kinesis Firehose delivery stream name to output ClickOps events to. | `string` | `null` | no |
| <a name="input_iam_role_arn"></a> [iam\_role\_arn](#input\_iam\_role\_arn) | Existing IAM role ARN for the lambda. Required if `create_iam_role` is set to `false` | `string` | `null` | no |
| <a name="input_included_accounts"></a> [included\_accounts](#input\_included\_accounts) | List of accounts that be scanned to manual actions. If empty will scan all accounts. | `list(string)` | `[]` | no |
| <a name="input_included_users"></a> [included\_users](#input\_included\_users) | List of emails that be scanned to manual actions. If empty will scan all emails. | `list(string)` | `[]` | no |
| <a name="input_kms_key_id_for_sns_topic"></a> [kms\_key\_id\_for\_sns\_topic](#input\_kms\_key\_id\_for\_sns\_topic) | KMS key ID for encrypting the sns\_topic (only applicable to org deployments). | `string` | `null` | no |
| <a name="input_lambda_deployment_s3_bucket"></a> [lambda\_deployment\_s3\_bucket](#input\_lambda\_deployment\_s3\_bucket) | S3 bucket for lambda deployment package. | `string` | `null` | no |
| <a name="input_lambda_deployment_s3_key"></a> [lambda\_deployment\_s3\_key](#input\_lambda\_deployment\_s3\_key) | S3 object key for lambda deployment package. Otherwise, defaults to `var.naming_prefix/local.deployment_filename`. | `string` | `null` | no |
| <a name="input_lambda_deployment_upload_to_s3_enabled"></a> [lambda\_deployment\_upload\_to\_s3\_enabled](#input\_lambda\_deployment\_upload\_to\_s3\_enabled) | If `true`, the lambda deployment package within this module repo will be copied to S3. If `false` then the S3 object must be uploaded separately. Ignored if `lambda_deployment_s3_bucket` is null. | `bool` | `true` | no |
| <a name="input_lambda_log_level"></a> [lambda\_log\_level](#input\_lambda\_log\_level) | Lambda logging level. One of: `["DEBUG", "INFO", "WARN", "ERROR"]`. | `string` | `"WARN"` | no |
| <a name="input_lambda_memory_size"></a> [lambda\_memory\_size](#input\_lambda\_memory\_size) | The amount of memory for Lambda to use | `number` | `"128"` | no |
| <a name="input_lambda_runtime"></a> [lambda\_runtime](#input\_lambda\_runtime) | The lambda runtime to use. One of: `["python3.9", "python3.8", "python3.7"]` | `string` | `"python3.8"` | no |
| <a name="input_log_retention_in_days"></a> [log\_retention\_in\_days](#input\_log\_retention\_in\_days) | Number of days to keep CloudWatch logs | `number` | `14` | no |
| <a name="input_naming_prefix"></a> [naming\_prefix](#input\_naming\_prefix) | Resources will be prefixed with this | `string` | `"clickops-notifier"` | no |
| <a name="input_standalone"></a> [standalone](#input\_standalone) | Deploy ClickOps in a standalone account instead of into an entire AWS Organization. Ideal for teams who want to monitor ClickOps in only their accounts where it is not instrumented at an Organizational level. | `bool` | `false` | no |
| <a name="input_subcription_filter_distribution"></a> [subcription\_filter\_distribution](#input\_subcription\_filter\_distribution) | The method used to distribute log data to the destination. By default log data is grouped by log stream, but the grouping can be set to random for a more even distribution. This property is only applicable when the destination is an Amazon Kinesis stream. Valid values are "Random" and "ByLogStream". | `string` | `"Random"` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags to add to resources in addition to the default\_tags for the provider | `map(string)` | `{}` | no |
| <a name="input_webhooks_for_msteams_notifications"></a> [webhooks\_for\_msteams\_notifications](#input\_webhooks\_for\_msteams\_notifications) | Map of `custom_name => webhook URL`s for MS Teams notifications. https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook?tabs=dotnet | `map(string)` | `{}` | no |
| <a name="input_webhooks_for_slack_notifications"></a> [webhooks\_for\_slack\_notifications](#input\_webhooks\_for\_slack\_notifications) | Map of `custom_name => webhook URL`s for Slack notifications. https://api.slack.com/messaging/webhooks | `map(string)` | `{}` | no |

----
### Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_clickops_notifier_lambda"></a> [clickops\_notifier\_lambda](#module\_clickops\_notifier\_lambda) | terraform-aws-modules/lambda/aws | 4.9.0 |

----
### Outputs

| Name | Description |
|------|-------------|
| <a name="output_clickops_notifier_lambda"></a> [clickops\_notifier\_lambda](#output\_clickops\_notifier\_lambda) | Expose all the outputs from the lambda module |
| <a name="output_sns_topic"></a> [sns\_topic](#output\_sns\_topic) | Expose the bucket notification SNS details |
| <a name="output_sqs_queue"></a> [sqs\_queue](#output\_sqs\_queue) | Expose the bucket notification SQS details |

----
### Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 4.9 |

----
### Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.15.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.9 |

----
### Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_log_subscription_filter.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_subscription_filter) | resource |
| [aws_s3_bucket_notification.bucket_notification](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_notification) | resource |
| [aws_s3_object.deployment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_object) | resource |
| [aws_sns_topic.bucket_notifications](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic) | resource |
| [aws_sns_topic_policy.bucket_notifications](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_policy) | resource |
| [aws_sns_topic_subscription.bucket_notifications](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_subscription) | resource |
| [aws_sqs_queue.bucket_notifications](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue) | resource |
| [aws_sqs_queue_policy.bucket_notifications](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue_policy) | resource |
| [aws_ssm_parameter.webhooks_for_msteams](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.webhooks_for_slack](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_cloudwatch_log_group.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/cloudwatch_log_group) | data source |
| [aws_iam_policy_document.bucket_notifications](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.lambda_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.sns_topic_policy_bucket_notifications](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |
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

    # Must CreateMultipartUpload before uploading any parts.
    "s3.amazonaws.com:UploadPart",
    "s3.amazonaws.com:UploadPartCopy",

    "route53domains:TransferDomain",

    "support.amazonaws.com:AddAttachmentsToSet",
    "support.amazonaws.com:AddCommunicationToCase",
    "support.amazonaws.com:CreateCase",
    "support.amazonaws.com:InitiateCallForCase",
    "support.amazonaws.com:InitiateChatForCase",
    "support.amazonaws.com:PutCaseAttributes",
    "support.amazonaws.com:RateCaseCommunication",
    "support.amazonaws.com:RefreshTrustedAdvisorCheck",
    "support.amazonaws.com:ResolveCase",

    "grafana.amazonaws.com:login_auth_sso",
  ]
}
```
<!-- END_TF_DOCS -->

----
