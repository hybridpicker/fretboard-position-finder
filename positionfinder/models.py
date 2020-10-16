from django.utils.translation import gettext as _
from django.db import models

class Root(models.Model):
    name = models.CharField(max_length=30)
    pitch = models.IntegerField()
    def __str__(self):
        return str(self.name)

    class Meta:
        '''
        Meta class for Root
        '''
        ordering = ('pitch', 'name')
        verbose_name = u'Rootnote'
        verbose_name_plural = u'Rootnotes'

class NotesCategory(models.Model):
    category_name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.category_name)

    class Meta:
        verbose_name = u'category name'
        verbose_name_plural = u'category names'

class Notes(models.Model):
    category = models.ForeignKey(
        NotesCategory,
        on_delete=models.CASCADE,)
    note_name = models.CharField(max_length=30)
    ordering = models.IntegerField(null=True, blank=True)
    tonal_root = models.IntegerField(default=0, help_text='defines the tonal space of the notes')
    first_note = models.IntegerField(default=0)
    second_note = models.IntegerField(null=True, blank=True)
    third_note = models.IntegerField(null=True, blank=True)
    fourth_note = models.IntegerField(null=True, blank=True)
    fifth_note = models.IntegerField(null=True, blank=True)
    sixth_note = models.IntegerField(null=True, blank=True)
    seventh_note = models.IntegerField(null=True, blank=True)
    eigth_note = models.IntegerField(null=True, blank=True)
    ninth_note = models.IntegerField(null=True, blank=True)
    tenth_note = models.IntegerField(null=True, blank=True)
    eleventh_note = models.IntegerField(null=True, blank=True)
    twelth_note = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return '%s : %s' % (self.category, self.note_name)

    class Meta:
        ordering = ['ordering', 'note_name']
        verbose_name = u'Tones for Scale'
        verbose_name_plural = u'Tones for Scales'
