from django.db import models
from django.utils.translation import ugettext as _
from django.db.models import SmallIntegerField

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
