from django.db import models
from django.utils.translation import gettext_lazy as _

from .chord_position_choices import ChordInversionChoicesField
from .models import NotesCategory
from .notes_choices import ChordChoicesField, NotesChoicesField
from .string_choices import StringChoicesField
from .string_range_choices import StringRangeChoicesField


def _ordering_defaults(chord: "ChordNotes") -> dict:
    """Return the three ordering fields copied from a chord."""
    return {
        "range_ordering": chord.range_ordering if hasattr(chord, "range_ordering") else None,
        "ordering": chord.ordering if hasattr(chord, "ordering") else None,
        "chord_ordering": chord.chord_ordering if hasattr(chord, "chord_ordering") else None,
    }


def _get_or_create_range(chord: "ChordNotes", range_name: str, strings: tuple, with_fourth: bool):
    """get_or_create the chord on another string range; returns (chord, created)."""
    defaults = {
        "first_note": chord.first_note,
        "first_note_string": strings[0],
        "second_note": chord.second_note,
        "second_note_string": strings[1],
        "third_note": chord.third_note,
        "third_note_string": strings[2],
    }
    if with_fourth:
        defaults["fourth_note"] = chord.fourth_note
        defaults["fourth_note_string"] = strings[3]
    defaults.update(_ordering_defaults(chord))
    return ChordNotes.objects.get_or_create(
        category_id=chord.category.id,
        type_name=chord.type_name,
        chord_name=chord.chord_name,
        range=range_name,
        tonal_root=chord.tonal_root,
        defaults=defaults,
    )


def create_eight_string_ranges(chord_id: int) -> None:
    """Create the extended 8-string range variants of a chord and their base positions."""
    chord = ChordNotes.objects.get(id=chord_id)

    # Only process if base chord has proper notes defined
    if None in (chord.first_note, chord.second_note, chord.third_note):
        return

    # Create standard triad on high strings including high A
    highA_e, created_highA_e = _get_or_create_range(
        chord, "highA - e", ("eString", "bString", "highAString"), False
    )
    # Extended range from high A to low B
    highA_lowB, created_highA_lowB = _get_or_create_range(
        chord, "highA - lowB", ("lowBString", "gString", "highAString"), False
    )
    # Standard extended 8-string range
    e_lowB, created_e_lowB = _get_or_create_range(
        chord, "e - lowB", ("lowBString", "AString", "eString"), False
    )

    # Create base positions for new ranges
    if created_highA_e:
        create_base_position(highA_e.id)
    if created_highA_lowB:
        create_base_position(highA_lowB.id)
    if created_e_lowB:
        create_base_position(e_lowB.id)

    # For seventh chords, create additional 8-string extended ranges
    if chord.fourth_note is not None:
        # Note: this range might conflict with the triad 'e - lowB' if tonal_root is the same.
        e_lowB_seventh, created_e_lowB_seventh = _get_or_create_range(
            chord, "e - lowB", ("lowBString", "ELowString", "bString", "eString"), True
        )

        # Create positions for seventh chord
        if created_e_lowB_seventh:
            create_base_position(e_lowB_seventh.id)


def create_fourthnote_positions(w: int, x: int, y: int, z: int, chord_id: int) -> list:
    """Create the three inversions of a four-note chord from its interval gaps."""
    chord = ChordNotes.objects.get(id=chord_id)
    created_positions = []

    # Check if positions already exist to avoid duplicates
    existing_count = ChordPosition.objects.filter(
        notes_name_id=chord.id, inversion_order="First Inversion"
    ).count()

    if existing_count > 0:
        return created_positions

    inversions = (
        ("First Inversion", (w, x, y, z)),
        ("Second Inversion", (w + x, x + y, y + z, z + w)),
        ("Third Inversion", (w + x + y, x + y + z, y + z + w, z + w + x)),
    )
    for inversion_order, (first, second, third, fourth) in inversions:
        created_positions.append(
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order=inversion_order,
                first_note=first,
                second_note=second,
                third_note=third,
                fourth_note=fourth,
            )
        )

    return created_positions


