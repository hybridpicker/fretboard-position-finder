/**
 * Enhanced cursor controls for chord inversions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Make sure cursor elements are visible
    ensureCursorsVisible();
    
    
    // Enhance the cursor click functions
    enhanceCursorClickFunctions();
});

/**
 * Make sure cursor navigation elements are visible
 * Uses the centralized cursor management approach
 */
function ensureCursorsVisible() {
    // Defer to the base script's cursor management
    if (typeof cleanupDuplicateCursors === 'function') {
        cleanupDuplicateCursors();
    } else {
        console.warn("cleanupDuplicateCursors not available");
        
        // Fallback implementation if base function not loaded yet
        const leftCursor = document.querySelector('.left-cursor');
        const rightCursor = document.querySelector('.right-cursor');
        
        // Only make them visible if they exist
        if (leftCursor) {
            leftCursor.style.display = 'flex';
            leftCursor.style.visibility = 'visible';
            leftCursor.style.opacity = '1';
        }
        
        if (rightCursor) {
            rightCursor.style.display = 'flex';
            rightCursor.style.visibility = 'visible';
            rightCursor.style.opacity = '1';
        }
    }
}

/**
 * Enhance the cursor click functionality to ensure notes update properly
 * Note: direct_chord_navigation.js may override these functions, which is OK
 */
function enhanceCursorClickFunctions() {
    // Only set up functions if they don't already exist
    // This will be overridden by direct_chord_navigation.js if it's loaded
    if (typeof window.leftCursorClick !== 'function') {
        window.leftCursorClick = function() {
            
            // Make sure the notes display is updated
            ensureNotesUpdate();
            
            // Dispatch cursor navigation event
            document.dispatchEvent(new CustomEvent('cursor-navigation-complete', {
                detail: { direction: 'left' }
            }));
            
            // Restore multi-inversion display if available
            if (typeof window.forceCorrectInversionDisplay === 'function') {
                // Use the force fix method - most reliable
                setTimeout(window.forceCorrectInversionDisplay, 150);
            } else if (typeof window.updateChordInversions === 'function') {
                window.updateChordInversions();
            } else if (typeof enhanceChordDisplay === 'function') {
                setTimeout(enhanceChordDisplay, 150);
            }
        };
    }
    
    if (typeof window.rightCursorClick !== 'function') {
        window.rightCursorClick = function() {
            
            // Make sure the notes display is updated
            ensureNotesUpdate();
            
            // Dispatch cursor navigation event
            document.dispatchEvent(new CustomEvent('cursor-navigation-complete', {
                detail: { direction: 'right' }
            }));
            
            // Restore multi-inversion display if available
            if (typeof window.forceCorrectInversionDisplay === 'function') {
                // Use the force fix method - most reliable
                setTimeout(window.forceCorrectInversionDisplay, 150);
            } else if (typeof window.updateChordInversions === 'function') {
                window.updateChordInversions();
            } else if (typeof enhanceChordDisplay === 'function') {
                setTimeout(enhanceChordDisplay, 150);
            }
        };
    }
    
    // Register additional callbacks to always ensure notes update
    document.addEventListener('cursor-navigation-complete', function(e) {
        ensureNotesUpdate();
    });
}

/**
 * Ensure the notes display is updated after position change
 */
function ensureNotesUpdate() {
    // Get current position and range
    const urlParams = new URLSearchParams(window.location.search);
    const pos_val = urlParams.get('position_select') || 
                  (document.getElementById('position_select') ? document.getElementById('position_select').value : 'Basic Position');
    const note_range = urlParams.get('note_range') || 
                     (document.getElementById('note_range') ? document.getElementById('note_range').value : 'e - g');
    
    
    // Update the position select element if it exists
    const positionSelect = document.getElementById('position_select');
    if (positionSelect && positionSelect.value !== pos_val) {
        positionSelect.value = pos_val;
    }
    
    // Call the getTonesFromDataChords function to update the display
    if (typeof getTonesFromDataChords === 'function') {
        setTimeout(() => {
            getTonesFromDataChords(pos_val, note_range);
        }, 50);
    }
    
    // Update the selected position in the analysis container if present
    const positionValue = document.querySelector('.position-value');
    if (positionValue) {
        positionValue.textContent = pos_val;
    }
}

// Removed all logic related to getNoteNameFromData
// (was previously called to show note names on fretboard)
// ------------------------------------------------------------
// Root note keyboard shortcuts (up/down arrows) - Moved to root_note_keyboard_controls.js
// These are just placeholder functions for backwards compatibility
window.rootNoteUp = function() {
    // Implementation in root_note_keyboard_controls.js
};
window.rootNoteDown = function() {
    // Implementation in root_note_keyboard_controls.js
};
// Legacy aliases for compatibility with existing keymap handlers
window.increaseRoot = window.rootNoteUp;
window.decreaseRoot = window.rootNoteDown;

// Keyboard handlers: ensure left/right arrows click cursor buttons
document.addEventListener('keydown', function(event) {
    if (event.key === 'ArrowLeft') {
        event.preventDefault();
        const leftBtn = document.querySelector('.left-cursor');
        if (leftBtn) leftBtn.click();
    }
    if (event.key === 'ArrowRight') {
        event.preventDefault();
        const rightBtn = document.querySelector('.right-cursor');
        if (rightBtn) rightBtn.click();
    }
    // Up/Down arrows are handled in root_note_keyboard_controls.js
});
