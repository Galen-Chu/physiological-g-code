"""
Views for Export endpoints
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from genetic_engine.export_service import ExportService
from genetic_engine.codon_translator import CodonTranslator


class ExportViewSet(viewsets.ViewSet):
    """
    API endpoints for exporting analysis results.

    Endpoints:
    - csv: Export to CSV format
    - json: Export to JSON format
    - fasta: Export to FASTA format
    - pdf_data: Get PDF-ready data
    - image_data: Get image/chart data
    - batch: Export to multiple formats
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.export_service = ExportService()

    @action(detail=False, methods=['post'])
    def csv(self, request):
        """
        Export analysis results to CSV format.

        POST /api/export/csv/
        {
            "data": {...},  // Analysis results
            "include_metadata": true
        }
        """
        data = request.data.get('data', {})
        include_metadata = request.data.get('include_metadata', True)

        if not data:
            return Response(
                {'error': 'No data provided for export'},
                status=status.HTTP_400_BAD_REQUEST
            )

        csv_content = self.export_service.export_to_csv(
            data,
            include_metadata=include_metadata
        )

        filename = self.export_service.generate_export_filename(
            analysis_type=data.get('analysis_type', 'analysis'),
            format_type='csv',
            sequence_identifier=data.get('sequence_name')
        )

        return Response({
            'content': csv_content,
            'filename': filename,
            'format': 'csv',
            'content_type': 'text/csv'
        })

    @action(detail=False, methods=['post'])
    def json(self, request):
        """
        Export analysis results to JSON format.

        POST /api/export/json/
        {
            "data": {...},
            "pretty": true,
            "include_metadata": true
        }
        """
        data = request.data.get('data', {})
        pretty = request.data.get('pretty', True)
        include_metadata = request.data.get('include_metadata', True)

        if not data:
            return Response(
                {'error': 'No data provided for export'},
                status=status.HTTP_400_BAD_REQUEST
            )

        json_content = self.export_service.export_to_json(
            data,
            pretty=pretty,
            include_metadata=include_metadata
        )

        filename = self.export_service.generate_export_filename(
            analysis_type=data.get('analysis_type', 'analysis'),
            format_type='json',
            sequence_identifier=data.get('sequence_name')
        )

        return Response({
            'content': json_content,
            'filename': filename,
            'format': 'json',
            'content_type': 'application/json'
        })

    @action(detail=False, methods=['post'])
    def fasta(self, request):
        """
        Export sequence to FASTA format with hexagram annotations.

        POST /api/export/fasta/
        {
            "sequence": "ATGCGATAA...",
            "hexagram_sequence": [1, 2, 3, ...],
            "sequence_name": "My Sequence"
        }
        """
        sequence = request.data.get('sequence', '')
        hexagram_sequence = request.data.get('hexagram_sequence', [])
        sequence_name = request.data.get('sequence_name', 'sequence')

        if not sequence:
            return Response(
                {'error': 'Sequence is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        fasta_content = self.export_service.export_to_fasta(
            sequence=sequence,
            hexagram_sequence=hexagram_sequence,
            sequence_name=sequence_name,
            include_hexagram_annotations=True
        )

        filename = self.export_service.generate_export_filename(
            analysis_type='sequence',
            format_type='fasta',
            sequence_identifier=sequence_name
        )

        return Response({
            'content': fasta_content,
            'filename': filename,
            'format': 'fasta',
            'content_type': 'text/plain'
        })

    @action(detail=False, methods=['post'])
    def pdf_data(self, request):
        """
        Get PDF-ready data structure.

        POST /api/export/pdf_data/
        {
            "data": {...},
            "title": "Analysis Report"
        }
        """
        data = request.data.get('data', {})
        title = request.data.get('title', 'Genetic-Hexagram Analysis Report')

        if not data:
            return Response(
                {'error': 'No data provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pdf_data = self.export_service.export_to_pdf(data, title)

        filename = self.export_service.generate_export_filename(
            analysis_type=data.get('analysis_type', 'report'),
            format_type='pdf',
            sequence_identifier=data.get('sequence_name')
        )

        return Response({
            'data': pdf_data,
            'filename': filename,
            'format': 'pdf'
        })

    @action(detail=False, methods=['post'])
    def image_data(self, request):
        """
        Get image/chart data for visualization.

        POST /api/export/image_data/
        {
            "data": {...},
            "chart_type": "bar",
            "width": 800,
            "height": 600
        }
        """
        data = request.data.get('data', {})
        chart_type = request.data.get('chart_type', 'bar')
        width = request.data.get('width', 800)
        height = request.data.get('height', 600)

        if not data:
            return Response(
                {'error': 'No data provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        chart_data = self.export_service.export_to_image_data(
            data,
            chart_type=chart_type,
            width=width,
            height=height
        )

        return Response(chart_data)

    @action(detail=False, methods=['post'])
    def batch(self, request):
        """
        Export to multiple formats at once.

        POST /api/export/batch/
        {
            "data": {...},
            "formats": ["csv", "json", "fasta"],
            "base_filename": "my_analysis"
        }
        """
        data = request.data.get('data', {})
        formats = request.data.get('formats', ['csv', 'json'])
        base_filename = request.data.get('base_filename', 'analysis')

        if not data:
            return Response(
                {'error': 'No data provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        exports = self.export_service.batch_export(data, formats, base_filename)

        return Response({
            'exports': exports,
            'count': len(exports)
        })

    @action(detail=False, methods=['post'])
    def from_sequence(self, request):
        """
        Export a raw sequence to various formats.

        POST /api/export/from_sequence/
        {
            "sequence": "ATGCGATAA...",
            "formats": ["csv", "json", "fasta"],
            "sequence_name": "My Sequence",
            "mapping_scheme": "scheme_1"
        }
        """
        sequence = request.data.get('sequence', '')
        formats = request.data.get('formats', ['csv', 'json', 'fasta'])
        sequence_name = request.data.get('sequence_name', 'sequence')
        mapping_scheme = request.data.get('mapping_scheme', 'scheme_1')

        if not sequence:
            return Response(
                {'error': 'Sequence is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Translate sequence to hexagrams
        translator = CodonTranslator(mapping_scheme=mapping_scheme)
        hexagram_sequence = translator.translate_sequence(sequence)

        # Build data structure
        data = {
            'analysis_type': 'sequence_analysis',
            'sequence': sequence,
            'sequence_name': sequence_name,
            'sequence_length': len(sequence),
            'mapping_scheme': mapping_scheme,
            'hexagram_sequence': hexagram_sequence,
            'codon_count': len(hexagram_sequence)
        }

        # Add frequency data
        from collections import Counter
        valid_hexagrams = [h for h in hexagram_sequence if h > 0]
        if valid_hexagrams:
            data['hexagram_frequency'] = dict(Counter(valid_hexagrams))

        # Export to requested formats
        base_filename = self.export_service.generate_export_filename(
            analysis_type='sequence',
            format_type='',
            sequence_identifier=sequence_name
        ).rstrip('.')

        exports = self.export_service.batch_export(data, formats, base_filename)

        return Response({
            'exports': exports,
            'count': len(exports),
            'data': data
        })
