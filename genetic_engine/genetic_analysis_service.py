"""
Genetic Analysis Service - Orchestrates codon-to-hexagram analysis
"""
import logging
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from api.models import Codon, Hexagram, CodonSequence, CodonHexagramMapping, HexagramInterpretation
from .codon_translator import CodonTranslator
from .hexagram_mapper import HexagramMapper
from .genetic_ai_client import GeneticGeminiClient

User = get_user_model()
logger = logging.getLogger(__name__)


class GeneticAnalysisService:
    """
    Main service for genetic-hexagram analysis.

    Orchestrates:
    - Sequence translation to hexagrams
    - Pattern analysis
    - AI interpretation generation
    - Mapping management
    """

    def __init__(self, user: Optional[User] = None):
        """
        Initialize the service.

        Args:
            user: Optional user context for personalized analysis
        """
        self.user = user
        self.translator = CodonTranslator()
        self.mapper = HexagramMapper()
        self.ai_client = GeneticGeminiClient()
        logger.info("GeneticAnalysisService initialized")

    def analyze_sequence(
        self,
        sequence: str,
        sequence_name: str,
        sequence_type: str = 'DNA',
        mapping_scheme: str = 'scheme_1',
        save: bool = True
    ) -> Dict[str, Any]:
        """
        Perform complete analysis of a genetic sequence.

        Args:
            sequence: DNA/RNA sequence string
            sequence_name: Name for this sequence
            sequence_type: 'DNA' or 'RNA'
            mapping_scheme: Binary mapping scheme to use
            save: Whether to save results to database

        Returns:
            Dictionary with complete analysis results
        """
        sequence = sequence.upper().replace(' ', '')

        # Convert RNA to DNA if needed
        if sequence_type == 'RNA':
            sequence = sequence.replace('U', 'T')

        # Translate sequence to hexagrams
        hexagram_sequence = self.translator.translate_sequence(sequence)

        # Translate to amino acids
        amino_acid_sequence = self.translator.translate_to_amino_acids(sequence)

        # Get codon list
        codons = self.translator.get_codons if hasattr(self.translator, 'get_codons') else \
                 [sequence[i:i+3] for i in range(0, len(sequence), 3)]

        # Analyze patterns
        frequency = self.translator.get_codon_frequency(hexagram_sequence)
        dominant = self.translator.get_dominant_hexagram(hexagram_sequence)
        diversity = self.translator.calculate_hexagram_diversity(hexagram_sequence)

        # Get transitions
        transitions = self.mapper.get_hexagram_transitions(hexagram_sequence)
        transition_analysis = self.mapper.analyze_transition_pattern(transitions)

        # Build results
        results = {
            'sequence_name': sequence_name,
            'raw_sequence': sequence,
            'sequence_type': sequence_type,
            'length': len(sequence),
            'codon_count': len(codons),
            'hexagram_sequence': hexagram_sequence,
            'amino_acid_sequence': amino_acid_sequence,
            'codons': codons,
            'dominant_hexagram': dominant,
            'hexagram_frequency': frequency,
            'diversity': diversity,
            'transitions': transitions,
            'transition_analysis': transition_analysis,
            'gc_content': self._calculate_gc_content(sequence),
            'mapping_scheme': mapping_scheme,
        }

        # Save if requested
        if save and self.user:
            results['saved_object'] = self._save_sequence_analysis(results)

        return results

    def get_hexagram_for_codon(
        self,
        codon: str,
        mapping_scheme: str = 'scheme_1'
    ) -> Optional[int]:
        """
        Get the hexagram for a single codon.

        Args:
            codon: Three-nucleotide sequence
            mapping_scheme: Mapping scheme to use

        Returns:
            Hexagram number (1-64) or None
        """
        return self.mapper.map_codon_to_hexagram(codon, mapping_scheme)

    def generate_hexagram_interpretation(
        self,
        hexagram_number: int,
        codon: Optional[str] = None,
        context: Optional[str] = None,
        save: bool = True
    ) -> Dict[str, str]:
        """
        Generate AI interpretation for a hexagram.

        Args:
            hexagram_number: Hexagram number (1-64)
            codon: Optional associated codon
            context: Additional context
            save: Whether to save to database

        Returns:
            Dictionary with interpretation
        """
        try:
            hexagram = Hexagram.objects.get(number=hexagram_number)
        except Hexagram.DoesNotExist:
            logger.error(f"Hexagram {hexagram_number} not found")
            return {'error': 'Hexagram not found'}

        # Get codon info if provided
        codon_obj = None
        amino_acid = None
        if codon:
            try:
                codon_obj = Codon.objects.get(sequence=codon.upper())
                amino_acid = codon_obj.amino_acid
            except Codon.DoesNotExist:
                pass

        # Generate interpretation
        interpretation = self.ai_client.generate_hexagram_interpretation(
            hexagram_number=hexagram_number,
            hexagram_name=hexagram.name_english,
            hexagram_binary=hexagram.binary,
            codon=codon,
            amino_acid=amino_acid,
            context=context
        )

        # Save if requested
        if save and self.user:
            self._save_interpretation(hexagram, codon_obj, interpretation, context)

        return interpretation

    def induce_codon_mapping(
        self,
        include_amino_acids: bool = True,
        save: bool = True
    ) -> Dict[str, Any]:
        """
        Use AI to induce optimal codon-hexagram mapping.

        Args:
            include_amino_acids: Whether to include amino acid properties
            save: Whether to save mapping to database

        Returns:
            Dictionary with induced mapping
        """
        # Get all codons
        codons = list(Codon.objects.values_list('sequence', flat=True))
        amino_acids = []
        if include_amino_acids:
            amino_acids = list(Codon.objects.values_list('amino_acid_code', flat=True))

        # Get existing mappings
        existing_mapping = CodonHexagramMapping.objects.filter(
            mapping_type='BINARY',
            is_active=True
        ).first()

        existing_data = None
        if existing_mapping:
            existing_data = {m['codon']: m['hexagram'] for m in existing_mapping.mapping_rules}

        # Induce new mapping
        result = self.ai_client.induce_codon_hexagram_mapping(
            codons=codons,
            amino_acids=amino_acids,
            existing_mappings=existing_data
        )

        # Save if requested
        if save and result.get('mappings'):
            self._save_induced_mapping(result)

        return result

    def get_active_mapping(self) -> Optional[CodonHexagramMapping]:
        """Get the currently active codon-hexagram mapping"""
        return CodonHexagramMapping.objects.filter(is_active=True).first()

    def get_sequence_statistics(
        self,
        sequence_id: int
    ) -> Dict[str, Any]:
        """
        Get statistics for a saved sequence.

        Args:
            sequence_id: ID of saved sequence

        Returns:
            Dictionary with statistics
        """
        try:
            seq = CodonSequence.objects.get(id=sequence_id, user=self.user)
        except CodonSequence.DoesNotExist:
            return {'error': 'Sequence not found'}

        return {
            'name': seq.name,
            'codon_count': seq.codon_count,
            'gc_content': seq.gc_content,
            'dominant_hexagram': seq.dominant_hexagram.number if seq.dominant_hexagram else None,
            'hexagram_diversity': seq.hexagram_diversity,
            'organism': seq.organism,
            'gene_name': seq.gene_name,
        }

    def _calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content percentage"""
        if len(sequence) == 0:
            return 0.0
        gc_count = sequence.upper().count('G') + sequence.upper().count('C')
        return (gc_count / len(sequence)) * 100

    @transaction.atomic
    def _save_sequence_analysis(self, results: Dict[str, Any]) -> CodonSequence:
        """Save sequence analysis to database"""
        sequence = CodonSequence.objects.create(
            user=self.user,
            name=results['sequence_name'],
            raw_sequence=results['raw_sequence'],
            sequence_type=results['sequence_type'],
            codon_count=results['codon_count'],
            gc_content=results['gc_content'],
            amino_acid_sequence=results['amino_acid_sequence'],
            hexagram_sequence=results['hexagram_sequence'],
        )

        # Set dominant hexagram
        if results['dominant_hexagram']:
            try:
                sequence.dominant_hexagram = Hexagram.objects.get(
                    number=results['dominant_hexagram']
                )
            except Hexagram.DoesNotExist:
                pass

        sequence.hexagram_diversity = results['diversity']
        sequence.save()

        logger.info(f"Saved sequence analysis: {sequence.id}")
        return sequence

    def _save_interpretation(
        self,
        hexagram: Hexagram,
        codon: Optional[Codon],
        interpretation: Dict[str, str],
        context: Optional[str]
    ) -> HexagramInterpretation:
        """Save interpretation to database"""
        return HexagramInterpretation.objects.create(
            hexagram=hexagram,
            user=self.user,
            codon=codon,
            context=context or '',
            interpretation=interpretation.get('interpretation', ''),
            biological_significance=interpretation.get('biological_significance', ''),
            traditional_meaning=interpretation.get('traditional_meaning', ''),
            synthesis=interpretation.get('synthesis', ''),
            concepts=interpretation.get('keywords', []),
        )

    @transaction.atomic
    def _save_induced_mapping(self, result: Dict[str, Any]) -> CodonHexagramMapping:
        """Save induced mapping to database"""
        # Deactivate existing mappings
        CodonHexagramMapping.objects.filter(is_active=True).update(is_active=False)

        # Create new mapping
        mapping = CodonHexagramMapping.objects.create(
            name=f"AI Induced Mapping {timezone.now().strftime('%Y-%m-%d')}",
            description=result.get('approach', ''),
            mapping_type='AI_INDUCED',
            created_by=self.user,
            is_active=True,
            mapping_rules=result.get('mappings', []),
            total_mappings=len(result.get('mappings', [])),
            ai_model='gemini-pro',
            ai_confidence_scores=result.get('confidence'),
        )

        mapping.calculate_coverage()
        logger.info(f"Saved induced mapping: {mapping.id}")
        return mapping
