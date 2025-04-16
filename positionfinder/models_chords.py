from django.utils.translation import gettext_lazy as _
from django.db import models

from .models import NotesCategory
from .string_choices import StringChoicesField
from .chord_position_choices import ChordInversionChoicesField
from .string_range_choices import StringRangeChoicesField
from .notes_choices import NotesChoicesField, ChordChoicesField

def create_eight_string_ranges(chord_id):
    chord = ChordNotes.objects.get(id=chord_id)

    # Only process if base chord has proper notes defined
    if None in (chord.first_note, chord.second_note, chord.third_note):
        return

    # Create standard triad on high strings including high A
    highA_e, created_highA_e = ChordNotes.objects.get_or_create(
        category_id=chord.category.id,
        type_name=chord.type_name,
        chord_name=chord.chord_name,
        range='highA - e',
        tonal_root=chord.tonal_root,
        defaults={
            'first_note': chord.first_note,
            'first_note_string': 'eString',
            'second_note': chord.second_note,
            'second_note_string': 'bString',
            'third_note': chord.third_note,
            'third_note_string': 'highAString',
            'range_ordering': chord.range_ordering if hasattr(chord, 'range_ordering') else None,
            'ordering': chord.ordering if hasattr(chord, 'ordering') else None,
            'chord_ordering': chord.chord_ordering if hasattr(chord, 'chord_ordering') else None
        }
    )

    # Extended range from high A to low B
    highA_lowB, created_highA_lowB = ChordNotes.objects.get_or_create(
        category_id=chord.category.id,
        type_name=chord.type_name,
        chord_name=chord.chord_name,
        range='highA - lowB',
        tonal_root=chord.tonal_root,
        defaults={
            'first_note': chord.first_note,
            'first_note_string': 'lowBString',
            'second_note': chord.second_note,
            'second_note_string': 'gString',
            'third_note': chord.third_note,
            'third_note_string': 'highAString',
            'range_ordering': chord.range_ordering if hasattr(chord, 'range_ordering') else None,
            'ordering': chord.ordering if hasattr(chord, 'ordering') else None,
            'chord_ordering': chord.chord_ordering if hasattr(chord, 'chord_ordering') else None
        }
    )

    # Standard extended 8-string range
    e_lowB, created_e_lowB = ChordNotes.objects.get_or_create(
        category_id=chord.category.id,
        type_name=chord.type_name,
        chord_name=chord.chord_name,
        range='e - lowB',
        tonal_root=chord.tonal_root,
        defaults={
            'first_note': chord.first_note,
            'first_note_string': 'lowBString',
            'second_note': chord.second_note,
            'second_note_string': 'AString',
            'third_note': chord.third_note,
            'third_note_string': 'eString',
            'range_ordering': chord.range_ordering if hasattr(chord, 'range_ordering') else None,
            'ordering': chord.ordering if hasattr(chord, 'ordering') else None,
            'chord_ordering': chord.chord_ordering if hasattr(chord, 'chord_ordering') else None
        }
    )

    # Create base positions for new ranges
    if created_highA_e: create_base_position(highA_e.id)
    if created_highA_lowB: create_base_position(highA_lowB.id)
    if created_e_lowB: create_base_position(e_lowB.id)

    # For seventh chords, create additional 8-string extended ranges
    if chord.fourth_note is not None:
        # Extended 8-string range for seventh chords
        e_lowB_seventh, created_e_lowB_seventh = ChordNotes.objects.get_or_create(
            category_id=chord.category.id,
            type_name=chord.type_name,
            chord_name=chord.chord_name,
            range='e - lowB', # Note: This range might conflict with the triad 'e - lowB' if tonal_root is the same. Consider a different range name if needed.
            tonal_root=chord.tonal_root,
            # Use more specific fields to ensure uniqueness for seventh chords if necessary
            # e.g., include fourth_note in the main query part if it defines uniqueness
            defaults={
                'first_note': chord.first_note,
                'first_note_string': 'lowBString',
                'second_note': chord.second_note,
                'second_note_string': 'ELowString',  
                'third_note': chord.third_note,
                'third_note_string': 'bString',
                'fourth_note': chord.fourth_note,
                'fourth_note_string': 'eString',
                'range_ordering': chord.range_ordering if hasattr(chord, 'range_ordering') else None,
                'ordering': chord.ordering if hasattr(chord, 'ordering') else None,
                'chord_ordering': chord.chord_ordering if hasattr(chord, 'chord_ordering') else None
            }
        )

        # Create positions for seventh chord
        if created_e_lowB_seventh: create_base_position(e_lowB_seventh.id)

