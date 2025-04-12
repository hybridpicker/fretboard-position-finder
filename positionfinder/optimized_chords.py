"""
Optimized chord positions for 6-string and 8-string guitars.
Focused on playability, ergonomics, and practical voicings.
"""
from django.db import transaction
from .models import NotesCategory
from .models_chords import ChordNotes, ChordPosition
from .template_notes import STRINGS

# Define common chord types and their intervals
CHORD_TYPES = {
    # Triads
    'Major': [0, 4, 7],
    'Minor': [0, 3, 7],
    'Diminished': [0, 3, 6],
    'Augmented': [0, 4, 8],
    'Sus2': [0, 2, 7],
    'Sus4': [0, 5, 7],
    
    # 7th chords
    'Major 7': [0, 4, 7, 11],
    'Minor 7': [0, 3, 7, 10],
    'Dominant 7': [0, 4, 7, 10],
    'Diminished 7': [0, 3, 6, 9],
    'Half-Diminished 7': [0, 3, 6, 10],
    'MinMaj 7': [0, 3, 7, 11],
    'Augmented 7': [0, 4, 8, 10],
    'Augmented Major 7': [0, 4, 8, 11],
    
    # Extended chords
    'Major 9': [0, 4, 7, 11, 14],
    'Minor 9': [0, 3, 7, 10, 14],
    'Dominant 9': [0, 4, 7, 10, 14],
    'Major 11': [0, 4, 7, 11, 14, 17],
    'Minor 11': [0, 3, 7, 10, 14, 17],
    'Dominant 11': [0, 4, 7, 10, 14, 17],
    'Major 13': [0, 4, 7, 11, 14, 17, 21],
    'Minor 13': [0, 3, 7, 10, 14, 17, 21],
    'Dominant 13': [0, 4, 7, 10, 14, 17, 21],
    
    # Altered chords
    'Major 7(#5)': [0, 4, 8, 11],
    'Major 7(b5)': [0, 4, 6, 11],
    'Dominant 7(#5)': [0, 4, 8, 10],
    'Dominant 7(b5)': [0, 4, 6, 10],
    'Dominant 7(b9)': [0, 4, 7, 10, 13],
    'Dominant 7(#9)': [0, 4, 7, 10, 15],
    'Dominant 7(#11)': [0, 4, 7, 10, 14, 18],
    'Minor 7(b5)': [0, 3, 6, 10],
}

# Standard 6-string chord voicings
STANDARD_VOICINGS = {
    # Major triad voicings (focusing on different ranges)
    'Major_V1': {
        'range': 'e - g',
        'strings': ['eString', 'bString', 'gString'],
        'notes': [0, 1, 2],
        'description': 'High range major triad'
    },
    'Major_V2': {
        'range': 'b - d',
        'strings': ['bString', 'gString', 'dString'],
        'notes': [0, 1, 2],
        'description': 'Mid range major triad'
    },
    'Major_V3': {
        'range': 'g - A',
        'strings': ['gString', 'dString', 'AString'],
        'notes': [0, 1, 2],
        'description': 'Low mid range major triad'
    },
    'Major_V4': {
        'range': 'd - E',
        'strings': ['dString', 'AString', 'ELowString'],
        'notes': [0, 1, 2],
        'description': 'Low range major triad'
    },
    
    # Minor triad voicings
    'Minor_V1': {
        'range': 'e - g',
        'strings': ['eString', 'bString', 'gString'],
        'notes': [0, 1, 2],
        'description': 'High range minor triad'
    },
    'Minor_V2': {
        'range': 'b - d',
        'strings': ['bString', 'gString', 'dString'],
        'notes': [0, 1, 2],
        'description': 'Mid range minor triad'
    },
    'Minor_V3': {
        'range': 'g - A',
        'strings': ['gString', 'dString', 'AString'],
        'notes': [0, 1, 2],
        'description': 'Low mid range minor triad'
    },
    'Minor_V4': {
        'range': 'd - E',
        'strings': ['dString', 'AString', 'ELowString'],
        'notes': [0, 1, 2],
        'description': 'Low range minor triad'
    },
    
    # Major 7th voicings
    'Major 7_V1': {
        'range': 'e - d',
        'strings': ['eString', 'bString', 'gString', 'dString'],
        'notes': [0, 1, 2, 3],
        'description': 'High range major 7th'
    },
    'Major 7_V2': {
        'range': 'b - A',
        'strings': ['bString', 'gString', 'dString', 'AString'],
        'notes': [0, 1, 2, 3],
        'description': 'Mid range major 7th'
    },
    'Major 7_V3': {
        'range': 'g - E',
        'strings': ['gString', 'dString', 'AString', 'ELowString'],
        'notes': [0, 1, 2, 3],
        'description': 'Low range major 7th'
    },
    
    # Minor 7th voicings
    'Minor 7_V1': {
        'range': 'e - d',
        'strings': ['eString', 'bString', 'gString', 'dString'],
        'notes': [0, 1, 2, 3],
        'description': 'High range minor 7th'
    },
    'Minor 7_V2': {
        'range': 'b - A',
        'strings': ['bString', 'gString', 'dString', 'AString'],
        'notes': [0, 1, 2, 3],
        'description': 'Mid range minor 7th'
    },
    'Minor 7_V3': {
        'range': 'g - E',
        'strings': ['gString', 'dString', 'AString', 'ELowString'],
        'notes': [0, 1, 2, 3],
        'description': 'Low range minor 7th'
    },
    
    # Dominant 7th voicings
    'Dominant 7_V1': {
        'range': 'e - d',
        'strings': ['eString', 'bString', 'gString', 'dString'],
        'notes': [0, 1, 2, 3],
        'description': 'High range dominant 7th'
    },
    'Dominant 7_V2': {
        'range': 'b - A',
        'strings': ['bString', 'gString', 'dString', 'AString'],
        'notes': [0, 1, 2, 3],
        'description': 'Mid range dominant 7th'
    },
    'Dominant 7_V3': {
        'range': 'g - E',
        'strings': ['gString', 'dString', 'AString', 'ELowString'],
        'notes': [0, 1, 2, 3],
        'description': 'Low range dominant 7th'
    },
}

