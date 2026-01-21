"""
Views for CodonSequence API endpoints
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from api.models import CodonSequence
from api.serializers import CodonSequenceSerializer


class CodonSequenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CodonSequence model.

    retrieve:
    Return a single sequence.

    list:
    Return all sequences for the current user.

    create:
    Create a new sequence.
    """
    serializer_class = CodonSequenceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sequence_type', 'organism', 'gene_name', 'is_reference']
    search_fields = ['name', 'description', 'gene_name', 'organism']
    ordering_fields = ['name', 'created_at', 'codon_count']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return sequences for the current user"""
        return CodonSequence.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Analyze a genetic sequence"""
        sequence = request.data.get('sequence')
        name = request.data.get('name', 'Untitled Sequence')
        sequence_type = request.data.get('sequence_type', 'DNA')
        mapping_scheme = request.data.get('mapping_scheme', 'scheme_1')

        if not sequence:
            return Response({'error': 'Sequence is required'}, status=400)

        from genetic_engine.genetic_analysis_service import GeneticAnalysisService
        service = GeneticAnalysisService(user=request.user)

        results = service.analyze_sequence(
            sequence=sequence,
            sequence_name=name,
            sequence_type=sequence_type,
            mapping_scheme=mapping_scheme,
            save=True
        )

        return Response(results)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get detailed statistics for a sequence"""
        sequence = self.get_object()

        from genetic_engine.genetic_analysis_service import GeneticAnalysisService
        service = GeneticAnalysisService(user=request.user)

        stats = service.get_sequence_statistics(sequence.id)
        return Response(stats)

    @action(detail=False, methods=['get'])
    def reference_sequences(self, request):
        """Get all reference sequences"""
        references = CodonSequence.objects.filter(is_reference=True)
        serializer = self.get_serializer(references, many=True)
        return Response(serializer.data)
