# positionfinder/views_arpeggio.py
import json
from django import forms
from django.shortcuts import render, redirect

from .models import Notes, Root, NotesCategory
from .positions import NotesPosition
from .note_setup import get_notes_tones
from .root_note_setup import get_root_note
from .functionality_tones_setup import get_functionality_tones, get_functionality_pitches
from. functionality_tones_setup import get_functionality_note_names
from .get_position import get_notes_position
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ObjectDoesNotExist
from .template_notes import ALL_NOTES_POSITION

from .get_position_dict_scales import get_scale_position_dict, get_transposable_positions
from .get_position_dict_scales import transpose_actual_position, re_ordering_positions

from django.shortcuts import render
from positionfinder.models import Notes  # For Scales and Arpeggios
from positionfinder.views_helpers import get_menu_options

def arpeggio_list(request):
    arpeggios = Notes.objects.filter(category_id=2)  # ID 2 = Arpeggios
    menu_options = get_menu_options()
    print("Arpeggios View:", menu_options)  # Debugging output
    return render(request, 'arpeggio_list.html', {'arpeggios': arpeggios, **menu_options})



def fretboard_arpeggio_view (request):
    ''' Select which notes '''
    all_notes_position = ALL_NOTES_POSITION
    category = NotesCategory.objects.all()
    menu_options = get_menu_options() 
    '''
    Template Variables
    '''
    selected_category = 2
    root_id = 1
    root_pitch = 0
    tonal_root = 0
    category_id = 2
    notes_options_id = 2

    if request.method == 'GET':
        '''
        Template View
        '''
        position = all_notes_position
        try:
            root_id = request.GET['root']
        except MultiValueDictKeyError:
            root_id = 1
        try:
            category_id = request.GET['models_select']
        except MultiValueDictKeyError:
            category_id = 2
        try:
            position_id = request.GET['position_select']
        except MultiValueDictKeyError:
            position_id = '0'
        try:
            notes_options_id = request.GET['notes_options_select']
        except MultiValueDictKeyError:
            notes_options_id = '2'


    if category_id == '1':
        return redirect('show_scale_fretboard')
    if category_id == '3':
        return redirect('show_chords_fretboard')

    notes_options = Notes.objects.filter(category_id=category_id).first().pk

    root_pitch = Root.objects.get(pk=root_id).pitch
    notes_options = Notes.objects.filter(category=category_id)
    if position_id != '0':
        try:
            position = get_notes_position(position_id, root_pitch)
        except ObjectDoesNotExist:
            position = all_notes_position
    else:
        position = all_notes_position
    position_options = NotesPosition.objects.filter(notes_name=notes_options_id)
    tones = get_notes_tones(notes_options_id, root_pitch, tonal_root, root_id)
    tensions = get_functionality_tones(notes_options_id, root_pitch)
    root = get_root_note(root_pitch, tonal_root, root_id)

    position_options = NotesPosition.objects.filter(notes_name=notes_options_id)
    root_options = Root.objects.all()

    selected_category = int(category_id)
    selected_notes = int(notes_options_id)
    if position_id is not None:
        selected_position = int(position_id)
    else:
        selected_position = 0

    '''
    Controlling Lines
    '''
    try:
        selected_category_name = NotesCategory.objects.get(pk=category_id).category_name
    except NotesCategory.DoesNotExist:
        selected_category_name = NotesCategory.objects.first().category_name
    selected_root_name = Root.objects.get(pk=root_id).name
    selected_root_id = Root.objects.get(pk=root_id).id
    if position_id != '0':
        try:
            selected_position_name = NotesPosition.objects.get(pk=position_id).position_order
            selected_position_name = 'Position: ' + str(selected_position_name)
        except NotesPosition.DoesNotExist:
            selected_position_name = 'All Notes'
    else:
        selected_position_name = 'All Notes'

    selected_notes_name = Notes.objects.get(pk=notes_options_id).note_name

    note_names = get_functionality_note_names(notes_options_id, root_pitch, tonal_root, root_id)
    tension_pitches = get_functionality_pitches(notes_options_id, root_pitch)

    tensions_json_data = {"tensions": tensions}
    tension_json_data = json.dumps(tensions_json_data)
    note_name_json_data = {"tones": note_names}
    note_name_json_data = json.dumps(note_name_json_data)

    position_json_data = {}
    position_json_data = get_scale_position_dict(selected_notes_name,
                                                 selected_root_id,
                                                 root_pitch,
                                                 tonal_root,
                                                 selected_root_name)

    if len(position_json_data) > 1:
        # Get Meta-Data for transposable position function
        x = Notes.objects.get(id=notes_options_id).note_name
        y = len(NotesPosition.objects.all().filter(notes_name__note_name=x))
        transposable_position = get_transposable_positions(y, position_json_data)

        # Transpose position that transposable
        position_json_data = transpose_actual_position(position_json_data, transposable_position)

        # ReOrdering Positions
        position_json_data = re_ordering_positions(position_json_data)
    
    selected_root_options = get_root_note(root_pitch, tonal_root, root_id)
    position_json_data["name"] = selected_notes_name
    position_json_data["root"] = selected_root_options

    scale_json_data = json.dumps(position_json_data)

    # notes data
    selected_position = position_id


    # String Names for template
    string_names = ["eString", "bString", "gString", "dString", "AString", "ELowString"]
    

    context = {
        'scale_json_data': scale_json_data,

        'tension_json_data': tension_json_data,
        'note_name_json_data': note_name_json_data,
        'tones': tones,
        'root': root,

        'root_options': root_options,
        'position_options': position_options,
        'position': position,
        'category': category,
        'selected_category': selected_category,
        'notes_options': notes_options,
        'selected_notes': selected_notes,
        'selected_position': selected_position,

        'tensions': tensions,
        'tension_pitches': tension_pitches,
        'note_names': note_names,

        'selected_root_name': selected_root_name,
        'selected_root_id': selected_root_id,
        'selected_category_name': selected_category_name,
        'selected_notes_name': selected_notes_name,

        'string_names': string_names,
        }
    
    context.update(menu_options)

    return render(request, 'fretboard.html', context)