# 8-string extended chord voicings - optimized for ergonomics and playability
EXTENDED_VOICINGS = {
    # Major triad voicings for 8-string
    'Major_V8_1': {
        'range': 'highA - g',
        'strings': ['highAString', 'eString', 'bString', 'gString'],
        'notes': [2, 0, 1, 2],  # 5th on highA, more ergonomic
        'description': 'Extended high range major (8-string)'
    },
    'Major_V8_2': {
        'range': 'e - lowB',
        'strings': ['eString', 'AString', 'ELowString', 'lowBString'],
        'notes': [0, 1, 2, 0],  # Root doubled on lowB, fuller sound
        'description': 'Extended low range major (8-string)'
    },
    'Major_V8_3': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'bString', 'AString', 'lowBString'],
        'notes': [1, 2, 0, 0],  # Root doubled for stability, better string spacing
        'description': 'Full range major triad (8-string)'
    },
    
    # Optimized 7th chord voicings for 8-string
    'Major 7_V8_1': {
        'range': 'highA - d',
        'strings': ['highAString', 'eString', 'bString', 'gString', 'dString'],
        'notes': [3, 0, 1, 2, 3],  # 7th on highA for clarity
        'description': 'Extended high range major 7th (8-string)'
    },
    'Major 7_V8_2': {
        'range': 'g - lowB',
        'strings': ['gString', 'dString', 'AString', 'ELowString', 'lowBString'],
        'notes': [3, 1, 2, 0, 0],  # Root doubled for stability
        'description': 'Extended low range major 7th (8-string)'
    },
    'Major 7_V8_3': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'bString', 'dString', 'AString', 'lowBString'],
        'notes': [3, 1, 2, 0, 0],  # Most ergonomic finger spacing
        'description': 'Full range major 7th (8-string)'
    },
    
    # Minor triad voicings for 8-string
    'Minor_V8_1': {
        'range': 'highA - g',
        'strings': ['highAString', 'eString', 'bString', 'gString'],
        'notes': [2, 0, 1, 2],  # 5th on highA, better ergonomics
        'description': 'Extended high range minor (8-string)'
    },
    'Minor_V8_2': {
        'range': 'e - lowB',
        'strings': ['eString', 'AString', 'ELowString', 'lowBString'],
        'notes': [0, 1, 2, 0],  # Root doubled on lowB
        'description': 'Extended low range minor (8-string)'
    },
    'Minor_V8_3': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'bString', 'dString', 'lowBString'],
        'notes': [1, 2, 0, 0],  # Root doubled for stability
        'description': 'Full range minor (8-string)'
    },
    
    # Optimized minor 7th voicings for 8-string
    'Minor 7_V8_1': {
        'range': 'highA - d',
        'strings': ['highAString', 'eString', 'bString', 'gString', 'dString'],
        'notes': [3, 0, 1, 2, 0],  # Root doubled on dString
        'description': 'Extended high range minor 7th (8-string)'
    },
    'Minor 7_V8_2': {
        'range': 'g - lowB',
        'strings': ['gString', 'dString', 'AString', 'ELowString', 'lowBString'],
        'notes': [1, 2, 3, 0, 0],  # Root doubled on low B and E
        'description': 'Extended low range minor 7th (8-string)'
    },
    'Minor 7_V8_3': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'bString', 'dString', 'AString', 'lowBString'],
        'notes': [3, 1, 2, 3, 0],  # Most ergonomic and playable
        'description': 'Full range minor 7th (8-string)'
    },
    
    # Optimized dominant 7th voicings for 8-string
    'Dominant 7_V8_1': {
        'range': 'highA - d',
        'strings': ['highAString', 'eString', 'bString', 'gString', 'dString'],
        'notes': [3, 0, 1, 2, 3],  # 7th on highA and dString
        'description': 'Extended high range dominant 7th (8-string)'
    },
    'Dominant 7_V8_2': {
        'range': 'g - lowB',
        'strings': ['gString', 'dString', 'AString', 'ELowString', 'lowBString'],
        'notes': [3, 1, 2, 0, 0],  # Root doubled for stability
        'description': 'Extended low range dominant 7th (8-string)'
    },
    'Dominant 7_V8_3': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'bString', 'dString', 'AString', 'lowBString'],
        'notes': [3, 1, 2, 3, 0],  # Ideal spacing for playability
        'description': 'Full range dominant 7th (8-string)'
    },
    
    # Optimized 9th chord voicings for 8-string
    'Major 9_V8_1': {
        'range': 'highA - A',
        'strings': ['highAString', 'eString', 'bString', 'gString', 'dString', 'AString'],
        'notes': [4, 0, 1, 2, 3, 0],  # Root doubled on AString, most playable
        'description': 'High range major 9th (8-string)'
    },
    'Major 9_V8_2': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'eString', 'gString', 'AString', 'ELowString', 'lowBString'],
        'notes': [4, 1, 2, 3, 0, 0],  # Root doubled for stability
        'description': 'Full range major 9th (8-string)'
    },
    'Dominant 9_V8_1': {
        'range': 'highA - A',
        'strings': ['highAString', 'eString', 'bString', 'gString', 'dString', 'AString'],
        'notes': [4, 0, 1, 2, 3, 0],  # Root doubled on AString, 9th on highA
        'description': 'High range dominant 9th (8-string)'
    },
    'Dominant 9_V8_2': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'bString', 'dString', 'AString', 'ELowString', 'lowBString'],
        'notes': [4, 1, 2, 3, 0, 0],  # Most ergonomic hand position
        'description': 'Full range dominant 9th (8-string)'
    },
    'Minor 9_V8_1': {
        'range': 'highA - A',
        'strings': ['highAString', 'eString', 'bString', 'gString', 'dString', 'AString'],
        'notes': [4, 0, 1, 2, 3, 0],  # Root doubled on AString, 9th on highA
        'description': 'High range minor 9th (8-string)'
    },
    'Minor 9_V8_2': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'bString', 'dString', 'AString', 'ELowString', 'lowBString'],
        'notes': [4, 1, 2, 3, 0, 0],  # Best finger spacing
        'description': 'Full range minor 9th (8-string)'
    },
    
    # Optimized 11th chord voicings for 8-string
    'Dominant 11_V8_1': {
        'range': 'highA - E',
        'strings': ['highAString', 'eString', 'bString', 'gString', 'dString', 'AString', 'ELowString'],
        'notes': [5, 0, 4, 1, 2, 3, 0],  # Root doubled on ELowString, 11th on highA
        'description': 'Extended dominant 11th (8-string)'
    },
    'Dominant 11_V8_2': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'eString', 'gString', 'dString', 'AString', 'ELowString', 'lowBString'],
        'notes': [5, 4, 2, 3, 0, 1, 0],  # More ergonomic finger spacing for playability
        'description': 'Optimized dominant 11th (8-string)'
    },
    
    # Optimized 13th chord voicings for 8-string
    'Dominant 13_V8_1': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'eString', 'bString', 'gString', 'dString', 'AString', 'ELowString', 'lowBString'],
        'notes': [6, 0, 4, 1, 2, 3, 5, 0],  # Full 8-string dominant 13th - balanced spacing
        'description': 'Full range dominant 13th (8-string)'
    },
    'Dominant 13_V8_2': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'eString', 'bString', 'gString', 'dString', 'AString', 'ELowString', 'lowBString'],
        'notes': [6, 4, 1, 2, 3, 5, 0, 0],  # Root doubled on low strings - better playability
        'description': 'Optimized dominant 13th (8-string)'
    },
    
    # Add altered chord voicings for 8-string
    'Dominant 7(#5)_V8_1': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'bString', 'dString', 'AString', 'lowBString'],
        'notes': [3, 1, 2, 3, 0],  # Ergonomic spacing
        'description': 'Full range dominant 7(#5) (8-string)'
    },
    'Dominant 7(b5)_V8_1': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'bString', 'dString', 'AString', 'lowBString'],
        'notes': [3, 1, 2, 3, 0],  # Ergonomic spacing
        'description': 'Full range dominant 7(b5) (8-string)'
    },
    'Major 7(#5)_V8_1': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'bString', 'dString', 'AString', 'lowBString'],
        'notes': [3, 1, 2, 3, 0],  # Ergonomic spacing
        'description': 'Full range major 7(#5) (8-string)'
    },
    'Minor 7b5_V8_1': {
        'range': 'highA - lowB',
        'strings': ['highAString', 'bString', 'dString', 'AString', 'lowBString'],
        'notes': [3, 1, 2, 3, 0],  # Ergonomic spacing
        'description': 'Full range minor 7b5 (8-string)'
    },
}

