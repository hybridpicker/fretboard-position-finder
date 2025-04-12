from django.core.management.base import BaseCommand
from django.db.models import Q
from positionfinder.models_chords import ChordNotes, ChordPosition
from positionfinder.models import NotesCategory
from positionfinder.string_choices import StringChoicesField
from positionfinder.notes_choices import ChordChoicesField

class Command(BaseCommand):
    help = 'Comprehensive Triad Debugging'

    def handle(self, *args, **options):
        # Check if Triads category exists
        triads_categories = NotesCategory.objects.filter(category_name='Triads')
        self.stdout.write("\nTriads Categories:")
        for cat in triads_categories:
            self.stdout.write(f"- {cat.category_name}")

        # Find chords matching the specific conditions
        chords = ChordNotes.objects.filter(
            Q(category__category_name='Triads') | 
            Q(category__category_name='Spread Triads'),
            range='a - b',
            chord_name='Major',
            fourth_note__isnull=True
        )

        self.stdout.write("\nMatching Chords:")
        for chord in chords:
            self.stdout.write(f"Chord Details:")
            self.stdout.write(f"Category: {chord.category.category_name}")
            self.stdout.write(f"Chord Name: {chord.chord_name}")
            self.stdout.write(f"Range: {chord.range}")
            self.stdout.write(f"First Note String: {chord.first_note_string}")
            self.stdout.write(f"Second Note String: {chord.second_note_string}")
            self.stdout.write(f"Third Note String: {chord.third_note_string}")
            
            # Check positions
            positions = ChordPosition.objects.filter(notes_name=chord)
            self.stdout.write(f"Positions count: {positions.count()}")
            for pos in positions:
                self.stdout.write(f"Position Details:")
                self.stdout.write(f"Inversion Order: {pos.inversion_order}")
                self.stdout.write(f"First Note: {pos.first_note}")
                self.stdout.write(f"Second Note: {pos.second_note}")
                self.stdout.write(f"Third Note: {pos.third_note}")
            
            self.stdout.write("-" * 50)

        # Diagnose Triads creation
        self.stdout.write("\nDiagnosing Triad Creation:")
        
        # Find or create Triads category if not exists
        triads_category, created = NotesCategory.objects.get_or_create(
            category_name='Triads'
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created Triads category'))
        
        # Create a sample Major Triad in a - b range if not exists
        existing_chord = ChordNotes.objects.filter(
            category=triads_category,
            range='a - b',
            chord_name='Major',
            fourth_note__isnull=True
        ).first()
        
        if not existing_chord:
            new_chord = ChordNotes.objects.create(
                category=triads_category,
                range='a - b',
                chord_name='Major',
                first_note=0,  # Root
                second_note=4,  # Major Third
                third_note=7,   # Perfect Fifth
                first_note_string='bString',
                second_note_string='gString',
                third_note_string='AString'
            )
            
            # Create a basic position
            ChordPosition.objects.create(
                notes_name=new_chord,
                inversion_order='Basic Position',
                first_note=0,
                second_note=0,
                third_note=0
            )
            
            self.stdout.write(self.style.SUCCESS(
                f'Created new Major Triad in a - b range: {new_chord.id}'
            ))
        else:
            self.stdout.write(f"Existing chord found: {existing_chord.id}")
