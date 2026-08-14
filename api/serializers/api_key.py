"""APIKey serializer. The plaintext key is only included on creation."""
from rest_framework import serializers

from api.models import APIKey


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = (
            'id', 'name', 'prefix', 'scopes', 'rate_limit',
            'rate_limit_period', 'is_active', 'expires_at',
            'total_requests', 'last_used_at', 'created_at',
        )
        read_only_fields = (
            'id', 'prefix', 'total_requests', 'last_used_at', 'created_at',
        )
