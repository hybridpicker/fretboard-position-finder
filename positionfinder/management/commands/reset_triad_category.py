from django.core.management.base import BaseCommand
from django.db.models import Q
from positionfinder.models_chords import ChordNotes
from positionfinder.models import NotesCategory

class Command(BaseCommand):
    help = 'Reset Triad Categories and Voicings'

    def handle(self, *args, **options):
        # Ensure Triads category exists
        triads_category, created = NotesCategory.objects.get_or_create(
            category_name='Triads'
        )
        
        # Find existing Spread Triads category
        try:
            spread_triads_category = NotesCategory.objects.get(category_name='Spread Triads')
        except NotesCategory.DoesNotExist:
            spread_triads_category = NotesCategory.objects.create(category_name='Spread Triads')

        # Ranges to process
        ranges_to_reset = ['a - b', 'e - d']
        chord_types = ['Major', 'Minor', 'Diminished', 'Augmented']

        for range_check in ranges_to_reset:
            for chord_type in chord_types:
                # Find chords in Spread Triads
                chords_to_move = ChordNotes.objects.filter(
                    category=spread_triads_category,
                    range=range_check,
                    chord_name=chord_type,
                    fourth_note__isnull=True
                )

                for chord in chords_to_move:
                    # Move back to Triads category with standard voicing
                    chord.category = triads_category
                    
                    # Reset string assignments based on range
                    if range_check == 'a - b':
                        chord.first_note_string = 'bString'
                        chord.second_note_string = 'gString'
                        chord.third_note_string = 'AString'
                    elif range_check == 'e - d':
                        chord.first_note_string = 'dString'
                        chord.second_note_string = 'gString'
                        chord.third_note_string = 'bString'
                    
                    chord.save()
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'Moved {chord_type} Triad in {range_check} back to Triads category'
                    ))

        self.stdout.write(self.style.SUCCESS(
            'Completed resetting triad categories'
        ))
