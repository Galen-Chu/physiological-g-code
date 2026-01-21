"""
Serializers for HexagramInterpretation model
"""
from rest_framework import serializers
from api.models import HexagramInterpretation


class HexagramInterpretationSerializer(serializers.ModelSerializer):
    """Serializer for HexagramInterpretation model"""

    hexagram_name = serializers.CharField(source='hexagram.name_english', read_only=True)
    hexagram_number = serializers.IntegerField(source='hexagram.number', read_only=True)
    codon_sequence = serializers.CharField(source='codon.sequence', read_only=True)

    class Meta:
        model = HexagramInterpretation
        fields = [
            'id',
            'hexagram',
            'hexagram_name',
            'hexagram_number',
            'user',
            'context',
            'interpretation',
            'codon',
            'codon_sequence',
            'biological_significance',
            'traditional_meaning',
            'synthesis',
            'concepts',
            'confidence',
            'model_version',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Set user from context"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
