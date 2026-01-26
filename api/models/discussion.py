"""
Discussion Model - Community discussion threads
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class Discussion(models.Model):
    """
    Community discussion threads.

    Users can start discussions about:
    - General topics
    - Research findings
    - Questions
    - Announcements
    """

    class DiscussionType(models.TextChoices):
        GENERAL = 'general', 'General Discussion'
        RESEARCH = 'research', 'Research'
        QUESTION = 'question', 'Question'
        ANNOUNCEMENT = 'announcement', 'Announcement'

    # Author
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='discussions',
        help_text='User who created the discussion',
    )

    # Content
    title = models.CharField(
        max_length=255,
        help_text='Discussion title',
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text='URL-friendly version of title',
    )

    content = models.TextField(
        help_text='Discussion content (supports Markdown)',
    )

    discussion_type = models.CharField(
        max_length=20,
        choices=DiscussionType.choices,
        default=DiscussionType.GENERAL,
        help_text='Type of discussion',
    )

    # Tags (JSON array)
    tags = models.JSONField(
        blank=True,
        null=True,
        help_text='Discussion tags',
    )

    # Optional links to hexagrams or mappings
    linked_hexagram = models.ForeignKey(
        'Hexagram',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discussions',
        help_text='Hexagram linked to this discussion',
    )

    linked_mapping = models.ForeignKey(
        'CodonHexagramMapping',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discussions',
        help_text='Mapping scheme linked to this discussion',
    )

    # Status flags
    is_pinned = models.BooleanField(
        default=False,
        help_text='Discussion is pinned to top',
    )

    is_locked = models.BooleanField(
        default=False,
        help_text='Discussion is locked (no new comments)',
    )

    is_solved = models.BooleanField(
        default=False,
        help_text='Question is solved (for question-type discussions)',
    )

    # Statistics
    view_count = models.IntegerField(
        default=0,
        help_text='Number of views',
    )

    comment_count = models.IntegerField(
        default=0,
        help_text='Number of comments',
    )

    participant_count = models.IntegerField(
        default=0,
        help_text='Number of unique participants',
    )

    # Last comment info (denormalized for performance)
    last_comment_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp of last comment',
    )

    last_comment_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='last_comments_in_discussions',
        help_text='User who made the last comment',
    )

    # Voting
    vote_score = models.IntegerField(
        default=0,
        help_text='Net vote score (upvotes - downvotes)',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Discussion'
        verbose_name_plural = 'Discussions'
        ordering = ['-is_pinned', '-last_comment_at', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['author']),
            models.Index(fields=['discussion_type']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['-last_comment_at']),
            models.Index(fields=['is_pinned', '-last_comment_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate slug from title if not provided
        if not self.slug:
            base_slug = slugify(self.title)[:50]
            unique_slug = base_slug
            counter = 1
            while Discussion.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Get URL for this discussion."""
        return reverse('discussion-detail', kwargs={'slug': self.slug})

    def increment_view_count(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def update_participant_count(self):
        """Recalculate participant count."""
        from api.models import Comment
        participants = Comment.objects.filter(
            discussion=self
        ).values_list('author', flat=True).distinct()
        self.participant_count = participants.count() + 1  # +1 for author
        self.save(update_fields=['participant_count'])
