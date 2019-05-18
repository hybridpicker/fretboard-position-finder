from django.utils.translation import gettext as _
from django.db import models
from .models import Notes

# Classes for Fingering Positions

class NotesPosition(models.Model):
    notes_name = models.ForeignKey(
        Notes,
        on_delete=models.CASCADE,)
    position_order = models.IntegerField(_(u'Order of Position'))
    position = models.CharField(_(u'position'), max_length=25,
                                help_text='2,3,4,5')
    def __str__(self):
        return '%s - %s' % (self.position_order, self.notes_name)

    class Meta:
        ordering = ('notes_name', 'position_order')
        verbose_name = u'notes position'
        verbose_name_plural = u'notes positions'
