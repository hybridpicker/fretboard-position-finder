/**
 * Fixed Cursor Navigation Functions for Fretboard Position Finder
 * 
 * These functions handle cursor navigation for both modes:
 * - 'scales': Position navigation for scales and arpeggios
 * - 'chords': Inversion navigation for chords
 */

// Initialize global state values if needed
window.currentMode = window.currentMode || (window.location.href.toLowerCase().includes('chord') ? 'chords' : 'scales');
window.currentScalePosition = 0; // Default to "All Positions" for scales
window.maxScalePosition = 5; // Default, will be updated from DOM
window.currentChordType = 'triad'; // Default, will be updated from URL if needed
window.currentInversion = 0; // Default to Root Position

// DOM loaded initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log("Fixed cursor navigation loaded, initializing...");
    
    // Initialize state based on URL and DOM
    initializeState();
    
    // Setup cursor event handlers
    setupCursorEventHandlers();
    
    // Initial UI updates
    if (window.currentMode === 'scales') {
        updateScaleDisplay();
    } else if (window.currentMode === 'chords') {
        updateChordDisplay();
    }
    updateCursorVisibility();
    
    console.log("Cursor navigation initialized with state:", {
        currentMode: window.currentMode,
        currentScalePosition: window.currentScalePosition,
        maxScalePosition: window.maxScalePosition,
        currentChordType: window.currentChordType,
        currentInversion: window.currentInversion
    });
});

/**
 * Initialize global state based on URL parameters and DOM elements
 */
function initializeState() {
    // Determine current mode from URL (already set above but recheck)
    if (window.location.href.toLowerCase().includes('chord')) {
        window.currentMode = 'chords';
    } else {
        window.currentMode = 'scales';
    }
    
    // Get URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    
    // Initialize state for scales mode
    if (window.currentMode === 'scales') {
        // Get current position from URL
        const posParam = urlParams.get('position_select');
        if (posParam !== null) {
            window.currentScalePosition = parseInt(posParam);
            if (isNaN(window.currentScalePosition)) {
                window.currentScalePosition = 0; // Default to All Positions
            }
        }
        
        // Get max position from select element
        const posSelect = document.getElementById('position_select');
        if (posSelect) {
            let maxPos = 0;
            for (let i = 0; i < posSelect.options.length; i++) {
                const val = parseInt(posSelect.options[i].value);
                if (!isNaN(val) && val !== 0 && val > maxPos) {
                    maxPos = val;
                }
            }
            if (maxPos > 0) {
                window.maxScalePosition = maxPos;
            }
        }
    }
    // Initialize state for chords mode
    else if (window.currentMode === 'chords') {
        // Get position/inversion from URL
        const posParam = urlParams.get('position_select');
        if (posParam) {
            if (posParam === 'Root Position' || posParam === 'Basic Position') {
                window.currentInversion = 0;
            } else if (posParam.includes('1st') || posParam.includes('First')) {
                window.currentInversion = 1;
            } else if (posParam.includes('2nd') || posParam.includes('Second')) {
                window.currentInversion = 2;
            } else if (posParam.includes('3rd') || posParam.includes('Third')) {
                window.currentInversion = 3;
            }
        }
        
        // Determine chord type (triad or fourNote)
        const chordParam = urlParams.get('chords_options_select');
        if (chordParam && (
            chordParam.includes('7') || 
            chordParam.includes('9') || 
            chordParam.includes('11') || 
            chordParam.includes('13')
        )) {
            window.currentChordType = 'fourNote';
        }
    }
}

/**
 * Set up click event handlers for cursor elements
 */
function setupCursorEventHandlers() {
    // Remove any existing inline click handlers
    const leftCursor = document.querySelector('.left-cursor');
    const rightCursor = document.querySelector('.right-cursor');
    
    if (leftCursor) {
        if (leftCursor.hasAttribute('onclick')) {
            leftCursor.removeAttribute('onclick');
        }
        leftCursor.addEventListener('click', leftCursorClick);
    }
    
    if (rightCursor) {
        if (rightCursor.hasAttribute('onclick')) {
            rightCursor.removeAttribute('onclick');
        }
        rightCursor.addEventListener('click', rightCursorClick);
    }
}

/**
 * Left cursor click handler
 * Decrements position or inversion based on mode
 */
function leftCursorClick() {
    console.log("leftCursorClick called - Mode:", window.currentMode);
    
    if (window.currentMode === 'scales') {
        // Scales logic - decrement position, don't go below 0
        if (window.currentScalePosition > 0) {
            window.currentScalePosition--;
            updateScaleDisplay();
            updateCursorVisibility();
        }
    } else if (window.currentMode === 'chords') {
        // Chords logic - decrement inversion with wrap-around
        const maxInversion = (window.currentChordType === 'triad') ? 2 : 3;
        
        window.currentInversion--;
        if (window.currentInversion < 0) {
            window.currentInversion = maxInversion;
        }
        
        updateChordDisplay();
        updateCursorVisibility();
    }
}

/**
 * Right cursor click handler
 * Increments position or inversion based on mode
 */
