"""
Hexagram Mapper - Maps codons to I Ching hexagrams with various schemes
"""
import logging
from typing import Dict, List, Optional, Tuple
from django.core.cache import cache

logger = logging.getLogger(__name__)


class HexagramMapper:
    """
    Maps codons to hexagrams using different schemes.

    This class implements various mapping methodologies:
    1. Binary mapping (direct nucleotide to binary conversion)
    2. Trigram-based mapping (codon -> trigrams -> hexagram)
    3. Amino acid property mapping
    4. AI-induced mappings (learned optimal associations)
    """

    # I Ching binary representations (King Wen sequence)
    # Format: [bottom line, ..., top line] where 0=yin, 1=yang
    HEXAGRAM_BINARY_DATA = {
        1: [1, 1, 1, 1, 1, 1],  # Heaven/Heaven
        2: [0, 0, 0, 0, 0, 0],  # Earth/Earth
        3: [1, 0, 0, 0, 1, 0],  # Thunder/Water
        4: [0, 1, 0, 0, 0, 1],  # Water/Mountain
        5: [1, 1, 1, 0, 1, 0],  # Heaven/Water
        6: [0, 1, 0, 1, 1, 1],  # Water/Heaven
        7: [0, 1, 0, 0, 0, 0],  # Water/Earth
        8: [0, 0, 0, 0, 1, 0],  # Earth/Water
        9: [1, 1, 1, 0, 1, 1],  # Heaven/Wind
        10: [1, 1, 0, 1, 1, 1],  # Lake/Heaven
        11: [1, 1, 1, 0, 0, 0],  # Heaven/Earth
        12: [0, 0, 0, 1, 1, 1],  # Earth/Heaven
        13: [1, 0, 1, 1, 1, 1],  # Fire/Heaven
        14: [1, 1, 1, 1, 0, 1],  # Heaven/Fire
        15: [0, 0, 1, 0, 0, 0],  # Mountain/Earth
        16: [0, 0, 0, 1, 0, 0],  # Earth/Thunder
        17: [1, 0, 0, 1, 1, 0],  # Thunder/Lake
        18: [0, 1, 1, 0, 0, 1],  # Wind/Mountain
        19: [1, 1, 0, 0, 0, 0],  # Lake/Earth
        20: [0, 0, 0, 0, 1, 1],  # Earth/Wind
        21: [1, 0, 0, 1, 0, 1],  # Thunder/Fire
        22: [1, 0, 1, 0, 0, 1],  # Fire/Mountain
        23: [0, 0, 0, 0, 0, 1],  # Earth/Mountain
        24: [1, 0, 0, 0, 0, 0],  # Thunder/Earth
        25: [1, 0, 0, 1, 1, 1],  # Thunder/Heaven
        26: [1, 1, 1, 0, 0, 1],  # Heaven/Mountain
        27: [1, 0, 0, 0, 0, 1],  # Thunder/Mountain
        28: [0, 1, 1, 1, 1, 0],  # Wind/Lake
        29: [0, 1, 0, 0, 1, 0],  # Water/Water
        30: [1, 0, 1, 1, 0, 1],  # Fire/Fire
        31: [0, 0, 1, 1, 1, 0],  # Mountain/Lake
        32: [0, 1, 1, 1, 0, 0],  # Wind/Thunder
        33: [0, 0, 1, 1, 1, 1],  # Mountain/Heaven
        34: [1, 1, 1, 1, 0, 0],  # Heaven/Thunder
        35: [0, 0, 0, 1, 0, 1],  # Earth/Fire
        36: [1, 0, 1, 0, 0, 0],  # Fire/Earth
        37: [1, 0, 1, 0, 1, 1],  # Fire/Wind
        38: [1, 1, 0, 1, 0, 1],  # Lake/Fire
        39: [0, 0, 1, 0, 1, 0],  # Mountain/Water
        40: [0, 1, 0, 1, 0, 0],  # Water/Thunder
        41: [1, 1, 0, 0, 0, 1],  # Lake/Mountain
        42: [1, 0, 0, 0, 1, 1],  # Thunder/Wind
        43: [1, 1, 1, 1, 1, 0],  # Heaven/Lake
        44: [0, 1, 1, 1, 1, 1],  # Wind/Heaven
        45: [0, 0, 0, 1, 1, 0],  # Earth/Lake
        46: [0, 1, 1, 0, 0, 0],  # Wind/Earth
        47: [0, 1, 0, 1, 1, 0],  # Water/Lake
        48: [0, 1, 1, 0, 1, 0],  # Wind/Water
        49: [1, 0, 1, 1, 1, 0],  # Fire/Lake
        50: [0, 1, 1, 1, 0, 1],  # Wind/Fire
        51: [1, 0, 0, 1, 0, 0],  # Thunder/Thunder
        52: [0, 0, 1, 0, 0, 1],  # Mountain/Mountain
        53: [0, 0, 1, 0, 1, 1],  # Mountain/Wind
        54: [1, 1, 0, 1, 0, 0],  # Lake/Thunder
        55: [1, 0, 1, 1, 0, 0],  # Fire/Thunder
        56: [0, 0, 1, 1, 0, 1],  # Mountain/Fire
        57: [0, 1, 1, 0, 1, 1],  # Wind/Wind
        58: [1, 1, 0, 1, 1, 0],  # Lake/Lake
        59: [0, 1, 0, 0, 1, 1],  # Water/Wind
        60: [1, 1, 0, 0, 1, 0],  # Lake/Water
        61: [1, 1, 0, 0, 1, 1],  # Lake/Wind
        62: [0, 0, 1, 1, 0, 0],  # Mountain/Thunder
        63: [1, 0, 1, 0, 1, 0],  # Fire/Water
        64: [0, 1, 0, 1, 0, 1],  # Water/Fire
    }

    # Trigram binary values
    TRIGRAMS = {
        '☰': [1, 1, 1],  # Heaven (Qián)
        '☱': [0, 1, 1],  # Lake (Duì)
        '☲': [1, 0, 1],  # Fire (Lí)
        '☳': [1, 0, 0],  # Thunder (Zhèn)
        '☴': [0, 1, 0],  # Wind (Xùn)
        '☵': [0, 0, 1],  # Water (Kǎn)
        '☶': [0, 0, 0],  # Mountain (Gèn)
        '☷': [1, 1, 0],  # Earth (Kūn)
    }

    def __init__(self, mapping_type: str = 'binary'):
        """
        Initialize the mapper.

        Args:
            mapping_type: Type of mapping ('binary', 'trigram', 'amino_acid', 'ai')
        """
        self.mapping_type = mapping_type
        self.cache_prefix = f"hexagram_map_{mapping_type}"
        logger.info(f"HexagramMapper initialized with {mapping_type} mapping")

    def get_hexagram_binary(self, hexagram_number: int) -> Optional[List[int]]:
        """
        Get binary representation of a hexagram.

        Args:
            hexagram_number: Hexagram number (1-64)

        Returns:
            List of 6 binary digits (bottom to top)
        """
        return self.HEXAGRAM_BINARY_DATA.get(hexagram_number)

    def binary_to_hexagram_number(self, binary: List[int]) -> Optional[int]:
        """
        Convert binary representation to hexagram number.

        Args:
            binary: List of 6 binary digits

        Returns:
            Hexagram number (1-64) or None if not found
        """
        binary_str = ''.join(map(str, binary))
        for num, bin_data in self.HEXAGRAM_BINARY_DATA.items():
            if bin_data == list(binary):
                return num
        return None

    def map_codon_binary_to_hexagram(self, codon_binary: str) -> Optional[int]:
        """
        Map a 6-bit codon binary to a hexagram number.

        Args:
            codon_binary: Six-bit binary string

        Returns:
            Hexagram number (1-64) or None
        """
        try:
            # Reverse the binary because hexagram lines are read bottom-to-top
            # but codon position is read left-to-right
            binary_list = [int(b) for b in codon_binary[::-1]]
            return self.binary_to_hexagram_number(binary_list)
        except (ValueError, TypeError):
            return None

    def map_codon_to_hexagram(self, codon: str, scheme: str = 'scheme_1') -> Optional[int]:
        """
        Map a codon to a hexagram using binary mapping.

        Args:
            codon: Three-nucleotide sequence
            scheme: Binary mapping scheme name

        Returns:
            Hexagram number (1-64) or None
        """
        from .codon_translator import CodonTranslator

        translator = CodonTranslator(mapping_scheme=scheme)
        codon_binary = translator.codon_to_binary(codon)
        return self.map_codon_binary_to_hexagram(codon_binary)

    def create_custom_mapping(
        self,
        codon_hexagram_pairs: List[Tuple[str, int]]
    ) -> Dict[str, int]:
        """
        Create a custom codon-to-hexagram mapping.

        Args:
            codon_hexagram_pairs: List of (codon, hexagram_number) tuples

        Returns:
            Dictionary mapping codons to hexagram numbers
        """
        mapping = {}
        for codon, hexagram in codon_hexagram_pairs:
            mapping[codon.upper()] = hexagram
        return mapping

    def validate_mapping(self, mapping: Dict[str, int]) -> Dict[str, any]:
        """
        Validate a codon-hexagram mapping.

        Args:
            mapping: Dictionary mapping codons to hexagram numbers

        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'coverage': 0.0,
            'unique_hexagrams': set()
        }

        # Check if all hexagram numbers are valid (1-64)
        for codon, hexagram in mapping.items():
            if hexagram < 1 or hexagram > 64:
                results['errors'].append(
                    f"Invalid hexagram number {hexagram} for codon {codon}"
                )
                results['valid'] = False
            results['unique_hexagrams'].add(hexagram)

        # Calculate coverage
        from api.models import Codon
        total_codons = Codon.objects.count()
        if total_codons > 0:
            results['coverage'] = (len(mapping) / total_codons) * 100

        # Check for duplicate hexagram mappings
        if len(results['unique_hexagrams']) < len(mapping):
            results['warnings'].append(
                "Multiple codons map to the same hexagram"
            )

        return results

    def get_complementary_hexagram(self, hexagram_number: int) -> Optional[int]:
        """
        Get the complementary hexagram (yin/yang inversion).

        Args:
            hexagram_number: Original hexagram number

        Returns:
            Complementary hexagram number
        """
        binary = self.get_hexagram_binary(hexagram_number)
        if binary is None:
            return None

        # Invert all bits (0->1, 1->0)
        complementary_binary = [1 - bit for bit in binary]
        return self.binary_to_hexagram_number(complementary_binary)

    def get_nuclear_hexagram(self, hexagram_number: int) -> Optional[int]:
        """
        Get the nuclear hexagram (lines 2-5).

        Args:
            hexagram_number: Original hexagram number

        Returns:
            Nuclear hexagram number
        """
        binary = self.get_hexagram_binary(hexagram_number)
        if binary is None:
            return None

        # Take lines 2, 3, 4, 5 (indices 1, 2, 3, 4)
        # Duplicate the middle lines to form a new hexagram
        nuclear_binary = [binary[1], binary[2], binary[3], binary[4]]
        # Pad with first and last lines
        nuclear_binary = [binary[0]] + nuclear_binary[:2] + nuclear_binary[2:] + [binary[5]]

        return self.binary_to_hexagram_number(nuclear_binary)

    def batch_map_codons(
        self,
        codons: List[str],
        mapping: Optional[Dict[str, int]] = None,
        scheme: str = 'scheme_1'
    ) -> List[int]:
        """
        Map multiple codons to hexagrams.

        Args:
            codons: List of codon sequences
            mapping: Optional custom mapping dictionary
            scheme: Binary mapping scheme if not using custom mapping

        Returns:
            List of hexagram numbers
        """
        hexagrams = []

        if mapping:
            # Use custom mapping
            for codon in codons:
                hexagrams.append(mapping.get(codon.upper(), 0))
        else:
            # Use binary scheme
            for codon in codons:
                hexagram = self.map_codon_to_hexagram(codon, scheme)
                hexagrams.append(hexagram if hexagram else 0)

        return hexagrams

    def get_hexagram_transitions(
        self,
        hexagram_sequence: List[int]
    ) -> List[Tuple[int, int]]:
        """
        Get transitions between consecutive hexagrams.

        Args:
            hexagram_sequence: List of hexagram numbers

        Returns:
            List of (from, to) transition tuples
        """
        transitions = []
        for i in range(len(hexagram_sequence) - 1):
            from_hex = hexagram_sequence[i]
            to_hex = hexagram_sequence[i + 1]
            if from_hex > 0 and to_hex > 0:
                transitions.append((from_hex, to_hex))
        return transitions

    def analyze_transition_pattern(
        self,
        transitions: List[Tuple[int, int]]
    ) -> Dict[str, any]:
        """
        Analyze hexagram transition patterns.

        Args:
            transitions: List of (from, to) transition tuples

        Returns:
            Dictionary with transition statistics
        """
        from collections import Counter

        transition_counts = Counter(transitions)
        total = len(transitions)

        return {
            'total_transitions': total,
            'unique_transitions': len(transition_counts),
            'most_common': transition_counts.most_common(10) if transition_counts else [],
            'transition_frequency': dict(transition_counts)
        }
