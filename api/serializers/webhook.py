"""Webhook serializer. The signing secret is only included on creation/regeneration."""
from rest_framework import serializers

from api.models import Webhook


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = (
            'id', 'name', 'url', 'events', 'is_active',
            'total_sent', 'total_failed',
            'last_success_at', 'last_failure_at', 'last_failure_reason',
            'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'total_sent', 'total_failed',
            'last_success_at', 'last_failure_at', 'last_failure_reason',
            'created_at', 'updated_at',
        )
