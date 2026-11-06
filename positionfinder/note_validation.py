"""
Note Validation Module

This module handles direct validation and correction of note displays on the fretboard.
It ensures that only the exact assigned notes are displayed, preventing
extra notes from appearing on the fretboard.
"""


def _is_note_entry(key: str, value: object) -> bool:
    """Whether the entry is a string-note list with at least four fields."""
    return key != "assigned_strings" and isinstance(value, list) and len(value) >= 4


def _ensure_root(valid_position_data: dict) -> None:
    """Make sure at least one note is flagged as root (falls back to the first note)."""
    for key, value in valid_position_data.items():
        if _is_note_entry(key, value) and value[3]:
            return  # is_root flag (index 3) is true

    # If no root found, set the first note as root
    if len(valid_position_data) > 1:  # More than just assigned_strings
        for key, value in valid_position_data.items():
            if _is_note_entry(key, value):
                value[3] = True  # Set is_root flag to True
                break


def validate_and_filter_note_positions(position_data: dict) -> dict:
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
    assigned_strings = position_data.get("assigned_strings", [])

    # Create a new clean dictionary for the result, assigned_strings first
    valid_position_data = {"assigned_strings": assigned_strings}

    # Only include keys that are in the assigned_strings list
    for key, value in position_data.items():
        if key != "assigned_strings" and key in assigned_strings:
            valid_position_data[key] = value[:] if isinstance(value, list) else value

    _ensure_root(valid_position_data)

    return valid_position_data


def apply_note_validation(positions_context: dict) -> dict:
    """
    Apply validation to all positions in the context.

    Args:
        positions_context: The context dictionary containing position data

    Returns:
        Updated context with validated position data
    """
    if "positions" in positions_context:
        # Apply validation to each position
        for i, position in enumerate(positions_context["positions"]):
            positions_context["positions"][i] = validate_and_filter_note_positions(position)

    return positions_context
