resource "aws_cloudwatch_log_group" "func" {
  name              = "/aws/lambda/${aws_lambda_function.func.function_name}"
  retention_in_days = var.log_retention_in_days

  tags = var.tags
}