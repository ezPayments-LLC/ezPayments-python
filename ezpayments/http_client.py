"""Low-level HTTP client for the ezPayments API."""

import platform

import requests

from ezpayments import __version__
from ezpayments.exceptions import (
    APIError,
    AuthenticationError,
    EzPaymentsError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

_STATUS_MAP = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthenticationError,
    404: NotFoundError,
    422: ValidationError,
    429: RateLimitError,
}


class HTTPClient:
    """Handles raw HTTP communication with the ezPayments API.

    Args:
        api_key: Bearer token for authentication.
        base_url: Base URL of the ezPayments API.
        timeout: Request timeout in seconds.
    """

    def __init__(self, api_key, base_url, timeout=30):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(self._default_headers())

    def _default_headers(self):
        """Build default headers included with every request."""
        return {
            "Authorization": "Bearer {}".format(self.api_key),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ezpayments-python/{} python/{}".format(
                __version__, platform.python_version()
            ),
        }

    def request(self, method, path, params=None, json_data=None, headers=None):
        """Send an HTTP request and return the parsed response.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE).
            path: API path relative to base URL (e.g. ``/api/v3/payment-links/``).
            params: Query parameters for GET requests.
            json_data: JSON body for POST/PATCH requests.
            headers: Additional headers to merge with defaults.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            AuthenticationError: For 401/403 responses.
            ValidationError: For 400/422 responses.
            NotFoundError: For 404 responses.
            RateLimitError: For 429 responses.
            APIError: For 5xx and other unexpected responses.
            EzPaymentsError: For network or connection failures.
        """
        url = "{}{}".format(self.base_url, path)

        merged_headers = {}
        if headers:
            merged_headers.update(headers)

        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=merged_headers,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as exc:
            raise EzPaymentsError(
                message="Network error: {}".format(str(exc))
            ) from exc

        return self._handle_response(response)

    def _handle_response(self, response):
        """Parse the API response and raise appropriate exceptions on errors.

        Args:
            response: The ``requests.Response`` object.

        Returns:
            Parsed JSON body as a dictionary.

        Raises:
            Appropriate exception subclass based on HTTP status code.
        """
        if response.status_code == 204:
            return None

        try:
            body = response.json()
        except ValueError:
            if response.status_code >= 400:
                raise APIError(
                    message="Invalid JSON response from API",
                    http_status=response.status_code,
                )
            return {}

        if response.status_code >= 400:
            self._raise_for_error(response.status_code, body)

        return body

    def _raise_for_error(self, status_code, body):
        """Map an error response to the appropriate exception class.

        Args:
            status_code: HTTP status code.
            body: Parsed JSON body containing the error envelope.

        Raises:
            Appropriate exception subclass.
        """
        error_data = body.get("error", {})
        message = error_data.get("message", "Unknown API error")
        error_type = error_data.get("type")
        error_code = error_data.get("code")
        param = error_data.get("param")

        meta = body.get("meta", {})
        request_id = meta.get("request_id")

        exc_class = _STATUS_MAP.get(status_code, APIError)
        raise exc_class(
            message=message,
            http_status=status_code,
            error_type=error_type,
            error_code=error_code,
            param=param,
            request_id=request_id,
        )
