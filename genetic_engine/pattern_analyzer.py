"""
Pattern Analyzer - Advanced pattern detection for genetic-hexagram sequences
"""
import logging
from typing import List, Dict, Tuple, Optional, Any
from collections import Counter, defaultdict
import math
from scipy import stats
import numpy as np

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """
    Advanced pattern detection for genetic-hexagram sequences.

    This class provides tools for:
    - Position-specific hexagram distribution analysis
    - Sliding window pattern detection
    - Motif discovery in hexagram sequences
    - Conservation analysis across sequences
    - Information theory calculations (entropy)
    """

    def __init__(self):
        """Initialize the PatternAnalyzer."""
        logger.info("PatternAnalyzer initialized")

    def analyze_position_patterns(
        self,
        hexagram_sequence: List[int],
        codon_positions: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Analyze position-specific hexagram distribution.

        Determines which hexagrams appear at specific codon positions
        and identifies positional bias.

        Args:
            hexagram_sequence: List of hexagram numbers (1-64)
            codon_positions: Optional list of codon positions (1-indexed)

        Returns:
            Dictionary with position-specific analysis results
        """
        if not hexagram_sequence:
            return {
                'error': 'Empty sequence provided',
                'position_distribution': {},
                'positional_bias': {},
                'dominant_at_position': {}
            }

        # Generate positions if not provided
        if codon_positions is None:
            codon_positions = list(range(1, len(hexagram_sequence) + 1))

        # Group hexagrams by position
        position_hexagrams: Dict[int, List[int]] = defaultdict(list)
        for hexagram, position in zip(hexagram_sequence, codon_positions):
            if hexagram > 0:  # Skip invalid markers
                position_hexagrams[position].append(hexagram)

        # Calculate distribution for each position
        position_distribution: Dict[int, Dict[str, Any]] = {}
        positional_bias: Dict[int, float] = {}
        dominant_at_position: Dict[int, Tuple[int, float]] = {}

        for position, hexagrams in sorted(position_hexagrams.items()):
            counts = Counter(hexagrams)
            total = len(hexagrams)

            # Calculate frequencies
            frequencies = {
                hexagram: count / total for hexagram, count in counts.items()
            }

            # Find dominant hexagram
            dominant_hex, dominant_count = counts.most_common(1)[0]
            dominant_freq = dominant_count / total

            # Calculate positional bias (chi-square expected)
            expected_freq = 1.0 / 64.0  # Expected uniform distribution
            bias = sum(
                (freq - expected_freq) ** 2 / expected_freq
                for freq in frequencies.values()
            )

            position_distribution[position] = {
                'hexagram_counts': dict(counts),
                'frequencies': frequencies,
                'total_codons': total
            }
            positional_bias[position] = bias
            dominant_at_position[position] = (dominant_hex, dominant_freq)

        # Calculate overall statistics
        all_biases = list(positional_bias.values())
        avg_bias = sum(all_biases) / len(all_biases) if all_biases else 0.0

        return {
            'position_distribution': position_distribution,
            'positional_bias': positional_bias,
            'average_bias': avg_bias,
            'dominant_at_position': dominant_at_position,
            'high_bias_positions': {
                pos: bias for pos, bias in positional_bias.items()
                if bias > avg_bias * 2
            }
        }

    def sliding_window_analysis(
        self,
        hexagram_sequence: List[int],
        window_size: int = 3,
        step_size: int = 1
    ) -> Dict[str, Any]:
        """
        Analyze subsequences using a sliding window approach.

        Detects patterns that occur within specific window sizes
        as the window moves across the sequence.

        Args:
            hexagram_sequence: List of hexagram numbers
            window_size: Size of the sliding window (number of codons)
            step_size: How many positions to move the window each step

        Returns:
            Dictionary with sliding window analysis results
        """
        if not hexagram_sequence:
            return {'error': 'Empty sequence provided'}

        if window_size > len(hexagram_sequence):
            return {'error': f'Window size {window_size} exceeds sequence length {len(hexagram_sequence)}'}

        windows = []
        window_patterns = Counter()
        window_start_positions = []

        # Slide window across sequence
        for i in range(0, len(hexagram_sequence) - window_size + 1, step_size):
            window = hexagram_sequence[i:i + window_size]
            windows.append(window)

            # Filter out invalid hexagrams
            valid_window = tuple(h for h in window if h > 0)
            if len(valid_window) == window_size:
                window_patterns[valid_window] += 1
                window_start_positions.append(i + 1)  # 1-indexed

        if not window_patterns:
            return {
                'window_size': window_size,
                'step_size': step_size,
                'total_windows': 0,
                'unique_patterns': 0,
                'patterns': {}
            }

        # Calculate pattern statistics
        total_windows = len(windows)
        pattern_frequencies = {
            pattern: count / total_windows
            for pattern, count in window_patterns.items()
        }

        # Find most common patterns
        most_common = window_patterns.most_common(10)

        # Calculate window diversity
        pattern_entropy = self._calculate_entropy(list(window_patterns.values()))

        return {
            'window_size': window_size,
            'step_size': step_size,
            'total_windows': total_windows,
            'unique_patterns': len(window_patterns),
            'pattern_entropy': pattern_entropy,
            'patterns': {
                'counts': dict(window_patterns),
                'frequencies': pattern_frequencies
            },
            'most_common_patterns': most_common,
            'window_start_positions': window_start_positions
        }

    def discover_motifs(
        self,
        hexagram_sequence: List[int],
        motif_lengths: Optional[List[int]] = None,
        min_occurrences: int = 3,
        max_motifs: int = 20
    ) -> Dict[str, Any]:
        """
        Discover recurring patterns (motifs) in the hexagram sequence.

        A motif is a sequence of hexagrams that occurs multiple times
        throughout the genetic sequence.

        Args:
            hexagram_sequence: List of hexagram numbers
            motif_lengths: List of motif lengths to search for (default: [2,3,4,5])
            min_occurrences: Minimum number of occurrences to be considered a motif
            max_motifs: Maximum number of motifs to return

        Returns:
            Dictionary with discovered motifs
        """
        if not hexagram_sequence:
            return {'error': 'Empty sequence provided'}

        if motif_lengths is None:
            motif_lengths = [2, 3, 4, 5]

        # Filter invalid hexagrams
        valid_sequence = [h for h in hexagram_sequence if h > 0]
        if not valid_sequence:
            return {'error': 'No valid hexagrams in sequence'}

        all_motifs = Counter()
        motif_positions: Dict[Tuple[int, ...], List[int]] = defaultdict(list)

        # Search for motifs of each length
        for length in motif_lengths:
            if length > len(valid_sequence):
                continue

            for i in range(len(valid_sequence) - length + 1):
                motif = tuple(valid_sequence[i:i + length])
                all_motifs[motif] += 1
                motif_positions[motif].append(i + 1)  # 1-indexed

        # Filter by minimum occurrences
        significant_motifs = {
            motif: count for motif, count in all_motifs.items()
            if count >= min_occurrences
        }

        if not significant_motifs:
            return {
                'sequence_length': len(valid_sequence),
                'motif_lengths_searched': motif_lengths,
                'min_occurrences': min_occurrences,
                'motifs_found': 0,
                'motifs': []
            }

        # Sort by frequency and take top motifs
        sorted_motifs = sorted(
            significant_motifs.items(),
            key=lambda x: x[1],
            reverse=True
        )[:max_motifs]

        # Calculate motif statistics
        motif_details = []
        for motif, count in sorted_motifs:
            positions = motif_positions[motif]
            positions_list = sorted(positions)

            # Calculate spacing between occurrences
            if len(positions_list) > 1:
                spacings = [positions_list[i + 1] - positions_list[i]
                           for i in range(len(positions_list) - 1)]
                avg_spacing = sum(spacings) / len(spacings)
                min_spacing = min(spacings)
                max_spacing = max(spacings)
            else:
                avg_spacing = min_spacing = max_spacing = 0

            motif_details.append({
                'motif': list(motif),
                'length': len(motif),
                'occurrences': count,
                'frequency': count / len(valid_sequence),
                'positions': positions_list,
                'avg_spacing': avg_spacing,
                'min_spacing': min_spacing,
                'max_spacing': max_spacing
            })

        # Calculate motif conservation (how much motifs overlap)
        total_motif_coverage = sum(
            len(motif['motif']) * motif['occurrences']
            for motif in motif_details
        )
        coverage_ratio = total_motif_coverage / len(valid_sequence)

        return {
            'sequence_length': len(valid_sequence),
            'motif_lengths_searched': motif_lengths,
            'min_occurrences': min_occurrences,
            'motifs_found': len(motif_details),
            'motif_coverage_ratio': coverage_ratio,
            'motifs': motif_details
        }

    def analyze_conservation(
        self,
        sequences: List[List[int]],
        sequence_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze conservation across multiple sequences.

        Identifies positions and patterns that are conserved (similar)
        across different genetic sequences.

        Args:
            sequences: List of hexagram sequences
            sequence_names: Optional names for each sequence

        Returns:
            Dictionary with conservation analysis results
        """
        if not sequences:
            return {'error': 'No sequences provided'}

        if sequence_names is None:
            sequence_names = [f"Sequence_{i+1}" for i in range(len(sequences))]

        if len(sequence_names) != len(sequences):
            return {'error': 'Number of names must match number of sequences'}

        # Filter invalid hexagrams and pad sequences to same length
        min_length = min(len(seq) for seq in sequences)
        aligned_sequences = []

        for seq in sequences:
            valid_seq = [h for h in seq[:min_length] if h > 0]
            aligned_sequences.append(valid_seq)

        # Calculate position-wise conservation
        position_conservation: List[Dict[str, Any]] = []
        for pos in range(min_length):
            hexagrams_at_pos = [seq[pos] for seq in aligned_sequences if pos < len(seq)]
            if not hexagrams_at_pos:
                continue

            counts = Counter(hexagrams_at_pos)
            most_common_hex, most_common_count = counts.most_common(1)[0]
            conservation_score = most_common_count / len(hexagrams_at_pos)

            position_conservation.append({
                'position': pos + 1,  # 1-indexed
                'hexagram_counts': dict(counts),
                'dominant_hexagram': most_common_hex,
                'dominant_count': most_common_count,
                'conservation_score': conservation_score,
                'is_conserved': conservation_score >= 0.8  # 80% threshold
            })

        # Find highly conserved positions
        highly_conserved = [
            p for p in position_conservation if p['is_conserved']
        ]

        # Calculate sequence similarity matrix
        similarity_matrix = self._calculate_similarity_matrix(aligned_sequences)

        # Calculate average conservation
        avg_conservation = sum(
            p['conservation_score'] for p in position_conservation
        ) / len(position_conservation) if position_conservation else 0.0

        return {
            'num_sequences': len(sequences),
            'sequence_names': sequence_names,
            'alignment_length': min_length,
            'average_conservation': avg_conservation,
            'highly_conserved_positions': highly_conserved,
            'position_conservation': position_conservation,
            'similarity_matrix': similarity_matrix,
            'conserved_regions': self._find_conserved_regions(position_conservation)
        }

    def calculate_position_entropy(
        self,
        hexagram_sequence: List[int],
        window_size: int = 10
    ) -> Dict[str, Any]:
        """
        Calculate information theory metrics for sequence positions.

        Uses Shannon entropy to measure the uncertainty/diversity
        at each position or in sliding windows.

        Args:
            hexagram_sequence: List of hexagram numbers
            window_size: Window size for local entropy calculation

        Returns:
            Dictionary with entropy analysis results
        """
        if not hexagram_sequence:
            return {'error': 'Empty sequence provided'}

        # Filter invalid hexagrams
        valid_sequence = [h for h in hexagram_sequence if h > 0]
        if not valid_sequence:
            return {'error': 'No valid hexagrams in sequence'}

        # Calculate position-wise entropy (for multiple aligned sequences)
        # For single sequence, calculate local entropy in windows
        local_entropies = []

        for i in range(0, len(valid_sequence) - window_size + 1):
            window = valid_sequence[i:i + window_size]
            counts = Counter(window)
            entropy = self._calculate_entropy(list(counts.values()))
            local_entropies.append({
                'position': i + 1,  # Start position (1-indexed)
                'window': window,
                'entropy': entropy
            })

        # Calculate overall sequence entropy
        overall_counts = Counter(valid_sequence)
        overall_entropy = self._calculate_entropy(list(overall_counts.values()))

        # Calculate complexity (normalized entropy)
        max_entropy = math.log(64)  # Maximum entropy for 64 possible hexagrams
        complexity = overall_entropy / max_entropy

        # Find information-rich regions (high entropy)
        avg_entropy = sum(e['entropy'] for e in local_entropies) / len(local_entropies)
        high_entropy_regions = [
            e for e in local_entropies
            if e['entropy'] > avg_entropy * 1.5
        ]

        # Find information-poor regions (low entropy = conserved)
        low_entropy_regions = [
            e for e in local_entropies
            if e['entropy'] < avg_entropy * 0.5
        ]

        return {
            'sequence_length': len(valid_sequence),
            'window_size': window_size,
            'overall_entropy': overall_entropy,
            'max_possible_entropy': max_entropy,
            'complexity_score': complexity,
            'average_local_entropy': avg_entropy,
            'high_entropy_regions': high_entropy_regions,
            'low_entropy_regions': low_entropy_regions,
            'local_entropies': local_entropies,
            'hexagram_distribution': dict(overall_counts)
        }

    def _calculate_entropy(self, counts: List[int]) -> float:
        """
        Calculate Shannon entropy from a list of counts.

        Args:
            counts: List of frequency counts

        Returns:
            Shannon entropy value
        """
        if not counts:
            return 0.0

        total = sum(counts)
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in counts:
            if count > 0:
                probability = count / total
                entropy -= probability * math.log(probability)

        return entropy

    def _calculate_similarity_matrix(
        self,
        sequences: List[List[int]]
    ) -> List[List[float]]:
        """
        Calculate pairwise similarity matrix for sequences.

        Args:
            sequences: List of aligned hexagram sequences

        Returns:
            2D list of similarity scores
        """
        n = len(sequences)
        matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 1.0
                elif i < j:
                    # Calculate Jaccard similarity
                    set_i = set(sequences[i])
                    set_j = set(sequences[j])

                    intersection = len(set_i & set_j)
                    union = len(set_i | set_j)

                    similarity = intersection / union if union > 0 else 0.0
                    matrix[i][j] = similarity
                    matrix[j][i] = similarity

        return matrix

    def _find_conserved_regions(
        self,
        position_conservation: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find continuous regions of high conservation.

        Args:
            position_conservation: List of position conservation data

        Returns:
            List of conserved region dictionaries
        """
        conserved_regions = []
        current_region = None

        for pos_data in position_conservation:
            if pos_data['is_conserved']:
                if current_region is None:
                    current_region = {
                        'start_position': pos_data['position'],
                        'end_position': pos_data['position'],
                        'dominant_hexagrams': [pos_data['dominant_hexagram']],
                        'avg_conservation': pos_data['conservation_score']
                    }
                else:
                    current_region['end_position'] = pos_data['position']
                    current_region['dominant_hexagrams'].append(pos_data['dominant_hexagram'])
                    current_region['avg_conservation'] += pos_data['conservation_score']
            else:
                if current_region is not None:
                    # Finalize current region
                    length = current_region['end_position'] - current_region['start_position'] + 1
                    current_region['length'] = length
                    current_region['avg_conservation'] /= length
                    conserved_regions.append(current_region)
                    current_region = None

        # Don't forget the last region
        if current_region is not None:
            length = current_region['end_position'] - current_region['start_position'] + 1
            current_region['length'] = length
            current_region['avg_conservation'] /= length
            conserved_regions.append(current_region)

        return conserved_regions

    def detect_hexagram_run(
        self,
        hexagram_sequence: List[int],
        min_run_length: int = 3
    ) -> Dict[str, Any]:
        """
        Detect runs of the same hexagram.

        Args:
            hexagram_sequence: List of hexagram numbers
            min_run_length: Minimum length to be considered a run

        Returns:
            Dictionary with run detection results
        """
        if not hexagram_sequence:
            return {'error': 'Empty sequence provided'}

        runs = []
        current_hexagram = None
        current_run_start = 0
        current_run_length = 0

        for i, hexagram in enumerate(hexagram_sequence):
            if hexagram <= 0:  # Skip invalid hexagrams
                if current_run_length >= min_run_length:
                    runs.append({
                        'hexagram': current_hexagram,
                        'start_position': current_run_start + 1,  # 1-indexed
                        'end_position': i,  # End before invalid
                        'length': current_run_length
                    })
                current_hexagram = None
                current_run_length = 0
                continue

            if hexagram == current_hexagram:
                current_run_length += 1
            else:
                # Check if previous run meets minimum length
                if current_run_length >= min_run_length:
                    runs.append({
                        'hexagram': current_hexagram,
                        'start_position': current_run_start + 1,
                        'end_position': i,
                        'length': current_run_length
                    })

                current_hexagram = hexagram
                current_run_start = i
                current_run_length = 1

        # Check final run
        if current_run_length >= min_run_length:
            runs.append({
                'hexagram': current_hexagram,
                'start_position': current_run_start + 1,
                'end_position': len(hexagram_sequence),
                'length': current_run_length
            })

        return {
            'min_run_length': min_run_length,
            'total_runs': len(runs),
            'runs': runs
        }

    def calculate_hexagram_correlation(
        self,
        hexagram_sequence: List[int],
        lag: int = 1
    ) -> Dict[str, Any]:
        """
        Calculate autocorrelation of hexagram sequence.

        Args:
            hexagram_sequence: List of hexagram numbers
            lag: Lag distance for autocorrelation

        Returns:
            Dictionary with correlation results
        """
        # Filter invalid hexagrams
        valid_sequence = [h for h in hexagram_sequence if h > 0]

        if len(valid_sequence) < 2 * lag:
            return {'error': 'Sequence too short for autocorrelation with lag {}'.format(lag)}

        # Create lagged sequences
        original = valid_sequence[:-lag]
        lagged = valid_sequence[lag:]

        # Calculate correlation
        correlation = np.corrcoef(original, lagged)[0, 1]

        return {
            'lag': lag,
            'correlation': correlation if not math.isnan(correlation) else 0.0,
            'sequence_length': len(valid_sequence),
            'interpretation': self._interpret_correlation(correlation)
        }

    def _interpret_correlation(self, correlation: float) -> str:
        """Interpret correlation coefficient."""
        abs_corr = abs(correlation)
        if abs_corr < 0.1:
            return "No correlation"
        elif abs_corr < 0.3:
            return "Weak correlation"
        elif abs_corr < 0.5:
            return "Moderate correlation"
        elif abs_corr < 0.7:
            return "Strong correlation"
        else:
            return "Very strong correlation"
