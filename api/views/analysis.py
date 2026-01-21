"""
Views for genetic analysis endpoints
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from genetic_engine.genetic_analysis_service import GeneticAnalysisService


class AnalysisViewSet(viewsets.ViewSet):
    """
    API endpoints for genetic-hexagram analysis.

    analyze_codon: Analyze a single codon
    analyze_sequence: Analyze a DNA/RNA sequence
    get_hexagram_for_codon: Get hexagram for a codon
    """

    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['analyze_codon', 'get_hexagram_for_codon']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def analyze_codon(self, request):
        """
        Analyze a single codon and return its hexagram.

        POST /api/analysis/analyze_codon/
        {
            "codon": "ATG",
            "mapping_scheme": "scheme_1"
        }
        """
        codon = request.data.get('codon', '').upper()
        mapping_scheme = request.data.get('mapping_scheme', 'scheme_1')

        if not codon or len(codon) != 3:
            return Response(
                {'error': 'Valid 3-nucleotide codon required'},
                status=400
            )

        service = GeneticAnalysisService()
        hexagram_number = service.get_hexagram_for_codon(codon, mapping_scheme)

        if hexagram_number is None:
            return Response(
                {'error': 'Could not map codon to hexagram'},
                status=500
            )

        # Get hexagram details
        from api.models import Hexagram
        from api.serializers import HexagramSerializer

        try:
            hexagram = Hexagram.objects.get(number=hexagram_number)
            serializer = HexagramSerializer(hexagram)
            return Response({
                'codon': codon,
                'hexagram': serializer.data,
                'mapping_scheme': mapping_scheme
            })
        except Hexagram.DoesNotExist:
            return Response(
                {'error': f'Hexagram {hexagram_number} not found in database'},
                status=404
            )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def analyze_sequence(self, request):
        """
        Analyze a complete DNA/RNA sequence.

        POST /api/analysis/analyze_sequence/
        {
            "sequence": "ATGCGATAA...",
            "name": "My Sequence",
            "sequence_type": "DNA",
            "mapping_scheme": "scheme_1"
        }
        """
        sequence = request.data.get('sequence', '')
        name = request.data.get('name', 'Untitled')
        sequence_type = request.data.get('sequence_type', 'DNA')
        mapping_scheme = request.data.get('mapping_scheme', 'scheme_1')

        if not sequence:
            return Response({'error': 'Sequence is required'}, status=400)

        service = GeneticAnalysisService(user=request.user)
        results = service.analyze_sequence(
            sequence=sequence,
            sequence_name=name,
            sequence_type=sequence_type,
            mapping_scheme=mapping_scheme,
            save=True
        )

        return Response(results)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def translate_codons(self, request):
        """
        Translate multiple codons to hexagrams.

        POST /api/analysis/translate_codons/
        {
            "codons": ["ATG", "CGA", "TAA"],
            "mapping_scheme": "scheme_1"
        }
        """
        codons = request.data.get('codons', [])
        mapping_scheme = request.data.get('mapping_scheme', 'scheme_1')

        if not codons:
            return Response({'error': 'Codons list is required'}, status=400)

        from genetic_engine.hexagram_mapper import HexagramMapper
        mapper = HexagramMapper()

        results = mapper.batch_map_codons(codons, scheme=mapping_scheme)

        return Response({
            'codons': codons,
            'hexagrams': results,
            'mapping_scheme': mapping_scheme
        })

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def mapping_schemes(self, request):
        """
        Get available mapping schemes.

        GET /api/analysis/mapping_schemes/
        """
        schemes = {
            'scheme_1': {
                'name': 'Purine/Pyrimidine',
                'description': 'A/T=0, G/C=1 (based on chemical structure)',
            },
            'scheme_2': {
                'name': 'AT/GC Alternation',
                'description': 'A=0, T=1, G=0, C=1',
            },
            'scheme_3': {
                'name': 'Hydrogen Bond Count',
                'description': 'A/T=0 (2 bonds), G/C=1 (3 bonds)',
            },
            'scheme_4': {
                'name': 'Molecular Weight',
                'description': 'Based on molecular weight differences',
            },
        }
        return Response(schemes)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint with documentation links"""
    return Response({
        'physiological_g_code_api': 'Physiological G-Code API',
        'version': '1.0.0',
        'endpoints': {
            'codons': '/api/codons/',
            'hexagrams': '/api/hexagrams/',
            'sequences': '/api/sequences/',
            'interpretations': '/api/interpretations/',
            'mappings': '/api/mappings/',
            'analysis': '/api/analysis/',
            'schema': '/api/schema/',
        },
        'documentation': {
            'swagger': '/api/swagger/',
            'redoc': '/api/redoc/',
        }
    })
