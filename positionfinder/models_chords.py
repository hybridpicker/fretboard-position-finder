from django.utils.translation import gettext as _
from django.db import models

from .models import NotesCategory
from .string_choices import StringChoicesField
from .chord_position_choices import ChordInversionChoicesField
from .string_range_choices import StringRangeChoicesField
from .notes_choices import NotesChoicesField, ChordChoicesField

def create_base_position(id):
    chord = ChordNotes.objects.get(id=id)
    base_position = ChordPosition.objects.create(notes_name_id=chord.id,
                                                 inversion_order='Basic Position',
                                                 first_note=0,
                                                 second_note=0,
                                                 third_note=0,
                                                 fourth_note=0,)


def create_chord(id):
    chord = ChordNotes.objects.get(id=id)

    if chord.chord_name == 'Major 7':
        major_7 = ChordNotes.objects.get(id=id)
        minor_7 = ChordNotes.objects.create(category_id=major_7.category.id,
                                            type_name=major_7.type_name,
                                            chord_name='Minor 7', range=major_7.range,
                                            tonal_root=major_7.tonal_root,
                                            first_note=major_7.first_note,
                                            first_note_string=major_7.first_note_string,
                                            second_note=major_7.second_note - 1,
                                            second_note_string=major_7.second_note_string,
                                            third_note=major_7.third_note,
                                            third_note_string=major_7.third_note_string,
                                            fourth_note=major_7.fourth_note - 1,
                                            fourth_note_string=major_7.fourth_note_string)

        minor_7_b5 = ChordNotes.objects.create(category_id=minor_7.category.id,
                                            type_name=minor_7.type_name,
                                            chord_name='Minor 7b5', range=minor_7.range,
                                            tonal_root=minor_7.tonal_root,
                                            first_note=minor_7.first_note,
                                            first_note_string=minor_7.first_note_string,
                                            second_note=minor_7.second_note,
                                            second_note_string=minor_7.second_note_string,
                                            third_note=minor_7.third_note - 1,
                                            third_note_string=minor_7.third_note_string,
                                            fourth_note=minor_7.fourth_note,
                                            fourth_note_string=minor_7.fourth_note_string)

        dominant_7 = ChordNotes.objects.create(category_id=major_7.category.id,
                                            type_name=major_7.type_name,
                                            chord_name='Dominant 7', range=major_7.range,
                                            tonal_root=major_7.tonal_root,
                                            first_note=major_7.first_note,
                                            first_note_string=major_7.first_note_string,
                                            second_note=major_7.second_note,
                                            second_note_string=major_7.second_note_string,
                                            third_note=major_7.third_note,
                                            third_note_string=major_7.third_note_string,
                                            fourth_note=major_7.fourth_note - 1,
                                            fourth_note_string=major_7.fourth_note_string)

        base_position = create_base_position(id)
        base_position = create_base_position(minor_7.id)
        base_position = create_base_position(minor_7_b5.id)
        base_position = create_base_position(dominant_7.id)

## TODO find pattern for saving automatically other inversions ###
def create_four_note_inversions(id):
    chord = ChordPosition.objects.get(id=id)
    if chord.notes_name.chord_name == 'Major 7' and chord.inversion_order != 'Basic Position':
        major_7 = chord
        minor_7 = ChordPosition.objects.create(notes_name_id=major_7.notes_name.id + 1,
                                            inversion_order=major_7.inversion_order,
                                            first_note=major_7.first_note,
                                            second_note=major_7.second_note,
                                            third_note=major_7.third_note,
                                            fourth_note=major_7.fourth_note,)
        minor_7_b5 = ChordPosition.objects.create(notes_name_id=major_7.notes_name.id + 2,
                                            inversion_order=major_7.inversion_order,
                                            first_note=major_7.first_note,
                                            second_note=major_7.second_note,
                                            third_note=major_7.third_note,
                                            fourth_note=major_7.fourth_note,)
        dominant_7 = ChordPosition.objects.create(notes_name_id=major_7.notes_name.id + 3,
                                            inversion_order=major_7.inversion_order,
                                            first_note=major_7.first_note,
                                            second_note=major_7.second_note,
                                            third_note=major_7.third_note,
                                            fourth_note=major_7.fourth_note,)
    else:
        pass

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
    def save(self, *args, **kwargs):
        super(ChordNotes, self).save(*args, **kwargs)
        create_chords = create_chord(self.id)


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

    def save(self, *args, **kwargs):
        super(ChordPosition, self).save(*args, **kwargs)

    def __str__(self):
        return '%s : %s %s' % (self.inversion_order,
                               self.notes_name.type_name,
                               self.notes_name.chord_name)

    class Meta:
        ordering = ('notes_name', 'inversion_order')
        verbose_name = u'Chord position'
        verbose_name_plural = u'Chord positions'
