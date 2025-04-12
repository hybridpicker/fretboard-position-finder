
import os
import sys
import django

# Add the project directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fretboard.settings")
django.setup()

from positionfinder.models import Notes

print('Notes entries with pentatonic in the name:')
for note in Notes.objects.filter(note_name__icontains='pentatonic'):
    print(f'ID: {note.id}, Name: {note.note_name}, Category: {note.category_id}')

print('\nChecking specific IDs:')
try:
    note4 = Notes.objects.filter(id=4).first()
    if note4:
        print(f'ID 4: {note4.note_name}, Category: {note4.category_id}')
    else:
        print('ID 4 not found')
except Exception as e:
    print(f'Error checking ID 4: {e}')

try:    
    note49 = Notes.objects.filter(id=49).first()
    if note49:
        print(f'ID 49: {note49.note_name}, Category: {note49.category_id}')
    else:
        print('ID 49 not found')
except Exception as e:
    print(f'Error checking ID 49: {e}')
