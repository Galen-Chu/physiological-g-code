"""
Hexagram Model - Represents I Ching (易經) hexagrams
"""
from django.db import models


class Hexagram(models.Model):
    """
    Represents an I Ching hexagram - a six-line figure composed of
    solid (yang) and broken (yin) lines.

    Binary representation: 0 = broken line (yin), 1 = solid line (yang)
    Lines are read from bottom to top (line 1 to line 6)
    """

    # Hexagram number (1-64)
    number = models.IntegerField(
        unique=True,
        help_text='Hexagram number (1-64) in the King Wen sequence',
    )

    # Binary representation (6 bits, bottom to top)
    # e.g., "111111" for hexagram 1 (all yang)
    #      "000000" for hexagram 2 (all yin)
    binary = models.CharField(
        max_length=6,
        unique=True,
        help_text='Binary representation (bottom line to top line)',
    )

    # Chinese name (traditional and simplified)
    name_chinese = models.CharField(
        max_length=10,
        help_text='Hexagram name in Chinese',
    )

    # Pinyin romanization
    name_pinyin = models.CharField(
        max_length=50,
        help_text='Hexagram name in pinyin',
    )

    # English translation
    name_english = models.CharField(
        max_length=100,
        help_text='English translation of hexagram name',
    )

    # The six lines (as individual characters for easy access)
    # yin = broken line (0), yang = solid line (1)
    line1 = models.CharField(max_length=1, help_text='Bottom line (0=yin, 1=yang)')
    line2 = models.CharField(max_length=1, help_text='Second line (0=yin, 1=yang)')
    line3 = models.CharField(max_length=1, help_text='Third line (0=yin, 1=yang)')
    line4 = models.CharField(max_length=1, help_text='Fourth line (0=yin, 1=yang)')
    line5 = models.CharField(max_length=1, help_text='Fifth line (0=yin, 1=yang)')
    line6 = models.CharField(max_length=1, help_text='Top line (0=yin, 1=yang)')

    # Trigrams (lower and upper)
    # Lower trigram = lines 1-3
    # Upper trigram = lines 4-6
    lower_trigram = models.CharField(
        max_length=3,
        help_text='Lower trigram (lines 1-3)',
    )

    upper_trigram = models.CharField(
        max_length=3,
        help_text='Upper trigram (lines 4-6)',
    )

    # Lower trigram name (e.g., "Heaven", "Earth", "Water", "Fire", etc.)
    lower_trigram_name = models.CharField(
        max_length=50,
        help_text='Name of lower trigram',
    )

    upper_trigram_name = models.CharField(
        max_length=50,
        help_text='Name of upper trigram',
    )

    # Keywords/concepts associated with this hexagram
    keywords = models.JSONField(
        default=list,
        help_text='Keywords and concepts associated with this hexagram',
    )

    # Traditional interpretation/description
    description = models.TextField(
        help_text='Traditional interpretation and meaning',
    )

    # Nuclear hexagram (inner structure)
    # Formed by lines 2,3,4,5
    nuclear_hexagram = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nuclear_of',
        help_text='Nuclear hexagram (lines 2-5)',
    )

    # Opposite hexagram (yin/yang inversion of all lines)
    opposite_hexagram = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opposite_of',
        help_text='Opposite hexagram (all lines inverted)',
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['number']
        verbose_name = 'Hexagram'
        verbose_name_plural = 'Hexagrams'
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['binary']),
        ]

    def __str__(self):
        return f"Hexagram {self.number}: {self.name_chinese} ({self.name_english})"

    def get_lines_array(self):
        """Return lines as array of integers (bottom to top)"""
        return [int(self.line1), int(self.line2), int(self.line3),
                int(self.line4), int(self.line5), int(self.line6)]

    def get_yang_lines(self):
        """Return count of yang lines"""
        lines = self.get_lines_array()
        return sum(lines)

    def get_yin_lines(self):
        """Return count of yin lines"""
        return 6 - self.get_yang_lines()

    def is_balanced(self):
        """Check if hexagram is balanced (3 yin, 3 yang)"""
        return self.get_yin_lines() == 3

    def get_binary_value(self):
        """Return binary representation as integer"""
        return int(self.binary, 2)

    def get_hexagram_unicode(self):
        """Return Unicode character for hexagram (if available)"""
        # Unicode hexagram range: U+4DC0 to U+4DFF
        unicode_offset = 0x4DC0
        return chr(unicode_offset + self.number - 1)
