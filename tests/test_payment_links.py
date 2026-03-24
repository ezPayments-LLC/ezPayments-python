"""Tests for the PaymentLinks resource."""

from unittest.mock import MagicMock, patch

import pytest

from ezpayments import EzPayments


class TestPaymentLinks:
    """Test PaymentLinks CRUD operations."""

    def setup_method(self):
        self.client = EzPayments(api_key="sk_live_test123")
        self.mock_session = patch.object(
            self.client._http_client._session, "request"
        ).start()

    def teardown_method(self):
        patch.stopall()

    def _make_response(self, status_code=200, body=None):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = body or {}
        return response

    def test_create_payment_link(self):
        expected = {
            "data": {
                "id": "pl_abc123",
                "amount": "50.00",
                "description": "Test payment",
                "status": "active",
                "url": "https://pay.ezpayments.co/pl_abc123",
            },
            "meta": {"request_id": "req_001", "mode": "live"},
        }
        self.mock_session.return_value = self._make_response(200, expected)

        result = self.client.payment_links.create(
            amount="50.00", description="Test payment"
        )

        assert result == expected
        call_kwargs = self.mock_session.call_args
        assert call_kwargs.kwargs["method"] == "POST"
        assert "/api/v3/payment-links/" in call_kwargs.kwargs["url"]
        assert call_kwargs.kwargs["json"] == {
            "amount": "50.00",
            "description": "Test payment",
        }

    def test_create_with_idempotency_key(self):
        self.mock_session.return_value = self._make_response(200, {"data": {}})

        self.client.payment_links.create(
            amount="25.00", idempotency_key="idem_123"
        )

        call_kwargs = self.mock_session.call_args
        assert call_kwargs.kwargs["headers"]["Idempotency-Key"] == "idem_123"

    def test_create_with_extra_kwargs(self):
        self.mock_session.return_value = self._make_response(200, {"data": {}})

        self.client.payment_links.create(
            amount="100.00", currency="USD", customer_email="test@example.com"
        )

        call_kwargs = self.mock_session.call_args
        body = call_kwargs.kwargs["json"]
        assert body["amount"] == "100.00"
        assert body["currency"] == "USD"
        assert body["customer_email"] == "test@example.com"

    def test_list_payment_links(self):
        expected = {
            "data": [{"id": "pl_1"}, {"id": "pl_2"}],
            "meta": {"request_id": "req_002", "mode": "live"},
        }
        self.mock_session.return_value = self._make_response(200, expected)

        result = self.client.payment_links.list(page=1, status="active")

        assert result == expected
        call_kwargs = self.mock_session.call_args
        assert call_kwargs.kwargs["method"] == "GET"
        assert call_kwargs.kwargs["params"] == {"page": 1, "status": "active"}

    def test_list_without_params(self):
        self.mock_session.return_value = self._make_response(200, {"data": []})

        self.client.payment_links.list()

        call_kwargs = self.mock_session.call_args
        assert call_kwargs.kwargs["params"] is None

    def test_retrieve_payment_link(self):
        expected = {"data": {"id": "pl_abc123", "amount": "50.00"}}
        self.mock_session.return_value = self._make_response(200, expected)

        result = self.client.payment_links.retrieve("pl_abc123")

        assert result == expected
        call_kwargs = self.mock_session.call_args
        assert call_kwargs.kwargs["method"] == "GET"
        assert "/api/v3/payment-links/pl_abc123/" in call_kwargs.kwargs["url"]

    def test_update_payment_link(self):
        expected = {"data": {"id": "pl_abc123", "description": "Updated"}}
        self.mock_session.return_value = self._make_response(200, expected)

        result = self.client.payment_links.update("pl_abc123", description="Updated")

        assert result == expected
        call_kwargs = self.mock_session.call_args
        assert call_kwargs.kwargs["method"] == "PATCH"
        assert call_kwargs.kwargs["json"] == {"description": "Updated"}

    def test_delete_payment_link(self):
        self.mock_session.return_value = self._make_response(204)

        result = self.client.payment_links.delete("pl_abc123")

        assert result is None
        call_kwargs = self.mock_session.call_args
        assert call_kwargs.kwargs["method"] == "DELETE"

    def test_get_fees(self):
        expected = {
            "data": {
                "platform_fee": "1.50",
                "processing_fee": "0.30",
                "total_fee": "1.80",
            }
        }
        self.mock_session.return_value = self._make_response(200, expected)

        result = self.client.payment_links.get_fees("pl_abc123")

        assert result == expected
        call_kwargs = self.mock_session.call_args
        assert call_kwargs.kwargs["method"] == "GET"
        assert "/api/v3/payment-links/pl_abc123/fees/" in call_kwargs.kwargs["url"]
