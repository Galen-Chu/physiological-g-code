"""
Serializers for Codon model
"""
from rest_framework import serializers
from api.models import Codon


class CodonSerializer(serializers.ModelSerializer):
    """Serializer for Codon model"""

    class Meta:
        model = Codon
        fields = [
            'id',
            'sequence',
            'codon_type',
            'amino_acid',
            'amino_acid_code',
            'amino_acid_full_name',
            'is_start',
            'is_stop',
            'binary_representation',
            'mapped_hexagram',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        """Add computed fields"""
        data = super().to_representation(instance)
        data['rna_equivalent'] = instance.to_rna()
        data['complement'] = instance.get_complement()
        return data
