"""Exception classes for the ezPayments SDK."""


class EzPaymentsError(Exception):
    """Base exception for all ezPayments SDK errors.

    Attributes:
        message: Human-readable error description.
        http_status: HTTP status code, if applicable.
        error_type: Error type string from the API response.
        error_code: Machine-readable error code from the API response.
        param: The parameter related to the error, if applicable.
        request_id: The request ID from the API response, if available.
    """

    def __init__(
        self,
        message=None,
        http_status=None,
        error_type=None,
        error_code=None,
        param=None,
        request_id=None,
    ):
        super().__init__(message)
        self.message = message or "An unknown error occurred"
        self.http_status = http_status
        self.error_type = error_type
        self.error_code = error_code
        self.param = param
        self.request_id = request_id

    def __str__(self):
        parts = [self.message]
        if self.error_code:
            parts.append("(code: {})".format(self.error_code))
        if self.request_id:
            parts.append("[request_id: {}]".format(self.request_id))
        return " ".join(parts)


class AuthenticationError(EzPaymentsError):
    """Raised when the API key is invalid or missing (HTTP 401)."""

    pass


class ValidationError(EzPaymentsError):
    """Raised when the request parameters are invalid (HTTP 400/422)."""

    pass


class NotFoundError(EzPaymentsError):
    """Raised when the requested resource does not exist (HTTP 404)."""

    pass


class RateLimitError(EzPaymentsError):
    """Raised when the API rate limit has been exceeded (HTTP 429)."""

    pass


class APIError(EzPaymentsError):
    """Raised for all other API errors (HTTP 5xx, unexpected status codes)."""

    pass


class WebhookSignatureError(EzPaymentsError):
    """Raised when webhook signature verification fails."""

    pass
