#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fretboard.settings')
django.setup()

from positionfinder.models import NotesCategory
from positionfinder.models_chords import ChordNotes
from django.db.models import Q

# Check for arpeggio category
print("Checking for arpeggio category...")
arpeggio_categories = NotesCategory.objects.filter(category_name__icontains='arpeggio')
print(f"Arpeggio categories found: {arpeggio_categories.count()}")
for cat in arpeggio_categories:
    print(f"ID: {cat.id}, Name: {cat.category_name}")

# Check for any chords that might be categorized as arpeggios
print("\nChecking for chords that might be categorized as arpeggios...")
# Try to find any chords with category related to arpeggios
chords = ChordNotes.objects.filter(category__category_name__icontains='arpeggio')
print(f"ChordNotes entries with arpeggio category: {chords.count()}")

# Try to find any chords with type_name related to arpeggios
arpeggio_type_chords = ChordNotes.objects.filter(type_name__icontains='arpeggio')
print(f"ChordNotes entries with arpeggio in type_name: {arpeggio_type_chords.count()}")

# Check all NotesCategory entries
print("\nListing all NotesCategory entries...")
all_categories = NotesCategory.objects.all()
print(f"Total categories: {all_categories.count()}")
for cat in all_categories:
    print(f"ID: {cat.id}, Name: {cat.category_name}")

# Look for minor arpeggios in ChordNotes
print("\nLooking for minor arpeggios...")
minor_arpeggios = ChordNotes.objects.filter(
    Q(chord_name__icontains='minor') | Q(chord_name__icontains='m')
)
print(f"ChordNotes entries with 'minor' in chord_name: {minor_arpeggios.count()}")

# Check specifically for A minor
print("\nChecking for A minor chords...")
a_minor = ChordNotes.objects.filter(
    Q(tonal_root=14) & (Q(chord_name__icontains='minor') | Q(chord_name__icontains='m'))
)
print(f"ChordNotes entries for A minor: {a_minor.count()}")

# Show the first few ChordNotes records
print("\nShowing sample ChordNotes records...")
sample_chords = ChordNotes.objects.all()[:5]
for chord in sample_chords:
    print(f"ID: {chord.id}, Category: {chord.category}, Type: {chord.type_name}, Name: {chord.chord_name}, Root: {chord.tonal_root}")
