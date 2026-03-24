"""Transactions resource."""


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

    def list(self, **kwargs):
        """List all transactions.

        Args:
            **kwargs: Optional query parameters for filtering and pagination
                (e.g. ``page=1``, ``status="completed"``).

        Returns:
            A dictionary containing the list of transactions and pagination info.

        Example::

            txns = client.transactions.list(status="completed", page=1)
        """
        return self._http.request("GET", self._base_path, params=kwargs or None)

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
