"""
Chord Validation Utilities

This module provides functions for validating chord formations and diagnosing issues.
"""

def validate_chord_notes(chord_id):
    """
    Validate that a chord's note definitions are correct and well-formed.
    
    Args:
        chord_id: ID of the chord to validate
        
    Returns:
        dict: Validation report with issues and status
    """
    from .models_chords import ChordNotes, ChordPosition
    
    report = {
        'valid': True,
        'issues': [],
        'note_count': 0,
        'string_assignments': {},
        'positions': []
    }
    
    try:
        chord = ChordNotes.objects.get(id=chord_id)
        
        # Get all notes defined for this chord
        notes = []
        strings = []
        
        # Check first note
        if chord.first_note is not None:
            notes.append(chord.first_note)
            if chord.first_note_string:
                strings.append(chord.first_note_string)
                report['string_assignments'][chord.first_note_string] = chord.first_note
            else:
                report['issues'].append("First note has no string assignment")
                report['valid'] = False
        
        # Check second note
        if chord.second_note is not None:
            notes.append(chord.second_note)
            if chord.second_note_string:
                strings.append(chord.second_note_string)
                report['string_assignments'][chord.second_note_string] = chord.second_note
            else:
                report['issues'].append("Second note has no string assignment")
                report['valid'] = False
        
        # Check third note
        if chord.third_note is not None:
            notes.append(chord.third_note)
            if chord.third_note_string:
                strings.append(chord.third_note_string)
                report['string_assignments'][chord.third_note_string] = chord.third_note
            else:
                report['issues'].append("Third note has no string assignment")
                report['valid'] = False
        
        # Check fourth note if present
        if chord.fourth_note is not None:
            notes.append(chord.fourth_note)
            if chord.fourth_note_string:
                strings.append(chord.fourth_note_string)
                report['string_assignments'][chord.fourth_note_string] = chord.fourth_note
            else:
                report['issues'].append("Fourth note has no string assignment")
                report['valid'] = False
        
        # Check fifth note if present
        if chord.fifth_note is not None:
            notes.append(chord.fifth_note)
            if chord.fifth_note_string:
                strings.append(chord.fifth_note_string)
                report['string_assignments'][chord.fifth_note_string] = chord.fifth_note
            else:
                report['issues'].append("Fifth note has no string assignment")
                report['valid'] = False
        
        # Check sixth note if present
        if chord.sixth_note is not None:
            notes.append(chord.sixth_note)
            if chord.sixth_note_string:
                strings.append(chord.sixth_note_string)
                report['string_assignments'][chord.sixth_note_string] = chord.sixth_note
            else:
                report['issues'].append("Sixth note has no string assignment")
                report['valid'] = False
        
        # Check for duplicate string assignments
        if len(strings) != len(set(strings)):
            report['issues'].append("Duplicate string assignments found")
            report['valid'] = False
        
        report['note_count'] = len(notes)
        
        # Now check chord positions
        positions = ChordPosition.objects.filter(notes_name_id=chord_id)
        for position in positions:
            pos_info = {
                'id': position.id,
                'inversion': position.inversion_order,
                'note_offsets': []
            }
            
            # Add note offsets
            if position.first_note is not None:
                pos_info['note_offsets'].append(position.first_note)
            if position.second_note is not None:
                pos_info['note_offsets'].append(position.second_note)
            if position.third_note is not None:
                pos_info['note_offsets'].append(position.third_note)
            if position.fourth_note is not None:
                pos_info['note_offsets'].append(position.fourth_note)
            if position.fifth_note is not None:
                pos_info['note_offsets'].append(position.fifth_note)
            if position.sixth_note is not None:
                pos_info['note_offsets'].append(position.sixth_note)
            
            report['positions'].append(pos_info)
        
        # Validate chord type has expected number of notes
        if chord.chord_name in ['Major', 'Minor', 'Diminished', 'Augmented', 'Sus2', 'Sus4']:
            # Triads should have 3 notes
            if report['note_count'] != 3:
                report['issues'].append(f"Triad chord {chord.chord_name} has {report['note_count']} notes instead of 3")
                report['valid'] = False
        elif chord.chord_name in ['Major 7', 'Minor 7', 'Dominant 7', 'Minor 7b5', 'MinMaj 7', 
                                'Major 7(#5)', 'Major 7(b5)', 'Dominant 7(#5)', 'Dominant 7(b5)']:
            # 7th chords should have 4 notes
            if report['note_count'] != 4:
                report['issues'].append(f"7th chord {chord.chord_name} has {report['note_count']} notes instead of 4")
                report['valid'] = False
        
        return report
    
    except ChordNotes.DoesNotExist:
        report['valid'] = False
        report['issues'].append(f"Chord with ID {chord_id} does not exist")
        return report
    except Exception as e:
        report['valid'] = False
        report['issues'].append(f"Error validating chord: {str(e)}")
        return report


