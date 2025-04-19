/**
 * Cursor functions for chord inversions AND scale positions.
 * Handles left and right cursor navigation based on the current mode ('scales' or 'chords').
 */

// --- Assumed Global State Variables & DOM Elements ---
// These variables are expected to be defined and managed elsewhere in the application scope.
/*
let currentMode = 'scales'; // Can be 'scales' or 'chords'
let currentScalePosition = 0; // For scales: 0="All", 1="Pos 1", ...
let maxScalePosition = 5;     // Example maximum position for scales
let currentChordType = 'triad'; // Can be 'triad' or 'fourNote'
let currentInversion = 0;     // For chords: 0="Basic", 1="1st Inv", ...
let leftCursorElement;       // Holds the DOM element for the left cursor (e.g., document.querySelector('.left-cursor'))
let rightCursorElement;      // Holds the DOM element for the right cursor (e.g., document.querySelector('.right-cursor'))
let displayElement;          // Holds the DOM element for displaying the state (e.g., document.getElementById('currentStateDisplay'))
*/
// --- End Assumed Globals ---


/**
 * Helper function to get a query parameter from the URL
 * (Existing function - kept for potential other uses in the file)
 */
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

/**
 * Helper function to get chord type from the URL or select element
 * (Existing function - kept for potential other uses in the file)
 */
function getChordType() {
    // Check URL first
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('chords_options_select')) {
        return urlParams.get('chords_options_select');
    }

    // Check chord options select element
    const chordSelect = document.getElementById('chords_options_select');
    if (chordSelect && chordSelect.selectedIndex >= 0) {
        return chordSelect.options[chordSelect.selectedIndex].value;
    }

    // Default to major
    return 'Major';
}

/**
 * Helper function to get available positions based on chord type
 * (Existing function - kept for potential other uses in the file)
 */
function getChordPositions(chordType) {
    // Use the shared function from direct_chord_navigation.js if available
    if (typeof getAvailablePositions === 'function') {
        return getAvailablePositions();
    }

    // Default positions
    let positions = ['Root Position', 'First Inversion', 'Second Inversion'];

    // Add third inversion for seventh chords
    if (chordType && (chordType.includes('7') || chordType.includes('9') || chordType.includes('11') || chordType.includes('13'))) {
        positions.push('Third Inversion');
    }

    // Check if we have voicing_data available
    if (typeof voicing_data !== 'undefined' && voicing_data !== null) {
        // Get current range from URL or select element
        const currentRange = getQueryParam('note_range') ||
            (document.getElementById('note_range') ? document.getElementById('note_range').value : 'e - g');


        if (voicing_data[currentRange] && typeof voicing_data[currentRange] === 'object') {
            // Get all position keys and filter out invalid ones
            const dataPositions = Object.keys(voicing_data[currentRange])
                .filter(pos => pos && !/^\d+$/.test(pos) && typeof voicing_data[currentRange][pos] === 'object');


            if (dataPositions.length > 0) {
                // Normalize position names for consistency
                return dataPositions.map(pos => {
                    // Map "Basic Position" to "Root Position" for consistency
                    if (pos === 'Basic Position') return 'Root Position';

                    // Handle any variations with "First Root" in them
                    if (pos.includes('First Root') || pos.includes('First Basic')) return 'Root Position';

                    return pos;
                });
            }
        } else {

            // If the requested range doesn't exist, try to find any range data
            const availableRanges = Object.keys(voicing_data)
                .filter(k => typeof voicing_data[k] === 'object' &&
                       !['chord', 'type', 'root', 'note_range'].includes(k));


            // If we found any ranges, try to get positions from the first available one
            if (availableRanges.length > 0) {
                const firstRange = availableRanges[0];

                const fallbackPositions = Object.keys(voicing_data[firstRange])
                    .filter(pos => pos && !/^\d+$/.test(pos) &&
                           typeof voicing_data[firstRange][pos] === 'object');

                if (fallbackPositions.length > 0) {
                    // Normalize position names for consistency
                    return fallbackPositions.map(pos => {
                        if (pos === 'Basic Position') return 'Root Position';
                        if (pos.includes('First Root') || pos.includes('First Basic')) return 'Root Position';
                        return pos;
                    });
                }
            }
        }
    }

    // If we have a position select element, get positions from there
    const positionSelect = document.getElementById('position_select');
    if (positionSelect && positionSelect.options.length > 0) {
        // Get unique positions from the select element, filtering out numeric-only values
        const uniquePositions = new Set();
        for (let i = 0; i < positionSelect.options.length; i++) {
            const value = positionSelect.options[i].value;
            // Skip empty values or values that are only numbers
            if (value && !/^\d+$/.test(value)) {
                uniquePositions.add(value);
            }
        }
        const selectPositions = Array.from(uniquePositions);
        if (selectPositions.length > 0) {
            return selectPositions;
        }
    }

    return positions;
}

