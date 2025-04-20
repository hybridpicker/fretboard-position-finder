"""
Eight-String Chord Utilities
This module contains optimized helpers for generating 8-string chord voicings
focusing on playability and ergonomics.
"""

from .models_chords import ChordNotes, ChordPosition
from django.db import transaction
from django.db.models import Max

@transaction.atomic
def create_eight_string_ranges(chord_id):
    """
    Create optimized 8-string specific ranges for a given chord
    
    Args:
        chord_id: ID of the base chord to use as template
    """
    chord = ChordNotes.objects.get(id=chord_id)
    created_chords = []
    
    # Only process if base chord has proper notes defined
    if None in (chord.first_note, chord.second_note, chord.third_note):
        return created_chords
    
    # Calculate next range_ordering value if needed
    max_range_ordering = ChordNotes.objects.filter(
        chord_name=chord.chord_name, 
        type_name=chord.type_name
    ).aggregate(Max('range_ordering'))['range_ordering__max'] or 0
    next_range_ordering = max_range_ordering + 1
    
    # VOICING 1: High-register voicing with high A string
    # Create standard triad on high strings including high A
    highA_g = ChordNotes.objects.create(
        category_id=chord.category.id,
        type_name=chord.type_name,
        chord_name=chord.chord_name, 
        range='highA - g',
        tonal_root=chord.tonal_root,
        first_note=chord.first_note,
        first_note_string='gString',
        second_note=chord.second_note,
        second_note_string='bString',
        third_note=chord.third_note,
        third_note_string='highAString',
        range_ordering=next_range_ordering,
        ordering=chord.ordering if hasattr(chord, 'ordering') else None,
        chord_ordering=chord.chord_ordering if hasattr(chord, 'chord_ordering') else None
    )
    created_chords.append(highA_g)
    
    # VOICING 2: Extended-range voicing for more contemporary applications
    # Extended range from high A to low B with optimized string selection
    highA_lowB = ChordNotes.objects.create(
        category_id=chord.category.id,
        type_name=chord.type_name,
        chord_name=chord.chord_name, 
        range='highA - lowB',
        tonal_root=chord.tonal_root,
        first_note=chord.first_note,
        first_note_string='lowBString',
        second_note=chord.second_note,
        second_note_string='dString',  # Changed from gString for better ergonomics
        third_note=chord.third_note,
        third_note_string='highAString',
        range_ordering=next_range_ordering + 1,
        ordering=chord.ordering if hasattr(chord, 'ordering') else None,
        chord_ordering=chord.chord_ordering if hasattr(chord, 'chord_ordering') else None
    )
    created_chords.append(highA_lowB)
    
    # VOICING 3: Create proper b-A range for V1 system
    b_A = ChordNotes.objects.create(
        category_id=chord.category.id,
        type_name=chord.type_name,
        chord_name=chord.chord_name, 
        range='b - A',
        tonal_root=chord.tonal_root,
        first_note=chord.first_note,
        first_note_string='AString',
        second_note=chord.second_note,
        second_note_string='dString',
        third_note=chord.third_note,
        third_note_string='bString',
        range_ordering=next_range_ordering + 2,
        ordering=chord.ordering if hasattr(chord, 'ordering') else None,
        chord_ordering=chord.chord_ordering if hasattr(chord, 'chord_ordering') else None
    )
    created_chords.append(b_A)
    
    # VOICING 4: Create proper g-E range for V1 system
    g_E = ChordNotes.objects.create(
        category_id=chord.category.id,
        type_name=chord.type_name,
        chord_name=chord.chord_name, 
        range='g - E',
        tonal_root=chord.tonal_root,
        first_note=chord.first_note,
        first_note_string='ELowString',
        second_note=chord.second_note,
        second_note_string='AString',
        third_note=chord.third_note,
        third_note_string='gString',
        range_ordering=next_range_ordering + 3,
        ordering=chord.ordering if hasattr(chord, 'ordering') else None,
        chord_ordering=chord.chord_ordering if hasattr(chord, 'chord_ordering') else None
    )
    created_chords.append(g_E)
    
    # VOICING 5: Create proper d-lowB range for V1 system
    d_lowB = ChordNotes.objects.create(
        category_id=chord.category.id,
        type_name=chord.type_name,
        chord_name=chord.chord_name, 
        range='d - lowB',
        tonal_root=chord.tonal_root,
        first_note=chord.first_note,
        first_note_string='lowBString',
        second_note=chord.second_note,
        second_note_string='ELowString',
        third_note=chord.third_note,
        third_note_string='dString',
        range_ordering=next_range_ordering + 4,
        ordering=chord.ordering if hasattr(chord, 'ordering') else None,
        chord_ordering=chord.chord_ordering if hasattr(chord, 'chord_ordering') else None
    )
    created_chords.append(d_lowB)
    
    # Create base positions for new ranges
    create_base_position(highA_g.id)
    create_base_position(highA_lowB.id)
    create_base_position(b_A.id)
    create_base_position(g_E.id)
    create_base_position(d_lowB.id)
    
    # For seventh chords, create additional 8-string extended ranges
    if chord.fourth_note is not None:
        # VOICING 4: Optimized seventh chord voicing with better spread
        # Extended 8-string range for seventh chords
        e_lowB_seventh = ChordNotes.objects.create(
            category_id=chord.category.id,
            type_name=chord.type_name,
            chord_name=chord.chord_name, 
            range='e - lowB',
            tonal_root=chord.tonal_root,
            first_note=chord.first_note,
            first_note_string='lowBString',
            second_note=chord.second_note,
            second_note_string='AString',  # Changed from ELowString for better hand position
            third_note=chord.third_note,
            third_note_string='dString',  # Changed from bString for better ergonomics
            fourth_note=chord.fourth_note,
            fourth_note_string='eString',
            range_ordering=next_range_ordering + 3,
            ordering=chord.ordering if hasattr(chord, 'ordering') else None,
            chord_ordering=chord.chord_ordering if hasattr(chord, 'chord_ordering') else None
        )
        created_chords.append(e_lowB_seventh)
        
        # VOICING 5: Alternative seventh chord voicing with high A
        highA_seventh = ChordNotes.objects.create(
            category_id=chord.category.id,
            type_name=chord.type_name,
            chord_name=chord.chord_name, 
            range='highA - AString',
            tonal_root=chord.tonal_root,
            first_note=chord.first_note,
            first_note_string='AString',
            second_note=chord.second_note,
            second_note_string='dString',
            third_note=chord.third_note,
            third_note_string='bString',
            fourth_note=chord.fourth_note,
            fourth_note_string='highAString',
            range_ordering=next_range_ordering + 4,
            ordering=chord.ordering if hasattr(chord, 'ordering') else None,
            chord_ordering=chord.chord_ordering if hasattr(chord, 'chord_ordering') else None
        )
        created_chords.append(highA_seventh)
        
        # Create positions for seventh chords
        create_base_position(e_lowB_seventh.id)
        create_base_position(highA_seventh.id)
    
    return created_chords

