"""
Comparative Analysis Model - Stores results of sequence and mapping scheme comparisons
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class ComparativeAnalysis(models.Model):
    """
    Stores results from comparative analyses.

    This model caches comparison results:
    - Sequence vs sequence comparisons
    - Mapping scheme comparisons
    - Statistical test results
    - Multi-sequence alignments
    """

    class AnalysisType(models.TextChoices):
        SEQUENCE_COMPARISON = 'sequence_comparison', 'Sequence Comparison'
        MAPPING_COMPARISON = 'mapping_comparison', 'Mapping Scheme Comparison'
        STATISTICAL_TEST = 'statistical_test', 'Statistical Test'
        MULTIPLE_SEQUENCE = 'multiple_sequence', 'Multiple Sequence Alignment'
        CONSERVED_REGIONS = 'conserved_regions', 'Conserved Regions'
        CUSTOM = 'custom', 'Custom Comparison'

    # User who created this analysis
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comparative_analyses',
        help_text='User who created this analysis',
    )

    # Type of comparison
    analysis_type = models.CharField(
        max_length=50,
        choices=AnalysisType.choices,
        help_text='Type of comparative analysis',
    )

    # Sequences being compared (stored as semicolon-separated)
    sequence1 = models.TextField(
        help_text='First genetic sequence',
    )

    sequence2 = models.TextField(
        blank=True,
        help_text='Second genetic sequence (if applicable)',
    )

    # Additional sequences for multi-sequence analysis
    additional_sequences = models.JSONField(
        blank=True,
        null=True,
        help_text='Additional sequences for multi-sequence analysis',
    )

    # Sequence names
    sequence1_name = models.CharField(
        max_length=255,
        blank=True,
        help_text='Name for sequence 1',
    )

    sequence2_name = models.CharField(
        max_length=255,
        blank=True,
        help_text='Name for sequence 2',
    )

    # Mapping schemes used
    mapping_schemes = models.JSONField(
        help_text='Mapping schemes used in comparison',
    )

    # Comparison results (flexible JSON structure)
    results = models.JSONField(
        help_text='Detailed comparison results',
    )

    # Summary metrics
    similarity_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Overall similarity score (0-1)',
    )

    match_percentage = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text='Percentage of matching hexagrams',
    )

    # Statistical test results (if applicable)
    test_type = models.CharField(
        max_length=50,
        blank=True,
        help_text='Type of statistical test performed',
    )

    p_value = models.FloatField(
        null=True,
        blank=True,
        help_text='P-value from statistical test',
    )

    is_significant = models.BooleanField(
        null=True,
        blank=True,
        help_text='Whether result is statistically significant',
    )

    # Analysis metadata
    analysis_name = models.CharField(
        max_length=255,
        blank=True,
        help_text='Optional name for this analysis',
    )

    analysis_description = models.TextField(
        blank=True,
        help_text='Description of what was compared',
    )

    # Parameters used
    window_size = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Window size used (if applicable)',
    )

    min_conservation = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Minimum conservation threshold (if applicable)',
    )

    # Is this a public analysis?
    is_public = models.BooleanField(
        default=False,
        help_text='Whether this analysis is visible to other users',
    )

    # Tags
    tags = models.JSONField(
        blank=True,
        null=True,
        help_text='Tags for categorizing this analysis',
    )

    # Notes
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about this analysis',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comparative Analysis'
        verbose_name_plural = 'Comparative Analyses'
        indexes = [
            models.Index(fields=['user', 'analysis_type']),
            models.Index(fields=['analysis_type', 'is_public']),
            models.Index(fields=['created_at']),
            models.Index(fields=['similarity_score']),
        ]

    def __str__(self):
        name = self.analysis_name or f"{self.analysis_type}"
        if self.similarity_score is not None:
            return f"{name} (similarity: {self.similarity_score:.2f})"
        return name

    def get_sequence_count(self) -> int:
        """Get the number of sequences in this analysis."""
        count = 1 if self.sequence1 else 0
        count += 1 if self.sequence2 else 0
        count += len(self.additional_sequences) if self.additional_sequences else 0
        return count

    def get_hexagram_difference_count(self) -> int:
        """Get the number of differing hexagrams."""
        if self.results and 'differences_count' in self.results:
            return self.results['differences_count']
        return 0


class ComparisonCache(models.Model):
    """
    Cache for frequently used comparisons.
    """

    # Cache key (hash of input parameters)
    cache_key = models.CharField(
        max_length=255,
        unique=True,
        help_text='Unique key for this cached comparison',
    )

    # User who created (optional, for user-specific caching)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comparison_caches',
        help_text='User who created this cache (null for global cache)',
    )

    # Input parameters
    input_data = models.JSONField(
        help_text='Input parameters for comparison',
    )

    # Cached results
    results = models.JSONField(
        help_text='Cached comparison results',
    )

    # Metadata
    hit_count = models.IntegerField(
        default=0,
        help_text='Number of times this cache was accessed',
    )

    last_accessed = models.DateTimeField(
        auto_now=True,
        help_text='Last time this cache was accessed',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-hit_count', '-created_at']
        verbose_name = 'Comparison Cache'
        verbose_name_plural = 'Comparison Caches'
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['user']),
            models.Index(fields=['last_accessed']),
        ]

    def __str__(self):
        return f"Cache {self.cache_key} ({self.hit_count} hits)"