/**
 * Helper function to update position in UI and URL
 * (Existing function - kept for potential other uses in the file)
 */
function updatePosition(position) {
    // Use the shared function from direct_chord_navigation.js if available
    if (typeof updatePositionInUI === 'function' && typeof updatePositionInURL === 'function') {
        updatePositionInUI(position);
        updatePositionInURL(position);
        return;
    }

    // Update position select if it exists
    const positionSelect = document.getElementById('position_select');
    if (positionSelect) {
        for (let i = 0; i < positionSelect.options.length; i++) {
            if (positionSelect.options[i].value === position) {
                positionSelect.selectedIndex = i;
                break;
            }
        }
    }

    // Update URL without page reload
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('position_select', position);
    const newUrl = window.location.pathname + '?' + urlParams.toString();
    window.history.replaceState(null, '', newUrl);
}

/**
 * Function to get tones from data for chords
 * (Existing function - kept for potential other uses in the file)
 */
function getTonesFromDataChords(position, range) {
    // Use the original function if available
    if (window.getTonesFromDataChords && typeof window.getTonesFromDataChords === 'function' && window.getTonesFromDataChords !== this.getTonesFromDataChords) {
        return window.getTonesFromDataChords(position, range);
    }

    // If direct chord navigation is available, use that
    if (typeof activateNotesForPosition === 'function') {
        activateNotesForPosition(position);
        return;
    }


    // Simple implementation if nothing else is available
    try {
        // Normalize position names for lookup
        const normalizePosition = (pos) => {
            // Handle various aliases for Root Position
            if (pos === 'Root Position' || pos === 'Basic Position' ||
                pos.includes('First Root') || pos.includes('First Basic')) {
                return 'Basic Position';
            }
            return pos;
        };

        // First try the exact position name
        let positionData = null;

        if (typeof voicing_data !== 'undefined' && voicing_data[range]) {
            // Try direct position name first
            if (voicing_data[range][position]) {
                positionData = voicing_data[range][position];
            }
            // Then try normalized position name
            else {
                const lookupPosition = normalizePosition(position);
                if (voicing_data[range][lookupPosition]) {
                    positionData = voicing_data[range][lookupPosition];
                }
                // Try the reverse mapping (Basic Position -> Root Position)
                else if (position === 'Basic Position' && voicing_data[range]['Root Position']) {
                    positionData = voicing_data[range]['Root Position'];
                }
                // Try First Inversion as a fallback
                else if (voicing_data[range]['First Inversion']) {
                    positionData = voicing_data[range]['First Inversion'];
                }
                // Try any available position as a last resort
                else {
                    const availablePositions = Object.keys(voicing_data[range])
                        .filter(key => typeof voicing_data[range][key] === 'object');

                    if (availablePositions.length > 0) {
                        const fallbackPosition = availablePositions[0];
                        positionData = voicing_data[range][fallbackPosition];
                    } else {
                        console.error(`No voicing data for ${range} / ${position} and no fallbacks available`);
                        return;
                    }
                }
            }
        } else {
            console.error(`No voicing data for range: ${range}`);
            return;
        }

        if (!positionData) {
            console.error(`Could not find position data for ${range} / ${position}`);
            return;
        }

        // Handle array format
        if (Array.isArray(positionData)) {
            positionData = positionData[0];
        }

        // Reset all active elements
        document.querySelectorAll('.active').forEach(el => {
            el.classList.remove('active');
        });

        // Activate notes for each string
        for (const stringName in positionData) {
            if (!positionData.hasOwnProperty(stringName)) continue;

            // Get note data
            const noteData = positionData[stringName];
            if (!noteData) continue;

            // Handle different formats
            let noteName = '';
            let isRoot = false;

            if (Array.isArray(noteData)) {
                noteName = noteData[0].toLowerCase();
                isRoot = noteData[1] === 'Root' || noteData[1] === 'R' ||
                        noteData[2] === 'Root' || noteData[2] === 'R';
            } else if (typeof noteData === 'string') {
                noteName = noteData.toLowerCase();
            } else {
                continue;
            }

            // Define valid note names explicitly
            const validNoteNames = ['a', 'ab', 'as', 'b', 'bb', 'c', 'cs', 'db', 'd', 'ds', 'eb', 'e', 'f', 'fs', 'gb', 'g', 'gs'];

            // Get base note without octave
            const baseNote = noteName.replace(/[0-9]/g, '').toLowerCase();

            // Validate the note name
            if (!validNoteNames.includes(baseNote)) {
                console.warn(`Invalid note name: ${baseNote} from ${noteName}`);
                continue;
            }

            // Find elements - use original note name with octave for DOM selection
            const selector = `.${stringName} .note.${noteName.toLowerCase()}`;
            const noteElements = document.querySelectorAll(selector);

            // If no exact notes found, try with base note (without octave)
            if (noteElements.length === 0) {
                const baseSelector = `.${stringName} .note.${baseNote}`;
                const baseNoteElements = document.querySelectorAll(baseSelector);

                baseNoteElements.forEach(noteEl => {
                    noteEl.classList.add('active');

                    // Find tone element
                    const toneEl = noteEl.querySelector('img.tone');
                    if (toneEl) {
                        toneEl.classList.add('active');

                        // If root note, change color
                        if (isRoot) {
                            toneEl.src = '/static/media/red_circle.svg';
                            toneEl.classList.add('root');
                        }
                    }
                });
            } else {
                noteElements.forEach(noteEl => {
                    noteEl.classList.add('active');

                    // Find tone element
                    const toneEl = noteEl.querySelector('img.tone');
                    if (toneEl) {
                        toneEl.classList.add('active');

                    // If root note, change color
                    if (isRoot) {
                        toneEl.src = '/static/media/red_circle.svg';
                        toneEl.classList.add('root');
                    }
                }
            });
            }
        }

        // After processing all strings, check if any notes were activated
        const activatedCount = document.querySelectorAll('.note.active').length;

        // If no notes were activated at all, try more desperate measures
        if (activatedCount === 0) {

            // Look for any notes with classes containing our expected note names
            for (const stringName in positionData) {
                if (!positionData.hasOwnProperty(stringName)) continue;

                // Get note data
                const noteData = positionData[stringName];
                if (!noteData) continue;

                // Get the note name
                let noteName = '';
                if (Array.isArray(noteData)) {
                    noteName = noteData[0].toLowerCase().replace(/[0-9]/g, '');
                } else if (typeof noteData === 'string') {
                    noteName = noteData.toLowerCase().replace(/[0-9]/g, '');
                } else {
                    continue;
                }

                // Try to find any notes on this string
                const stringElements = document.querySelectorAll(`.${stringName} .note`);

                // Check each note's classes to find a match
                stringElements.forEach(noteEl => {
                    const noteClasses = Array.from(noteEl.classList);
                    for (const cls of noteClasses) {
                        if (cls.includes(noteName)) {
                            noteEl.classList.add('active');

                            // Activate the tone
                            const toneEl = noteEl.querySelector('img.tone');
                            if (toneEl) {
                                toneEl.classList.add('active');
                            }

                            // Only activate one note per string
                            break;
                        }
                    }
                });
            }
        }

        // Ensure we have at least one root note
        const rootNotes = document.querySelectorAll('img.tone.root');
        if (rootNotes.length === 0) {
            const firstActive = document.querySelector('.note.active img.tone');
            if (firstActive) {
                firstActive.classList.add('root');
                firstActive.src = '/static/media/red_circle.svg';
            }
        }

    } catch (error) {
        console.error('Error updating tones:', error);
    }
}


