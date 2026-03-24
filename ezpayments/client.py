"""Main client for the ezPayments SDK."""

from ezpayments.http_client import HTTPClient
from ezpayments.resources import APIKeys, PaymentLinks, Transactions, WebhookEndpoints

_DEFAULT_BASE_URL = "https://app.ezpayments.co"


class EzPayments:
    """Client for the ezPayments Merchant API.

    Provides access to all API resources through convenient sub-clients.

    Args:
        api_key: Your ezPayments API secret key (e.g. ``sk_live_xxx``).
        base_url: Override the default API base URL. Useful for testing
            against sandbox environments.
        timeout: Request timeout in seconds. Defaults to 30.

    Attributes:
        payment_links: :class:`~ezpayments.resources.PaymentLinks` resource.
        transactions: :class:`~ezpayments.resources.Transactions` resource.
        webhook_endpoints: :class:`~ezpayments.resources.WebhookEndpoints` resource.
        api_keys: :class:`~ezpayments.resources.APIKeys` resource.

    Example::

        from ezpayments import EzPayments

        client = EzPayments(api_key="sk_live_xxx")
        link = client.payment_links.create(amount="50.00", description="Order #1")
    """

    def __init__(self, api_key, base_url=_DEFAULT_BASE_URL, timeout=30):
        if not api_key:
            raise ValueError("An API key is required. Pass api_key='sk_live_...'")

        self._http_client = HTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

        self.payment_links = PaymentLinks(self._http_client)
        self.transactions = Transactions(self._http_client)
        self.webhook_endpoints = WebhookEndpoints(self._http_client)
        self.api_keys = APIKeys(self._http_client)
