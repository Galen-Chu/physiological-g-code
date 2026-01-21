"""
Views for Hexagram API endpoints
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from api.models import Hexagram
from api.serializers import HexagramSerializer


class HexagramViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Hexagram model.

    retrieve:
    Return a single hexagram.

    list:
    Return all hexagrams with filtering.
    """
    queryset = Hexagram.objects.all()
    serializer_class = HexagramSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['number', 'lower_trigram_name', 'upper_trigram_name']
    search_fields = ['name_chinese', 'name_pinyin', 'name_english', 'keywords']
    ordering_fields = ['number']
    ordering = ['number']

    @action(detail=True, methods=['get'])
    def codons(self, request, pk=None):
        """Get all codons that map to this hexagram"""
        hexagram = self.get_object()
        from api.serializers import CodonSerializer
        codons = hexagram.codons.all()
        serializer = CodonSerializer(codons, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def complementary(self, request, pk=None):
        """Get the complementary hexagram (yin/yang inversion)"""
        hexagram = self.get_object()
        if hexagram.opposite_hexagram:
            serializer = self.get_serializer(hexagram.opposite_hexagram)
            return Response(serializer.data)
        return Response({'hexagram': None}, status=404)

    @action(detail=True, methods=['get'])
    def nuclear(self, request, pk=None):
        """Get the nuclear hexagram (lines 2-5)"""
        hexagram = self.get_object()
        if hexagram.nuclear_hexagram:
            serializer = self.get_serializer(hexagram.nuclear_hexagram)
            return Response(serializer.data)
        return Response({'hexagram': None}, status=404)

    @action(detail=False, methods=['get'])
    def balanced(self, request):
        """Get all balanced hexagrams (3 yin, 3 yang)"""
        balanced = [h for h in self.queryset.all() if h.is_balanced()]
        serializer = self.get_serializer(balanced, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def all_yang(self, request):
        """Get hexagrams with all yang lines (6)"""
        all_yang = [h for h in self.queryset.all() if h.get_yang_lines() == 6]
        serializer = self.get_serializer(all_yang, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def all_yin(self, request):
        """Get hexagrams with all yin lines (6)"""
        all_yin = [h for h in self.queryset.all() if h.get_yin_lines() == 6]
        serializer = self.get_serializer(all_yin, many=True)
        return Response(serializer.data)
