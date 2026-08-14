"""Discussion / Comment serializers."""
from rest_framework import serializers

from api.models import Discussion, Comment


class DiscussionSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Discussion
        fields = (
            'id', 'author', 'title', 'slug', 'content', 'discussion_type',
            'tags', 'linked_hexagram', 'linked_mapping',
            'is_pinned', 'is_locked', 'is_solved',
            'view_count', 'comment_count', 'participant_count',
            'last_comment_at', 'vote_score', 'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'author', 'slug', 'is_pinned', 'is_locked',
            'view_count', 'comment_count', 'participant_count',
            'last_comment_at', 'vote_score', 'created_at', 'updated_at',
        )

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        discussion = super().create(validated_data)

        profile = getattr(validated_data['author'], 'profile', None)
        if profile:
            profile.discussions_started += 1
            profile.save(update_fields=['discussions_started'])
        return discussion


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    discussion = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id', 'author', 'discussion', 'parent', 'content',
            'upvotes', 'downvotes', 'vote_score',
            'is_flagged', 'is_removed', 'removal_reason',
            'created_at', 'updated_at', 'edited_at',
        )
        read_only_fields = (
            'id', 'author', 'discussion', 'upvotes', 'downvotes',
            'vote_score', 'is_flagged', 'is_removed', 'removal_reason',
            'created_at', 'updated_at',
        )

    def get_discussion(self, obj):
        from django.contrib.contenttypes.models import ContentType
        discussion_ct = ContentType.objects.get_for_model(Discussion)
        if obj.content_type_id == discussion_ct.id:
            return obj.object_id
        return None
