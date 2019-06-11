from django.utils.translation import gettext as _
from django.db import models

from .models import NotesCategory
from .string_choices import StringChoicesField
from .chord_position_choices import ChordInversionChoicesField
from .string_range_choices import StringRangeChoicesField
from .notes_choices import NotesChoicesField, ChordChoicesField

def create_fourthnote_positions(w,x,y,z,chord_id):
    chord = ChordNotes.objects.get(id=chord_id)
    #First Inversion
    ChordPosition.objects.create(notes_name_id=chord.id,
                                            inversion_order='First Inversion',
                                            first_note=w,
                                            second_note=x,
                                            third_note=y,
                                            fourth_note=z,)
    #Second Inversion
    ChordPosition.objects.create(notes_name_id=chord.id,
                                            inversion_order='Second Inversion',
                                            first_note=w+x,
                                            second_note=x+y,
                                            third_note=y+z,
                                            fourth_note=z+w,)
    #Third Inversion
    ChordPosition.objects.create(notes_name_id=chord.id,
                                            inversion_order='Third Inversion',
                                            first_note=w+x+y,
                                            second_note=x+y+z,
                                            third_note=y+z+w,
                                            fourth_note=z+w+x,)

def create_base_position(id):
    chord = ChordNotes.objects.get(id=id)
    base_position = ChordPosition.objects.create(notes_name_id=chord.id,
                                                 inversion_order='Basic Position',
                                                 first_note=0,
                                                 second_note=0,
                                                 third_note=0,
                                                 fourth_note=0,)

    if not None in (chord.first_note, chord.second_note, chord.third_note, chord.fourth_note) and chord.fifth_note is None:
        id = chord.id
        w = chord.second_note - chord.first_note
        while w < 0:
            w += 12
        x = chord.third_note - chord.second_note
        while x < 0:
            x += 12
        y = chord.fourth_note - chord.third_note
        while y < 0:
            y += 12
        z = chord.first_note - chord.fourth_note
        while z < 0:
            z += 12
        create_fourthnote_positions(w,x,y,z,id)


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
