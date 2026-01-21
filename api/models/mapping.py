"""
Codon-Hexagram Mapping Model - Stores mapping schemes between codons and hexagrams
"""
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class CodonHexagramMapping(models.Model):
    """
    Defines how codons map to hexagrams.

    Multiple mapping schemes can exist:
    1. Binary mapping (nucleotide to binary to hexagram)
    2. AI-induced mapping (learning optimal associations)
    3. Traditional mapping (based on ancient correspondences)
    4. Custom user-defined mappings
    """

    class MappingType(models.TextChoices):
        BINARY = 'BINARY', 'Binary'
        AI_INDUCED = 'AI_INDUCED', 'AI Induced'
        TRADITIONAL = 'TRADITIONAL', 'Traditional'
        CUSTOM = 'CUSTOM', 'Custom'
        EXPERIMENTAL = 'EXPERIMENTAL', 'Experimental'

    # Name of this mapping scheme
    name = models.CharField(
        max_length=200,
        help_text='Name of this mapping scheme',
    )

    # Description of the mapping methodology
    description = models.TextField(
        help_text='Description of how this mapping was derived',
    )

    # Type of mapping
    mapping_type = models.CharField(
        max_length=20,
        choices=MappingType.choices,
        default=MappingType.BINARY,
        help_text='Type of mapping scheme',
    )

    # Creator of this mapping (null for system/default mappings)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_mappings',
        help_text='User who created this mapping',
    )

    # Is this the active/default mapping?
    is_active = models.BooleanField(
        default=False,
        help_text='Whether this mapping is currently active',
    )

    # Version tracking
    version = models.CharField(
        max_length=20,
        blank=True,
        help_text='Version of this mapping',
    )

    parent_mapping = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='variants',
        help_text='Parent mapping this was derived from',
    )

    # Mapping rules (stored as JSON for flexibility)
    # Format: [{"codon": "ATG", "hexagram": 1}, ...]
    mapping_rules = models.JSONField(
        default=list,
        help_text='Array of codon-to-hexagram mappings',
    )

    # Binary scheme parameters (for BINARY type)
    binary_scheme = models.JSONField(
        null=True,
        blank=True,
        help_text='Binary mapping scheme parameters',
    )

    # AI model info (for AI_INDUCED type)
    ai_model = models.CharField(
        max_length=100,
        blank=True,
        help_text='AI model used for induction',
    )

    ai_confidence_scores = models.JSONField(
        null=True,
        blank=True,
        help_text='Confidence scores for each mapping',
    )

    # Statistics
    total_mappings = models.IntegerField(
        default=0,
        help_text='Total number of codon-hexagram mappings',
    )

    coverage = models.FloatField(
        default=0.0,
        help_text='Percentage of possible codons mapped',
    )

    # Validation metrics
    validation_score = models.FloatField(
        null=True,
        blank=True,
        help_text='Validation score (if applicable)',
    )

    # Is this mapping published/shared?
    is_public = models.BooleanField(
        default=False,
        help_text='Whether this mapping is public',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', '-created_at']
        verbose_name = 'Codon-Hexagram Mapping'
        verbose_name_plural = 'Codon-Hexagram Mappings'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['mapping_type']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        active_str = " [ACTIVE]" if self.is_active else ""
        return f"{self.name} ({self.mapping_type}){active_str}"

    def get_hexagram_for_codon(self, codon_sequence):
        """Get the hexagram number for a given codon sequence"""
        for rule in self.mapping_rules:
            if rule.get('codon') == codon_sequence:
                return rule.get('hexagram')
        return None

    def calculate_coverage(self):
        """Calculate percentage of possible codons mapped"""
        from .codon import Codon
        total_codons = Codon.objects.count()
        if total_codons == 0:
            self.coverage = 0.0
        else:
            self.coverage = (self.total_mappings / total_codons) * 100
        self.save()
