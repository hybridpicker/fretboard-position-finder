#!/usr/bin/env python
"""
This script updates the chordData.json fixture to include all V2 chords.
It creates a backup of the existing fixture before updating it.
"""
import os
import django
import json
import subprocess
import shutil
from datetime import datetime
import sys

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fretboard.settings")
django.setup()

from positionfinder.models_chords import ChordNotes, ChordPosition
from django.core import serializers

def main():
    print("========================================")
    print("V2 CHORD FIXTURE UPDATER")
    print("========================================")
    
    # Path to the chord fixture
    fixture_file = 'fixtures/chordData.json'
    fixture_path = os.path.join(os.getcwd(), fixture_file)
    
    # Check if the fixture exists
    if not os.path.exists(fixture_path):
        print(f"Error: Fixture file not found at {fixture_path}")
        
        # Check if we have any alternative chord fixture files
        alt_fixture = 'fixtures/chord_data_clean.json'
        if os.path.exists(os.path.join(os.getcwd(), alt_fixture)):
            fixture_file = alt_fixture
            fixture_path = os.path.join(os.getcwd(), fixture_file)
            print(f"Using alternative fixture file: {fixture_file}")
        else:
            # No fixture file found, create a new one
            print("No existing chord fixture found. Will create a new one.")
    
    # Create backup directory if it doesn't exist
    backup_dir = os.path.join(os.getcwd(), 'fixtures/backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup if the fixture exists
    if os.path.exists(fixture_path):
        # Check the file for V2 chords
        try:
            with open(fixture_path, 'r') as f:
                data = json.load(f)
                
            # Count the V2 chords in the fixture
            v2_chords = sum(1 for item in data 
                            if item.get('model') == 'positionfinder.chordnotes' 
                            and item.get('fields', {}).get('type_name') == 'V2')
            
            # Count the V2 chord types in the fixture
            v2_chord_types = set()
            for item in data:
                if (item.get('model') == 'positionfinder.chordnotes' and 
                    item.get('fields', {}).get('type_name') == 'V2'):
                    v2_chord_types.add(item.get('fields', {}).get('chord_name', ''))
            
            print(f"Current fixture contains {v2_chords} V2 chords")
            print(f"V2 chord types: {sorted(v2_chord_types)}")
            
            # Check if we have all the required chord types
            required_types = ['Dominant 7', 'Major 7', 'Minor 7', 'Minor 7b5']
            missing_types = [t for t in required_types if t not in v2_chord_types]
            
            if v2_chords >= 400 and not missing_types:
                print("\nFixture already contains all required V2 chords!")
                user_choice = input("Update fixture anyway? (y/n): ").lower().strip()
                if user_choice != 'y':
                    print("Operation cancelled.")
                    return
            elif missing_types:
                print(f"\nMissing chord types: {missing_types}")
            else:
                print(f"\nExpected at least 400 V2 chords, but found only {v2_chords}")
                
        except Exception as e:
            print(f"Error checking fixture: {e}")
        
        # Create the backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f"{os.path.basename(fixture_file).split('.')[0]}_backup_{timestamp}.json")
        
        try:
            shutil.copy2(fixture_path, backup_file)
            print(f"Created backup at {backup_file}")
        except Exception as e:
            print(f"Error creating backup: {e}")
            user_choice = input("Continue without backup? (y/n): ").lower().strip()
            if user_choice != 'y':
                print("Operation cancelled.")
                return
    
    # Get the V2 chord count from the database
    db_v2_chords = ChordNotes.objects.filter(type_name='V2').count()
    db_v2_chord_types = set(ChordNotes.objects.filter(type_name='V2')
                           .values_list('chord_name', flat=True)
                           .distinct())
    
    print(f"\nDatabase contains {db_v2_chords} V2 chords")
    print(f"Database V2 chord types: {sorted(db_v2_chord_types)}")
    
    # Update the fixture
    print("\nUpdating chord fixture...")
    
    try:
        # Approach 1: Use Django's dumpdata command
        cmd = f"python manage.py dumpdata positionfinder.chordnotes positionfinder.chordposition --indent 2 > {fixture_file}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error using dumpdata command: {result.stderr}")
            print("Trying alternative serialization method...")
            
            # Approach 2: Use Django's serializers directly
            chord_notes = ChordNotes.objects.all()
            chord_positions = ChordPosition.objects.all()
            
            # Serialize both models
            serialized_chordnotes = serializers.serialize('json', chord_notes, indent=2)
            serialized_positions = serializers.serialize('json', chord_positions, indent=2)
            
            # Combine the serialized data
            chordnotes_data = json.loads(serialized_chordnotes)
            positions_data = json.loads(serialized_positions)
            combined_data = chordnotes_data + positions_data
            
            # Write to the fixture file
            with open(fixture_path, 'w') as f:
                json.dump(combined_data, f, indent=2)
        
        print("Fixture update completed.")
        
        # Verify the update
        try:
            with open(fixture_path, 'r') as f:
                updated_data = json.load(f)
                
            updated_v2_chords = sum(1 for item in updated_data 
                                  if item.get('model') == 'positionfinder.chordnotes' 
                                  and item.get('fields', {}).get('type_name') == 'V2')
            
            updated_types = set()
            for item in updated_data:
                if (item.get('model') == 'positionfinder.chordnotes' and 
                    item.get('fields', {}).get('type_name') == 'V2'):
                    updated_types.add(item.get('fields', {}).get('chord_name', ''))
            
            print(f"\nVerification results:")
            print(f"- Fixture now contains {updated_v2_chords} V2 chords")
            print(f"- V2 chord types: {sorted(updated_types)}")
            
            # Check if any required types are still missing
            still_missing = [t for t in ['Dominant 7', 'Major 7', 'Minor 7', 'Minor 7b5'] if t not in updated_types]
            
            if updated_v2_chords >= 400 and not still_missing:
                print("\nSuccess! Fixture now contains all required V2 chords.")
            else:
                if still_missing:
                    print(f"\nWarning: Still missing chord types: {still_missing}")
                if updated_v2_chords < 400:
                    print(f"\nWarning: Expected at least 400 V2 chords, but found only {updated_v2_chords}")
        
        except Exception as e:
            print(f"Error verifying fixture update: {e}")
    
    except Exception as e:
        print(f"Error updating fixture: {e}")
    
    print("\nTo load the updated fixture, run:")
    print(f"python manage.py loaddata {fixture_file}")
    print("\nOr use the enhanced load_fixtures.sh script:")
    print("./load_fixtures.sh")

if __name__ == "__main__":
    main()
