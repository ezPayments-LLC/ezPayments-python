"""Webhook signature verification utilities."""

import hashlib
import hmac
import time

from ezpayments.exceptions import WebhookSignatureError

_DEFAULT_TOLERANCE = 300  # 5 minutes


class Webhook:
    """Verify incoming webhook signatures from ezPayments.

    ezPayments signs every webhook delivery with an HMAC-SHA256 signature
    so you can confirm that the payload was not tampered with.
    """

    @staticmethod
    def verify(secret, signature_header, body, tolerance=_DEFAULT_TOLERANCE):
        """Verify a webhook signature.

        Args:
            secret: The webhook signing secret (provided when you create a
                webhook endpoint).
            signature_header: The value of the ``X-EzPayments-Signature`` header.
            body: The raw request body as ``bytes`` or ``str``.
            tolerance: Maximum allowed age of the signature in seconds.
                Defaults to 300 (5 minutes). Set to ``None`` to disable
                timestamp checking.

        Returns:
            ``True`` if the signature is valid.

        Raises:
            WebhookSignatureError: If the signature is missing, malformed,
                invalid, or if the timestamp is outside the tolerance window.

        Example::

            from ezpayments.webhook import Webhook

            try:
                Webhook.verify(
                    secret="whsec_abc123",
                    signature_header=request.headers["X-EzPayments-Signature"],
                    body=request.body,
                )
                # Signature is valid, process the event
            except WebhookSignatureError:
                # Reject the request
                pass
        """
        if not signature_header:
            raise WebhookSignatureError(message="Missing signature header")

        if isinstance(body, str):
            body = body.encode("utf-8")

        if isinstance(secret, str):
            secret = secret.encode("utf-8")

        timestamp, signatures = Webhook._parse_header(signature_header)

        if not signatures:
            raise WebhookSignatureError(
                message="No v1 signature found in header"
            )

        if tolerance is not None:
            now = int(time.time())
            if abs(now - timestamp) > tolerance:
                raise WebhookSignatureError(
                    message="Signature timestamp is outside the tolerance zone"
                )

        expected = Webhook._compute_signature(timestamp, body, secret)

        for sig in signatures:
            if hmac.compare_digest(expected, sig):
                return True

        raise WebhookSignatureError(message="Signature verification failed")

    @staticmethod
    def _parse_header(header):
        """Parse the signature header into timestamp and signature values.

        The header format is: ``t=<timestamp>,v1=<hex_signature>``

        Args:
            header: Raw header string value.

        Returns:
            A tuple of ``(timestamp_int, [signature_strings])``.

        Raises:
            WebhookSignatureError: If the header is malformed.
        """
        timestamp = None
        signatures = []

        try:
            pairs = header.split(",")
            for pair in pairs:
                key, value = pair.strip().split("=", 1)
                if key == "t":
                    timestamp = int(value)
                elif key == "v1":
                    signatures.append(value)
        except (ValueError, AttributeError):
            raise WebhookSignatureError(message="Malformed signature header")

        if timestamp is None:
            raise WebhookSignatureError(
                message="Missing timestamp in signature header"
            )

        return timestamp, signatures

    @staticmethod
    def _compute_signature(timestamp, body, secret):
        """Compute the expected HMAC-SHA256 signature.

        The signed payload is ``"{timestamp}.{body}"``.

        Args:
            timestamp: Unix timestamp as an integer.
            body: Raw request body as bytes.
            secret: Webhook signing secret as bytes.

        Returns:
            Hex-encoded HMAC-SHA256 signature string.
        """
        signed_payload = "{}.".format(timestamp).encode("utf-8") + body
        return hmac.new(secret, signed_payload, hashlib.sha256).hexdigest()
