# positionfinder/chord_position_choices.py
from django.db import models
from django.utils.translation import gettext as _
from django.db.models import SmallIntegerField

INVERSION_CHOICES = {
    'Basic Position' : _(u'Basic Position'),
    'First Inversion' : _(u'First Inversion'),
    'Second Inversion' : _(u'Second Inversion'),
    'Third Inversion' : _(u'Third Inversion'),
    'Fourth Inversion' : _(u'Fourth Inversion'),
    'Fifth Inversion' : _(u'Fifth Inversion'),
    'Sixth Inversion' : _(u'Sixth Inversion'),
}

class ChordInversionChoicesField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = tuple(sorted(INVERSION_CHOICES.items()))
        kwargs['max_length'] = 20
        super(ChordInversionChoicesField, self).__init__(*args, **kwargs)
