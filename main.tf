data "aws_iam_policy_document" "lambda_permissions" {

  statement {
    sid       = "SSMAccess"
    actions   = ["ssm:GetParameter"]
    resources = ["arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${var.naming_prefix}/webhooks-*"]
  }

  # Organizational deployment
  dynamic "statement" {
    for_each = !var.standalone ? toset(["organizational_deployment"]) : toset([])
    content {
      sid       = "S3AccessBucket"
      actions   = ["s3:ListBucket"]
      resources = [data.aws_s3_bucket.cloudtrail_bucket[0].arn]
    }
  }

  dynamic "statement" {
    for_each = !var.standalone ? toset(["organizational_deployment"]) : toset([])
    content {
      sid       = "S3AccessBucketObject"
      actions   = ["s3:GetObject"]
      resources = ["${data.aws_s3_bucket.cloudtrail_bucket[0].arn}/*"]
    }
  }

  dynamic "statement" {
    for_each = !var.standalone ? toset(["organizational_deployment"]) : toset([])
    content {
      sid = "SQSAccess"
      actions = [
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:ReceiveMessage"
      ]
      resources = [aws_sqs_queue.bucket_notifications[0].arn]
    }
  }
}

locals {
  deployment_filename     = "deployment-clickopsnotifier-${var.lambda_runtime}.zip"
  deployment_path         = "${path.module}/${local.deployment_filename}"
  deployment_upload_to_s3 = var.lambda_deployment_upload_to_s3_enabled && (var.lambda_deployment_s3_bucket != null)
  deployment_s3_key = coalesce(
    var.lambda_deployment_s3_key,
    join("/", [var.naming_prefix, local.deployment_filename])
  )
}

resource "aws_s3_object" "deployment" {
  count = local.deployment_upload_to_s3 ? 1 : 0

  bucket = var.lambda_deployment_s3_bucket
  key    = local.deployment_s3_key
  source = local.deployment_path

  etag = filemd5(local.deployment_path)
}

module "clickops_notifier_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "4.9.0"

  function_name = var.naming_prefix
  description   = "ClickOps Notifier Lambda"

  handler     = var.standalone ? "app.handler_standalone" : "app.handler_organizational"
  runtime     = var.lambda_runtime
  timeout     = var.event_processing_timeout
  memory_size = var.lambda_memory_size

  # Where should we get the package from?
  create_package         = false
  local_existing_package = var.lambda_deployment_s3_bucket == null ? local.deployment_path : null
  s3_existing_package = (
    var.lambda_deployment_s3_bucket == null
    ? null
    : {
      bucket = var.lambda_deployment_s3_bucket
      key    = local.deployment_s3_key
    }
  )

  # Publish creation/changes as a new Lambda Function Version
  publish = true

  create_lambda_function_url = false

  # Logs
  cloudwatch_logs_retention_in_days = var.log_retention_in_days

  # IAM
  create_role = var.create_iam_role
  lambda_role = var.iam_role_arn

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_permissions.json

  attach_policy_statements = length(var.additional_iam_policy_statements) > 0
  policy_statements        = var.additional_iam_policy_statements

  environment_variables = {
    WEBHOOKS_FOR_SLACK   = jsonencode(aws_ssm_parameter.webhooks_for_slack[*].name)
    WEBHOOKS_FOR_MSTEAMS = jsonencode(aws_ssm_parameter.webhooks_for_msteams[*].name)

    EXCLUDED_ACCOUNTS = jsonencode(var.excluded_accounts)
    INCLUDED_ACCOUNTS = jsonencode(var.included_accounts)

    EXCLUDED_USERS = jsonencode(var.excluded_users)
    INCLUDED_USERS = jsonencode(var.included_users)

    EXCLUDED_SCOPED_ACTIONS = jsonencode(local.ignored_scoped_events)

    LOG_LEVEL = var.lambda_log_level

    FIREHOSE_DELIVERY_STREAM_NAME = coalesce(var.firehose_delivery_stream_name, "__NONE__")
  }

  allowed_triggers = var.standalone ? {
    permission = {
      statement_id = "AllowExecutionFromCloudWatch"
      principal    = "logs.amazonaws.com"
      source_arn   = "${data.aws_cloudwatch_log_group.this[0].arn}:*"
    }
  } : {}

  event_source_mapping = var.standalone ? {} : {
    src = {
      event_source_arn                   = aws_sqs_queue.bucket_notifications[0].arn
      batch_size                         = var.event_batch_size
      maximum_batching_window_in_seconds = var.event_maximum_batching_window
    }
  }

  tags = var.tags

  depends_on = [aws_s3_object.deployment]
}

resource "aws_ssm_parameter" "webhooks_for_slack" {
  for_each = nonsensitive(toset(keys(var.webhooks_for_slack_notifications)))

  name        = "/${var.naming_prefix}/webhooks-for-slack/${each.key}"
  description = "Webhook \"${each.key}\" for clickops notifications via Slack."
  type        = "SecureString"
  value       = var.webhooks_for_slack_notifications[each.key]

  tags = var.tags
}

resource "aws_ssm_parameter" "webhooks_for_msteams" {
  for_each = nonsensitive(toset(keys(var.webhooks_for_msteams_notifications)))

  name        = "/${var.naming_prefix}/webhooks-for-msteams/${each.key}"
  description = "Webhook \"${each.key}\" for clickops notifications via MS Teams."
  type        = "SecureString"
  value       = var.webhooks_for_msteams_notifications[each.key]

  tags = var.tags
}