def fix_chord_validation_issues(chord_id):
    """
    Analyze and fix common validation issues for a chord.
    
    Args:
        chord_id: ID of the chord to fix
        
    Returns:
        dict: Report of actions taken
    """
    from .models_chords import ChordNotes, ChordPosition
    
    report = {
        'fixed': False,
        'actions': [],
        'remaining_issues': []
    }
    
    try:
        # First validate the chord
        validation = validate_chord_notes(chord_id)
        
        if validation['valid']:
            report['fixed'] = True
            report['actions'].append("Chord was already valid, no fixes needed")
            return report
        
        # Get the chord
        chord = ChordNotes.objects.get(id=chord_id)
        
        # Fix various issues
        
        # 1. Fix missing string assignments
        string_assignments_fixed = False
        
        if chord.first_note is not None and not chord.first_note_string:
            # V1 ranges - proper string assignments
            if chord.range == 'highA - g':
                chord.first_note_string = 'gString'
            elif chord.range == 'e - d':
                chord.first_note_string = 'dString'
            elif chord.range == 'b - A':
                chord.first_note_string = 'AString'
            elif chord.range == 'g - E':
                chord.first_note_string = 'ELowString'
            elif chord.range == 'd - lowB':
                chord.first_note_string = 'lowBString'
            # Support for existing highA - e range in V1 system
            elif chord.range == 'highA - e':
                if chord.type_name == 'V1':
                    chord.first_note_string = 'eString'
                else:
                    chord.first_note_string = 'eString'
            elif chord.range == 'e - lowB':
                chord.first_note_string = 'eString'
            else:
                chord.first_note_string = 'eString'  # Default
            string_assignments_fixed = True
            report['actions'].append(f"Set first note string to {chord.first_note_string}")
        
        if chord.second_note is not None and not chord.second_note_string:
            # V1 ranges - proper string assignments
            if chord.range == 'highA - g':
                chord.second_note_string = 'bString'
            elif chord.range == 'e - d':
                chord.second_note_string = 'gString'
            elif chord.range == 'b - A':
                chord.second_note_string = 'dString'
            elif chord.range == 'g - E':
                chord.second_note_string = 'AString'
            elif chord.range == 'd - lowB':
                chord.second_note_string = 'ELowString'
            # Legacy ranges
            elif chord.range == 'highA - e':
                chord.second_note_string = 'bString'
            elif chord.range == 'e - lowB':
                chord.second_note_string = 'AString'
            else:
                chord.second_note_string = 'bString'  # Default
            string_assignments_fixed = True
            report['actions'].append(f"Set second note string to {chord.second_note_string}")
        
        if chord.third_note is not None and not chord.third_note_string:
            # V1 ranges - proper string assignments
            if chord.range == 'highA - g':
                chord.third_note_string = 'highAString'
            elif chord.range == 'e - d':
                chord.third_note_string = 'bString'
            elif chord.range == 'b - A':
                chord.third_note_string = 'gString'
            elif chord.range == 'g - E':
                chord.third_note_string = 'dString'
            elif chord.range == 'd - lowB':
                chord.third_note_string = 'AString'
            # Legacy ranges
            elif chord.range == 'highA - e':
                chord.third_note_string = 'highAString'
            elif chord.range == 'e - lowB':
                chord.third_note_string = 'lowBString'
            else:
                chord.third_note_string = 'gString'  # Default
            string_assignments_fixed = True
            report['actions'].append(f"Set third note string to {chord.third_note_string}")
        
        if chord.fourth_note is not None and not chord.fourth_note_string:
            # V1 ranges - proper string assignments for 7th chords
            if chord.range == 'highA - g':
                chord.fourth_note_string = 'eString'
            elif chord.range == 'e - d':
                chord.fourth_note_string = 'eString'
            elif chord.range == 'b - A':
                chord.fourth_note_string = 'bString' 
            elif chord.range == 'g - E':
                chord.fourth_note_string = 'gString'
            elif chord.range == 'd - lowB':
                chord.fourth_note_string = 'dString'
            # Legacy ranges
            elif chord.range == 'highA - e':
                chord.fourth_note_string = 'gString'
            elif chord.range == 'e - lowB':
                chord.fourth_note_string = 'ELowString'
            else:
                chord.fourth_note_string = 'dString'  # Default
            string_assignments_fixed = True
            report['actions'].append(f"Set fourth note string to {chord.fourth_note_string}")
        
        # 2. Check for note count consistency based on chord type
        if chord.chord_name in ['Major', 'Minor', 'Diminished', 'Augmented', 'Sus2', 'Sus4']:
            # Should be a triad (3 notes)
            if chord.fourth_note is not None:
                chord.fourth_note = None
                chord.fourth_note_string = None
                report['actions'].append("Removed fourth note from triad chord")
            if chord.fifth_note is not None:
                chord.fifth_note = None
                chord.fifth_note_string = None
                report['actions'].append("Removed fifth note from triad chord")
            if chord.sixth_note is not None:
                chord.sixth_note = None
                chord.sixth_note_string = None
                report['actions'].append("Removed sixth note from triad chord")
        
        # Save the changes
        if string_assignments_fixed or len(report['actions']) > 0:
            chord.save()
            report['fixed'] = True
            report['actions'].append("Saved chord modifications")
        
        # 3. Fix positions
        positions = ChordPosition.objects.filter(notes_name_id=chord_id)
        positions.delete()
        report['actions'].append(f"Deleted {len(positions)} problematic positions")
        
        # Recreate positions properly
        from .eight_string_setup import create_base_position
        new_positions = create_base_position(chord_id)
        report['actions'].append(f"Created {len(new_positions)} new positions")
        
        # Validate again after fixes
        new_validation = validate_chord_notes(chord_id)
        if not new_validation['valid']:
            report['fixed'] = False
            report['remaining_issues'] = new_validation['issues']
        
        return report
    
    except ChordNotes.DoesNotExist:
        report['fixed'] = False
        report['remaining_issues'].append(f"Chord with ID {chord_id} does not exist")
        return report
    except Exception as e:
        report['fixed'] = False
        report['remaining_issues'].append(f"Error fixing chord: {str(e)}")
        return report
