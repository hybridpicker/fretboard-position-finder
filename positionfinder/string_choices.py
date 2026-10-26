from django.db import models
from django.utils.translation import gettext_lazy as _

# String choices for 6, 7, and 8-string guitars
# Ordered numerically by string number (0th - 7th)
STRING_CHOICES = {
    "highAString": _("High A String (0th)"),  # 8-string
    "eString": _("High E String (1st)"),  # Standard 6-string
    "bString": _("B String (2nd)"),  # Standard 6-string
    "gString": _("G String (3rd)"),  # Standard 6-string
    "dString": _("D String (4th)"),  # Standard 6-string
    "AString": _("A String (5th)"),  # Standard 6-string
    "ELowString": _("Low E String (6th)"),  # Standard 6-string
    "lowBString": _("Low B String (7th)"),  # 7-string
}

# Tuning notes for reference - standard tunings
TUNING_NOTES = {
    "6-string": ["E4", "B3", "G3", "D3", "A2", "E2"],
    "7-string": ["E4", "B3", "G3", "D3", "A2", "E2", "B1"],
    "8-string": ["A4", "E4", "B3", "G3", "D3", "A2", "E2", "B1"],  # High A variant
}


class StringChoicesField(models.CharField):
    def __init__(self, *args, **kwargs):
        # Note: Django choices are often sorted alphabetically by key by default in forms/admin.
        # The order here primarily affects readability of this definition.
        kwargs["choices"] = tuple(STRING_CHOICES.items())  # Keep definition order
        # If strict alphabetical sorting is desired for the field:
        # kwargs['choices'] = tuple(sorted(STRING_CHOICES.items()))
        kwargs["max_length"] = 20
        super().__init__(*args, **kwargs)
