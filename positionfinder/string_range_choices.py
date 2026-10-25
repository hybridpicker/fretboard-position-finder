from django.db import models
from django.utils.translation import gettext_lazy as _

STRING_RANGE_CHOICES = {
    # Standard 6-string ranges
    "a - b": _("a - b"),
    "e - g": _("e - g"),
    "b - d": _("b - d"),
    "g - A": _("g - A"),
    "d - E": _("d - E"),
    "A - B": _("A - B"),
    "a - g": _("a - g"),
    "e - d": _("e - d"),
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
    # 8-string specific ranges - high range
    "highA - e": _("highA - e"),
    "highA - b": _("highA - b"),
    "highA - g": _("highA - g"),
    "highA - d": _("highA - d"),
    "highA - A": _("highA - A"),
    "highA - E": _("highA - E"),
    # 8-string specific ranges - full extended range
    "highA - lowB": _("highA - lowB"),
    # 8-string specific ranges - mid to low range
    "e - lowB": _("e - lowB"),
    "b - lowB": _("b - lowB"),
    "g - lowB": _("g - lowB"),
    "d - lowB": _("d - lowB"),
    "A - lowB": _("A - lowB"),
    "E - lowB": _("E - lowB"),
    # Additional optimized ranges for 8-string
    "highA - AString": _("highA - AString"),
    "highA - ELowString": _("highA - ELowString"),
    "bString - lowB": _("bString - lowB"),
    "dString - lowB": _("dString - lowB"),
}


class StringRangeChoicesField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = tuple(sorted(STRING_RANGE_CHOICES.items()))
        kwargs["max_length"] = (
            20  # Increased to accommodate longer strings like 'highA - ELowString'
        )
        super().__init__(*args, **kwargs)
