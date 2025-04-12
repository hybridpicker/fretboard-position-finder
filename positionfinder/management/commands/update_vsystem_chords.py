"""
Management command to update existing V-System chord records.
"""
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from positionfinder.models_chords import ChordNotes, ChordPosition

class Command(BaseCommand):
    help = 'Update existing V-System chord records'

    def handle(self, *args, **options):
        # First, let's check if we have any V-System chords
        v1_count = ChordNotes.objects.filter(type_name='V1').count()
        v2_count = ChordNotes.objects.filter(type_name='V2').count()
        
        self.stdout.write(f"Found {v1_count} V1 chords and {v2_count} V2 chords")
        
        if v1_count == 0 and v2_count == 0:
            self.stdout.write("No V-System chords found, creating them...")
            self.create_basic_vsystem_chords()
        else:
            self.stdout.write("Updating existing V-System chords...")
            self.update_vsystem_chords()
    
    def create_basic_vsystem_chords(self):
        """Create basic V-System chords directly in the database."""
        try:
            # V1 Major 7 chord for C
            chord = ChordNotes.objects.create(
                category_id=3,  # Chords category
                type_name='V1',
                chord_name='Maj7',
                range='e-g',
                tonal_root=0,  # C
                first_note=0,   # C
                first_note_string='dString',
                second_note=4,  # E
                second_note_string='gString',
                third_note=7,   # G
                third_note_string='bString',
                fourth_note=11, # B
                fourth_note_string='eString',
            )
            
            # Create positions
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Basic Position',
                first_note=0,
                second_note=0,
                third_note=0,
                fourth_note=0,
            )
            
            # Calculate intervals for inversions
            w = 4  # C to E
            x = 3  # E to G
            y = 4  # G to B
            z = 1  # B to C (next octave)
            
            # Create first inversion
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='First Inversion',
                first_note=w,
                second_note=x,
                third_note=y,
                fourth_note=z,
            )
            
            # Create second inversion
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Second Inversion',
                first_note=w+x,
                second_note=x+y,
                third_note=y+z,
                fourth_note=z+w,
            )
            
            # Create third inversion
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Third Inversion',
                first_note=w+x+y,
                second_note=x+y+z,
                third_note=y+z+w,
                fourth_note=z+w+x,
            )
            
            self.stdout.write(f"Created V1 C Major 7 chord: {chord}")
            
            # V2 Dominant 7 chord for C
            chord = ChordNotes.objects.create(
                category_id=3,  # Chords category
                type_name='V2',
                chord_name='Dom7',
                range='e-g',
                tonal_root=0,  # C
                first_note=7,   # G (drop-2 voicing, second highest note dropped down)
                first_note_string='dString',
                second_note=0,  # C
                second_note_string='gString',
                third_note=4,   # E
                third_note_string='bString',
                fourth_note=10, # Bb (minor 7th)
                fourth_note_string='eString',
            )
            
            # Create positions
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Basic Position',
                first_note=0,
                second_note=0,
                third_note=0,
                fourth_note=0,
            )
            
            # Calculate intervals for inversions
            w = 5  # G to C
            x = 4  # C to E
            y = 6  # E to Bb
            z = 9  # Bb to G (next octave)
            
            # Create first inversion
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='First Inversion',
                first_note=w,
                second_note=x,
                third_note=y,
                fourth_note=z,
            )
            
            # Create second inversion
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Second Inversion',
                first_note=w+x,
                second_note=x+y,
                third_note=y+z,
                fourth_note=z+w,
            )
            
            # Create third inversion
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Third Inversion',
                first_note=w+x+y,
                second_note=x+y+z,
                third_note=y+z+w,
                fourth_note=z+w+x,
            )
            
            self.stdout.write(f"Created V2 C Dominant 7 chord: {chord}")
            
            self.stdout.write(self.style.SUCCESS("Successfully created V-System chords"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating V-System chords: {e}"))
    
    def update_vsystem_chords(self):
        """Update existing V-System chord records."""
        try:
            with transaction.atomic():
                # Fix any issues with existing V-System chords
                v_system_chords = ChordNotes.objects.filter(type_name__in=['V1', 'V2'])
                
                for chord in v_system_chords:
                    # Make sure we use short strings for range and chord_name
                    if len(chord.range) > 8:
                        chord.range = 'e-g'  # Use a short range name
                        
                    # Keep proper chord names that are compatible with the chord function generator
                    # The full names are more descriptive and help distinguish Major 7 from Dominant 7
                    if chord.chord_name == 'Maj7':
                        chord.chord_name = 'Major 7'
                    elif chord.chord_name == 'Maj7#5':
                        chord.chord_name = 'Major 7(#5)'
                    elif chord.chord_name == 'Maj7b5':
                        chord.chord_name = 'Major 7(b5)'
                    elif chord.chord_name == 'Dom7':
                        chord.chord_name = 'Dominant 7'
                    elif chord.chord_name == 'Dom7#5':
                        chord.chord_name = 'Dominant 7(#5)'
                    elif chord.chord_name == 'Dom7b5':
                        chord.chord_name = 'Dominant 7(b5)'
                    elif chord.chord_name == 'Min7':
                        chord.chord_name = 'Minor 7'
                    elif chord.chord_name == 'MinMaj7':
                        chord.chord_name = 'MinMaj 7'
                    # If it's a triad, check if we can convert it to a seventh chord
                    elif chord.chord_name == 'Major' and chord.fourth_note is None:
                        # Add a major 7th if possible
                        if chord.first_note is not None and chord.second_note is not None and chord.third_note is not None:
                            # Calculate the major 7th (11 semitones above root)
                            chord.fourth_note = (chord.first_note + 11) % 12
                            # Find an available string for the 4th note
                            available_strings = ['eString', 'bString', 'gString', 'dString', 'AString', 'ELowString']
                            used_strings = [
                                chord.first_note_string, 
                                chord.second_note_string, 
                                chord.third_note_string
                            ]
                            for string in available_strings:
                                if string not in used_strings:
                                    chord.fourth_note_string = string
                                    break
                            chord.chord_name = 'Maj7'
                    elif chord.chord_name == 'Minor' and chord.fourth_note is None:
                        # Add a minor 7th if possible
                        if chord.first_note is not None and chord.second_note is not None and chord.third_note is not None:
                            # Calculate the minor 7th (10 semitones above root)
                            chord.fourth_note = (chord.first_note + 10) % 12
                            # Find an available string for the 4th note
                            available_strings = ['eString', 'bString', 'gString', 'dString', 'AString', 'ELowString']
                            used_strings = [
                                chord.first_note_string, 
                                chord.second_note_string, 
                                chord.third_note_string
                            ]
                            for string in available_strings:
                                if string not in used_strings:
                                    chord.fourth_note_string = string
                                    break
                            chord.chord_name = 'Min7'
                        
                    chord.save()
                    
                    # Make sure positions exist
                    if not ChordPosition.objects.filter(notes_name_id=chord.id).exists():
                        # Create basic position
                        ChordPosition.objects.create(
                            notes_name_id=chord.id,
                            inversion_order='Basic Position',
                            first_note=0,
                            second_note=0,
                            third_note=0,
                            fourth_note=0 if chord.fourth_note is not None else None,
                        )
                
                self.stdout.write(f"Updated {v_system_chords.count()} V-System chords")
                
                # Try to ensure V1 and V2 appear in AllChordTypes
                with connection.cursor() as cursor:
                    # Check if AllChordTypes table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='AllChordTypes'")
                    if cursor.fetchone():
                        # Try to add V1 and V2 to AllChordTypes
                        try:
                            cursor.execute("INSERT OR IGNORE INTO AllChordTypes (type_name, ordering) VALUES ('V1', 10)")
                            cursor.execute("INSERT OR IGNORE INTO AllChordTypes (type_name, ordering) VALUES ('V2', 11)")
                            self.stdout.write("Added V1 and V2 to AllChordTypes table")
                        except Exception as e:
                            self.stdout.write(f"Error updating AllChordTypes: {e}")
            
            self.stdout.write(self.style.SUCCESS("Successfully updated V-System chords"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error updating V-System chords: {e}"))
