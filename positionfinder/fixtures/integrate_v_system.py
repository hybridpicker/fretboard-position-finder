#!/usr/bin/env python3
"""
This script integrates the V-System chord voicings (V3-V14) 
into the main database dump file.
"""

import json
import os

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
V_SYSTEM_FILE = os.path.join(BASE_DIR, 'v_system_voicings.json')
DATABASE_DUMP = os.path.join(BASE_DIR, 'databasedump.json')
OUTPUT_FILE = os.path.join(BASE_DIR, 'databasedump_with_vsystem.json')

def main():
    # Load V-System chord voicings
    with open(V_SYSTEM_FILE, 'r') as f:
        v_system_data = json.load(f)
    
    # Load the database dump
    with open(DATABASE_DUMP, 'r') as f:
        db_data = json.load(f)
    
    # Find the highest primary key for chord notes
    max_pk = 0
    for item in db_data:
        if item['model'] == 'positionfinder.chordnotes':
            max_pk = max(max_pk, item['pk'])
    
    # Assign primary keys to V-System chord voicings
    for i, voicing in enumerate(v_system_data):
        voicing['pk'] = max_pk + i + 1
    
    # Combine the data
    combined_data = db_data + v_system_data
    
    # Write the combined data to a new file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(combined_data, f, indent=4)
    
    print(f"Integration complete. Added {len(v_system_data)} V-System chord voicings.")
    print(f"Output written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
