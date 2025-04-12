from django.core.management.base import BaseCommand
from positionfinder.models_chords import ChordNotes
from positionfinder.models import NotesCategory

class Command(BaseCommand):
    help = 'Diagnose Triads and Spread Triads'

    def handle(self, *args, **options):
        # Print all categories
        self.stdout.write("All Categories:")
        categories = NotesCategory.objects.all()
        for category in categories:
            self.stdout.write(f"- {category.category_name}")

        # Check ChordNotes
        self.stdout.write("\nChordNotes Analysis:")
        # Filter to get potential triads (3 note chords)
        chord_notes = ChordNotes.objects.filter(fourth_note__isnull=True)
        
        self.stdout.write(f"Total 3-note chords: {chord_notes.count()}")
        
        # Group by category and range
        category_ranges = chord_notes.values('category__category_name', 'range').distinct()
        
        self.stdout.write("\nCategory and Range combinations:")
        for item in category_ranges:
            count = chord_notes.filter(
                category__category_name=item['category__category_name'], 
                range=item['range']
            ).count()
            self.stdout.write(f"- {item['category__category_name']} - {item['range']}: {count} chords")

        # Sample triads
        self.stdout.write("\nSample Triads:")
        sample_triads = chord_notes[:5]
        for triad in sample_triads:
            self.stdout.write(f"- {triad.category.category_name} - {triad.chord_name} - {triad.range}")