# Add drop 2 and drop 3 voicings for jazz-style chords
DROP_VOICINGS = {
    # Drop 2 voicings (drop the second highest note from the close position)
    'Major 7_Drop2_V1': {
        'range': 'e - A',
        'strings': ['eString', 'bString', 'dString', 'AString'],
        'notes': [0, 3, 1, 2],
        'description': 'Drop 2 major 7th, high range'
    },
    'Major 7_Drop2_V2': {
        'range': 'b - E',
        'strings': ['bString', 'gString', 'AString', 'ELowString'],
        'notes': [0, 3, 1, 2],
        'description': 'Drop 2 major 7th, low range'
    },
    'Dominant 7_Drop2_V1': {
        'range': 'e - A',
        'strings': ['eString', 'bString', 'dString', 'AString'],
        'notes': [0, 3, 1, 2],
        'description': 'Drop 2 dominant 7th, high range'
    },
    'Dominant 7_Drop2_V2': {
        'range': 'b - E',
        'strings': ['bString', 'gString', 'AString', 'ELowString'],
        'notes': [0, 3, 1, 2],
        'description': 'Drop 2 dominant 7th, low range'
    },
    'Minor 7_Drop2_V1': {
        'range': 'e - A',
        'strings': ['eString', 'bString', 'dString', 'AString'],
        'notes': [0, 3, 1, 2],
        'description': 'Drop 2 minor 7th, high range'
    },
    'Minor 7_Drop2_V2': {
        'range': 'b - E',
        'strings': ['bString', 'gString', 'AString', 'ELowString'],
        'notes': [0, 3, 1, 2],
        'description': 'Drop 2 minor 7th, low range'
    },
    
    # Drop 3 voicings (drop the third highest note from the close position)
    'Major 7_Drop3_V1': {
        'range': 'e - A',
        'strings': ['eString', 'gString', 'dString', 'AString'],
        'notes': [0, 2, 3, 1],
        'description': 'Drop 3 major 7th'
    },
    'Dominant 7_Drop3_V1': {
        'range': 'e - A',
        'strings': ['eString', 'gString', 'dString', 'AString'],
        'notes': [0, 2, 3, 1],
        'description': 'Drop 3 dominant 7th'
    },
    'Minor 7_Drop3_V1': {
        'range': 'e - A',
        'strings': ['eString', 'gString', 'dString', 'AString'],
        'notes': [0, 2, 3, 1],
        'description': 'Drop 3 minor 7th'
    },
}