// --- NEW HELPER FUNCTIONS ---

/**
 * Updates the relevant UI element to show the current state.
 * - For 'chords' mode, updates the selected option in the '#position_select' dropdown.
 * - For 'scales' mode, logs a warning as the display mechanism is unclear (likely not the select element).
 */
function updateDisplay() {
    // Get the display element directly (in case it's changed)
    const displayElement = document.getElementById('position_select');
    
    // Make sure we have a display element and current mode
    if (!displayElement) {
        console.error("updateDisplay: Display element #position_select not found!");
        return;
    }
    
    if (typeof window.currentMode === 'undefined') {
        console.error("updateDisplay: Current mode (window.currentMode) is not defined!");
        return;
    }

    try {
        if (window.currentMode === 'scales') {
            if (typeof window.currentScalePosition === 'undefined') {
                console.error("updateDisplay (scales): Scale position (window.currentScalePosition) is not defined!");
                return;
            }

            // Target value is the scale position number (0 for "All Notes")
            const targetValue = String(window.currentScalePosition); // Option values are strings

            // Find the option with the target value and select it
            let foundOption = false;
            for (let i = 0; i < displayElement.options.length; i++) {
                if (displayElement.options[i].value === targetValue) {
                    displayElement.selectedIndex = i;
                    foundOption = true;
                    console.log(`updateDisplay (scales): Selected option with value "${targetValue}"`);
                    break;
                }
            }

            if (!foundOption) {
                console.warn(`updateDisplay (scales): Option with value "${targetValue}" not found in #position_select.`);
            }
            
            // Update the custom select display if it exists
            const customDisplay = document.querySelector('.select-selected');
            if (customDisplay && foundOption) {
                customDisplay.innerHTML = displayElement.options[displayElement.selectedIndex].innerHTML;
            }
        } else if (window.currentMode === 'chords') {
            if (!displayElement || displayElement.tagName !== 'SELECT') {
                 console.error("updateDisplay (chords): displayElement is not a SELECT element or is null. Expected #position_select.");
                 return;
            }
             if (typeof window.currentInversion === 'undefined') {
                 console.error("updateDisplay (chords): Chord inversion (window.currentInversion) is not defined!");
                 return;
             }

            // Determine the target option value based on inversion number
            let targetValue = null;
            switch (window.currentInversion) {
                case 0:
                    // The HTML uses "Root Position", while internal logic might use "Basic Position". Map 0 to "Root Position".
                    targetValue = "Root Position";
                    break;
                case 1:
                    targetValue = "1st Inversion"; // Assuming HTML uses "1st Inversion"
                    break;
                case 2:
                    targetValue = "2nd Inversion"; // Assuming HTML uses "2nd Inversion"
                    break;
                case 3:
                    // Only valid for fourNote chords
                    if (typeof window.currentChordType !== 'undefined' && window.currentChordType === 'fourNote') {
                         targetValue = "3rd Inversion"; // Assuming HTML uses "3rd Inversion"
                    } else {
                        console.warn("updateDisplay (chords): Inversion 3 requested for non-fourNote chord type:", window.currentChordType);
                        // Don't change selection if invalid state is reached
                        return;
                    }
                    break;
                default:
                     console.warn("updateDisplay (chords): Unknown currentInversion:", window.currentInversion);
                     return; // Don't change selection
            }

            // Find the option with the target value and select it
            let foundOption = false;
            for (let i = 0; i < displayElement.options.length; i++) {
                if (displayElement.options[i].value === targetValue) {
                    displayElement.selectedIndex = i;
                    foundOption = true;
                    console.log(`updateDisplay (chords): Selected option "${targetValue}"`);
                    break;
                }
            }

            if (!foundOption) {
                console.warn(`updateDisplay (chords): Option with value "${targetValue}" not found in #position_select.`);
            }

            // Optional: Trigger a change event if other parts of the app listen for it
            // displayElement.dispatchEvent(new Event('change'));

        } else {
            console.warn("updateDisplay: Unknown currentMode:", window.currentMode);
        }
    } catch (e) {
        console.error("Error in updateDisplay:", e);
    }
}

