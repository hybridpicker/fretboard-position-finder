"""
Management command to create V-System seventh chords.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from positionfinder.models_chords import ChordNotes, ChordPosition

class Command(BaseCommand):
    help = 'Create V-System seventh chords'

    def add_arguments(self, parser):
        parser.add_argument(
            '--v-system',
            type=str,
            default='all',
            help='V-System to generate (v1, v2, or all)',
        )
        
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing V-System chords before generating new ones',
        )

    def handle(self, *args, **options):
        v_system = options['v_system'].lower()
        clean = options['clean']
        
        # Clean existing V-System chords if requested
        if clean:
            self.stdout.write('Cleaning existing V-System chords...')
            try:
                with transaction.atomic():
                    # Delete chord positions first (due to foreign key)
                    from django.db.models import Q
                    positions_deleted = ChordPosition.objects.filter(
                        notes_name__type_name__in=['V1', 'V2']
                    ).delete()[0]
                    
                    # Now delete the chords
                    chords_deleted = ChordNotes.objects.filter(
                        type_name__in=['V1', 'V2']
                    ).delete()[0]
                    
                    self.stdout.write(f'Deleted {positions_deleted} positions and {chords_deleted} chords')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error during cleanup: {e}'))
                return
        
        # Create V-System seventh chords
        try:
            # Seventh chord types - the core of Ted Greene's V-System
            chord_types = {
                "Major 7": [0, 4, 7, 11],        # Root, Major 3rd, Perfect 5th, Major 7th
                "Dominant 7": [0, 4, 7, 10],     # Root, Major 3rd, Perfect 5th, Minor 7th
                "Minor 7": [0, 3, 7, 10],        # Root, Minor 3rd, Perfect 5th, Minor 7th
                "Minor 7b5": [0, 3, 6, 10],      # Root, Minor 3rd, Diminished 5th, Minor 7th
                "MinMaj 7": [0, 3, 7, 11],       # Root, Minor 3rd, Perfect 5th, Major 7th
            }
            
            # Define string sets - top 4 strings is common for V-System voicings
            string_sets = [
                ("e-d", ["eString", "bString", "gString", "dString"]),  # Top 4 strings (standard) - Corrected range name
                ("d-e", ["dString", "gString", "bString", "eString"]),  # Middle 4 strings - Corrected range name
            ]
            
            total_created = 0
            
            # For each root note (0-11)
            for root in range(12):
                self.stdout.write(f"Creating chords for root {root}...")
                
                # For each chord type
                for chord_name, intervals in chord_types.items():
                    self.stdout.write(f"  Creating {chord_name} chords...")
                    
                    # For each string set
                    for range_name, strings in string_sets:
                        # For V1 (close position)
                        if v_system in ['v1', 'all']:
                            try:
                                # Create V1 (close position) seventh chord
                                # Sort notes to ensure they're in close position
                                notes = [(root + interval) % 12 for interval in intervals]
                                notes.sort()
                                
                                # Create chord in database
                                chord = ChordNotes.objects.create(
                                    category_id=3,  # Chords category
                                    type_name='V1',
                                    chord_name=chord_name,
                                    range=range_name,
                                    tonal_root=root,
                                    first_note=notes[0],
                                    first_note_string=strings[0],
                                    second_note=notes[1],
                                    second_note_string=strings[1],
                                    third_note=notes[2],
                                    third_note_string=strings[2],
                                    fourth_note=notes[3],
                                    fourth_note_string=strings[3],
                                )
                                
                                # Create positions
                                # self.create_positions(chord) # Position creation handled by model logic
                                total_created += 1
                                
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f"    Error creating V1 {chord_name} for root {root}: {e}"))
                        
                        # For V2 (drop-2)
                        if v_system in ['v2', 'all']:
                            try:
                                # Create V2 (drop-2) seventh chord
                                notes = [(root + interval) % 12 for interval in intervals]
                                notes.sort()  # Get in close position first
                                
                                # For drop-2, drop the second highest note
                                drop_note = notes[2]  # The second highest note
                                notes.remove(drop_note)
                                # Insert at beginning to maintain sorted order
                                notes.insert(0, (drop_note - 12) % 12)
                                
                                # Create chord in database
                                chord = ChordNotes.objects.create(
                                    category_id=3,  # Chords category
                                    type_name='V2',
                                    chord_name=chord_name,
                                    range=range_name,
                                    tonal_root=root,
                                    first_note=notes[0],
                                    first_note_string=strings[0],
                                    second_note=notes[1],
                                    second_note_string=strings[1],
                                    third_note=notes[2],
                                    third_note_string=strings[2],
                                    fourth_note=notes[3],
                                    fourth_note_string=strings[3],
                                )
                                
                                # Create positions
                                self.create_positions(chord)
                                total_created += 1
                                
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f"    Error creating V2 {chord_name} for root {root}: {e}"))
            
            self.stdout.write(self.style.SUCCESS(f"Successfully created {total_created} V-System seventh chords"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
    
    # def create_positions(self, chord):
    #     """Create positions for a chord."""
    #     # Create basic position (no transposition)
    #     ChordPosition.objects.create(
    #         notes_name_id=chord.id,
    #         inversion_order='Basic Position',
    #         first_note=0,
    #         second_note=0,
    #         third_note=0,
    #         fourth_note=0,
    #     )
        
    #     # Create first inversion
    #     first_notes = self.calculate_intervals(chord)
    #     ChordPosition.objects.create(
    #         notes_name_id=chord.id,
    #         inversion_order='First Inversion',
    #         first_note=first_notes[0],
    #         second_note=first_notes[1],
    #         third_note=first_notes[2],
    #         fourth_note=first_notes[3],
    #     )
        
    #     # Create second inversion
    #     second_notes = [
    #         first_notes[0] + first_notes[1],
    #         first_notes[1] + first_notes[2],
    #         first_notes[2] + first_notes[3],
    #         first_notes[3] + first_notes[0]
    #     ]
    #     ChordPosition.objects.create(
    #         notes_name_id=chord.id,
    #         inversion_order='Second Inversion',
    #         first_note=second_notes[0],
    #         second_note=second_notes[1],
    #         third_note=second_notes[2],
    #         fourth_note=second_notes[3],
    #     )
        
    #     # Create third inversion
    #     third_notes = [
    #         second_notes[0] + second_notes[1],
    #         second_notes[1] + second_notes[2],
    #         second_notes[2] + second_notes[3],
    #         second_notes[3] + second_notes[0]
    #     ]
    #     ChordPosition.objects.create(
    #         notes_name_id=chord.id,
    #         inversion_order='Third Inversion',
    #         first_note=third_notes[0],
    #         second_note=third_notes[1],
    #         third_note=third_notes[2],
    #         fourth_note=third_notes[3],
    #     )
    
    # def calculate_intervals(self, chord):
    #     """Calculate the intervals between notes in a chord."""
    #     # Get the notes
    #     notes = [
    #         chord.first_note,
    #         chord.second_note,
    #         chord.third_note,
    #         chord.fourth_note
    #     ]
        
    #     # Calculate intervals
    #     intervals = []
    #     for i in range(3):
    #         interval = notes[i+1] - notes[i]
    #         # If negative, add an octave
    #         if interval < 0:
    #             interval += 12
    #         intervals.append(interval)
        
    #     # Last interval (from last note back to first)
    #     interval = notes[0] - notes[3]
    #     # If negative, add an octave
    #     if interval < 0:
    #         interval += 12
    #     intervals.append(interval)
        
    #     return intervals
