/**
 * Unified Cursor Navigation System for Fretboard Position Finder
 * 
 * This file consolidates all cursor navigation functionality for both:
 * - Scales/Arpeggios: Navigate between positions (All, Pos 1, Pos 2, etc.)
 * - Chords: Cycle through inversions (Root, 1st Inversion, 2nd Inversion, etc.)
 * 
 * Behavior:
 * - Left Cursor: Go to previous position/inversion (wrap around for chords)
 * - Right Cursor: Go to next position/inversion (wrap around for chords)
 * - Cursor visibility: Hide cursors when no more positions available
 */

// ---- GLOBAL STATE ----
window.fpf = window.fpf || {}; // Global namespace for our functionality
window.fpf.cursor = {
    mode: null,           // 'scales' or 'chords'
    position: 0,          // Current scale position (0 = "All Positions")
    maxPosition: 5,       // Maximum scale position
    chordType: 'triad',   // 'triad' or 'fourNote'
    inversion: 0,         // Current chord inversion (0 = Root Position)
    maxInversion: 2,      // Maximum chord inversion
    initialized: false,   // Flag to prevent multiple initializations
    debugMode: true       // Enable detailed debug logging
};

// Helper function to log debug information
function cursorDebugLog(message, data = null) {
    if (window.fpf.cursor.debugMode) {
        if (data) {
            console.log(`CURSOR_DEBUG_LOG: ${message}`, data);
        } else {
            console.log(`CURSOR_DEBUG_LOG: ${message}`);
        }
    }
}

// ---- HELPER FUNCTIONS ----

/**
 * Get a query parameter from the URL
 * @param {string} param - Parameter name
 * @return {string|null} Parameter value or null if not found
 */
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

/**
 * Update a URL parameter without reloading the page
 * @param {string} param - Parameter name
 * @param {string} value - New parameter value
 */
function updateUrlParam(param, value) {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set(param, value);
    const newUrl = window.location.pathname + '?' + urlParams.toString();
    window.history.replaceState(null, '', newUrl);
}

/**
 * Get the current chord type from URL or select element
 * @return {string} Chord type (e.g., 'Major', 'Minor7', etc.)
 */
function getChordType() {
    // First check URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('chords_options_select')) {
        return urlParams.get('chords_options_select');
    }

    // Then check chord select element
    const chordSelect = document.getElementById('chords_options_select');
    if (chordSelect && chordSelect.selectedIndex >= 0) {
        return chordSelect.options[chordSelect.selectedIndex].value;
    }

    // Default to Major
    return 'Major';
}

/**
 * Determine if chord type is a four-note chord (7th, 9th, etc.)
 * @param {string} chordType - The chord type to check
 * @return {boolean} True if it's a four+ note chord
 */
function isFourNoteChord(chordType) {
    return chordType.includes('7') || 
           chordType.includes('9') || 
           chordType.includes('11') || 
           chordType.includes('13');
}

/**
 * Get the position name based on inversion index
 * @param {number} inversion - Inversion index (0, 1, 2, 3)
 * @return {string} Position name (Root Position, 1st Inversion, etc.)
 */
function getPositionName(inversion) {
    switch (inversion) {
        case 0: return "Root Position";
        case 1: return "First Inversion";
        case 2: return "Second Inversion";
        case 3: return "Third Inversion";
        default: return "Root Position";
    }
}

/**
 * Get inversion index from position name
 * @param {string} position - Position name
 * @return {number} Inversion index (0, 1, 2, 3)
 */
function getInversionIndex(position) {
    if (!position) return 0;
    
    position = position.toLowerCase();
    if (position.includes('root') || position.includes('basic')) {
        return 0;
    } else if (position.includes('first') || position.includes('1st')) {
        return 1;
    } else if (position.includes('second') || position.includes('2nd')) {
        return 2;
    } else if (position.includes('third') || position.includes('3rd')) {
        return 3;
    }
    return 0; // Default to root position
}

/**
 * Get available positions for the current chord type
 * @return {Array} Array of position names
 */
