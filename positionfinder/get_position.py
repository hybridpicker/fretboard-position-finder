from .positions import NotesPosition

def get_notes_position(position_id, root):
    position = NotesPosition.objects.get(pk=position_id).position
    # Handle empty position data
    if not position or position.strip() == '':
        return []
    # Transform into List and add root_pitch
    position_list = [int(x) + int(root) for x in position.split(',') if x.strip()]
    # Check if every item in list is not bigger than fretboard
    check_range = all(x <= 17 for x in position_list)
    if check_range:
        return position_list
    else:
        # minus octave
        position_list = [x - 12 for x in position_list]
        return position_list
