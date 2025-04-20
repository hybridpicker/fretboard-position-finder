/**
 * Recursive Function Fix
 * 
 * This script detects and breaks circular references between functions
 * that could cause infinite recursion.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Wait for all scripts to load
    setTimeout(detectAndFixRecursivePatterns, 2000);
});

/**
 * Detect and fix potentially recursive function patterns
 */
function detectAndFixRecursivePatterns() {
    console.log("Recursive Function Fix: Checking for circular references...");
    
    // Check for the key recursive pattern identified in the error
    if (typeof window.activateNotesForPosition === 'function' &&
        typeof window.getTonesFromDataChords === 'function') {
        
        console.log("Recursive Function Fix: Found potentially recursive functions:");
        console.log("- activateNotesForPosition");
        console.log("- getTonesFromDataChords");
        
        // Save original functions
        const originalActivateNotes = window.activateNotesForPosition;
        const originalGetTones = window.getTonesFromDataChords;
        
        // Create a direct implementation of getTonesFromDataChords that doesn't call activateNotesForPosition
        window.getTonesFromDataChords = function(position, range) {
            console.log(`Recursive Function Fix: Direct getTonesFromDataChords(${position}, ${range})`);
            
            // Prevent infinite loop by checking call stack depth with a custom property
            if (window.getTonesFromDataChords.callDepth > 0) {
                console.warn("Recursive Function Fix: Breaking potential infinite loop in getTonesFromDataChords");
                return;
            }
            
            try {
                window.getTonesFromDataChords.callDepth = 1;
                
                // Direct implementation only for breaking the circular reference
                const urlParams = new URLSearchParams(window.location.search);
                const currentRange = range || urlParams.get('note_range') || 'e - g';
                
                // Make sure we have voicing data
                if (typeof window.voicing_data === 'undefined' || !window.voicing_data) {
                    console.warn("Recursive Function Fix: No voicing_data available");
                    return;
                }
                
                // Skip to direct DOM manipulation to activate notes
                try {
                    // Reset active notes
                    document.querySelectorAll('.active').forEach(el => {
                        el.classList.remove('active');
                    });
                    
                    // Reset root notes
                    document.querySelectorAll('img.tone.root').forEach(el => {
                        el.classList.remove('root');
                        el.src = '/static/media/yellow_circle.svg';
                    });
                    
                    // Get position data
                    const positionData = getPositionData(position, currentRange);
                    if (!positionData) {
                        console.warn(`Recursive Function Fix: No data found for position ${position}`);
                        return;
                    }
                    
                    // Activate notes based on position data
                    activateNotesFromData(positionData);
                    
                    console.log(`Recursive Function Fix: Successfully activated notes for ${position}`);
                } catch (error) {
                    console.error(`Recursive Function Fix: Error in direct implementation: ${error.message}`);
                    
                    // Try calling original with a circuit breaker
                    if (typeof originalGetTones === 'function' && originalGetTones !== window.getTonesFromDataChords) {
                        console.log("Recursive Function Fix: Trying original getTonesFromDataChords as fallback");
                        originalGetTones(position, range);
                    }
                }
            } finally {
                window.getTonesFromDataChords.callDepth = 0;
            }
        };
        
        // Initialize call depth property
        window.getTonesFromDataChords.callDepth = 0;
        
        console.log("Recursive Function Fix: Applied fixes for circular references");
    } else {
        console.log("Recursive Function Fix: No potentially recursive pattern detected");
    }
}

/**
 * Helper function to get position data from the voicing_data object
 */
function getPositionData(position, range) {
    if (!window.voicing_data || !window.voicing_data[range]) {
        return null;
    }
    
    // Try direct position
    if (window.voicing_data[range][position]) {
        return window.voicing_data[range][position];
    }
    
    // Try normalized position names
    if (position === 'Root Position' && window.voicing_data[range]['Basic Position']) {
        return window.voicing_data[range]['Basic Position'];
    }
    
    if (position === 'Basic Position' && window.voicing_data[range]['Root Position']) {
        return window.voicing_data[range]['Root Position'];
    }
    
    // Look for anything that might match
    const positionKeys = Object.keys(window.voicing_data[range]);
    for (const key of positionKeys) {
        if (key.toLowerCase().includes(position.toLowerCase())) {
            return window.voicing_data[range][key];
        }
    }
    
    return null;
}

/**
 * Helper function to activate notes based on position data
 */
function activateNotesFromData(positionData) {
    // Get first object in array if needed
    if (Array.isArray(positionData)) {
        positionData = positionData[0];
    }
    
    // Process each string's note
    for (const stringName in positionData) {
        if (!positionData.hasOwnProperty(stringName) || stringName === 'assigned_strings') {
            continue;
        }
        
        // Extract note data
        const noteData = positionData[stringName];
        if (!noteData) continue;
        
        // Determine note name and if it's a root
        let noteName = '';
        let isRoot = false;
        
        if (Array.isArray(noteData)) {
            noteName = noteData[0].toLowerCase();
            isRoot = noteData[1] === 'Root' || noteData[1] === 'R' ||
                    noteData[2] === 'Root' || noteData[2] === 'R' ||
                    (noteData.length >= 4 && noteData[3] === true);
        } else if (typeof noteData === 'string') {
            noteName = noteData.toLowerCase();
        } else {
            continue;
        }
        
        // Get both with and without octave versions
        const noteBase = noteName.replace(/[0-9]/g, '');
        
        // Try to find the note elements
        const fullNoteSelector = `.${stringName} .note.${noteName}`;
        const baseNoteSelector = `.${stringName} .note.${noteBase}`;
        
        let noteElements = document.querySelectorAll(fullNoteSelector);
        
        // If no elements found with full name, try base name
        if (noteElements.length === 0) {
            noteElements = document.querySelectorAll(baseNoteSelector);
        }
        
        // Apply active class to found notes
        noteElements.forEach(noteEl => {
            noteEl.classList.add('active');
            
            // Find and activate tone
            const toneEl = noteEl.querySelector('img.tone');
            if (toneEl) {
                toneEl.classList.add('active');
                
                // Mark root if needed
                if (isRoot) {
                    toneEl.classList.add('root');
                    toneEl.src = '/static/media/red_circle.svg';
                }
            }
        });
    }
    
    // Ensure at least one root note is marked
    const rootElements = document.querySelectorAll('img.tone.root');
    if (rootElements.length === 0) {
        // Fallback: mark the first active note as root
        const firstToneEl = document.querySelector('.note.active img.tone');
        if (firstToneEl) {
            firstToneEl.classList.add('root');
            firstToneEl.src = '/static/media/red_circle.svg';
        }
    }
}