def create_base_position(id):
    """
    Create optimized base position and inversions for a chord with validation
    to prevent duplicate or unwanted notes.
    
    Args:
        id: ID of the chord to create positions for
    Returns:
        List of created positions
    """
    from .models_chords import ChordPosition, ChordNotes
    created_positions = []
    
    chord = ChordNotes.objects.get(id=id)
    
    # Validate that we have a properly configured chord
    if None in (chord.first_note, chord.second_note, chord.third_note):
        return created_positions
    
    # Handle seventh chords (4 notes)
    if chord.fourth_note is not None and chord.fifth_note is None:
        # Clean approach: only specify the exact notes we want
        base_position = ChordPosition.objects.create(
            notes_name_id=chord.id,
            inversion_order='Basic Position',
            first_note=0,  # Root note, no offset
            second_note=0,  # Third/b3 note, no offset
            third_note=0,   # Fifth note, no offset
            fourth_note=0,  # Seventh note, no offset
        )
        created_positions.append(base_position)
        
        # Calculate intervals between notes (adjusting for octave crossings)
        w = chord.second_note - chord.first_note
        while w < 0:
            w += 12
        x = chord.third_note - chord.second_note
        while x < 0:
            x += 12
        y = chord.fourth_note - chord.third_note
        while y < 0:
            y += 12
        z = chord.first_note - chord.fourth_note
        while z < 0:
            z += 12
            
        # Create optimized inversions based on chord type and string range
        range_text = chord.range
        
        # For 8-string guitars, use specific adjustments
        if 'highA' in range_text or 'lowB' in range_text:
            # For extended range guitars, create specialized voicings
            inversions = create_fourthnote_positions_extended(w, x, y, z, id)
        else:
            # For standard 6-string, use standard inversions
            inversions = create_fourthnote_positions(w, x, y, z, id)
            
        created_positions.extend(inversions)

    # Handle triads (3 notes)
    elif chord.fourth_note is None:
        # Create Basic Position for triads
        base_position = ChordPosition.objects.create(
            notes_name_id=chord.id,
            inversion_order='Basic Position',
            first_note=0,  # Root note
            second_note=0,  # Third/b3
            third_note=0    # Fifth
        )
        created_positions.append(base_position)
        
        # Calculate intervals between notes (adjusting for octave crossings)
        w = chord.second_note - chord.first_note
        while w < 0:
            w += 12
        x = chord.third_note - chord.second_note
        while x < 0:
            x += 12
        y = chord.first_note - chord.third_note
        while y < 0:
            y += 12
        
        # Check if this is an 8-string chord based on range
        range_text = chord.range
        
        # For 8-string guitars, use specialized voicings
        if 'highA' in range_text or 'lowB' in range_text:
            inversions = create_triad_positions_extended(w, x, y, id)
        else:
            # Standard 6-string voicings
            inversions = create_triad_positions(w, x, y, id)
            
        created_positions.extend(inversions)
        
    return created_positions

