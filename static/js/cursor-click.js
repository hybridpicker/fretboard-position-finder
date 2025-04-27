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
    maxPosition: 6,       // Maximum scale position - default to 6 (will be updated dynamically)
    chordType: 'triad',   // 'triad' or 'fourNote'
    inversion: 0,         // Current chord inversion (0 = Root Position)
    initialized: false    // Flag to prevent multiple initializations
};

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
 * Detect maximum position number from DOM or scale_data
 * @return {number} The maximum position number (>= 5)
 */
function detectMaxPosition() {
    let maxPosition = 6; // Default minimum value
    
    // Try to get from position select element first
    const positionSelect = document.getElementById('position_select');
    if (positionSelect) {
        for (let i = 0; i < positionSelect.options.length; i++) {
            const value = positionSelect.options[i].value;
            const numValue = parseInt(value);
            
            // Only consider numeric options (not "All Positions" or text values)
            if (!isNaN(numValue) && numValue > maxPosition) {
                maxPosition = numValue;
            }
        }
    }
    
    // Try to get from scale_data if available
    if (typeof scale_data !== 'undefined' && scale_data) {
        // Look for highest numeric position key
        const positions = Object.keys(scale_data)
            .map(key => parseInt(key))
            .filter(num => !isNaN(num) && num > 0);
            
        if (positions.length > 0) {
            const dataMax = Math.max(...positions);
            if (dataMax > maxPosition) {
                maxPosition = dataMax;
            }
        }
    }
    
    console.log("Detected maximum position:", maxPosition);
    return maxPosition;
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
    console.log("updateChordDisplay - Updating to inversion:", inversionValue, "position:", positionName);
    
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
                console.log("Found matching option:", optionValue, "at index:", i);
                break;
            }
        }
        
        if (!foundMatchingOption) {
            console.warn("No matching option found for position:", positionName);
            console.log("Available options:", Array.from(positionSelect.options).map(o => o.value));
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
    
    // Default if all else fails
    if (!range) {
        range = 'e - g';
    }
    
    console.log("Using range:", range);
    
    // Most important: Call the getTonesFromDataChords function to update the fretboard
    if (typeof getTonesFromDataChords === 'function') {
        console.log("Calling getTonesFromDataChords with position:", positionName, "range:", range);
        try {
            getTonesFromDataChords(positionName, range);
        } catch (err) {
            console.error("Error in getTonesFromDataChords:", err);
            
            // Try alternate case
            if (positionName === 'Root Position') {
                console.log("Retrying with 'Basic Position'");
                try {
                    getTonesFromDataChords('Basic Position', range);
                } catch (err2) {
                    console.error("Error in retry attempt:", err2);
                }
            }
        }
    } else {
        console.error("getTonesFromDataChords function not found. Chord inversion cannot be updated.");
    }
    
    // Try to trigger any additional display updates
    if (typeof refreshChordDisplay === 'function') {
        setTimeout(refreshChordDisplay, 50);
    }
    
    if (typeof updateVoicingsDisplay === 'function') {
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
        
        console.log("Scales cursor visibility - left:", leftCursor.style.visibility, "right:", rightCursor.style.visibility, "maxPosition:", state.maxPosition);
    } else if (state.mode === 'chords') {
        // For chords, we should still hide cursors at extremes (even though they wrap)
        // to match the requirement
        const maxInversion = (state.chordType === 'triad') ? 2 : 3;
        
        leftCursor.style.visibility = (state.inversion <= 0) ? 'hidden' : 'visible';
        leftCursor.style.display = (state.inversion <= 0) ? 'none' : 'block';
        
        rightCursor.style.visibility = (state.inversion >= maxInversion) ? 'hidden' : 'visible';
        rightCursor.style.display = (state.inversion >= maxInversion) ? 'none' : 'block';
        
        console.log("Chords cursor visibility - left:", leftCursor.style.visibility, "right:", rightCursor.style.visibility);
    } else {
        // Unknown mode, hide both cursors
        leftCursor.style.visibility = 'hidden';
        leftCursor.style.display = 'none';
        rightCursor.style.visibility = 'hidden';
        rightCursor.style.display = 'none';
        
        console.warn("Unknown mode, hiding cursors");
    }
}

// ---- MAIN CURSOR CLICK FUNCTIONS ----

/**
 * Left cursor click handler
 * Move to previous position/inversion
 */
window.fpfLeftCursorClick = function() {
    const state = window.fpf.cursor;
    console.log("Left cursor clicked. Current mode:", state.mode);
    
    if (state.mode === 'scales') {
        // For scales: Go back one position, stop at 0
        if (state.position > 0) {
            state.position--;
            console.log("Updating scale position to:", state.position);
            updateScaleDisplay(state.position);
        }
    } else if (state.mode === 'chords') {
        // For chords: Go back one inversion, wrap around to max
        const maxInversion = (state.chordType === 'triad') ? 2 : 3;
        
        state.inversion--;
        if (state.inversion < 0) {
            state.inversion = maxInversion;
        }
        console.log("Updating chord inversion to:", state.inversion);
        updateChordDisplay(state.inversion);
    } else {
        console.warn("Unknown mode, cannot handle left click");
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
            setTimeout(window.forceCorrectInversionDisplay, 150);
        } else if (typeof window.updateChordInversions === 'function') {
            setTimeout(window.updateChordInversions, 150);
        } else if (typeof enhanceChordDisplay === 'function') {
            setTimeout(enhanceChordDisplay, 150);
        }
    }
};

