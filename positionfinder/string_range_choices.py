from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import SmallIntegerField

STRING_RANGE_CHOICES = {
    # Standard 6-string ranges
    'a - b': _(u'a - b'),
    'e - g': _(u'e - g'),
    'b - d': _(u'b - d'),
    'g - A': _(u'g - A'),
    'd - E': _(u'd - E'),
    'A - B': _(u'A - B'),
    'a - g': _(u'a - g'),
    'e - d': _(u'e - d'),
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
    
    # 8-string specific ranges - high range
    'highA - e': _(u'highA - e'),
    'highA - b': _(u'highA - b'),
    'highA - g': _(u'highA - g'),
    'highA - d': _(u'highA - d'),
    'highA - A': _(u'highA - A'),
    'highA - E': _(u'highA - E'),
    
    # 8-string specific ranges - full extended range
    'highA - lowB': _(u'highA - lowB'),
    
    # 8-string specific ranges - mid to low range
    'e - lowB': _(u'e - lowB'),
    'b - lowB': _(u'b - lowB'),
    'g - lowB': _(u'g - lowB'),
    'd - lowB': _(u'd - lowB'),
    'A - lowB': _(u'A - lowB'),
    'E - lowB': _(u'E - lowB'),
    
    # Additional optimized ranges for 8-string
    'highA - AString': _(u'highA - AString'),
    'highA - ELowString': _(u'highA - ELowString'),
    'bString - lowB': _(u'bString - lowB'),
    'dString - lowB': _(u'dString - lowB'),
}

class StringRangeChoicesField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = tuple(sorted(STRING_RANGE_CHOICES.items()))
        kwargs['max_length'] = 20  # Increased to accommodate longer strings like 'highA - ELowString'
        super(StringRangeChoicesField, self).__init__(*args, **kwargs)
