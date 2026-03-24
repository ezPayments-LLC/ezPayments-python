"""Tests for webhook signature verification."""

import hashlib
import hmac
import time

import pytest

from ezpayments.exceptions import WebhookSignatureError
from ezpayments.webhook import Webhook


class TestWebhookVerification:
    """Test webhook signature verification."""

    def _make_signature(self, secret, body, timestamp=None):
        """Helper to create a valid signature header."""
        if timestamp is None:
            timestamp = int(time.time())
        if isinstance(body, str):
            body = body.encode("utf-8")
        if isinstance(secret, str):
            secret = secret.encode("utf-8")

        signed_payload = "{}.".format(timestamp).encode("utf-8") + body
        sig = hmac.new(secret, signed_payload, hashlib.sha256).hexdigest()
        return "t={},v1={}".format(timestamp, sig), timestamp

    def test_valid_signature(self):
        secret = "whsec_test123"
        body = '{"event": "payment_link.paid"}'
        header, _ = self._make_signature(secret, body)

        result = Webhook.verify(secret, header, body)
        assert result is True

    def test_valid_signature_with_bytes_body(self):
        secret = "whsec_test123"
        body = b'{"event": "payment_link.paid"}'
        header, _ = self._make_signature(secret, body)

        result = Webhook.verify(secret, header, body)
        assert result is True

    def test_invalid_signature(self):
        secret = "whsec_test123"
        body = '{"event": "payment_link.paid"}'
        timestamp = int(time.time())
        header = "t={},v1={}".format(timestamp, "a" * 64)

        with pytest.raises(WebhookSignatureError, match="Signature verification failed"):
            Webhook.verify(secret, header, body)

    def test_wrong_secret(self):
        secret = "whsec_test123"
        body = '{"event": "payment_link.paid"}'
        header, _ = self._make_signature(secret, body)

        with pytest.raises(WebhookSignatureError, match="Signature verification failed"):
            Webhook.verify("whsec_wrong_secret", header, body)

    def test_tampered_body(self):
        secret = "whsec_test123"
        body = '{"event": "payment_link.paid"}'
        header, _ = self._make_signature(secret, body)

        with pytest.raises(WebhookSignatureError, match="Signature verification failed"):
            Webhook.verify(secret, header, '{"event": "payment_link.refunded"}')

    def test_missing_signature_header(self):
        with pytest.raises(WebhookSignatureError, match="Missing signature header"):
            Webhook.verify("whsec_test", "", '{"event": "test"}')

    def test_none_signature_header(self):
        with pytest.raises(WebhookSignatureError, match="Missing signature header"):
            Webhook.verify("whsec_test", None, '{"event": "test"}')

    def test_malformed_header(self):
        with pytest.raises(WebhookSignatureError):
            Webhook.verify("whsec_test", "not_a_valid_header", '{"event": "test"}')

    def test_missing_timestamp(self):
        with pytest.raises(WebhookSignatureError, match="Missing timestamp"):
            Webhook.verify("whsec_test", "v1=abcdef", '{"event": "test"}')

    def test_no_v1_signature(self):
        with pytest.raises(WebhookSignatureError, match="No v1 signature found"):
            Webhook.verify("whsec_test", "t=12345", '{"event": "test"}')

    def test_expired_signature(self):
        secret = "whsec_test123"
        body = '{"event": "payment_link.paid"}'
        old_timestamp = int(time.time()) - 600  # 10 minutes ago
        header, _ = self._make_signature(secret, body, timestamp=old_timestamp)

        with pytest.raises(WebhookSignatureError, match="outside the tolerance"):
            Webhook.verify(secret, header, body, tolerance=300)

    def test_tolerance_disabled(self):
        secret = "whsec_test123"
        body = '{"event": "payment_link.paid"}'
        old_timestamp = int(time.time()) - 86400  # 24 hours ago
        header, _ = self._make_signature(secret, body, timestamp=old_timestamp)

        result = Webhook.verify(secret, header, body, tolerance=None)
        assert result is True

    def test_signature_within_tolerance(self):
        secret = "whsec_test123"
        body = '{"event": "payment_link.paid"}'
        recent_timestamp = int(time.time()) - 60  # 1 minute ago
        header, _ = self._make_signature(secret, body, timestamp=recent_timestamp)

        result = Webhook.verify(secret, header, body, tolerance=300)
        assert result is True
