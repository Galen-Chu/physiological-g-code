"""
Serializers for Analysis Pattern models
"""
from rest_framework import serializers
from api.models import AnalysisPattern, PatternMatch


class AnalysisPatternSerializer(serializers.ModelSerializer):
    """Serializer for AnalysisPattern model"""

    pattern_length = serializers.IntegerField(read_only=True)
    hexagram_diversity = serializers.FloatField(read_only=True)
    dominant_hexagram = serializers.IntegerField(read_only=True)

    class Meta:
        model = AnalysisPattern
        fields = [
            'id',
            'user',
            'pattern_type',
            'sequence',
            'hexagram_sequence',
            'pattern_data',
            'frequency',
            'significance_score',
            'pattern_name',
            'pattern_description',
            'window_size',
            'min_occurrences',
            'start_position',
            'end_position',
            'related_sequences',
            'mapping_scheme',
            'is_public',
            'is_verified',
            'tags',
            'notes',
            'pattern_length',
            'hexagram_diversity',
            'dominant_hexagram',
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


class PatternMatchSerializer(serializers.ModelSerializer):
    """Serializer for PatternMatch model"""

    class Meta:
        model = PatternMatch
        fields = [
            'id',
            'pattern',
            'sequence_id',
            'sequence_name',
            'match_positions',
            'match_score',
            'is_reverse_complement',
            'discovered_at',
        ]
        read_only_fields = [
            'discovered_at',
        ]


class PatternAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for pattern analysis requests"""

    sequence = serializers.CharField(
        help_text='DNA or RNA sequence to analyze',
    )
    mapping_scheme = serializers.CharField(
        required=False,
        default='scheme_1',
        help_text='Binary mapping scheme to use',
    )
    window_size = serializers.IntegerField(
        required=False,
        default=3,
        help_text='Window size for sliding window analysis',
    )
    min_occurrences = serializers.IntegerField(
        required=False,
        default=3,
        help_text='Minimum occurrences for motif detection',
    )
    motif_lengths = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[2, 3, 4, 5],
        help_text='Motif lengths to search for',
    )


class PositionAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for position analysis requests"""

    sequence = serializers.CharField(
        help_text='DNA or RNA sequence to analyze',
    )
    mapping_scheme = serializers.CharField(
        required=False,
        default='scheme_1',
        help_text='Binary mapping scheme to use',
    )


class SlidingWindowRequestSerializer(serializers.Serializer):
    """Serializer for sliding window analysis requests"""

    sequence = serializers.CharField(
        help_text='DNA or RNA sequence to analyze',
    )
    window_size = serializers.IntegerField(
        required=False,
        default=3,
        min_value=2,
        help_text='Size of sliding window',
    )
    step_size = serializers.IntegerField(
        required=False,
        default=1,
        min_value=1,
        help_text='Step size for sliding window',
    )
    mapping_scheme = serializers.CharField(
        required=False,
        default='scheme_1',
        help_text='Binary mapping scheme to use',
    )


class MotifDiscoveryRequestSerializer(serializers.Serializer):
    """Serializer for motif discovery requests"""

    sequence = serializers.CharField(
        help_text='DNA or RNA sequence to analyze',
    )
    motif_lengths = serializers.ListField(
        child=serializers.IntegerField(min_value=2, max_value=10),
        required=False,
        default=[2, 3, 4, 5],
        help_text='Motif lengths to search for',
    )
    min_occurrences = serializers.IntegerField(
        required=False,
        default=3,
        min_value=2,
        help_text='Minimum number of occurrences',
    )
    max_motifs = serializers.IntegerField(
        required=False,
        default=20,
        min_value=1,
        help_text='Maximum number of motifs to return',
    )
    mapping_scheme = serializers.CharField(
        required=False,
        default='scheme_1',
        help_text='Binary mapping scheme to use',
    )


class ConservationAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for conservation analysis requests"""

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
