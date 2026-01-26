"""
Export Service - Export analysis results to various formats
"""
import logging
import io
import csv
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ExportService:
    """
    Service for exporting genetic-hexagram analysis results to various formats.

    Supported formats:
    - CSV: Spreadsheet-compatible format
    - PDF: Professional report with charts
    - Image (PNG/SVG): Visual export
    - FASTA: Biological format with hexagram annotations
    - JSON: Structured data export
    """

    def __init__(self):
        """Initialize the ExportService."""
        logger.info("ExportService initialized")

    def export_to_csv(
        self,
        data: Dict[str, Any],
        columns: Optional[List[str]] = None,
        include_metadata: bool = True
    ) -> str:
        """
        Export analysis results to CSV format.

        Args:
            data: Analysis results dictionary
            columns: Specific columns to include (default: all)
            include_metadata: Whether to include metadata rows

        Returns:
            CSV-formatted string
        """
        output = io.StringIO()

        if include_metadata:
            # Write metadata
            writer = csv.writer(output)
            writer.writerow(['# Metadata'])
            writer.writerow(['# Export Date', datetime.now().isoformat()])
            writer.writerow(['# Analysis Type', data.get('analysis_type', 'Unknown')])

            if 'sequence_length' in data:
                writer.writerow(['# Sequence Length', data['sequence_length']])
            if 'codon_count' in data:
                writer.writerow(['# Codon Count', data['codon_count']])
            if 'mapping_scheme' in data:
                writer.writerow(['# Mapping Scheme', data['mapping_scheme']])

            writer.writerow([])  # Empty row separator

        # Write data section
        writer = csv.writer(output)

        # Handle different data structures
        if 'hexagram_sequence' in data:
            # Hexagram sequence export
            hexagrams = data['hexagram_sequence']
            writer.writerow(['Position', 'Codon', 'Hexagram', 'Amino Acid'])

            for i, hexagram in enumerate(hexagrams):
                writer.writerow([
                    i + 1,
                    data.get('codons', [])[i] if 'codons' in data and i < len(data.get('codons', [])) else 'N/A',
                    hexagram if hexagram > 0 else 'Invalid',
                    data.get('amino_acids', [])[i] if 'amino_acids' in data and i < len(data.get('amino_acids', [])) else 'N/A'
                ])

        elif 'position_distribution' in data:
            # Position analysis export
            writer.writerow(['Position', 'Hexagram', 'Frequency', 'Bias'])

            for pos, pos_data in data['position_distribution'].items():
                dominant_hex, freq = pos_data.get('dominant_at_position', (0, 0))
                writer.writerow([
                    pos,
                    dominant_hex,
                    f"{freq:.2%}",
                    data.get('positional_bias', {}).get(pos, 0)
                ])

        elif 'motifs' in data:
            # Motif discovery export
            writer.writerow(['Motif', 'Length', 'Occurrences', 'Frequency', 'Positions'])

            for motif in data['motifs']:
                writer.writerow([
                    '-'.join(map(str, motif['motif'])),
                    motif['length'],
                    motif['occurrences'],
                    f"{motif['frequency']:.4f}",
                    ', '.join(map(str, motif['positions']))
                ])

        elif 'side_by_side' in data:
            # Side-by-side comparison export
            writer.writerow(['Position', data.get('sequence1_name', 'Sequence 1'),
                           data.get('sequence2_name', 'Sequence 2'), 'Match'])

            for item in data['side_by_side']:
                writer.writerow([
                    item['position'],
                    item['sequence1_hexagram'],
                    item['sequence2_hexagram'],
                    'Yes' if item['match'] else 'No'
                ])

        elif 'hexagram_frequency' in data:
            # Hexagram frequency export
            writer.writerow(['Hexagram', 'Count', 'Frequency'])

            for hexagram, count in data['hexagram_frequency'].items():
                total = sum(data['hexagram_frequency'].values())
                freq = count / total if total > 0 else 0
                writer.writerow([hexagram, count, f"{freq:.4f}"])

        else:
            # Generic key-value export
            writer.writerow(['Key', 'Value'])
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                writer.writerow([key, value])

        return output.getvalue()

    def export_to_json(
        self,
        data: Dict[str, Any],
        pretty: bool = True,
        include_metadata: bool = True
    ) -> str:
        """
        Export analysis results to JSON format.

        Args:
            data: Analysis results dictionary
            pretty: Whether to format with indentation
            include_metadata: Whether to include export metadata

        Returns:
            JSON-formatted string
        """
        export_data = dict(data)

        if include_metadata:
            export_data['_export_metadata'] = {
                'export_date': datetime.now().isoformat(),
                'format': 'json',
                'version': '1.0'
            }

        if pretty:
            return json.dumps(export_data, indent=2, default=str)
        else:
            return json.dumps(export_data, default=str)

    def export_to_fasta(
        self,
        sequence: str,
        hexagram_sequence: List[int],
        sequence_name: str = "sequence",
        include_hexagram_annotations: bool = True
    ) -> str:
        """
        Export sequence in FASTA format with hexagram annotations.

        Args:
            sequence: DNA/RNA sequence
            hexagram_sequence: List of hexagram numbers
            sequence_name: Name for the sequence
            include_hexagram_annotations: Whether to include hexagram data in comments

        Returns:
            FASTA-formatted string
        """
        output = io.StringIO()

        # Write header
        output.write(f">{sequence_name}")

        if include_hexagram_annotations:
            hexagram_str = '-'.join(map(str, hexagram_sequence[:10]))  # First 10
            if len(hexagram_sequence) > 10:
                hexagram_str += "..."
            output.write(f" hexagrams={hexagram_str}")

        output.write("\n")

        # Write sequence in blocks of 60 characters
        for i in range(0, len(sequence), 60):
            output.write(sequence[i:i+60])
            output.write("\n")

        # Write hexagram annotations as separate records
        if include_hexagram_annotations:
            output.write(f">>{sequence_name}_hexagrams\n")
            hexagram_str = '-'.join(map(str, hexagram_sequence))
            for i in range(0, len(hexagram_str), 60):
                output.write(hexagram_str[i:i+60])
                output.write("\n")

        return output.getvalue()

    def export_to_image_data(
        self,
        data: Dict[str, Any],
        chart_type: str = 'bar',
        width: int = 800,
        height: int = 600
    ) -> Dict[str, Any]:
        """
        Prepare data for image/chart export.

        This returns structured data that can be used with charting libraries
        (Plotly.js on frontend, or matplotlib/server-side).

        Args:
            data: Analysis results dictionary
            chart_type: Type of chart ('bar', 'pie', 'line', 'heatmap')
            width: Chart width in pixels
            height: Chart height in pixels

        Returns:
            Dictionary with chart data configuration
        """
        chart_config = {
            'type': chart_type,
            'width': width,
            'height': height,
            'data': None,
            'layout': {}
        }

        if chart_type == 'bar' and 'hexagram_frequency' in data:
            # Bar chart of hexagram frequencies
            frequencies = data['hexagram_frequency']
            sorted_hexagrams = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)

            chart_config['data'] = {
                'x': [str(h) for h, _ in sorted_hexagrams],
                'y': [count for _, count in sorted_hexagrams],
                'type': 'bar',
                'name': 'Hexagram Frequency'
            }
            chart_config['layout'] = {
                'title': 'Hexagram Frequency Distribution',
                'xaxis': {'title': 'Hexagram Number'},
                'yaxis': {'title': 'Count'}
            }

        elif chart_type == 'pie' and 'hexagram_frequency' in data:
            # Pie chart of hexagram distribution
            frequencies = data['hexagram_frequency']
            sorted_hexagrams = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)

            chart_config['data'] = {
                'labels': [str(h) for h, _ in sorted_hexagrams],
                'values': [count for _, count in sorted_hexagrams],
                'type': 'pie',
                'name': 'Hexagram Distribution'
            }
            chart_config['layout'] = {
                'title': 'Hexagram Distribution'
            }

        elif chart_type == 'line' and 'local_entropies' in data:
            # Line chart of entropy over sequence
            entropies = data['local_entropies']
            chart_config['data'] = {
                'x': [e['position'] for e in entropies],
                'y': [e['entropy'] for e in entropies],
                'type': 'scatter',
                'mode': 'lines',
                'name': 'Entropy'
            }
            chart_config['layout'] = {
                'title': 'Position Entropy',
                'xaxis': {'title': 'Position'},
                'yaxis': {'title': 'Entropy (bits)'}
            }

        elif chart_type == 'heatmap' and 'position_distribution' in data:
            # Heatmap of position vs hexagram
            positions = sorted(data['position_distribution'].keys())
            all_hexagrams = set()

            for pos_data in data['position_distribution'].values():
                all_hexagrams.update(pos_data.get('hexagram_counts', {}).keys())

            all_hexagrams = sorted(all_hexagrams)

            # Build heatmap matrix
            matrix = []
            for pos in positions:
                row = []
                counts = data['position_distribution'][pos].get('hexagram_counts', {})
                for hexagram in all_hexagrams:
                    row.append(counts.get(hexagram, 0))
                matrix.append(row)

            chart_config['data'] = {
                'x': [str(h) for h in all_hexagrams],
                'y': [str(p) for p in positions],
                'z': matrix,
                'type': 'heatmap'
            }
            chart_config['layout'] = {
                'title': 'Position vs Hexagram Heatmap',
                'xaxis': {'title': 'Hexagram'},
                'yaxis': {'title': 'Position'}
            }

        return chart_config

    def export_to_pdf(
        self,
        data: Dict[str, Any],
        title: str = "Genetic-Hexagram Analysis Report"
    ) -> Dict[str, Any]:
        """
        Prepare data for PDF export.

        Returns a structured format that can be used to generate PDFs
        on the server using ReportLab or similar.

        Args:
            data: Analysis results dictionary
            title: Report title

        Returns:
            Dictionary with PDF content structure
        """
        pdf_content = {
            'title': title,
            'date': datetime.now().isoformat(),
            'sections': []
        }

        # Summary section
        if 'sequence_length' in data or 'codon_count' in data:
            pdf_content['sections'].append({
                'type': 'summary',
                'title': 'Analysis Summary',
                'data': {
                    'Sequence Length': data.get('sequence_length', 'N/A'),
                    'Codon Count': data.get('codon_count', 'N/A'),
                    'Mapping Scheme': data.get('mapping_scheme', 'N/A'),
                    'Dominant Hexagram': data.get('dominant_hexagram', 'N/A'),
                    'Diversity': f"{data.get('hexagram_diversity', 0):.4f}"
                }
            })

        # Hexagram frequency table
        if 'hexagram_frequency' in data:
            pdf_content['sections'].append({
                'type': 'table',
                'title': 'Hexagram Frequency Distribution',
                'headers': ['Hexagram', 'Count', 'Frequency'],
                'rows': [
                    [h, count, f"{count / sum(data['hexagram_frequency'].values()):.4f}"]
                    for h, count in sorted(
                        data['hexagram_frequency'].items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:20]  # Limit to top 20
                ]
            })

        # Chart data
        if 'hexagram_frequency' in data:
            pdf_content['sections'].append({
                'type': 'chart',
                'title': 'Frequency Distribution Chart',
                'chart_data': self.export_to_image_data(data, chart_type='bar')
            })

        # Pattern information
        if 'motifs' in data:
            pdf_content['sections'].append({
                'type': 'patterns',
                'title': 'Discovered Motifs',
                'motifs': data['motifs'][:10]  # Limit to top 10
            })

        # Position analysis
        if 'position_distribution' in data:
            pdf_content['sections'].append({
                'type': 'position_analysis',
                'title': 'Position-Specific Analysis',
                'data': data['position_distribution']
            })

        return pdf_content

    def generate_export_filename(
        self,
        analysis_type: str,
        format_type: str,
        sequence_identifier: Optional[str] = None
    ) -> str:
        """
        Generate a filename for export.

        Args:
            analysis_type: Type of analysis (e.g., 'pattern', 'comparative')
            format_type: File format (e.g., 'csv', 'json', 'pdf')
            sequence_identifier: Optional sequence identifier

        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if sequence_identifier:
            # Sanitize sequence identifier
            safe_id = ''.join(c if c.isalnum() or c in '_-' else '_' for c in sequence_identifier)[:30]
            return f"{analysis_type}_{safe_id}_{timestamp}.{format_type}"

        return f"{analysis_type}_{timestamp}.{format_type}"

    def batch_export(
        self,
        data: Dict[str, Any],
        formats: List[str],
        base_filename: str
    ) -> Dict[str, str]:
        """
        Export data to multiple formats at once.

        Args:
            data: Analysis results dictionary
            formats: List of format types ('csv', 'json', 'fasta', etc.)
            base_filename: Base filename (without extension)

        Returns:
            Dictionary mapping format to content
        """
        exports = {}

        for format_type in formats:
            filename = f"{base_filename}.{format_type}"

            try:
                if format_type == 'csv':
                    exports[filename] = self.export_to_csv(data)
                elif format_type == 'json':
                    exports[filename] = self.export_to_json(data)
                elif format_type == 'fasta':
                    # FASTA needs sequence and hexagram_sequence
                    exports[filename] = self.export_to_fasta(
                        data.get('sequence', ''),
                        data.get('hexagram_sequence', []),
                        data.get('sequence_name', base_filename)
                    )
                elif format_type == 'pdf_data':
                    exports[filename] = self.export_to_pdf(data)
                elif format_type == 'image_data':
                    exports[filename] = self.export_to_image_data(data)
                else:
                    logger.warning(f"Unknown export format: {format_type}")
            except Exception as e:
                logger.error(f"Error exporting to {format_type}: {e}")
                exports[filename] = f"Error: {str(e)}"

        return exports
