locals {
  // https://aws.amazon.com/blogs/compute/upcoming-changes-to-the-python-sdk-in-aws-lambda/
  python_layers = {
    "ap-northeast-1" = "arn:aws:lambda:ap-northeast-1:249908578461:layer:AWSLambda-Python-AWS-SDK:4"
    "us-east-1"      = "arn:aws:lambda:us-east-1:668099181075:layer:AWSLambda-Python-AWS-SDK:4"
    "ap-southeast-1" = "arn:aws:lambda:ap-southeast-1:468957933125:layer:AWSLambda-Python-AWS-SDK:4"
    "eu-west-1"      = "arn:aws:lambda:eu-west-1:399891621064:layer:AWSLambda-Python-AWS-SDK:4"
    "us-west-1"      = "arn:aws:lambda:us-west-1:325793726646:layer:AWSLambda-Python-AWS-SDK:4"
    "ap-east-1"      = "arn:aws:lambda:ap-east-1:118857876118:layer:AWSLambda-Python-AWS-SDK:4"
    "ap-northeast-2" = "arn:aws:lambda:ap-northeast-2:296580773974:layer:AWSLambda-Python-AWS-SDK:4"
    "ap-northeast-3" = "arn:aws:lambda:ap-northeast-3:961244031340:layer:AWSLambda-Python-AWS-SDK:4"
    "ap-south-1"     = "arn:aws:lambda:ap-south-1:631267018583:layer:AWSLambda-Python-AWS-SDK:4"
    "ap-southeast-2" = "arn:aws:lambda:ap-southeast-2:817496625479:layer:AWSLambda-Python-AWS-SDK:4"
    "ca-central-1"   = "arn:aws:lambda:ca-central-1:778625758767:layer:AWSLambda-Python-AWS-SDK:4"
    "eu-central-1"   = "arn:aws:lambda:eu-central-1:292169987271:layer:AWSLambda-Python-AWS-SDK:4"
    "eu-north-1"     = "arn:aws:lambda:eu-north-1:642425348156:layer:AWSLambda-Python-AWS-SDK:4"
    "eu-west-2"      = "arn:aws:lambda:eu-west-2:142628438157:layer:AWSLambda-Python-AWS-SDK:4"
    "eu-west-3"      = "arn:aws:lambda:eu-west-3:959311844005:layer:AWSLambda-Python-AWS-SDK:4"
    "sa-east-1"      = "arn:aws:lambda:sa-east-1:640010853179:layer:AWSLambda-Python-AWS-SDK:4"
    "us-east-2"      = "arn:aws:lambda:us-east-2:259788987135:layer:AWSLambda-Python-AWS-SDK:4"
    "us-west-2"      = "arn:aws:lambda:us-west-2:420165488524:layer:AWSLambda-Python-AWS-SDK:5"
    "cn-north-1"     = "arn:aws-cn:lambda:cn-north-1:683298794825:layer:AWSLambda-Python-AWS-SDK:4"
    "cn-northwest-1" = "arn:aws-cn:lambda:cn-northwest-1:382066503313:layer:AWSLambda-Python-AWS-SDK:4"
    "us-gov-west"    = "arn:aws-us-gov:lambda:us-gov-west-1:556739011827:layer:AWSLambda-Python-AWS-SDK:4"
    "us-gov-east"    = "arn:aws-us-gov:lambda:us-gov-east-1:138526772879:layer:AWSLambda-Python-AWS-SDK:4"
  }
}

data "aws_s3_bucket" "cloudtrail_bucket" {
  bucket = var.cloudtrail_bucket_name
}

data "aws_caller_identity" "current" {}
