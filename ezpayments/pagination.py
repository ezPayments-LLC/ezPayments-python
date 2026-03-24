"""Pagination helpers for list endpoints."""

from urllib.parse import parse_qs, urlparse


class PaginatedResponse:
    """Wrapper for paginated API responses.

    Provides convenient access to results and cursor-based page navigation.

    Args:
        data: The ``"data"`` portion of the API response envelope containing
            ``results``, ``next``, and ``previous`` fields.
        meta: The ``"meta"`` portion of the API response envelope.
        http_client: The ``HTTPClient`` used to fetch subsequent pages.
        resource_path: The API path for the resource (e.g. ``/api/v3/payment-links/``).

    Example::

        page = client.payment_links.list(limit=10)
        for link in page:
            print(link["id"])

        while page.has_more:
            page = page.next_page()
            for link in page:
                print(link["id"])
    """

    def __init__(self, data, meta, http_client, resource_path):
        self.results = data.get("results", [])
        self.next_url = data.get("next")
        self.previous_url = data.get("previous")
        self.meta = meta or {}
        self._client = http_client
        self._resource_path = resource_path

    @property
    def has_more(self):
        """Whether there is a next page of results."""
        return self.next_url is not None

    def next_page(self):
        """Fetch the next page of results.

        Returns:
            A new ``PaginatedResponse`` for the next page.

        Raises:
            StopIteration: If there are no more pages.
        """
        if not self.next_url:
            raise StopIteration("No more pages")

        params = self._extract_params(self.next_url)
        response = self._client.request("GET", self._resource_path, params=params)
        data = response.get("data", {})
        meta = response.get("meta", {})
        return PaginatedResponse(data, meta, self._client, self._resource_path)

    def previous_page(self):
        """Fetch the previous page of results.

        Returns:
            A new ``PaginatedResponse`` for the previous page.

        Raises:
            StopIteration: If there is no previous page.
        """
        if not self.previous_url:
            raise StopIteration("No previous page")

        params = self._extract_params(self.previous_url)
        response = self._client.request("GET", self._resource_path, params=params)
        data = response.get("data", {})
        meta = response.get("meta", {})
        return PaginatedResponse(data, meta, self._client, self._resource_path)

    def auto_paging_iter(self):
        """Iterate over all results across every page.

        Yields:
            Each result item from the current page and all subsequent pages.

        Example::

            for link in client.payment_links.list(limit=50).auto_paging_iter():
                print(link["id"])
        """
        page = self
        while True:
            for item in page.results:
                yield item
            if not page.has_more:
                break
            page = page.next_page()

    @staticmethod
    def _extract_params(url):
        """Extract query parameters from a full URL.

        Args:
            url: A full URL string (e.g. ``https://...?cursor=abc&limit=20``).

        Returns:
            A dictionary of query parameter names to values.
        """
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        # parse_qs returns lists; flatten single-value params
        return {k: v[0] if len(v) == 1 else v for k, v in params.items()}

    def __iter__(self):
        return iter(self.results)

    def __len__(self):
        return len(self.results)

    def __repr__(self):
        return "PaginatedResponse(results={}, has_more={})".format(
            len(self.results), self.has_more
        )
