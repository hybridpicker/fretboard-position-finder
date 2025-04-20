"""
Optimized positions for scales and chords in 6-string and 8-string configurations.
Focused on playability, ergonomics, and musicality.
"""
from django.db import transaction
from .models import Notes, NotesCategory
from .positions import NotesPosition

# Define optimized position patterns
MAJOR_SCALE_POSITIONS = [
    # Position 1 - Open position (most common)
    "0,2,4,5,7,9,11",
    
    # Position 2 - 2nd position (starts with index finger on 2nd fret)
    "2,4,5,7,9,11,12",
    
    # Position 3 - 4th position
    "4,5,7,9,11,12,14",
    
    # Position 4 - 5th position
    "5,7,9,11,12,14,16",
    
    # Position 5 - 7th position
    "7,9,11,12,14,16,17",
    
    # Position 6 - 9th position
    "9,11,12,14,16,17,19",
    
    # Position 7 - 12th position (octave)
    "12,14,16,17,19,21,23",
]

# Extended positions for 8-string (add lower and higher positions)
MAJOR_SCALE_8STRING_POSITIONS = MAJOR_SCALE_POSITIONS + [
    # Position 8 - Lower extension (utilizing low B string)
    "-2,0,2,4,5,7,9",
    
    # Position 9 - Higher extension (utilizing high A string)
    "14,16,17,19,21,23,24",
]

# Define optimized position patterns for other common scales
MINOR_SCALE_POSITIONS = [
    # Position 1 - Open position
    "0,2,3,5,7,8,10",
    
    # Position 2 - 2nd position
    "2,3,5,7,8,10,12",
    
    # Position 3 - 3rd position
    "3,5,7,8,10,12,14",
    
    # Position 4 - 5th position
    "5,7,8,10,12,14,15",
    
    # Position 5 - 7th position
    "7,8,10,12,14,15,17",
    
    # Position 6 - 8th position
    "8,10,12,14,15,17,19",
    
    # Position 7 - 12th position (octave)
    "12,14,15,17,19,20,22",
]

# Minor positions for 8-string
MINOR_SCALE_8STRING_POSITIONS = MINOR_SCALE_POSITIONS + [
    # Position 8 - Lower extension
    "-3,-1,0,2,3,5,7",
    
    # Position 9 - Higher extension
    "15,17,19,20,22,24,26",
]

# Positions for other common scales (pentatonic, blues, etc.)
PENTATONIC_MAJOR_POSITIONS = [
    # Position 1 - Open position
    "0,2,4,7,9",
    
    # Position 2 - 2nd position
    "2,4,7,9,12",
    
    # Position 3 - 4th position
    "4,7,9,12,14",
    
    # Position 4 - 7th position
    "7,9,12,14,16",
    
    # Position 5 - 9th position
    "9,12,14,16,19",
    
    # Position 6 - 12th position (octave)
    "12,14,16,19,21",
]

PENTATONIC_MINOR_POSITIONS = [
    # Position 1 - Open position
    "0,3,5,7,10",
    
    # Position 2 - 3rd position
    "3,5,7,10,12",
    
    # Position 3 - 5th position
    "5,7,10,12,15",
    
    # Position 4 - 7th position
    "7,10,12,15,17",
    
    # Position 5 - 10th position
    "10,12,15,17,19",
    
    # Position 6 - 12th position (octave)
    "12,15,17,19,22",
]

BLUES_SCALE_POSITIONS = [
    # Position 1 - Open position
    "0,3,5,6,7,10",
    
    # Position 2 - 3rd position
    "3,5,6,7,10,12",
    
    # Position 3 - 5th position
    "5,6,7,10,12,15",
    
    # Position 4 - 7th position
    "7,10,12,13,15,17",
    
    # Position 5 - 10th position
    "10,12,13,15,17,19",
    
    # Position 6 - 12th position (octave)
    "12,15,17,18,19,22",
]