/**
 * Updates the visibility of the left and right cursor elements based on the current state.
 */
function updateCursorVisibility() {
    // Find cursor elements dynamically each time, as they might be added/removed
    const leftCursor = document.querySelector('.left-cursor');
    const rightCursor = document.querySelector('.right-cursor');

    // Log if elements are found (for debugging)
    // console.log("updateCursorVisibility - Found elements:", { leftCursor, rightCursor });

     if (typeof window.currentMode === 'undefined') {
        console.error("updateCursorVisibility: Current mode (window.currentMode) is not defined!");
        // Hide both cursors if possible on error
        if (leftCursor) leftCursor.style.visibility = 'hidden';
        if (rightCursor) rightCursor.style.visibility = 'hidden';
        return;
    }

    try {
        let hideLeft = false;
        let hideRight = false;

        if (window.currentMode === 'scales') {
             if (typeof window.currentScalePosition === 'undefined' || typeof window.maxScalePosition === 'undefined') {
                 console.error("Scale state (window.currentScalePosition, window.maxScalePosition) is not defined!");
                 hideLeft = true; // Hide both on error
                 hideRight = true;
             } else {
                hideLeft = window.currentScalePosition <= 0; // Hide if 0 or less
                hideRight = window.currentScalePosition >= window.maxScalePosition; // Hide if max or more
             }
        } else if (window.currentMode === 'chords') {
             if (typeof window.currentInversion === 'undefined' || typeof window.currentChordType === 'undefined') {
                 console.error("Chord state (window.currentInversion, window.currentChordType) is not defined!");
                 hideLeft = true; // Hide both on error
                 hideRight = true;
             } else {
                const maxInversion = (window.currentChordType === 'triad') ? 2 : 3;
                hideLeft = window.currentInversion <= 0; // Hide if 0 or less
                hideRight = window.currentInversion >= maxInversion; // Hide if max or more
             }
        } else {
             console.warn("Unknown currentMode in updateCursorVisibility:", window.currentMode);
             hideLeft = true; // Hide both on unknown mode
             hideRight = true;
        }

        // Incorrect block removed. The correct logic using locally queried cursors follows.
        if (leftCursor) {
            leftCursor.style.visibility = hideLeft ? 'hidden' : 'visible';
        } else {
            // Log error if expected cursor is missing when trying to update visibility
            // console.error("updateCursorVisibility: Left cursor element (.left-cursor) not found when trying to set visibility.");
        }

        if (rightCursor) {
            rightCursor.style.visibility = hideRight ? 'hidden' : 'visible';
        } else {
             // Log error if expected cursor is missing when trying to update visibility
            // console.error("updateCursorVisibility: Right cursor element (.right-cursor) not found when trying to set visibility.");
        }

    } catch(e) {
        console.error("Error in updateCursorVisibility:", e);
        // Attempt to hide cursors on error if they exist
        try {
            const lc = document.querySelector('.left-cursor');
            const rc = document.querySelector('.right-cursor');
            if (lc) lc.style.visibility = 'hidden';
            if (rc) rc.style.visibility = 'hidden';
        } catch (finalError) {
            console.error("Could not hide cursors during error handling:", finalError);
        }
    }
}

