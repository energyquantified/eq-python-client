

class APIError(Exception):
    """
    Base exception for all errors that may occur during an API call.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HTTPError(APIError):
    """
    Base class for all HTTP errors. Mostly used to wrap request's HTTP errors.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UnauthorizedError(APIError):
    """
    Authentication errors such as invalid API key or that the user is blocked.
    """

    def __init__(self, reason=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason = reason or ""

    def __str__(self):
        return self.reason


class ValidationError(APIError):
    """
    Validation error of some kind (invalid parameter or combination
    of parameters).
    """

    def __init__(self, reason=None, parameter=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason = reason
        self.parameter = parameter

    def __str__(self):
        if self.parameter:
            return f"Field=\"{self.parameter}\", message: {self.reason}"
        else:
            return self.reason


class ForbiddenError(APIError):
    """
    The resource is not accessible for the user.
    """

    def __init__(self, reason=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason = reason or ""

    def __str__(self):
        return self.reason


class NotFoundError(APIError):
    """
    The resource was not found on the server.
    """

    def __init__(self, reason=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason = reason or ""

    def __str__(self):
        return self.reason


class InternalServerError(APIError):
    """
    The server failed to process the request.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return (
            "Server failed to process the request. If the problem persists, "
            "please send an email to contact@energyquantified.com."
        )
