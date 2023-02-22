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

variable "webhook" {
  type        = string
  description = "The webhook URL for notifications. https://api.slack.com/messaging/webhooks"
  sensitive   = true
}

# -------------------------------------------------------------------------------------
# Optional Variables
# -------------------------------------------------------------------------------------

# Application Related Optional Variables
variable "message_format" {
  type        = string
  description = "Where do you want to send this message? slack or msteams"
  default     = "slack"

  validation {
    condition = contains([
      "slack",
      "msteams"
    ], var.message_format)
    error_message = "Invalid message_format provided."
  }
}

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
  default     = 10
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
  description = "The lambda runtime to use. One of: `[\"python3.9\", \"python3.8\", \"python3.7\"]`"
  default     = "python3.8"

  validation {
    condition = contains([
      "python3.9",
      "python3.8",
      "python3.7"
    ], var.lambda_runtime)
    error_message = "Invalid lambda_runtime provided."
  }
}

variable "lambda_memory_size" {
  type        = number
  description = "The amount of memory for Lambda to use"
  default     = "128"
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

# Other configuration
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