/**
 * Helper function to get the string name of a chord position based on inversion number.
 * @param {number} inversionNumber - The inversion number (0, 1, 2, 3).
 * @param {string} chordType - The type of chord ('triad' or 'fourNote').
 * @returns {string|null} The position name or null if invalid.
 */
function getPositionNameFromInversion(inversionNumber, chordType) {
    switch (inversionNumber) {
        case 0: return "Root Position"; // Or "Basic Position" if that's used elsewhere
        case 1: return "1st Inversion";
        case 2: return "2nd Inversion";
        case 3:
            // Only valid for fourNote chords
            if (chordType === 'fourNote') {
                 return "3rd Inversion";
            } else {
                console.warn("getPositionNameFromInversion: Inversion 3 requested for non-fourNote chord type:", chordType);
                return null; // Invalid state
            }
        default:
             console.warn("getPositionNameFromInversion: Unknown inversionNumber:", inversionNumber);
             return null; // Unknown state
    }
}

// --- END NEW HELPER FUNCTIONS ---


// --- UPDATED CURSOR CLICK HANDLERS ---

/**
 * Handles the logic when the left cursor is clicked.
 * Decrements the state (scale position or chord inversion) based on the current mode.
 */
function fpfLeftCursorClick() { // Renamed
    // Log current state on click entry (using window object)
    console.log("fpfLeftCursorClick - State:", { // Renamed log
        currentMode: window.currentMode,
        currentScalePosition: window.currentScalePosition,
        maxScalePosition: window.maxScalePosition,
        currentChordType: window.currentChordType,
        currentInversion: window.currentInversion
    });

    // Ensure global variables are accessible (from window object)
    if (typeof window.currentMode === 'undefined') {
        console.error("fpfLeftCursorClick: currentMode is not defined!"); // Renamed log
        return; // Stop execution if mode is unknown
    }

    try {
        if (window.currentMode === 'scales') {
            // Ensure scale state variables are defined
            if (typeof window.currentScalePosition === 'undefined') {
                 console.error("fpfLeftCursorClick (scales): currentScalePosition is not defined!"); // Renamed log
                 return;
            }
            if (window.currentScalePosition > 0) {
                window.currentScalePosition--;
            }
            // Stop at 0 (no wrap around)
        } else if (window.currentMode === 'chords') {
             // Ensure chord state variables are defined
             if (typeof window.currentInversion === 'undefined' || typeof window.currentChordType === 'undefined') {
                 console.error("fpfLeftCursorClick (chords): currentInversion or currentChordType is not defined!"); // Renamed log
                 return;
             }
            const maxInversion = (window.currentChordType === 'triad') ? 2 : 3;
            window.currentInversion--;
            if (window.currentInversion < 0) {
                window.currentInversion = maxInversion; // Wrap around from -1 to max
            }
        } else {
             console.warn("fpfLeftCursorClick: Unknown currentMode:", window.currentMode); // Renamed log
             return; // Do nothing if mode is unknown
        }

        // Update UI after state change
        updateDisplay();
        updateCursorVisibility();
        // Trigger note update based on the new state
        if (window.currentMode === 'scales') {
            if (typeof getTonesFromDataScales === 'function') {
                console.log(`Triggering getTonesFromDataScales for position ${window.currentScalePosition}`);
                getTonesFromDataScales(String(window.currentScalePosition)); // Ensure it's a string if needed
            } else {
                console.warn("getTonesFromDataScales function not found.");
            }
        } else if (window.currentMode === 'chords') {
            if (typeof getTonesFromDataChords === 'function') {
                const positionName = getPositionNameFromInversion(window.currentInversion, window.currentChordType);
                const currentRange = getQueryParam('note_range'); // Get current range
                if (positionName && currentRange) {
                     console.log(`Triggering getTonesFromDataChords for position "${positionName}" and range "${currentRange}"`);
                     getTonesFromDataChords(positionName, currentRange);
                } else {
                     console.warn("Could not trigger getTonesFromDataChords due to invalid positionName or missing range.", { positionName, currentRange });
                }
            } else {
                 console.warn("getTonesFromDataChords function not found.");
            }
        }

        // Dispatch a navigation complete event for listeners
        console.log(`LEFT cursor navigation: mode=${window.currentMode}, inversion=${window.currentInversion}`);
        document.dispatchEvent(new CustomEvent('cursor-navigation-complete', {
            detail: { 
                direction: 'left', 
                mode: window.currentMode,
                inversion: window.currentInversion
            }
        }));
        
        // Restore multi-inversion display if in chords mode
        if (window.currentMode === 'chords') {
            if (typeof window.forceCorrectInversionDisplay === 'function') {
                // Use the force fix for direct correction - most reliable method
                setTimeout(window.forceCorrectInversionDisplay, 150);
            } else if (typeof window.updateChordInversions === 'function') {
                window.updateChordInversions();
            } else if (typeof enhanceChordDisplay === 'function') {
                setTimeout(enhanceChordDisplay, 150);
            }
        }
    } catch (e) {
        console.error("Error in fpfLeftCursorClick:", e); // Renamed log
        // Optionally try to reset UI or log error state
    }
}

