locals {
  // https://github.com/phzietsman/aws-lambda-layer-common
  python_layers = {
    "ap-northeast-1" = "arn:aws:lambda:ap-northeast-1:306986787463:layer:common-python-libraries:1"
    "us-east-1"      = "arn:aws:lambda:us-east-1:306986787463:layer:common-python-libraries:1"
    "ap-southeast-1" = "arn:aws:lambda:ap-southeast-1:306986787463:layer:common-python-libraries:1"
    "eu-west-1"      = "arn:aws:lambda:eu-west-1:306986787463:layer:common-python-libraries:1"
    "us-west-1"      = "arn:aws:lambda:us-west-1:306986787463:layer:common-python-libraries:1"
    "ap-east-1"      = "arn:aws:lambda:ap-east-1:306986787463:layer:common-python-libraries:1"
    "ap-northeast-2" = "arn:aws:lambda:ap-northeast-2:306986787463:layer:common-python-libraries:1"
    "ap-northeast-3" = "arn:aws:lambda:ap-northeast-3:306986787463:layer:common-python-libraries:1"
    "ap-south-1"     = "arn:aws:lambda:ap-south-1:306986787463:layer:common-python-libraries:1"
    "ap-southeast-2" = "arn:aws:lambda:ap-southeast-2:306986787463:layer:common-python-libraries:1"
    "ca-central-1"   = "arn:aws:lambda:ca-central-1:306986787463:layer:common-python-libraries:1"
    "eu-central-1"   = "arn:aws:lambda:eu-central-1:306986787463:layer:common-python-libraries:1"
    "eu-north-1"     = "arn:aws:lambda:eu-north-1:306986787463:layer:common-python-libraries:1"
    "eu-west-2"      = "arn:aws:lambda:eu-west-2:306986787463:layer:common-python-libraries:1"
    "eu-west-3"      = "arn:aws:lambda:eu-west-3:306986787463:layer:common-python-libraries:1"
    "sa-east-1"      = "arn:aws:lambda:sa-east-1:306986787463:layer:common-python-libraries:1"
    "us-east-2"      = "arn:aws:lambda:us-east-2:306986787463:layer:common-python-libraries:1"
    "us-west-2"      = "arn:aws:lambda:us-west-2:306986787463:layer:common-python-libraries:1"
  }
}

data "aws_s3_bucket" "cloudtrail_bucket" {
  bucket = var.cloudtrail_bucket_name
}

data "aws_caller_identity" "current" {}