# Positions for modes
DORIAN_POSITIONS = [
    # Position 1 - Open position
    "0,2,3,5,7,9,10",
    
    # Position 2 - 2nd position
    "2,3,5,7,9,10,12",
    
    # Position 3 - 3rd position
    "3,5,7,9,10,12,14",
    
    # Position 4 - 5th position
    "5,7,9,10,12,14,15",
    
    # Position 5 - 7th position
    "7,9,10,12,14,15,17",
    
    # Position 6 - 9th position
    "9,10,12,14,15,17,19",
    
    # Position 7 - 12th position (octave)
    "12,14,15,17,19,21,22",
]

PHRYGIAN_POSITIONS = [
    # Position 1 - Open position
    "0,1,3,5,7,8,10",
    
    # Position 2 - 1st position
    "1,3,5,7,8,10,12",
    
    # Position 3 - 3rd position
    "3,5,7,8,10,12,13",
    
    # Position 4 - 5th position
    "5,7,8,10,12,13,15",
    
    # Position 5 - 7th position
    "7,8,10,12,13,15,17",
    
    # Position 6 - 8th position
    "8,10,12,13,15,17,19",
    
    # Position 7 - 12th position (octave)
    "12,13,15,17,19,20,22",
]

LYDIAN_POSITIONS = [
    # Position 1 - Open position
    "0,2,4,6,7,9,11",
    
    # Position 2 - 2nd position
    "2,4,6,7,9,11,12",
    
    # Position 3 - 4th position
    "4,6,7,9,11,12,14",
    
    # Position 4 - 6th position
    "6,7,9,11,12,14,16",
    
    # Position 5 - 7th position
    "7,9,11,12,14,16,18",
    
    # Position 6 - 9th position
    "9,11,12,14,16,18,19",
    
    # Position 7 - 12th position (octave)
    "12,14,16,18,19,21,23",
]

MIXOLYDIAN_POSITIONS = [
    # Position 1 - Open position
    "0,2,4,5,7,9,10",
    
    # Position 2 - 2nd position
    "2,4,5,7,9,10,12",
    
    # Position 3 - 4th position
    "4,5,7,9,10,12,14",
    
    # Position 4 - 5th position
    "5,7,9,10,12,14,16",
    
    # Position 5 - 7th position
    "7,9,10,12,14,16,17",
    
    # Position 6 - 9th position
    "9,10,12,14,16,17,19",
    
    # Position 7 - 12th position (octave)
    "12,14,16,17,19,21,22",
]

LOCRIAN_POSITIONS = [
    # Position 1 - Open position
    "0,1,3,5,6,8,10",
    
    # Position 2 - 1st position
    "1,3,5,6,8,10,12",
    
    # Position 3 - 3rd position
    "3,5,6,8,10,12,13",
    
    # Position 4 - 5th position
    "5,6,8,10,12,13,15",
    
    # Position 5 - 6th position
    "6,8,10,12,13,15,17",
    
    # Position 6 - 8th position
    "8,10,12,13,15,17,18",
    
    # Position 7 - 12th position (octave)
    "12,13,15,17,18,20,22",
]

# Jazz and exotic scales
MELODIC_MINOR_POSITIONS = [
    # Position 1 - Open position
    "0,2,3,5,7,9,11",
    
    # Position 2 - 2nd position
    "2,3,5,7,9,11,12",
    
    # Position 3 - 3rd position
    "3,5,7,9,11,12,14",
    
    # Position 4 - 5th position
    "5,7,9,11,12,14,15",
    
    # Position 5 - 7th position
    "7,9,11,12,14,15,17",
    
    # Position 6 - 9th position
    "9,11,12,14,15,17,19",
    
    # Position 7 - 12th position (octave)
    "12,14,15,17,19,21,23",
]

HARMONIC_MINOR_POSITIONS = [
    # Position 1 - Open position
    "0,2,3,5,7,8,11",
    
    # Position 2 - 2nd position
    "2,3,5,7,8,11,12",
    
    # Position 3 - 3rd position
    "3,5,7,8,11,12,14",
    
    # Position 4 - 5th position
    "5,7,8,11,12,14,15",
    
    # Position 5 - 7th position
    "7,8,11,12,14,15,17",
    
    # Position 6 - 8th position
    "8,11,12,14,15,17,19",
    
    # Position 7 - 12th position (octave)
    "12,14,15,17,19,20,23",
]

