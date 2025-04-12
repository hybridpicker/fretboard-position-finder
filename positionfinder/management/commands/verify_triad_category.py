from django.core.management.base import BaseCommand
from positionfinder.models_chords import ChordNotes
from positionfinder.models import NotesCategory

class Command(BaseCommand):
    help = 'Verify Triad Categorization'

    def handle(self, *args, **options):
        # Get Spread Triads category
        spread_triads_category = NotesCategory.objects.get(category_name='Spread Triads')
        
        # Check specific ranges
        ranges_to_check = ['a - b', 'e - d']
        
        for range_check in ranges_to_check:
            spread_triads = ChordNotes.objects.filter(
                category=spread_triads_category,
                range=range_check,
                fourth_note__isnull=True
            )
            
            self.stdout.write(f"\nSpread Triads in {range_check} range:")
            for triad in spread_triads:
                self.stdout.write(f"- {triad.chord_name}")
                self.stdout.write(f"  First Note String: {triad.first_note_string}")
                self.stdout.write(f"  Second Note String: {triad.second_note_string}")
                self.stdout.write(f"  Third Note String: {triad.third_note_string}")
                self.stdout.write("-" * 50)
