import json
import subprocess

def run_query(query):
    """Run a PostgreSQL query and return the results."""
    result = subprocess.run(
        ['psql', '-U', 'postgres', '-h', 'localhost', '-d', 'fretboard', '-t', '-c', query],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def get_model_data(table_name, django_model_name, fields):
    """Get data for a model in Django fixture format."""
    field_list = ", ".join(fields)
    
    query = f"""
    SELECT json_build_object(
        'model', '{django_model_name}',
        'pk', id,
        'fields', json_build_object(
            {', '.join([f"'{field}', {field}" for field in fields])}
        )
    )
    FROM {table_name}
    ORDER BY id
    """
    
    result = run_query(query)
    entries = [json.loads(line) for line in result.split('\n') if line.strip()]
    return entries

# Create fixture data
fixture_data = []

# NotesCategory
fixture_data.extend(get_model_data(
    'positionfinder_notescategory',
    'positionfinder.notescategory',
    ['category_name']
))

# Root
fixture_data.extend(get_model_data(
    'positionfinder_root',
    'positionfinder.root',
    ['name', 'pitch']
))

# Notes
fixture_data.extend(get_model_data(
    'positionfinder_notes',
    'positionfinder.notes',
    ['category_id', 'note_name', 'ordering']
))

# NotesPosition
fixture_data.extend(get_model_data(
    'positionfinder_notesposition',
    'positionfinder.notesposition',
    ['position_order', 'notes_name_id']
))

# ChordNotes
fixture_data.extend(get_model_data(
    'positionfinder_chordnotes',
    'positionfinder.chordnotes',
    [
        'type_name', 'chord_name', 'range', 'tonal_root', 
        'first_note', 'first_note_string', 'second_note', 'second_note_string',
        'third_note', 'third_note_string', 'fourth_note', 'fourth_note_string',
        'fifth_note', 'fifth_note_string', 'sixth_note', 'sixth_note_string',
        'ordering', 'range_ordering', 'chord_ordering', 'category_id'
    ]
))

# ChordPosition
fixture_data.extend(get_model_data(
    'positionfinder_chordposition',
    'positionfinder.chordposition',
    ['inversion_order', 'notes_name_id']
))

# Write fixture data to file
with open('positionfinder/fixtures/databasedump.json', 'w') as f:
    json.dump(fixture_data, f, indent=4)

print(f"Fixture created with {len(fixture_data)} objects")