# Dictionary mapping scale names to position patterns
SCALE_POSITIONS = {
    "Major": MAJOR_SCALE_POSITIONS,
    "Minor": MINOR_SCALE_POSITIONS,
    "Pentatonic Major": PENTATONIC_MAJOR_POSITIONS,
    "Pentatonic Minor": PENTATONIC_MINOR_POSITIONS,
    "Blues": BLUES_SCALE_POSITIONS,
    "Dorian": DORIAN_POSITIONS,
    "Phrygian": PHRYGIAN_POSITIONS,
    "Lydian": LYDIAN_POSITIONS,
    "Mixolydian": MIXOLYDIAN_POSITIONS,
    "Locrian": LOCRIAN_POSITIONS,
    "Melodic Minor": MELODIC_MINOR_POSITIONS,
    "Harmonic Minor": HARMONIC_MINOR_POSITIONS,
}

# 8-string extensions (only for scales that need special handling)
SCALE_POSITIONS_8STRING = {
    "Major": MAJOR_SCALE_8STRING_POSITIONS,
    "Minor": MINOR_SCALE_8STRING_POSITIONS,
}

def create_optimized_positions():
    """
    Create optimized positions for all scales in the database.
    """
    with transaction.atomic():
        # Get scales category
        scales_category = NotesCategory.objects.get(category_name='Scales')
        
        # Get all scales
        scales = Notes.objects.filter(category=scales_category)
        
        # Clear existing positions
        NotesPosition.objects.filter(notes_name__category=scales_category).delete()
        
        # Create new optimized positions
        for scale in scales:
            scale_name = scale.note_name
            
            # Check if we have optimized positions for this scale
            if scale_name in SCALE_POSITIONS:
                positions = SCALE_POSITIONS[scale_name]
                
                # Create positions
                for i, position in enumerate(positions, 1):
                    NotesPosition.objects.create(
                        notes_name=scale,
                        position_order=i,
                        position=position
                    )
                    
                # Check if we need to add 8-string specific positions
                if scale_name in SCALE_POSITIONS_8STRING and len(SCALE_POSITIONS_8STRING[scale_name]) > len(positions):
                    # Add the additional 8-string positions
                    extended_positions = SCALE_POSITIONS_8STRING[scale_name][len(positions):]
                    for i, position in enumerate(extended_positions, len(positions) + 1):
                        NotesPosition.objects.create(
                            notes_name=scale,
                            position_order=i,
                            position=position
                        )
            else:
                # For scales without specific optimized positions, create default positions
                # based on the Major scale pattern but adjusted for the scale's intervals
                
                # Get scale intervals
                intervals = []
                for i in range(1, 13):
                    note_attr = f'note_{i}' if i > 1 else 'first_note'
                    note_val = getattr(scale, note_attr, None)
                    if note_val is not None:
                        intervals.append(note_val)
                
                # Create positions based on standard patterns but adjusted for this scale
                for i, base_position in enumerate(MAJOR_SCALE_POSITIONS, 1):
                    # Start with the base fret
                    base_fret = int(base_position.split(',')[0])
                    
                    # Create a position string using this scale's intervals
                    position_values = [str(base_fret + interval) for interval in intervals]
                    position_string = ','.join(position_values)
                    
                    NotesPosition.objects.create(
                        notes_name=scale,
                        position_order=i,
                        position=position_string
                    )

def update_specific_scale_positions(scale_name, positions):
    """
    Update positions for a specific scale.
    
    Args:
        scale_name: Name of the scale to update
        positions: List of position strings
    """
    with transaction.atomic():
        try:
            scale = Notes.objects.get(note_name=scale_name, category__category_name='Scales')
            
            # Clear existing positions
            NotesPosition.objects.filter(notes_name=scale).delete()
            
            # Create new positions
            for i, position in enumerate(positions, 1):
                NotesPosition.objects.create(
                    notes_name=scale,
                    position_order=i,
                    position=position
                )
            
            return True
        except Notes.DoesNotExist:
            return False
