"""
Management command to check V-System voicings in the database.
"""
from django.core.management.base import BaseCommand
from positionfinder.models_chords import ChordNotes

class Command(BaseCommand):
    help = 'Check V-System voicings in the database'

    def handle(self, *args, **options):
        # Check for V-System types
        v_system_types = ChordNotes.objects.filter(type_name__in=['V1', 'V2']).values_list('type_name', flat=True).distinct()
        self.stdout.write(f"V-System types in database: {list(v_system_types)}")
        
        # Count V1 and V2 chords
        v1_count = ChordNotes.objects.filter(type_name='V1').count()
        v2_count = ChordNotes.objects.filter(type_name='V2').count()
        self.stdout.write(f"V1 chord count: {v1_count}")
        self.stdout.write(f"V2 chord count: {v2_count}")
        
        # Check chord names for V1
        if v1_count > 0:
            v1_chord_names = ChordNotes.objects.filter(type_name='V1').values_list('chord_name', flat=True).distinct()
            self.stdout.write(f"V1 chord names: {list(v1_chord_names)}")
            
            # Check ranges for V1
            v1_ranges = ChordNotes.objects.filter(type_name='V1').values_list('range', flat=True).distinct()
            self.stdout.write(f"V1 ranges: {list(v1_ranges)}")
            
            # Sample a V1 chord
            sample_v1 = ChordNotes.objects.filter(type_name='V1').first()
            if sample_v1:
                self.stdout.write(f"Sample V1 chord: {sample_v1}")
                self.stdout.write(f"  - range: {sample_v1.range}")
                self.stdout.write(f"  - chord_name: {sample_v1.chord_name}")
                self.stdout.write(f"  - tonal_root: {sample_v1.tonal_root}")
                
                # Check positions for this chord
                from positionfinder.models_chords import ChordPosition
                positions = ChordPosition.objects.filter(notes_name_id=sample_v1.id)
                self.stdout.write(f"  - positions: {positions.count()}")
        
        # List all unique type_name values in the database
        all_types = ChordNotes.objects.values_list('type_name', flat=True).distinct()
        self.stdout.write(f"All types in database: {list(all_types)}")
