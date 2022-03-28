resource "aws_iam_role" "lambda" {
  name               = var.naming_prefix
  assume_role_policy = data.aws_iam_policy_document.lambda_role_trust.json

  tags = var.tags
}

data "aws_iam_policy_document" "lambda_role_trust" {
  statement {
    sid = "LambdaTrust"

    actions = [
      "sts:AssumeRole"
    ]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "lambda_permissions" {
  name   = var.naming_prefix
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda_permissions.json
}

data "aws_iam_policy_document" "lambda_permissions" {
  statement {
    sid = "LoggingCreateLogGroup"

    actions = [
      "logs:CreateLogGroup"
    ]

    resources = [
      "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:${aws_cloudwatch_log_group.func.name}"
    ]
  }

  statement {
    sid = "LoggingPutEvents"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:${aws_cloudwatch_log_group.func.name}:log-stream:*"
    ]
  }

  statement {
    sid = "S3AccessBucket"

    actions = [
      "s3:ListBucket"
    ]

    resources = [
      "${data.aws_s3_bucket.cloudtrail_bucket.arn}"
    ]
  }

  statement {
    sid = "S3AccessBucketObject"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${data.aws_s3_bucket.cloudtrail_bucket.arn}/*"
    ]
  }

  statement {
    sid = "SSMAccess"

    actions = [
      "ssm:GetParameter"
    ]

    resources = [
      aws_ssm_parameter.slack_webhook.arn
    ]
  }

  statement {
    sid = "SQSAccess"

    actions = [
      "sqs:*"
    ]

    resources = [
      aws_sqs_queue.bucket_notifications.arn
    ]
  }
}
