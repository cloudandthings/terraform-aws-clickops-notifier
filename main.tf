data "aws_iam_policy_document" "lambda_permissions" {

  statement {
    sid = "SSMAccess"

    actions = [
      "ssm:GetParameter"
    ]

    resources = [
      aws_ssm_parameter.slack_webhook.arn
    ]
  }

  # Organizational deployment

  dynamic "statement" {

    for_each = !var.standalone ? toset(["organizational_deployment"]) : toset([])

    content {
      sid = "S3AccessBucket"

      actions = [
        "s3:ListBucket"
      ]

      resources = [
        data.aws_s3_bucket.cloudtrail_bucket[0].arn
      ]
    }
  }

  dynamic "statement" {

    for_each = !var.standalone ? toset(["organizational_deployment"]) : toset([])

    content {
      sid = "S3AccessBucketObject"

      actions = [
        "s3:GetObject"
      ]

      resources = [
        "${data.aws_s3_bucket.cloudtrail_bucket[0].arn}/*"
      ]
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

      resources = [
        aws_sqs_queue.bucket_notifications[0].arn
      ]
    }
  }
}

module "clickops_notifier_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "3.2.1"

  function_name = var.naming_prefix
  description   = "ClickOps Notifier Lambda"

  handler     = var.standalone ? "main.handler_standalone" : "main.handler_organizational"
  runtime     = var.lambda_runtime
  publish     = true
  source_path = "${path.module}/lambda/app"

  timeout     = var.event_processing_timeout
  memory_size = var.lambda_memory_size

  create_role = var.create_iam_role
  lambda_role = var.iam_role_arn

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_permissions.json

  attach_policy_statements = length(var.additional_iam_policy_statements) > 0
  policy_statements        = var.additional_iam_policy_statements

  cloudwatch_logs_retention_in_days = var.log_retention_in_days

  environment_variables = {
    WEBHOOK_PARAMETER = aws_ssm_parameter.slack_webhook.name

    EXCLUDED_ACCOUNTS = jsonencode(var.excluded_accounts)
    INCLUDED_ACCOUNTS = jsonencode(var.included_accounts)

    EXCLUDED_USERS = jsonencode(var.excluded_users)
    INCLUDED_USERS = jsonencode(var.included_users)

    EXCLUDED_SCOPED_ACTIONS = jsonencode(local.ignored_scoped_events)

    ADDITIONAL_METADATA = jsonencode(var.clickops_metadata)

    MESSAGE_FORMAT = var.message_format

    LOG_LEVEL = "INFO"
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
}

resource "aws_ssm_parameter" "slack_webhook" {

  name        = "/${var.naming_prefix}/slack-webhook"
  description = "Incomming webhook for clickops notifications."

  type  = "SecureString"
  value = var.webhook

  lifecycle {
    ignore_changes = [
      value,
    ]
  }
}
