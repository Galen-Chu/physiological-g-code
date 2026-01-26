"""
Views for Pattern Analysis endpoints
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from genetic_engine.codon_translator import CodonTranslator
from genetic_engine.pattern_analyzer import PatternAnalyzer
from genetic_engine.hexagram_mapper import HexagramMapper
from api.models import AnalysisPattern
from api.serializers import (
    AnalysisPatternSerializer,
    PatternMatchSerializer,
    PositionAnalysisRequestSerializer,
    SlidingWindowRequestSerializer,
    MotifDiscoveryRequestSerializer,
    ConservationAnalysisRequestSerializer,
)


class PatternAnalysisViewSet(viewsets.ViewSet):
    """
    API endpoints for advanced pattern detection and analysis.

    Endpoints:
    - position_analysis: Analyze position-specific hexagram distribution
    - sliding_window: Sliding window pattern detection
    - motif_discovery: Discover recurring motifs
    - conservation: Analyze conservation across sequences
    - entropy: Calculate position entropy
    - runs: Detect hexagram runs
    - correlation: Calculate autocorrelation
    """

    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        """List all saved patterns for the current user"""
        patterns = AnalysisPattern.objects.filter(user=request.user)
        serializer = AnalysisPatternSerializer(patterns, many=True)
        return Response({
            'count': patterns.count(),
            'results': serializer.data
        })

    def retrieve(self, request, pk=None):
        """Get a specific pattern by ID"""
        try:
            pattern = AnalysisPattern.objects.get(pk=pk)
            # Check ownership or public
            if pattern.user != request.user and not pattern.is_public:
                return Response(
                    {'error': 'You do not have permission to view this pattern'},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = AnalysisPatternSerializer(pattern)
            return Response(serializer.data)
        except AnalysisPattern.DoesNotExist:
            return Response(
                {'error': 'Pattern not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def position_analysis(self, request):
        """
        Analyze position-specific hexagram distribution.

        POST /api/patterns/position_analysis/
        {
            "sequence": "ATGCGATAA...",
            "mapping_scheme": "scheme_1"
        }
        """
        serializer = PositionAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        sequence = data['sequence'].upper().replace(' ', '')
        mapping_scheme = data.get('mapping_scheme', 'scheme_1')

        # Translate sequence to hexagrams
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagram_sequence = translator.translate_sequence(sequence)

        # Perform position analysis
        analyzer = PatternAnalyzer()
        results = analyzer.analyze_position_patterns(hexagram_sequence)

        # Add metadata
        results['sequence_length'] = len(sequence)
        results['codon_count'] = len(hexagram_sequence)
        results['mapping_scheme'] = mapping_scheme

        # Optionally save as pattern
        save_pattern = request.data.get('save_pattern', False)
        if save_pattern:
            pattern = AnalysisPattern.objects.create(
                user=request.user,
                pattern_type=AnalysisPattern.PatternType.POSITION_SPECIFIC,
                sequence=sequence,
                hexagram_sequence=hexagram_sequence,
                pattern_data=results,
                frequency=1,
                significance_score=results.get('average_bias', 0.0) / 10.0,  # Normalize
                mapping_scheme=mapping_scheme,
                pattern_description=f"Position analysis of {len(sequence)}bp sequence",
            )
            results['saved_pattern_id'] = pattern.id

        return Response(results)

    @action(detail=False, methods=['post'])
    def sliding_window(self, request):
        """
        Analyze sequence using sliding window approach.

        POST /api/patterns/sliding_window/
        {
            "sequence": "ATGCGATAA...",
            "window_size": 3,
            "step_size": 1,
            "mapping_scheme": "scheme_1"
        }
        """
        serializer = SlidingWindowRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        sequence = data['sequence'].upper().replace(' ', '')
        window_size = data.get('window_size', 3)
        step_size = data.get('step_size', 1)
        mapping_scheme = data.get('mapping_scheme', 'scheme_1')

        # Translate sequence to hexagrams
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagram_sequence = translator.translate_sequence(sequence)

        # Perform sliding window analysis
        analyzer = PatternAnalyzer()
        results = analyzer.sliding_window_analysis(
            hexagram_sequence,
            window_size=window_size,
            step_size=step_size
        )

        # Add metadata
        if 'error' not in results:
            results['sequence_length'] = len(sequence)
            results['codon_count'] = len(hexagram_sequence)
            results['mapping_scheme'] = mapping_scheme

            # Optionally save
            save_pattern = request.data.get('save_pattern', False)
            if save_pattern:
                pattern = AnalysisPattern.objects.create(
                    user=request.user,
                    pattern_type=AnalysisPattern.PatternType.SLIDING_WINDOW,
                    sequence=sequence,
                    hexagram_sequence=hexagram_sequence,
                    pattern_data=results,
                    frequency=results.get('unique_patterns', 0),
                    significance_score=min(results.get('pattern_entropy', 0.0) / 5.0, 1.0),
                    window_size=window_size,
                    mapping_scheme=mapping_scheme,
                    pattern_description=f"Sliding window analysis (size={window_size})",
                )
                results['saved_pattern_id'] = pattern.id

        return Response(results)

    @action(detail=False, methods=['post'])
    def motif_discovery(self, request):
        """
        Discover recurring motifs in the sequence.

        POST /api/patterns/motif_discovery/
        {
            "sequence": "ATGCGATAA...",
            "motif_lengths": [2, 3, 4, 5],
            "min_occurrences": 3,
            "max_motifs": 20,
            "mapping_scheme": "scheme_1"
        }
        """
        serializer = MotifDiscoveryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        sequence = data['sequence'].upper().replace(' ', '')
        motif_lengths = data.get('motif_lengths', [2, 3, 4, 5])
        min_occurrences = data.get('min_occurrences', 3)
        max_motifs = data.get('max_motifs', 20)
        mapping_scheme = data.get('mapping_scheme', 'scheme_1')

        # Translate sequence to hexagrams
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagram_sequence = translator.translate_sequence(sequence)

        # Perform motif discovery
        analyzer = PatternAnalyzer()
        results = analyzer.discover_motifs(
            hexagram_sequence,
            motif_lengths=motif_lengths,
            min_occurrences=min_occurrences,
            max_motifs=max_motifs
        )

        # Add metadata
        if 'error' not in results:
            results['sequence_length'] = len(sequence)
            results['codon_count'] = len(hexagram_sequence)
            results['mapping_scheme'] = mapping_scheme

            # Optionally save
            save_pattern = request.data.get('save_pattern', False)
            if save_pattern and results.get('motifs_found', 0) > 0:
                pattern = AnalysisPattern.objects.create(
                    user=request.user,
                    pattern_type=AnalysisPattern.PatternType.MOTIF,
                    sequence=sequence,
                    hexagram_sequence=hexagram_sequence,
                    pattern_data=results,
                    frequency=results.get('motifs_found', 0),
                    significance_score=min(results.get('motif_coverage_ratio', 0.0), 1.0),
                    min_occurrences=min_occurrences,
                    mapping_scheme=mapping_scheme,
                    pattern_description=f"Motif discovery: {results['motifs_found']} motifs found",
                )
                results['saved_pattern_id'] = pattern.id

        return Response(results)

    @action(detail=False, methods=['post'])
    def conservation(self, request):
        """
        Analyze conservation across multiple sequences.

        POST /api/patterns/conservation/
        {
            "sequences": ["ATGCGATAA...", "ATGCGACAA..."],
            "sequence_names": ["Seq1", "Seq2"],
            "mapping_scheme": "scheme_1"
        }
        """
        serializer = ConservationAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        sequences = [seq.upper().replace(' ', '') for seq in data['sequences']]
        sequence_names = data.get('sequence_names', [f"Sequence_{i+1}" for i in range(len(sequences))])
        mapping_scheme = data.get('mapping_scheme', 'scheme_1')

        # Translate all sequences to hexagrams
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagram_sequences = [
            translator.translate_sequence(seq) for seq in sequences
        ]

        # Perform conservation analysis
        analyzer = PatternAnalyzer()
        results = analyzer.analyze_conservation(hexagram_sequences, sequence_names)

        results['mapping_scheme'] = mapping_scheme

        # Optionally save
        save_pattern = request.data.get('save_pattern', False)
        if save_pattern and 'error' not in results:
            pattern = AnalysisPattern.objects.create(
                user=request.user,
                pattern_type=AnalysisPattern.PatternType.CONSERVATION,
                sequence=';'.join(sequences),
                hexagram_sequence=hexagram_sequences,
                pattern_data=results,
                frequency=len(sequences),
                significance_score=results.get('average_conservation', 0.0),
                related_sequences=sequences,
                mapping_scheme=mapping_scheme,
                pattern_description=f"Conservation analysis of {len(sequences)} sequences",
            )
            results['saved_pattern_id'] = pattern.id

        return Response(results)

    @action(detail=False, methods=['post'])
    def entropy(self, request):
        """
        Calculate position entropy for the sequence.

        POST /api/patterns/entropy/
        {
            "sequence": "ATGCGATAA...",
            "window_size": 10,
            "mapping_scheme": "scheme_1"
        }
        """
        sequence = request.data.get('sequence', '').upper().replace(' ', '')
        window_size = request.data.get('window_size', 10)
        mapping_scheme = request.data.get('mapping_scheme', 'scheme_1')

        if not sequence:
            return Response({'error': 'Sequence is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Translate sequence to hexagrams
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagram_sequence = translator.translate_sequence(sequence)

        # Calculate entropy
        analyzer = PatternAnalyzer()
        results = analyzer.calculate_position_entropy(hexagram_sequence, window_size)

        results['sequence_length'] = len(sequence)
        results['codon_count'] = len(hexagram_sequence)
        results['mapping_scheme'] = mapping_scheme

        # Optionally save
        save_pattern = request.data.get('save_pattern', False)
        if save_pattern and 'error' not in results:
            pattern = AnalysisPattern.objects.create(
                user=request.user,
                pattern_type=AnalysisPattern.PatternType.CUSTOM,
                sequence=sequence,
                hexagram_sequence=hexagram_sequence,
                pattern_data=results,
                frequency=1,
                significance_score=results.get('complexity_score', 0.0),
                window_size=window_size,
                mapping_scheme=mapping_scheme,
                pattern_description=f"Entropy analysis (complexity: {results.get('complexity_score', 0):.2f})",
            )
            results['saved_pattern_id'] = pattern.id

        return Response(results)

    @action(detail=False, methods=['post'])
    def runs(self, request):
        """
        Detect runs of the same hexagram.

        POST /api/patterns/runs/
        {
            "sequence": "ATGCGATAA...",
            "min_run_length": 3,
            "mapping_scheme": "scheme_1"
        }
        """
        sequence = request.data.get('sequence', '').upper().replace(' ', '')
        min_run_length = request.data.get('min_run_length', 3)
        mapping_scheme = request.data.get('mapping_scheme', 'scheme_1')

        if not sequence:
            return Response({'error': 'Sequence is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Translate sequence to hexagrams
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagram_sequence = translator.translate_sequence(sequence)

        # Detect runs
        analyzer = PatternAnalyzer()
        results = analyzer.detect_hexagram_run(hexagram_sequence, min_run_length)

        results['sequence_length'] = len(sequence)
        results['codon_count'] = len(hexagram_sequence)
        results['mapping_scheme'] = mapping_scheme

        # Optionally save
        save_pattern = request.data.get('save_pattern', False)
        if save_pattern and 'error' not in results and results.get('total_runs', 0) > 0:
            pattern = AnalysisPattern.objects.create(
                user=request.user,
                pattern_type=AnalysisPattern.PatternType.RUN,
                sequence=sequence,
                hexagram_sequence=hexagram_sequence,
                pattern_data=results,
                frequency=results.get('total_runs', 0),
                significance_score=min(results.get('total_runs', 0) / 10.0, 1.0),
                pattern_description=f"Run detection: {results['total_runs']} runs found",
            )
            results['saved_pattern_id'] = pattern.id

        return Response(results)

    @action(detail=False, methods=['post'])
    def correlation(self, request):
        """
        Calculate autocorrelation of hexagram sequence.

        POST /api/patterns/correlation/
        {
            "sequence": "ATGCGATAA...",
            "lag": 1,
            "mapping_scheme": "scheme_1"
        }
        """
        sequence = request.data.get('sequence', '').upper().replace(' ', '')
        lag = request.data.get('lag', 1)
        mapping_scheme = request.data.get('mapping_scheme', 'scheme_1')

        if not sequence:
            return Response({'error': 'Sequence is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Translate sequence to hexagrams
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagram_sequence = translator.translate_sequence(sequence)

        # Calculate correlation
        analyzer = PatternAnalyzer()
        results = analyzer.calculate_hexagram_correlation(hexagram_sequence, lag)

        results['sequence_length'] = len(sequence)
        results['codon_count'] = len(hexagram_sequence)
        results['mapping_scheme'] = mapping_scheme

        # Optionally save
        save_pattern = request.data.get('save_pattern', False)
        if save_pattern and 'error' not in results:
            pattern = AnalysisPattern.objects.create(
                user=request.user,
                pattern_type=AnalysisPattern.PatternType.CORRELATION,
                sequence=sequence,
                hexagram_sequence=hexagram_sequence,
                pattern_data=results,
                frequency=1,
                significance_score=abs(results.get('correlation', 0.0)),
                pattern_description=f"Correlation analysis (lag={lag}): {results.get('interpretation', '')}",
            )
            results['saved_pattern_id'] = pattern.id

        return Response(results)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def verify(self, request, pk=None):
        """
        Mark a pattern as verified.

        POST /api/patterns/{id}/verify/
        """
        try:
            pattern = AnalysisPattern.objects.get(pk=pk)
            if pattern.user != request.user:
                return Response(
                    {'error': 'You can only verify your own patterns'},
                    status=status.HTTP_403_FORBIDDEN
                )

            pattern.is_verified = True
            pattern.save()

            serializer = AnalysisPatternSerializer(pattern)
            return Response(serializer.data)
        except AnalysisPattern.DoesNotExist:
            return Response(
                {'error': 'Pattern not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_public(self, request, pk=None):
        """
        Toggle the public visibility of a pattern.

        POST /api/patterns/{id}/toggle_public/
        """
        try:
            pattern = AnalysisPattern.objects.get(pk=pk)
            if pattern.user != request.user:
                return Response(
                    {'error': 'You can only modify your own patterns'},
                    status=status.HTTP_403_FORBIDDEN
                )

            pattern.is_public = not pattern.is_public
            pattern.save()

            serializer = AnalysisPatternSerializer(pattern)
            return Response(serializer.data)
        except AnalysisPattern.DoesNotExist:
            return Response(
                {'error': 'Pattern not found'},
                status=status.HTTP_404_NOT_FOUND
            )
