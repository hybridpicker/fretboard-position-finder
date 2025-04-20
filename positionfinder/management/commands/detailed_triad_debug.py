from django.core.management.base import BaseCommand
from django.db.models import Q
from positionfinder.models_chords import ChordNotes
from positionfinder.models import NotesCategory

class Command(BaseCommand):
    help = 'Detailed Debug of Triad String Assignments'

    def handle(self, *args, **options):
        # Get categories
        categories = NotesCategory.objects.all()
        self.stdout.write("Categories:")
        for cat in categories:
            self.stdout.write(f"- {cat.category_name}")

        # Find chord notes
        chord_notes = ChordNotes.objects.filter(
            category__category_name__in=['Chords', 'Spread Triads'],
            fourth_note__isnull=True  # Only 3-note chords
        )

        self.stdout.write("\nChord Notes Analysis:")
        for chord in chord_notes:
            self.stdout.write(f"\nChord Details:")
            self.stdout.write(f"Category: {chord.category.category_name}")
            self.stdout.write(f"Chord Name: {chord.chord_name}")
            self.stdout.write(f"Range: {chord.range}")
            self.stdout.write(f"First Note String: {chord.first_note_string}")
            self.stdout.write(f"Second Note String: {chord.second_note_string}")
            self.stdout.write(f"Third Note String: {chord.third_note_string}")
            self.stdout.write("-" * 50)
