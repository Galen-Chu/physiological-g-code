"""
API Key Model - API keys for third-party integrations
"""
import secrets
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


def generate_api_key():
    """Generate a secure random API key."""
    return secrets.token_urlsafe(32)


def generate_api_key_prefix():
    """Generate a prefix for the API key (for identification)."""
    return 'pgc_' + secrets.token_urlsafe(8)


class APIKey(models.Model):
    """
    API keys for third-party integrations.

    Allows external applications to access the API on behalf of a user.
    """

    # User who owns this API key
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_keys',
        help_text='User who owns this API key',
    )

    # Key identification
    name = models.CharField(
        max_length=100,
        help_text='Name for this API key (e.g., "Mobile App", "Integration X")',
    )

    # The actual key (stored hashed)
    key = models.CharField(
        max_length=255,
        unique=True,
        default=generate_api_key,
        help_text='The API key',
    )

    # Prefix for display (first few chars only)
    prefix = models.CharField(
        max_length=20,
        unique=True,
        default=generate_api_key_prefix,
        help_text='Key prefix for identification',
    )

    # Scopes/permissions (JSON array of permissions)
    scopes = models.JSONField(
        default=list,
        help_text='Permissions granted to this key',
    )

    # Rate limiting
    rate_limit = models.IntegerField(
        default=1000,
        help_text='Requests per hour',
    )

    rate_limit_period = models.CharField(
        max_length=20,
        choices=[
            ('minute', 'Per minute'),
            ('hour', 'Per hour'),
            ('day', 'Per day'),
        ],
        default='hour',
        help_text='Rate limit period',
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this key is active',
    )

    # Expiration
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this key expires (null = never)',
    )

    # Usage statistics
    total_requests = models.IntegerField(
        default=0,
        help_text='Total requests made with this key',
    )

    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time this key was used',
    )

    # Last used IP
    last_used_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='Last IP address that used this key',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['prefix']),
            models.Index(fields=['is_active']),
            models.Index(fields=['key']),
        ]

    def __str__(self):
        return f"{self.name} ({self.prefix}...)"

    def is_valid(self) -> bool:
        """Check if this key is valid and not expired."""
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True

    def record_usage(self, ip_address=None):
        """Record that this key was used."""
        self.total_requests += 1
        self.last_used_at = timezone.now()
        if ip_address:
            self.last_used_ip = ip_address
        self.save(update_fields=['total_requests', 'last_used_at', 'last_used_ip'])

    def has_scope(self, scope: str) -> bool:
        """Check if this key has a specific scope."""
        return '*' in self.scopes or scope in self.scopes

    @staticmethod
    def generate_key() -> str:
        """Generate a new API key."""
        return generate_api_key()

    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key for storage."""
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()

    def revoke(self):
        """Revoke this API key."""
        self.is_active = False
        self.save()


class APIKeyUsageLog(models.Model):
    """
    Log of API key usage for analytics and debugging.
    """

    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.CASCADE,
        related_name='usage_logs',
        help_text='The API key that was used',
    )

    # Request details
    endpoint = models.CharField(
        max_length=255,
        help_text='API endpoint that was accessed',
    )

    method = models.CharField(
        max_length=10,
        help_text='HTTP method (GET, POST, etc.)',
    )

    # Response
    status_code = models.IntegerField(
        help_text='HTTP response status code',
    )

    # Metadata
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the request',
    )

    user_agent = models.TextField(
        blank=True,
        help_text='User agent string',
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='When the request was made',
    )

    class Meta:
        verbose_name = 'API Key Usage Log'
        verbose_name_plural = 'API Key Usage Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['api_key', '-timestamp']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['status_code']),
        ]

    def __str__(self):
        return f"{self.api_key.name} - {self.endpoint} ({self.status_code})"