/**
 * Handles the logic when the right cursor is clicked.
 * Increments the state (scale position or chord inversion) based on the current mode.
 */
function fpfRightCursorClick() { // Renamed
    // Log current state on click entry (using window object)
    console.log("fpfRightCursorClick - State:", { // Renamed log
        currentMode: window.currentMode,
        currentScalePosition: window.currentScalePosition,
        maxScalePosition: window.maxScalePosition,
        currentChordType: window.currentChordType,
        currentInversion: window.currentInversion
    });

     // Ensure global variables are accessible (from window object)
    if (typeof window.currentMode === 'undefined') {
        console.error("fpfRightCursorClick: currentMode is not defined!"); // Renamed log
        return; // Stop execution if mode is unknown
    }

    try {
        if (window.currentMode === 'scales') {
             // Ensure scale state variables are defined
             if (typeof window.currentScalePosition === 'undefined' || typeof window.maxScalePosition === 'undefined') {
                 console.error("rightCursorClick (scales): currentScalePosition or maxScalePosition is not defined!");
                 return;
             }
            if (window.currentScalePosition < window.maxScalePosition) {
                window.currentScalePosition++;
            }
            // Stop at maxScalePosition (no wrap around)
        } else if (window.currentMode === 'chords') {
             // Ensure chord state variables are defined
             if (typeof window.currentInversion === 'undefined' || typeof window.currentChordType === 'undefined') {
                 console.error("rightCursorClick (chords): currentInversion or currentChordType is not defined!");
                 return;
             }
            const maxInversion = (window.currentChordType === 'triad') ? 2 : 3;
            window.currentInversion++;
            if (window.currentInversion > maxInversion) {
                window.currentInversion = 0; // Wrap around from max+1 to 0
            }
        } else {
             console.warn("fpfRightCursorClick: Unknown currentMode:", window.currentMode); // Renamed log
             return; // Do nothing if mode is unknown
        }

        // Update UI after state change
        updateDisplay();
        updateCursorVisibility();

        // Trigger note update based on the new state
        if (window.currentMode === 'scales') {
            if (typeof getTonesFromDataScales === 'function') {
                 console.log(`Triggering getTonesFromDataScales for position ${window.currentScalePosition}`);
                 getTonesFromDataScales(String(window.currentScalePosition)); // Ensure it's a string if needed
            } else {
                 console.warn("getTonesFromDataScales function not found.");
            }
        } else if (window.currentMode === 'chords') {
             if (typeof getTonesFromDataChords === 'function') {
                 const positionName = getPositionNameFromInversion(window.currentInversion, window.currentChordType);
                 const currentRange = getQueryParam('note_range'); // Get current range
                 if (positionName && currentRange) {
                     console.log(`Triggering getTonesFromDataChords for position "${positionName}" and range "${currentRange}"`);
                     getTonesFromDataChords(positionName, currentRange);
                 } else {
                     console.warn("Could not trigger getTonesFromDataChords due to invalid positionName or missing range.", { positionName, currentRange });
                 }
             } else {
                 console.warn("getTonesFromDataChords function not found.");
             }
        }
        updateDisplay();
        updateCursorVisibility();

        // Dispatch a navigation complete event for listeners
        console.log(`RIGHT cursor navigation: mode=${window.currentMode}, inversion=${window.currentInversion}`);
        document.dispatchEvent(new CustomEvent('cursor-navigation-complete', {
            detail: { 
                direction: 'right', 
                mode: window.currentMode,
                inversion: window.currentInversion
            }
        }));
        
        // Restore multi-inversion display if in chords mode
        if (window.currentMode === 'chords') {
            if (typeof window.forceCorrectInversionDisplay === 'function') {
                // Use the force fix for direct correction - most reliable method
                setTimeout(window.forceCorrectInversionDisplay, 150);
            } else if (typeof window.updateChordInversions === 'function') {
                window.updateChordInversions();
            } else if (typeof enhanceChordDisplay === 'function') {
                setTimeout(enhanceChordDisplay, 150);
            }
        }
    } catch (e) {
        console.error("Error in fpfRightCursorClick:", e); // Renamed log
        // Optionally try to reset UI or log error state
    }
}

