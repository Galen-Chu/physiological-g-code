"""
Django management command to load all 64 DNA codons
"""
from django.core.management.base import BaseCommand
from api.models import Codon


class Command(BaseCommand):
    help = 'Load all 64 DNA codons into the database'

    # Standard genetic code
    CODON_TABLE = [
        # (codon, amino_acid, amino_acid_code, amino_acid_full_name, is_start, is_stop)
        ('TTT', 'Phenylalanine', 'F', 'Phenylalanine', False, False),
        ('TTC', 'Phenylalanine', 'F', 'Phenylalanine', False, False),
        ('TTA', 'Leucine', 'L', 'Leucine', False, False),
        ('TTG', 'Leucine', 'L', 'Leucine', False, False),
        ('CTT', 'Leucine', 'L', 'Leucine', False, False),
        ('CTC', 'Leucine', 'L', 'Leucine', False, False),
        ('CTA', 'Leucine', 'L', 'Leucine', False, False),
        ('CTG', 'Leucine', 'L', 'Leucine', False, False),
        ('ATT', 'Isoleucine', 'I', 'Isoleucine', False, False),
        ('ATC', 'Isoleucine', 'I', 'Isoleucine', False, False),
        ('ATA', 'Isoleucine', 'I', 'Isoleucine', False, False),
        ('ATG', 'Methionine', 'M', 'Methionine', True, False),  # Start codon
        ('GTT', 'Valine', 'V', 'Valine', False, False),
        ('GTC', 'Valine', 'V', 'Valine', False, False),
        ('GTA', 'Valine', 'V', 'Valine', False, False),
        ('GTG', 'Valine', 'V', 'Valine', False, False),
        ('TCT', 'Serine', 'S', 'Serine', False, False),
        ('TCC', 'Serine', 'S', 'Serine', False, False),
        ('TCA', 'Serine', 'S', 'Serine', False, False),
        ('TCG', 'Serine', 'S', 'Serine', False, False),
        ('CCT', 'Proline', 'P', 'Proline', False, False),
        ('CCC', 'Proline', 'P', 'Proline', False, False),
        ('CCA', 'Proline', 'P', 'Proline', False, False),
        ('CCG', 'Proline', 'P', 'Proline', False, False),
        ('ACT', 'Threonine', 'T', 'Threonine', False, False),
        ('ACC', 'Threonine', 'T', 'Threonine', False, False),
        ('ACA', 'Threonine', 'T', 'Threonine', False, False),
        ('ACG', 'Threonine', 'T', 'Threonine', False, False),
        ('GCT', 'Alanine', 'A', 'Alanine', False, False),
        ('GCC', 'Alanine', 'A', 'Alanine', False, False),
        ('GCA', 'Alanine', 'A', 'Alanine', False, False),
        ('GCG', 'Alanine', 'A', 'Alanine', False, False),
        ('TAT', 'Tyrosine', 'Y', 'Tyrosine', False, False),
        ('TAC', 'Tyrosine', 'Y', 'Tyrosine', False, False),
        ('TAA', 'Stop', 'Stop', 'Stop Codon', False, True),
        ('TAG', 'Stop', 'Stop', 'Stop Codon', False, True),
        ('CAT', 'Histidine', 'H', 'Histidine', False, False),
        ('CAC', 'Histidine', 'H', 'Histidine', False, False),
        ('CAA', 'Glutamine', 'Q', 'Glutamine', False, False),
        ('CAG', 'Glutamine', 'Q', 'Glutamine', False, False),
        ('AAT', 'Asparagine', 'N', 'Asparagine', False, False),
        ('AAC', 'Asparagine', 'N', 'Asparagine', False, False),
        ('AAA', 'Lysine', 'K', 'Lysine', False, False),
        ('AAG', 'Lysine', 'K', 'Lysine', False, False),
        ('GAT', 'Aspartic Acid', 'D', 'Aspartic Acid', False, False),
        ('GAC', 'Aspartic Acid', 'D', 'Aspartic Acid', False, False),
        ('GAA', 'Glutamic Acid', 'E', 'Glutamic Acid', False, False),
        ('GAG', 'Glutamic Acid', 'E', 'Glutamic Acid', False, False),
        ('TGT', 'Cysteine', 'C', 'Cysteine', False, False),
        ('TGC', 'Cysteine', 'C', 'Cysteine', False, False),
        ('TGA', 'Stop', 'Stop', 'Stop Codon', False, True),
        ('TGG', 'Tryptophan', 'W', 'Tryptophan', False, False),
        ('CGT', 'Arginine', 'R', 'Arginine', False, False),
        ('CGC', 'Arginine', 'R', 'Arginine', False, False),
        ('CGA', 'Arginine', 'R', 'Arginine', False, False),
        ('CGG', 'Arginine', 'R', 'Arginine', False, False),
        ('AGT', 'Serine', 'S', 'Serine', False, False),
        ('AGC', 'Serine', 'S', 'Serine', False, False),
        ('AGA', 'Arginine', 'R', 'Arginine', False, False),
        ('AGG', 'Arginine', 'R', 'Arginine', False, False),
        ('GGT', 'Glycine', 'G', 'Glycine', False, False),
        ('GGC', 'Glycine', 'G', 'Glycine', False, False),
        ('GGA', 'Glycine', 'G', 'Glycine', False, False),
        ('GGG', 'Glycine', 'G', 'Glycine', False, False),
    ]

    def handle(self, *args, **options):
        created = 0
        updated = 0

        # Binary mapping scheme 1: A/T=0, G/C=1
        def codon_to_binary(codon):
            mapping = {'A': '0', 'T': '0', 'G': '1', 'C': '1'}
            return ''.join(mapping[base] for base in codon)

        for codon_data in self.CODON_TABLE:
            (
                codon_seq, amino_acid, aa_code, aa_full_name,
                is_start, is_stop
            ) = codon_data

            codon, created_flag = Codon.objects.update_or_create(
                sequence=codon_seq,
                defaults={
                    'codon_type': 'DNA',
                    'amino_acid': amino_acid,
                    'amino_acid_code': aa_code,
                    'amino_acid_full_name': aa_full_name,
                    'is_start': is_start,
                    'is_stop': is_stop,
                    'binary_representation': codon_to_binary(codon_seq),
                }
            )

            if created_flag:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded codons: {created} created, {updated} updated'
            )
        )