function getAvailablePositions() {
    const chordType = getChordType();
    const isFourNote = isFourNoteChord(chordType);
    
    // Default positions based on chord type
    let positions = ['Root Position', 'First Inversion', 'Second Inversion'];
    
    // Add third inversion for four-note chords
    if (isFourNote) {
        positions.push('Third Inversion');
    }
    
    // Try to get positions from voicing_data if available
    if (typeof voicing_data !== 'undefined' && voicing_data) {
        const range = getQueryParam('note_range') || 
                     (document.getElementById('note_range') ? 
                      document.getElementById('note_range').value : 'e - g');
                      
        if (voicing_data[range]) {
            const dataPositions = Object.keys(voicing_data[range])
                .filter(pos => pos && !/^\d+$/.test(pos) && 
                       typeof voicing_data[range][pos] === 'object');
                
            if (dataPositions.length > 0) {
                // Normalize position names for consistency
                return dataPositions.map(pos => {
                    if (pos === 'Basic Position') return 'Root Position';
                    if (pos.includes('First Root') || pos.includes('First Basic')) 
                        return 'Root Position';
                    return pos;
                });
            }
        }
    }
    
    // Try to get positions from position_select element
    const positionSelect = document.getElementById('position_select');
    if (positionSelect && positionSelect.options.length > 0) {
        const uniquePositions = new Set();
        for (let i = 0; i < positionSelect.options.length; i++) {
            const value = positionSelect.options[i].value;
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
 * Create cursor elements if they don't exist
 */
function ensureCursorElements() {
    let leftCursor = document.querySelector('.left-cursor');
    let rightCursor = document.querySelector('.right-cursor');
    
    // Only create elements if they don't exist
    if (!leftCursor) {
        console.log("Creating left cursor element");
        leftCursor = document.createElement('div');
        leftCursor.className = 'left-cursor';
        leftCursor.style.position = 'absolute';
        leftCursor.style.top = '50%';
        leftCursor.style.left = '15px';
        leftCursor.style.width = '30px';
        leftCursor.style.height = '30px';
        leftCursor.style.transform = 'translateY(-50%)';
        leftCursor.style.backgroundColor = 'rgba(0, 0, 0, 0.2)';
        leftCursor.style.borderRadius = '50%';
        leftCursor.style.cursor = 'pointer';
        leftCursor.style.zIndex = '999';
        
        // Add to document body
        document.body.appendChild(leftCursor);
        
        // Add click event
        leftCursor.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            window.fpfLeftCursorClick();
        });
    }
    
    if (!rightCursor) {
        console.log("Creating right cursor element");
        rightCursor = document.createElement('div');
        rightCursor.className = 'right-cursor';
        rightCursor.style.position = 'absolute';
        rightCursor.style.top = '50%';
        rightCursor.style.right = '15px';
        rightCursor.style.width = '30px';
        rightCursor.style.height = '30px';
        rightCursor.style.transform = 'translateY(-50%)';
        rightCursor.style.backgroundColor = 'rgba(0, 0, 0, 0.2)';
        rightCursor.style.borderRadius = '50%';
        rightCursor.style.cursor = 'pointer';
        rightCursor.style.zIndex = '999';
        
        // Add to document body
        document.body.appendChild(rightCursor);
        
        // Add click event
        rightCursor.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            window.fpfRightCursorClick();
        });
    }
    
    return { leftCursor, rightCursor };
}

// ---- UI UPDATE FUNCTIONS ----

/**
 * Update scale display with the new position value
 * @param {number} positionValue - The position value (0, 1, 2, etc.)
 */
function updateScaleDisplay(positionValue) {
    console.log("updateScaleDisplay - Updating to position:", positionValue);
    
    // Update the select dropdown
    const positionSelect = document.getElementById('position_select');
    if (positionSelect) {
        positionSelect.value = String(positionValue);
        
        // Trigger change event to update UI
        const event = new Event('change');
        positionSelect.dispatchEvent(event);
    }
    
    // Update URL parameter
    updateUrlParam('position_select', positionValue);
    
    // Most important: Call the getTonesFromDataScales function to update the fretboard
    if (typeof getTonesFromDataScales === 'function') {
        // Make sure we reset any previous state
        if (typeof resetFretboard === 'function') {
            resetFretboard();
        }
        getTonesFromDataScales(String(positionValue));
    } else {
        console.error("getTonesFromDataScales function not found. Scale position cannot be updated.");
    }
}

