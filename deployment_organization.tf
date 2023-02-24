#--------------------------------------------------------------------------------------
# OVERVIEW
#--------------------------------------------------------------------------------------

# We will use SNS for bucket notifications which can then be routed to multiple subscribers.
# This enables fan-out to other interested subscribers if needed.
# One such subscriber will be SQS and the ClickOps lambda will subscribe to the SQS queue.

# Ref: https://aws.amazon.com/blogs/compute/fanout-s3-event-notifications-to-multiple-endpoints/

#--------------------------------------------------------------------------------------
# aws_s3_bucket
#--------------------------------------------------------------------------------------
data "aws_s3_bucket" "cloudtrail_bucket" {
  count = var.standalone ? 0 : 1

  bucket = var.cloudtrail_bucket_name
}

#--------------------------------------------------------------------------------------
# aws_sns_topic
#--------------------------------------------------------------------------------------
resource "aws_sns_topic" "bucket_notifications" {
  count = var.standalone ? 0 : 1

  name = var.naming_prefix
  # Cannot use AWS managed KMS key with S3 bucket notifications
  # Ref: https://aws.amazon.com/premiumsupport/knowledge-center/sns-not-receiving-s3-event-notifications/
  # kms_master_key_id = "alias/aws/sns"

  tags = var.tags
}

data "aws_iam_policy_document" "sns_topic_policy_bucket_notifications" {
  count = var.standalone ? 0 : 1

  statement {
    actions   = ["SNS:Publish"]
    effect    = "Allow"
    resources = [aws_sns_topic.bucket_notifications[0].arn]
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [data.aws_s3_bucket.cloudtrail_bucket[0].arn]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

resource "aws_sns_topic_policy" "bucket_notifications" {
  count = var.standalone ? 0 : 1

  arn    = aws_sns_topic.bucket_notifications[0].arn
  policy = data.aws_iam_policy_document.sns_topic_policy_bucket_notifications[0].json

}

#--------------------------------------------------------------------------------------
# aws_s3_bucket_notification
#--------------------------------------------------------------------------------------
resource "aws_s3_bucket_notification" "bucket_notification" {
  count = var.standalone ? 0 : 1

  bucket = data.aws_s3_bucket.cloudtrail_bucket[0].id

  topic {
    topic_arn     = aws_sns_topic.bucket_notifications[0].arn
    events        = ["s3:ObjectCreated:*"]
    filter_suffix = ".json.gz"
  }

  depends_on = [
    aws_sns_topic_policy.bucket_notifications
  ]
}

#--------------------------------------------------------------------------------------
# aws_sqs_queue
#--------------------------------------------------------------------------------------
resource "aws_sqs_queue" "bucket_notifications" {
  count = var.standalone ? 0 : 1

  name                       = var.naming_prefix
  visibility_timeout_seconds = var.event_processing_timeout + 5

  sqs_managed_sse_enabled = true
  tags                    = var.tags
}

data "aws_iam_policy_document" "bucket_notifications" {
  count = var.standalone ? 0 : 1

  statement {
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.bucket_notifications[0].arn]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.bucket_notifications[0].arn]
    }
  }
}

resource "aws_sqs_queue_policy" "bucket_notifications" {
  count = var.standalone ? 0 : 1

  queue_url = aws_sqs_queue.bucket_notifications[0].id
  policy    = data.aws_iam_policy_document.bucket_notifications[0].json
}

#--------------------------------------------------------------------------------------
# aws_sns_topic_subscription
#--------------------------------------------------------------------------------------
resource "aws_sns_topic_subscription" "bucket_notifications" {
  count = var.standalone ? 0 : 1

  topic_arn = aws_sns_topic.bucket_notifications[0].arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.bucket_notifications[0].arn
}
