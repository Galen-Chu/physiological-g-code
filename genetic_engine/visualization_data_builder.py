"""
Visualization Data Builder - Build data for interactive visualizations
"""
import logging
from typing import Dict, List, Any, Optional
from collections import Counter
import math

logger = logging.getLogger(__name__)


class VisualizationDataBuilder:
    """
    Build structured data for interactive visualizations.

    This class prepares data for charting libraries like Plotly.js:
    - Frequency distribution charts
    - Transition network graphs
    - Heatmaps
    - 3D relationship visualizations
    """

    def __init__(self):
        """Initialize the VisualizationDataBuilder."""
        logger.info("VisualizationDataBuilder initialized")

    def build_frequency_chart_data(
        self,
        hexagram_sequence: List[int],
        chart_type: str = 'bar',
        top_n: int = 20
    ) -> Dict[str, Any]:
        """
        Build data for frequency distribution charts.

        Args:
            hexagram_sequence: List of hexagram numbers
            chart_type: Type of chart ('bar', 'pie', 'donut')
            top_n: Number of top hexagrams to show

        Returns:
            Dictionary with chart data for Plotly.js
        """
        # Count frequencies
        valid_hexagrams = [h for h in hexagram_sequence if h > 0]
        if not valid_hexagrams:
            return {'error': 'No valid hexagrams in sequence'}

        counts = Counter(valid_hexagrams)
        total = len(valid_hexagrams)

        # Sort by frequency
        sorted_counts = counts.most_common(top_n)

        hexagram_numbers = [str(h) for h, _ in sorted_counts]
        frequencies = [count for _, count in sorted_counts]
        percentages = [count / total * 100 for count in frequencies]

        # Get hexagram names if possible
        hexagram_names = self._get_hexagram_names([h for h, _ in sorted_counts])

        # Build hover text
        hover_text = [
            f"Hexagram {h}<br>{names.get(h, 'Unknown')}<br>Count: {count}<br>{pct:.2f}%"
            for (h, count), names, pct in zip(sorted_counts, [hexagram_names] * len(sorted_counts), percentages)
        ]

        # Build chart configuration
        if chart_type in ['bar', 'histogram']:
            data = {
                'type': 'bar',
                'x': hexagram_numbers,
                'y': frequencies,
                'text': hover_text,
                'hoverinfo': 'text',
                'marker': {
                    'color': frequencies,
                    'colorscale': 'Viridis',
                    'colorbar': {'title': 'Count'}
                },
                'name': 'Frequency'
            }
            layout = {
                'title': 'Hexagram Frequency Distribution',
                'xaxis': {'title': 'Hexagram Number'},
                'yaxis': {'title': 'Count'}
            }

        elif chart_type in ['pie', 'donut']:
            data = {
                'type': 'pie',
                'labels': [f"Hexagram {h}" for h, _ in sorted_counts],
                'values': frequencies,
                'text': hover_text,
                'hoverinfo': 'text+label+value',
                'hole': 0.4 if chart_type == 'donut' else 0,
                'name': 'Frequency'
            }
            layout = {
                'title': f'Hexagram Distribution {"(Donut)" if chart_type == "donut" else ""}'
            }

        else:
            return {'error': f'Unknown chart type: {chart_type}'}

        return {
            'data': [data],
            'layout': layout,
            'config': {'responsive': True}
        }

    def build_transition_network_data(
        self,
        hexagram_sequence: List[int],
        min_edge_weight: int = 1
    ) -> Dict[str, Any]:
        """
        Build data for transition network visualization.

        Shows how hexagrams transition to each other in sequence.

        Args:
            hexagram_sequence: List of hexagram numbers
            min_edge_weight: Minimum transition count to show edge

        Returns:
            Dictionary with network graph data for Plotly.js
        """
        # Get transitions
        transitions = []
        for i in range(len(hexagram_sequence) - 1):
            from_hex = hexagram_sequence[i]
            to_hex = hexagram_sequence[i + 1]
            if from_hex > 0 and to_hex > 0:
                transitions.append((from_hex, to_hex))

        if not transitions:
            return {'error': 'No transitions found'}

        # Count transitions
        transition_counts = Counter(transitions)

        # Filter by minimum weight
        filtered_transitions = {
            (h1, h2): count for (h1, h2), count in transition_counts.items()
            if count >= min_edge_weight
        }

        if not filtered_transitions:
            return {'error': 'No transitions meet minimum weight threshold'}

        # Build nodes (unique hexagrams)
        unique_hexagrams = set()
        for h1, h2 in filtered_transitions.keys():
            unique_hexagrams.add(h1)
            unique_hexagrams.add(h2)

        hexagram_names = self._get_hexagram_names(list(unique_hexagrams))

        # Calculate node positions (circular layout)
        nodes = []
        num_nodes = len(unique_hexagrams)
        for i, hexagram in enumerate(sorted(unique_hexagrams)):
            angle = 2 * math.pi * i / num_nodes
            nodes.append({
                'id': hexagram,
                'label': str(hexagram),
                'name': hexagram_names.get(hexagram, 'Unknown'),
                'x': math.cos(angle),
                'y': math.sin(angle)
            })

        # Build edges
        edges = []
        for (h1, h2), count in filtered_transitions.items():
            # Find node indices
            x1 = next(n['x'] for n in nodes if n['id'] == h1)
            y1 = next(n['y'] for n in nodes if n['id'] == h1)
            x2 = next(n['x'] for n in nodes if n['id'] == h2)
            y2 = next(n['y'] for n in nodes if n['id'] == h2)

            edges.append({
                'from': h1,
                'to': h2,
                'count': count,
                'x': [x1, x2, None],
                'y': [y1, y2, None]
            })

        # Create trace for edges
        edge_x = []
        edge_y = []
        edge_text = []
        for edge in edges:
            edge_x.extend(edge['x'])
            edge_y.extend(edge['y'])
            edge_text.append(f"{edge['from']} → {edge['to']}<br>Count: {edge['count']}")

        edge_trace = {
            'type': 'scatter',
            'mode': 'lines',
            'x': edge_x,
            'y': edge_y,
            'line': {'width': 1, 'color': '#888'},
            'hoverinfo': 'none'
        }

        # Create trace for nodes
        node_x = [n['x'] for n in nodes]
        node_y = [n['y'] for n in nodes]
        node_text = [
            f"Hexagram {n['id']}<br>{n['name']}<br>Outgoing: {sum(1 for e in edges if e['from'] == n['id'])}<br>Incoming: {sum(1 for e in edges if e['to'] == n['id'])}"
            for n in nodes
        ]

        node_sizes = []
        for n in nodes:
            out_count = sum(1 for e in edges if e['from'] == n['id'])
            in_count = sum(1 for e in edges if e['to'] == n['id'])
            node_sizes.append(10 + (out_count + in_count) * 3)

        node_trace = {
            'type': 'scatter',
            'mode': 'markers+text',
            'x': node_x,
            'y': node_y,
            'text': [str(n['id']) for n in nodes],
            'textposition': 'middle center',
            'textfont': {'size': 10},
            'marker': {
                'size': node_sizes,
                'color': list(range(len(nodes))),
                'colorscale': 'Viridis',
                'line': {'width': 2, 'color': '#fff'}
            },
            'hovertext': node_text,
            'hoverinfo': 'text'
        }

        return {
            'data': [edge_trace, node_trace],
            'layout': {
                'title': 'Hexagram Transition Network',
                'showlegend': False,
                'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                'hovermode': 'closest',
                'margin': {'b': 20, 'l': 5, 'r': 5, 't': 40}
            },
            'config': {'responsive': True}
        }

    def build_heatmap_data(
        self,
        hexagram_sequence: List[int],
        codon_positions: Optional[List[int]] = None,
        window_size: int = 10
    ) -> Dict[str, Any]:
        """
        Build data for position vs hexagram heatmap.

        Args:
            hexagram_sequence: List of hexagram numbers
            codon_positions: Optional codon positions (1-indexed)
            window_size: Window size for aggregating positions

        Returns:
            Dictionary with heatmap data for Plotly.js
        """
        if not hexagram_sequence:
            return {'error': 'Empty sequence provided'}

        # Filter valid hexagrams
        valid_hexagrams = [h for h in hexagram_sequence if h > 0]
        if not valid_hexagrams:
            return {'error': 'No valid hexagrams in sequence'}

        # Aggregate positions into windows
        if codon_positions is None:
            codon_positions = list(range(1, len(valid_hexagrams) + 1))

        # Create position windows
        position_windows = {}
        for i, (hexagram, position) in enumerate(zip(valid_hexagrams, codon_positions)):
            window = (position - 1) // window_size
            if window not in position_windows:
                position_windows[window] = []
            position_windows[window].append(hexagram)

        # Build heatmap matrix
        windows = sorted(position_windows.keys())
        all_hexagrams = sorted(set(valid_hexagrams))

        # Count hexagrams per window
        matrix = []
        for window in windows:
            hexagrams_in_window = position_windows[window]
            counts = Counter(hexagrams_in_window)
            row = [counts.get(h, 0) for h in all_hexagrams]
            matrix.append(row)

        # Build hover text
        hover_text = []
        for i, window in enumerate(windows):
            for j, hexagram in enumerate(all_hexagrams):
                count = matrix[i][j]
                start_pos = window * window_size + 1
                end_pos = (window + 1) * window_size
                hover_text.append(
                    f"Position: {start_pos}-{end_pos}<br>"
                    f"Hexagram: {hexagram}<br>"
                    f"Count: {count}"
                )

        return {
            'data': [{
                'type': 'heatmap',
                'x': [str(h) for h in all_hexagrams],
                'y': [f"{w * window_size + 1}-{(w + 1) * window_size}" for w in windows],
                'z': matrix,
                'hovertext': hover_text,
                'hoverinfo': 'text',
                'colorscale': 'Viridis',
                'colorbar': {'title': 'Count'}
            }],
            'layout': {
                'title': f'Position vs Hexagram Heatmap (Window Size: {window_size})',
                'xaxis': {'title': 'Hexagram'},
                'yaxis': {'title': 'Position Range'}
            },
            'config': {'responsive': True}
        }

    def build_3d_relations_data(
        self,
        sequences: List[List[int]],
        sequence_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Build data for 3D relationship visualization.

        Projects sequences into 3D space based on hexagram patterns.

        Args:
            sequences: List of hexagram sequences
            sequence_names: Optional names for sequences

        Returns:
            Dictionary with 3D scatter data for Plotly.js
        """
        if not sequences:
            return {'error': 'No sequences provided'}

        if sequence_names is None:
            sequence_names = [f"Sequence {i+1}" for i in range(len(sequences))]

        # Calculate features for each sequence
        points = []
        for seq, name in zip(sequences, sequence_names):
            # Filter valid hexagrams
            valid_seq = [h for h in seq if h > 0]
            if not valid_seq:
                continue

            # Feature 1: Diversity (Shannon entropy)
            counts = Counter(valid_seq)
            total = len(valid_seq)
            diversity = 0.0
            for count in counts.values():
                proportion = count / total
                diversity -= proportion * math.log(proportion)

            # Feature 2: Dominance (frequency of most common hexagram)
            most_common_count = counts.most_common(1)[0][1]
            dominance = most_common_count / total

            # Feature 3: Sequence length (normalized)
            length = len(valid_seq)

            points.append({
                'name': name,
                'x': diversity,
                'y': dominance,
                'z': length,
                'diversity': diversity,
                'dominance': dominance,
                'length': length
            })

        if not points:
            return {'error': 'No valid points to plot'}

        return {
            'data': [{
                'type': 'scatter3d',
                'mode': 'markers',
                'x': [p['x'] for p in points],
                'y': [p['y'] for p in points],
                'z': [p['z'] for p in points],
                'text': [p['name'] for p in points],
                'hovertemplate': (
                    '<b>%{text}</b><br>'
                    'Diversity: %{x:.3f}<br>'
                    'Dominance: %{y:.3f}<br>'
                    'Length: %{z}<br>'
                    '<extra></extra>'
                ),
                'marker': {
                    'size': 10,
                    'color': list(range(len(points))),
                    'colorscale': 'Viridis',
                    'opacity': 0.8
                }
            }],
            'layout': {
                'title': 'Sequence Relationships (3D Projection)',
                'scene': {
                    'xaxis': {'title': 'Diversity (entropy)'},
                    'yaxis': {'title': 'Dominance'},
                    'zaxis': {'title': 'Length'}
                },
                'margin': {'l': 0, 'r': 0, 'b': 0, 't': 40}
            },
            'config': {'responsive': True}
        }

    def build_radar_chart_data(
        self,
        sequences: List[List[int]],
        sequence_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Build data for radar chart comparing sequences.

        Args:
            sequences: List of hexagram sequences
            sequence_names: Optional names for sequences

        Returns:
            Dictionary with radar chart data for Plotly.js
        """
        if not sequences:
            return {'error': 'No sequences provided'}

        if sequence_names is None:
            sequence_names = [f"Sequence {i+1}" for i in range(len(sequences))]

        # Define hexagram categories (group into 8 octants)
        categories = [
            '1-8 (Early Heaven)',
            '9-16',
            '17-24',
            '25-32',
            '33-40',
            '41-48',
            '49-56',
            '57-64 (Late Heaven)'
        ]

        traces = []
        for seq, name in zip(sequences, sequence_names):
            valid_seq = [h for h in seq if h > 0]
            if not valid_seq:
                continue

            # Count hexagrams in each category
            counts = [0] * 8
            for h in valid_seq:
                if 1 <= h <= 8:
                    counts[0] += 1
                elif 9 <= h <= 16:
                    counts[1] += 1
                elif 17 <= h <= 24:
                    counts[2] += 1
                elif 25 <= h <= 32:
                    counts[3] += 1
                elif 33 <= h <= 40:
                    counts[4] += 1
                elif 41 <= h <= 48:
                    counts[5] += 1
                elif 49 <= h <= 56:
                    counts[6] += 1
                elif 57 <= h <= 64:
                    counts[7] += 1

            traces.append({
                'type': 'scatterpolar',
                'name': name,
                'r': counts,
                'theta': categories
            })

        return {
            'data': traces,
            'layout': {
                'title': 'Hexagram Distribution Comparison',
                'polar': {
                    'radialaxis': {'visible': True, 'range': [0, 'auto']}
                }
            },
            'config': {'responsive': True}
        }

    def _get_hexagram_names(self, hexagram_numbers: List[int]) -> Dict[int, str]:
        """
        Get hexagram names from database or cache.

        Args:
            hexagram_numbers: List of hexagram numbers

        Returns:
            Dictionary mapping hexagram numbers to names
        """
        try:
            from api.models import Hexagram

            hexagrams = Hexagram.objects.filter(number__in=hexagram_numbers)
            return {h.number: h.name_english for h in hexagrams}
        except Exception as e:
            logger.warning(f"Could not fetch hexagram names: {e}")
            return {}

    def build_sunburst_data(
        self,
        hexagram_sequence: List[int],
        sequence_name: str = "Sequence"
    ) -> Dict[str, Any]:
        """
        Build data for sunburst chart showing hexagram hierarchy.

        Args:
            hexagram_sequence: List of hexagram numbers
            sequence_name: Name for the sequence

        Returns:
            Dictionary with sunburst chart data for Plotly.js
        """
        valid_hexagrams = [h for h in hexagram_sequence if h > 0]
        if not valid_hexagrams:
            return {'error': 'No valid hexagrams in sequence'}

        counts = Counter(valid_hexagrams)
        total = len(valid_hexagrams)

        # Group hexagrams by octants (8 groups)
        labels = [sequence_name]
        parents = [""]
        values = []
        hover_text = []

        for i in range(8):
            start = i * 8 + 1
            end = (i + 1) * 8
            group_hexagrams = [h for h in valid_hexagrams if start <= h <= end]

            if group_hexagrams:
                labels.append(f"Hexagrams {start}-{end}")
                parents.append(sequence_name)
                values.append(len(group_hexagrams))

                # Add individual hexagrams as children
                for h in range(start, end + 1):
                    count = counts.get(h, 0)
                    if count > 0:
                        labels.append(str(h))
                        parents.append(f"Hexagrams {start}-{end}")
                        values.append(count)
                        hover_text.append(
                            f"Hexagram {h}<br>"
                            f"Count: {count}<br>"
                            f"Frequency: {count / total:.2%}"
                        )

        return {
            'data': [{
                'type': 'sunburst',
                'labels': labels,
                'parents': parents,
                'values': values,
                'hovertext': hover_text if hover_text else None,
                'hoverinfo': 'text' if hover_text else 'label+value+percent parent',
                'outsidetextfont': {'size': 20},
                'marker': {'line': {'width': 2}}
            }],
            'layout': {
                'title': 'Hexagram Distribution Hierarchy',
                'margin': {'l': 0, 'r': 0, 'b': 0, 't': 40}
            },
            'config': {'responsive': True}
        }

    def build_gauge_chart_data(
        self,
        metric_name: str,
        value: float,
        min_value: float = 0.0,
        max_value: float = 1.0,
        thresholds: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Build data for gauge/meter chart.

        Useful for displaying diversity scores, similarity scores, etc.

        Args:
            metric_name: Name of the metric
            value: Current value
            min_value: Minimum possible value
            max_value: Maximum possible value
            thresholds: Optional threshold markers

        Returns:
            Dictionary with gauge chart data for Plotly.js
        """
        # Default thresholds (green-yellow-red)
        if thresholds is None:
            range_size = max_value - min_value
            thresholds = [
                {'value': min_value + range_size * 0.33, 'color': '#3cb371'},
                {'value': min_value + range_size * 0.66, 'color': '#ffd700'},
                {'value': max_value, 'color': '#cd5c5c'}
            ]

        # Calculate steps
        steps = []
        prev_value = min_value
        for threshold in thresholds:
            steps.append({
                'range': [prev_value, threshold['value']],
                'color': threshold['color']
            })
            prev_value = threshold['value']

        return {
            'data': [{
                'type': 'indicator',
                'mode': 'gauge+number',
                'value': value,
                'title': {'text': metric_name},
                'gauge': {
                    'axis': {'range': [min_value, max_value]},
                    'bar': {'color': '#1f77b4'},
                    'steps': steps,
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': value
                    }
                }
            }],
            'layout': {
                'title': metric_name,
                'margin': {'l': 0, 'r': 0, 'b': 0, 't': 40}
            },
            'config': {'responsive': True}
        }