/**
 * Update chord display with the new inversion
 * @param {number} inversionValue - The inversion index (0, 1, 2, 3)
 */
function updateChordDisplay(inversionValue) {
    // Get position name from inversion index
    const positionName = getPositionName(inversionValue);
    cursorDebugLog(`updateChordDisplay - Inversion: ${inversionValue}, Position: "${positionName}"`);
    
    // Update the select dropdown
    const positionSelect = document.getElementById('position_select');
    let foundMatchingOption = false;
    
    if (positionSelect) {
        // Find option with matching position name
        for (let i = 0; i < positionSelect.options.length; i++) {
            const optionValue = positionSelect.options[i].value;
            if (optionValue === positionName ||
                (positionName === 'Root Position' && optionValue === 'Basic Position')) {
                positionSelect.selectedIndex = i;
                foundMatchingOption = true;
                cursorDebugLog(`Found matching option: "${optionValue}" at index: ${i}`);
                break;
            }
        }
        
        if (!foundMatchingOption) {
            cursorDebugLog(`No matching option found for position: "${positionName}"`);
            cursorDebugLog(`Available options:`, Array.from(positionSelect.options).map(o => o.value));
        }
        
        // Trigger change event to update UI
        const event = new Event('change');
        positionSelect.dispatchEvent(event);
    }
    
    // Update URL parameter
    updateUrlParam('position_select', positionName);
    
    // Get current range - try multiple sources
    let range = null;
    
    // Try URL param first
    const urlParams = new URLSearchParams(window.location.search);
    range = urlParams.get('note_range');
    
    // If not in URL, try select element
    if (!range) {
        const rangeSelect = document.getElementById('note_range');
        if (rangeSelect) {
            range = rangeSelect.value;
        }
    }
    
    // If still not found, try existing voicing_data
    if (!range && typeof voicing_data !== 'undefined' && voicing_data.note_range) {
        range = voicing_data.note_range;
    }
    
    // Try controller as another source if all else fails
    if (!range && window.chordFretboardController && window.chordFretboardController.chordState) {
        range = window.chordFretboardController.chordState.currentRange;
    }
    
    // Default if all else fails
    if (!range) {
        range = 'e - g';
    }
    
    cursorDebugLog(`Using note range: "${range}"`);
    
    // DIRECT CONTROLLER CALL APPROACH
    // If the unified controller is available, use it directly
    if (window.chordFretboardController) {
        cursorDebugLog(`Calling unified controller.updateChordDisplay directly`);
        try {
            window.chordFretboardController.updateChordDisplay(positionName, range);
            return; // Exit early if we successfully called the controller
        } catch (err) {
            cursorDebugLog(`Error calling controller directly: ${err.message}`);
            // Continue to fallback methods
        }
    }
    
    // BRIDGE FUNCTION APPROACH
    // Most important: Call the getTonesFromDataChords function to update the fretboard
    if (typeof window.getTonesFromDataChords === 'function') {
        cursorDebugLog(`Calling getTonesFromDataChords bridge with position: "${positionName}", range: "${range}"`);
        try {
            window.getTonesFromDataChords(positionName, range);
        } catch (err) {
            cursorDebugLog(`Error in getTonesFromDataChords: ${err.message}`);
            
            // Try alternate case
            if (positionName === 'Root Position') {
                cursorDebugLog(`Retrying with 'Basic Position'`);
                try {
                    window.getTonesFromDataChords('Basic Position', range);
                } catch (err2) {
                    cursorDebugLog(`Error in retry attempt: ${err2.message}`);
                }
            }
        }
    } else {
        cursorDebugLog(`ERROR: getTonesFromDataChords function not found. Chord inversion cannot be updated.`);
    }
    
    // Try to trigger any additional display updates
    if (typeof refreshChordDisplay === 'function') {
        cursorDebugLog(`Calling refreshChordDisplay helper`);
        setTimeout(refreshChordDisplay, 50);
    }
    
    if (typeof updateVoicingsDisplay === 'function') {
        cursorDebugLog(`Calling updateVoicingsDisplay helper`);
        setTimeout(updateVoicingsDisplay, 50);
    }
}

