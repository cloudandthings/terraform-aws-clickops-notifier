# Changelog

All notable changes to this project will be documented in this file.

## [5.0.3](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v5.0.2...v5.0.3) (2023-06-09)


### Bug Fixes

* exclude grafana login and support ([#68](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/68)) ([e639c03](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/e639c032e3823a11fc3cf5224ab3a1aac9493ee2))
* ignore route53domains:TransferDomain ([ae3e1b1](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/ae3e1b1b14a7f0607c57c072680e95444c1e2044))
* ignore route53domains:TransferDomain ([b0d1030](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/b0d103030bc5419a01e5679e76269f0a577301c0))

## [5.0.2](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v5.0.1...v5.0.2) (2023-04-18)


### Bug Fixes

* Ensure trail_event_origin is constructed from strings ([4b6fb20](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/4b6fb2092a7cae149bc269df1fd8768d296c6a9f))

## [5.0.1](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v5.0.0...v5.0.1) (2023-03-22)


### Bug Fixes

* Remove s3 UploadPart and UploadPartCopy from notifications ([#61](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/61)) ([74d4fbf](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/74d4fbf6d5360cd0e1eaf4b247ce9e5e2ea66644))

## [5.0.0](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v4.1.0...v5.0.0) (2023-02-28)


### ⚠ BREAKING CHANGES

* Minimum required Terraform version increased from 0.14 to 0.15
* Change from single webhook to support many webhooks. ([#58](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/58))

### Features

* Change from single webhook to support many webhooks. ([#58](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/58)) ([1579406](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/15794066d64357ddb40ead3b518d413947d3279a))


### Bug Fixes

* Minimum required Terraform version increased from 0.14 to 0.15 ([ecbd182](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/ecbd182b6acf15b002d2513f30e490ab5684f00a))
* Remove lifecycle rule for ignoring SSM value changes ([a8f1e2b](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/a8f1e2ba15bb5c425d149c9f3dfb93667a352e53))
* Update deployment packages ([05961ae](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/05961aebb2af7972c337de74f62202f864a4db24))

## [4.1.0](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v4.0.0...v4.1.0) (2023-02-27)


### Features

* Add `allowed_aws_principals_for_sns_subscribe` ([c86bf9e](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/c86bf9e4e41f0ab85611e34c85604c22d943a97d))

## [4.0.0](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v3.0.0...v4.0.0) (2023-02-24)


### ⚠ BREAKING CHANGES

* Rename of s3_X vars to lambda_deployment_X, for clarity. ([#51](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/51))

### Features

* Add `kms_key_id_for_sns_topic` ([502714e](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/502714e080de59457e631ec322e0d8334e0470f6))
* Add `lambda_log_level` variable ([a2f6d5a](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/a2f6d5a24151e46c2018a7bed5e5f003b8df2736))
* Additional s3 bucket notification queues ([#49](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/49)) ([e48ade6](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/e48ade6beab24316bcb81d67fb4c67adf0f8472c))
* For org deployments, use SNS to enable fan-out use cases. ([b68fb7f](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/b68fb7f55c2394cb1052316215ee56b12214a867))
* Update app logic to use SNS ([cf7464d](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/cf7464dbd2e5280168805b86e17e7af37971fd0c))


### Bug Fixes

* Add tags to aws_sqs_queue, aws_ssm_parameter ([817708a](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/817708a39d95f687e1c4f3789a47b647d130c58a))
* DeliveryStream was causing exceptions when disabled ([740c765](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/740c765eec6a18a39d24a4a06e0c62792851dbcf))
* Increase default event_batch_size from 10 to 100 ([750fe31](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/750fe3160ffeec14c2d50517a1628e0b5c030963))
* Remove `additional_s3_bucket_notification_queues` ([c6c9488](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/c6c94889a6878f420e0d12b4c409a924448534d1))
* Rename of s3_X vars to lambda_deployment_X, for clarity. ([#51](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/51)) ([85856bd](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/85856bd5af9788fddb92abe15b234f7fc37476a4))
* Truncate Slack notification of event to 3k chars ([2ab3b1b](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/2ab3b1beeda9d71eecfddfda389db601693beb6d))
* Update lambda builds to latest ([d709560](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/d7095600f8001f935c9193ca4d4a5021edce0e77))

## [3.0.0](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v2.1.0...v3.0.0) (2023-02-16)


### ⚠ BREAKING CHANGES

* Lambda deployment options. Use pre-built package by default. And deprecate python3.6. ([#46](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/46))

### Features

* Lambda deployment options. Use pre-built package by default. And deprecate python3.6. ([#46](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/46)) ([0e12d94](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/0e12d946e670a7c8d1759e6ae3a256c01e9a3db0))

## [2.1.0](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v2.0.0...v2.1.0) (2023-02-02)


### Features

* Ability to send ClickOps to Firehose ([#45](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/45)) ([7b9e362](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/7b9e36266991fa41ba5aac198a8b3dba8a202f8b))


### Bug Fixes

* Bump min Terraform version from 0.13.1 to 0.14.0 ([14db95e](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/14db95e30be09f9af9e67741967572d2fe3999d5))
* **examples:** Standalone example works now ([5bb738c](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/5bb738c8a20e0e4f19f4f204c49cc33f56669fa0))

## [2.0.0](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v1.6.0...v2.0.0) (2022-12-26)


### ⚠ BREAKING CHANGES

* Add support for standalone deployments. (#38)

### Features

* Add support for standalone deployments. ([#38](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/38)) ([d64f647](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/d64f6479ee505c19cbc75c1d518d763e54d4a004))

## [1.6.0](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v1.5.0...v1.6.0) (2022-11-07)


### Features

* Allow lambda memory size setting ([#34](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/34)) and Add TrustedAdvisor refresh checks to exclusions ([#21](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/21)) ([94aa7db](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/94aa7dbb5d91d898ba8e6ee7f3eb1256c51f9989))

## [1.5.0](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v1.4.0...v1.5.0) (2022-10-29)


### Features

* Allow user provided IAM role ([#32](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/32)) ([ade5f2e](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/ade5f2e582ffd51a51500308407e9d5b610ca7f7))

## [1.4.0](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v1.3.0...v1.4.0) (2022-10-26)


### Features

* Update default exclusions and update variable description ([#30](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/30)) ([bd9b7e8](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/bd9b7e84d2b1dfc43e58fe331b0276cc7271b1e9))

## [1.3.0](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v1.2.0...v1.3.0) (2022-09-07)


### Features

* Add check for `sessionCredentialFromConsole` ([#26](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/26)) ([b944f3a](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/b944f3a30a442b2bd3fea0d6a8fbe75c38648ab7))

## [1.2.0](https://github.com/cloudandthings/terraform-aws-clickops-notifier/compare/v1.1.1...v1.2.0) (2022-07-23)


### Features

* `excluded_scoped_actions` and `excluded_scoped_actions_effect` ([#19](https://github.com/cloudandthings/terraform-aws-clickops-notifier/issues/19)) ([91db59e](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/91db59eca25cbc14fa1bd1f6edc12bcad4f463b3))


### Bug Fixes

* GH token ([91a02c8](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/91a02c896755d911fcbb38d1c4ed1f909fa7eb75))
* release branch ([580176d](https://github.com/cloudandthings/terraform-aws-clickops-notifier/commit/580176d7144b30790f31d3b382312f7d274136d1))
