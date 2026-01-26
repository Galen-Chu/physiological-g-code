"""
Comment Model - Threaded comments on discussions
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Comment(models.Model):
    """
    Threaded comments on discussions and other content.

    Supports nested replies via parent field.
    """

    # Generic foreign key for commenting on any model
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        help_text='Type of object being commented on',
    )

    object_id = models.PositiveIntegerField(
        help_text='ID of object being commented on',
    )

    # Author
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='User who wrote the comment',
    )

    # Content
    content = models.TextField(
        help_text='Comment content (supports Markdown)',
    )

    # Threaded replies
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text='Parent comment (for threaded replies)',
    )

    # Voting
    upvotes = models.IntegerField(
        default=0,
        help_text='Number of upvotes',
    )

    downvotes = models.IntegerField(
        default=0,
        help_text='Number of downvotes',
    )

    vote_score = models.IntegerField(
        default=0,
        help_text='Net vote score (upvotes - downvotes)',
    )

    # Moderation
    is_flagged = models.BooleanField(
        default=False,
        help_text='Comment has been flagged for review',
    )

    is_removed = models.BooleanField(
        default=False,
        help_text='Comment has been removed by moderator',
    )

    removal_reason = models.TextField(
        blank=True,
        help_text='Reason for removal',
    )

    # Mention detection (store mentioned user IDs)
    mentioned_users = models.JSONField(
        blank=True,
        null=True,
        help_text='List of mentioned user IDs',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time comment was edited',
    )

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['author']),
            models.Index(fields=['parent']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['-vote_score']),
        ]

    def __str__(self):
        preview = self.content[:50]
        return f"{self.author.username}: {preview}..."

    def get_replies(self):
        """Get all replies to this comment."""
        return Comment.objects.filter(parent=self, is_removed=False)

    def get_thread(self):
        """Get all comments in thread (this comment and all replies)."""
        thread = [self]
        for reply in self.get_replies():
            thread.extend(reply.get_thread())
        return thread

    def mark_as_edited(self):
        """Mark comment as edited."""
        from django.utils import timezone
        self.edited_at = timezone.now()
        self.save(update_fields=['edited_at'])
