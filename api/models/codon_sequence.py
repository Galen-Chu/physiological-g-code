"""
Codon Sequence Model - Represents DNA/RNA sequences
"""
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class CodonSequence(models.Model):
    """
    Represents a DNA or RNA sequence that can be analyzed
    and translated into hexagrams.
    """

    class SequenceType(models.TextChoices):
        DNA = 'DNA', 'DNA'
        RNA = 'RNA', 'RNA'

    # Name/identifier for this sequence
    name = models.CharField(
        max_length=200,
        help_text='Name or identifier for this sequence',
    )

    # Description of the sequence (e.g., gene name, protein)
    description = models.TextField(
        blank=True,
        help_text='Description of the sequence',
    )

    # User who owns this sequence
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='codon_sequences',
        help_text='User who owns this sequence',
    )

    # Type of sequence
    sequence_type = models.CharField(
        max_length=3,
        choices=SequenceType.choices,
        default=SequenceType.DNA,
        help_text='Type of sequence (DNA or RNA)',
    )

    # The raw sequence (must be multiple of 3 for complete codons)
    raw_sequence = models.TextField(
        help_text='Raw DNA/RNA sequence string',
    )

    # Organism/source (e.g., "Homo sapiens", "E. coli")
    organism = models.CharField(
        max_length=200,
        blank=True,
        help_text='Source organism',
    )

    # Gene or protein name
    gene_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Associated gene name',
    )

    # Chromosome or location
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text='Chromosomal location',
    )

    # Analysis results (cached)
    amino_acid_sequence = models.TextField(
        blank=True,
        help_text='Translated amino acid sequence',
    )

    hexagram_sequence = models.JSONField(
        default=list,
        blank=True,
        help_text='Sequence of hexagram numbers corresponding to codons',
    )

    # Statistics
    gc_content = models.FloatField(
        null=True,
        blank=True,
        help_text='GC content percentage',
    )

    codon_count = models.IntegerField(
        default=0,
        help_text='Number of codons in sequence',
    )

    # Hexagram analysis
    dominant_hexagram = models.ForeignKey(
        'Hexagram',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dominant_in',
        help_text='Most frequently appearing hexagram',
    )

    hexagram_diversity = models.FloatField(
        null=True,
        blank=True,
        help_text='Shannon diversity index of hexagrams',
    )

    # Is this a reference sequence?
    is_reference = models.BooleanField(
        default=False,
        help_text='Whether this is a reference sequence',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Codon Sequence'
        verbose_name_plural = 'Codon Sequences'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['sequence_type']),
            models.Index(fields=['gene_name']),
            models.Index(fields=['organism']),
        ]

    def __str__(self):
        return f"{self.name} ({self.codon_count} codons)"

    def calculate_gc_content(self):
        """Calculate GC content percentage"""
        seq = self.raw_sequence.upper()
        if len(seq) == 0:
            return 0.0
        gc_count = seq.count('G') + seq.count('C')
        return (gc_count / len(seq)) * 100

    def get_codons(self):
        """Split sequence into codons"""
        seq = self.raw_sequence.upper()
        return [seq[i:i+3] for i in range(0, len(seq), 3)]

    def translate_to_amino_acids(self, codons):
        """Translate codons to amino acid sequence"""
        from .codon import Codon

        amino_acids = []
        for codon_seq in codons:
            try:
                codon = Codon.objects.get(sequence=codon_seq)
                amino_acids.append(codon.amino_acid_code)
            except Codon.DoesNotExist:
                amino_acids.append('X')  # Unknown amino acid
        return ''.join(amino_acids)

    def analyze(self):
        """Perform full analysis of the sequence"""
        codons = self.get_codons()
        self.codon_count = len(codons)
        self.gc_content = self.calculate_gc_content()
        self.amino_acid_sequence = self.translate_to_amino_acids(codons)
        self.save()
