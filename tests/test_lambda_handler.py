from clickops import app


def test_lambda_handler_standalone():
    """
    This test ensures that the lambda handler_standalone function is callable.
    """
    test_event = None
    app.handler_standalone(test_event, None)


def test_lambda_handler_organizational():
    """
    This test ensures that the lambda handler_organizational function is callable.
    """
    test_event = None
    app.handler_organizational(test_event, None)
