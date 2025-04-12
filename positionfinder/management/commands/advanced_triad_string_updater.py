from django.core.management.base import BaseCommand
from django.db.models import Q
from positionfinder.models_chords import ChordNotes
from positionfinder.models import NotesCategory

class Command(BaseCommand):
    help = 'Advanced Update of String for Note in Triads and Spread Triads'

    def handle(self, *args, **options):
        # Comprehensive range list
        triad_ranges = [
            'e - g', 'b - d', 'd - E', 'g - A', 
            'e - d', 'b - A', 'a - b', 'a - g', 
            'A - B', 'g - E', 'A - lowB'
        ]
        
        # Detailed string mappings with distinctions between triads and spread triads
        string_mappings = {
            # Standard Triads
            'Chords': {
                'e - g': {
                    'first_note_string': 'gString',
                    'second_note_string': 'bString', 
                    'third_note_string': 'eString'
                },
                'b - d': {
                    'first_note_string': 'dString',
                    'second_note_string': 'bString', 
                    'third_note_string': 'gString'
                },
                'd - E': {
                    'first_note_string': 'ELowString',
                    'second_note_string': 'AString', 
                    'third_note_string': 'dString'
                },
                'g - A': {
                    'first_note_string': 'AString',
                    'second_note_string': 'dString', 
                    'third_note_string': 'gString'
                },
                'e - d': {
                    'first_note_string': 'dString',
                    'second_note_string': 'gString', 
                    'third_note_string': 'bString'
                },
                'b - A': {
                    'first_note_string': 'AString',
                    'second_note_string': 'bString', 
                    'third_note_string': 'dString'
                },
                'a - b': {
                    'first_note_string': 'bString',
                    'second_note_string': 'gString', 
                    'third_note_string': 'AString'
                },
                'a - g': {
                    'first_note_string': 'gString',
                    'second_note_string': 'AString', 
                    'third_note_string': 'dString'
                },
                'A - B': {
                    'first_note_string': 'BString',
                    'second_note_string': 'AString', 
                    'third_note_string': 'highEString'
                },
                'g - E': {
                    'first_note_string': 'ELowString',
                    'second_note_string': 'gString', 
                    'third_note_string': 'AString'
                },
                'A - lowB': {
                    'first_note_string': 'lowBString',
                    'second_note_string': 'ELowString', 
                    'third_note_string': 'AString'
                }
            },
            # Spread Triads - more spread out voicings
            'Spread Triads': {
                'e - g': {
                    'first_note_string': 'highAString',
                    'second_note_string': 'eString', 
                    'third_note_string': 'bString'
                },
                'b - d': {
                    'first_note_string': 'gString',
                    'second_note_string': 'highEString', 
                    'third_note_string': 'AString'
                },
                'd - E': {
                    'first_note_string': 'dString',
                    'second_note_string': 'lowBString', 
                    'third_note_string': 'gString'
                },
                'g - A': {
                    'first_note_string': 'highEString',
                    'second_note_string': 'AString', 
                    'third_note_string': 'dString'
                },
                'e - d': {
                    'first_note_string': 'bString',
                    'second_note_string': 'highAString', 
                    'third_note_string': 'dString'
                },
                'b - A': {
                    'first_note_string': 'gString',
                    'second_note_string': 'highEString', 
                    'third_note_string': 'AString'
                },
                'a - b': {
                    'first_note_string': 'highAString',
                    'second_note_string': 'BString', 
                    'third_note_string': 'gString'
                },
                'a - g': {
                    'first_note_string': 'highEString',
                    'second_note_string': 'dString', 
                    'third_note_string': 'AString'
                },
                'A - B': {
                    'first_note_string': 'highAString',
                    'second_note_string': 'highEString', 
                    'third_note_string': 'BString'
                },
                'g - E': {
                    'first_note_string': 'lowBString',
                    'second_note_string': 'AString', 
                    'third_note_string': 'dString'
                },
                'A - lowB': {
                    'first_note_string': 'highEString',
                    'second_note_string': 'lowBString', 
                    'third_note_string': 'AString'
                }
            }
        }

        # Find all ChordNotes
        chord_notes = ChordNotes.objects.filter(
            category__category_name__in=['Chords', 'Spread Triads'],
            range__in=triad_ranges,
            fourth_note__isnull=True  # Only 3-note chords
        )

        updated_count = 0
        for chord in chord_notes:
            # Get the specific mapping for this category and range
            mapping = string_mappings.get(chord.category.category_name, {}).get(chord.range)
            
            if mapping:
                # Update fields if not already set
                needs_save = False
                for field, value in mapping.items():
                    current_value = getattr(chord, field)
                    if current_value is None or current_value == '':
                        setattr(chord, field, value)
                        needs_save = True
                
                if needs_save:
                    chord.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'Updated {chord.category.category_name} {chord.chord_name} Triad in {chord.range} with string assignments'
                    ))

        self.stdout.write(self.style.SUCCESS(
            f'Successfully updated {updated_count} Triads with advanced string assignments'
        ))
