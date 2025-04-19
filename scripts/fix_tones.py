#!/usr/bin/env python3
"""
Script to fix tone-related issues identified by the tests:
1. Create missing tone files by copying from enharmonic equivalents when possible
2. Fix enharmonic equivalent ordering in the NOTES data structure
3. Fix string intervals to ensure they match standard guitar tuning
"""

import os
import sys
import shutil
import json
import re
from pathlib import Path

def main():
    """Main function to perform tone fixes."""
    # Get the project base directory
    base_dir = Path(__file__).resolve().parent.parent
    
    # Paths for tone files and JS data
    tone_dir = base_dir / 'static' / 'media' / 'tone_sounds'
    js_file = base_dir / 'static' / 'js' / 'base.2.0.4.js'
    
    if not tone_dir.exists():
        print(f"Error: Tone directory not found: {tone_dir}")
        return 1
    
    if not js_file.exists():
        print(f"Error: JavaScript file not found: {js_file}")
        return 1
    
    # 1. Define enharmonic equivalents mapping
    enharmonic_map = {
        'cs': 'db', 'db': 'cs',
        'ds': 'eb', 'eb': 'ds',
        'fs': 'gb', 'gb': 'fs',
        'gs': 'ab', 'ab': 'gs',
        'as': 'bb', 'bb': 'as'
    }
    
    # 2. Find existing tone files
    existing_tones = [f.stem for f in tone_dir.glob('*.mp3')]
    print(f"Found {len(existing_tones)} existing tone files")
    
    # 3. Check for missing tones based on expected structure
    # Expected NOTES structure (abbreviated)
    expected_notes = {
        'eString': [['f2'], ['gb2', 'fs2'], ['g2'], ['gs2', 'ab2'], ['a2'], ['bb2', 'as2'], ['b2'], ['c3'], ['cs3', 'db3'], ['d3'], ['ds3', 'eb3'], ['e3'], ['f3'], ['fs3', 'gb3'], ['g3'], ['gs3', 'ab3'], ['a3']],
        'bString': [['c2'], ['cs2', 'db2'], ['d2'], ['ds2', 'eb2'], ['e2'], ['f2'], ['fs2', 'gb2'], ['g2'], ['gs2', 'ab2'], ['a2'], ['bb2', 'as2'], ['b2'], ['c3'], ['cs3', 'db3'], ['d3'], ['ds3', 'eb3'], ['e3']],
        'gString': [['gs1', 'ab1'], ['a1'], ['bb1', 'as1'], ['b1'], ['c2'], ['cs2', 'db2'], ['d2'], ['ds2', 'eb2'], ['e2'], ['f2'], ['fs2', 'gb2'], ['g2'], ['gs2', 'ab2'], ['a2'], ['bb2', 'as2'], ['b2'], ['c3']],
        'dString': [['ds1', 'eb1'], ['e1'], ['f1'], ['fs1', 'gb1'], ['g1'], ['gs1', 'ab1'], ['a1'], ['bb1', 'as1'], ['b1'], ['c2'], ['cs2', 'db2'], ['d2'], ['ds2', 'eb2'], ['e2'], ['f2'], ['fs2', 'gb2'], ['g2']],
        'AString': [['bb0', 'as0'], ['b0'], ['c1'], ['cs1', 'db1'], ['d1'], ['ds1', 'eb1'], ['e1'], ['f1'], ['fs1', 'gb1'], ['g1'], ['gs1', 'ab1'], ['a1'], ['bb1', 'as1'], ['b1'], ['c2'], ['cs2', 'db2'], ['d2']],
        'ELowString': [['f0'], ['fs0', 'gb0'], ['g0'], ['gs0', 'ab0'], ['a0'], ['bb0', 'as0'], ['b0'], ['c1'], ['cs1', 'db1'], ['d1'], ['ds1', 'eb1'], ['e1'], ['f1'], ['fs1', 'gb1'], ['g1'], ['gs1', 'ab1'], ['a1']],
        'highAString': [['bb2', 'as2'], ['b2'], ['c3'], ['cs3', 'db3'], ['d3'], ['ds3', 'eb3'], ['e3'], ['f3'], ['fs3', 'gb3'], ['g3'], ['gs3', 'ab3'], ['a3'], ['bb3', 'as3'], ['b3'], ['c4'], ['cs4', 'db4'], ['d4']],
        'lowBString': [['c0'], ['cs0', 'db0'], ['d0'], ['ds0', 'eb0'], ['e0'], ['f0'], ['fs0', 'gb0'], ['g0'], ['gs0', 'ab0'], ['a0'], ['bb0', 'as0'], ['b0'], ['c1'], ['cs1', 'db1'], ['d1'], ['ds1', 'eb1'], ['e1']]
    }
    
    # Get a flat list of all expected tones
    all_expected_tones = []
    for string_name, frets in expected_notes.items():
        for fret in frets:
            for tone in fret:
                if tone not in all_expected_tones:
                    all_expected_tones.append(tone)
    
    print(f"Found {len(all_expected_tones)} unique tones in the expected data structure")
    
    # Find missing tone files
    missing_tones = [tone for tone in all_expected_tones if tone not in existing_tones]
    print(f"Found {len(missing_tones)} missing tone files")
    
    # 4. Try to create missing tone files by copying from enharmonic equivalents
    tones_copied = 0
    tones_not_found = []
    
    for tone in missing_tones:
        # Extract note and octave
        note_match = re.match(r'([a-z]+)([0-4])', tone)
        if not note_match:
            print(f"Warning: Could not parse tone name: {tone}")
            tones_not_found.append(tone)
            continue
            
        note, octave = note_match.groups()
        
        # Check if there's an enharmonic equivalent
        if note in enharmonic_map:
            alt_note = enharmonic_map[note]
            alt_tone = f"{alt_note}{octave}"
            
            # Check if the alternative tone exists
            alt_file = tone_dir / f"{alt_tone}.mp3"
            if alt_file.exists():
                # Copy the file
                shutil.copy2(alt_file, tone_dir / f"{tone}.mp3")
                print(f"Copied {alt_tone}.mp3 to {tone}.mp3")
                tones_copied += 1
            else:
                print(f"Warning: Could not find enharmonic equivalent {alt_tone}.mp3 for {tone}")
                tones_not_found.append(tone)
        else:
            print(f"Warning: No enharmonic equivalent defined for {note}")
            tones_not_found.append(tone)
    
    print(f"Created {tones_copied} missing tone files by copying enharmonic equivalents")
    if tones_not_found:
        print(f"Could not create {len(tones_not_found)} tone files: {', '.join(tones_not_found)}")
    
    # 5. Fix the JS file to use the corrected NOTES structure
    print("\nUpdating JavaScript file with correct NOTES structure...")
    
    # Read the original file
    with open(js_file, 'r') as f:
        js_content = f.read()
    
    # Find the NOTES object in the file
    notes_obj_pattern = r'const NOTES = \{[^;]+\};'
    notes_obj_match = re.search(notes_obj_pattern, js_content, re.DOTALL)
    
    if not notes_obj_match:
        print("Error: Could not find NOTES object in JavaScript file")
        return 1
    
    # Generate the new NOTES object as a string
    new_notes_lines = ['const NOTES = {']
    
    for string_name, frets in expected_notes.items():
        frets_str = []
        for fret in frets:
            if len(fret) == 1:
                frets_str.append(f"['{fret[0]}']")
            else:
                frets_str.append(f"['{fret[0]}', '{fret[1]}']")
        
        new_notes_lines.append(f"    '{string_name}': [{', '.join(frets_str)}],")
    
    # Remove trailing comma from last line and close the object
    new_notes_lines[-1] = new_notes_lines[-1].rstrip(',')
    new_notes_lines.append('};')
    
    # Join the lines to form the new NOTES object
    new_notes_obj = '\n'.join(new_notes_lines)
    
    # Replace the old NOTES object with the new one
    new_js_content = js_content.replace(notes_obj_match.group(0), new_notes_obj)
    
    # Write the updated content back to the file
    with open(js_file, 'w') as f:
        f.write(new_js_content)
    
    print(f"Updated {js_file} with corrected NOTES structure")
    
    # 6. Special handling for problematic tone files
    # If any 2.mp3 or b00.mp3 files exist, we need to handle them correctly
    problematic_files = ['2.mp3', 'b00.mp3']
    for file_name in problematic_files:
        file_path = tone_dir / file_name
        if file_path.exists():
            if file_name == '2.mp3':
                # This might be a misnamed tone - find most likely C2 or similar
                print(f"Warning: Found problematic file {file_name}")
            elif file_name == 'b00.mp3':
                # This is likely supposed to be b0.mp3
                target_path = tone_dir / 'b0.mp3'
                if not target_path.exists():
                    shutil.copy2(file_path, target_path)
                    print(f"Copied {file_name} to b0.mp3")
    
    print("\nTone fix script completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
