#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fretboard.settings')
django.setup()

from positionfinder.models import NotesCategory, Root
from positionfinder.models_chords import ChordNotes
from django.db.models import Q

# Check A note mapping
print("Checking A note mapping...")
a_notes = Root.objects.filter(name__icontains='A')
for a in a_notes:
    print(f"A note: ID={a.id}, Name={a.name}, Pitch={a.pitch}")
    
# Try to find any A minor pentatonic arpeggios
print("\nLooking for A minor pentatonic arpeggios...")
a_minor_pent = ChordNotes.objects.filter(
    Q(chord_name__icontains='minor pentatonic') & 
    (Q(tonal_root=9) | Q(tonal_root=14))  # Try both 9 and 14 as potential A values
)
print(f"Found {a_minor_pent.count()} A minor pentatonic arpeggios")

for arp in a_minor_pent:
    print(f"ID: {arp.id}, Category: {arp.category}, Type: {arp.type_name}, Name: {arp.chord_name}, Root: {arp.tonal_root}, Range: {arp.range}")
    
# Show all roots
print("\nAll root notes in database:")
roots = Root.objects.all().order_by('pitch')
for r in roots:
    print(f"ID: {r.id}, Name: {r.name}, Pitch: {r.pitch}")
