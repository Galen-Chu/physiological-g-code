"""
Vote Model - Votes on comments, discussions, and mappings
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Vote(models.Model):
    """
    User votes on content.

    Supports voting on:
    - Comments
    - Discussions
    - Mappings
    """

    class VoteType(models.TextChoices):
        UPVOTE = 'upvote', 'Upvote'
        DOWNVOTE = 'downvote', 'Downvote'

    # User who cast the vote
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votes',
        help_text='User who cast the vote',
    )

    # Generic foreign key for voting on any model
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        help_text='Type of object being voted on',
    )

    object_id = models.PositiveIntegerField(
        help_text='ID of object being voted on',
    )

    # Vote type
    vote_type = models.CharField(
        max_length=10,
        choices=VoteType.choices,
        help_text='Type of vote',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'
        ordering = ['-created_at']
        unique_together = ['user', 'content_type', 'object_id']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} {self.vote_type} on {self.content_type.model} #{self.object_id}"

    @classmethod
    def get_vote(cls, user, obj):
        """Get user's vote on an object."""
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(obj)
        try:
            return Vote.objects.get(
                user=user,
                content_type=content_type,
                object_id=obj.pk
            )
        except Vote.DoesNotExist:
            return None

    @classmethod
    def toggle_vote(cls, user, obj, vote_type):
        """Toggle a vote (remove if exists, add if doesn't)."""
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(obj)

        # Check if vote already exists
        try:
            existing_vote = Vote.objects.get(
                user=user,
                content_type=content_type,
                object_id=obj.pk
            )
            # If same vote type, remove it (toggle off)
            if existing_vote.vote_type == vote_type:
                existing_vote.delete()
                return 'removed'
            else:
                # Change vote type
                existing_vote.vote_type = vote_type
                existing_vote.save()
                return 'changed'
        except Vote.DoesNotExist:
            # Create new vote
            Vote.objects.create(
                user=user,
                content_type=content_type,
                object_id=obj.pk,
                vote_type=vote_type
            )
            return 'added'
