from django.db import models
from django.utils.translation import gettext_lazy as _

INVERSION_CHOICES = {
    "Basic Position": _("Basic Position"),
    "First Inversion": _("First Inversion"),
    "Second Inversion": _("Second Inversion"),
    "Third Inversion": _("Third Inversion"),
    "Fourth Inversion": _("Fourth Inversion"),
    "Fifth Inversion": _("Fifth Inversion"),
    "Sixth Inversion": _("Sixth Inversion"),
}


class ChordInversionChoicesField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = tuple(sorted(INVERSION_CHOICES.items()))
        kwargs["max_length"] = 20
        super().__init__(*args, **kwargs)
