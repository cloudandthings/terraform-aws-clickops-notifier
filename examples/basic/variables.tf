variable "region" {
  type        = string
  description = "Region to deploy resources in"
}


variable "cloudtrail_bucket_name" {
  type        = string
  description = "Bucket containing the Cloudtrail logs that you want to process. ControlTower bucket name follows this naming convention `aws-controltower-logs-{{account_id}}-{{region}}`"
}

variable "webhook" {
  type        = string
  description = "The webhook URL for notifications. https://api.slack.com/messaging/webhooks"
  sensitive   = true
}
