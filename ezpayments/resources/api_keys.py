"""API Keys resource."""


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

    def list(self, **kwargs):
        """List all API keys.

        Args:
            **kwargs: Optional query parameters for filtering and pagination.

        Returns:
            A dictionary containing the list of API keys.

        Example::

            keys = client.api_keys.list()
        """
        return self._http.request("GET", self._base_path, params=kwargs or None)

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