def create_triad_positions(w: int, x: int, y: int, chord_id: int) -> list:
    """Create the two inversions of a triad from its interval gaps."""
    chord = ChordNotes.objects.get(id=chord_id)
    created_positions = []

    # Check if positions already exist to avoid duplicates
    existing_count = ChordPosition.objects.filter(
        notes_name_id=chord.id, inversion_order="First Inversion"
    ).count()

    if existing_count > 0:
        return created_positions

    inversions = (
        ("First Inversion", (w, x, y)),
        ("Second Inversion", (w + x, x + y, y + w)),
    )
    for inversion_order, (first, second, third) in inversions:
        created_positions.append(
            ChordPosition.objects.create(
                notes_name_id=chord.id,
                inversion_order=inversion_order,
                first_note=first,
                second_note=second,
                third_note=third,
            )
        )

    return created_positions


def _interval(start: int, end: int) -> int:
    """Distance from start up to end, adjusted for octave crossings."""
    gap = end - start
    while gap < 0:
        gap += 12
    return gap


def _create_four_note_base(chord: "ChordNotes", id: int) -> list:
    """Create basic position and inversions for a four-note chord."""
    created_positions = [
        ChordPosition.objects.create(
            notes_name_id=chord.id,
            inversion_order="Basic Position",
            first_note=0,
            second_note=0,
            third_note=0,
            fourth_note=0,
        )
    ]

    # Calculate intervals between notes (adjusting for octave crossings)
    w = _interval(chord.first_note, chord.second_note)
    x = _interval(chord.second_note, chord.third_note)
    y = _interval(chord.third_note, chord.fourth_note)
    z = _interval(chord.fourth_note, chord.first_note)

    created_positions.extend(create_fourthnote_positions(w, x, y, z, id))
    return created_positions


def _create_triad_base(chord: "ChordNotes", id: int) -> list:
    """Create basic position and inversions for a triad."""
    created_positions = [
        ChordPosition.objects.create(
            notes_name_id=chord.id,
            inversion_order="Basic Position",
            first_note=0,
            second_note=0,
            third_note=0,
        )
    ]

    # Calculate intervals between notes (adjusting for octave crossings)
    w = _interval(chord.first_note, chord.second_note)
    x = _interval(chord.second_note, chord.third_note)
    y = _interval(chord.third_note, chord.first_note)

    created_positions.extend(create_triad_positions(w, x, y, id))
    return created_positions


def create_base_position(id: int) -> list | None:
    """
    Create base position and inversions for a chord

    Args:
        id: ID of the chord to create positions for

    Returns:
        List of created positions or None if positions already exist
    """
    chord = ChordNotes.objects.get(id=id)

    # First, check if positions already exist to avoid duplicates
    existing_positions = ChordPosition.objects.filter(notes_name_id=id).count()
    if existing_positions > 0:
        return None

    # For V1 chords, all chords should have 4 notes, even if some are duplicated
    # This ensures consistent voicing across the V-System
    if chord.type_name == "V1":
        # V1 chords always have 4 notes (they are 7th or extended chords)
        if None in (chord.first_note, chord.second_note, chord.third_note, chord.fourth_note):
            return None
        return _create_four_note_base(chord, id)

    # For other chord types, check if it's a seventh chord (four notes)
    elif (
        None not in (chord.first_note, chord.second_note, chord.third_note, chord.fourth_note)
        and chord.fifth_note is None
    ):
        return _create_four_note_base(chord, id)

    # Check if this is a triad (three notes only)
    elif (
        None not in (chord.first_note, chord.second_note, chord.third_note)
        and chord.fourth_note is None
    ):
        return _create_triad_base(chord, id)

    # Notes aren't properly defined
    else:
        return None