/**
 * Update cursor visibility based on current state
 */
function updateCursorVisibility() {
    const state = window.fpf.cursor;
    
    // Ensure cursor elements exist
    const { leftCursor, rightCursor } = ensureCursorElements();
    
    if (state.mode === 'scales') {
        // Hide left cursor when at "All Positions" (0)
        leftCursor.style.visibility = (state.position <= 0) ? 'hidden' : 'visible';
        leftCursor.style.display = (state.position <= 0) ? 'none' : 'block';
        
        // Hide right cursor when at max position
        rightCursor.style.visibility = (state.position >= state.maxPosition) ? 'hidden' : 'visible';
        rightCursor.style.display = (state.position >= state.maxPosition) ? 'none' : 'block';
        
        cursorDebugLog(`Scales cursor visibility updated - left: ${leftCursor.style.visibility}, right: ${rightCursor.style.visibility}`);
        cursorDebugLog(`Scales cursor state - position: ${state.position}, maxPosition: ${state.maxPosition}`);
    } else if (state.mode === 'chords') {
        // For chords, we use the maxInversion properly
        const maxInversion = state.maxInversion || ((state.chordType === 'triad') ? 2 : 3);
        
        leftCursor.style.visibility = (state.inversion <= 0) ? 'hidden' : 'visible';
        leftCursor.style.display = (state.inversion <= 0) ? 'none' : 'block';
        
        rightCursor.style.visibility = (state.inversion >= maxInversion) ? 'hidden' : 'visible';
        rightCursor.style.display = (state.inversion >= maxInversion) ? 'none' : 'block';
        
        cursorDebugLog(`Chords cursor visibility updated - left: ${leftCursor.style.visibility}, right: ${rightCursor.style.visibility}`);
        cursorDebugLog(`Chords cursor state - inversion: ${state.inversion}, maxInversion: ${maxInversion}, chordType: ${state.chordType}`);
    } else {
        // Unknown mode, hide both cursors
        leftCursor.style.visibility = 'hidden';
        leftCursor.style.display = 'none';
        rightCursor.style.visibility = 'hidden';
        rightCursor.style.display = 'none';
        
        cursorDebugLog(`Mode not recognized: ${state.mode}, hiding cursors`);
    }
}

// ---- MAIN CURSOR CLICK FUNCTIONS ----

/**
 * Left cursor click handler
 * Move to previous position/inversion
 */
window.fpfLeftCursorClick = function() {
    const state = window.fpf.cursor;
    cursorDebugLog(`Left cursor clicked in mode: ${state.mode}`);
    
    if (state.mode === 'scales') {
        // For scales: Go back one position, stop at 0
        if (state.position > 0) {
            state.position--;
            cursorDebugLog(`Scales mode: updating position to ${state.position}`);
            updateScaleDisplay(state.position);
        } else {
            cursorDebugLog(`Scales mode: already at position 0, not changing`);
        }
    } else if (state.mode === 'chords') {
        // For chords: Go back one inversion, wrap around to max
        const maxInversion = state.maxInversion || ((state.chordType === 'triad') ? 2 : 3);
        
        state.inversion--;
        if (state.inversion < 0) {
            state.inversion = maxInversion;
        }
        cursorDebugLog(`Chords mode: updating inversion to ${state.inversion}`);
        cursorDebugLog(`Chords mode: mapped to position name "${getPositionName(state.inversion)}"`);
        updateChordDisplay(state.inversion);
    } else {
        cursorDebugLog(`Unknown mode: ${state.mode}, cannot handle left click`);
        return;
    }
    
    // Update cursor visibility
    updateCursorVisibility();
    
    // Dispatch event for other components
    document.dispatchEvent(new CustomEvent('cursor-navigation-complete', {
        detail: { 
            direction: 'left',
            mode: state.mode,
            position: state.position,
            inversion: state.inversion
        }
    }));
    
    // Restore multi-inversion display if in chords mode
    if (state.mode === 'chords') {
        if (typeof window.forceCorrectInversionDisplay === 'function') {
            cursorDebugLog(`Attempting to call forceCorrectInversionDisplay after chord navigation`);
            setTimeout(window.forceCorrectInversionDisplay, 150);
        } else if (typeof window.updateChordInversions === 'function') {
            cursorDebugLog(`Attempting to call updateChordInversions after chord navigation`);
            setTimeout(window.updateChordInversions, 150);
        } else if (typeof enhanceChordDisplay === 'function') {
            cursorDebugLog(`Attempting to call enhanceChordDisplay after chord navigation`);
            setTimeout(enhanceChordDisplay, 150);
        } else {
            cursorDebugLog(`No inversion display enhancement functions found`);
        }
    }
};

