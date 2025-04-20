from django.core.management.base import BaseCommand
from django.db.models import Q
from positionfinder.models_chords import ChordNotes
from positionfinder.models import NotesCategory

class Command(BaseCommand):
    help = 'Debug Triad and Spread Triad Categories'

    def handle(self, *args, **options):
        # Print out all categories
        self.stdout.write("Categories:")
        categories = NotesCategory.objects.all()
        for category in categories:
            self.stdout.write(f"- {category.category_name}")

        # Check chord notes
        self.stdout.write("\nChord Notes Analysis:")
        
        # Get all relevant chord notes
        chord_notes = ChordNotes.objects.filter(
            fourth_note__isnull=True,  # 3-note chords
            chord_name__in=['Major', 'Minor', 'Diminished', 'Augmented']
        )

        # Group by category
        category_analysis = chord_notes.values('category__category_name').distinct()
        
        self.stdout.write("\nChord Notes by Category:")
        for cat in category_analysis:
            category_count = chord_notes.filter(category__category_name=cat['category__category_name']).count()
            self.stdout.write(f"- {cat['category__category_name']}: {category_count} chords")

        # Detailed breakdown of ranges
        self.stdout.write("\nChord Notes by Range:")
        ranges = chord_notes.values('range').distinct()
        for r in ranges:
            range_count = chord_notes.filter(range=r['range']).count()
            self.stdout.write(f"- {r['range']}: {range_count} chords")
