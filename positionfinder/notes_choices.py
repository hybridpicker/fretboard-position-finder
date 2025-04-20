from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import SmallIntegerField

NOTE_MAPPING = {
    'c': 'C',
    'cs': 'C#',
    'd': 'D',
    'ds': 'D#',
    'e': 'E',
    'f': 'F',
    'fs': 'F#',
    'g': 'G',
    'gs': 'G#',
    'a': 'A',
    'as': 'A#',
    'b': 'B',
    'db': 'Db',
    'eb': 'Eb',
    'gb': 'Gb',
    'ab': 'Ab',
    'bb': 'Bb'
}

NOTE_ORDER = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']

# The highest strings should be at the beginning of the list
# For 8-String: highA-b should be first
# For 6-String: e-g should be first
NOTE_RANGE_ORDER = [
    # 8-String highest ranges first
    'highA - b', 'highA - e', 'highA - g', 'a - b', 'highA - lowB',
    # 6-String highest ranges
    'e - g', 'e - d', 'e - A', 'e - E', 'e - B', 'e - lowB',
    # Middle ranges
    'b - d', 'b - A', 'b - E', 'b - B', 
    # Lower ranges
    'g - A', 'g - E', 'g - B', 'd - E', 'd - B', 'A - B', 'A - lowB', 'd - lowB'
]

STRING_RANGE_CHOICES = {
    # 8-String specific ranges - from highest to lowest
    'highA - b': _(u'highA - b'),
    'highA - e': _(u'highA - e'),
    'highA - g': _(u'highA - g'),
    'a - b': _(u'a - b'),  # Legacy naming for highA-e
    'highA - lowB': _(u'highA - lowB'),
    
    # 6-String standard ranges - from highest to lowest
    'e - g': _(u'e - g'),
    'e - d': _(u'e - d'),
    'b - d': _(u'b - d'),
    'g - A': _(u'g - A'),
    'd - E': _(u'd - E'),
    
    # 8-String extended ranges - from highest to lowest
    'e - lowB': _(u'e - lowB'),
    'd - lowB': _(u'd - lowB'),
    'A - lowB': _(u'A - lowB'),
    
    # Other less common ranges
    'A - B': _(u'A - B'),
    'a - g': _(u'a - g'),
    'b - A': _(u'b - A'),
    'g - E': _(u'g - E'),
    'd - B': _(u'd - B'),
    'a - D': _(u'a - D'),
    'e - A': _(u'e - A'),
    'b - E': _(u'b - E'),
    'g - B': _(u'g - B'),
    'a - A': _(u'a - A'),
    'e - E': _(u'e - E'),
    'b - B': _(u'b - B'),
    'a - E': _(u'a - E'),
    'e - B': _(u'e - B'),
}

NOTES_CHOICES = {
    0 : _(u'C'),
    1 : _(u'Db/C#'),
    2 : _(u'D'),
    3 : _(u'Eb/D#'),
    4 : _(u'E'),
    5 : _(u'F'),
    6 : _(u'Gb/F#'),
    7 : _(u'G'),
    8 : _(u'Ab/G#'),
    9 : _(u'A'),
    10 : _(u'Bb/A#'),
    11 : _(u'B'),
}

class NotesChoicesField(models.IntegerField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = tuple(sorted(NOTES_CHOICES.items()))
        super(NotesChoicesField, self).__init__(*args, **kwargs)

CHORD_CHOICES = {
    'Major 7' : _(u'Major 7'),
    'Major7(#5)': _(u'Major7(#5)'),
    'Minor 7' : _(u'Minor 7'),
    'Dominant 7' : _(u'Dominant 7'),
    'Minor7b5' : _(u'Minor 7b5'),
    'Major' : _(u'Major'),
    'Minor' : _(u'Minor'),
    'Diminished' : _(u'Diminished'),
    'Diminished 7' : _(u'Diminished 7'),
    'Augmented' : _(u'Augmented'),
    'Altered 7' : _(u'Altered 7'),
    'MinMaj7' : _(u'MinMaj7'),
    '7 #5' : _(u'7 #5'),
    '6 #5' : _(u'6 #5'),
}

class ChordChoicesField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = tuple(sorted(CHORD_CHOICES.items()))
        kwargs['max_length'] = 20
        super(ChordChoicesField, self).__init__(*args, **kwargs)
