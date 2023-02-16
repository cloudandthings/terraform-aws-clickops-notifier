<!-- BEGIN_TF_DOCS -->
----
## main.tf
```hcl
terraform {
  required_version = ">= 0.14.0"

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
  webhook                = "https://fake.com"
  message_format         = "slack"
  tags                   = local.tags
}


resource "aws_s3_bucket" "test_bucket" {
  bucket = local.naming_prefix
  tags   = local.tags
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
| <a name="provider_aws"></a> [aws](#provider\_aws) | ~> 4.9 |
| <a name="provider_random"></a> [random](#provider\_random) | ~> 3.4 |

----
### Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.14.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 4.9 |
| <a name="requirement_random"></a> [random](#requirement\_random) | ~> 3.4 |

----
### Resources

| Name | Type |
|------|------|
| [aws_s3_bucket.test_bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [random_pet.run_id](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/pet) | resource |

----
<!-- END_TF_DOCS -->
