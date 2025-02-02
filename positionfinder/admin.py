# positionfinder/admin.py
from django.contrib import admin
from .models import Notes, Root, NotesCategory
from .positions import NotesPosition
from .models_chords import ChordNotes, ChordPosition

admin.site.register(Root)
admin.site.register(Notes)
admin.site.register(NotesCategory)
admin.site.register(NotesPosition)
admin.site.register(ChordNotes)
admin.site.register(ChordPosition)