def _shift(note: int | None, delta: int) -> int | None:
    """Shift a note by delta semitones, keeping None."""
    return note + delta if note is not None else None


def _get_or_create_variant(
    source: "ChordNotes",
    ref: "ChordNotes",
    chord_name: str,
    chord_ordering: int,
    deltas: tuple,
):
    """
    get_or_create a derived chord: notes and strings come from ref shifted by deltas
    (3 or 4 entries); category, type, range, root and ordering fields from ref/source.
    """
    defaults = {
        "first_note": ref.first_note,
        "first_note_string": ref.first_note_string,
        "second_note": _shift(ref.second_note, deltas[0]),
        "second_note_string": ref.second_note_string,
        "third_note": _shift(ref.third_note, deltas[1]),
        "third_note_string": ref.third_note_string,
    }
    if len(deltas) > 2:
        defaults["fourth_note"] = _shift(ref.fourth_note, deltas[2])
        defaults["fourth_note_string"] = ref.fourth_note_string
    defaults.update(
        {
            "range_ordering": source.range_ordering,
            "ordering": source.ordering,
            "chord_ordering": chord_ordering,
        }
    )
    return ChordNotes.objects.get_or_create(
        category_id=ref.category.id,
        type_name=ref.type_name,
        chord_name=chord_name,
        range=ref.range,
        tonal_root=ref.tonal_root,
        defaults=defaults,
    )


# (chord_name, chord_ordering, (second, third, fourth) semitone shifts) derived from Major 7
_MAJOR_7_VARIANTS = (
    ("Major 7(#5)", 5, (-1, 1, 0)),
    ("Major 7(b5)", 6, (-1, -1, -1)),
    ("Minor 7", 2, (-1, 0, -1)),
    ("MinMaj 7", 7, (-1, 0, 0)),
)
_DOMINANT_7_VARIANTS = (
    ("Dominant 7", 3, (0, 0, -1)),
    ("Dominant 7(#5)", 8, (0, 1, -1)),
    ("Dominant 7(b5)", 9, (0, -1, -1)),
)


def _create_major_7_variants(major_7: "ChordNotes") -> None:
    """Derive the minor/dominant/altered seventh chords from a Major 7 chord."""
    results = [_get_or_create_variant(major_7, major_7, *spec) for spec in _MAJOR_7_VARIANTS]
    minor_7 = results[2][0]

    # Note: Uses minor_7 object for category, type, range, root, notes; ordering from major_7.
    results.append(_get_or_create_variant(major_7, minor_7, "Minor 7b5", 4, (0, -1, 0)))
    for spec in _DOMINANT_7_VARIANTS:
        results.append(_get_or_create_variant(major_7, major_7, *spec))

    # Only create base positions if the chord was newly created
    for variant, created in results:
        if created:
            create_base_position(variant.id)


def _create_major_variants(major: "ChordNotes") -> None:
    """Derive Minor, Diminished and Augmented triads from a Major chord."""
    minor, created_minor = _get_or_create_variant(major, major, "Minor", 2, (-1, 0))
    # Note: Uses minor object for category, type, range, root, notes; ordering from major.
    dim, created_dim = _get_or_create_variant(major, minor, "Diminished", 3, (0, -1))
    augmented, created_aug = _get_or_create_variant(major, major, "Augmented", 4, (1, 1))

    # Only create base positions if the chord was newly created
    if created_minor:
        create_base_position(minor.id)
    if created_dim:
        create_base_position(dim.id)
    if created_aug:
        create_base_position(augmented.id)


def create_chord(id: int) -> None:
    """Create the derived chord types (minor, dominant, ...) for a Major or Major 7 chord."""
    chord = ChordNotes.objects.get(id=id)

    if chord.chord_name == "Major 7":
        _create_major_7_variants(ChordNotes.objects.get(id=id))
    elif chord.chord_name == "Major":
        _create_major_variants(ChordNotes.objects.get(id=id))


