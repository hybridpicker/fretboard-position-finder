from django.db import models
from django.utils.translation import gettext_lazy as _

from .models import Notes

# Classes for Fingering Positions


class NotesPosition(models.Model):
    """A fingering position (fret list) belonging to a Notes row."""

    notes_name = models.ForeignKey(
        Notes,
        on_delete=models.CASCADE,
    )
    position_order = models.IntegerField(_("Order of Position"))
    position = models.CharField(_("position"), max_length=25, help_text="2,3,4,5")

    def __str__(self) -> str:
        return "%s - %s" % (self.position_order, self.notes_name)

    class Meta:
        """Model options."""

        ordering = ("notes_name", "position_order")
        verbose_name = "notes position"
        verbose_name_plural = "notes positions"
