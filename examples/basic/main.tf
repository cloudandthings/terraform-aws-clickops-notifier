terraform {
  required_version = ">= 0.13.1"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.9.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "clickops_notifications" {
  source = "../../"

  cloudtrail_bucket_name = var.cloudtrail_bucket_name
  webhook                = var.webhook
  message_format         = "slack"
}
