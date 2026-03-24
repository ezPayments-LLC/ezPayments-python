"""API Keys resource."""

from ezpayments.pagination import PaginatedResponse


class APIKeys:
    """Manage API keys for programmatic access.

    API keys are used to authenticate requests to the ezPayments API.

    Args:
        http_client: An ``HTTPClient`` instance for making API requests.
    """

    _base_path = "/api/v3/api-keys/"

    def __init__(self, http_client):
        self._http = http_client

    def create(self, name=None, idempotency_key=None, **kwargs):
        """Create a new API key.

        Args:
            name: Optional human-readable name for the key.
            idempotency_key: Optional idempotency key to prevent duplicate requests.
            **kwargs: Additional fields to include in the request body.

        Returns:
            A dictionary containing the created API key data.
            The secret key value is only returned once at creation time.

        Example::

            key = client.api_keys.create(name="Production Key")
            secret = key["data"]["secret_key"]
        """
        data = {}
        if name is not None:
            data["name"] = name
        data.update(kwargs)

        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        return self._http.request(
            "POST", self._base_path, json_data=data, headers=headers
        )

    def list(self, limit=None, starting_after=None, **kwargs):
        """List all API keys.

        Args:
            limit: Maximum number of results to return (1-100, default 20).
            starting_after: Cursor for fetching the next page of results.
                Pass the cursor value from a previous response's ``next`` URL.
            **kwargs: Additional query parameters for filtering.

        Returns:
            A :class:`~ezpayments.pagination.PaginatedResponse` containing
            the results and pagination helpers.

        Example::

            page = client.api_keys.list(limit=10)
            for key in page:
                print(key["id"])
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

    def delete(self, key_id):
        """Revoke and delete an API key.

        Args:
            key_id: The unique identifier of the API key to delete.

        Returns:
            ``None`` on successful deletion.

        Example::

            client.api_keys.delete("key_abc123")
        """
        path = "{}{}/".format(self._base_path, key_id)
        return self._http.request("DELETE", path)
