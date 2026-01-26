"""
Views for Comparative Analysis endpoints
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from genetic_engine.comparative_analyzer import ComparativeAnalyzer
from api.models import ComparativeAnalysis
from api.serializers import (
    ComparativeAnalysisSerializer,
    SequenceComparisonRequestSerializer,
    MappingComparisonRequestSerializer,
    StatisticalTestRequestSerializer,
    MultipleSequenceComparisonRequestSerializer,
    ConservedRegionsRequestSerializer,
)


class ComparativeAnalysisViewSet(viewsets.ViewSet):
    """
    API endpoints for comparative analysis.

    Endpoints:
    - side_by_side: Compare two sequences side-by-side
    - mapping_comparison: Compare mapping schemes
    - statistical_test: Perform statistical significance tests
    - multiple_sequences: Compare multiple sequences
    - conserved_regions: Find conserved regions
    - similarity_metrics: Calculate similarity metrics
    """

    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        """List all comparative analyses for the current user"""
        analyses = ComparativeAnalysis.objects.filter(user=request.user)
        serializer = ComparativeAnalysisSerializer(analyses, many=True)
        return Response({
            'count': analyses.count(),
            'results': serializer.data
        })

    def retrieve(self, request, pk=None):
        """Get a specific analysis by ID"""
        try:
            analysis = ComparativeAnalysis.objects.get(pk=pk)
            # Check ownership or public
            if analysis.user != request.user and not analysis.is_public:
                return Response(
                    {'error': 'You do not have permission to view this analysis'},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = ComparativeAnalysisSerializer(analysis)
            return Response(serializer.data)
        except ComparativeAnalysis.DoesNotExist:
            return Response(
                {'error': 'Analysis not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def side_by_side(self, request):
        """
        Compare two sequences side-by-side.

        POST /api/comparative/side_by_side/
        {
            "sequence1": "ATGCGATAA...",
            "sequence2": "ATGCGACAA...",
            "sequence1_name": "Seq1",
            "sequence2_name": "Seq2",
            "mapping_scheme": "scheme_1",
            "include_alignment": false
        }
        """
        serializer = SequenceComparisonRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        analyzer = ComparativeAnalyzer()

        results = analyzer.compare_sequences(
            sequence1=data['sequence1'],
            sequence2=data['sequence2'],
            mapping_scheme=data.get('mapping_scheme', 'scheme_1'),
            include_alignment=data.get('include_alignment', False)
        )

        # Add sequence names
        results['sequence1_name'] = data.get('sequence1_name', 'Sequence 1')
        results['sequence2_name'] = data.get('sequence2_name', 'Sequence 2')

        # Optionally save
        save_analysis = request.data.get('save_analysis', False)
        if save_analysis and 'error' not in results:
            analysis = ComparativeAnalysis.objects.create(
                user=request.user,
                analysis_type=ComparativeAnalysis.AnalysisType.SEQUENCE_COMPARISON,
                sequence1=data['sequence1'],
                sequence2=data['sequence2'],
                sequence1_name=data.get('sequence1_name', 'Sequence 1'),
                sequence2_name=data.get('sequence2_name', 'Sequence 2'),
                mapping_schemes=[data.get('mapping_scheme', 'scheme_1')],
                results=results,
                similarity_score=results['similarity_metrics'].get('jaccard', 0.0),
                match_percentage=results.get('match_percentage', 0.0),
                analysis_description=f"Comparison of {data.get('sequence1_name', 'Sequence 1')} and {data.get('sequence2_name', 'Sequence 2')}",
            )
            results['saved_analysis_id'] = analysis.id

        return Response(results)

    @action(detail=False, methods=['post'])
    def mapping_comparison(self, request):
        """
        Compare different mapping schemes on the same sequence.

        POST /api/comparative/mapping_comparison/
        {
            "sequence": "ATGCGATAA...",
            "schemes": ["scheme_1", "scheme_2", "scheme_3", "scheme_4"]
        }
        """
        serializer = MappingComparisonRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        analyzer = ComparativeAnalyzer()

        results = analyzer.compare_mapping_schemes(
            sequence=data['sequence'],
            schemes=data.get('schemes', ['scheme_1', 'scheme_2', 'scheme_3', 'scheme_4'])
        )

        # Optionally save
        save_analysis = request.data.get('save_analysis', False)
        if save_analysis and 'error' not in results:
            analysis = ComparativeAnalysis.objects.create(
                user=request.user,
                analysis_type=ComparativeAnalysis.AnalysisType.MAPPING_COMPARISON,
                sequence1=data['sequence'],
                mapping_schemes=data.get('schemes', ['scheme_1', 'scheme_2', 'scheme_3', 'scheme_4']),
                results=results,
                analysis_description=f"Mapping scheme comparison on {len(data['sequence'])}bp sequence",
            )
            results['saved_analysis_id'] = analysis.id

        return Response(results)

    @action(detail=False, methods=['post'])
    def statistical_test(self, request):
        """
        Perform statistical significance tests.

        POST /api/comparative/statistical_test/
        {
            "sequence1": "ATGCGATAA...",
            "sequence2": "ATGCGACAA...",
            "test_type": "chi_square",
            "mapping_scheme": "scheme_1"
        }
        """
        serializer = StatisticalTestRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        analyzer = ComparativeAnalyzer()

        results = analyzer.statistical_significance_test(
            sequence1=data['sequence1'],
            sequence2=data['sequence2'],
            test_type=data.get('test_type', 'chi_square'),
            mapping_scheme=data.get('mapping_scheme', 'scheme_1')
        )

        # Optionally save
        save_analysis = request.data.get('save_analysis', False)
        if save_analysis and 'error' not in results:
            analysis = ComparativeAnalysis.objects.create(
                user=request.user,
                analysis_type=ComparativeAnalysis.AnalysisType.STATISTICAL_TEST,
                sequence1=data['sequence1'],
                sequence2=data['sequence2'],
                mapping_schemes=[data.get('mapping_scheme', 'scheme_1')],
                results=results,
                test_type=data.get('test_type', 'chi_square'),
                p_value=results.get('p_value'),
                is_significant=results.get('is_significant'),
                analysis_description=f"{data.get('test_type', 'chi_square')} test",
            )
            results['saved_analysis_id'] = analysis.id

        return Response(results)

    @action(detail=False, methods=['post'])
    def multiple_sequences(self, request):
        """
        Compare multiple sequences at once.

        POST /api/comparative/multiple_sequences/
        {
            "sequences": ["ATGCGATAA...", "ATGCGACAA...", "ATGCGATAA..."],
            "sequence_names": ["Seq1", "Seq2", "Seq3"],
            "mapping_scheme": "scheme_1"
        }
        """
        serializer = MultipleSequenceComparisonRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        analyzer = ComparativeAnalyzer()

        results = analyzer.compare_multiple_sequences(
            sequences=data['sequences'],
            sequence_names=data.get('sequence_names'),
            mapping_scheme=data.get('mapping_scheme', 'scheme_1')
        )

        # Optionally save
        save_analysis = request.data.get('save_analysis', False)
        if save_analysis and 'error' not in results:
            analysis = ComparativeAnalysis.objects.create(
                user=request.user,
                analysis_type=ComparativeAnalysis.AnalysisType.MULTIPLE_SEQUENCE,
                sequence1=data['sequences'][0] if data['sequences'] else '',
                sequence2=data['sequences'][1] if len(data['sequences']) > 1 else '',
                additional_sequences=data['sequences'][2:] if len(data['sequences']) > 2 else None,
                mapping_schemes=[data.get('mapping_scheme', 'scheme_1')],
                results=results,
                analysis_description=f"Comparison of {len(data['sequences'])} sequences",
            )
            results['saved_analysis_id'] = analysis.id

        return Response(results)

    @action(detail=False, methods=['post'])
    def conserved_regions(self, request):
        """
        Find conserved regions across multiple sequences.

        POST /api/comparative/conserved_regions/
        {
            "sequences": ["ATGCGATAA...", "ATGCGACAA..."],
            "window_size": 5,
            "min_conservation": 0.8,
            "mapping_scheme": "scheme_1"
        }
        """
        serializer = ConservedRegionsRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        analyzer = ComparativeAnalyzer()

        results = analyzer.find_conserved_regions(
            sequences=data['sequences'],
            window_size=data.get('window_size', 5),
            min_conservation=data.get('min_conservation', 0.8),
            mapping_scheme=data.get('mapping_scheme', 'scheme_1')
        )

        # Optionally save
        save_analysis = request.data.get('save_analysis', False)
        if save_analysis and 'error' not in results:
            analysis = ComparativeAnalysis.objects.create(
                user=request.user,
                analysis_type=ComparativeAnalysis.AnalysisType.CONSERVED_REGIONS,
                sequence1=data['sequences'][0] if data['sequences'] else '',
                additional_sequences=data['sequences'][1:] if len(data['sequences']) > 1 else None,
                mapping_schemes=[data.get('mapping_scheme', 'scheme_1')],
                results=results,
                window_size=data.get('window_size', 5),
                min_conservation=data.get('min_conservation', 0.8),
                analysis_description=f"Conserved regions in {len(data['sequences'])} sequences",
            )
            results['saved_analysis_id'] = analysis.id

        return Response(results)

    @action(detail=False, methods=['post'])
    def similarity_metrics(self, request):
        """
        Calculate detailed similarity metrics between two sequences.

        POST /api/comparative/similarity_metrics/
        {
            "sequence1": "ATGCGATAA...",
            "sequence2": "ATGCGACAA...",
            "mapping_scheme": "scheme_1"
        }
        """
        sequence1 = request.data.get('sequence1', '')
        sequence2 = request.data.get('sequence2', '')
        mapping_scheme = request.data.get('mapping_scheme', 'scheme_1')

        if not sequence1 or not sequence2:
            return Response(
                {'error': 'Both sequence1 and sequence2 are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        analyzer = ComparativeAnalyzer()
        results = analyzer.calculate_similarity_metrics(
            sequence1=sequence1,
            sequence2=sequence2,
            mapping_scheme=mapping_scheme
        )

        results['sequence1_length'] = len(sequence1)
        results['sequence2_length'] = len(sequence2)
        results['mapping_scheme'] = mapping_scheme

        return Response(results)
