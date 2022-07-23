output "clickops_notifier_lambda" {
  description = "Expose all the outputs from the lambda module"
  value       = module.clickops_notifier_lambda
}

output "sqs_queue" {
  description = "Expose the bucket notification SQS details"
  value       = aws_sqs_queue.bucket_notifications
}
