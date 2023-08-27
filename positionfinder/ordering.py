from positionfinder.models_chords import ChordNotes

def re_ordering(type, order):
    """Re-orders the chords based on the given type and order."""
    
    # Fetch all chords of the specified type from the database
    chords = ChordNotes.objects.filter(type_name=type)
    
    # Update the ordering field for each chord and save it back to the database
    for x in chords:
        x.ordering = order
        x.save()
