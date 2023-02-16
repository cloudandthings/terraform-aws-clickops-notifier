import pytest

from clickopsnotifier import app


def test_lambda_handler_standalone():
    """
    This test ensures that the lambda handler_standalone function is callable.
    """
    with pytest.raises(KeyError):
        app.handler_standalone(None, None)


def test_lambda_handler_organizational():
    """
    This test ensures that the lambda handler_organizational function is callable.
    """
    with pytest.raises(KeyError):
        app.handler_organizational(None, None)
