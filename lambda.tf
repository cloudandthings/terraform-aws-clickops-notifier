resource "aws_lambda_function" "func" {

  function_name = var.naming_prefix
  role          = aws_iam_role.lambda.arn

  handler = "main.handler"
  runtime = "python3.8"

  filename         = data.archive_file.func.output_path
  source_code_hash = filebase64sha256(data.archive_file.func.output_path)

  timeout     = var.event_processing_timeout
  memory_size = 128

  layers = [local.python_layers[var.region]]

  environment {
    variables = {
      WEBHOOK_PARAMETER = aws_ssm_parameter.slack_webhook.name
      EXCLUDED_ACCOUNTS = jsonencode(var.excluded_accounts)
      INCLUDED_ACCOUNTS = jsonencode(var.included_accounts)

      EXCLUDED_USERS = jsonencode(var.excluded_users)
      INCLUDED_USERS = jsonencode(var.included_users)

      LOG_LEVEL         = "INFO"
    }
  }

  tags = var.tags
}

data "archive_file" "func" {
  type             = "zip"
  source_dir       = "${path.module}/lambda/app"
  output_file_mode = "0666"
  output_path      = "${path.module}/lambda.zip"
}

resource "aws_lambda_event_source_mapping" "bucket_notifications" {
  event_source_arn = aws_sqs_queue.bucket_notifications.arn
  function_name    = aws_lambda_function.func.arn

  batch_size                         = var.event_batch_size
  maximum_batching_window_in_seconds = var.event_maximum_batching_window

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
