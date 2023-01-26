import pytest
import tftest
import os
import logging


def pytest_addoption(parser):
    parser.addoption("--profile", action="store")
    parser.addoption("--terraform-binary", action="store", default="terraform")


@pytest.fixture(scope="session")
def profile(request):
    """Return AWS profile."""
    profile = request.config.getoption("--profile")
    if profile is None:
        raise Exception("--profile must be specified")
    return profile


def terraform_examples_dir():
    return os.path.join(os.getcwd(), "examples")


@pytest.fixture(scope="session")
def terraform_binary(request):
    """Return path to Terraform binary."""
    return request.config.getoption("--terraform-binary")


@pytest.fixture(scope="session")
def terraform_examples():
    """Return a list of examples, i.e subdirectories in `examples/`."""
    directory = terraform_examples_dir()
    return [f.name for f in os.scandir(directory) if f.is_dir()]


@pytest.fixture(scope="session")
def terraform_config(terraform_binary, terraform_examples):
    """Convenience fixture for passing around config."""
    config = {
        "terraform_binary": terraform_binary,
        "terraform_examples": terraform_examples,
    }
    logging.info(config)
    return config


def get_tf(test_name, terraform_config, variables=None):
    """Construct and return `tftest.TerraformTest`, for executing Terraform commands."""
    basedir = None
    if "." in test_name:  # Called with __name__, eg tests.test_examples_basic
        test_name = test_name.split(".")[-1]
        if test_name.startswith("test_"):
            test_name = test_name[len("test_") :]
    if test_name.startswith("examples_"):
        basedir = terraform_examples_dir()
        test_name = test_name[len("examples_") :].replace("_", "-")
    logging.info(f"{basedir=} {test_name=}")

    tf = tftest.TerraformTest(
        tfdir=test_name, basedir=basedir, binary=terraform_config["terraform_binary"]
    )
    # # Populate test.auto.tfvars.json with the specified variables
    # variables = variables or {}
    # with open(os.path.join(basedir, test_name, "test.auto.tfvars.json"), "w") as f:
    #     json.dump(variables, f)
    tf.setup()
    return tf


def terraform_plan(test_name, terraform_config, variables=None):
    """Run `terraform plan -out`, returning the plan output."""
    tf = get_tf(test_name, terraform_config, variables=variables)
    yield tf.plan(output=True)


def terraform_apply_and_output(test_name, terraform_config, variables=None):
    """Run `terraform_apply` and then `terraform output`, returning the output."""
    tf = get_tf(test_name, terraform_config, variables=variables)
    try:
        tf.apply()
        yield tf.output()
    finally:
        tf.destroy(**{"auto_approve": True})


def terraform_apply(test_name, terraform_config, variables=None):
    """Run `terraform_apply` and then `terraform output`, returning the output."""
    tf = get_tf(test_name, terraform_config, variables=variables)
    try:
        yield tf.apply()
    finally:
        tf.destroy(**{"auto_approve": True})
