"""
Notification Model - User notifications for community activity
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """
    User notifications for community activity.

    Types of notifications:
    - comment_reply: Someone replied to your comment
    - comment_mention: Someone mentioned you in a comment
    - discussion_reply: Someone replied to your discussion
    - vote_received: Your content was upvoted
    - badge_earned: You earned a badge
    - mapping_approved: Your mapping was approved
    """

    class NotificationType(models.TextChoices):
        COMMENT_REPLY = 'comment_reply', 'Comment Reply'
        COMMENT_MENTION = 'comment_mention', 'Comment Mention'
        DISCUSSION_REPLY = 'discussion_reply', 'Discussion Reply'
        VOTE_RECEIVED = 'vote_received', 'Vote Received'
        BADGE_EARNED = 'badge_earned', 'Badge Earned'
        MAPPING_APPROVED = 'mapping_approved', 'Mapping Approved'
        MAPPING_FORKED = 'mapping_forked', 'Mapping Forked'
        CUSTOM = 'custom', 'Custom Notification'

    # Recipient
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text='User receiving the notification',
    )

    # Type
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        help_text='Type of notification',
    )

    # Actor (user who triggered the notification)
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='triggered_notifications',
        help_text='User who triggered the notification',
    )

    # Generic foreign key to the related object
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Type of related object',
    )

    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='ID of related object',
    )

    # Content
    title = models.CharField(
        max_length=255,
        help_text='Notification title',
    )

    message = models.TextField(
        help_text='Notification message',
    )

    url = models.URLField(
        blank=True,
        help_text='URL to link to',
    )

    # Status
    is_read = models.BooleanField(
        default=False,
        help_text='Notification has been read',
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When notification was read',
    )

    # Email notification
    email_sent = models.BooleanField(
        default=False,
        help_text='Email notification has been sent',
    )

    email_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When email was sent',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.recipient.username}: {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    @classmethod
    def create_notification(cls, recipient, notification_type, title, message, url='', actor=None, content_object=None):
        """Create a new notification."""
        from django.contrib.contenttypes.models import ContentType

        content_type = None
        object_id = None

        if content_object:
            content_type = ContentType.objects.get_for_model(content_object)
            object_id = content_object.pk

        return Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            url=url,
            actor=actor,
            content_type=content_type,
            object_id=object_id
        )
