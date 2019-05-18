from django.utils.translation import gettext as _
from django.db import models

from .models import NotesCategory
from .string_choices import StringChoicesField
from .chord_position_choices import ChordInversionChoicesField
from .string_range_choices import StringRangeChoicesField
from .notes_choices import NotesChoicesField, ChordChoicesField

class ChordNotes(models.Model):
    category = models.ForeignKey(
        NotesCategory,
        on_delete=models.CASCADE,)
    type_name = models.CharField(max_length=30)
    chord_name = ChordChoicesField(_("Chord Name"), default="Major 7")
    range = StringRangeChoicesField(_("String Range"), default="e - g")
    tonal_root = models.IntegerField(default=0, help_text='defines the tonal space')
    first_note = NotesChoicesField(_("First Note"), default=0)
    first_note_string = StringChoicesField(_("String for Note"),
                                           null=True, blank=True)
    second_note = NotesChoicesField(_("Second Note"),
                                    null=True, blank=True)
    second_note_string = StringChoicesField(_("String for Note"),
                                            null=True, blank=True)
    third_note = NotesChoicesField(_("Third Note"),
                                   null=True, blank=True)
    third_note_string = StringChoicesField(_("String for Note"),
                                           null=True, blank=True)
    fourth_note = NotesChoicesField(_("Fourth Tone"),
                                    null=True, blank=True)
    fourth_note_string = StringChoicesField(_("String for Note"),
                                            null=True, blank=True)
    fifth_note = NotesChoicesField(_("Sixth Tone"),
                                   null=True, blank=True)
    fifth_note_string = StringChoicesField(_("String for Note"),
                                           null=True, blank=True)
    sixth_note = NotesChoicesField(_("Seventh Tone"),
                                   null=True, blank=True)
    sixth_note_string = StringChoicesField(_("String for Note"),
                                           null=True, blank=True)

    def __str__(self):
        return '%s : %s (%s)' % (self.type_name, self.chord_name,
                                      self.range)

    class Meta:
        verbose_name = u'Tones for Chord'
        verbose_name_plural = u'Tones for Chords'

class ChordPosition(models.Model):
    notes_name = models.ForeignKey(
        ChordNotes,
        on_delete=models.CASCADE,)
    inversion_order = ChordInversionChoicesField(_("Inversion for Chord"),
                                                 null=True, blank=True)
    first_note = models.IntegerField(default=0)
    second_note = models.IntegerField(null=True, blank=True)
    third_note = models.IntegerField(null=True, blank=True)
    fourth_note = models.IntegerField(null=True, blank=True)
    fifth_note = models.IntegerField(null=True, blank=True)
    sixth_note = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return '%s : %s %s' % (self.inversion_order,
                               self.notes_name.type_name,
                               self.notes_name.chord_name)

    class Meta:
        ordering = ('notes_name', 'inversion_order')
        verbose_name = u'Chord position'
        verbose_name_plural = u'Chord positions'