function rightCursorClick() {
    console.log("rightCursorClick called - Mode:", window.currentMode);
    
    if (window.currentMode === 'scales') {
        // Check if we're at the maximum position
        if (window.currentScalePosition < window.maxScalePosition) {
            window.currentScalePosition++;
            updateScaleDisplay();
            updateCursorVisibility();
        }
    } else if (window.currentMode === 'chords') {
        // Chords logic - increment inversion with wrap-around
        const maxInversion = (window.currentChordType === 'triad') ? 2 : 3;
        
        window.currentInversion++;
        if (window.currentInversion > maxInversion) {
            window.currentInversion = 0;
        }
        
        updateChordDisplay();
        updateCursorVisibility();
    }
}

/**
 * Update the display for scale positions
 * This directly updates the fretboard without page reload
 */
function updateScaleDisplay() {
    console.log(`updateScaleDisplay - Setting position to ${window.currentScalePosition}`);
    
    // Update select element
    const positionSelect = document.getElementById('position_select');
    if (positionSelect) {
        positionSelect.value = String(window.currentScalePosition);
        
        // Also update the display text for any custom select elements
        const displayDiv = document.querySelector('.select-selected');
        if (displayDiv) {
            for (let i = 0; i < positionSelect.options.length; i++) {
                if (positionSelect.options[i].value == window.currentScalePosition) {
                    displayDiv.innerHTML = positionSelect.options[i].innerHTML;
                    break;
                }
            }
        }
    }
    
    // Update URL without reloading
    const url = new URL(window.location.href);
    url.searchParams.set('position_select', window.currentScalePosition);
    window.history.replaceState({}, '', url);
    
    // Update fretboard display
    if (typeof getTonesFromDataScales === 'function') {
        getTonesFromDataScales(String(window.currentScalePosition));
    } else {
        console.warn("getTonesFromDataScales function not found");
    }
}

/**
 * Update the display for chord inversions
 * This directly updates the fretboard without page reload
 */
function updateChordDisplay() {
    console.log(`updateChordDisplay - Setting inversion to ${window.currentInversion}`);
    
    // Map inversion number to position name
    let positionName;
    switch (window.currentInversion) {
        case 0: positionName = 'Root Position'; break;
        case 1: positionName = '1st Inversion'; break;
        case 2: positionName = '2nd Inversion'; break;
        case 3: positionName = '3rd Inversion'; break;
        default: positionName = 'Root Position';
    }
    
    // Update select element
    const positionSelect = document.getElementById('position_select');
    if (positionSelect) {
        // Find the correct option value that matches our position name
        let found = false;
        for (let i = 0; i < positionSelect.options.length; i++) {
            const optionValue = positionSelect.options[i].value;
            // Match various position name formats
            if (
                (window.currentInversion === 0 && (optionValue === 'Root Position' || optionValue === 'Basic Position')) ||
                (window.currentInversion === 1 && (optionValue === '1st Inversion' || optionValue === 'First Inversion')) ||
                (window.currentInversion === 2 && (optionValue === '2nd Inversion' || optionValue === 'Second Inversion')) ||
                (window.currentInversion === 3 && (optionValue === '3rd Inversion' || optionValue === 'Third Inversion'))
            ) {
                positionSelect.selectedIndex = i;
                positionName = optionValue; // Use the actual option value
                found = true;
                break;
            }
        }
        
        // Update the display text for any custom select elements
        const displayDiv = document.querySelector('.select-selected');
        if (displayDiv && found) {
            displayDiv.innerHTML = positionSelect.options[positionSelect.selectedIndex].innerHTML;
        }
    }
    
    // Update URL without reloading
    const url = new URL(window.location.href);
    url.searchParams.set('position_select', positionName);
    window.history.replaceState({}, '', url);
    
    // Get current note range
    const range = new URLSearchParams(window.location.search).get('note_range') || 
                 (document.getElementById('note_range') ? document.getElementById('note_range').value : 'e - g');
    
    // Update chord diagram
    if (typeof getTonesFromDataChords === 'function') {
        getTonesFromDataChords(positionName, range);
    } else {
        console.warn("getTonesFromDataChords function not found");
    }
}

/**
 * Update cursor visibility based on current state
 */
function updateCursorVisibility() {
    const leftCursor = document.querySelector('.left-cursor');
    const rightCursor = document.querySelector('.right-cursor');
    
    if (!leftCursor || !rightCursor) {
        console.warn("Cursor elements not found");
        return;
    }
    
    if (window.currentMode === 'scales') {
        // For scales: hide left at position 0, hide right at max position
        const hideLeft = window.currentScalePosition <= 0;
        const hideRight = window.currentScalePosition >= window.maxScalePosition;
        
        leftCursor.style.visibility = hideLeft ? 'hidden' : 'visible';
        rightCursor.style.visibility = hideRight ? 'hidden' : 'visible';
        
        console.log(`Scale cursor visibility updated: left=${!hideLeft}, right=${!hideRight}`);
    } else if (window.currentMode === 'chords') {
        // For chords: hide left at 0, hide right at max inversion (despite wrap-around)
        const maxInversion = (window.currentChordType === 'triad') ? 2 : 3;
        
        const hideLeft = window.currentInversion <= 0;
        const hideRight = window.currentInversion >= maxInversion;
        
        leftCursor.style.visibility = hideLeft ? 'hidden' : 'visible';
        rightCursor.style.visibility = hideRight ? 'hidden' : 'visible';
        
        console.log(`Chord cursor visibility updated: left=${!hideLeft}, right=${!hideRight}`);
    }
}
