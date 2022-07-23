data "aws_s3_bucket" "cloudtrail_bucket" {
  bucket = var.cloudtrail_bucket_name
}

locals {
  ignored_scoped_events = var.excluded_scoped_actions_effect == "APPEND" ? concat(local.ignored_scoped_events_built_in, var.excluded_scoped_actions) : var.excluded_scoped_actions
}
