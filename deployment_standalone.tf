resource "aws_cloudwatch_log_subscription_filter" "this" {
  depends_on = [
    module.clickops_notifier_lambda
  ]
  count = var.standalone ? 1 : 0

  name           = "${var.naming_prefix}-filter"
  log_group_name = var.cloudtrail_log_group
  # Ideally we want to filter on:
  # { ($.readOnly IS FALSE) && ($.sessionCredentialFromConsole IS TRUE) }
  # but the sessionCredentialFromConsole is not always present and filter
  # does not support NOT EXISTS at this stage
  filter_pattern  = "{ ($.readOnly IS FALSE) }"
  destination_arn = module.clickops_notifier_lambda.lambda_function_arn
  distribution    = var.subcription_filter_distribution
}

data "aws_cloudwatch_log_group" "this" {
  count = var.standalone ? 1 : 0

  name = var.cloudtrail_log_group
}
