"""
Comparative Analyzer - Compare sequences and mapping schemes
"""
import logging
from typing import List, Dict, Tuple, Optional, Any
from collections import Counter
import math
import numpy as np
from scipy import stats
from scipy.spatial.distance import jaccard, cosine

logger = logging.getLogger(__name__)


class ComparativeAnalyzer:
    """
    Comparative analysis for genetic-hexagram sequences.

    This class provides tools for:
    - Side-by-side sequence comparison
    - Mapping scheme comparison
    - Statistical significance testing
    - Similarity metrics calculation
    """

    def __init__(self):
        """Initialize the ComparativeAnalyzer."""
        logger.info("ComparativeAnalyzer initialized")

    def compare_sequences(
        self,
        sequence1: str,
        sequence2: str,
        mapping_scheme: str = 'scheme_1',
        include_alignment: bool = True
    ) -> Dict[str, Any]:
        """
        Compare two sequences side-by-side.

        Args:
            sequence1: First DNA/RNA sequence
            sequence2: Second DNA/RNA sequence
            mapping_scheme: Binary mapping scheme to use
            include_alignment: Whether to include alignment details

        Returns:
            Dictionary with comparison results
        """
        from genetic_engine.codon_translator import CodonTranslator

        # Translate sequences to hexagrams
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagrams1 = translator.translate_sequence(sequence1)
        hexagrams2 = translator.translate_sequence(sequence2)

        # Basic statistics
        stats1 = self._calculate_sequence_stats(hexagrams1, sequence1)
        stats2 = self._calculate_sequence_stats(hexagrams2, sequence2)

        # Calculate similarity metrics
        similarity = self._calculate_pairwise_similarity(hexagrams1, hexagrams2)

        # Side-by-side comparison
        min_length = min(len(hexagrams1), len(hexagrams2))
        side_by_side = []

        for i in range(min_length):
            hex1 = hexagrams1[i]
            hex2 = hexagrams2[i]
            match = hex1 == hex2 and hex1 > 0
            side_by_side.append({
                'position': i + 1,
                'sequence1_hexagram': hex1,
                'sequence2_hexagram': hex2,
                'match': match
            })

        # Count matches
        valid_comparisons = sum(
            1 for item in side_by_side
            if item['sequence1_hexagram'] > 0 and item['sequence2_hexagram'] > 0
        )
        matches = sum(1 for item in side_by_side if item['match'])
        match_percentage = (matches / valid_comparisons * 100) if valid_comparisons > 0 else 0

        # Find differences
        differences = [
            item for item in side_by_side
            if not item['match'] and
            item['sequence1_hexagram'] > 0 and
            item['sequence2_hexagram'] > 0
        ]

        result = {
            'sequence1_stats': stats1,
            'sequence2_stats': stats2,
            'similarity_metrics': similarity,
            'match_percentage': match_percentage,
            'matches': matches,
            'valid_comparisons': valid_comparisons,
            'differences_count': len(differences),
            'mapping_scheme': mapping_scheme
        }

        if include_alignment:
            result['side_by_side'] = side_by_side
            result['differences'] = differences[:100]  # Limit to first 100

        return result

    def compare_mapping_schemes(
        self,
        sequence: str,
        schemes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare different mapping schemes on the same sequence.

        Args:
            sequence: DNA/RNA sequence
            schemes: List of mapping schemes to compare (default: all schemes)

        Returns:
            Dictionary with mapping scheme comparison results
        """
        from genetic_engine.codon_translator import CodonTranslator

        if schemes is None:
            schemes = ['scheme_1', 'scheme_2', 'scheme_3', 'scheme_4']

        results = {}
        hexagram_data = {}

        # Translate using each scheme
        for scheme in schemes:
            translator = CodonTranslator(mapping_scheme=scheme)
            hexagrams = translator.translate_sequence(sequence)
            hexagram_data[scheme] = hexagrams

            stats = self._calculate_sequence_stats(hexagrams, sequence)
            results[scheme] = stats

        # Compare schemes pairwise
        pairwise_comparisons = []
        for i, scheme1 in enumerate(schemes):
            for scheme2 in schemes[i + 1:]:
                hex1 = hexagram_data[scheme1]
                hex2 = hexagram_data[scheme2]

                similarity = self._calculate_pairwise_similarity(hex1, hex2)
                matches = sum(1 for h1, h2 in zip(hex1, hex2) if h1 == h2 and h1 > 0)
                valid_pairs = sum(1 for h1, h2 in zip(hex1, hex2) if h1 > 0 and h2 > 0)
                match_pct = (matches / valid_pairs * 100) if valid_pairs > 0 else 0

                pairwise_comparisons.append({
                    'scheme1': scheme1,
                    'scheme2': scheme2,
                    'matches': matches,
                    'valid_pairs': valid_pairs,
                    'match_percentage': match_pct,
                    'similarity': similarity
                })

        return {
            'sequence_length': len(sequence),
            'schemes_compared': schemes,
            'scheme_results': results,
            'pairwise_comparisons': pairwise_comparisons
        }

    def statistical_significance_test(
        self,
        sequence1: str,
        sequence2: str,
        test_type: str = 'chi_square',
        mapping_scheme: str = 'scheme_1'
    ) -> Dict[str, Any]:
        """
        Perform statistical significance tests on hexagram distributions.

        Args:
            sequence1: First sequence
            sequence2: Second sequence
            test_type: Type of test ('chi_square', 'fisher_exact', 'ks_test')
            mapping_scheme: Binary mapping scheme

        Returns:
            Dictionary with test results
        """
        from genetic_engine.codon_translator import CodonTranslator

        # Translate sequences
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagrams1 = [h for h in translator.translate_sequence(sequence1) if h > 0]
        hexagrams2 = [h for h in translator.translate_sequence(sequence2) if h > 0]

        result = {
            'test_type': test_type,
            'sequence1_count': len(hexagrams1),
            'sequence2_count': len(hexagrams2),
            'mapping_scheme': mapping_scheme
        }

        if test_type == 'chi_square':
            result.update(self._chi_square_test(hexagrams1, hexagrams2))
        elif test_type == 'fisher_exact':
            result.update(self._fisher_exact_test(hexagrams1, hexagrams2))
        elif test_type == 'ks_test':
            result.update(self._kolmogorov_smirnov_test(hexagrams1, hexagrams2))
        else:
            result['error'] = f'Unknown test type: {test_type}'

        return result

    def calculate_similarity_metrics(
        self,
        sequence1: str,
        sequence2: str,
        mapping_scheme: str = 'scheme_1'
    ) -> Dict[str, Any]:
        """
        Calculate multiple similarity metrics between two sequences.

        Args:
            sequence1: First sequence
            sequence2: Second sequence
            mapping_scheme: Binary mapping scheme

        Returns:
            Dictionary with various similarity metrics
        """
        from genetic_engine.codon_translator import CodonTranslator

        # Translate sequences
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagrams1 = translator.translate_sequence(sequence1)
        hexagrams2 = translator.translate_sequence(sequence2)

        return self._calculate_pairwise_similarity(hexagrams1, hexagrams2, detailed=True)

    def _calculate_sequence_stats(
        self,
        hexagrams: List[int],
        raw_sequence: str
    ) -> Dict[str, Any]:
        """Calculate statistics for a hexagram sequence."""
        from collections import Counter

        valid_hexagrams = [h for h in hexagrams if h > 0]

        if not valid_hexagrams:
            return {
                'total_codons': len(hexagrams),
                'valid_hexagrams': 0,
                'dominant_hexagram': None,
                'diversity': 0.0
            }

        counts = Counter(valid_hexagrams)
        dominant, dominant_count = counts.most_common(1)[0]

        # Calculate Shannon diversity
        total = len(valid_hexagrams)
        diversity = 0.0
        for count in counts.values():
            proportion = count / total
            diversity -= proportion * math.log(proportion)

        return {
            'total_codons': len(hexagrams),
            'valid_hexagrams': len(valid_hexagrams),
            'unique_hexagrams': len(counts),
            'dominant_hexagram': dominant,
            'dominant_frequency': dominant_count / total,
            'diversity': diversity
        }

    def _calculate_pairwise_similarity(
        self,
        hexagrams1: List[int],
        hexagrams2: List[int],
        detailed: bool = False
    ) -> Dict[str, Any]:
        """Calculate similarity metrics between two hexagram sequences."""
        # Filter invalid hexagrams
        valid1 = [h for h in hexagrams1 if h > 0]
        valid2 = [h for h in hexagrams2 if h > 0]

        if not valid1 or not valid2:
            return {
                'jaccard': 0.0,
                'cosine': 0.0,
                'overlap': 0.0,
                'matches': 0
            }

        # Create sets for Jaccard
        set1 = set(valid1)
        set2 = set(valid2)

        # Jaccard similarity
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        jaccard_sim = intersection / union if union > 0 else 0

        # Cosine similarity (using frequency vectors)
        counter1 = Counter(valid1)
        counter2 = Counter(valid2)

        all_hexagrams = set(counter1.keys()) | set(counter2.keys())
        vec1 = np.array([counter1.get(h, 0) for h in all_hexagrams])
        vec2 = np.array([counter2.get(h, 0) for h in all_hexagrams])

        cosine_sim = 1 - cosine(vec1, vec2) if np.linalg.norm(vec1) > 0 and np.linalg.norm(vec2) > 0 else 0

        # Overlap coefficient
        overlap = intersection / min(len(set1), len(set2)) if min(len(set1), len(set2)) > 0 else 0

        # Position-wise matches (for aligned comparison)
        min_len = min(len(hexagrams1), len(hexagrams2))
        matches = sum(
            1 for i in range(min_len)
            if hexagrams1[i] == hexagrams2[i] and hexagrams1[i] > 0
        )
        valid_positions = sum(
            1 for i in range(min_len)
            if hexagrams1[i] > 0 and hexagrams2[i] > 0
        )
        match_percentage = (matches / valid_positions * 100) if valid_positions > 0 else 0

        result = {
            'jaccard': jaccard_sim,
            'cosine': cosine_sim,
            'overlap': overlap,
            'match_percentage': match_percentage,
            'matches': matches,
            'valid_positions': valid_positions
        }

        if detailed:
            # Add frequency correlation
            if len(vec1) > 1 and len(vec2) > 1:
                correlation = np.corrcoef(vec1, vec2)[0, 1]
                result['frequency_correlation'] = correlation if not math.isnan(correlation) else 0.0

            # Add hexagram-specific comparison
            common_hexagrams = sorted(set1 & set2)
            unique_to_1 = sorted(set1 - set2)
            unique_to_2 = sorted(set2 - set1)

            result['common_hexagrams'] = common_hexagrams
            result['unique_to_sequence1'] = unique_to_1
            result['unique_to_sequence2'] = unique_to_2
            result['common_count'] = len(common_hexagrams)

        return result

    def _chi_square_test(
        self,
        hexagrams1: List[int],
        hexagrams2: List[int]
    ) -> Dict[str, Any]:
        """Perform chi-square test of independence."""
        # Create contingency table
        all_hexagrams = sorted(set(hexagrams1) | set(hexagrams2))

        # Build observed frequencies
        observed = []
        for hexagram in all_hexagrams:
            observed.append([
                hexagrams1.count(hexagram),
                hexagrams2.count(hexagram)
            ])

        observed = np.array(observed)

        # Perform chi-square test
        try:
            chi2, p_value, dof, expected = stats.chi2_contingency(observed)

            # Interpret p-value
            alpha = 0.05
            significant = p_value < alpha

            return {
                'chi_square_statistic': float(chi2),
                'p_value': float(p_value),
                'degrees_of_freedom': int(dof),
                'is_significant': significant,
                'interpretation': 'Significant difference' if significant else 'No significant difference',
                'alpha': alpha
            }
        except Exception as e:
            return {
                'error': str(e),
                'note': 'Chi-square test failed, possibly due to small sample size'
            }

    def _fisher_exact_test(
        self,
        hexagrams1: List[int],
        hexagrams2: List[int]
    ) -> Dict[str, Any]:
        """
        Perform Fisher's exact test.

        Note: For simplicity, this tests if a specific hexagram
        is enriched in one sequence vs the other.
        """
        # Find the most common hexagram
        counter1 = Counter(hexagrams1)
        counter2 = Counter(hexagrams2)

        # Test the most common hexagram from sequence 1
        if not counter1:
            return {'error': 'No valid hexagrams in sequence 1'}

        target_hexagram = counter1.most_common(1)[0][0]

        # Create 2x2 contingency table
        # [[has_target, no_target], [has_target, no_target]]
        a = counter1.get(target_hexagram, 0)
        b = len(hexagrams1) - a
        c = counter2.get(target_hexagram, 0)
        d = len(hexagrams2) - c

        contingency = [[a, b], [c, d]]

        try:
            odds_ratio, p_value = stats.fisher_exact(contingency)

            alpha = 0.05
            significant = p_value < alpha

            return {
                'hexagram_tested': target_hexagram,
                'contingency_table': {
                    'sequence1_has_target': a,
                    'sequence1_no_target': b,
                    'sequence2_has_target': c,
                    'sequence2_no_target': d
                },
                'odds_ratio': float(odds_ratio),
                'p_value': float(p_value),
                'is_significant': significant,
                'interpretation': f'Hexagram {target_hexagram} is {"enriched" if odds_ratio > 1 else "depleted"} in sequence 1'
            }
        except Exception as e:
            return {
                'error': str(e),
                'note': 'Fisher exact test failed'
            }

    def _kolmogorov_smirnov_test(
        self,
        hexagrams1: List[int],
        hexagrams2: List[int]
    ) -> Dict[str, Any]:
        """Perform Kolmogorov-Smirnov test for distribution similarity."""
        try:
            statistic, p_value = stats.ks_2samp(hexagrams1, hexagrams2)

            alpha = 0.05
            significant = p_value < alpha

            return {
                'ks_statistic': float(statistic),
                'p_value': float(p_value),
                'is_significant': significant,
                'interpretation': 'Different distributions' if significant else 'Similar distributions',
                'alpha': alpha
            }
        except Exception as e:
            return {
                'error': str(e),
                'note': 'KS test failed'
            }

    def compare_multiple_sequences(
        self,
        sequences: List[str],
        sequence_names: Optional[List[str]] = None,
        mapping_scheme: str = 'scheme_1'
    ) -> Dict[str, Any]:
        """
        Compare multiple sequences at once.

        Args:
            sequences: List of DNA/RNA sequences
            sequence_names: Optional names for sequences
            mapping_scheme: Binary mapping scheme

        Returns:
            Dictionary with multi-sequence comparison results
        """
        from genetic_engine.codon_translator import CodonTranslator

        if sequence_names is None:
            sequence_names = [f"Sequence_{i+1}" for i in range(len(sequences))]

        # Translate all sequences
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagram_sequences = [
            translator.translate_sequence(seq) for seq in sequences
        ]

        # Calculate similarity matrix
        n = len(sequences)
        similarity_matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                elif i < j:
                    sim = self._calculate_pairwise_similarity(
                        hexagram_sequences[i],
                        hexagram_sequences[j]
                    )
                    similarity_matrix[i][j] = sim['jaccard']
                    similarity_matrix[j][i] = sim['jaccard']

        # Calculate statistics for each sequence
        sequence_stats = []
        for i, (hexagrams, name) in enumerate(zip(hexagram_sequences, sequence_names)):
            stats = self._calculate_sequence_stats(hexagrams, sequences[i])
            stats['name'] = name
            sequence_stats.append(stats)

        # Find most similar pair
        max_sim = 0
        most_similar_pair = (0, 0)
        for i in range(n):
            for j in range(i + 1, n):
                if similarity_matrix[i][j] > max_sim:
                    max_sim = similarity_matrix[i][j]
                    most_similar_pair = (i, j)

        # Find most divergent pair
        min_sim = 1.0
        most_divergent_pair = (0, 0)
        for i in range(n):
            for j in range(i + 1, n):
                if similarity_matrix[i][j] < min_sim:
                    min_sim = similarity_matrix[i][j]
                    most_divergent_pair = (i, j)

        return {
            'sequence_count': n,
            'sequence_names': sequence_names,
            'sequence_stats': sequence_stats,
            'similarity_matrix': similarity_matrix,
            'most_similar_pair': {
                'indices': list(most_similar_pair),
                'names': [sequence_names[most_similar_pair[0]], sequence_names[most_similar_pair[1]]],
                'similarity': max_sim
            },
            'most_divergent_pair': {
                'indices': list(most_divergent_pair),
                'names': [sequence_names[most_divergent_pair[0]], sequence_names[most_divergent_pair[1]]],
                'similarity': min_sim
            },
            'mapping_scheme': mapping_scheme
        }

    def find_conserved_regions(
        self,
        sequences: List[str],
        window_size: int = 5,
        min_conservation: float = 0.8,
        mapping_scheme: str = 'scheme_1'
    ) -> Dict[str, Any]:
        """
        Find regions that are conserved across multiple sequences.

        Args:
            sequences: List of sequences to compare
            window_size: Size of sliding window
            min_conservation: Minimum conservation threshold (0-1)
            mapping_scheme: Binary mapping scheme

        Returns:
            Dictionary with conserved region data
        """
        from genetic_engine.codon_translator import CodonTranslator

        # Translate sequences
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagram_sequences = [
            translator.translate_sequence(seq) for seq in sequences
        ]

        # Find minimum length
        min_length = min(len(hs) for hs in hexagram_sequences)

        # Slide window and calculate conservation
        conserved_regions = []
        current_region = None

        for pos in range(0, min_length - window_size + 1):
            # Extract window from each sequence
            windows = [hs[pos:pos + window_size] for hs in hexagram_sequences]

            # Calculate conservation
            # A position is conserved if all sequences have the same hexagram
            conserved_positions = 0
            for i in range(window_size):
                hexagrams_at_pos = [w[i] for w in windows if i < len(w) and w[i] > 0]
                if hexagrams_at_pos and len(set(hexagrams_at_pos)) == 1:
                    conserved_positions += 1

            conservation = conserved_positions / window_size

            if conservation >= min_conservation:
                if current_region is None:
                    current_region = {
                        'start_position': pos + 1,  # 1-indexed
                        'end_position': pos + window_size,
                        'max_conservation': conservation,
                        'windows': []
                    }
                else:
                    current_region['end_position'] = pos + window_size
                    current_region['max_conservation'] = max(
                        current_region['max_conservation'],
                        conservation
                    )

                current_region['windows'].append({
                    'position': pos + 1,
                    'conservation': conservation,
                    'conserved_hexagrams': [
                        w[i] if i < len(w) else 0
                        for w in windows
                        for i in range(window_size)
                    ]
                })
            else:
                if current_region is not None:
                    current_region['length'] = (
                        current_region['end_position'] - current_region['start_position'] + 1
                    )
                    current_region['avg_conservation'] = sum(
                        w['conservation'] for w in current_region['windows']
                    ) / len(current_region['windows'])
                    conserved_regions.append(current_region)
                    current_region = None

        # Don't forget the last region
        if current_region is not None:
            current_region['length'] = (
                current_region['end_position'] - current_region['start_position'] + 1
            )
            current_region['avg_conservation'] = sum(
                w['conservation'] for w in current_region['windows']
            ) / len(current_region['windows'])
            conserved_regions.append(current_region)

        return {
            'sequence_count': len(sequences),
            'window_size': window_size,
            'min_conservation': min_conservation,
            'min_length': min_length,
            'conserved_regions': conserved_regions,
            'total_regions': len(conserved_regions)
        }
