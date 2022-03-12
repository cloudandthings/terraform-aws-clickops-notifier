# terraform-aws-clickops-notifier

Get notified when users are taking actions in the AWS Console. More [here](https://medium.com/cloudandthings/aws-clickoops-1b8cabc9b8e3)
## 🏗️ Module Usage
### Requirements

It is not strictly a requirement, that you use this with AWS ControlTower. The module has only been tested in the Log Archive account that ships with AWS ControTower. 

### Providers

| Name | Version |
|------|---------|
| aws | n/a |
| archive | n/a |

### Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| cloudtrail\_bucket\_name | Bucket containing the Cloudtrail logs that you want to process. ControlTower bucket name follows this naming convention `aws-controltower-logs-{{account_id}}-{{region}}` | `string` | n/a | yes |
| webhook | The webhook URL for notifications. https://api.slack.com/messaging/webhooks | `string` | n/a | yes |
| region | Region where this will be deployed. Used for [getting the correct lambda layer] | `string` | n/a | yes |
| message\_format | Where do you want to send this message? Only slack, for now. | `string` | `"slack"` | no |
| excluded\_accounts | List of accounts that be excluded for scans on manual actions. These take precidence over `included_accounts` | `list(string)` | `[]` | no |
| included\_accounts | List of accounts that be scanned to manual actions. If empty will scan all accounts. | `list(string)` | `[]` | no |
| excluded\_users | List of email addresses will not be reported on when practicing ClickOps. | `list(string)` | `[]` | no |
| included\_users | List of emails that be scanned to manual actions. If empty will scan all emails. | `list(string)` | `[]` | no |
| naming\_prefix | Resources will be prefixed with this | `string` | `"clickops-notifier"` | no |
| tags | Tags to add to resources in addition to the default\_tags for the provider | `map(string)` | `{}` | no |
| event\_processing\_timeout | Maximum number of seconds the lambda is allowed to run and number of seconds events should be hidden in SQS after being picked up my Lambda. | `number` | `60` | no |
| event\_batch\_size | Batch events into chunks of `event_batch_size` | `number` | `10` | no |
| event\_maximum\_batching\_window | Maximum batching window in seconds. | `number` | `300` | no |
| log\_retention\_in\_days | Number of days to keep CloudWatch logs | `number` | `14` | no |

----
## 🚙 Test Drive
Setup your AWS credentails such that `aws sts get-caller-identity | grep Account` gives you your ControlTower Log Archive account id.

```bash
cd sample

terraform init
terraform plan -out=plan

# var.cloudtrail_bucket_name
#   Enter a value: aws-controltower-logs-123456789012-eu-west-1

# var.region
#   Enter a value: eu-west-1

# var.webhook
#   Enter a value: https://hooks.slack.com/services/xxx/xxx/xxx

terraform apply plan
```