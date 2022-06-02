output "clickops_notifier_lambda" {
  value = module.clickops_notifier_lambda
}

output "sqs_queue" {
  value = aws_sqs_queue.bucket_notifications
}
