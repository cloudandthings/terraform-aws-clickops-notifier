terraform {
  required_version = ">= 0.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.9.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "3.4.3"
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

  naming_prefix            = "clickops-test-basic-${random_pet.run_id.id}"
  naming_prefix_cloudtrail = "${local.naming_prefix}-cloudtrail"
}

resource "random_pet" "run_id" {
  keepers = {
    # Generate a new pet name
    run_id = var.run_id
  }
}

#---------------------------------------
# Supporting infrastructure
#---------------------------------------
# S3 bucket
module "logs_bucket" {
  source  = "trussworks/logs/aws"
  version = "~> 14"

  s3_bucket_name = local.naming_prefix

  allow_cloudtrail = true
  force_destroy    = true

  tags = local.tags
}

# Cloudtrail with S3 and cloudwatch logs
module "aws_cloudtrail" {
  source  = "trussworks/cloudtrail/aws"
  version = "~> 4"

  s3_bucket_name = module.logs_bucket.aws_logs_bucket

  trail_name      = local.naming_prefix_cloudtrail
  iam_policy_name = local.naming_prefix_cloudtrail
  iam_role_name   = local.naming_prefix_cloudtrail

  cloudwatch_log_group_name = local.naming_prefix_cloudtrail
  log_retention_days        = 30

  tags = local.tags
}

#---------------------------------------
# Setup module
#---------------------------------------
module "clickops_notifications" {
  source = "../../"

  naming_prefix = local.naming_prefix
  standalone    = true

  cloudtrail_log_group = local.naming_prefix_cloudtrail

  webhook        = "https://fake.com"
  message_format = "slack"

  tags = local.tags

  depends_on = [module.aws_cloudtrail]
}
