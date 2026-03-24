"""Webhook Endpoints resource."""

from ezpayments.pagination import PaginatedResponse


class WebhookEndpoints:
    """Manage webhook endpoint subscriptions.

    Webhook endpoints allow you to receive real-time notifications
    about events in your ezPayments account.

    Args:
        http_client: An ``HTTPClient`` instance for making API requests.
    """

    _base_path = "/api/v3/webhook-endpoints/"

    def __init__(self, http_client):
        self._http = http_client

    def create(self, url, events, idempotency_key=None, **kwargs):
        """Create a new webhook endpoint.

        Args:
            url: The URL that will receive webhook events.
            events: A list of event types to subscribe to
                (e.g. ``["payment_link.paid", "payout.completed"]``).
            idempotency_key: Optional idempotency key to prevent duplicate requests.
            **kwargs: Additional fields to include in the request body.

        Returns:
            A dictionary containing the created webhook endpoint data,
            including the signing secret.

        Example::

            endpoint = client.webhook_endpoints.create(
                url="https://example.com/webhooks",
                events=["payment_link.paid"],
            )
            secret = endpoint["data"]["secret"]
        """
        data = {"url": url, "events": events}
        data.update(kwargs)

        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        return self._http.request(
            "POST", self._base_path, json_data=data, headers=headers
        )

    def list(self, limit=None, starting_after=None, **kwargs):
        """List all webhook endpoints.

        Args:
            limit: Maximum number of results to return (1-100, default 20).
            starting_after: Cursor for fetching the next page of results.
                Pass the cursor value from a previous response's ``next`` URL.
            **kwargs: Additional query parameters for filtering.

        Returns:
            A :class:`~ezpayments.pagination.PaginatedResponse` containing
            the results and pagination helpers.

        Example::

            page = client.webhook_endpoints.list(limit=10)
            for endpoint in page:
                print(endpoint["id"])
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if starting_after is not None:
            params["starting_after"] = starting_after
        params.update(kwargs)

        response = self._http.request(
            "GET", self._base_path, params=params or None
        )
        data = response.get("data", {})
        meta = response.get("meta", {})
        return PaginatedResponse(data, meta, self._http, self._base_path)

    def retrieve(self, endpoint_id):
        """Retrieve a single webhook endpoint by ID.

        Args:
            endpoint_id: The unique identifier of the webhook endpoint.

        Returns:
            A dictionary containing the webhook endpoint data.

        Example::

            endpoint = client.webhook_endpoints.retrieve("we_abc123")
        """
        path = "{}{}/".format(self._base_path, endpoint_id)
        return self._http.request("GET", path)

    def update(self, endpoint_id, **kwargs):
        """Update an existing webhook endpoint.

        Args:
            endpoint_id: The unique identifier of the webhook endpoint.
            **kwargs: Fields to update (e.g. ``url="https://new.example.com"``).

        Returns:
            A dictionary containing the updated webhook endpoint data.

        Example::

            endpoint = client.webhook_endpoints.update(
                "we_abc123",
                events=["payment_link.paid", "payout.completed"],
            )
        """
        path = "{}{}/".format(self._base_path, endpoint_id)
        return self._http.request("PATCH", path, json_data=kwargs)

    def delete(self, endpoint_id):
        """Delete a webhook endpoint.

        Args:
            endpoint_id: The unique identifier of the webhook endpoint.

        Returns:
            ``None`` on successful deletion.

        Example::

            client.webhook_endpoints.delete("we_abc123")
        """
        path = "{}{}/".format(self._base_path, endpoint_id)
        return self._http.request("DELETE", path)
