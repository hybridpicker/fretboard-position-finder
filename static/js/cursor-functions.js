/**
 * Cursor Navigation Functions for Fretboard Position Finder
 * 
 * These functions handle the cursor navigation for both modes:
 * - 'scales': Position navigation for scales and arpeggios
 * - 'chords': Inversion navigation for chords
 */

// Global state for cursor navigation
window.currentMode = window.currentMode || 'scales'; // Set default mode if not defined
window.currentScalePosition = window.currentScalePosition || 0; // Start at "All Positions" for scales
window.maxScalePosition = window.maxScalePosition || 5; // Default max position
window.currentChordType = window.currentChordType || 'triad'; // Default to triads
window.currentInversion = window.currentInversion || 0; // Start at root position / basic position

/**
 * Handles the navigation when the left cursor is clicked
 * Decrements position for scales or inversion for chords based on current mode
 */
function leftCursorClick() {
    console.log("leftCursorClick - Current State:", {
        currentMode: window.currentMode, 
        currentScalePosition: window.currentScalePosition,
        maxScalePosition: window.maxScalePosition,
        currentChordType: window.currentChordType,
        currentInversion: window.currentInversion
    });

    if (window.currentMode === 'scales') {
        // Scales & Arpeggios Logic
        if (window.currentScalePosition > 0) {
            window.currentScalePosition--;
            console.log(`Scale position decremented to ${window.currentScalePosition}`);
        } else {
            console.log("Already at minimum scale position 0, no change");
        }
    } else if (window.currentMode === 'chords') {
        // Chords Logic
        const maxInversion = (window.currentChordType === 'triad') ? 2 : 3;
        
        window.currentInversion--;
        if (window.currentInversion < 0) {
            window.currentInversion = maxInversion; // Wrap around to max inversion
            console.log(`Chord inversion wrapped from 0 to max ${maxInversion}`);
        } else {
            console.log(`Chord inversion decremented to ${window.currentInversion}`);
        }
    } else {
        console.warn(`Unknown mode '${window.currentMode}', no action taken`);
        return;
    }

    // Update UI after state change
    updateDisplay();
    updateCursorVisibility();
}

/**
 * Handles the navigation when the right cursor is clicked
 * Increments position for scales or inversion for chords based on current mode
 */
function rightCursorClick() {
    console.log("rightCursorClick - Current State:", {
        currentMode: window.currentMode, 
        currentScalePosition: window.currentScalePosition,
        maxScalePosition: window.maxScalePosition,
        currentChordType: window.currentChordType,
        currentInversion: window.currentInversion
    });

    if (window.currentMode === 'scales') {
        // Scales & Arpeggios Logic
        if (window.currentScalePosition < window.maxScalePosition) {
            window.currentScalePosition++;
            console.log(`Scale position incremented to ${window.currentScalePosition}`);
        } else {
            console.log(`Already at maximum scale position ${window.maxScalePosition}, no change`);
        }
    } else if (window.currentMode === 'chords') {
        // Chords Logic
        const maxInversion = (window.currentChordType === 'triad') ? 2 : 3;
        
        window.currentInversion++;
        if (window.currentInversion > maxInversion) {
            window.currentInversion = 0; // Wrap around to 0
            console.log(`Chord inversion wrapped from max ${maxInversion} to 0`);
        } else {
            console.log(`Chord inversion incremented to ${window.currentInversion}`);
        }
    } else {
        console.warn(`Unknown mode '${window.currentMode}', no action taken`);
        return;
    }

    // Update UI after state change
    updateDisplay();
    updateCursorVisibility();
}

/**
 * Updates the UI to display the current state
 * Shows the human-readable position or inversion in the appropriate display element
 */
