from django.db import models
from django.utils.translation import gettext as _

# Define choices for chord inversions
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
    """A custom field for chord inversion selection."""
    
    def __init__(self, *args, **kwargs):
        # Sort and set the choices for the field
        kwargs['choices'] = tuple(sorted(INVERSION_CHOICES.items()))
        # Set the maximum length for the field
        kwargs['max_length'] = 20
        super(ChordInversionChoicesField, self).__init__(*args, **kwargs)
