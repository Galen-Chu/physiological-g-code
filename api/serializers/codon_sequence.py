"""
Serializers for CodonSequence model
"""
from rest_framework import serializers
from api.models import CodonSequence, Hexagram


class CodonSequenceSerializer(serializers.ModelSerializer):
    """Serializer for CodonSequence model"""

    dominant_hexagram_name = serializers.CharField(source='dominant_hexagram.name_english', read_only=True)
    dominant_hexagram_number = serializers.IntegerField(source='domominant_hexagram.number', read_only=True)

    class Meta:
        model = CodonSequence
        fields = [
            'id',
            'name',
            'description',
            'user',
            'sequence_type',
            'raw_sequence',
            'organism',
            'gene_name',
            'location',
            'amino_acid_sequence',
            'hexagram_sequence',
            'gc_content',
            'codon_count',
            'dominant_hexagram',
            'dominant_hexagram_name',
            'dominant_hexagram_number',
            'hexagram_diversity',
            'is_reference',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'user',
            'amino_acid_sequence',
            'hexagram_sequence',
            'gc_content',
            'codon_count',
            'dominant_hexagram',
            'hexagram_diversity',
            'created_at',
            'updated_at',
        ]

    def create(self, validated_data):
        """Set user from context"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
