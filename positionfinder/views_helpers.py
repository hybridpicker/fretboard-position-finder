from .models import Arpeggio, Chord, Scale

def get_menu_options():
    arpeggio_options = Arpeggio.objects.values('id', 'note_name')
    chord_options = Chord.objects.values('id', 'note_name')
    scale_options = Scale.objects.values('id', 'note_name')

    return {
        'arpeggio_options': list(arpeggio_options),
        'chord_options': list(chord_options),
        'scale_options': list(scale_options),
    }
