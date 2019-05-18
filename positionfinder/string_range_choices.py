from django.db import models
from django.utils.translation import ugettext as _
from django.db.models import SmallIntegerField

STRING_RANGE_CHOICES = {
    'e - g' : _(u'e - g'),
    'b - d' : _(u'b - d'),
    'g - A' : _(u'g - A'),
    'd - E' : _(u'd - E'),
    'e - d' : _(u'e - d'),
    'b - A' : _(u'b - A'),
    'g - E' : _(u'g - E'),
    'e - A' : _(u'e - A'),
    'b - E' : _(u'b - E'),
    'e - E' : _(u'e - E'),
}

class StringRangeChoicesField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices']=tuple(sorted(STRING_RANGE_CHOICES.items()))
        kwargs['max_length']=8
        super(StringRangeChoicesField,self).__init__(*args, **kwargs)