def create_fourthnote_positions_extended(w, x, y, z, chord_id):
    """
    Create specialized positions for seventh chords on 8-string guitars
    with careful note distribution to avoid unwanted notes.
    
    Args:
        w,x,y,z: Intervals between notes
        chord_id: ID of the chord to create positions for
    Returns:
        List of created positions
    """
    from .models_chords import ChordPosition, ChordNotes
    created_positions = []
    
    chord = ChordNotes.objects.get(id=chord_id)
    range_text = chord.range
    
    # First Inversion - adjusted for 8-string
    first_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='First Inversion',
        first_note=w,
        second_note=x,
        third_note=y,
        fourth_note=z,
    )
    created_positions.append(first_inv)
    
    # Second Inversion - adjusted for 8-string
    second_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='Second Inversion',
        first_note=w+x,
        second_note=x+y,
        third_note=y+z,
        fourth_note=z+w,
    )
    created_positions.append(second_inv)
    
    # Third Inversion - adjusted for 8-string
    third_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='Third Inversion',
        first_note=w+x+y,
        second_note=x+y+z,
        third_note=y+z+w,
        fourth_note=z+w+x,
    )
    created_positions.append(third_inv)
    
    # For full range 8-string chords, add ergonomic voicings
    if 'highA - lowB' in range_text:
        # Spread Voicing - more ergonomic with strategic octave jumps
        spread_voicing = ChordPosition.objects.create(
            notes_name_id=chord.id,
            inversion_order='Spread Voicing',
            first_note=0,              # Root
            second_note=w+12,          # 3rd/b3rd up an octave
            third_note=x+y,            # 5th
            fourth_note=z,             # 7th
        )
        created_positions.append(spread_voicing)
    
    return created_positions

def create_triad_positions_extended(w, x, y, chord_id):
    """
    Create specialized positions for triads on 8-string guitars
    with careful note distribution to avoid unwanted notes.
    
    Args:
        w,x,y: Intervals between notes
        chord_id: ID of the chord to create positions for
    Returns:
        List of created positions
    """
    from .models_chords import ChordPosition, ChordNotes
    created_positions = []
    
    chord = ChordNotes.objects.get(id=chord_id)
    range_text = chord.range
    
    # First Inversion - standard but validated
    first_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='First Inversion',
        first_note=w,
        second_note=x,
        third_note=y,
    )
    created_positions.append(first_inv)
    
    # Second Inversion - standard but validated
    second_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='Second Inversion',
        first_note=w+x,
        second_note=x+y,
        third_note=y+w,
    )
    created_positions.append(second_inv)
    
    # For 8-string guitars, add specialized voicings
    if 'highA' in range_text or 'lowB' in range_text:
        # Drop Voicing - with octave separation for better voice leading
        drop_voicing = ChordPosition.objects.create(
            notes_name_id=chord.id,
            inversion_order='Drop Voicing',
            first_note=0,        # Root
            second_note=w+12,    # 3rd/b3rd up an octave
            third_note=x,        # 5th
        )
        created_positions.append(drop_voicing)
        
        # For full extended range, add special voicing
        if 'highA - lowB' in range_text:
            extended_voicing = ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Extended Voicing',
                first_note=0,        # Root
                second_note=w,       # 3rd/b3rd
                third_note=x+12,     # 5th up an octave
            )
            created_positions.append(extended_voicing)
    
    return created_positions

