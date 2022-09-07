data "aws_iam_policy_document" "lambda_permissions" {
  statement {
    sid = "S3AccessBucket"

    actions = [
      "s3:ListBucket"
    ]

    resources = [
      data.aws_s3_bucket.cloudtrail_bucket.arn
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
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:ReceiveMessage"
    ]

    resources = [
      aws_sqs_queue.bucket_notifications.arn
    ]
  }
}
