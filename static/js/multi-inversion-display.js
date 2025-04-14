/**
 * Chord display optimizer
 * Enhances chord displays with better visualization and user experience
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize chord display enhancements
    enhanceChordDisplay();
    
    // Add event listener for position changes
    window.addEventListener('popstate', function() {
        setTimeout(function() {
            enhanceChordDisplay();
        }, 200);
    });
});

/**
 * Enhance chord display with active inversion and transparent alternatives
 */
function enhanceChordDisplay() {
    // Only proceed if voicing_data is available
    if (typeof voicing_data === 'undefined' || !voicing_data || !voicing_data.note_range) {
        return;
    }

    // Get the current active range and position
    const currentRange = voicing_data.note_range || '';
    const urlParams = new URLSearchParams(window.location.search);
    const currentPosition = urlParams.get('position_select') || 'Root Position'; // Default to Root Position if not specified
    
    // Map 'Root Position' to 'Basic Position' for internal data access if needed
    const internalPosition = currentPosition === 'Root Position' ? 'Basic Position' : currentPosition;


    // --- Root Note Styling Cleanup --- 
    document.querySelectorAll('img.tone.root').forEach(img => {
        img.classList.remove('root', 'inversion-root'); // Remove root classes
        img.src = '/static/media/yellow_circle.svg'; // Reset to default image
        // Reset styles applied specifically for roots
        img.style.opacity = ''; 
        img.style.border = '';
        img.style.boxShadow = '';
        img.removeAttribute('data-root-for'); // Remove data attribute

        // Also reset the corresponding note name element's style if needed
        const noteDiv = img.closest('.note');
        if (noteDiv) {
            const noteNameDiv = noteDiv.querySelector('.notename');
            if (noteNameDiv) {
                noteNameDiv.style.fontWeight = ''; // Reset font weight
            }
        }
    });
    // --- End Root Note Styling Cleanup ---
    
    // First, reset all inversion-note styling
    document.querySelectorAll('.inversion-note, .inversion-tone').forEach(el => {
        el.classList.remove('inversion-note', 'inversion-tone');
        el.style.opacity = ''; // Reset opacity
        el.style.filter = ''; // Reset filter
        el.style.border = ''; // Reset border
        el.removeAttribute('data-inversion'); // Remove data attribute
    });
    
    // Get available positions for this range from voicing_data
    const availablePositions = [];
    if (voicing_data[currentRange]) {
        // Use a defined order if possible, otherwise just keys
        const order = ['Basic Position', 'First Inversion', 'Second Inversion', 'Third Inversion'];
        const availableKeys = Object.keys(voicing_data[currentRange]);
        order.forEach(pos => {
            if (availableKeys.includes(pos)) {
                availablePositions.push(pos);
            }
        });
        // Add any remaining keys not in the standard order (just in case)
        availableKeys.forEach(key => {
            if (!availablePositions.includes(key)) {
                availablePositions.push(key);
            }
        });
    } else {
        console.warn(`[MultiDisplayDebug] No data found for range: ${currentRange}`);
        return;
    }
    
    
    // --- Apply Styling Based on Data --- 
    availablePositions.forEach(positionKey => {
        try { // Add try block for the outer loop (each position)
            const positionDataArray = voicing_data[currentRange][positionKey];
            if (!positionDataArray || !Array.isArray(positionDataArray) || positionDataArray.length === 0) {
                console.warn(`[MultiDisplayDebug] No valid data array found for position ${positionKey}, skipping.`);
                return; // Use continue instead of return in forEach if possible, but return works here
            }
            
            const positionNotesData = positionDataArray[0]; 
            if (!positionNotesData) {
                console.warn(`[MultiDisplayDebug] No notes data object found for position ${positionKey}, skipping.`);
                return;
            }

            const positionStrings = Object.keys(positionNotesData);
            
            positionStrings.forEach(stringKey => {
                // *** ADDED CHECK: Skip processing if the key is 'assigned_strings' ***
                if (stringKey === 'assigned_strings') {
                    return; // Skip to the next stringKey in the forEach
                }
                // *** END ADDED CHECK ***
                try { // Add try block for the inner loop (each string/note)
                     const noteInfo = positionNotesData[stringKey];
                     if (!noteInfo) {
                        return; // Skip this string
                    }


                    let noteName = '';
                    let isRoot = false;

                    if (Array.isArray(noteInfo)) {
                        noteName = (noteInfo[0] || '').toLowerCase();
                        isRoot = noteInfo[3] === true; // Read the boolean is_root flag from Python
                    } else if (typeof noteInfo === 'string') {
                        noteName = noteInfo.toLowerCase();
                        isRoot = false; // Assume not root if only string is provided
                    } else {
                        console.warn(`[MultiDisplayDebug]    Unexpected noteInfo format for ${stringKey} in ${positionKey}:`, noteInfo);
                        return; // Skip if format is unexpected
                    }
                    
                    if (!noteName) {
                        return; // Skip if no note name derived
                    }

                    // Find corresponding elements on the fretboard
                    const noteElements = document.querySelectorAll(`.${stringKey} .note.${noteName}`);
                    const toneElements = document.querySelectorAll(`.${stringKey} img.tone.${noteName}`);
                    
                    if (noteElements.length === 0 || toneElements.length === 0) {
                         return; // Skip if elements not found
                    }

                    // --- Styling Logic --- 
                    if (positionKey === internalPosition) {
                        // Style for the CURRENTLY SELECTED inversion
                        noteElements.forEach(el => {
                            el.classList.add('active');
                            el.classList.remove('inversion-note');
                            el.style.opacity = '';
                            el.style.filter = '';
                            el.style.border = '';
                            const noteNameDiv = el.querySelector('.notename');
                            if (noteNameDiv) noteNameDiv.style.fontWeight = 'bold';
                        });
                        toneElements.forEach(el => {
                            el.classList.add('active');
                            el.classList.remove('inversion-tone');
                            el.style.visibility = 'visible';
                            el.style.opacity = '';
                            el.style.filter = '';
                            el.style.border = '';
                            el.style.boxShadow = ''; 
                            el.removeAttribute('data-inversion');

                            if (isRoot) {
                                el.classList.add('root');
                                el.src = '/static/media/red_circle.svg';
                                el.style.opacity = '1';
                                el.style.border = '2px dashed #AA5500';
                                el.style.boxShadow = '0 0 3px rgba(200, 100, 0, 0.3)';
                                el.setAttribute('data-root-for', positionKey);
                            } else {
                            }
                        });
                    } else {
                        // Style for ALTERNATIVE (not selected) inversions
                        noteElements.forEach(el => {
                            el.classList.add('active', 'inversion-note');
                            el.setAttribute('data-inversion', positionKey);
                            const noteNameDiv = el.querySelector('.notename');
                            if (noteNameDiv) noteNameDiv.style.fontWeight = '';
                        });
                        toneElements.forEach(el => {
                            el.classList.add('active', 'inversion-tone');
                            el.style.visibility = 'visible';
                            el.setAttribute('data-inversion', positionKey);

                            if (isRoot) {
                                el.classList.add('inversion-root');
                                el.setAttribute('data-root-for', positionKey);
                            }
                        });
                    }
                } catch (innerError) {
                    console.error(`[MultiDisplayDebug] Error processing string ${stringKey} in position ${positionKey}:`, innerError);
                }
            }); // End inner string loop
        } catch (outerError) {
             console.error(`[MultiDisplayDebug] Error processing position ${positionKey}:`, outerError);
        }
    }); // End outer position loop
    // --- End Apply Styling Based on Data --- 
    
    // Ensure the CSS style for inversion classes is present
    addInversionDisplayStyle();
    
    // Debug the final counts
}

