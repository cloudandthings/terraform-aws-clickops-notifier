output "clickops_notifier_lambda" {
  description = "Expose all the outputs from the lambda module"
  value       = module.clickops_notifier_lambda
}

output "sns_topic" {
  description = "Expose the bucket notification SNS details"
  value       = aws_sns_topic.bucket_notifications
}

output "sqs_queue" {
  description = "Expose the bucket notification SQS details"
  value       = aws_sqs_queue.bucket_notifications
}
