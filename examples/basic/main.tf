terraform {
  required_version = ">= 0.15.0"

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

module "clickops_notifications" {
  source = "../../"

  naming_prefix          = local.naming_prefix
  cloudtrail_bucket_name = aws_s3_bucket.test_bucket.id

  webhooks_for_slack_notifications = {
    my-first-notification : "https://fake.com"
  }
  webhooks_for_msteams_notifications = {
    my-second-notification : "https://fake.com"
  }

  tags = local.tags

  # Optional
  kms_key_id_for_sns_topic = aws_kms_key.clickops_sns_topic.arn
}


resource "aws_s3_bucket" "test_bucket" {
  bucket = local.naming_prefix
  tags   = local.tags
}

# To encrypt the SNS topic
data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "clickops_sns_topic" {
  statement {
    sid = "Enable IAM User Permissions"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }
  statement {
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
    actions = [
      "kms:GenerateDataKey*",
      "kms:Decrypt"
    ]
    resources = ["*"]
    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_s3_bucket.test_bucket.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

resource "aws_kms_key" "clickops_sns_topic" {
  description             = "KMS key for SNS topic ${local.naming_prefix}"
  deletion_window_in_days = 7
  policy                  = data.aws_iam_policy_document.clickops_sns_topic.json

  tags = local.tags
}
