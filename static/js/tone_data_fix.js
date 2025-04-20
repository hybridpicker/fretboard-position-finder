/**
 * Tone Data Fixes
 * Patches for getToneNameFromDataChords and related functions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Replace the buggy getToneNameFromDataChords function
    if (typeof window.getToneNameFromDataChords === 'function') {
        // Save the original for reference
        window.originalGetToneNameFromDataChords = window.getToneNameFromDataChords;
        
        // Replace with our fixed version
        window.getToneNameFromDataChords = function() {
            try {
                // Safely check for and set up the tension button
                var button = document.getElementById('show_tension_button');
                if (button) {
                    button.setAttribute('onclick', 'show_tension_notes_chords()');
                    button.innerHTML = 'Show Tensions';
                }
                
                // Safely get position and range values
                var positionSelect = document.getElementById('position_select');
                var noteRange = document.getElementById('note_range');
                
                var pos_val = positionSelect ? positionSelect.value : '0';
                var note_range_val = noteRange ? noteRange.value : '';
                
                // Only call getTonesFromDataChords if note_range is available
                if (note_range_val && typeof window.getTonesFromDataChords === 'function') {
                    window.getTonesFromDataChords(pos_val, note_range_val);
                } 
                // If debugging is enabled, we might want to warn about missing functions
                else if (typeof window.DJANGO_DEBUG !== 'undefined' && window.DJANGO_DEBUG) {
                    console.warn('Could not call getTonesFromDataChords - missing note range or function');
                }
            } catch (error) {
                console.error('Error in getToneNameFromDataChords:', error);
            }
            
            return true; // Return true to indicate successful execution
        };
    }
});