# Combine all voicings
ALL_VOICINGS = {}
ALL_VOICINGS.update(STANDARD_VOICINGS)
ALL_VOICINGS.update(EXTENDED_VOICINGS)
ALL_VOICINGS.update(DROP_VOICINGS)

def create_optimized_chord_voicings():
    """
    Create optimized chord voicings for common chord types.
    """
    with transaction.atomic():
        # Get chords category
        try:
            chords_category = NotesCategory.objects.get(category_name='Chords')
        except NotesCategory.DoesNotExist:
            return
        
        # Process each chord type
        for chord_name, intervals in CHORD_TYPES.items():
            # Find eligible voicings for this chord type
            eligible_voicings = {}
            for voicing_name, voicing_data in ALL_VOICINGS.items():
                # Check if this voicing is for this chord type
                chord_type_from_voicing = voicing_name.split('_')[0]
                if chord_type_from_voicing == chord_name:
                    eligible_voicings[voicing_name] = voicing_data
            
            # If no specific voicings, use generic voicings based on chord note count
            if not eligible_voicings:
                if len(intervals) == 3:  # Triads
                    for voicing_name, voicing_data in STANDARD_VOICINGS.items():
                        if voicing_name.startswith('Major_V'):
                            eligible_voicings[f"{chord_name}_{voicing_name.split('_')[1]}"] = voicing_data
                elif len(intervals) == 4:  # 7th chords
                    for voicing_name, voicing_data in STANDARD_VOICINGS.items():
                        if voicing_name.startswith('Major 7_V'):
                            eligible_voicings[f"{chord_name}_{voicing_name.split('_')[1]}"] = voicing_data
            
            # Create voicings for this chord type
            for voicing_name, voicing_data in eligible_voicings.items():
                # Extract voicing details
                range_value = voicing_data['range']
                strings = voicing_data['strings']
                notes_indices = voicing_data['notes']
                
                # Make sure notes_indices doesn't exceed intervals length
                valid_notes_indices = [i for i in notes_indices if i < len(intervals)]
                if not valid_notes_indices:
                    continue
                
                # Create the chord
                voicing_type = voicing_name.split('_')[1] if '_' in voicing_name else 'V1'
                
                # Determine string assignments
                string_note_assignments = {}
                for i, string in enumerate(strings):
                    if i < len(notes_indices) and notes_indices[i] < len(intervals):
                        note_index = notes_indices[i]
                        note_value = intervals[note_index]
                        string_note_assignments[string] = note_value
                
                # Create or update ChordNotes object
                try:
                    # See if this chord already exists
                    chord = ChordNotes.objects.get(
                        chord_name=chord_name,
                        type_name=voicing_type,
                        range=range_value
                    )
                    
                    # Update the existing chord
                    for i, (string, note_value) in enumerate(string_note_assignments.items()):
                        if i == 0:
                            chord.first_note = note_value
                            chord.first_note_string = string
                        elif i == 1:
                            chord.second_note = note_value
                            chord.second_note_string = string
                        elif i == 2:
                            chord.third_note = note_value
                            chord.third_note_string = string
                        elif i == 3:
                            chord.fourth_note = note_value
                            chord.fourth_note_string = string
                        elif i == 4:
                            chord.fifth_note = note_value
                            chord.fifth_note_string = string
                        elif i == 5:
                            chord.sixth_note = note_value
                            chord.sixth_note_string = string
                    
                    chord.save()
                    
                except ChordNotes.DoesNotExist:
                    # Create a new chord
                    chord_data = {
                        'category': chords_category,
                        'type_name': voicing_type,
                        'chord_name': chord_name,
                        'range': range_value,
                        'tonal_root': 0,
                        'ordering': 1,  # Default ordering
                    }
                    
                    # Add note values and string assignments
                    for i, (string, note_value) in enumerate(string_note_assignments.items()):
                        if i == 0:
                            chord_data['first_note'] = note_value
                            chord_data['first_note_string'] = string
                        elif i == 1:
                            chord_data['second_note'] = note_value
                            chord_data['second_note_string'] = string
                        elif i == 2:
                            chord_data['third_note'] = note_value
                            chord_data['third_note_string'] = string
                        elif i == 3:
                            chord_data['fourth_note'] = note_value
                            chord_data['fourth_note_string'] = string
                        elif i == 4:
                            chord_data['fifth_note'] = note_value
                            chord_data['fifth_note_string'] = string
                        elif i == 5:
                            chord_data['sixth_note'] = note_value
                            chord_data['sixth_note_string'] = string
                    
                    # Create the chord
                    chord = ChordNotes.objects.create(**chord_data)

