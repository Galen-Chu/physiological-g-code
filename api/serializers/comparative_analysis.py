"""
Serializers for Comparative Analysis models
"""
from rest_framework import serializers
from api.models import ComparativeAnalysis, ComparisonCache


class ComparativeAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for ComparativeAnalysis model"""

    sequence_count = serializers.IntegerField(read_only=True)
    hexagram_difference_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ComparativeAnalysis
        fields = [
            'id',
            'user',
            'analysis_type',
            'sequence1',
            'sequence2',
            'additional_sequences',
            'sequence1_name',
            'sequence2_name',
            'mapping_schemes',
            'results',
            'similarity_score',
            'match_percentage',
            'test_type',
            'p_value',
            'is_significant',
            'analysis_name',
            'analysis_description',
            'window_size',
            'min_conservation',
            'is_public',
            'tags',
            'notes',
            'sequence_count',
            'hexagram_difference_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'user',
            'created_at',
            'updated_at',
        ]

    def create(self, validated_data):
        """Set user from context"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class ComparisonCacheSerializer(serializers.ModelSerializer):
    """Serializer for ComparisonCache model"""

    class Meta:
        model = ComparisonCache
        fields = [
            'id',
            'cache_key',
            'user',
            'input_data',
            'results',
            'hit_count',
            'last_accessed',
            'created_at',
        ]
        read_only_fields = [
            'cache_key',
            'hit_count',
            'last_accessed',
            'created_at',
        ]


class SequenceComparisonRequestSerializer(serializers.Serializer):
    """Serializer for sequence comparison requests"""

    sequence1 = serializers.CharField(
        help_text='First DNA/RNA sequence',
    )
    sequence2 = serializers.CharField(
        help_text='Second DNA/RNA sequence',
    )
    sequence1_name = serializers.CharField(
        required=False,
        default='Sequence 1',
        help_text='Name for first sequence',
    )
    sequence2_name = serializers.CharField(
        required=False,
        default='Sequence 2',
        help_text='Name for second sequence',
    )
    mapping_scheme = serializers.CharField(
        required=False,
        default='scheme_1',
        help_text='Binary mapping scheme to use',
    )
    include_alignment = serializers.BooleanField(
        required=False,
        default=False,
        help_text='Include detailed side-by-side alignment',
    )


class MappingComparisonRequestSerializer(serializers.Serializer):
    """Serializer for mapping scheme comparison requests"""

    sequence = serializers.CharField(
        help_text='DNA/RNA sequence to analyze',
    )
    schemes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=['scheme_1', 'scheme_2', 'scheme_3', 'scheme_4'],
        help_text='Mapping schemes to compare',
    )


class StatisticalTestRequestSerializer(serializers.Serializer):
    """Serializer for statistical test requests"""

    sequence1 = serializers.CharField(
        help_text='First DNA/RNA sequence',
    )
    sequence2 = serializers.CharField(
        help_text='Second DNA/RNA sequence',
    )
    test_type = serializers.ChoiceField(
        choices=['chi_square', 'fisher_exact', 'ks_test'],
        default='chi_square',
        help_text='Type of statistical test',
    )
    mapping_scheme = serializers.CharField(
        required=False,
        default='scheme_1',
        help_text='Binary mapping scheme to use',
    )


class MultipleSequenceComparisonRequestSerializer(serializers.Serializer):
    """Serializer for multiple sequence comparison requests"""

    sequences = serializers.ListField(
        child=serializers.CharField(),
        min_length=2,
        help_text='List of sequences to compare',
    )
    sequence_names = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='Optional names for each sequence',
    )
    mapping_scheme = serializers.CharField(
        required=False,
        default='scheme_1',
        help_text='Binary mapping scheme to use',
    )


class ConservedRegionsRequestSerializer(serializers.Serializer):
    """Serializer for conserved regions search requests"""

    sequences = serializers.ListField(
        child=serializers.CharField(),
        min_length=2,
        help_text='List of sequences to analyze',
    )
    window_size = serializers.IntegerField(
        required=False,
        default=5,
        min_value=2,
        help_text='Size of sliding window',
    )
    min_conservation = serializers.FloatField(
        required=False,
        default=0.8,
        min_value=0.0,
        max_value=1.0,
        help_text='Minimum conservation threshold (0-1)',
    )
    mapping_scheme = serializers.CharField(
        required=False,
        default='scheme_1',
        help_text='Binary mapping scheme to use',
    )