/**
 * Right cursor click handler
 * Move to next position/inversion
 */
window.fpfRightCursorClick = function() {
    const state = window.fpf.cursor;
    cursorDebugLog(`Right cursor clicked in mode: ${state.mode}`);
    
    if (state.mode === 'scales') {
        // For scales: Go forward one position, stop at max
        if (state.position < state.maxPosition) {
            state.position++;
            cursorDebugLog(`Scales mode: updating position to ${state.position}`);
            updateScaleDisplay(state.position);
        } else {
            cursorDebugLog(`Scales mode: already at max position ${state.maxPosition}, not changing`);
        }
    } else if (state.mode === 'chords') {
        // For chords: Go forward one inversion, wrap around to 0
        const maxInversion = state.maxInversion || ((state.chordType === 'triad') ? 2 : 3);
        
        state.inversion++;
        if (state.inversion > maxInversion) {
            state.inversion = 0;
        }
        cursorDebugLog(`Chords mode: updating inversion to ${state.inversion}`);
        cursorDebugLog(`Chords mode: mapped to position name "${getPositionName(state.inversion)}"`);
        updateChordDisplay(state.inversion);
    } else {
        cursorDebugLog(`Unknown mode: ${state.mode}, cannot handle right click`);
        return;
    }
    
    // Update cursor visibility
    updateCursorVisibility();
    
    // Dispatch event for other components
    document.dispatchEvent(new CustomEvent('cursor-navigation-complete', {
        detail: { 
            direction: 'right',
            mode: state.mode,
            position: state.position,
            inversion: state.inversion
        }
    }));
    
    // Restore multi-inversion display if in chords mode
    if (state.mode === 'chords') {
        if (typeof window.forceCorrectInversionDisplay === 'function') {
            cursorDebugLog(`Attempting to call forceCorrectInversionDisplay after chord navigation`);
            setTimeout(window.forceCorrectInversionDisplay, 150);
        } else if (typeof window.updateChordInversions === 'function') {
            cursorDebugLog(`Attempting to call updateChordInversions after chord navigation`);
            setTimeout(window.updateChordInversions, 150);
        } else if (typeof enhanceChordDisplay === 'function') {
            cursorDebugLog(`Attempting to call enhanceChordDisplay after chord navigation`);
            setTimeout(enhanceChordDisplay, 150);
        } else {
            cursorDebugLog(`No inversion display enhancement functions found`);
        }
    }
};

// Add legacy function names for backward compatibility
window.leftCursorClick = window.fpfLeftCursorClick;
window.rightCursorClick = window.fpfRightCursorClick;

// ---- INITIALIZATION ----

/**
 * Initialize the cursor system
 */
