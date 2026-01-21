"""
Codon Translator - Converts DNA/RNA sequences to hexagrams
"""
import logging
from typing import List, Dict, Tuple, Optional
from Bio.Seq import Seq
from Bio.Data import CodonTable

logger = logging.getLogger(__name__)


class CodonTranslator:
    """
    Translates DNA/RNA codon sequences into hexagrams.

    Supports multiple mapping schemes:
    1. Direct binary mapping (nucleotide -> binary -> hexagram)
    2. Complementary strand mapping
    3. Amino acid based mapping
    """

    # Standard DNA to binary mapping schemes
    BINARY_SCHEMES = {
        'scheme_1': {  # A/T=0, G/C=1 (purine/pyrimidine based)
            'A': '0', 'T': '0', 'G': '1', 'C': '1',
            'U': '0'  # RNA equivalent of T
        },
        'scheme_2': {  # A=0, T=1, G=0, C=1 (AT/GC alternation)
            'A': '0', 'T': '1', 'G': '0', 'C': '1',
            'U': '1'
        },
        'scheme_3': {  # A=0, T=0, G=1, C=1 (hydrogen bond count: 2 vs 3)
            'A': '0', 'T': '0', 'G': '1', 'C': '1',
            'U': '0'
        },
        'scheme_4': {  # Molecular weight based
            'A': '0', 'G': '1', 'C': '0', 'T': '1',
            'U': '1'
        },
    }

    def __init__(self, mapping_scheme: str = 'scheme_1'):
        """
        Initialize the translator with a mapping scheme.

        Args:
            mapping_scheme: Name of the binary mapping scheme to use
        """
        self.mapping_scheme = mapping_scheme
        self.binary_map = self.BINARY_SCHEMES.get(
            mapping_scheme,
            self.BINARY_SCHEMES['scheme_1']
        )
        logger.info(f"CodonTranslator initialized with {mapping_scheme}")

    def codon_to_binary(self, codon: str) -> str:
        """
        Convert a single codon to binary representation.

        Args:
            codon: Three-nucleotide sequence (e.g., "ATG")

        Returns:
            Six-bit binary string (e.g., "000111")
        """
        codon = codon.upper()
        binary = ''.join(self.binary_map.get(base, '0') for base in codon)
        return binary

    def binary_to_hexagram_number(self, binary: str) -> int:
        """
        Convert 6-bit binary to hexagram number (1-64).

        Args:
            binary: Six-bit binary string

        Returns:
            Hexagram number (1-64) or None if invalid
        """
        try:
            # Convert binary to integer (0-63)
            value = int(binary, 2)
            # Convert to hexagram number (1-64)
            # Using King Wen sequence or simple binary ordering
            # For now: binary 000000 = hexagram 2, 111111 = hexagram 1
            # This is a simplified approach
            return value + 1
        except ValueError:
            logger.error(f"Invalid binary string: {binary}")
            return None

    def translate_codon(self, codon: str) -> Optional[int]:
        """
        Translate a single codon to hexagram number.

        Args:
            codon: Three-nucleotide sequence

        Returns:
            Hexagram number (1-64) or None if invalid
        """
        binary = self.codon_to_binary(codon)
        return self.binary_to_hexagram_number(binary)

    def translate_sequence(self, sequence: str) -> List[int]:
        """
        Translate a DNA/RNA sequence to hexagram numbers.

        Args:
            sequence: DNA or RNA sequence (must be multiple of 3)

        Returns:
            List of hexagram numbers
        """
        sequence = sequence.upper().replace(' ', '')
        hexagrams = []

        # Split into codons
        codons = [sequence[i:i+3] for i in range(0, len(sequence), 3)]

        for codon in codons:
            if len(codon) == 3:
                hexagram_num = self.translate_codon(codon)
                if hexagram_num:
                    hexagrams.append(hexagram_num)
                else:
                    hexagrams.append(0)  # Invalid codon marker

        return hexagrams

    def translate_to_amino_acids(self, sequence: str, genetic_table: int = 1) -> str:
        """
        Translate DNA sequence to amino acids using BioPython.

        Args:
            sequence: DNA sequence
            genetic_table: NCBI genetic table number (default: 1 = Standard)

        Returns:
            Amino acid sequence string
        """
        try:
            seq_obj = Seq(sequence)
            table = CodonTable.unambiguous_dna_by_id[genetic_table]
            amino_acids = seq_obj.translate(table=table)
            return str(amino_acids)
        except Exception as e:
            logger.error(f"Error translating to amino acids: {e}")
            return ""

    def get_reverse_complement(self, sequence: str) -> str:
        """
        Get reverse complement of DNA sequence.

        Args:
            sequence: DNA sequence

        Returns:
            Reverse complement sequence
        """
        try:
            seq_obj = Seq(sequence)
            return str(seq_obj.reverse_complement())
        except Exception as e:
            logger.error(f"Error getting reverse complement: {e}")
            return ""

    def translate_both_strands(self, sequence: str) -> Dict[str, List[int]]:
        """
        Translate both forward and reverse strands.

        Args:
            sequence: DNA sequence

        Returns:
            Dictionary with 'forward' and 'reverse' hexagram lists
        """
        reverse_seq = self.get_reverse_complement(sequence)
        return {
            'forward': self.translate_sequence(sequence),
            'reverse': self.translate_sequence(reverse_seq)
        }

    def get_codon_frequency(self, hexagram_sequence: List[int]) -> Dict[int, int]:
        """
        Get frequency of each hexagram in a sequence.

        Args:
            hexagram_sequence: List of hexagram numbers

        Returns:
            Dictionary mapping hexagram numbers to counts
        """
        frequency = {}
        for hexagram in hexagram_sequence:
            if hexagram > 0:  # Skip invalid markers
                frequency[hexagram] = frequency.get(hexagram, 0) + 1
        return frequency

    def get_dominant_hexagram(self, hexagram_sequence: List[int]) -> Optional[int]:
        """
        Get the most frequently occurring hexagram.

        Args:
            hexagram_sequence: List of hexagram numbers

        Returns:
            Dominant hexagram number or None if empty
        """
        frequency = self.get_codon_frequency(hexagram_sequence)
        if not frequency:
            return None
        return max(frequency.items(), key=lambda x: x[1])[0]

    def calculate_hexagram_diversity(self, hexagram_sequence: List[int]) -> float:
        """
        Calculate Shannon diversity index of hexagrams.

        Args:
            hexagram_sequence: List of hexagram numbers

        Returns:
            Diversity index (higher = more diverse)
        """
        from collections import Counter
        import math

        # Filter out invalid hexagrams
        valid_hexagrams = [h for h in hexagram_sequence if h > 0]

        if not valid_hexagrams:
            return 0.0

        total = len(valid_hexagrams)
        counts = Counter(valid_hexagrams)

        shannon = 0.0
        for count in counts.values():
            proportion = count / total
            shannon -= proportion * math.log(proportion)

        return shannon


class RNACompatibilityMixin:
    """Mixin for handling RNA sequences (U instead of T)"""

    @staticmethod
    def rna_to_dna(rna_sequence: str) -> str:
        """Convert RNA to DNA (U -> T)"""
        return rna_sequence.upper().replace('U', 'T')

    @staticmethod
    def dna_to_rna(dna_sequence: str) -> str:
        """Convert DNA to RNA (T -> U)"""
        return dna_sequence.upper().replace('T', 'U')
