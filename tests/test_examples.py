import pytest

from tests.conftest import terraform_apply, terraform_plan


@pytest.mark.slow
def test_examples_basic(terraform_config):
    terraform_apply("examples_basic", terraform_config)


@pytest.mark.slow
def test_examples_role(terraform_config):
    terraform_plan("examples_role", terraform_config)


@pytest.mark.slow
def test_examples_standalone(terraform_config):
    terraform_plan("examples_standalone", terraform_config)
