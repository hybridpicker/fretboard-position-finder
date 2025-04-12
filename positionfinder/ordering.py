from positionfinder.models_chords import ChordNotes

def re_ordering(type, order):
    chords = ChordNotes.objects.filter(type_name=type)
    for x in chords:
         x.ordering = order
         x.save()