function updateDisplay() {
    console.log("updateDisplay - Updating display based on current state");
    
    // Find display element if not already assigned
    const displayElement = document.getElementById('position_select');
    if (!displayElement) {
        console.error("updateDisplay: Display element not found!");
        return;
    }

    if (window.currentMode === 'scales') {
        // Display scale position in select element
        try {
            // Convert position to string since option values are strings
            const positionValue = String(window.currentScalePosition);
            
            // Find matching option in select element
            let found = false;
            for (let i = 0; i < displayElement.options.length; i++) {
                if (displayElement.options[i].value === positionValue) {
                    displayElement.selectedIndex = i;
                    found = true;
                    break;
                }
            }
            
            if (!found) {
                console.warn(`No option found for scale position ${positionValue}`);
            }
            
            // Update the displayed position text if separate display element exists
            const positionDisplay = document.querySelector('.position-value');
            if (positionDisplay) {
                positionDisplay.textContent = window.currentScalePosition === 0 
                    ? "All Positions" 
                    : `Position ${window.currentScalePosition}`;
            }
            
            // Update fretboard display for the new position
            if (typeof getTonesFromDataScales === 'function') {
                getTonesFromDataScales(positionValue);
            } else {
                console.warn("getTonesFromDataScales function not found!");
            }
            
        } catch (error) {
            console.error("Error updating scale position display:", error);
        }
    } else if (window.currentMode === 'chords') {
        // Display chord inversion in select element
        try {
            // Map inversion number to position name
            let positionName;
            switch (window.currentInversion) {
                case 0:
                    positionName = "Root Position"; // or "Basic Position"
                    break;
                case 1:
                    positionName = "1st Inversion";
                    break;
                case 2:
                    positionName = "2nd Inversion";
                    break;
                case 3:
                    positionName = "3rd Inversion";
                    break;
                default:
                    positionName = "Root Position"; // Default
            }
            
            // Find matching option in select element
            let found = false;
            for (let i = 0; i < displayElement.options.length; i++) {
                if (displayElement.options[i].value === positionName) {
                    displayElement.selectedIndex = i;
                    found = true;
                    break;
                }
            }
            
            if (!found) {
                // Try with "Basic Position" if "Root Position" wasn't found
                if (positionName === "Root Position") {
                    for (let i = 0; i < displayElement.options.length; i++) {
                        if (displayElement.options[i].value === "Basic Position") {
                            displayElement.selectedIndex = i;
                            found = true;
                            break;
                        }
                    }
                }
                
                if (!found) {
                    console.warn(`No option found for chord position ${positionName}`);
                }
            }
            
            // Update the displayed position text if separate display element exists
            const positionDisplay = document.querySelector('.position-value');
            if (positionDisplay) {
                positionDisplay.textContent = positionName;
            }
            
            // Update chord diagram for the new inversion
            if (typeof getTonesFromDataChords === 'function') {
                // Get current range
                const urlParams = new URLSearchParams(window.location.search);
                const currentRange = urlParams.get('note_range') || 
                    (document.getElementById('note_range') ? document.getElementById('note_range').value : 'e - g');
                
                getTonesFromDataChords(positionName, currentRange);
            } else {
                console.warn("getTonesFromDataChords function not found!");
            }
            
        } catch (error) {
            console.error("Error updating chord inversion display:", error);
        }
    } else {
        console.warn(`Unknown mode '${window.currentMode}', cannot update display`);
    }
}

/**
 * Updates the visibility of cursor elements based on current state
 * Hides cursors when at min/max positions to prevent invalid navigation
 */
