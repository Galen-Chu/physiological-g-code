"""
Serializers for CodonHexagramMapping model
"""
from rest_framework import serializers
from api.models import CodonHexagramMapping


class CodonHexagramMappingSerializer(serializers.ModelSerializer):
    """Serializer for CodonHexagramMapping model"""

    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = CodonHexagramMapping
        fields = [
            'id',
            'name',
            'description',
            'mapping_type',
            'created_by',
            'created_by_username',
            'is_active',
            'version',
            'parent_mapping',
            'mapping_rules',
            'binary_scheme',
            'ai_model',
            'ai_confidence_scores',
            'total_mappings',
            'coverage',
            'validation_score',
            'is_public',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_by', 'coverage', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Set creator from context"""
        user = self.context['request'].user
        validated_data['created_by'] = user
        return super().create(validated_data)
