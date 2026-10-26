from django.contrib import admin

from .models import Notes, NotesCategory, Root
from .models_chords import ChordNotes, ChordPosition
from .positions import NotesPosition

admin.site.register(Root)
admin.site.register(Notes)
admin.site.register(NotesCategory)
admin.site.register(NotesPosition)
admin.site.register(ChordNotes)
admin.site.register(ChordPosition)
