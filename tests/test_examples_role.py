import pytest

from conftest import terraform_apply


@pytest.fixture(scope="session")
def plan(terraform_config):
    yield from terraform_apply(__name__, terraform_config)


@pytest.mark.slow
def test_it(plan):
    pass
