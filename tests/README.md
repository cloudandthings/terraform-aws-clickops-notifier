These tests can easily be run interactively as follows:

- Configure `terraform.tfvars` in each test folder

- Configure AWS credentials

- Create SSM Parameter (optional)

- Configure AWS region: `export AWS_DEFAULT_REGION=x`

Then execute:

```sh
pytest -m 'not slow' --run-id MY_RUN_ID
```
or

```sh
pytest -m 'not slow' --run-id MY_RUN_ID --ec2-key-pair-name MY_KEY_PAIR_NAME
```

While the tests are running, CTRL-C can be used to kill the tests and automatically destroy all created infrastructure.
