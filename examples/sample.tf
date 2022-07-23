terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.49.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "clickops_notifications" {
  source = "../"

  cloudtrail_bucket_name = var.cloudtrail_bucket_name
  webhook                = var.webhook
  message_format         = "slack"
}

variable "cloudtrail_bucket_name" {}
variable "webhook" {}
