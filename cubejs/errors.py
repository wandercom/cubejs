"""Errors expected from CubeJS server."""


class ServerError(Exception):
    """Raised when CubeJS responds with an error."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return f"CubeJS server error: {self.message}"


class AuthorizationError(Exception):
    """Raised when CubeJS responds with an authorization error."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return f"CubeJS authorization error: {self.message}"


class RequestError(Exception):
    """Raised when CubeJS responds with 400 error."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return f"CubeJS 400 request error: {self.message}"


class UnexpectedResponseError(Exception):
    """Raised when CubeJS responds with an unexpected response code."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return f"CubeJS unexpected response: {self.message}"


class RetryableError(Exception):
    """Raised when a retry can be performed."""

    def __str__(self) -> str:
        return "CubeJS failed but we can attempt a retry"


class ContinueWaitError(RetryableError):
    """Raised when CubeJS responds with 'Continue wait' message."""

    def __str__(self) -> str:
        return "CubeJS query is not ready yet, continue waiting..."


class BadGatewayError(RetryableError):
    """Raised when CubeJS responds with 'Bad Gateway'."""

    def __str__(self) -> str:
        return "CubeJS may be scaling instances, attempting a retry..."
