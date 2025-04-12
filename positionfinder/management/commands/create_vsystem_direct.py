"""
Management command to directly create V-System chords in the database.
This bypasses the create_chord and create_eight_string_ranges functions
which cause issues with V-System chords.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from positionfinder.models_chords import ChordNotes, ChordPosition
from positionfinder.v_system_generator import VoicingSystem

class Command(BaseCommand):
    help = 'Directly create V-System voicings in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--v-system',
            type=str,
            default='v1',
            help='V-System to generate (v1, v2)',
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
        
        # Create V-System chords directly in the database
        try:
            # We'll use shorter string identifiers due to the field length limitation
            chord_types = {
                "Major": [0, 4, 7],             # Root, Major 3rd, Perfect 5th
                "Minor": [0, 3, 7],             # Root, Minor 3rd, Perfect 5th
                "Maj7": [0, 4, 7, 11],          # Root, Major 3rd, Perfect 5th, Major 7th
                "Dom7": [0, 4, 7, 10],          # Root, Major 3rd, Perfect 5th, Minor 7th
                "Min7": [0, 3, 7, 10],          # Root, Minor 3rd, Perfect 5th, Minor 7th
            }
            
            v_system_type = 'V1' if v_system == 'v1' else 'V2'
            
            # Create one chord of each type for all roots
            total_created = 0
            
            # String set for short range name (e-g is 5 chars)
            range_name = 'e-g'
            
            for chord_type, intervals in chord_types.items():
                self.stdout.write(f'Creating {v_system_type} chords for {chord_type}...')
                
                for root in range(12):  # 0-11 for all chromatic notes
                    self.stdout.write(f'  Creating chord for root {root}...')
                    try:
                        with transaction.atomic():
                            if v_system_type == 'V1':
                                # For V1, arrange notes in close position
                                if len(intervals) == 3:  # Triad
                                    notes = [(root + interval) % 12 for interval in intervals]
                                    notes.sort()  # Close position
                                    
                                    # Create chord
                                    chord = ChordNotes.objects.create(
                                        category_id=1,  # Default category
                                        type_name=v_system_type,
                                        chord_name=chord_type,
                                        range=range_name,
                                        tonal_root=root,
                                        first_note=notes[0],
                                        first_note_string='eString',
                                        second_note=notes[1],
                                        second_note_string='bString',
                                        third_note=notes[2],
                                        third_note_string='gString',
                                    )
                                else:  # Seventh chord
                                    notes = [(root + interval) % 12 for interval in intervals]
                                    notes.sort()  # Close position
                                    
                                    # Create chord
                                    chord = ChordNotes.objects.create(
                                        category_id=1,  # Default category
                                        type_name=v_system_type,
                                        chord_name=chord_type,
                                        range=range_name,
                                        tonal_root=root,
                                        first_note=notes[0],
                                        first_note_string='eString',
                                        second_note=notes[1],
                                        second_note_string='bString',
                                        third_note=notes[2],
                                        third_note_string='gString',
                                        fourth_note=notes[3],
                                        fourth_note_string='dString',
                                    )
                            else:  # V2
                                # For V2, arrange notes in drop-2 voicing
                                if len(intervals) == 3:  # Triad
                                    notes = [(root + interval) % 12 for interval in intervals]
                                    notes.sort()  # Close position
                                    
                                    # For drop-2, take the second highest note down an octave
                                    drop_note = notes[1]
                                    drop2_notes = [notes[0], notes[2]]
                                    drop2_notes.insert(0, (drop_note - 12) % 12)
                                    
                                    # Create chord
                                    chord = ChordNotes.objects.create(
                                        category_id=1,  # Default category
                                        type_name=v_system_type,
                                        chord_name=chord_type,
                                        range=range_name,
                                        tonal_root=root,
                                        first_note=drop2_notes[0],
                                        first_note_string='gString',
                                        second_note=drop2_notes[1],
                                        second_note_string='bString',
                                        third_note=drop2_notes[2],
                                        third_note_string='eString',
                                    )
                                else:  # Seventh chord
                                    notes = [(root + interval) % 12 for interval in intervals]
                                    notes.sort()  # Close position
                                    
                                    # For drop-2, take the second highest note down an octave
                                    drop_note = notes[2]
                                    drop2_notes = [notes[0], notes[1], notes[3]]
                                    drop2_notes.insert(0, (drop_note - 12) % 12)
                                    
                                    # Create chord
                                    chord = ChordNotes.objects.create(
                                        category_id=1,  # Default category
                                        type_name=v_system_type,
                                        chord_name=chord_type,
                                        range=range_name,
                                        tonal_root=root,
                                        first_note=drop2_notes[0],
                                        first_note_string='dString',
                                        second_note=drop2_notes[1],
                                        second_note_string='gString',
                                        third_note=drop2_notes[2],
                                        third_note_string='bString',
                                        fourth_note=drop2_notes[3],
                                        fourth_note_string='eString',
                                    )
                            
                            # Create basic position
                            ChordPosition.objects.create(
                                notes_name_id=chord.id,
                                inversion_order='Basic Position',
                                first_note=0,
                                second_note=0,
                                third_note=0,
                                fourth_note=0 if len(intervals) == 4 else None,
                            )
                            
                            total_created += 1
                            self.stdout.write(f'    Created {chord}')
                            
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'    Error creating chord: {e}'))
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created {total_created} {v_system_type} chords'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
