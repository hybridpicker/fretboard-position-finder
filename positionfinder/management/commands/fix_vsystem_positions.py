"""
Management command to fix V-System chord positions.
This command focuses on creating proper inversions and positions for V-System chords.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from positionfinder.models_chords import ChordNotes, ChordPosition
import math

class Command(BaseCommand):
    help = 'Fix V-System chord positions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='all',
            help='V-System type to fix (v1, v2, or all)',
        )

    def handle(self, *args, **options):
        v_system_type = options['type'].lower()
        
        # Set the types to fix
        types_to_fix = []
        if v_system_type == 'all':
            types_to_fix = ['V1', 'V2']
        elif v_system_type == 'v1':
            types_to_fix = ['V1']
        elif v_system_type == 'v2':
            types_to_fix = ['V2']
        else:
            self.stdout.write(self.style.ERROR(f"Invalid type: {v_system_type}. Use 'v1', 'v2', or 'all'."))
            return
            
        # Fix V-System chord positions
        self.stdout.write(f"Fixing positions for {', '.join(types_to_fix)} chords...")
        
        # Count chords that need fixing
        chord_count = ChordNotes.objects.filter(type_name__in=types_to_fix).count()
        self.stdout.write(f"Found {chord_count} chords to fix.")
        
        # Track progress
        fixed_count = 0
        error_count = 0
        
        # Process each chord
        for chord in ChordNotes.objects.filter(type_name__in=types_to_fix):
            try:
                # Skip chords that don't have all four notes defined
                if None in (chord.first_note, chord.second_note, chord.third_note, chord.fourth_note):
                    self.stdout.write(self.style.WARNING(f"Skipping chord {chord.id} ({chord.chord_name}) - missing notes"))
                    continue
                
                # Delete existing positions for this chord
                positions_deleted = ChordPosition.objects.filter(notes_name_id=chord.id).delete()[0]
                
                # Create proper positions
                self._create_positions(chord)
                
                # Update progress
                fixed_count += 1
                if fixed_count % 10 == 0:
                    self.stdout.write(f"Fixed {fixed_count}/{chord_count} chords...")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fixing chord {chord.id}: {e}"))
                error_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f"Fixed positions for {fixed_count} chords with {error_count} errors."))
    
    def _create_positions(self, chord):
        """Create proper positions for a chord."""
        # Extract the notes and ensure they're in numerical order
        notes = [
            chord.first_note,
            chord.second_note,
            chord.third_note,
            chord.fourth_note
        ]
        
        original_notes = notes.copy()
        chord_type = chord.type_name  # 'V1' or 'V2'
        
        # For V1 (close position), notes should already be sorted
        if chord_type == 'V1':
            # Sort notes in ascending order
            sorted_notes = sorted(notes)
            
            # Create Basic Position (root position)
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Basic Position',
                first_note=0,
                second_note=0,
                third_note=0,
                fourth_note=0
            )
            
            # First Inversion (root moves to top)
            # Calculate intervals between adjacent notes
            intervals = self._calculate_intervals(sorted_notes)
            
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='First Inversion',
                first_note=intervals[0],  # Distance from 1st to 2nd note
                second_note=intervals[1],  # Distance from 2nd to 3rd note
                third_note=intervals[2],   # Distance from 3rd to 4th note
                fourth_note=intervals[3]   # Distance from 4th back to 1st (next octave)
            )
            
            # Second Inversion (first two notes move to top)
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Second Inversion',
                first_note=intervals[0] + intervals[1],
                second_note=intervals[1] + intervals[2],
                third_note=intervals[2] + intervals[3],
                fourth_note=intervals[3] + intervals[0]
            )
            
            # Third Inversion (first three notes move to top)
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Third Inversion',
                first_note=intervals[0] + intervals[1] + intervals[2],
                second_note=intervals[1] + intervals[2] + intervals[3],
                third_note=intervals[2] + intervals[3] + intervals[0],
                fourth_note=intervals[3] + intervals[0] + intervals[1]
            )
            
        # For V2 (drop-2), notes should be in drop-2 order
        elif chord_type == 'V2':
            # Notes in a drop-2 voicing should have the 2nd highest note dropped down an octave
            # First, let's find what the close position would be
            sorted_notes = sorted(notes)
            
            # In V2, the second-highest note is dropped down an octave
            # So the ordering should be: dropped note, lowest note, second lowest, highest
            drop2_notes = sorted_notes.copy()
            second_highest = drop2_notes[2]  # Third position (index 2) is second highest
            drop2_notes.remove(second_highest)
            drop2_notes.insert(0, (second_highest - 12) % 12)  # Drop by octave and insert at start
            
            # Create Basic Position (root position for drop-2)
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Basic Position',
                first_note=0,
                second_note=0,
                third_note=0,
                fourth_note=0
            )
            
            # Calculate intervals for drop-2 voicing
            intervals = self._calculate_intervals(drop2_notes)
            
            # First Inversion
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='First Inversion',
                first_note=intervals[0],
                second_note=intervals[1],
                third_note=intervals[2],
                fourth_note=intervals[3]
            )
            
            # Second Inversion
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Second Inversion',
                first_note=intervals[0] + intervals[1],
                second_note=intervals[1] + intervals[2],
                third_note=intervals[2] + intervals[3],
                fourth_note=intervals[3] + intervals[0]
            )
            
            # Third Inversion
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Third Inversion',
                first_note=intervals[0] + intervals[1] + intervals[2],
                second_note=intervals[1] + intervals[2] + intervals[3],
                third_note=intervals[2] + intervals[3] + intervals[0],
                fourth_note=intervals[3] + intervals[0] + intervals[1]
            )
    
    def _calculate_intervals(self, notes):
        """Calculate intervals between notes of a chord."""
        intervals = []
        
        # Calculate intervals between adjacent notes
        for i in range(len(notes) - 1):
            interval = notes[i + 1] - notes[i]
            # Ensure positive interval (if negative, add 12 to get within an octave)
            if interval < 0:
                interval += 12
            intervals.append(interval)
        
        # Calculate interval from highest note back to lowest (completing the cycle)
        # This will be the distance from the highest note to the lowest note in the next octave
        last_interval = notes[0] + 12 - notes[-1]
        # Ensure positive interval (if negative, add 12 to get within an octave)
        if last_interval < 0:
            last_interval += 12
        intervals.append(last_interval)
        
        return intervals
