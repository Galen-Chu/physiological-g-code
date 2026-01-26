"""
Analysis Pattern Model - Stores discovered patterns from genetic-hexagram analysis
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class AnalysisPattern(models.Model):
    """
    Stores patterns discovered through genetic-hexagram analysis.

    This model caches results from various pattern detection algorithms:
    - Position-specific patterns
    - Sliding window patterns
    - Motif discoveries
    - Conservation patterns
    """

    class PatternType(models.TextChoices):
        POSITION_SPECIFIC = 'position', 'Position-Specific'
        SLIDING_WINDOW = 'sliding_window', 'Sliding Window'
        MOTIF = 'motif', 'Motif'
        CONSERVATION = 'conservation', 'Conservation'
        RUN = 'run', 'Hexagram Run'
        CORRELATION = 'correlation', 'Correlation'
        TRANSITION = 'transition', 'Transition Pattern'
        CUSTOM = 'custom', 'Custom Pattern'

    # User who created/found this pattern
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='analysis_patterns',
        help_text='User who discovered this pattern',
    )

    # Type of pattern
    pattern_type = models.CharField(
        max_length=50,
        choices=PatternType.choices,
        help_text='Type of pattern detected',
    )

    # Original genetic sequence (DNA/RNA)
    sequence = models.TextField(
        help_text='Original genetic sequence in which pattern was found',
    )

    # Hexagram sequence derived from genetic sequence
    hexagram_sequence = models.JSONField(
        help_text='Hexagram sequence as JSON array',
    )

    # Pattern data (flexible JSON structure based on pattern type)
    pattern_data = models.JSONField(
        help_text='Detailed pattern data (structure varies by pattern_type)',
    )

    # How many times this pattern occurs
    frequency = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Number of times this pattern occurs in the sequence',
    )

    # Statistical significance score
    significance_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Statistical significance (0-1, higher is more significant)',
    )

    # Pattern metadata
    pattern_name = models.CharField(
        max_length=255,
        blank=True,
        help_text='Optional name for this pattern',
    )

    pattern_description = models.TextField(
        blank=True,
        help_text='Description of what this pattern represents',
    )

    # Analysis parameters
    window_size = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Window size used for sliding window analysis (if applicable)',
    )

    min_occurrences = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Minimum occurrences threshold (if applicable)',
    )

    # Position information
    start_position = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Starting position of pattern in sequence (1-indexed)',
    )

    end_position = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Ending position of pattern in sequence (1-indexed)',
    )

    # Related sequences for comparative analysis
    related_sequences = models.JSONField(
        blank=True,
        null=True,
        help_text='Related sequences used for conservation analysis (if applicable)',
    )

    # Mapping scheme used
    mapping_scheme = models.CharField(
        max_length=50,
        blank=True,
        help_text='Binary mapping scheme used (e.g., "scheme_1")',
    )

    # Is this a public pattern?
    is_public = models.BooleanField(
        default=False,
        help_text='Whether this pattern is visible to other users',
    )

    # Is verified/validated?
    is_verified = models.BooleanField(
        default=False,
        help_text='Whether this pattern has been verified',
    )

    # Tags for categorization
    tags = models.JSONField(
        blank=True,
        null=True,
        help_text='Tags for categorizing this pattern',
    )

    # Notes
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about this pattern',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-significance_score', '-created_at']
        verbose_name = 'Analysis Pattern'
        verbose_name_plural = 'Analysis Patterns'
        indexes = [
            models.Index(fields=['user', 'pattern_type']),
            models.Index(fields=['pattern_type', 'significance_score']),
            models.Index(fields=['is_public']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        name = self.pattern_name or f"{self.pattern_type} Pattern"
        return f"{name} (significance: {self.significance_score:.2f})"

    def get_pattern_length(self) -> int:
        """Get the length of the pattern."""
        if self.start_position and self.end_position:
            return self.end_position - self.start_position + 1
        elif self.hexagram_sequence:
            return len(self.hexagram_sequence)
        return 0

    def get_hexagram_diversity(self) -> float:
        """Calculate diversity of hexagrams in this pattern."""
        if not self.hexagram_sequence:
            return 0.0

        from collections import Counter
        import math

        counts = Counter(self.hexagram_sequence)
        total = len(self.hexagram_sequence)

        if total == 0:
            return 0.0

        shannon = 0.0
        for count in counts.values():
            proportion = count / total
            shannon -= proportion * math.log(proportion)

        return shannon

    def get_dominant_hexagram(self) -> int:
        """Get the most frequent hexagram in this pattern."""
        if not self.hexagram_sequence:
            return 0

        from collections import Counter
        counts = Counter(self.hexagram_sequence)
        if not counts:
            return 0

        return counts.most_common(1)[0][0]


class PatternMatch(models.Model):
    """
    Records where a pattern matches in various sequences.
    """

    # The pattern that matched
    pattern = models.ForeignKey(
        AnalysisPattern,
        on_delete=models.CASCADE,
        related_name='matches',
        help_text='The pattern that was matched',
    )

    # Sequence where match was found
    sequence_id = models.IntegerField(
        help_text='ID of the sequence where pattern was found',
    )

    # Sequence name (optional, denormalized for easy display)
    sequence_name = models.CharField(
        max_length=255,
        blank=True,
        help_text='Name of the sequence where pattern was found',
    )

    # Match positions
    match_positions = models.JSONField(
        help_text='List of positions where pattern matches (1-indexed)',
    )

    # Match quality score
    match_score = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Quality of this match (0-1)',
    )

    # Is this a reverse complement match?
    is_reverse_complement = models.BooleanField(
        default=False,
        help_text='Whether this is a match on the reverse complement strand',
    )

    # Timestamp
    discovered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-match_score', '-discovered_at']
        verbose_name = 'Pattern Match'
        verbose_name_plural = 'Pattern Matches'
        indexes = [
            models.Index(fields=['pattern', 'sequence_id']),
            models.Index(fields=['sequence_id']),
        ]

    def __str__(self):
        return f"Pattern {self.pattern.id} in {self.sequence_name} (score: {self.match_score:.2f})"
