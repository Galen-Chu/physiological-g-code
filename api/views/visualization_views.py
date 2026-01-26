"""
Views for Visualization endpoints
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from genetic_engine.visualization_data_builder import VisualizationDataBuilder
from genetic_engine.codon_translator import CodonTranslator


class VisualizationViewSet(viewsets.ViewSet):
    """
    API endpoints for visualization data.

    Endpoints:
    - frequency: Frequency distribution chart data
    - transitions: Transition network graph data
    - heatmap: Position vs hexagram heatmap data
    - 3d_relations: 3D relationship visualization data
    - radar: Radar chart comparison data
    - sunburst: Sunburst hierarchy data
    - gauge: Gauge/meter chart data
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.builder = VisualizationDataBuilder()

    @action(detail=False, methods=['post'])
    def frequency(self, request):
        """
        Get frequency distribution chart data.

        POST /api/visualizations/frequency/
        {
            "hexagram_sequence": [1, 2, 3, ...],
            "chart_type": "bar",
            "top_n": 20
        }
        """
        hexagram_sequence = request.data.get('hexagram_sequence', [])
        chart_type = request.data.get('chart_type', 'bar')
        top_n = request.data.get('top_n', 20)

        if not hexagram_sequence:
            return Response(
                {'error': 'hexagram_sequence is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        chart_data = self.builder.build_frequency_chart_data(
            hexagram_sequence,
            chart_type=chart_type,
            top_n=top_n
        )

        return Response(chart_data)

    @action(detail=False, methods=['post'])
    def transitions(self, request):
        """
        Get transition network graph data.

        POST /api/visualizations/transitions/
        {
            "hexagram_sequence": [1, 2, 3, ...],
            "min_edge_weight": 1
        }
        """
        hexagram_sequence = request.data.get('hexagram_sequence', [])
        min_edge_weight = request.data.get('min_edge_weight', 1)

        if not hexagram_sequence:
            return Response(
                {'error': 'hexagram_sequence is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        graph_data = self.builder.build_transition_network_data(
            hexagram_sequence,
            min_edge_weight=min_edge_weight
        )

        return Response(graph_data)

    @action(detail=False, methods=['post'])
    def heatmap(self, request):
        """
        Get position vs hexagram heatmap data.

        POST /api/visualizations/heatmap/
        {
            "hexagram_sequence": [1, 2, 3, ...],
            "window_size": 10
        }
        """
        hexagram_sequence = request.data.get('hexagram_sequence', [])
        window_size = request.data.get('window_size', 10)

        if not hexagram_sequence:
            return Response(
                {'error': 'hexagram_sequence is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        heatmap_data = self.builder.build_heatmap_data(
            hexagram_sequence,
            window_size=window_size
        )

        return Response(heatmap_data)

    @action(detail=False, methods=['post'])
    def d3_relations(self, request):
        """
        Get 3D relationship visualization data.

        POST /api/visualizations/3d_relations/
        {
            "sequences": [[1, 2, 3], [4, 5, 6], ...],
            "sequence_names": ["Seq1", "Seq2"]
        }
        """
        sequences = request.data.get('sequences', [])
        sequence_names = request.data.get('sequence_names', None)

        if not sequences:
            return Response(
                {'error': 'sequences is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        plot_data = self.builder.build_3d_relations_data(
            sequences,
            sequence_names=sequence_names
        )

        return Response(plot_data)

    @action(detail=False, methods=['post'])
    def radar(self, request):
        """
        Get radar chart comparison data.

        POST /api/visualizations/radar/
        {
            "sequences": [[1, 2, 3], [4, 5, 6], ...],
            "sequence_names": ["Seq1", "Seq2"]
        }
        """
        sequences = request.data.get('sequences', [])
        sequence_names = request.data.get('sequence_names', None)

        if not sequences:
            return Response(
                {'error': 'sequences is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        radar_data = self.builder.build_radar_chart_data(
            sequences,
            sequence_names=sequence_names
        )

        return Response(radar_data)

    @action(detail=False, methods=['post'])
    def sunburst(self, request):
        """
        Get sunburst hierarchy chart data.

        POST /api/visualizations/sunburst/
        {
            "hexagram_sequence": [1, 2, 3, ...],
            "sequence_name": "My Sequence"
        }
        """
        hexagram_sequence = request.data.get('hexagram_sequence', [])
        sequence_name = request.data.get('sequence_name', 'Sequence')

        if not hexagram_sequence:
            return Response(
                {'error': 'hexagram_sequence is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sunburst_data = self.builder.build_sunburst_data(
            hexagram_sequence,
            sequence_name=sequence_name
        )

        return Response(sunburst_data)

    @action(detail=False, methods=['post'])
    def gauge(self, request):
        """
        Get gauge/meter chart data.

        POST /api/visualizations/gauge/
        {
            "metric_name": "Diversity",
            "value": 0.75,
            "min_value": 0.0,
            "max_value": 1.0
        }
        """
        metric_name = request.data.get('metric_name', 'Metric')
        value = request.data.get('value', 0.0)
        min_value = request.data.get('min_value', 0.0)
        max_value = request.data.get('max_value', 1.0)
        thresholds = request.data.get('thresholds', None)

        gauge_data = self.builder.build_gauge_chart_data(
            metric_name=metric_name,
            value=value,
            min_value=min_value,
            max_value=max_value,
            thresholds=thresholds
        )

        return Response(gauge_data)

    @action(detail=False, methods=['post'])
    def from_sequence(self, request):
        """
        Generate visualization data directly from a raw sequence.

        POST /api/visualizations/from_sequence/
        {
            "sequence": "ATGCGATAA...",
            "viz_type": "frequency",
            "mapping_scheme": "scheme_1",
            "chart_type": "bar"
        }
        """
        sequence = request.data.get('sequence', '')
        viz_type = request.data.get('viz_type', 'frequency')
        mapping_scheme = request.data.get('mapping_scheme', 'scheme_1')
        extra_params = {k: v for k, v in request.data.items()
                       if k not in ['sequence', 'viz_type', 'mapping_scheme']}

        if not sequence:
            return Response(
                {'error': 'sequence is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Translate sequence to hexagrams
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagram_sequence = translator.translate_sequence(sequence)

        # Build visualization based on type
        if viz_type == 'frequency':
            chart_type = extra_params.get('chart_type', 'bar')
            top_n = extra_params.get('top_n', 20)
            viz_data = self.builder.build_frequency_chart_data(
                hexagram_sequence,
                chart_type=chart_type,
                top_n=top_n
            )
        elif viz_type == 'transitions':
            min_edge_weight = extra_params.get('min_edge_weight', 1)
            viz_data = self.builder.build_transition_network_data(
                hexagram_sequence,
                min_edge_weight=min_edge_weight
            )
        elif viz_type == 'heatmap':
            window_size = extra_params.get('window_size', 10)
            viz_data = self.builder.build_heatmap_data(
                hexagram_sequence,
                window_size=window_size
            )
        elif viz_type == 'sunburst':
            sequence_name = extra_params.get('sequence_name', 'Sequence')
            viz_data = self.builder.build_sunburst_data(
                hexagram_sequence,
                sequence_name=sequence_name
            )
        else:
            return Response(
                {'error': f'Unknown visualization type: {viz_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add metadata
        viz_data['metadata'] = {
            'sequence_length': len(sequence),
            'codon_count': len(hexagram_sequence),
            'mapping_scheme': mapping_scheme,
            'viz_type': viz_type
        }

        return Response(viz_data)

    @action(detail=False, methods=['post'])
    def compare_sequences(self, request):
        """
        Generate comparison visualizations for multiple sequences.

        POST /api/visualizations/compare_sequences/
        {
            "sequences": ["ATGCGATAA...", "ATGCGACAA..."],
            "viz_types": ["radar", "3d"],
            "mapping_scheme": "scheme_1",
            "sequence_names": ["Seq1", "Seq2"]
        }
        """
        sequences = request.data.get('sequences', [])
        viz_types = request.data.get('viz_types', ['radar'])
        mapping_scheme = request.data.get('mapping_scheme', 'scheme_1')
        sequence_names = request.data.get('sequence_names', None)

        if not sequences:
            return Response(
                {'error': 'sequences is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if sequence_names is None:
            sequence_names = [f"Sequence {i+1}" for i in range(len(sequences))]

        if len(sequence_names) != len(sequences):
            return Response(
                {'error': 'Number of sequence_names must match number of sequences'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Translate all sequences
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagram_sequences = [
            translator.translate_sequence(seq) for seq in sequences
        ]

        # Generate visualizations
        visualizations = {}
        for viz_type in viz_types:
            if viz_type == 'radar':
                visualizations['radar'] = self.builder.build_radar_chart_data(
                    hexagram_sequences,
                    sequence_names=sequence_names
                )
            elif viz_type == '3d' or viz_type == '3d_relations':
                visualizations['3d_relations'] = self.builder.build_3d_relations_data(
                    hexagram_sequences,
                    sequence_names=sequence_names
                )

        return Response({
            'visualizations': visualizations,
            'metadata': {
                'sequence_count': len(sequences),
                'mapping_scheme': mapping_scheme,
                'sequence_names': sequence_names
            }
        })