function initCursorSystem() {
    const state = window.fpf.cursor;
    
    if (state.initialized) {
        cursorDebugLog(`Cursor system already initialized, skipping`);
        return; // Already initialized
    }
    
    cursorDebugLog(`Initializing cursor system...`);
    
    // Create cursor elements if they don't exist
    ensureCursorElements();
    
    // Detect mode from URL
    const url = window.location.href.toLowerCase();
    if (url.includes('chord')) {
        state.mode = 'chords';
        cursorDebugLog(`Mode detection: 'chords' detected from URL`);
        
        // For chord mode, detect chord type
        // First check if unified controller is available
        if (typeof window.chordFretboardController !== 'undefined') {
            cursorDebugLog(`Chord controller: Unified controller detected`);
            
            // Get chord type from controller
            const controller = window.chordFretboardController;
            if (controller && controller.chordState) {
                state.chordType = controller.chordState.chordType || 'triad';
                cursorDebugLog(`Chord controller: Using chord type from controller: ${state.chordType}`);
                
                // Set initial inversion based on controller's current position
                const currentPos = controller.chordState.currentPosition || 'Root Position';
                state.inversion = getInversionIndex(currentPos);
                cursorDebugLog(`Chord controller: Set initial inversion to ${state.inversion} from position "${currentPos}"`);
            } else {
                cursorDebugLog(`Chord controller: Found but missing chordState, using defaults`);
            }
        }
        // Fallback to voicing_data if available
        else if (typeof window.voicing_data !== 'undefined') {
            cursorDebugLog(`Chord data: Using legacy voicing_data`);
            
            // Determine chord type (triad vs seventh)
            const chordName = window.voicing_data.chord || '';
            cursorDebugLog(`Chord data: Detected chord name "${chordName}"`);
            
            if (chordName.includes('7') || chordName.includes('Seventh')) {
                state.chordType = 'seventh';
                cursorDebugLog(`Chord data: Detected seventh chord type`);
            } else {
                state.chordType = 'triad';
                cursorDebugLog(`Chord data: Detected triad chord type`);
            }
        } else {
            cursorDebugLog(`Chord data: No data source found, defaulting to triad`);
        }
        
        // Set default max inversion based on chord type
        let theoreticalMaxInversion = (state.chordType === 'triad') ? 2 : 3;
        cursorDebugLog(`Chord setup: Theoretical max inversion from chord type: ${theoreticalMaxInversion}`);
        
        // Get current inversion
        // If there's a position select, read from there first
        const positionSelect = document.getElementById('position_select');
        if (positionSelect && positionSelect.value) {
            state.inversion = getInversionIndex(positionSelect.value);
            cursorDebugLog(`Chord position: Using value from position_select: "${positionSelect.value}" → inversion ${state.inversion}`);
            
            // Use select options to determine actual max inversion
            if (positionSelect.options.length > 0) {
                // Count how many inversion options are available in the UI
                const availableOptions = Array.from(positionSelect.options).map(o => o.value);
                cursorDebugLog(`Available position options:`, availableOptions);
                
                // Find the maximum inversion index from available options
                let uiMaxInversion = 0;
                for (const option of availableOptions) {
                    const invIndex = getInversionIndex(option);
                    if (invIndex > uiMaxInversion) {
                        uiMaxInversion = invIndex;
                    }
                }
                
                cursorDebugLog(`UI-based max inversion: ${uiMaxInversion}`);
                
                // Use the smaller of theoretical or UI-based max
                state.maxInversion = Math.min(uiMaxInversion, theoreticalMaxInversion);
                cursorDebugLog(`Using final maxInversion: ${state.maxInversion} (minimum of theoretical and UI-based)`);
            } else {
                state.maxInversion = theoreticalMaxInversion;
                cursorDebugLog(`No options in select, using theoretical maxInversion: ${state.maxInversion}`);
            }
        } else {
            cursorDebugLog(`Chord position: No position_select element or value found, using theoretical max`);
            state.maxInversion = theoreticalMaxInversion;
        }
        
        // If still default (0), check URL
        if (state.inversion === 0) {
            const urlParams = new URLSearchParams(window.location.search);
            const position = urlParams.get('position_select');
            if (position) {
                state.inversion = getInversionIndex(position);
                cursorDebugLog(`Chord position: Using value from URL param: "${position}" → inversion ${state.inversion}`);
            } else {
                cursorDebugLog(`Chord position: No position in URL, using default inversion 0`);
            }
        }
    } else if (url.includes('scale') || url.includes('arpeggio')) {
        state.mode = 'scales';
        cursorDebugLog(`Mode detection: 'scales' detected from URL`);
        
        // Try to get position from URL
        const urlParams = new URLSearchParams(window.location.search);
        const position = urlParams.get('position');
        if (position !== null) {
            try {
                state.position = parseInt(position) || 0;
                cursorDebugLog(`Scale position: Set from URL parameter to ${state.position}`);
            } catch (e) {
                state.position = 0;
                cursorDebugLog(`Scale position: Error parsing URL parameter, defaulting to 0`);
            }
        } else {
            cursorDebugLog(`Scale position: No URL parameter found, using default 0`);
        }
        
        // Determine max position from UI
        const positionSelect = document.getElementById('position');
        if (positionSelect) {
            state.maxPosition = positionSelect.options.length - 1;
            cursorDebugLog(`Scale max position: Set from select element to ${state.maxPosition}`);
            
            // Debug output all select options
            const options = Array.from(positionSelect.options).map(o => o.value);
            cursorDebugLog(`Available position options:`, options);
        } else {
            // Default to 7 if not found (standard for common scales)
            state.maxPosition = 7;
            cursorDebugLog(`Scale max position: No select element found, defaulting to ${state.maxPosition}`);
        }
    } else {
        cursorDebugLog(`Mode detection: No mode detected in URL, defaulting to scales`);
        state.mode = 'scales';
    }
    
    // Examine critical DOM elements for debugging
    cursorDebugLog(`DOM inspection: Looking for position_select element`);
    const positionSelect = document.getElementById('position_select');
    cursorDebugLog(`DOM inspection: position_select element found: ${positionSelect ? 'yes' : 'no'}`);
    
    cursorDebugLog(`DOM inspection: Looking for chord_type_select element`);
    const chordTypeSelect = document.getElementById('chord_type_select');
    cursorDebugLog(`DOM inspection: chord_type_select element found: ${chordTypeSelect ? 'yes' : 'no'}`);
    
    // Update cursor visibility
    updateCursorVisibility();
    
    // Mark as initialized
    state.initialized = true;
    cursorDebugLog(`Cursor system initialization complete. Mode: ${state.mode}`);
    cursorDebugLog(`Final state:`, JSON.parse(JSON.stringify(state)));
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize after a short delay to allow other scripts to load
    setTimeout(initCursorSystem, 300);
    
    // Also initialize after a longer delay to handle late-loading elements
    setTimeout(initCursorSystem, 1000);
    
    // Add another initialization attempt after 3 seconds
    setTimeout(initCursorSystem, 3000);
    
    // Set window globals for debugging
    window.debugCursorSystem = function() {
        return {
            state: window.fpf.cursor,
            leftCursor: document.querySelector('.left-cursor'),
            rightCursor: document.querySelector('.right-cursor')
        };
    };
    
    // Expose a function to manually create cursor elements
    window.forceCursorCreation = ensureCursorElements;
});

