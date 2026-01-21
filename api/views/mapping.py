"""
Views for CodonHexagramMapping API endpoints
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny
from api.models import CodonHexagramMapping
from api.serializers import CodonHexagramMappingSerializer


class CodonHexagramMappingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CodonHexagramMapping model.

    retrieve:
    Return a single mapping.

    list:
    Return all mappings (public only for anonymous users).

    create:
    Create a new mapping.
    """
    serializer_class = CodonHexagramMappingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['mapping_type', 'is_active', 'is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'coverage']
    ordering = ['-is_active', '-created_at']

    def get_queryset(self):
        """Return public mappings or user's own mappings"""
        user = self.request.user
        if user.is_authenticated:
            return CodonHexagramMapping.objects.filter(
                is_public=True
            ) | CodonHexagramMapping.objects.filter(
                created_by=user
            )
        return CodonHexagramMapping.objects.filter(is_public=True)

    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get the currently active mapping"""
        mapping = CodonHexagramMapping.objects.filter(is_active=True).first()
        if mapping:
            serializer = self.get_serializer(mapping)
            return Response(serializer.data)
        return Response({'mapping': None}, status=404)

    @action(detail=False, methods=['post'])
    def activate(self, request):
        """Activate a specific mapping (deactivates others)"""
        mapping_id = request.data.get('mapping_id')
        if not mapping_id:
            return Response({'error': 'mapping_id is required'}, status=400)

        try:
            mapping = CodonHexagramMapping.objects.get(id=mapping_id)
        except CodonHexagramMapping.DoesNotExist:
            return Response({'error': 'Mapping not found'}, status=404)

        # Check ownership
        if mapping.created_by != request.user:
            return Response({'error': 'Not authorized'}, status=403)

        # Deactivate all and activate this one
        CodonHexagramMapping.objects.filter(is_active=True).update(is_active=False)
        mapping.is_active = True
        mapping.save()

        serializer = self.get_serializer(mapping)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def induce(self, request):
        """Use AI to induce a new codon-hexagram mapping"""
        from genetic_engine.genetic_analysis_service import GeneticAnalysisService

        service = GeneticAnalysisService(user=request.user)
        result = service.induce_codon_mapping(save=True)

        return Response(result)

    @action(detail=True, methods=['get'])
    def validate(self, request, pk=None):
        """Validate a mapping scheme"""
        mapping = self.get_object()
        from genetic_engine.hexagram_mapper import HexagramMapper

        mapper = HexagramMapper()
        mapping_dict = {rule['codon']: rule['hexagram'] for rule in mapping.mapping_rules}
        validation = mapper.validate_mapping(mapping_dict)

        return Response(validation)
