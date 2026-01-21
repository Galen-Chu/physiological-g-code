"""
Serializers for Hexagram model
"""
from rest_framework import serializers
from api.models import Hexagram


class HexagramSerializer(serializers.ModelSerializer):
    """Serializer for Hexagram model"""

    lines_array = serializers.ListField(read_only=True)
    yang_lines = serializers.IntegerField(read_only=True)
    yin_lines = serializers.IntegerField(read_only=True)
    is_balanced = serializers.BooleanField(read_only=True)
    unicode_char = serializers.CharField(read_only=True)

    class Meta:
        model = Hexagram
        fields = [
            'id',
            'number',
            'binary',
            'name_chinese',
            'name_pinyin',
            'name_english',
            'line1',
            'line2',
            'line3',
            'line4',
            'line5',
            'line6',
            'lower_trigram',
            'upper_trigram',
            'lower_trigram_name',
            'upper_trigram_name',
            'keywords',
            'description',
            'nuclear_hexagram',
            'opposite_hexagram',
            'lines_array',
            'yang_lines',
            'yin_lines',
            'is_balanced',
            'unicode_char',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_lines_array(self, obj):
        return obj.get_lines_array()

    def get_yang_lines(self, obj):
        return obj.get_yang_lines()

    def get_yin_lines(self, obj):
        return obj.get_yin_lines()

    def get_is_balanced(self, obj):
        return obj.is_balanced()

    def get_unicode_char(self, obj):
        return obj.get_hexagram_unicode()