def create_fourthnote_positions(w,x,y,z,chord_id):
    chord = ChordNotes.objects.get(id=chord_id)
    created_positions = []
    
    # Check if positions already exist to avoid duplicates
    existing_count = ChordPosition.objects.filter(
        notes_name_id=chord.id,
        inversion_order='First Inversion'
    ).count()
    
    if existing_count > 0:
        return created_positions
    
    
    #First Inversion
    first_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='First Inversion',
        first_note=w,
        second_note=x,
        third_note=y,
        fourth_note=z,
    )
    created_positions.append(first_inv)
    
    #Second Inversion
    second_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='Second Inversion',
        first_note=w+x,
        second_note=x+y,
        third_note=y+z,
        fourth_note=z+w,
    )
    created_positions.append(second_inv)
    
    #Third Inversion
    third_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='Third Inversion',
        first_note=w+x+y,
        second_note=x+y+z,
        third_note=y+z+w,
        fourth_note=z+w+x,
    )
    created_positions.append(third_inv)
    
    return created_positions

def create_triad_positions(w,x,y,chord_id):
    chord = ChordNotes.objects.get(id=chord_id)
    created_positions = []
    
    # Check if positions already exist to avoid duplicates
    existing_count = ChordPosition.objects.filter(
        notes_name_id=chord.id,
        inversion_order='First Inversion'
    ).count()
    
    if existing_count > 0:
        return created_positions
    
    
    #First Inversion
    first_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='First Inversion',
        first_note=w,
        second_note=x,
        third_note=y,
    )
    created_positions.append(first_inv)
    
    #Second Inversion
    second_inv = ChordPosition.objects.create(
        notes_name_id=chord.id,
        inversion_order='Second Inversion',
        first_note=w+x,
        second_note=x+y,
        third_note=y+w,
    )
    created_positions.append(second_inv)
    
    return created_positions

