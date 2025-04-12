from django.core.management.base import BaseCommand
from django.db.models import Q
from positionfinder.models_chords import ChordNotes
from positionfinder.models import NotesCategory

class Command(BaseCommand):
    help = 'Audit Triad String Assignments'

    def handle(self, *args, **options):
        # Specific query matching your error context
        chord_notes = ChordNotes.objects.filter(
            Q(category__category_name='Chords') | Q(category__category_name='Spread Triads'),
            range='a - b',
            chord_name='Major',
            fourth_note__isnull=True
        )

        self.stdout.write("\nAudit Results:")
        for chord in chord_notes:
            self.stdout.write(f"Chord Details:")
            self.stdout.write(f"Category: {chord.category.category_name}")
            self.stdout.write(f"Chord Name: {chord.chord_name}")
            self.stdout.write(f"Range: {chord.range}")
            self.stdout.write(f"First Note String: {chord.first_note_string}")
            self.stdout.write(f"Second Note String: {chord.second_note_string}")
            self.stdout.write(f"Third Note String: {chord.third_note_string}")
            self.stdout.write("-" * 50)

        # Check for categories and ranges
        self.stdout.write("\nCategories:")
        categories = NotesCategory.objects.all()
        for cat in categories:
            self.stdout.write(f"- {cat.category_name}")

        self.stdout.write("\nChord Ranges:")
        ranges = ChordNotes.objects.filter(
            Q(category__category_name='Chords') | Q(category__category_name='Spread Triads')
        ).values_list('range', flat=True).distinct()
        for r in ranges:
            self.stdout.write(f"- {r}")