class ChordNotes(models.Model):
    """A chord voicing (notes and strings) on one string range."""

    category = models.ForeignKey(
        NotesCategory,
        on_delete=models.CASCADE,
    )
    ordering = models.IntegerField(null=True, blank=True)
    type_name = models.CharField(max_length=30)
    chord_name = ChordChoicesField(_("Chord Name"), default="Major 7")
    chord_ordering = models.IntegerField(null=True, blank=True)
    range = StringRangeChoicesField(
        _("String Range"), max_length=20, default="e - g"
    )  # Max length increased in StringRangeChoicesField
    range_ordering = models.IntegerField(null=True, blank=True)
    tonal_root = models.IntegerField(default=0, help_text="defines the tonal space")
    first_note = NotesChoicesField(_("First Note"), default=0)
    first_note_string = StringChoicesField(_("String for Note"), null=True, blank=True)
    second_note = NotesChoicesField(_("Second Note"), default=4)
    second_note_string = StringChoicesField(_("String for Note"), null=True, blank=True)
    third_note = NotesChoicesField(_("Third Note"), default=7)
    third_note_string = StringChoicesField(_("String for Note"), null=True, blank=True)
    fourth_note = NotesChoicesField(_("Fourth Tone"), null=True, blank=True)
    fourth_note_string = StringChoicesField(_("String for Note"), null=True, blank=True)
    fifth_note = NotesChoicesField(_("Sixth Tone"), null=True, blank=True)
    fifth_note_string = StringChoicesField(_("String for Note"), null=True, blank=True)
    sixth_note = NotesChoicesField(_("Seventh Tone"), null=True, blank=True)
    sixth_note_string = StringChoicesField(_("String for Note"), null=True, blank=True)
    # Add fields to match database schema based on IntegrityError

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._initial_data = self.__dict__.copy()

    def _load_initial_notes(self) -> dict:
        """Return the stored note values of this chord (empty if it is not stored yet)."""
        initial_data = {}
        if self.pk:
            try:
                initial_data = ChordNotes.objects.values(
                    "first_note",
                    "second_note",
                    "third_note",
                    "fourth_note",
                    "fifth_note",
                    "sixth_note",
                ).get(pk=self.pk)
            except ChordNotes.DoesNotExist:
                pass
        return initial_data

    def _notes_changed(self, initial_data: dict) -> bool:
        """Whether any note field differs from the stored values."""
        changed_fields = [
            field
            for field, initial_value in initial_data.items()
            if getattr(self, field) != initial_value
        ]
        return any(
            field
            in [
                "first_note",
                "second_note",
                "third_note",
                "fourth_note",
                "fifth_note",
                "sixth_note",
            ]
            for field in changed_fields
        )

    def save(self, *args, **kwargs) -> None:
        """Validate notes, save, and (re)create the chord positions."""
        # Validate notes before saving
        self._validate_chord_notes()

        # Set string assignments for V1 chords if creating with specific ranges
        if self.type_name == "V1" and self.range == "e - d":
            self.first_note_string = "dString"
            self.second_note_string = "gString"
            self.third_note_string = "bString"
            self.fourth_note_string = "eString"

        # Store initial data before saving to detect changes later
        initial_data = self._load_initial_notes()

        is_new = self._state.adding
        super().save(*args, **kwargs)  # Call the "real" save() method.

        # Check if this is a CMaj7 e-d V1 type chord that we need to generate variants for
        should_generate_variants = (
            self.chord_name == "Major 7"
            and self.type_name == "V1"
            and self.range == "e - d"
            and is_new  # Only on creation, not updates
            and None not in (self.first_note, self.second_note, self.third_note, self.fourth_note)
        )

        # Post-save actions
        if is_new:
            # Always create the base position (inversions) for the current chord/range
            create_base_position(self.id)
            # If needed, still generate chord variants (Dominant7, Minor7, etc.) for THIS range only
            if should_generate_variants:
                self._generate_chord_variants()
        elif self._notes_changed(initial_data):
            # Delete existing positions if notes have changed
            ChordPosition.objects.filter(notes_name=self).delete()
            # Recreate positions based on new notes for the current range only
            create_base_position(self.id)

    def _ensure_variant(self, chord_name: str, chord_ordering: int, changed: dict) -> None:
        """get_or_create a variant of this chord; `changed` holds its altered note values."""
        defaults = {
            "first_note": self.first_note,
            "first_note_string": self.first_note_string,
            "second_note": self.second_note,
            "second_note_string": self.second_note_string,
            "third_note": self.third_note,
            "third_note_string": self.third_note_string,
            "fourth_note": self.fourth_note,
            "fourth_note_string": self.fourth_note_string,
            "range_ordering": self.range_ordering if hasattr(self, "range_ordering") else None,
            "ordering": self.ordering if hasattr(self, "ordering") else None,
            "chord_ordering": chord_ordering,
        }
        defaults.update(changed)
        variant, created = ChordNotes.objects.get_or_create(
            category_id=self.category.id,
            type_name=self.type_name,
            chord_name=chord_name,
            range=self.range,
            tonal_root=self.tonal_root,
            defaults=defaults,
        )
        if created:
            create_base_position(variant.id)
        else:
            # Update existing chord if needed
            for field, value in changed.items():
                setattr(variant, field, value)
            variant.save()

    def _generate_chord_variants(self) -> None:
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
            # 1. Dominant7 - same as Major7 but with flat 7th (R-3-5-b7); stay within 0-11
            self._ensure_variant("Dominant 7", 3, {"fourth_note": (self.fourth_note - 1) % 12})
            # 2. Minor7 - minor third and flat 7th (R-b3-5-b7)
            self._ensure_variant(
                "Minor 7",
                2,
                {
                    "second_note": (self.second_note - 1) % 12,
                    "fourth_note": (self.fourth_note - 1) % 12,
                },
            )
            # 3. Minor7b5 - minor third, flat fifth, and flat 7th (R-b3-b5-b7)
            self._ensure_variant(
                "Minor 7b5",
                4,
                {
                    "second_note": (self.second_note - 1) % 12,
                    "third_note": (self.third_note - 1) % 12,
                    "fourth_note": (self.fourth_note - 1) % 12,
                },
            )

    def _validate_chord_notes(self) -> None:
        """
        Validates that the notes assigned to the chord are within the allowed range (0-11).
        Raises a ValueError if any note is outside this range.
        """
        notes_fields = [
            self.first_note,
            self.second_note,
            self.third_note,
            self.fourth_note,
            self.fifth_note,
            self.sixth_note,
        ]
        for note in notes_fields:
            if note is not None and not (0 <= note <= 11):
                raise ValueError(f"Invalid note value: {note}. Notes must be between 0 and 11.")

    def __str__(self) -> str:
        return f"{self.category} - {self.type_name} - {self.chord_name} - {self.range}"

    class Meta:
        """Model options."""

        verbose_name = _("Chord Note")
        verbose_name_plural = _("Chord Notes")
        ordering = ["ordering", "chord_ordering", "range_ordering"]


class ChordPosition(models.Model):
    """One inversion of a ChordNotes voicing, stored as interval offsets."""

    notes_name = models.ForeignKey(
        ChordNotes,
        on_delete=models.CASCADE,
    )
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

    def __str__(self) -> str:
        return f"{self.notes_name.category} - {self.notes_name.type_name} - \
                 {self.notes_name.chord_name} - {self.notes_name.range} - \
                 {self.inversion_order}"

    class Meta:
        """Model options."""

        verbose_name = _("Chord Position")
        verbose_name_plural = _("Chord Positions")
        ordering = ["notes_name"]