def create_base_position(id):
    """
    Create base position and inversions for a chord
    
    Args:
        id: ID of the chord to create positions for
    
    Returns:
        List of created positions or None if positions already exist
    """
    chord = ChordNotes.objects.get(id=id)
    created_positions = []
    
    # First, check if positions already exist to avoid duplicates
    existing_positions = ChordPosition.objects.filter(notes_name_id=id).count()
    if existing_positions > 0:
        return None
    
    # For V1 chords, all chords should have 4 notes, even if some are duplicated
    # This ensures consistent voicing across the V-System
    if chord.type_name == 'V1':
        # V1 chords always have 4 notes (they are 7th or extended chords)
        if None in (chord.first_note, chord.second_note, chord.third_note, chord.fourth_note):
            return None
        
        base_position = ChordPosition.objects.create(
            notes_name_id=chord.id,
            inversion_order='Basic Position',
            first_note=0,
            second_note=0,
            third_note=0,
            fourth_note=0,
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
            
        inversions = create_fourthnote_positions(w, x, y, z, id)
        created_positions.extend(inversions)
        
        return created_positions
    
    # For other chord types, check if it's a seventh chord (four notes)
    elif not None in (chord.first_note, chord.second_note, chord.third_note, chord.fourth_note) and chord.fifth_note is None:
        base_position = ChordPosition.objects.create(
            notes_name_id=chord.id,
            inversion_order='Basic Position',
            first_note=0,
            second_note=0,
            third_note=0,
            fourth_note=0,
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
            
        inversions = create_fourthnote_positions(w, x, y, z, id)
        created_positions.extend(inversions)
        
        return created_positions
    
    # Check if this is a triad (three notes only)
    elif not None in (chord.first_note, chord.second_note, chord.third_note) and chord.fourth_note is None:
        base_position = ChordPosition.objects.create(
            notes_name_id=chord.id,
            inversion_order='Basic Position',
            first_note=0,
            second_note=0,
            third_note=0
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
            
        inversions = create_triad_positions(w, x, y, id)
        created_positions.extend(inversions)
        
        return created_positions
    
    # If notes aren't properly defined, print a warning
    else:
        return None

def create_chord(id):
    chord = ChordNotes.objects.get(id=id)

    if chord.chord_name == 'Major 7':
        major_7 = ChordNotes.objects.get(id=id)

        major_7sharp5, created_maj7s5 = ChordNotes.objects.get_or_create(
            category_id=major_7.category.id,
            type_name=major_7.type_name,
            chord_name='Major 7(#5)',
            range=major_7.range,
            tonal_root=major_7.tonal_root,
            defaults={
                'first_note': major_7.first_note,
                'first_note_string': major_7.first_note_string,
                'second_note': major_7.second_note - 1 if major_7.second_note is not None else None,
                'second_note_string': major_7.second_note_string,
                'third_note': major_7.third_note + 1 if major_7.third_note is not None else None,
                'third_note_string': major_7.third_note_string,
                'fourth_note': major_7.fourth_note,
                'fourth_note_string': major_7.fourth_note_string,
                'range_ordering': major_7.range_ordering,
                'ordering': major_7.ordering,
                'chord_ordering': 5
            }
        )

        major_7flat5, created_maj7f5 = ChordNotes.objects.get_or_create(
            category_id=major_7.category.id,
            type_name=major_7.type_name,
            chord_name='Major 7(b5)',
            range=major_7.range,
            tonal_root=major_7.tonal_root,
            defaults={
                'first_note': major_7.first_note,
                'first_note_string': major_7.first_note_string,
                'second_note': major_7.second_note - 1 if major_7.second_note is not None else None,
                'second_note_string': major_7.second_note_string,
                'third_note': major_7.third_note - 1 if major_7.third_note is not None else None,
                'third_note_string': major_7.third_note_string,
                'fourth_note': major_7.fourth_note - 1 if major_7.fourth_note is not None else None,
                'fourth_note_string': major_7.fourth_note_string,
                'range_ordering': major_7.range_ordering,
                'ordering': major_7.ordering,
                'chord_ordering': 6
            }
        )

        minor_7, created_min7 = ChordNotes.objects.get_or_create(
            category_id=major_7.category.id,
            type_name=major_7.type_name,
            chord_name='Minor 7',
            range=major_7.range,
            tonal_root=major_7.tonal_root,
            defaults={
                'first_note': major_7.first_note,
                'first_note_string': major_7.first_note_string,
                'second_note': major_7.second_note - 1 if major_7.second_note is not None else None,
                'second_note_string': major_7.second_note_string,
                'third_note': major_7.third_note,
                'third_note_string': major_7.third_note_string,
                'fourth_note': major_7.fourth_note - 1 if major_7.fourth_note is not None else None,
                'fourth_note_string': major_7.fourth_note_string,
                'range_ordering': major_7.range_ordering,
                'ordering': major_7.ordering,
                'chord_ordering': 2
            }
        )

        minor_maj7, created_minmaj7 = ChordNotes.objects.get_or_create(
            category_id=major_7.category.id,
            type_name=major_7.type_name,
            chord_name='MinMaj 7',
            range=major_7.range,
            tonal_root=major_7.tonal_root,
            defaults={
                'first_note': major_7.first_note,
                'first_note_string': major_7.first_note_string,
                'second_note': major_7.second_note - 1 if major_7.second_note is not None else None,
                'second_note_string': major_7.second_note_string,
                'third_note': major_7.third_note,
                'third_note_string': major_7.third_note_string,
                'fourth_note': major_7.fourth_note,
                'fourth_note_string': major_7.fourth_note_string,
                'range_ordering': major_7.range_ordering,
                'ordering': major_7.ordering,
                'chord_ordering': 7
            }
        )

        # Note: Uses minor_7 object for category, type, range, root, notes. Ensure this is intended.
        minor_7_b5, created_min7f5 = ChordNotes.objects.get_or_create(
            category_id=minor_7.category.id,
            type_name=minor_7.type_name,
            chord_name='Minor 7b5',
            range=minor_7.range,
            tonal_root=minor_7.tonal_root,
            defaults={
                'first_note': minor_7.first_note,
                'first_note_string': minor_7.first_note_string,
                'second_note': minor_7.second_note,
                'second_note_string': minor_7.second_note_string,
                'third_note': minor_7.third_note - 1 if minor_7.third_note is not None else None,
                'third_note_string': minor_7.third_note_string,
                'fourth_note': minor_7.fourth_note,
                'fourth_note_string': minor_7.fourth_note_string,
                'range_ordering': major_7.range_ordering, # Uses major_7 for ordering? Verify if correct.
                'ordering': major_7.ordering, # Uses major_7 for ordering? Verify if correct.
                'chord_ordering': 4
            }
        )

        dominant_7, created_dom7 = ChordNotes.objects.get_or_create(
            category_id=major_7.category.id,
            type_name=major_7.type_name,
            chord_name='Dominant 7',
            range=major_7.range,
            tonal_root=major_7.tonal_root,
            defaults={
                'first_note': major_7.first_note,
                'first_note_string': major_7.first_note_string,
                'second_note': major_7.second_note,
                'second_note_string': major_7.second_note_string,
                'third_note': major_7.third_note,
                'third_note_string': major_7.third_note_string,
                'fourth_note': major_7.fourth_note - 1 if major_7.fourth_note is not None else None,
                'fourth_note_string': major_7.fourth_note_string,
                'range_ordering': major_7.range_ordering,
                'ordering': major_7.ordering,
                'chord_ordering': 3
            }
        )

        dominant_7sharp5, created_dom7s5 = ChordNotes.objects.get_or_create(
            category_id=major_7.category.id,
            type_name=major_7.type_name,
            chord_name='Dominant 7(#5)',
            range=major_7.range,
            tonal_root=major_7.tonal_root,
            defaults={
                'first_note': major_7.first_note,
                'first_note_string': major_7.first_note_string,
                'second_note': major_7.second_note,
                'second_note_string': major_7.second_note_string,
                'third_note': major_7.third_note + 1 if major_7.third_note is not None else None,
                'third_note_string': major_7.third_note_string,
                'fourth_note': major_7.fourth_note - 1 if major_7.fourth_note is not None else None,
                'fourth_note_string': major_7.fourth_note_string,
                'range_ordering': major_7.range_ordering,
                'ordering': major_7.ordering,
                'chord_ordering': 8
            }
        )

        dominant_7flat5, created_dom7f5 = ChordNotes.objects.get_or_create(
            category_id=major_7.category.id,
            type_name=major_7.type_name,
            chord_name='Dominant 7(b5)',
            range=major_7.range,
            tonal_root=major_7.tonal_root,
            defaults={
                'first_note': major_7.first_note,
                'first_note_string': major_7.first_note_string,
                'second_note': major_7.second_note,
                'second_note_string': major_7.second_note_string,
                'third_note': major_7.third_note - 1 if major_7.third_note is not None else None,
                'third_note_string': major_7.third_note_string,
                'fourth_note': major_7.fourth_note - 1 if major_7.fourth_note is not None else None,
                'fourth_note_string': major_7.fourth_note_string,
                'range_ordering': major_7.range_ordering,
                'ordering': major_7.ordering,
                'chord_ordering': 9
            }
        )

        # Only create base positions if the chord was newly created
        # Assuming 'id' refers to the original major_7 chord, its position might already exist.
        # create_base_position(id) # Consider if this is needed or if it should depend on a 'created' flag for major_7
        if created_maj7s5: create_base_position(major_7sharp5.id)
        if created_maj7f5: create_base_position(major_7flat5.id)
        if created_min7: create_base_position(minor_7.id)
        if created_minmaj7: create_base_position(minor_maj7.id)
        if created_min7f5: create_base_position(minor_7_b5.id)
        if created_dom7: create_base_position(dominant_7.id)
        if created_dom7s5: create_base_position(dominant_7sharp5.id)
        if created_dom7f5: create_base_position(dominant_7flat5.id)

    elif chord.chord_name == 'Major':
        major = ChordNotes.objects.get(id=id)

        minor, created_minor = ChordNotes.objects.get_or_create(
            category_id=major.category.id,
            type_name=major.type_name,
            chord_name='Minor',
            range=major.range,
            tonal_root=major.tonal_root,
            defaults={
                'first_note': major.first_note,
                'first_note_string': major.first_note_string,
                'second_note': major.second_note - 1 if major.second_note is not None else None,
                'second_note_string': major.second_note_string,
                'third_note': major.third_note,
                'third_note_string': major.third_note_string,
                'range_ordering': major.range_ordering,
                'ordering': major.ordering,
                'chord_ordering': 2
            }
        )

        # Note: Uses minor object for category, type, range, root, notes. Ensure this is intended.
        dim, created_dim = ChordNotes.objects.get_or_create(
            category_id=minor.category.id,
            type_name=minor.type_name,
            chord_name='Diminished',
            range=minor.range,
            tonal_root=minor.tonal_root,
            defaults={
                'first_note': minor.first_note,
                'first_note_string': minor.first_note_string,
                'second_note': minor.second_note,
                'second_note_string': minor.second_note_string,
                'third_note': minor.third_note - 1 if minor.third_note is not None else None,
                'third_note_string': minor.third_note_string,
                'range_ordering': major.range_ordering, # Uses major for ordering? Verify if correct.
                'ordering': major.ordering, # Uses major for ordering? Verify if correct.
                'chord_ordering': 3
            }
        )

        augmented, created_aug = ChordNotes.objects.get_or_create(
            category_id=major.category.id,
            type_name=major.type_name,
            chord_name='Augmented',
            range=major.range,
            tonal_root=major.tonal_root,
            defaults={
                'first_note': major.first_note,
                'first_note_string': major.first_note_string,
                'second_note': major.second_note + 1 if major.second_note is not None else None,
                'second_note': major.second_note + 1,
                'second_note_string': major.second_note_string,
                'third_note': major.third_note + 1,
                'third_note_string': major.third_note_string,
                'third_note': major.third_note + 1 if major.third_note is not None else None,
                'range_ordering': major.range_ordering,
                'ordering': major.ordering,
                'chord_ordering': 4
            }
        )

        # Only create base positions if the chord was newly created
        # Assuming 'id' refers to the original major chord, its position might already exist.
        # create_base_position(id) # Consider if this is needed or if it should depend on a 'created' flag for major
        if created_minor: create_base_position(minor.id)
        if created_dim: create_base_position(dim.id)
        if created_aug: create_base_position(augmented.id)

class ChordNotes(models.Model):
    category = models.ForeignKey(
        NotesCategory,
        on_delete=models.CASCADE,)
    ordering = models.IntegerField(null=True, blank=True)
    type_name = models.CharField(max_length=30)
    chord_name = ChordChoicesField(_("Chord Name"), default="Major 7")
    chord_ordering = models.IntegerField(null=True, blank=True)
    range = StringRangeChoicesField(_("String Range"), max_length=20, default="e - g")  # Max length increased in StringRangeChoicesField
    range_ordering = models.IntegerField(null=True, blank=True)
    tonal_root = models.IntegerField(default=0, help_text='defines the tonal space')
    first_note = NotesChoicesField(_("First Note"), default=0)
    first_note_string = StringChoicesField(_("String for Note"),
                                           null=True, blank=True)
    second_note = NotesChoicesField(_("Second Note"),
                                    default=4)
    second_note_string = StringChoicesField(_("String for Note"),
                                            null=True, blank=True)
    third_note = NotesChoicesField(_("Third Note"),
                                   default=7)
    third_note_string = StringChoicesField(_("String for Note"),
                                           null=True, blank=True)
    fourth_note = NotesChoicesField(_("Fourth Tone"),
                                    null=True, blank=True)
    fourth_note_string = StringChoicesField(_("String for Note"),
                                            null=True, blank=True)
    fifth_note = NotesChoicesField(_("Sixth Tone"),
                                   null=True, blank=True)
    fifth_note_string = StringChoicesField(_("String for Note"),
                                           null=True, blank=True)
    sixth_note = NotesChoicesField(_("Seventh Tone"),
                                   null=True, blank=True)
    sixth_note_string = StringChoicesField(_("String for Note"),
                                           null=True, blank=True)
    # Add fields to match database schema based on IntegrityError


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_data = self.__dict__.copy()

    def save(self, *args, **kwargs):
        # Validate notes before saving
        self._validate_chord_notes()

        # Set string assignments for V1 chords if creating with specific ranges
        if self.type_name == 'V1' and self.range == 'e - d':
            self.first_note_string = 'dString'
            self.second_note_string = 'gString'
            self.third_note_string = 'bString'
            self.fourth_note_string = 'eString'
        
        # Store initial data before saving to detect changes later
        initial_data = {}
        if self.pk:
            try:
                initial_data = ChordNotes.objects.values(
                    'first_note', 'second_note', 'third_note', 'fourth_note', 'fifth_note', 'sixth_note'
                ).get(pk=self.pk)
            except ChordNotes.DoesNotExist:
                pass

        is_new = self._state.adding
        super().save(*args, **kwargs)  # Call the "real" save() method.
        
        # Check if this is a CMaj7 e-d V1 type chord that we need to generate variants for
        should_generate_variants = (
            self.chord_name == 'Major 7' and 
            self.type_name == 'V1' and 
            self.range == 'e - d' and
            is_new and  # Only on creation, not updates
            not None in (self.first_note, self.second_note, self.third_note, self.fourth_note)
        )

        # Determine if it's exactly a 4-note chord AFTER saving
        is_four_note_chord = (
            self.first_note is not None and
            self.second_note is not None and
            self.third_note is not None and
            self.fourth_note is not None and
            self.fifth_note is None and
            self.sixth_note is None
        )

        # Post-save actions
        if is_new:
            # Always create the base position (inversions) for the current chord/range
            create_base_position(self.id)
            # If needed, still generate chord variants (Dominant7, Minor7, etc.) for THIS range only
            if should_generate_variants:
                self._generate_chord_variants()
        else:
            # Check if any relevant note fields have changed compared to initial data
            changed_fields = [field for field, initial_value in initial_data.items()
                              if getattr(self, field) != initial_value]

            if any(field in ['first_note', 'second_note', 'third_note', 'fourth_note', 'fifth_note', 'sixth_note'] for field in changed_fields):
                # Delete existing positions if notes have changed
                ChordPosition.objects.filter(notes_name=self).delete()
                # Recreate positions based on new notes for the current range only
                create_base_position(self.id)
                
    def _generate_chord_variants(self):
        """
        Generates related chord variants from a Major7 chord.
        Creates:
        - Dominant7 (R-3-5-b7)
        - Minor7 (R-b3-5-b7)
        - Minor7b5 (R-b3-b5-b7)
        
        Includes all inversions and string ranges.
        """
        from django.db import transaction
        
        # Generate variants with transaction for all-or-nothing behavior
        with transaction.atomic():
            # 1. Create Dominant7 - same as Major7 but with flat 7th (R-3-5-b7)
            dominant7, created_dom7 = ChordNotes.objects.get_or_create(
                category_id=self.category.id,
                type_name=self.type_name,
                chord_name='Dominant 7',
                range=self.range,
                tonal_root=self.tonal_root,
                defaults={
                    'first_note': self.first_note,
                    'first_note_string': self.first_note_string,
                    'second_note': self.second_note,
                    'second_note_string': self.second_note_string,
                    'third_note': self.third_note,
                    'third_note_string': self.third_note_string,
                    'fourth_note': (self.fourth_note - 1) % 12,  # flat 7th - ensure we stay within 0-11
                    'fourth_note_string': self.fourth_note_string,
                    'range_ordering': self.range_ordering if hasattr(self, 'range_ordering') else None,
                    'ordering': self.ordering if hasattr(self, 'ordering') else None,
                    'chord_ordering': 3  # Standard ordering for Dominant7
                }
            )
            
            if created_dom7:
                create_base_position(dominant7.id)
            else:
                # Update existing chord if needed
                dominant7.fourth_note = (self.fourth_note - 1) % 12
                dominant7.save()
            
            # 2. Create Minor7 - minor third and flat 7th (R-b3-5-b7)
            minor7, created_min7 = ChordNotes.objects.get_or_create(
                category_id=self.category.id,
                type_name=self.type_name,
                chord_name='Minor 7',
                range=self.range,
                tonal_root=self.tonal_root,
                defaults={
                    'first_note': self.first_note,
                    'first_note_string': self.first_note_string,
                    'second_note': (self.second_note - 1) % 12,  # flat 3rd
                    'second_note_string': self.second_note_string,
                    'third_note': self.third_note,
                    'third_note_string': self.third_note_string,
                    'fourth_note': (self.fourth_note - 1) % 12,  # flat 7th
                    'fourth_note_string': self.fourth_note_string,
                    'range_ordering': self.range_ordering if hasattr(self, 'range_ordering') else None,
                    'ordering': self.ordering if hasattr(self, 'ordering') else None,
                    'chord_ordering': 2  # Standard ordering for Minor7
                }
            )
            
            if created_min7:
                create_base_position(minor7.id)
            else:
                # Update existing chord if needed
                minor7.second_note = (self.second_note - 1) % 12
                minor7.fourth_note = (self.fourth_note - 1) % 12
                minor7.save()
            
            # 3. Create Minor7b5 - minor third, flat fifth, and flat 7th (R-b3-b5-b7)
            minor7b5, created_min7b5 = ChordNotes.objects.get_or_create(
                category_id=self.category.id,
                type_name=self.type_name,
                chord_name='Minor 7b5',
                range=self.range,
                tonal_root=self.tonal_root,
                defaults={
                    'first_note': self.first_note,
                    'first_note_string': self.first_note_string,
                    'second_note': (self.second_note - 1) % 12,  # flat 3rd
                    'second_note_string': self.second_note_string,
                    'third_note': (self.third_note - 1) % 12,  # flat 5th
                    'third_note_string': self.third_note_string,
                    'fourth_note': (self.fourth_note - 1) % 12,  # flat 7th
                    'fourth_note_string': self.fourth_note_string,
                    'range_ordering': self.range_ordering if hasattr(self, 'range_ordering') else None,
                    'ordering': self.ordering if hasattr(self, 'ordering') else None,
                    'chord_ordering': 4  # Standard ordering for Minor7b5
                }
            )
            
            if created_min7b5:
                create_base_position(minor7b5.id)
            else:
                # Update existing chord if needed
                minor7b5.second_note = (self.second_note - 1) % 12
                minor7b5.third_note = (self.third_note - 1) % 12
                minor7b5.fourth_note = (self.fourth_note - 1) % 12
                minor7b5.save()

    def _validate_chord_notes(self):
        """
        Validates that the notes assigned to the chord are within the allowed range (0-11).
        Raises a ValueError if any note is outside this range.
        """
        notes_fields = [
            self.first_note, self.second_note, self.third_note,
            self.fourth_note, self.fifth_note, self.sixth_note
        ]
        for note in notes_fields:
            if note is not None and not (0 <= note <= 11):
                raise ValueError(f"Invalid note value: {note}. Notes must be between 0 and 11.")

    def __str__(self):
        return f"{self.category} - {self.type_name} - {self.chord_name} - {self.range}"

    class Meta:
        verbose_name = _("Chord Note")
        verbose_name_plural = _("Chord Notes")
        ordering = ['ordering', 'chord_ordering', 'range_ordering']

class ChordPosition(models.Model):
    notes_name = models.ForeignKey(
        ChordNotes,
        on_delete=models.CASCADE,)
    inversion_order = ChordInversionChoicesField(_("Inversion Order"), default="Basic Position")
    first_note = models.IntegerField(null=True, blank=True)
    second_note = models.IntegerField(null=True, blank=True)
    third_note = models.IntegerField(null=True, blank=True)
    fourth_note = models.IntegerField(null=True, blank=True)
    fifth_note = models.IntegerField(null=True, blank=True)
    sixth_note = models.IntegerField(null=True, blank=True)
    seventh_note = models.IntegerField(null=True, blank=True)
    eighth_note = models.IntegerField(null=True, blank=True)
    ninth_note = models.IntegerField(null=True, blank=True)
    tenth_note = models.IntegerField(null=True, blank=True)
    eleventh_note = models.IntegerField(null=True, blank=True)
    twelfth_note = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.notes_name.category} - {self.notes_name.type_name} - \
                 {self.notes_name.chord_name} - {self.notes_name.range} - \
                 {self.inversion_order}"

    class Meta:
        verbose_name = _("Chord Position")
        verbose_name_plural = _("Chord Positions")
        ordering = ['notes_name']
