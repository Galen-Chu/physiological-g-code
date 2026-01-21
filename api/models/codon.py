"""
Codon Model - Represents DNA/RNA codons (triplets of nucleotides)
"""
from django.db import models
from django.core.validators import RegexValidator


class Codon(models.Model):
    """
    Represents a DNA/RNA codon - a triplet of nucleotides.

    DNA nucleotides: A (Adenine), T (Thymine), G (Guanine), C (Cytosine)
    RNA nucleotides: A (Adenine), U (Uracil), G (Guanine), C (Cytosine)
    """

    class CodonType(models.TextChoices):
        DNA = 'DNA', 'DNA'
        RNA = 'RNA', 'RNA'

    # The codon sequence (e.g., "ATG", "UAG")
    sequence = models.CharField(
        max_length=3,
        validators=[
            RegexValidator(
                regex=r'^[ATGC]{3}$|^[AUGC]{3}$',
                message='Codon must be 3 nucleotides (ATGC for DNA, AUGC for RNA)',
            ),
        ],
        unique=True,
        help_text='Three-nucleotide sequence',
    )

    codon_type = models.CharField(
        max_length=3,
        choices=CodonType.choices,
        default=CodonType.DNA,
        help_text='Type of codon (DNA or RNA)',
    )

    # Amino acid that this codon codes for (Stop codon for termination)
    amino_acid = models.CharField(
        max_length=50,
        help_text='Amino acid coded by this codon (or "Stop" for termination codons)',
    )

    # Single letter abbreviation for amino acid
    amino_acid_code = models.CharField(
        max_length=1,
        help_text='Single letter amino acid code',
    )

    # Full name of amino acid
    amino_acid_full_name = models.CharField(
        max_length=100,
        help_text='Full name of amino acid',
    )

    # Is this a start codon (ATG/Methionine)?
    is_start = models.BooleanField(
        default=False,
        help_text='Whether this is a start codon (ATG)',
    )

    # Is this a stop codon (TAA, TAG, TGA)?
    is_stop = models.BooleanField(
        default=False,
        help_text='Whether this is a stop codon',
    )

    # Binary representation (for mapping to hexagrams)
    # A/T = 0, G/C = 1 (or similar mapping scheme)
    binary_representation = models.CharField(
        max_length=6,
        help_text='Binary representation for hexagram mapping (e.g., "000111")',
    )

    # Hexagram this codon maps to (if any)
    mapped_hexagram = models.ForeignKey(
        'Hexagram',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='codons',
        help_text='The hexagram this codon maps to',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sequence']
        verbose_name = 'Codon'
        verbose_name_plural = 'Codons'
        indexes = [
            models.Index(fields=['sequence']),
            models.Index(fields=['amino_acid_code']),
            models.Index(fields=['is_start']),
            models.Index(fields=['is_stop']),
        ]

    def __str__(self):
        return f"{self.sequence} ({self.codon_type}) -> {self.amino_acid}"

    def to_rna(self):
        """Convert DNA codon to RNA (T -> U)"""
        if self.codon_type == self.CodonType.DNA:
            return self.sequence.replace('T', 'U')
        return self.sequence

    def to_dna(self):
        """Convert RNA codon to DNA (U -> T)"""
        if self.codon_type == self.CodonType.RNA:
            return self.sequence.replace('U', 'T')
        return self.sequence

    def get_complement(self):
        """Get complementary DNA strand (A<->T, G<->C)"""
        complement_map = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
        return ''.join(complement_map.get(base, base) for base in self.sequence)
