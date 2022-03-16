SAM CLI, version 1.40.1

```
sam package \
--template template.yaml \
--s3-bucket aws-cat-clickops-main-deployment \
--s3-prefix sam-package \
--output-template-file packaged.yaml \
--region eu-west-1

sam publish \
-t packaged.yaml \
--region eu-west-1

sam deploy \
--template template.yaml \
--stack-name clickops \
--s3-prefix sam-deploy \
--s3-bucket aws-cat-clickops-main-deployment \
--capabilities CAPABILITY_NAMED_IAM \
--region eu-west-1 \
--parameter-overrides CloudtrailBucket=aws-controltower-logs-111111111111-eu-west-1 WebhookUrl=https://hooks.slack.com/services/1111111111111
```

https://serverlessland.com/patterns/s3-eventbridge
https://aws.amazon.com/blogs/compute/using-github-actions-to-deploy-serverless-applications/


This is the way to go:
https://github.com/aws/serverless-application-model/issues/1020#issuecomment-526074615


This does not work, need S3 object events in cloudtrail enabled
```
{
  "source": ["aws.s3"],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventSource": ["s3.amazonaws.com"],
    "eventName": ["PutObject"],
    "requestParameters": {
      "bucketName": ["aws-controltower-logs-920551683281-eu-west-1"]
    }
  }
}
```