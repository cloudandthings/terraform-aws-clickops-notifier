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

  webhooks_for_slack_notifications = {
    my-first-notification : "https://fake.com"
  }
  webhooks_for_msteams_notifications = {
    my-second-notification : "https://fake.com"
  }

  tags = local.tags

  # cloudtrail_bucket_name = aws_s3_bucket.clickops_cloudtrail.id
  cloudtrail_log_group = local.naming_prefix_cloudtrail

  depends_on = [
    module.aws_cloudtrail
  ]

}
