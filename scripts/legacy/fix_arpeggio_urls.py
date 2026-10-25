#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fretboard.settings')
django.setup()

import re

def fix_process_arpeggio_results():
    """
    Fix the process_arpeggio_results function in views_search.py to correctly generate
    URLs for arpeggio search results.
    """
    # Path to the views_search.py file
    file_path = 'positionfinder/views_search.py'
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the url part in process_arpeggio_results function
    pattern = r"'url': f\"/en/\?models_select=2&root_note_chord=\{arpeggio\.chord_name\}&chord_options_select=\{arpeggio\.type_name\}\""
    
    # Look for the pattern
    match = re.search(pattern, content)
    
    if match:
        old_url_line = match.group(0)
        
        # Create the new URL generation line
        new_url_line = """'url': f"/?root={root_id}&models_select=2&notes_options_select={arpeggio.id}&position_select=0" """
        
        # Replace just this line
        new_content = content.replace(old_url_line, new_url_line)
        
        # Also add the root lookup code right before the URL line
        root_lookup_code = """        # Get root ID for URL generation
        from .models import Root
        root_id = None
        if root_note:
            # Try to find root by name
            root_obj = Root.objects.filter(name__iexact=root_note).first()
            if root_obj:
                root_id = root_obj.id
        else:
            # Try to find root from arpeggio.tonal_root
            root_obj = Root.objects.filter(pitch=arpeggio.tonal_root).first()
            if root_obj:
                root_id = root_obj.id
        
        # Fallback if no root found
        if not root_id:
            # Use a default or log warning
            root_id = 14  # Default to A if no root found
            logger.warning(f"Could not find root ID for arpeggio {arpeggio.id}, using default ID 14")
        
        """
        
        # Find a good spot to insert the code (right before the url line)
        insertion_point = new_content.find(new_url_line)
        if insertion_point > 0:
            # Find the start of the line by going back to the previous newline
            line_start = new_content.rfind('\n', 0, insertion_point) + 1
            # Insert the root lookup code at this position
            new_content = new_content[:line_start] + root_lookup_code + new_content[line_start:]
        
        # Write the updated content back to the file
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        return True
    else:
        return False

if __name__ == "__main__":
    result = fix_process_arpeggio_results()
    if result:
        print("✅ Successfully updated process_arpeggio_results function to generate correct URLs")
    else:
        print("❌ Could not find the URL generation code in the expected format")