/**
 * Right cursor click handler
 * Move to next position/inversion
 */
window.fpfRightCursorClick = function() {
    const state = window.fpf.cursor;
    console.log("Right cursor clicked. Current mode:", state.mode);
    
    if (state.mode === 'scales') {
        // For scales: Go forward one position, stop at max
        if (state.position < state.maxPosition) {
            state.position++;
            console.log("Updating scale position to:", state.position);
            updateScaleDisplay(state.position);
        }
    } else if (state.mode === 'chords') {
        // For chords: Go forward one inversion, wrap around to 0
        const maxInversion = (state.chordType === 'triad') ? 2 : 3;
        
        state.inversion++;
        if (state.inversion > maxInversion) {
            state.inversion = 0;
        }
        console.log("Updating chord inversion to:", state.inversion);
        updateChordDisplay(state.inversion);
    } else {
        console.warn("Unknown mode, cannot handle right click");
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
            setTimeout(window.forceCorrectInversionDisplay, 150);
        } else if (typeof window.updateChordInversions === 'function') {
            setTimeout(window.updateChordInversions, 150);
        } else if (typeof enhanceChordDisplay === 'function') {
            setTimeout(enhanceChordDisplay, 150);
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
        return; // Already initialized
    }
    
    console.log("Initializing cursor system...");
    
    // Create cursor elements if they don't exist
    ensureCursorElements();
    
    // Detect mode from URL
    const url = window.location.href.toLowerCase();
    if (url.includes('chord')) {
        state.mode = 'chords';
        console.log("Detected chord mode");
    } else if (url.includes('scale') || url.includes('arpeggio')) {
        state.mode = 'scales';
        console.log("Detected scale/arpeggio mode");
    } else {
        // Try to detect from page content
        const scaleElements = document.querySelectorAll(
            '.scale-name, .scale-root, .arpeggio-name, .arpeggio-root'
        );
        const chordElements = document.querySelectorAll(
            '.chord-name, .chord-root, .chord-type'
        );
        
        if (scaleElements.length > chordElements.length) {
            state.mode = 'scales';
            console.log("Detected scale/arpeggio mode from DOM elements");
        } else {
            // Default to chords
            state.mode = 'chords';
            console.log("Defaulting to chord mode");
        }
    }
    
    // Check for voicing_data to confirm if we're in chord mode
    if (typeof voicing_data !== 'undefined') {
        state.mode = 'chords';
        console.log("Detected chord mode from presence of voicing_data");
    }
    
    // Check for scale_data to confirm if we're in scale mode
    if (typeof scale_data !== 'undefined') {
        state.mode = 'scales';
        console.log("Detected scale mode from presence of scale_data");
    }
    
    // Get current position from URL
    const urlParams = new URLSearchParams(window.location.search);
    const positionParam = urlParams.get('position_select');
    
    if (state.mode === 'scales') {
        // For scales: Try to parse position as number
        if (positionParam !== null && !isNaN(parseInt(positionParam))) {
            state.position = parseInt(positionParam);
        }
        
        // Detect maximum position dynamically
        state.maxPosition = detectMaxPosition();
        
        console.log("Scale system initialized with position:", state.position, "max:", state.maxPosition);
    } else if (state.mode === 'chords') {
        // For chords: Get inversion from position name
        if (positionParam) {
            state.inversion = getInversionIndex(positionParam);
        }
        
        // Determine chord type
        const chordTypeParam = getChordType();
        state.chordType = isFourNoteChord(chordTypeParam) ? 'fourNote' : 'triad';
        
        console.log("Chord system initialized with inversion:", state.inversion, "type:", state.chordType);
    }
    
    // Set up keyboard navigation
    document.addEventListener('keydown', function(event) {
        if (event.key === 'ArrowLeft') {
            event.preventDefault();
            window.fpfLeftCursorClick();
        } else if (event.key === 'ArrowRight') {
            event.preventDefault();
            window.fpfRightCursorClick();
        }
    });
    
    // Set up cursor click handlers using delegation
    document.body.addEventListener('click', function(event) {
        const leftCursor = event.target.closest('.left-cursor');
        const rightCursor = event.target.closest('.right-cursor');
        
        if (leftCursor) {
            event.preventDefault();
            event.stopPropagation();
            window.fpfLeftCursorClick();
        } else if (rightCursor) {
            event.preventDefault();
            event.stopPropagation();
            window.fpfRightCursorClick();
        }
    }, true); // Use capture phase
    
    // Mark as initialized
    state.initialized = true;
    
    // Initial UI update
    updateCursorVisibility();
    
    console.log("Cursor system initialization complete");
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
    
    // Expose a function to manually detect and set the maximum position
    window.updateMaxPosition = function() {
        window.fpf.cursor.maxPosition = detectMaxPosition();
        updateCursorVisibility();
        return window.fpf.cursor.maxPosition;
    };
});

// Re-export functions for backward compatibility
window.updateCursorVisibility = updateCursorVisibility;
window.getPositionName = getPositionName;
window.getInversionIndex = getInversionIndex;
window.getAvailablePositions = getAvailablePositions;