// --- END UPDATED CURSOR CLICK HANDLERS ---


// --- EXISTING CODE BELOW (Initialization, other helpers) ---

// Initialize cursor navigation
// Create a flag to prevent multiple initializations
let cursorInversionInitialized = false;

document.addEventListener('DOMContentLoaded', function() {
    // Prevent multiple initializations
    if (cursorInversionInitialized) {
        return;
    }
    cursorInversionInitialized = true;

    // --- Define Helper Functions within DOMContentLoaded scope ---

    /**
     * Helper function to get available positions based on range (from voicing_data)
     * (Existing function)
     */
    function getAvailablePositions(range) {
        if (typeof voicing_data !== 'undefined' && voicing_data && voicing_data[range]) {
            return Object.keys(voicing_data[range]).filter(pos => pos && !/^\d+$/.test(pos));
        }
        return []; // Return empty array if data not found
    }

    /**
     * Helper function to update a URL parameter without reloading the page
     * (Existing function)
     */
    function updateUrlParam(param, value) {
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set(param, value);
        const newUrl = window.location.pathname + '?' + urlParams.toString();
        window.history.replaceState(null, '', newUrl);
    }

    /**
     * Function to refresh the inversion display (e.g., highlighting the active one)
     * (Existing function - might need adjustments based on how state is managed now)
     */
    function refreshInversionDisplay() {
        console.log("refreshInversionDisplay called"); // Add log
        const currentPosition = getQueryParam('position_select');
        const currentRange = getQueryParam('note_range');
        const chordType = getChordType(); // Get current chord type
        const positions = getChordPositions(chordType); // Use the robust function

        console.log("Refresh - Current Position:", currentPosition, "Range:", currentRange, "Type:", chordType, "Available:", positions); // Add log

        if (!currentPosition || !positions || positions.length === 0) {
            console.warn("Refresh - Cannot refresh display: Missing current position or available positions.");
            return;
        }

        const displayContainer = document.getElementById('inversion-display-container'); // Assuming this container exists
        if (!displayContainer) {
            console.warn("Refresh - Inversion display container not found.");
            return;
        }

        // Clear previous display
        // displayContainer.innerHTML = ''; // Or update existing elements

        // Example: Update opacity or classes based on currentPosition
        const inversionElements = displayContainer.querySelectorAll('.inversion-item'); // Assuming items have this class

        // Find the root note for the current position (example logic)
        let rootNote = 'N/A';
        if (typeof voicing_data !== 'undefined' && voicing_data[currentRange] && voicing_data[currentRange][currentPosition]) {
            // Simplified root note finding - adjust based on actual data structure
            const positionData = voicing_data[currentRange][currentPosition];
            // Example: Find the first note marked as 'Root' or 'R'
            for (const stringKey in positionData) {
                const noteInfo = positionData[stringKey];
                if (Array.isArray(noteInfo) && (noteInfo[1] === 'Root' || noteInfo[1] === 'R' || noteInfo[2] === 'Root' || noteInfo[2] === 'R')) {
                    rootNote = noteInfo[0];
                    break;
                }
            }
        }

        // Update the root note display element
        const rootNoteDisplay = document.getElementById('current-root-note'); // Assuming this exists
        if (rootNoteDisplay) {
            rootNoteDisplay.textContent = `Root: ${rootNote}`;
            console.log("Refresh - Updated root note display:", rootNote); // Add log
        } else {
            console.warn("Refresh - Root note display element not found.");
        }


        // Update individual inversion items (example)
        inversionElements.forEach(item => {
            const itemPosition = item.dataset.position; // Assuming position is stored in data attribute
            if (itemPosition === currentPosition) {
                item.classList.add('active-inversion');
                item.style.opacity = '1';
            } else {
                item.classList.remove('active-inversion');
                item.style.opacity = '0.5'; // Example: Dim inactive inversions
            }
        });
         console.log("Refresh - Inversion display updated for position:", currentPosition); // Add log


        // --- Potentially redundant root note logic from original file ---
        // This seems complex and might be handled differently now. Review if needed.
        /*
        const rootNotesByPosition = {
            'Root Position': 'C', 'First Inversion': 'E', 'Second Inversion': 'G', 'Third Inversion': 'Bb' // Example for C7
        };
        const currentRoot = rootNotesByPosition[currentPosition] || '?';
        */

        // --- Potentially redundant chord structure display logic ---
        /*
        const chordStructureElement = document.getElementById('chord-structure-display');
        if (chordStructureElement) {
            // Logic to display chord structure based on chordType
            chordStructureElement.textContent = `Structure for ${chordType}`; // Placeholder
        }
        */
    }

    // --- End Helper Function Definitions ---


    // Code previously inside setTimeout now runs directly in DOMContentLoaded
    console.log("DOMContentLoaded callback executed (no setTimeout)."); // Add log

        console.log("DOMContentLoaded setTimeout callback executed."); // Add log

        // Assign only the display element globally, as cursors might be dynamic
        displayElement = document.getElementById('position_select'); // Updated ID
        console.log("cursor-inversion.js: Display Element Assigned:", { displayElement });
        if (!displayElement) {
            console.error("cursor-inversion.js: Display element with ID 'position_select' not found!");
        }
// Attempt to find cursor elements and remove inline onclick handlers
// This runs once on DOMContentLoaded. If elements are added later, this won't catch them,
// but the delegated listener below should still work.
const leftCursorDiv = document.querySelector('.left-cursor');
const rightCursorDiv = document.querySelector('.right-cursor');

if (leftCursorDiv && leftCursorDiv.hasAttribute('onclick')) {
    console.log("DOMContentLoaded: Removing inline onclick from .left-cursor");
    leftCursorDiv.removeAttribute('onclick');
} else if (leftCursorDiv) {
     console.log("DOMContentLoaded: .left-cursor found, but no inline onclick attribute.");
} else {
     // It's possible they haven't been added yet, which is okay for the delegated listener
     console.warn("DOMContentLoaded: .left-cursor element not found at this time.");
}

if (rightCursorDiv && rightCursorDiv.hasAttribute('onclick')) {
    console.log("DOMContentLoaded: Removing inline onclick from .right-cursor");
    rightCursorDiv.removeAttribute('onclick');
 } else if (rightCursorDiv) {
     console.log("DOMContentLoaded: .right-cursor found, but no inline onclick attribute.");
} else {
     // It's possible they haven't been added yet, which is okay for the delegated listener
     console.warn("DOMContentLoaded: .right-cursor element not found at this time.");
}

// Use event delegation (capture phase) for cursor clicks on the body
        // Use event delegation for cursor clicks on the body
        document.body.addEventListener('click', function(event) { // Add 'true' for capture phase
            // Log the actual clicked element for debugging delegation
            console.log("Body click detected. Target:", event.target);

            // Check if the clicked element (or its parent) is the left cursor
            const leftTarget = event.target.closest('.left-cursor');
            const rightTarget = event.target.closest('.right-cursor');

            if (leftTarget) {
                console.log("Delegated click: Left cursor detected.");
                event.preventDefault(); // Prevent default action (if any)
                event.stopPropagation(); // Stop event from bubbling further (e.g., to inline onclick)
                fpfLeftCursorClick(); // Call renamed function
            } // End if (leftTarget)
            // Check if the clicked element (or its parent) is the right cursor
            else if (rightTarget) {
                console.log("Delegated click: Right cursor detected.");
                event.preventDefault(); // Prevent default action (if any)
                event.stopPropagation(); // Stop event from bubbling further (e.g., to inline onclick)
                fpfRightCursorClick(); // Call renamed function
            } // End else if (rightTarget)
            // Extra closing brace removed
        }, true); // Use capture phase
        console.log("cursor-inversion.js: Delegated click listener added to body.");

        // Initial UI setup - updateDisplay should work, updateCursorVisibility needs modification
        // Note: left/rightCursorElement are no longer assigned globally here
        try {
             if (typeof updateDisplay === 'function' && typeof updateCursorVisibility === 'function') {
                 console.log("Performing initial display and cursor visibility update.");
                 updateDisplay(); // Should work if displayElement was found
                 updateCursorVisibility(); // Will need modification
             } else {
                 console.error("Initial setup failed: updateDisplay or updateCursorVisibility not defined.");
             }
        } catch (initError) {
             console.error("Error during initial UI setup:", initError);
        }

        // Duplicate initial setup block removed.

        // --- Keep potentially relevant existing helper functions ---
        // These might be used by other parts of the application or future features.

        // Helper functions moved outside setTimeout
    // End of code previously inside setTimeout

}); // End DOMContentLoaded
; // Add semicolon just in case

// --- End Existing Code ---
