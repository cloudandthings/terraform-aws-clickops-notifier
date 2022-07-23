
module "clickops_notifier_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "3.2.1"

  function_name = var.naming_prefix
  description   = "ClickOps Notifier Lambda"

  handler     = "main.handler"
  runtime     = var.lambda_runtime
  publish     = true
  source_path = "${path.module}/lambda/app"

  timeout     = var.event_processing_timeout
  memory_size = 128

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

    EXCLUDED_SCOPED_ACTIONS = jsonencode(local.excluded_scoped_actions)

    MESSAGE_FORMAT = var.message_format

    LOG_LEVEL = "INFO"
  }

  event_source_mapping = {
    sqs = {
      event_source_arn                   = aws_sqs_queue.bucket_notifications.arn
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
