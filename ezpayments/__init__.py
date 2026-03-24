"""ezPayments Python SDK.

A Python client library for the ezPayments Merchant API v3.

Basic usage::

    from ezpayments import EzPayments

    client = EzPayments(api_key="sk_live_xxx")
    link = client.payment_links.create(amount="50.00", description="Order #1")
"""

__version__ = "0.1.0"

from ezpayments.client import EzPayments
from ezpayments.exceptions import (
    APIError,
    AuthenticationError,
    EzPaymentsError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    WebhookSignatureError,
)
from ezpayments.pagination import PaginatedResponse
from ezpayments.webhook import Webhook

__all__ = [
    "EzPayments",
    "PaginatedResponse",
    "Webhook",
    "EzPaymentsError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "APIError",
    "WebhookSignatureError",
    "__version__",
]
