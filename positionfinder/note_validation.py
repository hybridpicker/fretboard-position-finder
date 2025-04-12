"""
Note Validation Module

This module handles direct validation and correction of note displays on the fretboard.
It ensures that only the exact assigned notes are displayed, preventing
extra notes from appearing on the fretboard.
"""

def validate_and_filter_note_positions(position_data):
    """
    Filter out any unwanted or duplicate notes from the position data.
    
    Args:
        position_data: Dictionary containing position note data
        
    Returns:
        Dictionary with only the valid notes
    """
    # Return empty data if input is empty
    if not position_data:
        return {}
    
    # Special case: position_data has 'assigned_strings' directly
    assigned_strings = position_data.get('assigned_strings', [])
    
    # Enable debug info to track validation issues
    debug_info = False
    if debug_info:
        # Placeholder for potential debug logic
        pass
    
    # Create a new clean dictionary for the result
    valid_position_data = {}
    
    # Add the assigned_strings list first
    valid_position_data['assigned_strings'] = assigned_strings
    
    # Only include keys that are in the assigned_strings list, or are 'assigned_strings' itself
    for key, value in position_data.items():
        if key == 'assigned_strings':
            continue  # Already added above
        elif key in assigned_strings:
            # This is a string key that's in our assigned list - include it
            valid_position_data[key] = value[:] if isinstance(value, list) else value
        elif debug_info:
            # Placeholder for potential debug logic if debug_info is True
            pass
    
    # Ensure we have at least one root note
    has_root = False
    for key, value in valid_position_data.items():
        if key != 'assigned_strings' and isinstance(value, list) and len(value) >= 4 and value[3]:
            # Check if is_root flag (index 3) is true
            has_root = True
            if debug_info:
                # Placeholder for debug logic when root is found
                pass
            break # Exit loop once root is found
    
    # If no root found, set the first note as root
    if not has_root and len(valid_position_data) > 1:  # More than just assigned_strings
        for key, value in valid_position_data.items():
            if key != 'assigned_strings' and isinstance(value, list) and len(value) >= 4:
                value[3] = True  # Set is_root flag to True
                if debug_info:
                    # Placeholder for debug logic when setting the first note as root
                    pass
                break # Exit loop after setting the first note as root
    
    if debug_info:
        # Placeholder for final debug checks or logging before returning
        pass
    
    return valid_position_data

def apply_note_validation(positions_context):
    """
    Apply validation to all positions in the context.
    
    Args:
        positions_context: The context dictionary containing position data
        
    Returns:
        Updated context with validated position data
    """
    if 'positions' in positions_context:
        # Apply validation to each position
        for i, position in enumerate(positions_context['positions']):
            positions_context['positions'][i] = validate_and_filter_note_positions(position)
    
    return positions_context
