#!/usr/bin/env python
"""
Script to clean up the ChordNotes table by removing any scale or arpeggio entries
that should not be in the Chord Nodes section.
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fretboard.settings')
django.setup()

from positionfinder.models_chords import ChordNotes
from positionfinder.models import Notes, NotesCategory
from django.db.models import Q

def find_scale_arpeggio_entries():
    """
    Find entries in ChordNotes that appear to be scales or arpeggios based on 
    naming patterns and structure.
    """
    # Patterns that indicate scale entries
    scale_patterns = [
        'pentatonic', 'blues scale', 'dorian', 'phrygian', 'lydian', 
        'mixolydian', 'locrian', 'harmonic minor', 'melodic minor',
        'natural minor', 'ionian'
    ]
    
    # Patterns that indicate arpeggio entries
    arpeggio_patterns = [
        'arpeggio', 'arpegg'
    ]
    
    # Build query for scales
    scale_query = Q()
    for pattern in scale_patterns:
        scale_query |= Q(chord_name__icontains=pattern)
    
    # Build query for arpeggios
    arpeggio_query = Q()
    for pattern in arpeggio_patterns:
        arpeggio_query |= Q(chord_name__icontains=pattern) | Q(type_name__icontains=pattern)
    
    # Get potential scale and arpeggio entries
    scale_entries = ChordNotes.objects.filter(scale_query)
    arpeggio_entries = ChordNotes.objects.filter(arpeggio_query)
    
    print(f"Found {scale_entries.count()} potential scale entries in ChordNotes")
    for entry in scale_entries:
        print(f"- ID: {entry.id}, Type: {entry.type_name}, Name: {entry.chord_name}")
    
    print(f"\nFound {arpeggio_entries.count()} potential arpeggio entries in ChordNotes")
    for entry in arpeggio_entries:
        print(f"- ID: {entry.id}, Type: {entry.type_name}, Name: {entry.chord_name}")
    
    return scale_entries, arpeggio_entries

def delete_invalid_entries(scale_entries, arpeggio_entries, confirm=True):
    """
    Delete the identified scale and arpeggio entries from ChordNotes.
    
    Args:
        scale_entries: QuerySet of scale entries to delete
        arpeggio_entries: QuerySet of arpeggio entries to delete
        confirm: If True, asks for confirmation before deleting
    """
    total_to_delete = scale_entries.count() + arpeggio_entries.count()
    
    if total_to_delete == 0:
        print("No entries to delete.")
        return
    
    print(f"\nPreparing to delete {total_to_delete} entries from ChordNotes:")
    print(f"- {scale_entries.count()} scale entries")
    print(f"- {arpeggio_entries.count()} arpeggio entries")
    
    if confirm:
        response = input("\nAre you sure you want to delete these entries? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled.")
            return
    
    # Delete the entries
    scale_ids = [entry.id for entry in scale_entries]
    arpeggio_ids = [entry.id for entry in arpeggio_entries]
    
    # Delete entries one by one and track success
    deleted_count = 0
    
    print("\nDeleting scale entries...")
    for entry_id in scale_ids:
        try:
            entry = ChordNotes.objects.get(id=entry_id)
            print(f"Deleting: ID {entry.id} - {entry.chord_name}")
            entry.delete()
            deleted_count += 1
        except Exception as e:
            print(f"Error deleting entry ID {entry_id}: {str(e)}")
    
    print("\nDeleting arpeggio entries...")
    for entry_id in arpeggio_ids:
        try:
            entry = ChordNotes.objects.get(id=entry_id)
            print(f"Deleting: ID {entry.id} - {entry.chord_name}")
            entry.delete()
            deleted_count += 1
        except Exception as e:
            print(f"Error deleting entry ID {entry_id}: {str(e)}")
    
    print(f"\nSuccessfully deleted {deleted_count} of {total_to_delete} entries.")

if __name__ == "__main__":
    print("Scanning ChordNotes for scale and arpeggio entries...")
    scale_entries, arpeggio_entries = find_scale_arpeggio_entries()
    
    delete_invalid_entries(scale_entries, arpeggio_entries)
    
    print("\nDatabase cleanup complete!")
