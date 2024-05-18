import json
from django import forms
from django.shortcuts import render, redirect

from .models import Root, NotesCategory
from .models_chords import ChordNotes, ChordPosition

from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist

from .root_chord_note_setup import get_root_note
from .functionality_chord_tones_setup import get_functionality_note_names

from .get_position_dict_chords import get_position_dict

from positionfinder.views_helpers import get_menu_options

'''
Main View
'''
def fretboard_chords_view(request):
    ''' Select which notes '''
    category = NotesCategory.objects.all()
    menu_options = get_menu_options()
    '''
    Template Variables
    '''
    selected_category = 3
    category_id = 3
    position_id = 0
    root_id = 1
    notes_options_id = ChordNotes.objects.all().first().id
    tonal_root = 0
    range = 'e - g'
    chord_select_name = 'Major 7'
    type_id = 'V2'
    selected_range = 'e - g'  # Initialisiere selected_range

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
            type_id = 'Triads'
        try:
            chord_select_name = request.GET['chords_options_select']
        except MultiValueDictKeyError:
            chord_select_name = 'Major'
        try:
            range = request.GET['note_range']
            selected_range = range  # Aktualisiere selected_range
        except MultiValueDictKeyError:
            range = 'e - g'
            selected_range = range

    '''
    Redirecting to other views if category is clicked
    '''
    if category_id == '2':
        return redirect('show_arpeggio_fretboard')
    elif category_id == '1':
        return redirect('show_scale_fretboard')

    # Getting Tonal Root from selected Chord Object
    try:
        chord_object = ChordNotes.objects.get(chord_name=chord_select_name,
                                              type_name=type_id, range=range)
    except ObjectDoesNotExist:
        try:
            chord_object = ChordNotes.objects.get(chord_name=chord_select_name,
                                                  type_name=type_id)
        except ObjectDoesNotExist:
            chord_object = ChordNotes.objects.filter(type_name=type_id).first()
        except MultipleObjectsReturned:
            chord_object = ChordNotes.objects.filter(chord_name=chord_select_name,
                                                     type_name=type_id).first()

    tonal_root = chord_object.tonal_root
    notes_options = ChordNotes.objects.filter(category=category_id)
    root_options = Root.objects.all()
    root_pitch = Root.objects.get(id=root_id).pitch
    selected_root_name = Root.objects.get(id=root_id).name
    selected_note_option = chord_object

    type_name = selected_note_option.type_name
    chord_name = selected_note_option.chord_name
    range_options = ChordNotes.objects.filter(type_name__in=[type_name],
                                              chord_name__in=[chord_name]).order_by('ordering', 'range_ordering')
    first_range_option = range_options.first().range
    type_options = ChordNotes.objects.all().values_list('type_name',
                                                        flat=True).order_by('ordering').distinct()

    notes_options_id = chord_object.id

    position_options = ChordPosition.objects.filter(notes_name_id=notes_options_id)
    chord_options = ChordNotes.objects.filter(type_name=type_id).values_list('chord_name',
                                                                             flat=True).order_by('chord_ordering').distinct()
    ## Creating List of available Root Pitches ##
    root = get_root_note(root_pitch, tonal_root, root_id)
    ## Getting Chord Notes in chronological Order as a [list] ##
    chord_json_data = {
        "chord": selected_note_option.chord_name,
        "type": selected_note_option.type_name,
        "root": root,
        "note_range": range 
    }

    # Creating for every String Range available Inversions #
    position_json_data = {}
    temp_data = {}
    range_data = {}

    for option in range_options:
        temp_data = {}
        range_data = {}

        for position in position_options:
            position_json_data = {
                position.inversion_order: [
                    get_position_dict(position.inversion_order,
                                      chord_name,
                                      option.range,
                                      type_name,
                                      root_pitch,
                                      tonal_root,
                                      selected_root_name)
                ]
            }
            range_data[position.inversion_order] = position_json_data[position.inversion_order]

            temp_data[option.range] = range_data
        chord_json_data[option.range] = range_data
        position_json_data = {}

    chord_json_data = json.dumps(chord_json_data)
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
        'selected_type': type_id,
        'first_range_option': first_range_option,
        'note_range': range,
        'selected_range': selected_range,
    }

    context.update(menu_options)

    return render(request, 'fretboard.html', context)
