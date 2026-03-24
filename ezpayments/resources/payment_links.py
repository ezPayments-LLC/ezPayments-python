"""Payment Links resource."""

from ezpayments.pagination import PaginatedResponse


class PaymentLinks:
    """Manage payment links.

    Payment links allow you to create shareable URLs that accept payments
    from your customers.

    Args:
        http_client: An ``HTTPClient`` instance for making API requests.
    """

    _base_path = "/api/v3/payment-links/"

    def __init__(self, http_client):
        self._http = http_client

    def create(self, amount, description=None, idempotency_key=None, **kwargs):
        """Create a new payment link.

        Args:
            amount: Payment amount as a string (e.g. ``"50.00"``).
            description: Optional description for the payment link.
            idempotency_key: Optional idempotency key to prevent duplicate requests.
            **kwargs: Additional fields to include in the request body.

        Returns:
            A dictionary containing the created payment link data.

        Example::

            link = client.payment_links.create(
                amount="50.00",
                description="Invoice #1234",
            )
        """
        data = {"amount": amount}
        if description is not None:
            data["description"] = description
        data.update(kwargs)

        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        return self._http.request(
            "POST", self._base_path, json_data=data, headers=headers
        )

    def list(self, limit=None, starting_after=None, **kwargs):
        """List all payment links.

        Args:
            limit: Maximum number of results to return (1-100, default 20).
            starting_after: Cursor for fetching the next page of results.
                Pass the cursor value from a previous response's ``next`` URL.
            **kwargs: Additional query parameters for filtering
                (e.g. ``status="active"``).

        Returns:
            A :class:`~ezpayments.pagination.PaginatedResponse` containing
            the results and pagination helpers.

        Example::

            # Get the first page
            page = client.payment_links.list(limit=10)
            for link in page:
                print(link["id"])

            # Iterate through all pages
            for link in client.payment_links.list(limit=50).auto_paging_iter():
                print(link["id"])
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

    def retrieve(self, payment_link_id):
        """Retrieve a single payment link by ID.

        Args:
            payment_link_id: The unique identifier of the payment link.

        Returns:
            A dictionary containing the payment link data.

        Example::

            link = client.payment_links.retrieve("pl_abc123")
        """
        path = "{}{}/".format(self._base_path, payment_link_id)
        return self._http.request("GET", path)

    def update(self, payment_link_id, **kwargs):
        """Update an existing payment link.

        Args:
            payment_link_id: The unique identifier of the payment link.
            **kwargs: Fields to update (e.g. ``description="Updated"``,
                ``amount="75.00"``).

        Returns:
            A dictionary containing the updated payment link data.

        Example::

            link = client.payment_links.update("pl_abc123", description="Updated")
        """
        path = "{}{}/".format(self._base_path, payment_link_id)
        return self._http.request("PATCH", path, json_data=kwargs)

    def delete(self, payment_link_id):
        """Delete a payment link.

        Args:
            payment_link_id: The unique identifier of the payment link.

        Returns:
            ``None`` on successful deletion.

        Example::

            client.payment_links.delete("pl_abc123")
        """
        path = "{}{}/".format(self._base_path, payment_link_id)
        return self._http.request("DELETE", path)

    def get_fees(self, payment_link_id):
        """Retrieve the fee breakdown for a payment link.

        Args:
            payment_link_id: The unique identifier of the payment link.

        Returns:
            A dictionary containing the fee details.

        Example::

            fees = client.payment_links.get_fees("pl_abc123")
        """
        path = "{}{}/fees/".format(self._base_path, payment_link_id)
        return self._http.request("GET", path)
