"""Transactions resource."""

from ezpayments.pagination import PaginatedResponse


class Transactions:
    """Retrieve transaction records.

    Transactions represent completed or pending payment activities
    associated with your account.

    Args:
        http_client: An ``HTTPClient`` instance for making API requests.
    """

    _base_path = "/api/v3/transactions/"

    def __init__(self, http_client):
        self._http = http_client

    def list(self, limit=None, starting_after=None, **kwargs):
        """List all transactions.

        Args:
            limit: Maximum number of results to return (1-100, default 20).
            starting_after: Cursor for fetching the next page of results.
                Pass the cursor value from a previous response's ``next`` URL.
            **kwargs: Additional query parameters for filtering
                (e.g. ``status="completed"``).

        Returns:
            A :class:`~ezpayments.pagination.PaginatedResponse` containing
            the results and pagination helpers.

        Example::

            page = client.transactions.list(limit=25, status="completed")
            for txn in page:
                print(txn["id"])
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

    def retrieve(self, transaction_id):
        """Retrieve a single transaction by ID.

        Args:
            transaction_id: The unique identifier of the transaction.

        Returns:
            A dictionary containing the transaction data.

        Example::

            txn = client.transactions.retrieve("txn_abc123")
        """
        path = "{}{}/".format(self._base_path, transaction_id)
        return self._http.request("GET", path)
