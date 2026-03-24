"""Tests for pagination support."""

from unittest.mock import MagicMock, patch

import pytest

from ezpayments import EzPayments
from ezpayments.pagination import PaginatedResponse


class TestPaginatedResponse:
    """Test PaginatedResponse wrapper."""

    def _make_page(self, results, next_url=None, previous_url=None):
        data = {
            "results": results,
            "next": next_url,
            "previous": previous_url,
        }
        meta = {"request_id": "req_test", "mode": "live"}
        client = MagicMock()
        return PaginatedResponse(data, meta, client, "/api/v3/payment-links/")

    def test_results_accessible(self):
        page = self._make_page([{"id": "pl_1"}, {"id": "pl_2"}])
        assert len(page) == 2
        assert page.results[0]["id"] == "pl_1"

    def test_iteration(self):
        page = self._make_page([{"id": "pl_1"}, {"id": "pl_2"}])
        ids = [item["id"] for item in page]
        assert ids == ["pl_1", "pl_2"]

    def test_has_more_true(self):
        page = self._make_page(
            [{"id": "pl_1"}],
            next_url="https://app.ezpayments.co/api/v3/payment-links/?cursor=abc123",
        )
        assert page.has_more is True

    def test_has_more_false(self):
        page = self._make_page([{"id": "pl_1"}])
        assert page.has_more is False

    def test_next_page_fetches_with_cursor(self):
        client = MagicMock()
        client.request.return_value = {
            "data": {
                "results": [{"id": "pl_3"}],
                "next": None,
                "previous": "https://app.ezpayments.co/api/v3/payment-links/?cursor=prev",
            },
            "meta": {"request_id": "req_002", "mode": "live"},
        }

        data = {
            "results": [{"id": "pl_1"}, {"id": "pl_2"}],
            "next": "https://app.ezpayments.co/api/v3/payment-links/?cursor=abc123&limit=2",
            "previous": None,
        }
        page = PaginatedResponse(data, {}, client, "/api/v3/payment-links/")

        next_page = page.next_page()

        client.request.assert_called_once_with(
            "GET",
            "/api/v3/payment-links/",
            params={"cursor": "abc123", "limit": "2"},
        )
        assert len(next_page) == 1
        assert next_page.results[0]["id"] == "pl_3"
        assert next_page.has_more is False

    def test_next_page_raises_when_no_more(self):
        page = self._make_page([{"id": "pl_1"}])
        with pytest.raises(StopIteration, match="No more pages"):
            page.next_page()

    def test_previous_page_fetches(self):
        client = MagicMock()
        client.request.return_value = {
            "data": {
                "results": [{"id": "pl_0"}],
                "next": "https://app.ezpayments.co/api/v3/payment-links/?cursor=abc",
                "previous": None,
            },
            "meta": {"request_id": "req_003", "mode": "live"},
        }

        data = {
            "results": [{"id": "pl_1"}],
            "next": None,
            "previous": "https://app.ezpayments.co/api/v3/payment-links/?cursor=prev123",
        }
        page = PaginatedResponse(data, {}, client, "/api/v3/payment-links/")

        prev_page = page.previous_page()

        client.request.assert_called_once_with(
            "GET",
            "/api/v3/payment-links/",
            params={"cursor": "prev123"},
        )
        assert prev_page.results[0]["id"] == "pl_0"

    def test_previous_page_raises_when_none(self):
        page = self._make_page([{"id": "pl_1"}])
        with pytest.raises(StopIteration, match="No previous page"):
            page.previous_page()

    def test_auto_paging_iter(self):
        client = MagicMock()
        # Second call returns the last page
        client.request.return_value = {
            "data": {
                "results": [{"id": "pl_3"}],
                "next": None,
                "previous": None,
            },
            "meta": {},
        }

        data = {
            "results": [{"id": "pl_1"}, {"id": "pl_2"}],
            "next": "https://app.ezpayments.co/api/v3/payment-links/?cursor=abc",
            "previous": None,
        }
        page = PaginatedResponse(data, {}, client, "/api/v3/payment-links/")

        all_ids = [item["id"] for item in page.auto_paging_iter()]
        assert all_ids == ["pl_1", "pl_2", "pl_3"]

    def test_empty_results(self):
        page = self._make_page([])
        assert len(page) == 0
        assert list(page) == []
        assert page.has_more is False

    def test_meta_preserved(self):
        data = {"results": [], "next": None, "previous": None}
        meta = {"request_id": "req_xyz", "mode": "live"}
        page = PaginatedResponse(data, meta, MagicMock(), "/api/v3/test/")
        assert page.meta["request_id"] == "req_xyz"
        assert page.meta["mode"] == "live"

    def test_repr(self):
        page = self._make_page([{"id": "pl_1"}])
        assert repr(page) == "PaginatedResponse(results=1, has_more=False)"

    def test_extract_params_multiple(self):
        url = "https://app.ezpayments.co/api/v3/payment-links/?cursor=abc&limit=10&status=active"
        params = PaginatedResponse._extract_params(url)
        assert params == {"cursor": "abc", "limit": "10", "status": "active"}


class TestResourceListPagination:
    """Test that resource list() methods return PaginatedResponse."""

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

    def _paginated_body(self, results, next_url=None):
        return {
            "data": {
                "results": results,
                "next": next_url,
                "previous": None,
            },
            "meta": {"request_id": "req_test", "mode": "live"},
        }

    def test_payment_links_list_returns_paginated_response(self):
        body = self._paginated_body([{"id": "pl_1"}, {"id": "pl_2"}])
        self.mock_session.return_value = self._make_response(200, body)

        result = self.client.payment_links.list(limit=10)

        assert isinstance(result, PaginatedResponse)
        assert len(result) == 2

    def test_payment_links_list_sends_limit_and_cursor(self):
        body = self._paginated_body([])
        self.mock_session.return_value = self._make_response(200, body)

        self.client.payment_links.list(limit=5, starting_after="cur_abc")

        call_kwargs = self.mock_session.call_args
        assert call_kwargs.kwargs["params"] == {
            "limit": 5,
            "starting_after": "cur_abc",
        }

    def test_transactions_list_returns_paginated_response(self):
        body = self._paginated_body([{"id": "txn_1"}])
        self.mock_session.return_value = self._make_response(200, body)

        result = self.client.transactions.list(limit=25)

        assert isinstance(result, PaginatedResponse)
        assert len(result) == 1

    def test_webhook_endpoints_list_returns_paginated_response(self):
        body = self._paginated_body([{"id": "we_1"}])
        self.mock_session.return_value = self._make_response(200, body)

        result = self.client.webhook_endpoints.list()

        assert isinstance(result, PaginatedResponse)

    def test_api_keys_list_returns_paginated_response(self):
        body = self._paginated_body([{"id": "key_1"}])
        self.mock_session.return_value = self._make_response(200, body)

        result = self.client.api_keys.list()

        assert isinstance(result, PaginatedResponse)

    def test_list_with_extra_filters(self):
        body = self._paginated_body([])
        self.mock_session.return_value = self._make_response(200, body)

        self.client.payment_links.list(limit=10, status="active")

        call_kwargs = self.mock_session.call_args
        assert call_kwargs.kwargs["params"] == {"limit": 10, "status": "active"}
