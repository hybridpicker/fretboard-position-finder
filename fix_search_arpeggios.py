#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fretboard.settings')
django.setup()

from positionfinder.models import Root
from positionfinder.models_chords import ChordNotes
from django.db.models import Q
import re

def create_root_mapping():
    """Create a mapping between note names, IDs, and pitch values"""
    mapping = {}
    roots = Root.objects.all()
    
    for root in roots:
        # Map both ID and name to pitch
        mapping[root.id] = root.pitch  # ID to pitch
        mapping[root.name] = root.pitch  # Name to pitch
        
        # Add name to ID mapping (using name.lower() to handle case insensitivity)
        mapping[root.name.lower()] = root.id
    
    return mapping

def fix_search_arpeggios():
    """
    Fix the search_arpeggios function in views_search.py to correctly handle
    root note mapping between ID and pitch value.
    """
    # Path to the views_search.py file
    file_path = 'positionfinder/views_search.py'
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the search_arpeggios function and the root filtering part
    root_filter_pattern = r'(if note:.*?root_id = ROOT_NAME_TO_ID\.get\(note\).*?if root_id is not None:.*?logger\.debug.*?qs = qs\.filter\(tonal_root=root_id\))'
    
    # Use re.DOTALL to match across newlines
    match = re.search(root_filter_pattern, content, re.DOTALL)
    
    if match:
        old_code = match.group(1)
        
        # Create the new code with pitch-based search
        new_code = """if note:
            from .models import Root
            # First try to find the note by name
            root_obj = Root.objects.filter(name__iexact=note).first()
            
            if root_obj:
                # Use the pitch value for filtering (not the ID)
                root_pitch = root_obj.pitch
                logger.debug(f"Filtering arpeggios by root_pitch: {root_pitch} (for note: {note}, ID: {root_obj.id})")
                qs = qs.filter(tonal_root=root_pitch)
            else:
                # Fall back to the old method if note isn't found
                root_id = ROOT_NAME_TO_ID.get(note)
                if root_id is not None:
                    # Get the corresponding pitch for this ID
                    root_obj = Root.objects.filter(id=root_id).first()
                    if root_obj:
                        root_pitch = root_obj.pitch
                        logger.debug(f"Filtering arpeggios by root_pitch: {root_pitch} (from ID: {root_id} for note: {note})")
                        qs = qs.filter(tonal_root=root_pitch)
                    else:
                        logger.debug(f"Filtering arpeggios by root_id: {root_id} (for note: {note})")
                        qs = qs.filter(tonal_root=root_id)
                else:
                    logger.warning(f"Could not find root_id or pitch for note: {note}. Skipping root filter.")"""
        
        # Replace the old code with the new code
        new_content = content.replace(old_code, new_code)
        
        # Write the updated content back to the file
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        return True
    else:
        return False

if __name__ == "__main__":
    result = fix_search_arpeggios()
    if result:
        print("✅ Successfully updated search_arpeggios function to handle pitch-based root filtering")
    else:
        print("❌ Could not find the search_arpeggios function in the expected format")
