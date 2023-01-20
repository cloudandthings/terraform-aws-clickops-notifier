<!-- BEGIN_TF_DOCS -->
----
## main.tf
```hcl
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
| <a name="module_clickops_notifications"></a> [clickops\_notifications](#module\_clickops\_notifications) | ../../ | n/a |

----
### Outputs

No outputs.

----
### Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 4.9.0 |
| <a name="provider_random"></a> [random](#provider\_random) | 3.4.3 |

----
### Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.13.1 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | 4.9.0 |
| <a name="requirement_random"></a> [random](#requirement\_random) | 3.4.3 |

----
### Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_log_group.this](https://registry.terraform.io/providers/hashicorp/aws/4.9.0/docs/resources/cloudwatch_log_group) | resource |
| [random_pet.run_id](https://registry.terraform.io/providers/hashicorp/random/3.4.3/docs/resources/pet) | resource |

----
<!-- END_TF_DOCS -->
