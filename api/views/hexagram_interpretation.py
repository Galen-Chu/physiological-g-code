"""
Views for HexagramInterpretation API endpoints
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from api.models import HexagramInterpretation, Hexagram
from api.serializers import HexagramInterpretationSerializer


class HexagramInterpretationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for HexagramInterpretation model.

    retrieve:
    Return a single interpretation.

    list:
    Return all interpretations for the current user.

    create:
    Create a new interpretation.
    """
    serializer_class = HexagramInterpretationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hexagram', 'codon']
    search_fields = ['context', 'interpretation', 'concepts']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return interpretations for the current user"""
        return HexagramInterpretation.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new AI interpretation"""
        hexagram_number = request.data.get('hexagram_number')
        codon = request.data.get('codon')
        context = request.data.get('context', '')

        if not hexagram_number:
            return Response({'error': 'hexagram_number is required'}, status=400)

        try:
            hexagram = Hexagram.objects.get(number=hexagram_number)
        except Hexagram.DoesNotExist:
            return Response({'error': 'Hexagram not found'}, status=404)

        from genetic_engine.genetic_analysis_service import GeneticAnalysisService
        service = GeneticAnalysisService(user=request.user)

        interpretation = service.generate_hexagram_interpretation(
            hexagram_number=hexagram_number,
            codon=codon,
            context=context,
            save=True
        )

        return Response(interpretation)

    @action(detail=True, methods=['get'])
    def by_hexagram(self, request, pk=None):
        """Get all interpretations for a specific hexagram"""
        hexagram_id = pk
        interpretations = self.get_queryset().filter(hexagram_id=hexagram_id)
        serializer = self.get_serializer(interpretations, many=True)
        return Response(serializer.data)
