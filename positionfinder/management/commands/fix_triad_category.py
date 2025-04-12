from django.core.management.base import BaseCommand
from django.db.models import Q
from positionfinder.models_chords import ChordNotes
from positionfinder.models import NotesCategory

class Command(BaseCommand):
    help = 'Move specific triads to Spread Triads category'

    def handle(self, *args, **options):
        # Create Spread Triads category if it doesn't exist
        spread_triads_category, created = NotesCategory.objects.get_or_create(
            category_name='Spread Triads'
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created new Spread Triads category'))
        
        # Find chords in a - b range with standard voicing
        chords_to_move = ChordNotes.objects.filter(
            category__category_name='Chords',
            range='a - b',
            fourth_note__isnull=True,
            first_note_string='bString',
            second_note_string='gString',
            third_note_string='AString'
        )

        updated_count = 0
        for chord in chords_to_move:
            # Update the category
            chord.category = spread_triads_category
            
            # Modify string assignments for spread voicing
            chord.first_note_string = 'highAString'
            chord.second_note_string = 'BString'
            chord.third_note_string = 'gString'
            
            chord.save()
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(
                f'Moved {chord.chord_name} triad in {chord.range} to Spread Triads'
            ))

        # Apply the same logic to other ranges where standard triad might need to be a spread triad
        spread_ranges = ['a - b', 'e - d']
        for spread_range in spread_ranges:
            spread_chords = ChordNotes.objects.filter(
                category__category_name='Chords',
                range=spread_range,
                fourth_note__isnull=True
            )
            
            for chord in spread_chords:
                # Customize spread voicing for each chord type
                if spread_range == 'a - b':
                    chord.first_note_string = 'highAString'
                    chord.second_note_string = 'BString'
                    chord.third_note_string = 'gString'
                elif spread_range == 'e - d':
                    chord.first_note_string = 'bString'
                    chord.second_note_string = 'highAString'
                    chord.third_note_string = 'dString'
                
                chord.category = spread_triads_category
                chord.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Moved {chord.chord_name} triad in {chord.range} to Spread Triads'
                ))

        self.stdout.write(self.style.SUCCESS(
            f'Successfully moved {updated_count} triads to Spread Triads category'
        ))
