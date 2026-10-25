from django.db import models
from django.utils.translation import gettext_lazy as _

NOTE_MAPPING = {
    "c": "C",
    "cs": "C#",
    "d": "D",
    "ds": "D#",
    "e": "E",
    "f": "F",
    "fs": "F#",
    "g": "G",
    "gs": "G#",
    "a": "A",
    "as": "A#",
    "b": "B",
    "db": "Db",
    "eb": "Eb",
    "gb": "Gb",
    "ab": "Ab",
    "bb": "Bb",
}

NOTE_ORDER = [
    "C",
    "C#",
    "Db",
    "D",
    "D#",
    "Eb",
    "E",
    "F",
    "F#",
    "Gb",
    "G",
    "G#",
    "Ab",
    "A",
    "A#",
    "Bb",
    "B",
]

# The highest strings should be at the beginning of the list
# For 8-String: highA-b should be first
# For 6-String: e-g should be first
NOTE_RANGE_ORDER = [
    # 8-String highest ranges first
    "highA - b",
    "highA - e",
    "highA - g",
    "a - b",
    "highA - lowB",
    # 6-String highest ranges
    "e - g",
    "e - d",
    "e - A",
    "e - E",
    "e - B",
    "e - lowB",
    # Middle ranges
    "b - d",
    "b - A",
    "b - E",
    "b - B",
    # Lower ranges
    "g - A",
    "g - E",
    "g - B",
    "d - E",
    "d - B",
    "A - B",
    "A - lowB",
    "d - lowB",
]

STRING_RANGE_CHOICES = {
    # 8-String specific ranges - from highest to lowest
    "highA - b": _("highA - b"),
    "highA - e": _("highA - e"),
    "highA - g": _("highA - g"),
    "a - b": _("a - b"),  # Legacy naming for highA-e
    "highA - lowB": _("highA - lowB"),
    # 6-String standard ranges - from highest to lowest
    "e - g": _("e - g"),
    "e - d": _("e - d"),
    "b - d": _("b - d"),
    "g - A": _("g - A"),
    "d - E": _("d - E"),
    # 8-String extended ranges - from highest to lowest
    "e - lowB": _("e - lowB"),
    "d - lowB": _("d - lowB"),
    "A - lowB": _("A - lowB"),
    # Other less common ranges
    "A - B": _("A - B"),
    "a - g": _("a - g"),
    "b - A": _("b - A"),
    "g - E": _("g - E"),
    "d - B": _("d - B"),
    "a - D": _("a - D"),
    "e - A": _("e - A"),
    "b - E": _("b - E"),
    "g - B": _("g - B"),
    "a - A": _("a - A"),
    "e - E": _("e - E"),
    "b - B": _("b - B"),
    "a - E": _("a - E"),
    "e - B": _("e - B"),
}

NOTES_CHOICES = {
    0: _("C"),
    1: _("Db/C#"),
    2: _("D"),
    3: _("Eb/D#"),
    4: _("E"),
    5: _("F"),
    6: _("Gb/F#"),
    7: _("G"),
    8: _("Ab/G#"),
    9: _("A"),
    10: _("Bb/A#"),
    11: _("B"),
}


class NotesChoicesField(models.IntegerField):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = tuple(sorted(NOTES_CHOICES.items()))
        super().__init__(*args, **kwargs)


CHORD_CHOICES = {
    "Major 7": _("Major 7"),
    "Major7(#5)": _("Major7(#5)"),
    "Minor 7": _("Minor 7"),
    "Dominant 7": _("Dominant 7"),
    "Minor7b5": _("Minor 7b5"),
    "Major": _("Major"),
    "Minor": _("Minor"),
    "Diminished": _("Diminished"),
    "Diminished 7": _("Diminished 7"),
    "Augmented": _("Augmented"),
    "Altered 7": _("Altered 7"),
    "MinMaj7": _("MinMaj7"),
    "7 #5": _("7 #5"),
    "6 #5": _("6 #5"),
}


class ChordChoicesField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = tuple(sorted(CHORD_CHOICES.items()))
        kwargs["max_length"] = 20
        super().__init__(*args, **kwargs)