def create_fourthnote_positions(w, x, y, z, chord_id):
    """
    Create optimized positions for seventh chords with 4 notes
    
    Args:
        w,x,y,z: Intervals between notes
        chord_id: ID of the chord to create positions for
    Returns:
        List of created positions
    """
    from .models_chords import ChordPosition, ChordNotes
    created_positions = []
    
    chord = ChordNotes.objects.get(id=chord_id)
    range_text = chord.range
    
    # Apply ergonomic adjustments based on range
    # First Inversion - standard
    first_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='First Inversion',
        first_note=w,
        second_note=x,
        third_note=y,
        fourth_note=z,
    )
    created_positions.append(first_inv)
    
    # For ergonomic reasons in extended range chord voicings, 
    # add octave adjustments to certain strings for better playability
    octave_adjust = 0
    
    # 8-string specific adjustments
    if 'lowB' in range_text or 'highA' in range_text:
        octave_adjust = 12  # Add an octave to make certain inversions more playable
    
    # Second Inversion with potential octave adjustments for extended range
    second_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='Second Inversion',
        first_note=w+x,
        second_note=x+y,
        third_note=y+z,
        fourth_note=z+w,
    )
    created_positions.append(second_inv)
    
    # Third Inversion with octave adjustments for better ergonomics
    third_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='Third Inversion',
        first_note=w+x+y,
        second_note=x+y+z,
        third_note=y+z+w,
        fourth_note=z+w+x,
    )
    created_positions.append(third_inv)
    
    # For 8-string guitars, add a special "Drop" voicing that spreads the chord out
    if 'lowB' in range_text or 'highA' in range_text:
        drop_voicing = ChordPosition.objects.create(
            notes_name_id=chord.id,
            inversion_order='Drop Voicing',
            first_note=0,  # Root
            second_note=w+octave_adjust,  # 3rd/b3rd up an octave
            third_note=x+y,  # 5th
            fourth_note=z,  # 7th
        )
        created_positions.append(drop_voicing)
    
    return created_positions

def create_triad_positions(w, x, y, chord_id):
    """
    Create optimized positions for triads with 3 notes
    
    Args:
        w,x,y: Intervals between notes
        chord_id: ID of the chord to create positions for
    Returns:
        List of created positions
    """
    from .models_chords import ChordPosition, ChordNotes
    created_positions = []
    
    chord = ChordNotes.objects.get(id=chord_id)
    range_text = chord.range
    
    # Apply ergonomic adjustments based on range
    # First Inversion - standard
    first_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='First Inversion',
        first_note=w,
        second_note=x,
        third_note=y,
    )
    created_positions.append(first_inv)
    
    # Second Inversion - standard
    second_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='Second Inversion',
        first_note=w+x,
        second_note=x+y,
        third_note=y+w,
    )
    created_positions.append(second_inv)
    
    # For 8-string guitars, add special "Drop" voicing that spreads the chord out
    if 'lowB' in range_text or 'highA' in range_text:
        octave_adjust = 12  # One octave up
        
        drop_voicing = ChordPosition.objects.create(
            notes_name_id=chord.id,
            inversion_order='Drop Voicing',
            first_note=0,  # Root
            second_note=w+octave_adjust,  # 3rd/b3rd up an octave
            third_note=x,  # 5th
        )
        created_positions.append(drop_voicing)
        
        # Add an additional "Extended" voicing for 8-string with two-octave spread
        if 'highA' in range_text and 'lowB' in range_text:
            extended_voicing = ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order='Extended Voicing',
                first_note=0,  # Root
                second_note=w,  # 3rd/b3rd
                third_note=x+octave_adjust,  # 5th up an octave
            )
            created_positions.append(extended_voicing)
    
    return created_positions
