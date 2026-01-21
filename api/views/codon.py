"""
Views for Codon API endpoints
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from api.models import Codon
from api.serializers import CodonSerializer


class CodonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Codon model.

    retrieve:
    Return a single codon.

    list:
    Return all codons with filtering.
    """
    queryset = Codon.objects.all()
    serializer_class = CodonSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['codon_type', 'is_start', 'is_stop', 'amino_acid_code']
    search_fields = ['sequence', 'amino_acid', 'amino_acid_full_name']
    ordering_fields = ['sequence', 'amino_acid']
    ordering = ['sequence']

    @action(detail=True, methods=['get'])
    def hexagram(self, request, pk=None):
        """Get the hexagram associated with this codon"""
        codon = self.get_object()
        if codon.mapped_hexagram:
            from api.serializers import HexagramSerializer
            serializer = HexagramSerializer(codon.mapped_hexagram)
            return Response(serializer.data)
        return Response({'hexagram': None}, status=404)

    @action(detail=False, methods=['get'])
    def start_codons(self, request):
        """Get all start codons"""
        start_codons = self.queryset.filter(is_start=True)
        serializer = self.get_serializer(start_codons, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stop_codons(self, request):
        """Get all stop codons"""
        stop_codons = self.queryset.filter(is_stop=True)
        serializer = self.get_serializer(stop_codons, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_amino_acid(self, request):
        """Get codons that code for a specific amino acid"""
        amino_acid = request.query_params.get('code')
        if not amino_acid:
            return Response({'error': 'Amino acid code required'}, status=400)

        codons = self.queryset.filter(amino_acid_code=amino_acid.upper())
        serializer = self.get_serializer(codons, many=True)
        return Response(serializer.data)
