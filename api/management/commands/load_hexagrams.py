"""
Django management command to load all 64 I Ching hexagrams
"""
from django.core.management.base import BaseCommand
from api.models import Hexagram


class Command(BaseCommand):
    help = 'Load all 64 I Ching hexagrams into the database'

    # Complete list of 64 hexagrams in King Wen sequence
    HEXAGRAMS = [
        # (number, binary, chinese, pinyin, english, lower_trigram, upper_trigram,
        #  lower_name, upper_name, keywords[], description)
        (1, '111111', '乾', 'Qian', 'The Creative', '111', '111', 'Heaven', 'Heaven',
         ['creation', 'strength', 'creativity', 'persistence'],
         'The creative works sublime success, furthering through perseverance.'),
        (2, '000000', '坤', 'Kun', 'The Receptive', '000', '000', 'Earth', 'Earth',
         ['receptivity', 'devotion', 'nurturing', 'support'],
         'The receptive brings sublime success, furthering through the perseverance of a mare.'),
        (3, '100010', '屯', 'Zhun', 'Difficulty at Beginning', '100', '010', 'Thunder', 'Water',
         ['beginning', 'difficulty', 'chaos', 'potential'],
         'Difficulty at beginning works supreme success, furthering through persistence.'),
        (4, '010001', '蒙', 'Meng', 'Youthful Folly', '010', '001', 'Water', 'Mountain',
         ['inexperience', 'learning', 'youth', 'growth'],
         'Youthful folly brings success, not repeating the first error.'),
        (5, '010111', '需', 'Xu', 'Waiting', '010', '111', 'Water', 'Heaven',
         ['waiting', 'patience', 'nourishment', 'confidence'],
         'Waiting with confidence brings success.'),
        (6, '111010', '訟', 'Song', 'Conflict', '111', '010', 'Heaven', 'Water',
         ['conflict', 'dispute', 'caution', 'resolution'],
         'Conflict requires caution and seeking middle ground.'),
        # ... (would include all 64 hexagrams)
    ]

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for hex_data in self.HEXAGRAMS:
            (
                number, binary, chinese, pinyin, english,
                lower_tri, upper_tri, lower_name, upper_name,
                keywords, description
            ) = hex_data

            hexagram, created_flag = Hexagram.objects.update_or_create(
                number=number,
                defaults={
                    'binary': binary,
                    'name_chinese': chinese,
                    'name_pinyin': pinyin,
                    'name_english': english,
                    'line1': binary[0],
                    'line2': binary[1],
                    'line3': binary[2],
                    'line4': binary[3],
                    'line5': binary[4],
                    'line6': binary[5],
                    'lower_trigram': lower_tri,
                    'upper_trigram': upper_tri,
                    'lower_trigram_name': lower_name,
                    'upper_trigram_name': upper_name,
                    'keywords': keywords,
                    'description': description,
                }
            )

            if created_flag:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded hexagrams: {created} created, {updated} updated'
            )
        )
