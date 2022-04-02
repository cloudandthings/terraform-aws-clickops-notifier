# Required Variables
variable "cloudtrail_bucket_name" {
  type        = string
  description = "Bucket containing the Cloudtrail logs that you want to process. ControlTower bucket name follows this naming convention `aws-controltower-logs-{{account_id}}-{{region}}`"
}

variable "webhook" {
  type        = string
  description = "The webhook URL for notifications. https://api.slack.com/messaging/webhooks"
  sensitive   = true
}

variable "region" {
  type        = string
  description = "Region where this will be deployed. Used for [getting the correct lambda layer]"

  validation {
    condition = contains([
      "ap-northeast-1",
      "us-east-1",
      "ap-southeast-1",
      "eu-west-1",
      "us-west-1",
      "ap-east-1",
      "ap-northeast-2",
      "ap-northeast-3",
      "ap-south-1",
      "ap-southeast-2",
      "ca-central-1",
      "eu-central-1",
      "eu-north-1",
      "eu-west-2",
      "eu-west-3",
      "sa-east-1",
      "us-east-2",
      "us-west-2"
    ], var.region)
    error_message = "Invalid region provided."
  }
}


# Application Related Optional Variables

variable "message_format" {
  type        = string
  description = "Where do you want to send this message? Only slack, for now."
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

