"""Tests for the EzPayments client and HTTP error handling."""

import json
from unittest.mock import MagicMock, patch

import pytest

from ezpayments import EzPayments
from ezpayments.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from ezpayments.resources import APIKeys, PaymentLinks, Transactions, WebhookEndpoints


class TestClientInitialization:
    """Test EzPayments client initialization."""

    def test_creates_client_with_api_key(self):
        client = EzPayments(api_key="sk_live_test123")
        assert client.payment_links is not None
        assert client.transactions is not None
        assert client.webhook_endpoints is not None
        assert client.api_keys is not None

    def test_raises_on_empty_api_key(self):
        with pytest.raises(ValueError, match="API key is required"):
            EzPayments(api_key="")

    def test_raises_on_none_api_key(self):
        with pytest.raises(ValueError, match="API key is required"):
            EzPayments(api_key=None)

    def test_default_base_url(self):
        client = EzPayments(api_key="sk_live_test123")
        assert client._http_client.base_url == "https://app.ezpayments.co"

    def test_custom_base_url(self):
        client = EzPayments(api_key="sk_live_test123", base_url="https://sandbox.example.com")
        assert client._http_client.base_url == "https://sandbox.example.com"

    def test_strips_trailing_slash_from_base_url(self):
        client = EzPayments(api_key="sk_live_test123", base_url="https://sandbox.example.com/")
        assert client._http_client.base_url == "https://sandbox.example.com"

    def test_custom_timeout(self):
        client = EzPayments(api_key="sk_live_test123", timeout=60)
        assert client._http_client.timeout == 60

    def test_resource_types(self):
        client = EzPayments(api_key="sk_live_test123")
        assert isinstance(client.payment_links, PaymentLinks)
        assert isinstance(client.transactions, Transactions)
        assert isinstance(client.webhook_endpoints, WebhookEndpoints)
        assert isinstance(client.api_keys, APIKeys)


class TestErrorHandling:
    """Test HTTP error code to exception mapping."""

    def _mock_response(self, status_code, body):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = body
        return response

    def test_401_raises_authentication_error(self):
        client = EzPayments(api_key="sk_live_bad")
        body = {"error": {"type": "authentication_error", "message": "Invalid API key"}}

        with patch.object(client._http_client._session, "request") as mock_req:
            mock_req.return_value = self._mock_response(401, body)
            with pytest.raises(AuthenticationError, match="Invalid API key"):
                client.payment_links.list()

    def test_400_raises_validation_error(self):
        client = EzPayments(api_key="sk_live_test")
        body = {
            "error": {
                "type": "validation_error",
                "message": "Amount is required",
                "param": "amount",
            }
        }

        with patch.object(client._http_client._session, "request") as mock_req:
            mock_req.return_value = self._mock_response(400, body)
            with pytest.raises(ValidationError, match="Amount is required") as exc_info:
                client.payment_links.create(amount="")
            assert exc_info.value.param == "amount"

    def test_404_raises_not_found_error(self):
        client = EzPayments(api_key="sk_live_test")
        body = {"error": {"type": "not_found", "message": "Payment link not found"}}

        with patch.object(client._http_client._session, "request") as mock_req:
            mock_req.return_value = self._mock_response(404, body)
            with pytest.raises(NotFoundError, match="Payment link not found"):
                client.payment_links.retrieve("pl_nonexistent")

    def test_429_raises_rate_limit_error(self):
        client = EzPayments(api_key="sk_live_test")
        body = {"error": {"type": "rate_limit", "message": "Too many requests"}}

        with patch.object(client._http_client._session, "request") as mock_req:
            mock_req.return_value = self._mock_response(429, body)
            with pytest.raises(RateLimitError, match="Too many requests"):
                client.payment_links.list()

    def test_500_raises_api_error(self):
        client = EzPayments(api_key="sk_live_test")
        body = {"error": {"type": "server_error", "message": "Internal server error"}}

        with patch.object(client._http_client._session, "request") as mock_req:
            mock_req.return_value = self._mock_response(500, body)
            with pytest.raises(APIError, match="Internal server error"):
                client.payment_links.list()

    def test_error_includes_request_id(self):
        client = EzPayments(api_key="sk_live_test")
        body = {
            "error": {"type": "server_error", "message": "Error"},
            "meta": {"request_id": "req_abc123"},
        }

        with patch.object(client._http_client._session, "request") as mock_req:
            mock_req.return_value = self._mock_response(500, body)
            with pytest.raises(APIError) as exc_info:
                client.payment_links.list()
            assert exc_info.value.request_id == "req_abc123"

    def test_204_returns_none(self):
        client = EzPayments(api_key="sk_live_test")

        response = MagicMock()
        response.status_code = 204

        with patch.object(client._http_client._session, "request") as mock_req:
            mock_req.return_value = response
            result = client.payment_links.delete("pl_abc123")
            assert result is None