def add_eighth_string_voicings():
    """
    Add optimized 8-string voicings for extended range guitars focusing on playability and ergonomics.
    """
    from django.db import transaction
    from .eight_string_setup import create_base_position
    
    with transaction.atomic():
        # Get chords category
        try:
            chords_category = NotesCategory.objects.get(category_name='Chords')
        except NotesCategory.DoesNotExist:
            return
        
        # Track statistics
        created_count = 0
        updated_count = 0
        error_count = 0
        
        # Add extended range voicings
        for voicing_name, voicing_data in EXTENDED_VOICINGS.items():
            try:
                chord_name = voicing_name.split('_')[0]
                if chord_name not in CHORD_TYPES:
                    continue
                    
                # Get intervals for this chord type
                intervals = CHORD_TYPES[chord_name]
                
                # Extract voicing details
                range_value = voicing_data['range']
                strings = voicing_data['strings']
                notes_indices = voicing_data['notes']
                voicing_type = voicing_name.split('_')[1]
                description = voicing_data.get('description', f'8-string {chord_name} voicing')
                
                # Add useful debug information
                
                # Determine string assignments with validation
                string_note_assignments = {}
                valid_assignments = True
                
                for i, string in enumerate(strings):
                    if i < len(notes_indices):
                        note_index = notes_indices[i]
                        if note_index < len(intervals):
                            note_value = intervals[note_index]
                            string_note_assignments[string] = note_value
                        else:
                            valid_assignments = False
                
                if not valid_assignments:
                    error_count += 1
                    continue
                
                # Calculate range ordering to ensure proper sorting
                # Higher numbers for extended range voicings to appear at the end
                range_ordering = ChordNotes.objects.filter(
                    chord_name=chord_name
                ).count() + 100  # Start 8-string voicings after standard voicings
                
                # Create chord data
                chord_data = {
                    'category': chords_category,
                    'type_name': voicing_type,
                    'chord_name': chord_name,
                    'range': range_value,
                    'tonal_root': 0,
                    'ordering': 1,  # Default ordering
                    'range_ordering': range_ordering,
                    'chord_ordering': list(CHORD_TYPES.keys()).index(chord_name) if chord_name in CHORD_TYPES else 99,
                }
                
                # Add note values and string assignments
                for i, (string, note_value) in enumerate(string_note_assignments.items()):
                    if i == 0:
                        chord_data['first_note'] = note_value
                        chord_data['first_note_string'] = string
                    elif i == 1:
                        chord_data['second_note'] = note_value
                        chord_data['second_note_string'] = string
                    elif i == 2:
                        chord_data['third_note'] = note_value
                        chord_data['third_note_string'] = string
                    elif i == 3:
                        chord_data['fourth_note'] = note_value
                        chord_data['fourth_note_string'] = string
                    elif i == 4:
                        chord_data['fifth_note'] = note_value
                        chord_data['fifth_note_string'] = string
                    elif i == 5:
                        chord_data['sixth_note'] = note_value
                        chord_data['sixth_note_string'] = string
                    elif i == 6:
                        # Handle rare case of 7-note chord (e.g. 13th chords)
                        # Warning: Check if your ChordNotes model supports this
                        # If not, skip adding this note but continue with the voicing
                
                # Create or update the chord
                try:
                    # Check if this chord already exists
                    chord = ChordNotes.objects.get(
                        chord_name=chord_name,
                        type_name=voicing_type,
                        range=range_value
                    )
                    
                    # Update fields
                    for key, value in chord_data.items():
                        if key != 'category':  # Don't change the category
                            setattr(chord, key, value)
                    
                    chord.save()
                    updated_count += 1
                    
                except ChordNotes.DoesNotExist:
                    # Create a new chord
                    chord = ChordNotes.objects.create(**chord_data)
                    create_base_position(chord.id)  # Create positions immediately
                    created_count += 1
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                error_count += 1
        
        # Print statistics

def add_8string_specific_ranges():
    """
    Update string range choices to include 8-string specific combinations.
    """
    # These new ranges should be added to STRING_RANGE_CHOICES in string_range_choices.py
    new_8string_ranges = [
        'highA - e', # High A to high E
        'highA - b', # High A to B
        'highA - g', # High A to G
        'highA - d', # High A to D
        'highA - A', # High A to A
        'highA - E', # High A to Low E
        'highA - lowB', # High A to Low B
        'e - lowB',  # High E to Low B
        'b - lowB',  # B to Low B
        'g - lowB',  # G to Low B
        'd - lowB',  # D to Low B
        'A - lowB',  # A to Low B
    ]
    
    # This function doesn't actually modify the database
    # It's meant to show what ranges should be added to STRING_RANGE_CHOICES
    for range_str in new_8string_ranges:
