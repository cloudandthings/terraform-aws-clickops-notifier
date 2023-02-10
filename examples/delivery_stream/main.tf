terraform {
  required_version = ">= 0.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.9"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}

locals {
  tags = {
    usage = "clickops-testing"
    run   = random_pet.run_id.id
  }

  naming_prefix = "clickops-test-basic-${random_pet.run_id.id}"
}

resource "random_pet" "run_id" {
  keepers = {
    # Generate a new pet name
    run_id = var.run_id
  }
}

#---------------------------------------
# Cloudtrail infrastructure - standalone
#---------------------------------------
# S3 bucket
module "logs_bucket" {
  source  = "trussworks/logs/aws"
  version = "~> 14"

  s3_bucket_name = local.naming_prefix

  allow_cloudtrail = true
  force_destroy    = true
}

# Cloudtrail
locals {
  naming_prefix_cloudtrail = "${local.naming_prefix}-cloudtrail"
  naming_prefix_firehose   = "${local.naming_prefix}-firehose"
}
module "aws_cloudtrail" {
  source  = "trussworks/cloudtrail/aws"
  version = "~> 4"

  s3_bucket_name = module.logs_bucket.aws_logs_bucket

  trail_name      = local.naming_prefix_cloudtrail
  iam_policy_name = local.naming_prefix_cloudtrail
  iam_role_name   = local.naming_prefix_cloudtrail

  cloudwatch_log_group_name = local.naming_prefix_cloudtrail
  log_retention_days        = 30
}

#---------------------------------------
# ClickOps module
#---------------------------------------
module "clickops_notifications" {
  source = "../.."

  standalone = true

  naming_prefix = local.naming_prefix

  webhook        = "https://fake.com"
  message_format = "slack"

  tags = local.tags

  # cloudtrail_bucket_name = aws_s3_bucket.clickops_cloudtrail.id
  cloudtrail_log_group = local.naming_prefix_cloudtrail

  firehose_delivery_stream_name = aws_kinesis_firehose_delivery_stream.extended_s3_stream.name

  depends_on = [
    module.aws_cloudtrail
  ]

}

#---------------------------------------
# Delivery stream infrastructure
#---------------------------------------
resource "aws_kinesis_firehose_delivery_stream" "extended_s3_stream" {
  name        = local.naming_prefix
  destination = "extended_s3"

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = aws_s3_bucket.firehose.arn

    compression_format = "UNCOMPRESSED"

    buffer_size     = 64
    buffer_interval = 300

    # Hive-style dynamic partitioning by recipientAccountId and awsRegion
    # https://docs.aws.amazon.com/firehose/latest/dev/dynamic-partitioning.html

    dynamic_partitioning_configuration {
      enabled = "true"
    }

    prefix = join("/", [
      "data",
      "recipientAccountId=!{partitionKeyFromQuery:recipientAccountId}",
      "awsRegion=!{partitionKeyFromQuery:awsRegion}",
      "year=!{timestamp:yyyy}", "month=!{timestamp:MM}", "day=!{timestamp:dd}", "hour=!{timestamp:HH}",
      ""
    ])
    error_output_prefix = join("/", [
      "errors",
      "year=!{timestamp:yyyy}", "month=!{timestamp:MM}", "day=!{timestamp:dd}", "hour=!{timestamp:HH}",
      "!{firehose:error-output-type}",
      ""
    ])

    processing_configuration {
      enabled = "true"

      # DeAggreagate records
      processors {
        type = "RecordDeAggregation"
        parameters {
          parameter_name  = "SubRecordType"
          parameter_value = "JSON"
        }
      }

      # Calculate partition variables
      processors {
        type = "MetadataExtraction"
        parameters {
          parameter_name  = "JsonParsingEngine"
          parameter_value = "JQ-1.6"
        }
        parameters {
          parameter_name  = "MetadataExtractionQuery"
          parameter_value = "{recipientAccountId:.recipientAccountId, awsRegion:.awsRegion}"
        }
      }

      # Append new line between output records
      processors {
        type = "AppendDelimiterToRecord"
      }
    }
  }
}

resource "aws_s3_bucket" "firehose" {
  bucket = local.naming_prefix_firehose
}

resource "aws_s3_bucket_acl" "firehose_bucket_acl" {
  bucket = aws_s3_bucket.firehose.id
  acl    = "private"
}

resource "aws_iam_role" "firehose" {
  name = local.naming_prefix_firehose

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "firehose.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "firehose" {
  name   = local.naming_prefix_firehose
  role   = aws_iam_role.firehose.id
  policy = data.aws_iam_policy_document.firehose.json
}

data "aws_iam_policy_document" "firehose" {
  statement {
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:PutObject"
    ]

    resources = [
      aws_s3_bucket.firehose.arn,
      "${aws_s3_bucket.firehose.arn}/*"
    ]
  }
}
