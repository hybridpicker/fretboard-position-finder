#!/usr/bin/env python
"""
Script to add missing arpeggios to the database, particularly pentatonic arpeggios
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fretboard.settings')
django.setup()

from positionfinder.models import NotesCategory
from positionfinder.models_chords import ChordNotes, create_base_position
from django.db import transaction

def create_pentatonic_arpeggios():
    """Create pentatonic arpeggios for all roots"""
    
    # Get the Arpeggios category
    arpeggio_category = NotesCategory.objects.get(category_name='Arpeggios')
    
    # Define pentatonic notes intervals
    minor_pentatonic_intervals = [0, 3, 7, 10]  # Root, b3, 5, b7
    major_pentatonic_intervals = [0, 4, 7, 9]   # Root, 3, 5, 6
    
    # Create arpeggios for each root (0-11)
    created_count = 0
    for root in range(12):
        
        # Minor Pentatonic Arpeggio
        minor_pent, created_min = ChordNotes.objects.get_or_create(
            category=arpeggio_category,
            type_name='Pentatonic',
            chord_name='Minor Pentatonic',
            range='e - E',  # Standard 6-string range
            tonal_root=root,
            defaults={
                'first_note': minor_pentatonic_intervals[0],  # Root
                'second_note': minor_pentatonic_intervals[1],  # b3
                'third_note': minor_pentatonic_intervals[2],   # 5
                'fourth_note': minor_pentatonic_intervals[3],  # b7
                'chord_ordering': 1,
                'range_ordering': 1
            }
        )
        
        if created_min:
            create_base_position(minor_pent.id)
            created_count += 1
            print(f"Created Minor Pentatonic Arpeggio for root {root}")
        
        # Major Pentatonic Arpeggio
        major_pent, created_maj = ChordNotes.objects.get_or_create(
            category=arpeggio_category,
            type_name='Pentatonic',
            chord_name='Major Pentatonic',
            range='e - E',  # Standard 6-string range
            tonal_root=root,
            defaults={
                'first_note': major_pentatonic_intervals[0],  # Root
                'second_note': major_pentatonic_intervals[1],  # 3
                'third_note': major_pentatonic_intervals[2],   # 5
                'fourth_note': major_pentatonic_intervals[3],  # 6
                'chord_ordering': 2,
                'range_ordering': 1
            }
        )
        
        if created_maj:
            create_base_position(major_pent.id)
            created_count += 1
            print(f"Created Major Pentatonic Arpeggio for root {root}")
    
    return created_count

def create_extended_arpeggios():
    """Create extended arpeggios for 8-string guitars"""
    from positionfinder.eight_string_setup import create_eight_string_ranges
    
    # Get all pentatonic arpeggios
    pentatonic_arpeggios = ChordNotes.objects.filter(
        category__category_name='Arpeggios',
        type_name='Pentatonic'
    )
    
    extended_count = 0
    for arpeggio in pentatonic_arpeggios:
        # Create 8-string versions
        extended_arpeggios = create_eight_string_ranges(arpeggio.id)
        extended_count += len(extended_arpeggios)
        print(f"Created {len(extended_arpeggios)} extended ranges for {arpeggio.chord_name} root {arpeggio.tonal_root}")
    
    return extended_count

if __name__ == "__main__":
    with transaction.atomic():
        print("Adding pentatonic arpeggios to database...")
        created = create_pentatonic_arpeggios()
        print(f"Created {created} new pentatonic arpeggios")
        
        print("\nCreating extended 8-string versions...")
        extended = create_extended_arpeggios()
        print(f"Created {extended} extended range arpeggios")
        
        print("\nDone!")
