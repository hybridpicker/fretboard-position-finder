"""
Script to add 8-string specific ranges to existing chord types
"""
import os
import sys
import django

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fretboard.settings')
django.setup()

from positionfinder.models_chords import ChordNotes, ChordPosition
from django.db import transaction

def create_eight_string_ranges():
    """
    Create 8-string specific ranges for all existing chord types and names
    """
    print("Creating 8-string specific ranges for existing chords...")
    
    # Get unique combinations of type_name and chord_name
    chord_combinations = ChordNotes.objects.values_list('type_name', 'chord_name', 'category_id').distinct()
    print(f"Found {len(chord_combinations)} unique chord combinations")
    
    count = 0
    
    # List of 8-string specific ranges to add
    eight_string_ranges = [
        {'range': 'highA - g', 'description': 'High register with high A string'},
        {'range': 'highA - e', 'description': 'Upper register with high A string'},
        {'range': 'highA - b', 'description': 'Mid-high register with high A string'},
        {'range': 'd - lowB', 'description': 'Low register with low B string'},
        {'range': 'e - lowB', 'description': 'Extended range from e to low B'},
        {'range': 'highA - lowB', 'description': 'Full 8-string range'}
    ]
    
    # For each combination, create the 8-string ranges
    for type_name, chord_name, category_id in chord_combinations:
        # Find an existing chord for this combination
        try:
            existing_chord = ChordNotes.objects.filter(
                type_name=type_name,
                chord_name=chord_name,
                category_id=category_id
            ).first()
            
            if not existing_chord:
                print(f"No existing chord found for {type_name} - {chord_name}")
                continue
                
            # Get the max range_ordering for this chord
            max_ordering = ChordNotes.objects.filter(
                type_name=type_name,
                chord_name=chord_name
            ).order_by('-range_ordering').values_list('range_ordering', flat=True).first() or 0
            
            with transaction.atomic():
                for i, range_info in enumerate(eight_string_ranges):
                    range_name = range_info['range']
                    description = range_info['description']
                    
                    # Check if this range already exists for this chord
                    if ChordNotes.objects.filter(
                        type_name=type_name,
                        chord_name=chord_name,
                        range=range_name
                    ).exists():
                        print(f"Range {range_name} already exists for {type_name} - {chord_name}")
                        continue
                    
                    # Create new chord notes with 8-string range
                    eight_string_chord = ChordNotes.objects.create(
                        category_id=category_id,
                        type_name=type_name,
                        chord_name=chord_name,
                        range=range_name,
                        tonal_root=existing_chord.tonal_root,
                        range_ordering=max_ordering + i + 1,
                        ordering=existing_chord.ordering if hasattr(existing_chord, 'ordering') else None,
                        chord_ordering=existing_chord.chord_ordering if hasattr(existing_chord, 'chord_ordering') else None,
                        first_note=existing_chord.first_note,
                        second_note=existing_chord.second_note,
                        third_note=existing_chord.third_note,
                        fourth_note=existing_chord.fourth_note,
                    )
                    
                    # Assign appropriate strings based on the range
                    if 'highA - g' in range_name:
                        eight_string_chord.first_note_string = 'gString'
                        eight_string_chord.second_note_string = 'bString'
                        eight_string_chord.third_note_string = 'eString'
                        eight_string_chord.fourth_note_string = 'highAString'
                    elif 'highA - e' in range_name:
                        eight_string_chord.first_note_string = 'eString'
                        eight_string_chord.second_note_string = 'bString'
                        eight_string_chord.third_note_string = 'highAString'
                        eight_string_chord.fourth_note_string = 'gString'
                    elif 'highA - b' in range_name:
                        eight_string_chord.first_note_string = 'bString'
                        eight_string_chord.second_note_string = 'eString'
                        eight_string_chord.third_note_string = 'highAString'
                        eight_string_chord.fourth_note_string = 'gString'
                    elif 'd - lowB' in range_name:
                        eight_string_chord.first_note_string = 'lowBString'
                        eight_string_chord.second_note_string = 'ELowString'
                        eight_string_chord.third_note_string = 'AString'
                        eight_string_chord.fourth_note_string = 'dString'
                    elif 'e - lowB' in range_name:
                        eight_string_chord.first_note_string = 'lowBString'
                        eight_string_chord.second_note_string = 'AString'
                        eight_string_chord.third_note_string = 'dString'
                        eight_string_chord.fourth_note_string = 'eString'
                    elif 'highA - lowB' in range_name:
                        eight_string_chord.first_note_string = 'lowBString'
                        eight_string_chord.second_note_string = 'dString'
                        eight_string_chord.third_note_string = 'bString'
                        eight_string_chord.fourth_note_string = 'highAString'
                    
                    eight_string_chord.save()
                    
                    # Copy positions (inversions) from the existing chord
                    existing_positions = ChordPosition.objects.filter(notes_name_id=existing_chord.id)
                    for pos in existing_positions:
                        ChordPosition.objects.create(
                            notes_name_id=eight_string_chord.id,
                            inversion_order=pos.inversion_order,
                            first_note=pos.first_note,
                            second_note=pos.second_note,
                            third_note=pos.third_note,
                            fourth_note=pos.fourth_note,
                            fifth_note=pos.fifth_note,
                            sixth_note=pos.sixth_note,
                            seventh_note=pos.seventh_note,
                            eighth_note=pos.eighth_note,
                            ninth_note=pos.ninth_note,
                            tenth_note=pos.tenth_note,
                            eleventh_note=pos.eleventh_note,
                            twelfth_note=pos.twelfth_note
                        )
                    
                    count += 1
                    print(f"Created {range_name} for {type_name} - {chord_name}")
        
        except Exception as e:
            print(f"Error creating 8-string ranges for {type_name} - {chord_name}: {str(e)}")
    
    print(f"Created {count} new 8-string chord ranges")

if __name__ == "__main__":
    create_eight_string_ranges()
