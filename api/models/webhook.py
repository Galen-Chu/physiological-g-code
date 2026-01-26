"""
Webhook Model - Webhooks for event notifications
"""
import secrets
import hmac
import hashlib
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

User = get_user_model()


def generate_webhook_secret():
    """Generate a secure secret for webhook signatures."""
    return secrets.token_hex(32)


class Webhook(models.Model):
    """
    Webhooks for event notifications.

    Allows external services to receive notifications when events occur.
    """

    # User who owns this webhook
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='webhooks',
        help_text='User who owns this webhook',
    )

    # Identification
    name = models.CharField(
        max_length=100,
        help_text='Name for this webhook',
    )

    # Endpoint details
    url = models.URLField(
        max_length=500,
        help_text='URL to send webhook events to',
    )

    # Secret for signature verification
    secret = models.CharField(
        max_length=255,
        default=generate_webhook_secret,
        help_text='Secret used to sign webhook payloads',
    )

    # Events to subscribe to (JSON array)
    # Examples: ['comment.created', 'discussion.created', 'mapping.created']
    events = models.JSONField(
        default=list,
        help_text='Events to subscribe to',
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this webhook is active',
    )

    # Delivery statistics
    total_sent = models.IntegerField(
        default=0,
        help_text='Total number of events sent',
    )

    total_failed = models.IntegerField(
        default=0,
        help_text='Total number of failed deliveries',
    )

    # Last delivery info
    last_success_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last successful delivery',
    )

    last_failure_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last failed delivery',
    )

    last_failure_reason = models.TextField(
        blank=True,
        help_text='Reason for last failure',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Webhook'
        verbose_name_plural = 'Webhooks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_active']),
            models.Index(fields=['events']),
        ]

    def __str__(self):
        return f"{self.name} -> {self.url}"

    def subscribe_to_event(self, event: str):
        """Subscribe to an event."""
        if event not in self.events:
            self.events.append(event)
            self.save()

    def unsubscribe_from_event(self, event: str):
        """Unsubscribe from an event."""
        if event in self.events:
            self.events.remove(event)
            self.save()

    def is_subscribed_to(self, event: str) -> bool:
        """Check if subscribed to an event."""
        return event in self.events or '*' in self.events

    def record_success(self):
        """Record a successful delivery."""
        self.total_sent += 1
        self.last_success_at = timezone.now()
        self.save(update_fields=['total_sent', 'last_success_at'])

    def record_failure(self, reason: str = 'Unknown'):
        """Record a failed delivery."""
        self.total_failed += 1
        self.last_failure_at = timezone.now()
        self.last_failure_reason = reason
        self.save(update_fields=['total_failed', 'last_failure_at', 'last_failure_reason'])

    def generate_signature(self, payload: str) -> str:
        """
        Generate HMAC signature for webhook payload.

        Args:
            payload: JSON string payload

        Returns:
            Hexadecimal signature
        """
        signature = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

    def verify_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: JSON string payload
            signature: Signature from request header

        Returns:
            True if signature is valid
        """
        expected = self.generate_signature(payload)
        return hmac.compare_digest(expected, signature)


class WebhookDeliveryLog(models.Model):
    """
    Log of webhook delivery attempts.
    """

    webhook = models.ForeignKey(
        Webhook,
        on_delete=models.CASCADE,
        related_name='delivery_logs',
        help_text='The webhook that was triggered',
    )

    # Event details
    event_type = models.CharField(
        max_length=50,
        help_text='Type of event that triggered this webhook',
    )

    # Payload
    payload = models.JSONField(
        help_text='Data sent in the webhook',
    )

    # Delivery status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('retrying', 'Retrying'),
        ],
        default='pending',
        help_text='Delivery status',
    )

    # Response
    status_code = models.IntegerField(
        null=True,
        blank=True,
        help_text='HTTP status code from webhook endpoint',
    )

    response_body = models.TextField(
        blank=True,
        help_text='Response body from webhook endpoint',
    )

    # Retry info
    retry_count = models.IntegerField(
        default=0,
        help_text='Number of retry attempts',
    )

    next_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When to retry next',
    )

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When delivery was completed',
    )

    class Meta:
        verbose_name = 'Webhook Delivery Log'
        verbose_name_plural = 'Webhook Delivery Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['event_type']),
        ]

    def __str__(self):
        return f"{self.webhook.name} - {self.event_type} ({self.status})"
