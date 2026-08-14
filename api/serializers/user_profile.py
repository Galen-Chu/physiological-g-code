"""UserProfile serializers."""
from rest_framework import serializers

from api.models import UserProfile


class PublicProfileSerializer(serializers.ModelSerializer):
    """Fields safe to show for any visitor."""

    username = serializers.CharField(source='user.username', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            'id', 'username', 'bio', 'avatar', 'institution', 'website',
            'orcid_id', 'research_interests', 'reputation_score', 'badges',
            'sequences_shared', 'mappings_created',
            'discussions_started', 'comments_posted', 'date_joined',
        )
        read_only_fields = fields


class OwnProfileSerializer(serializers.ModelSerializer):
    """Full profile, including notification preferences — owner only."""

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            'id', 'username', 'email', 'bio', 'avatar', 'institution',
            'website', 'orcid_id', 'research_interests',
            'reputation_score', 'badges',
            'sequences_shared', 'mappings_created',
            'discussions_started', 'comments_posted',
            'email_notifications', 'notification_frequency',
            'show_activity', 'show_email',
        )
        read_only_fields = (
            'id', 'username', 'email', 'reputation_score', 'badges',
            'sequences_shared', 'mappings_created',
            'discussions_started', 'comments_posted',
        )
