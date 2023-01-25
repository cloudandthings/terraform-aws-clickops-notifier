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
  webhook                = "https://fake.com"
  message_format         = "slack"
  tags                   = local.tags
}


resource "aws_s3_bucket" "test_bucket" {
  bucket = local.naming_prefix
  tags   = local.tags
}
