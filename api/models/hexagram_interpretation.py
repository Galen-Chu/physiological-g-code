"""
Hexagram Interpretation Model - AI-generated interpretations
"""
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class HexagramInterpretation(models.Model):
    """
    AI-generated interpretation of hexagrams in biological context.
    """

    # Hexagram being interpreted
    hexagram = models.ForeignKey(
        'Hexagram',
        on_delete=models.CASCADE,
        related_name='interpretations',
        help_text='The hexagram being interpreted',
    )

    # User who requested this interpretation
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hexagram_interpretations',
        null=True,
        blank=True,
        help_text='User who requested this interpretation',
    )

    # Context (e.g., specific codon, sequence, or biological process)
    context = models.CharField(
        max_length=200,
        blank=True,
        help_text='Context of interpretation (e.g., codon, gene name)',
    )

    # The interpretation text
    interpretation = models.TextField(
        help_text='AI-generated interpretation',
    )

    # Associated codon (if any)
    codon = models.ForeignKey(
        'Codon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interpretations',
        help_text='Associated codon',
    )

    # Biological significance
    biological_significance = models.TextField(
        blank=True,
        help_text='Biological significance in modern science',
    )

    # Traditional/I Ching meaning
    traditional_meaning = models.TextField(
        blank=True,
        help_text='Traditional I Ching meaning',
    )

    # Synthesis/mode of interpretation
    synthesis = models.TextField(
        blank=True,
        help_text='Synthesis of biological and traditional meanings',
    )

    # Keywords/concepts
    concepts = models.JSONField(
        default=list,
        blank=True,
        help_text='Key concepts and themes',
    )

    # Confidence score (if AI-generated)
    confidence = models.FloatField(
        null=True,
        blank=True,
        help_text='AI confidence score (0-1)',
    )

    # Model version used
    model_version = models.CharField(
        max_length=50,
        blank=True,
        help_text='AI model version used',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Hexagram Interpretation'
        verbose_name_plural = 'Hexagram Interpretations'
        indexes = [
            models.Index(fields=['hexagram']),
            models.Index(fields=['user']),
            models.Index(fields=['codon']),
        ]

    def __str__(self):
        context_str = f" - {self.context}" if self.context else ""
        return f"Interpretation of {self.hexagram}{context_str}"
