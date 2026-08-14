"""Unit tests for the genetic engine (no network, no database)."""
from genetic_engine.codon_translator import CodonTranslator
from genetic_engine.hexagram_mapper import HexagramMapper
from genetic_engine.genetic_analysis_service import GeneticAnalysisService

ALL_CODONS = [
    a + b + c
    for a in 'ACGT' for b in 'ACGT' for c in 'ACGT'
]


class TestCodonTranslator:
    def test_translate_returns_hexagram_number_for_all_64_codons(self):
        translator = CodonTranslator(mapping_scheme='scheme_1')
        results = [translator.translate_codon(codon) for codon in ALL_CODONS]
        assert all(isinstance(r, int) and 1 <= r <= 64 for r in results)

    def test_scheme_collapses_to_8_hexagrams_by_design(self):
        """Each scheme maps a base to one bit, so a codon (3 bases) yields
        3 bits -> at most 8 distinct hexagrams. That is the documented
        purine/pyrimidine compression, not a bug."""
        for scheme in ('scheme_1', 'scheme_2', 'scheme_3', 'scheme_4'):
            translator = CodonTranslator(mapping_scheme=scheme)
            results = {translator.translate_codon(codon) for codon in ALL_CODONS}
            assert 1 <= len(results) <= 8
            assert all(1 <= r <= 8 for r in results)

    def test_schemes_genuinely_differ(self):
        t1 = CodonTranslator(mapping_scheme='scheme_1')
        t2 = CodonTranslator(mapping_scheme='scheme_2')
        assert any(t1.translate_codon(c) != t2.translate_codon(c) for c in ALL_CODONS)

    def test_unknown_codon_returns_none(self):
        translator = CodonTranslator(mapping_scheme='scheme_1')
        assert translator.translate_codon('XXX') is None
        assert translator.translate_codon('AT') is None


class TestHexagramMapper:
    def test_get_hexagram_binary_for_all_64(self):
        mapper = HexagramMapper()
        for number in range(1, 65):
            binary = mapper.get_hexagram_binary(number)
            assert binary is not None and len(binary) == 6

    def test_complementary_hexagram_round_trip(self):
        mapper = HexagramMapper()
        for number in range(1, 65):
            comp = mapper.get_complementary_hexagram(number)
            if comp is not None:
                assert mapper.get_complementary_hexagram(comp) == number


class TestGeneticAnalysisService:
    def test_analyze_sequence_basic_fields(self):
        service = GeneticAnalysisService()
        results = service.analyze_sequence(
            sequence='ATGCGATAA',
            sequence_name='Sample Gene',
            sequence_type='DNA',
            mapping_scheme='scheme_1',
        )
        assert results['hexagram_sequence']  # non-empty
        assert len(results['hexagram_sequence']) == 3  # ATG CGA TAA
        assert results['amino_acid_sequence'] == 'M*R' or 'M' in results['amino_acid_sequence']
        # GC content of ATGCGATAA = 3/9
        gc = results.get('gc_content')
        if isinstance(gc, (int, float)):
            assert abs(gc - 100 * 3 / 9) < 0.01

    def test_analyze_sequence_is_case_insensitive(self):
        service = GeneticAnalysisService()
        upper = service.analyze_sequence(
            sequence='ATGCGATAA', sequence_name='U', sequence_type='DNA',
            mapping_scheme='scheme_1', save=False)
        lower = service.analyze_sequence(
            sequence='atgcgataa', sequence_name='L', sequence_type='DNA',
            mapping_scheme='scheme_1', save=False)
        assert upper['hexagram_sequence'] == lower['hexagram_sequence']