/**
 * Adds the CSS style block for inversion display if not already present.
 */
function addInversionDisplayStyle() {
    if (!document.getElementById('inversion-style')) {
        const style = document.createElement('style');
        style.id = 'inversion-style';
        style.textContent = `
            /* Style for notes belonging to alternative (non-selected) inversions */
            .inversion-note,
            .inversion-tone {
                opacity: 0.4 !important; /* Make them faded */
                filter: brightness(0.8); /* Slightly dimmer */
                transition: all 0.2s ease;
                border: 1px dashed rgba(100, 100, 255, 0.4); /* Subtle border */
            }
            
            /* Make alternative inversions more visible on hover */
            .inversion-note:hover,
            .inversion-tone:hover {
                opacity: 0.7 !important;
                filter: brightness(1);
                cursor: pointer;
                border: 1px solid rgba(100, 100, 255, 0.8);
            }

            /* Optional: Style for roots of alternative inversions if needed */
            .inversion-root {
                 /* Add specific style if you want to distinguish roots of alt inversions */
                 /* e.g., box-shadow: 0 0 2px rgba(100, 100, 255, 0.5); */
            }

            /* Ensure primary root note style overrides */
            img.tone.root {
                opacity: 1 !important; 
                filter: none !important;
                border: 2px dashed #AA5500 !important; 
                box-shadow: 0 0 3px rgba(200, 100, 0, 0.3) !important;
            } 
        `;
        document.head.appendChild(style);
    }
}

// Helper function to update chord inversions after navigation
// Can be called from cursor controls or UI events
function updateChordInversions() {
    enhanceChordDisplay();
}
