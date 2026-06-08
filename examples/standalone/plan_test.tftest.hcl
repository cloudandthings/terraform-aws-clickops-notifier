mock_provider "aws" {
  mock_data "aws_iam_policy_document" {
    defaults = {
      json = "{\"Version\":\"2012-10-17\",\"Statement\":[]}"
    }
  }
}
mock_provider "random" {}

run "plan_succeeds" {
  command = plan

  variables {
    run_id = "test"
  }
}
