from django.core.management.base import BaseCommand
from positionfinder.models_chords import ChordNotes
from positionfinder.models import NotesCategory

class Command(BaseCommand):
    help = 'Final Verification of Triad Categories'

    def handle(self, *args, **options):
        # Check Triads category
        triads_category = NotesCategory.objects.get(category_name='Triads')
        
        # Check specific ranges
        ranges_to_check = ['a - b', 'e - d']
        chord_types = ['Major', 'Minor', 'Diminished', 'Augmented']

        for range_check in ranges_to_check:
            self.stdout.write(f"\nTriads in {range_check} range:")
            for chord_type in chord_types:
                triads = ChordNotes.objects.filter(
                    category=triads_category,
                    range=range_check,
                    chord_name=chord_type,
                    fourth_note__isnull=True
                )
                
                for triad in triads:
                    self.stdout.write(f"- {chord_type}")
                    self.stdout.write(f"  First Note String: {triad.first_note_string}")
                    self.stdout.write(f"  Second Note String: {triad.second_note_string}")
                    self.stdout.write(f"  Third Note String: {triad.third_note_string}")
                    self.stdout.write("-" * 50)
