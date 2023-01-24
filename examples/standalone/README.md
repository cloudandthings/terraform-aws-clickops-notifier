<!-- BEGIN_TF_DOCS -->
----
## main.tf
```hcl
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

locals {
  naming_prefix            = "clickops-test-stand-${random_pet.run_id.id}"
  naming_prefix_cloudtrail = "${local.naming_prefix}-cloudtrail"
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

  tags = {}

  depends_on = [module.aws_cloudtrail]
}
```
----

## Documentation

----
### Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_run_id"></a> [run\_id](#input\_run\_id) | Used to ensure resources are unique | `string` | n/a | yes |

----
### Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_aws_cloudtrail"></a> [aws\_cloudtrail](#module\_aws\_cloudtrail) | trussworks/cloudtrail/aws | ~> 4 |
| <a name="module_clickops_notifications"></a> [clickops\_notifications](#module\_clickops\_notifications) | ../../ | n/a |
| <a name="module_logs_bucket"></a> [logs\_bucket](#module\_logs\_bucket) | trussworks/logs/aws | ~> 14 |

----
### Outputs

No outputs.

----
### Providers

| Name | Version |
|------|---------|
| <a name="provider_random"></a> [random](#provider\_random) | 3.4.3 |

----
### Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.14.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | 4.9.0 |
| <a name="requirement_random"></a> [random](#requirement\_random) | 3.4.3 |

----
### Resources

| Name | Type |
|------|------|
| [random_pet.run_id](https://registry.terraform.io/providers/hashicorp/random/3.4.3/docs/resources/pet) | resource |

----
<!-- END_TF_DOCS -->
