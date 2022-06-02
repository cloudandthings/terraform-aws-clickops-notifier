data "aws_s3_bucket" "cloudtrail_bucket" {
  bucket = var.cloudtrail_bucket_name
}

data "aws_caller_identity" "current" {}
