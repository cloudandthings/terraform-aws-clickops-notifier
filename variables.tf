# -------------------------------------------------------------------------------------
# Required Variables
# -------------------------------------------------------------------------------------
variable "standalone" {
  type        = bool
  description = "Deploy ClickOps in a standalone account instead of into an entire AWS Organization. Ideal for teams who want to monitor ClickOps in only their accounts where it is not instrumented at an Organizational level."
  default     = false
}

variable "cloudtrail_log_group" {
  type        = string
  description = "CloudWatch Log group for CloudTrail events."
  default     = ""
}

variable "cloudtrail_bucket_name" {
  type        = string
  description = "Bucket containing the Cloudtrail logs that you want to process. ControlTower bucket name follows this naming convention `aws-controltower-logs-{{account_id}}-{{region}}`"
  default     = ""
}

variable "webhooks_for_slack_notifications" {
  type        = map(string)
  description = "Map of `custom_name => webhook URL`s for Slack notifications. https://api.slack.com/messaging/webhooks"
  sensitive   = true
  default     = {}
}

variable "webhooks_for_msteams_notifications" {
  type        = map(string)
  description = "Map of `custom_name => webhook URL`s for MS Teams notifications. https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook?tabs=dotnet"
  sensitive   = true
  default     = {}
}


# -------------------------------------------------------------------------------------
# Optional Variables
# -------------------------------------------------------------------------------------

variable "excluded_accounts" {
  type        = list(string)
  description = "List of accounts that be excluded for scans on manual actions. These take precidence over `included_accounts`"
  default     = []
}

variable "included_accounts" {
  type        = list(string)
  description = "List of accounts that be scanned to manual actions. If empty will scan all accounts."
  default     = []
}

variable "excluded_users" {
  type        = list(string)
  description = "List of email addresses will not be reported on when practicing ClickOps."
  default     = []
}

variable "included_users" {
  type        = list(string)
  description = "List of emails that be scanned to manual actions. If empty will scan all emails."
  default     = []
}

variable "excluded_scoped_actions" {
  type        = list(string)
  description = "A list of service scoped actions that will not be alerted on. Format {{service}}.amazonaws.com:{{action}}"
  default     = []
}

variable "excluded_scoped_actions_effect" {
  type        = string
  description = "Should the existing exluded actions be replaces or appended to. By default it will append to the list, valid values: APPEND, REPLACE"
  default     = "APPEND"

  validation {
    condition = contains([
      "APPEND",
      "REPLACE"
    ], var.excluded_scoped_actions_effect)
    error_message = "Invalid excluded_scoped_actions_effect provided. Should be one of: APPEND, REPLACE."
  }
}

# Infrastructure optional variables
variable "naming_prefix" {
  type        = string
  description = "Resources will be prefixed with this"
  default     = "clickops-notifier"
}

variable "cloudtrail_bucket_notifications_sns_arn" {
  type        = string
  description = "SNS topic ARN for bucket notifications. If not provided, a new SNS topic will be created along with the bucket notifications configuration."
  default     = null
}

variable "tags" {
  type        = map(string)
  description = "Tags to add to resources in addition to the default_tags for the provider"
  default     = {}
}

# Event processing configuration
variable "event_processing_timeout" {
  type        = number
  description = "Maximum number of seconds the lambda is allowed to run and number of seconds events should be hidden in SQS after being picked up my Lambda."
  default     = 60
}

variable "event_batch_size" {
  type        = number
  description = "Batch events into chunks of `event_batch_size`"
  default     = 100
}

variable "event_maximum_batching_window" {
  type        = number
  description = "Maximum batching window in seconds."
  default     = 300
}

variable "log_retention_in_days" {
  type        = number
  description = "Number of days to keep CloudWatch logs"
  default     = 14
}

# Lambda configuration
variable "lambda_deployment_s3_bucket" {
  description = "S3 bucket for lambda deployment package."
  type        = string
  default     = null
}

variable "lambda_deployment_s3_key" {
  description = "S3 object key for lambda deployment package. Otherwise, defaults to `var.naming_prefix/local.deployment_filename`."
  type        = string
  default     = null
}

variable "lambda_deployment_upload_to_s3_enabled" {
  description = "If `true`, the lambda deployment package within this module repo will be copied to S3. If `false` then the S3 object must be uploaded separately. Ignored if `lambda_deployment_s3_bucket` is null."
  type        = bool
  default     = true
}

variable "lambda_runtime" {
  type        = string
  description = "The lambda runtime to use. One of: `[\"python3.9\", \"python3.8\", \"python3.11\"]`"
  default     = "python3.11"

  validation {
    condition = contains([
      "python3.9",
      "python3.8",
      "python3.11"
    ], var.lambda_runtime)
    error_message = "Invalid lambda_runtime provided."
  }
}

variable "lambda_memory_size" {
  type        = number
  description = "The amount of memory for Lambda to use"
  default     = "128"
}

variable "lambda_log_level" {
  description = "Lambda logging level. One of: `[\"DEBUG\", \"INFO\", \"WARN\", \"ERROR\"]`."
  type        = string
  default     = "WARN"

  validation {
    condition = contains([
      "DEBUG",
      "INFO",
      "WARN",
      "ERROR"
    ], var.lambda_log_level)
    error_message = "Invalid lambda_log_level provided."
  }
}

# IAM configuration
variable "create_iam_role" {
  description = "Determines whether a an IAM role is created or to use an existing IAM role"
  type        = bool
  default     = true
}

variable "iam_role_arn" {
  description = "Existing IAM role ARN for the lambda. Required if `create_iam_role` is set to `false`"
  type        = string
  default     = null
}

variable "additional_iam_policy_statements" {
  description = "Map of dynamic policy statements to attach to Lambda Function role"
  type        = any
  default     = {}
}

# Encryption configuration
variable "kms_key_id_for_sns_topic" {
  description = "KMS key ID for encrypting the sns_topic (only applicable to org deployments)."
  type        = string
  default     = null
}

# Other configuration
variable "allowed_aws_principals_for_sns_subscribe" {
  description = "List of AWS principals allowed to subscribe to the SNS topic (only applicable to org deployments)."
  type        = list(string)
  default     = []
}

variable "firehose_delivery_stream_name" {
  description = "Kinesis Firehose delivery stream name to output ClickOps events to."
  type        = string
  default     = null
}

variable "subcription_filter_distribution" {
  description = "The method used to distribute log data to the destination. By default log data is grouped by log stream, but the grouping can be set to random for a more even distribution. This property is only applicable when the destination is an Amazon Kinesis stream. Valid values are \"Random\" and \"ByLogStream\"."
  type        = string
  default     = "Random"

  validation {
    condition = contains([
      "Random",
      "ByLogStream"
    ], var.subcription_filter_distribution)
    error_message = "Invalid subcription_filter_distribution provided."
  }
}
