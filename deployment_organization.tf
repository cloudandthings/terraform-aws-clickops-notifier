data "aws_s3_bucket" "cloudtrail_bucket" {
  count = var.standalone ? 0 : 1

  bucket = var.cloudtrail_bucket_name
}


resource "aws_sqs_queue" "bucket_notifications" {
  count = var.standalone ? 0 : 1

  name                       = var.naming_prefix
  visibility_timeout_seconds = var.event_processing_timeout + 5
}

data "aws_iam_policy_document" "bucket_notifications" {
  count = var.standalone ? 0 : 1

  statement {
    actions = [
      "sqs:SendMessage"
    ]

    resources = [aws_sqs_queue.bucket_notifications[0].arn]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [data.aws_s3_bucket.cloudtrail_bucket[0].arn]
    }

  }
}

resource "aws_sqs_queue_policy" "bucket_notifications" {
  count = var.standalone ? 0 : 1

  queue_url = aws_sqs_queue.bucket_notifications[0].id
  policy    = data.aws_iam_policy_document.bucket_notifications[0].json
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  count = var.standalone ? 0 : 1

  bucket = data.aws_s3_bucket.cloudtrail_bucket[0].id

  queue {
    queue_arn     = aws_sqs_queue.bucket_notifications[0].arn
    events        = ["s3:ObjectCreated:*"]
    filter_suffix = ".json.gz"
  }

  depends_on = [
    aws_sqs_queue_policy.bucket_notifications
  ]
}