// Re-export functions for backward compatibility
window.updateCursorVisibility = updateCursorVisibility;
window.getPositionName = getPositionName;
window.getInversionIndex = getInversionIndex;
window.getAvailablePositions = getAvailablePositions;

// URL parameter handling for position_select
const URL_PARAM = 'position_select';

function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

function updateUrlParameter(value) {
    const url = new URL(window.location);
    if (value) {
        url.searchParams.set(URL_PARAM, value);
    } else {
        url.searchParams.delete(URL_PARAM);
    }
    // Use replaceState to avoid polluting browser history excessively
    // Use pushState if you want distinct history entries for each click
    window.history.replaceState({ path: url.toString() }, '', url.toString());
}

function initializeStateFromUrl() {
    const paramValue = getUrlParameter(URL_PARAM);
    cursorDebugLog(`Initializing state from URL parameter '${URL_PARAM}': ${paramValue}`);

    // Determine initial mode - THIS IS CRUCIAL
    // You MUST have logic here or elsewhere to set `currentMode` correctly
    // before this function runs. Example placeholder:
    // currentMode = determineCurrentModeFromPage();

    if (!currentMode) {
        cursorDebugLog("Current mode not set during initialization!");
        // Set a default or leave state as is?
    }

    if (paramValue) {
        if (currentMode === 'scale' || currentMode === 'arpeggio') {
            const pos = scaleUrlMap[paramValue];
            if (pos !== undefined && pos >= 0 && pos <= MAX_SCALE_POS) {
                scalePosition = pos;
            } else {
                cursorDebugLog(`Invalid scale position value '${paramValue}' in URL. Defaulting to 'all'.`);
                scalePosition = 0;
            }
        } else if (currentMode === 'chord') {
            const inv = chordUrlMap[paramValue];
            const maxInv = getMaxChordInversions(); // Need to potentially get chord data first?
            if (inv !== undefined && inv >= 0 && inv <= maxInv) {
                chordInversion = inv;
            } else {
                cursorDebugLog(`Invalid chord inversion value '${paramValue}' in URL. Defaulting to 'Root'.`);
                chordInversion = 0;
            }
        }
    } else {
        // No parameter, default to initial states
        if (currentMode === 'scale' || currentMode === 'arpeggio') {
             scalePosition = 0;
        } else if (currentMode === 'chord') {
             chordInversion = 0;
        }
    }

    // Update display based on initial state
    updateDisplay();
}

