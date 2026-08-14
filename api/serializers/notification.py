"""Notification serializer."""
from rest_framework import serializers

from api.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.ReadOnlyField(source='actor.username', default=None)

    class Meta:
        model = Notification
        fields = (
            'id', 'recipient', 'actor', 'notification_type',
            'title', 'message', 'url', 'is_read', 'read_at',
            'email_sent', 'created_at',
        )
        read_only_fields = fields
