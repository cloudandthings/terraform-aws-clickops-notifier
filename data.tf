locals {
  ignored_scoped_events = var.excluded_scoped_actions_effect == "APPEND" ? concat(local.ignored_scoped_events_built_in, var.excluded_scoped_actions) : var.excluded_scoped_actions
}

data "aws_caller_identity" "current" {}
