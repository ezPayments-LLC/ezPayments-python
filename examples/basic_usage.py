"""Basic usage examples for the ezPayments Python SDK."""

from ezpayments import EzPayments, Webhook
from ezpayments.exceptions import (
    AuthenticationError,
    NotFoundError,
    ValidationError,
    WebhookSignatureError,
)

# ------------------------------------------------------------------
# 1. Initialize the client
# ------------------------------------------------------------------
client = EzPayments(api_key="sk_live_your_api_key_here")

# ------------------------------------------------------------------
# 2. Payment Links
# ------------------------------------------------------------------

# Create a payment link
link = client.payment_links.create(
    amount="50.00",
    description="Invoice #1234",
    currency="USD",
)
print("Created payment link:", link["data"]["id"])

# List all payment links
links = client.payment_links.list(page=1, status="active")
for item in links["data"]:
    print(" -", item["id"])

# Retrieve a single payment link
link = client.payment_links.retrieve("pl_abc123")

# Update a payment link
updated = client.payment_links.update("pl_abc123", description="Updated description")

# Get fee breakdown
fees = client.payment_links.get_fees("pl_abc123")
print("Fees:", fees["data"])

# Delete a payment link
client.payment_links.delete("pl_abc123")

# ------------------------------------------------------------------
# 3. Transactions
# ------------------------------------------------------------------

# List transactions
transactions = client.transactions.list(status="completed", page=1)
for txn in transactions["data"]:
    print("Transaction:", txn["id"], txn.get("amount"))

# Retrieve a single transaction
txn = client.transactions.retrieve("txn_abc123")

# ------------------------------------------------------------------
# 4. Webhook Endpoints
# ------------------------------------------------------------------

# Create a webhook endpoint
endpoint = client.webhook_endpoints.create(
    url="https://example.com/webhooks/ezpayments",
    events=["payment_link.paid", "payout.completed"],
)
signing_secret = endpoint["data"]["secret"]
print("Webhook secret:", signing_secret)

# List all webhook endpoints
endpoints = client.webhook_endpoints.list()

# Update a webhook endpoint
client.webhook_endpoints.update(
    "we_abc123",
    events=["payment_link.paid", "payment_link.expired"],
)

# Delete a webhook endpoint
client.webhook_endpoints.delete("we_abc123")

# ------------------------------------------------------------------
# 5. API Keys
# ------------------------------------------------------------------

# Create an API key
key = client.api_keys.create(name="CI/CD Key")
print("New API key:", key["data"]["secret_key"])

# List all API keys
keys = client.api_keys.list()

# Delete an API key
client.api_keys.delete("key_abc123")

# ------------------------------------------------------------------
# 6. Webhook Signature Verification
# ------------------------------------------------------------------


def handle_webhook(request):
    """Example webhook handler for a web framework."""
    try:
        Webhook.verify(
            secret="whsec_your_signing_secret",
            signature_header=request.headers["X-EzPayments-Signature"],
            body=request.body,
        )
    except WebhookSignatureError:
        return {"status": 400, "body": "Invalid signature"}

    event = request.json()
    print("Received event:", event["type"])
    return {"status": 200, "body": "OK"}


# ------------------------------------------------------------------
# 7. Error Handling
# ------------------------------------------------------------------

try:
    client.payment_links.create(amount="invalid")
except ValidationError as e:
    print("Validation error:", e.message)
    print("Parameter:", e.param)
except AuthenticationError as e:
    print("Auth error:", e.message)
except NotFoundError as e:
    print("Not found:", e.message)
