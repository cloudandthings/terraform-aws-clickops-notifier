# Changelog

All notable changes to this project will be documented in this file.

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
