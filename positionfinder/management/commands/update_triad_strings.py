from django.core.management.base import BaseCommand
from positionfinder.models_chords import ChordNotes
from positionfinder.models import NotesCategory

class Command(BaseCommand):
    help = 'Update String for Note in Triads'

    def handle(self, *args, **options):
        # Triad ranges
        triad_ranges = ['e - g', 'b - d', 'd - E', 'g - A', 'e - d', 'b - A', 'a - b', 'a - g', 'A - B', 'g - E']
        
        # Define string mappings for each range
        string_mappings = {
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
            }
        }

        # Find all ChordNotes with appropriate characteristics
        chord_notes = ChordNotes.objects.filter(
            category__category_name='Chords',
            range__in=triad_ranges,
            fourth_note__isnull=True,  # Only triads (3 notes)
            chord_name__in=['Major', 'Minor', 'Diminished', 'Augmented']  # Only triad types
        )

        updated_count = 0
        for chord in chord_notes:
            mapping = string_mappings.get(chord.range)
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
                        f'Updated {chord.chord_name} Triad in {chord.range} with string assignments'
                    ))

        self.stdout.write(self.style.SUCCESS(
            f'Successfully updated {updated_count} Triads with string assignments'
        ))
