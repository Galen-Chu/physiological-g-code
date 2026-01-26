"""
User Profile Model - Extended user information for community features
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class UserProfile(models.Model):
    """
    Extended user profile for community features.

    Stores additional user information including:
    - Academic/professional details
    - Research interests
    - Reputation and badges
    - Notification preferences
    """

    # Link to Django User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text='Link to Django User model',
    )

    # Profile information
    bio = models.TextField(
        blank=True,
        max_length=1000,
        help_text='User biography',
    )

    avatar = models.URLField(
        blank=True,
        help_text='URL to user avatar image',
    )

    institution = models.CharField(
        max_length=255,
        blank=True,
        help_text='Academic institution or organization',
    )

    website = models.URLField(
        blank=True,
        help_text='Personal or professional website',
    )

    orcid_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='ORCID identifier for researchers',
    )

    # Research interests (JSON array of tags)
    research_interests = models.JSONField(
        blank=True,
        null=True,
        help_text='Research interest tags',
    )

    # Reputation system
    reputation_score = models.IntegerField(
        default=0,
        help_text='User reputation score',
    )

    # Badges (JSON array of badge names)
    badges = models.JSONField(
        blank=True,
        null=True,
        help_text='Earned badges',
    )

    # Statistics
    sequences_shared = models.IntegerField(
        default=0,
        help_text='Number of sequences shared',
    )

    mappings_created = models.IntegerField(
        default=0,
        help_text='Number of mapping schemes created',
    )

    discussions_started = models.IntegerField(
        default=0,
        help_text='Number of discussion threads started',
    )

    comments_posted = models.IntegerField(
        default=0,
        help_text='Number of comments posted',
    )

    # Notification preferences
    email_notifications = models.BooleanField(
        default=True,
        help_text='Receive email notifications',
    )

    notification_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily digest'),
            ('weekly', 'Weekly digest'),
            ('never', 'Never'),
        ],
        default='immediate',
        help_text='How often to receive notifications',
    )

    # Privacy settings
    show_activity = models.BooleanField(
        default=True,
        help_text='Show activity on profile',
    )

    show_email = models.BooleanField(
        default=False,
        help_text='Show email address on profile',
    )

    allow_messages = models.BooleanField(
        default=True,
        help_text='Allow other users to send messages',
    )

    # Moderation
    is_moderator = models.BooleanField(
        default=False,
        help_text='User has moderator privileges',
    )

    is_banned = models.BooleanField(
        default=False,
        help_text='User is banned from community features',
    )

    ban_reason = models.TextField(
        blank=True,
        help_text='Reason for ban',
    )

    ban_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the ban expires (null = permanent)',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['reputation_score']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_badge_list(self) -> list:
        """Get list of badges."""
        return self.badges if self.badges else []

    def add_badge(self, badge_name: str) -> bool:
        """Add a badge to the user."""
        if self.badges is None:
            self.badges = []
        if badge_name not in self.badges:
            self.badges.append(badge_name)
            self.save()
            return True
        return False

    def award_reputation(self, amount: int):
        """Award reputation points."""
        self.reputation_score += amount
        self.save()

    def increment_stat(self, stat_name: str):
        """Increment a stat counter."""
        if hasattr(self, stat_name):
            current_value = getattr(self, stat_name)
            setattr(self, stat_name, current_value + 1)
            self.save()

    def is_banned_active(self) -> bool:
        """Check if user is currently banned."""
        if not self.is_banned:
            return False
        if self.ban_expires_at is None:
            return True  # Permanent ban
        from django.utils import timezone
        return timezone.now() < self.ban_expires_at

    def get_reputation_level(self) -> str:
        """Get reputation level name."""
        score = self.reputation_score
        if score < 10:
            return 'Newcomer'
        elif score < 50:
            return 'Contributor'
        elif score < 150:
            return 'Researcher'
        elif score < 500:
            return 'Expert'
        elif score < 1000:
            return 'Master'
        else:
            return 'Grandmaster'
