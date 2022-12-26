terraform {
  required_version = ">= 0.13.1"

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
    uasage = "clickops-testing"
    run    = random_pet.run_id.id
  }

  naming_prefix = "clickops-test-basic-${random_pet.run_id.id}"
}

resource "random_pet" "run_id" {
  keepers = {
    # Generate a new pet name each time we switch to a new AMI id
    run_id = var.run_id
  }
}

module "clickops_notifications" {
  source = "../../"

  standalone           = true
  naming_prefix        = local.naming_prefix
  cloudtrail_log_group = "aws-controltower/CloudTrailLogs"
  webhook              = "https://fake.com"
  message_format       = "slack"
  tags                 = local.tags
  lambda_runtime       = "python3.9"
}