function updateDisplay() {
    if (currentMode === 'scale' || currentMode === 'arpeggio') {
        updateScaleArpeggioView();
    } else if (currentMode === 'chord') {
        updateChordView();
    } else {
         // If mode is unknown or not set, clear the parameter
         updateUrlParameter(null);
    }
}

function updateScaleArpeggioView() {
    cursorDebugLog(`Scale/Arpeggio: Fetching position ${scalePosition}`);
    getTonesFromDataScales(scalePosition); // Pass 0 for 'all', 1-6 for positions
    updateCursorVisibility();
    updateUrlParameter(scalePosMap[scalePosition]);
}

function updateChordView() {
    cursorDebugLog(`Chord: Fetching inversion ${chordInversion}`);
    getTonesFromDataChords(chordInversion);
    updateCursorVisibility();
    // Ensure the inversion exists in the map before setting URL
    const maxInv = getMaxChordInversions();
    if (chordInversion <= maxInv && chordInvMap[chordInversion]) {
        updateUrlParameter(chordInvMap[chordInversion]);
    } else {
        cursorDebugLog(`Inversion ${chordInversion} not found in map or exceeds max ${maxInv}`);
        updateUrlParameter(chordInvMap[0]); // Default to Root if invalid
    }

}

function updateCursorVisibility() {
    // ... existing code ...
}

// ... existing code ...

// Example: Allow other scripts to set the mode and initialize state
window.setCursorMode = (mode) => {
    currentMode = mode;
    // Reset state when mode changes and initialize from URL (or default)
    initializeStateFromUrl();
    cursorDebugLog(`Cursor mode set to: ${currentMode}`);
};

// Example: Function to reset cursor state explicitly, e.g., after a new search
window.resetCursorState = (mode, initialData = null) => {
    cursorDebugLog(`Resetting cursor state for mode: ${mode}`);
    currentMode = mode;
    window.currentSearchData = initialData; // Store data if needed for isFourNoteChord

    // Reset internal state variables FIRST
    if (mode === 'scale' || mode === 'arpeggio') {
        scalePosition = 0; // Default to 'all'
    } else if (mode === 'chord') {
        chordInversion = 0; // Default to 'root'
    } else {
         scalePosition = 0;
         chordInversion = 0;
    }

    // Update display and URL (which will use the reset internal state)
    updateDisplay();

    // Note: initializeStateFromUrl() might be better if you want the URL to dictate
    // the state even after a reset, but typically a reset implies going to default.
};

// Expose initialization function if needed externally
window.initializeCursorStateFromUrl = initializeStateFromUrl;
