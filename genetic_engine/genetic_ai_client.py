"""
Genetic AI Client - Google Gemini integration for genetic-hexagram analysis
"""
import logging
import json
from typing import Dict, List, Optional, Any
from django.conf import settings
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeneticAIError(Exception):
    """Custom exception for Genetic AI operations"""
    pass


class GeneticGeminiClient:
    """
    Google Gemini AI client for genetic-hexagram interpretations.

    This client handles:
    1. Generating hexagram interpretations in biological context
    2. Inducing optimal codon-hexagram mappings
    3. Analyzing genetic patterns with I Ching wisdom
    4. Synthesizing modern science with ancient philosophy
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client.

        Args:
            api_key: Google API key (uses settings if not provided)
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            logger.warning("No Gemini API key provided")
            self.model = None
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("GeneticGeminiClient initialized")

    def generate_hexagram_interpretation(
        self,
        hexagram_number: int,
        hexagram_name: str,
        hexagram_binary: str,
        codon: Optional[str] = None,
        amino_acid: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate AI interpretation of a hexagram in biological context.

        Args:
            hexagram_number: Hexagram number (1-64)
            hexagram_name: Hexagram name
            hexagram_binary: Binary representation
            codon: Associated codon (optional)
            amino_acid: Associated amino acid (optional)
            context: Additional context (optional)

        Returns:
            Dictionary with interpretation components
        """
        if not self.model:
            return self._mock_interpretation(hexagram_number)

        prompt = self._build_interpretation_prompt(
            hexagram_number, hexagram_name, hexagram_binary,
            codon, amino_acid, context
        )

        try:
            response = self.model.generate_content(prompt)
            return self._parse_interpretation_response(response.text)
        except Exception as e:
            logger.error(f"Error generating interpretation: {e}")
            return self._mock_interpretation(hexagram_number)

    def induce_codon_hexagram_mapping(
        self,
        codons: List[str],
        amino_acids: List[str],
        existing_mappings: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Use AI to induce optimal codon-to-hexagram mappings.

        The AI will analyze patterns and suggest meaningful associations
        based on biological properties, hexagram meanings, and
        philosophical correspondences.

        Args:
            codons: List of codon sequences
            amino_acids: Corresponding amino acids
            existing_mappings: Optional existing mappings to refine

        Returns:
            Dictionary with suggested mappings and rationale
        """
        if not self.model:
            return self._mock_mapping_induction(codons)

        prompt = self._build_mapping_prompt(
            codons, amino_acids, existing_mappings
        )

        try:
            response = self.model.generate_content(prompt)
            return self._parse_mapping_response(response.text, codons)
        except Exception as e:
            logger.error(f"Error inducing mapping: {e}")
            return self._mock_mapping_induction(codons)

    def analyze_sequence_patterns(
        self,
        sequence: str,
        hexagram_sequence: List[int],
        amino_acid_sequence: str
    ) -> Dict[str, Any]:
        """
        Analyze patterns in a genetic sequence with hexagram correlations.

        Args:
            sequence: Original DNA/RNA sequence
            hexagram_sequence: Corresponding hexagram numbers
            amino_acid_sequence: Translated amino acid sequence

        Returns:
            Dictionary with pattern analysis
        """
        if not self.model:
            return self._mock_pattern_analysis(sequence)

        prompt = self._build_pattern_analysis_prompt(
            sequence, hexagram_sequence, amino_acid_sequence
        )

        try:
            response = self.model.generate_content(prompt)
            return self._parse_pattern_response(response.text)
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
            return self._mock_pattern_analysis(sequence)

    def synthesize_biological_hexagram_meaning(
        self,
        biological_concept: str,
        hexagram_number: int,
        hexagram_name: str
    ) -> str:
        """
        Synthesize biological concept with hexagram wisdom.

        Args:
            biological_concept: Biological term or concept
            hexagram_number: Associated hexagram
            hexagram_name: Hexagram name

        Returns:
            Synthesized interpretation text
        """
        if not self.model:
            return self._mock_synthesis(biological_concept, hexagram_name)

        prompt = f"""
        Synthesize the meaning of the biological concept "{biological_concept}"
        with I Ching hexagram {hexagram_number} ({hexagram_name}).

        Provide a deep, meaningful interpretation that bridges:
        1. Modern scientific understanding of {biological_concept}
        2. Traditional I Ching wisdom of {hexagram_name}
        3. Philosophical connections between the two

        Format as a cohesive, insightful paragraph.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error synthesizing meaning: {e}")
            return self._mock_synthesis(biological_concept, hexagram_name)

    def _build_interpretation_prompt(
        self,
        hexagram_number: int,
        hexagram_name: str,
        hexagram_binary: str,
        codon: Optional[str],
        amino_acid: Optional[str],
        context: Optional[str]
    ) -> str:
        """Build prompt for hexagram interpretation"""
        prompt = f"""
        Interpret I Ching Hexagram {hexagram_number} ({hexagram_name}) in a biological context.

        Binary representation: {hexagram_binary}
        """

        if codon:
            prompt += f"\nAssociated codon: {codon}"
        if amino_acid:
            prompt += f"\nAmino acid: {amino_acid}"
        if context:
            prompt += f"\nContext: {context}"

        prompt += """

        Provide a comprehensive interpretation with these sections:
        1. **Traditional Meaning**: Core I Ching meaning
        2. **Biological Significance**: How this relates to the codon/amino acid
        3. **Synthesis**: Bridge between ancient wisdom and modern biology
        4. **Keywords**: 5-7 key concepts

        Format as JSON with keys: traditional_meaning, biological_significance, synthesis, keywords
        """
        return prompt

    def _build_mapping_prompt(
        self,
        codons: List[str],
        amino_acids: List[str],
        existing_mappings: Optional[Dict[str, int]]
    ) -> str:
        """Build prompt for mapping induction"""
        prompt = "Analyze these codons and suggest hexagram mappings:\n\n"

        for codon, amino in zip(codons, amino_acids):
            prompt += f"{codon} -> {amino}\n"

        if existing_mappings:
            prompt += f"\nExisting mappings to consider: {existing_mappings}"

        prompt += """

        Suggest hexagram mappings (1-64) based on:
        1. Binary properties of nucleotides
        2. Amino acid properties (hydrophobic, polar, charged)
        3. Traditional hexagram meanings
        4. Philosophical correspondences

        Return as JSON with:
        - mappings: [{"codon": "ATG", "hexagram": 1, "rationale": "..."}]
        - overall_approach: description of methodology
        """
        return prompt

    def _build_pattern_analysis_prompt(
        self,
        sequence: str,
        hexagram_sequence: List[int],
        amino_acid_sequence: str
    ) -> str:
        """Build prompt for pattern analysis"""
        prompt = f"""
        Analyze this genetic sequence and its hexagram correspondences:

        Sequence: {sequence[:50]}... (showing first 50 nucleotides)
        Hexagram sequence: {hexagram_sequence[:20]}
        Amino acid sequence: {amino_acid_sequence[:50]}

        Identify:
        1. Recurring hexagram patterns
        2. Significant hexagram transitions
        3. Correlations with protein structure
        4. Philosophical/biological insights

        Return as JSON with: patterns, transitions, insights, significance
        """
        return prompt

    def _parse_interpretation_response(self, response_text: str) -> Dict[str, str]:
        """Parse AI interpretation response"""
        try:
            # Try to parse as JSON
            data = json.loads(response_text)
            return {
                'traditional_meaning': data.get('traditional_meaning', ''),
                'biological_significance': data.get('biological_significance', ''),
                'synthesis': data.get('synthesis', ''),
                'keywords': data.get('keywords', [])
            }
        except json.JSONDecodeError:
            # Fallback: parse as text
            return {
                'interpretation': response_text,
                'keywords': []
            }

    def _parse_mapping_response(self, response_text: str, codons: List[str]) -> Dict[str, Any]:
        """Parse AI mapping response"""
        try:
            data = json.loads(response_text)
            return {
                'mappings': data.get('mappings', []),
                'approach': data.get('overall_approach', ''),
                'confidence': 0.8
            }
        except json.JSONDecodeError:
            return self._mock_mapping_induction(codons)

    def _parse_pattern_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI pattern response"""
        try:
            data = json.loads(response_text)
            return {
                'patterns': data.get('patterns', []),
                'transitions': data.get('transitions', []),
                'insights': data.get('insights', ''),
                'significance': data.get('significance', '')
            }
        except json.JSONDecodeError:
            return {
                'analysis': response_text,
                'patterns': []
            }

    # Mock methods for when API is unavailable
    def _mock_interpretation(self, hexagram_number: int) -> Dict[str, str]:
        """Generate mock interpretation"""
        return {
            'traditional_meaning': f"Traditional interpretation of hexagram {hexagram_number}",
            'biological_significance': "Biological significance to be determined",
            'synthesis': "Integration of ancient and modern wisdom",
            'keywords': ["change", "balance", "transformation"]
        }

    def _mock_mapping_induction(self, codons: List[str]) -> Dict[str, Any]:
        """Generate mock mapping"""
        mappings = []
        for i, codon in enumerate(codons[:64], 1):
            mappings.append({
                'codon': codon,
                'hexagram': i,
                'rationale': 'Binary-based mapping'
            })
        return {
            'mappings': mappings,
            'approach': 'Mock binary mapping',
            'confidence': 0.5
        }

    def _mock_pattern_analysis(self, sequence: str) -> Dict[str, Any]:
        """Generate mock pattern analysis"""
        return {
            'patterns': ['repetition', 'transition'],
            'transitions': [],
            'insights': 'Pattern analysis pending',
            'significance': 'To be determined'
        }

    def _mock_synthesis(self, concept: str, hexagram_name: str) -> str:
        """Generate mock synthesis"""
        return f"The biological concept of {concept} relates to {hexagram_name} through themes of transformation and balance."
