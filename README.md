# ezPayments Python SDK

The official Python client library for the [ezPayments](https://app.ezpayments.co) Merchant API v3.

[![PyPI version](https://img.shields.io/pypi/v/ezpayments)](https://pypi.org/project/ezpayments/)
[![Python versions](https://img.shields.io/pypi/pyversions/ezpayments)](https://pypi.org/project/ezpayments/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Installation

```bash
pip install ezpayments
```

## Quick Start

```python
from ezpayments import EzPayments

client = EzPayments(api_key="sk_live_your_key_here")

# Create a payment link
link = client.payment_links.create(
    amount="50.00",
    description="Invoice #1234",
)
print(link["data"]["url"])
```

---

## Configuration

```python
from ezpayments import EzPayments

client = EzPayments(
    api_key="sk_live_your_key_here",
    base_url="https://app.ezpayments.co",  # default
    timeout=30,                              # seconds, default
)
```

| Parameter  | Type  | Default                          | Description                  |
|------------|-------|----------------------------------|------------------------------|
| `api_key`  | `str` | *required*                       | Your API secret key          |
| `base_url` | `str` | `https://app.ezpayments.co`     | API base URL                 |
| `timeout`  | `int` | `30`                             | Request timeout in seconds   |

---

## API Reference

### Payment Links

```python
# Create
link = client.payment_links.create(
    amount="50.00",
    description="Order payment",
    currency="USD",                  # additional fields via kwargs
    idempotency_key="idem_abc123",   # optional
)

# List (with optional filters)
links = client.payment_links.list(page=1, status="active")

# Retrieve
link = client.payment_links.retrieve("pl_abc123")

# Update
link = client.payment_links.update("pl_abc123", description="Updated")

# Delete
client.payment_links.delete("pl_abc123")

# Get fee breakdown
fees = client.payment_links.get_fees("pl_abc123")
```

### Transactions

```python
# List
transactions = client.transactions.list(status="completed", page=1)

# Retrieve
txn = client.transactions.retrieve("txn_abc123")
```

### Webhook Endpoints

```python
# Create
endpoint = client.webhook_endpoints.create(
    url="https://example.com/webhooks",
    events=["payment_link.paid", "payout.completed"],
)
secret = endpoint["data"]["secret"]

# List
endpoints = client.webhook_endpoints.list()

# Retrieve
endpoint = client.webhook_endpoints.retrieve("we_abc123")

# Update
client.webhook_endpoints.update("we_abc123", events=["payment_link.paid"])

# Delete
client.webhook_endpoints.delete("we_abc123")
```

### API Keys

```python
# Create
key = client.api_keys.create(name="Production Key")

# List
keys = client.api_keys.list()

# Delete
client.api_keys.delete("key_abc123")
```

---

## Webhook Verification

Verify incoming webhook signatures to confirm that payloads are authentic and untampered.

```python
from ezpayments.webhook import Webhook
from ezpayments.exceptions import WebhookSignatureError

def webhook_handler(request):
    try:
        Webhook.verify(
            secret="whsec_your_signing_secret",
            signature_header=request.headers["X-EzPayments-Signature"],
            body=request.body,
        )
    except WebhookSignatureError as e:
        return HttpResponse(status=400)

    # Process the verified event
    event = request.json()
    print("Event type:", event["type"])
    return HttpResponse(status=200)
```

**Signature format:**

```
X-EzPayments-Signature: t=1234567890,v1=<hmac_sha256_hex>
```

The SDK computes `HMAC-SHA256(secret, "{timestamp}.{raw_body}")` and compares it against the `v1` value. Signatures older than 5 minutes are rejected by default (configurable via the `tolerance` parameter).

---

## Error Handling

The SDK maps API error responses to typed exception classes:

```python
from ezpayments.exceptions import (
    EzPaymentsError,       # base class for all errors
    AuthenticationError,   # 401 / 403
    ValidationError,       # 400 / 422
    NotFoundError,         # 404
    RateLimitError,        # 429
    APIError,              # 5xx / unexpected
)

try:
    client.payment_links.create(amount="invalid")
except ValidationError as e:
    print(e.message)       # "Amount must be a valid decimal"
    print(e.param)         # "amount"
    print(e.error_code)    # "invalid_amount"
    print(e.request_id)    # "req_abc123"
except AuthenticationError:
    print("Check your API key")
except EzPaymentsError as e:
    print("Unexpected error:", e)
```

**Exception attributes:**

| Attribute     | Type       | Description                          |
|---------------|------------|--------------------------------------|
| `message`     | `str`      | Human-readable error description     |
| `http_status` | `int`      | HTTP status code                     |
| `error_type`  | `str`      | Error type from the API              |
| `error_code`  | `str`      | Machine-readable error code          |
| `param`       | `str`      | Related parameter, if applicable     |
| `request_id`  | `str`      | Request ID for support inquiries     |

---

## Response Format

All API responses follow a standard envelope:

```json
{
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "mode": "live"
  }
}
```

Error responses:

```json
{
  "error": {
    "type": "validation_error",
    "message": "Amount is required",
    "code": "missing_amount",
    "param": "amount"
  }
}
```

---

## Idempotency

All `create` methods accept an optional `idempotency_key` parameter to safely retry requests without creating duplicates:

```python
link = client.payment_links.create(
    amount="50.00",
    idempotency_key="unique_request_id_123",
)
```

---

## Development

```bash
# Clone the repository
git clone https://github.com/elkhayyat/ezpayments-python.git
cd ezpayments-python

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