function updateCursorVisibility() {
    console.log("updateCursorVisibility - Updating cursor visibility");
    
    // Find cursor elements
    const leftCursor = document.querySelector('.left-cursor');
    const rightCursor = document.querySelector('.right-cursor');
    
    if (!leftCursor || !rightCursor) {
        console.warn("Cursor elements not found, cannot update visibility");
        return;
    }
    
    if (window.currentMode === 'scales') {
        // For scales: Hide left at 0, hide right at maxScalePosition
        const hideLeft = window.currentScalePosition <= 0;
        const hideRight = window.currentScalePosition >= window.maxScalePosition;
        
        leftCursor.style.visibility = hideLeft ? 'hidden' : 'visible';
        rightCursor.style.visibility = hideRight ? 'hidden' : 'visible';
        
        console.log(`Scale cursor visibility: left=${!hideLeft}, right=${!hideRight}`);
    } else if (window.currentMode === 'chords') {
        // For chords: Only hide at extremes if not wrapping
        const maxInversion = (window.currentChordType === 'triad') ? 2 : 3;
        
        // In the chord inversion case, we allow wrapping, so technically
        // both cursors should always be visible. But following the requirements:
        const hideLeft = window.currentInversion <= 0;
        const hideRight = window.currentInversion >= maxInversion;
        
        leftCursor.style.visibility = hideLeft ? 'hidden' : 'visible';
        rightCursor.style.visibility = hideRight ? 'hidden' : 'visible';
        
        console.log(`Chord cursor visibility: left=${!hideLeft}, right=${!hideRight}`);
    } else {
        console.warn(`Unknown mode '${window.currentMode}', hiding cursors`);
        leftCursor.style.visibility = 'hidden';
        rightCursor.style.visibility = 'hidden';
    }
}

// Initialize the cursor system when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("Cursor functions loaded, initializing...");
    
    // Detect current mode from URL or page content
    if (window.location.href.toLowerCase().includes('chord')) {
        window.currentMode = 'chords';
    } else if (window.location.href.toLowerCase().includes('scale') || 
               window.location.href.toLowerCase().includes('arpeggio')) {
        window.currentMode = 'scales';
    }
    
    // Get max scale position from select options
    const positionSelect = document.getElementById('position_select');
    if (positionSelect) {
        let maxPos = 0;
        for (let i = 0; i < positionSelect.options.length; i++) {
            const val = parseInt(positionSelect.options[i].value);
            if (!isNaN(val) && val !== 0 && val > maxPos) {
                maxPos = val;
            }
        }
        if (maxPos > 0) {
            window.maxScalePosition = maxPos;
        }
    }
    
    // Get current position/inversion from URL
    const urlParams = new URLSearchParams(window.location.search);
    if (window.currentMode === 'scales') {
        const posVal = urlParams.get('position_select');
        if (posVal !== null) {
            window.currentScalePosition = parseInt(posVal) || 0;
        }
    } else if (window.currentMode === 'chords') {
        const posVal = urlParams.get('position_select');
        if (posVal) {
            // Convert position name to inversion number
            if (posVal === 'Root Position' || posVal === 'Basic Position') {
                window.currentInversion = 0;
            } else if (posVal === '1st Inversion' || posVal === 'First Inversion') {
                window.currentInversion = 1;
            } else if (posVal === '2nd Inversion' || posVal === 'Second Inversion') {
                window.currentInversion = 2;
            } else if (posVal === '3rd Inversion' || posVal === 'Third Inversion') {
                window.currentInversion = 3;
            }
        }
        
        // Determine if we're dealing with a triad or four-note chord
        // This might be based on chord type in URL or other data
        const chordTypeParam = urlParams.get('chords_options_select');
        if (chordTypeParam && (
            chordTypeParam.includes('7') || 
            chordTypeParam.includes('9') || 
            chordTypeParam.includes('11') || 
            chordTypeParam.includes('13')
        )) {
            window.currentChordType = 'fourNote';
        } else {
            window.currentChordType = 'triad';
        }
    }
    
    // Set up event listeners for the cursor elements
    const leftCursor = document.querySelector('.left-cursor');
    const rightCursor = document.querySelector('.right-cursor');
    
    if (leftCursor) {
        leftCursor.addEventListener('click', leftCursorClick);
        console.log("Left cursor click handler attached");
    }
    
    if (rightCursor) {
        rightCursor.addEventListener('click', rightCursorClick);
        console.log("Right cursor click handler attached");
    }
    
    // Initial UI update
    updateDisplay();
    updateCursorVisibility();
    
    console.log("Cursor functions initialization complete");
});
