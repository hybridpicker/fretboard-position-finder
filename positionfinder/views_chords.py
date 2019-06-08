import json
from django import forms
from django.shortcuts import render, redirect

from .models import Root, NotesCategory
from .models_chords import ChordNotes, ChordPosition

from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ObjectDoesNotExist

from .root_chord_note_setup import get_root_note
from .functionalty_chord_tones_setup import get_functionalty_note_names

from .get_position_dict_chords import get_position_dict

'''
Main View
'''
def fretboard_chords_view (request):
    ''' Select which notes '''
    category = NotesCategory.objects.all()
    '''
    Template Variables
    '''
    selected_category = 3
    category_id = 3
    position_id = 0
    root_id = 1
    notes_options_id = ChordNotes.objects.all().first().id
    tonal_root = 0

    '''
    Requesting GET form
    '''
    if request.method == 'GET':
        '''
        Template View
        '''
        try:
            root_id = request.GET['root']
        except MultiValueDictKeyError:
            root_id = 1
        try:
            category_id = request.GET['models_select']
        except MultiValueDictKeyError:
            category_id = 3
        try:
            type_id = request.GET['type_options_select']
        except MultiValueDictKeyError:
            type_id = 'V2'
        try:
            chord_select_name = request.GET['chords_options_select']
        except MultiValueDictKeyError:
            chord_select_name = 'Major 7'

    '''
    Redirecting to other views if category is clicked
    '''
    if category_id == '2':
        return redirect('show_arpeggio_fretboard')
    elif category_id == '1':
        return redirect('show_scale_fretboard')

    # Getting Tonal Root from selected Chord Object
    tonal_root = ChordNotes.objects.get(chord_name=chord_select_name, type_name=type_id).tonal_root

    notes_options = ChordNotes.objects.filter(category=category_id)
    root_options = Root.objects.all()
    root_pitch = Root.objects.get(id=root_id).pitch
    selected_root_name = Root.objects.get(id=root_id).name
    selected_note_option = ChordNotes.objects.get(chord_name=chord_select_name, type_name=type_id)
    type_name = selected_note_option.type_name
    chord_name = selected_note_option.chord_name
    range_options = ChordNotes.objects.filter(type_name=type_name,
                    chord_name=chord_name).values_list('range', flat=True).order_by('id')
    range_options = ChordNotes.objects.filter(type_name__in=[type_name],
                                              chord_name__in=[chord_name])
    type_options = ChordNotes.objects.all().values_list('type_name', flat=True).distinct()
    selected_category = int(category_id)
    notes_options_id = ChordNotes.objects.get(chord_name=chord_select_name, type_name=type_id).id
    print(notes_options_id)
    position_options = ChordPosition.objects.filter(notes_name_id=notes_options_id)
    print(position_options)
    chord_options = ChordNotes.objects.all().values_list('chord_name', flat=True).distinct()

    ## Creating List of available Root Pitches ##
    root = get_root_note(root_pitch, tonal_root, root_id)
    ## Getting Chord Notes in chronological Order as a [list] ##
    note_names = get_functionalty_note_names(notes_options_id, root_pitch, tonal_root, root_id)
    chord_json_data = {"chord": selected_note_option.chord_name,
                       "type": selected_note_option.type_name,
                       "root": root}
    # Creating for every String Range available Inversions #
    position_json_data = {}
    for option in range_options:
        for position in position_options:
            position_json_data[position.inversion_order] = [get_position_dict(position.inversion_order,
                                                                              notes_options_id,
                                                                              root_pitch,
                                                                              tonal_root,
                                                                              selected_root_name)]
        chord_json_data[option.range] = position_json_data

    chord_json_data = json.dumps(chord_json_data)
    print(chord_json_data)
    print(root_id)
    # notes data
    context = {
        'selected_chord': selected_note_option.chord_name,
        'root_id': root_id,
        'root_name': selected_root_name,
        'root_options': root_options,
        'notes_options': notes_options,
        'selected_category': selected_category,
        'category': category,
        'position_options': position_options,
        'range_options': range_options,
        'type_options': type_options,
        'chord_json_data': chord_json_data,
        'chord_options': chord_options,
        }
    return render(request, 'fretboard_chords.html', context)
