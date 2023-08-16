from django.db import models
from django.utils.translation import gettext as _
from django.db.models import SmallIntegerField

STRING_CHOICES = {
    'eString' : _(u'eString'),
    'bString' : _(u'bString'),
    'gString' : _(u'gString'),
    'dString' : _(u'dString'),
    'AString' : _(u'AString'),
    'ELowString' : _(u'ELowString'),
}

class StringChoicesField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = tuple(sorted(STRING_CHOICES.items()))
        kwargs['max_length'] = 20
        super(StringChoicesField, self).__init__(*args, **kwargs)
