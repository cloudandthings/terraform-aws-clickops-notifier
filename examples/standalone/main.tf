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

  naming_prefix = "clickops-test-basic-${random_pet.run_id.id}"
}

resource "random_pet" "run_id" {
  keepers = {
    # Generate a new pet name
    run_id = var.run_id
  }
}

resource "aws_cloudwatch_log_group" "this" {
  name              = local.naming_prefix
  retention_in_days = 1
}

module "clickops_notifications" {
  source = "../../"

  standalone           = true
  naming_prefix        = local.naming_prefix
  cloudtrail_log_group = aws_cloudwatch_log_group.this.name
  webhook              = "https://fake.com"
  message_format       = "slack"
  tags                 = local.tags
  lambda_runtime       = "python3.8"
}
