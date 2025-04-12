/**
 * Cursor Fix for Fretboard Chords
 * 
 * This file fixes the issue with leftCursorClick() and rightCursorClick() functions
 * by exposing them globally and ensuring they work as expected.
 * 
 * @author Claude AI
 */

// Make sure these functions are available in the global scope (window object)
window.leftCursorClick = function() {
    console.log("leftCursorClick triggered");
    
    // Get current position and range
    var pos_val = getQueryParam('position_select');
    var note_range = getQueryParam('note_range');
    
    // Get available positions based on chord type
    const chordType = getChordType();
    const positions = getChordPositions(chordType);
    if (!positions || positions.length === 0) {
        console.warn('No positions available for range:', note_range);
        return;
    }
    
    // Find current position index
    const currentIndex = positions.indexOf(pos_val);
    if (currentIndex === -1) {
        console.warn('Current position not found in available positions');
        return;
    }
    
    // Calculate previous position (wrap around to end if at start)
    const prevIndex = currentIndex === 0 ? positions.length - 1 : currentIndex - 1;
    const newPosition = positions[prevIndex];
    
    // Update URL and trigger position change
    updateUrlParam('position_select', newPosition);
    
    // Dispatch custom event for position change
    document.dispatchEvent(new CustomEvent('chord-position-activated', {
        detail: {
            position: newPosition,
            range: note_range,
            direction: 'prev'
        }
    }));
    
    // Call setupInversionDisplay from chord-inversions-fixed.js if available
    if (typeof setupInversionDisplay === 'function') {
        setTimeout(setupInversionDisplay, 100);
    }
    
    // If we have a controller instance, update the chord display
    if (window.chordFretboardController && 
        typeof window.chordFretboardController.updateChordDisplay === 'function') {
        window.chordFretboardController.updateChordDisplay(newPosition, note_range);
    }
    
    // Use getTonesFromDataChords as a fallback if available
    if (typeof getTonesFromDataChords === 'function') {
        getTonesFromDataChords(newPosition, note_range);
    }
};

window.rightCursorClick = function() {
    console.log("rightCursorClick triggered");
    
    // Get current position and range
    var pos_val = getQueryParam('position_select');
    var note_range = getQueryParam('note_range');
    
    // Get available positions based on chord type
    const chordType = getChordType();
    const positions = getChordPositions(chordType);
    if (!positions || positions.length === 0) {
        console.warn('No positions available for chord type:', chordType);
        return;
    }
    
    // Find current position index
    let currentIndex = positions.indexOf(pos_val);
    
    // Calculate next position
    let nextIndex;
    if (currentIndex === -1) {
        console.warn('Current position not found. Defaulting to first position for next calculation.');
        // If current position is invalid, clicking right should go to the *second* position (index 1)
        // or wrap to the first (index 0) if there's only one position.
        nextIndex = positions.length > 1 ? 1 : 0;
    } else {
        nextIndex = currentIndex === positions.length - 1 ? 0 : currentIndex + 1;
    }
    
    // Ensure nextIndex is valid
    if (nextIndex < 0 || nextIndex >= positions.length) {
        console.error("Calculated invalid nextIndex:", nextIndex, "Positions:", positions);
        nextIndex = 0; // Fallback to first index
    }
    
    const newPosition = positions[nextIndex];
    
    // Update URL and trigger position change
    updateUrlParam('position_select', newPosition);
    
    // Dispatch custom event for position change
    document.dispatchEvent(new CustomEvent('chord-position-activated', {
        detail: {
            position: newPosition,
            range: note_range,
            direction: 'next'
        }
    }));
    
    // Call setupInversionDisplay from chord-inversions-fixed.js if available
    if (typeof setupInversionDisplay === 'function') {
        setTimeout(setupInversionDisplay, 100);
    }
    
    // If we have a controller instance, update the chord display
    if (window.chordFretboardController && 
        typeof window.chordFretboardController.updateChordDisplay === 'function') {
        window.chordFretboardController.updateChordDisplay(newPosition, note_range);
    }
    
    // Use getTonesFromDataChords as a fallback if available
    if (typeof getTonesFromDataChords === 'function') {
        getTonesFromDataChords(newPosition, note_range);
    }
};

// Helper functions needed by cursor click functions

// Helper function to get a query parameter from the URL
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// Helper function to get chord type from the URL or select element
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

// Helper function to get available positions based on chord type
function getChordPositions(chordType) {
    // Use available getAvailablePositions function if exists
    if (typeof getAvailablePositions === 'function') {
        return getAvailablePositions();
    }
    
    // Default positions
    let positions = ['Root Position', 'First Inversion', 'Second Inversion'];
    
    // Add third inversion for seventh chords
    if (chordType && (chordType.includes('7') || chordType.includes('9') || 
                      chordType.includes('11') || chordType.includes('13'))) {
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
                .filter(pos => pos && !/^\d+$/.test(pos) && 
                       typeof voicing_data[currentRange][pos] === 'object');
            
            if (dataPositions.length > 0) {
                // Normalize position names for consistency
                return dataPositions.map(pos => {
                    // Map "Basic Position" to "Root Position" for consistency
                    if (pos === 'Basic Position') return 'Root Position';
                    
                    // Handle any variations with "First Root" in them
                    if (pos.includes('First Root') || pos.includes('First Basic')) 
                        return 'Root Position';
                    
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
                        if (pos.includes('First Root') || pos.includes('First Basic')) 
                            return 'Root Position';
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

// Helper function to update URL parameters
function updateUrlParam(param, value) {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set(param, value);
    window.history.replaceState({}, '', `${window.location.pathname}?${urlParams}`);
}

// Initialize cursor handlers when the page is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Cursor-fix.js loaded: Adding global cursor click functions');
    
    // Make sure these functions are exposed to cursor_management.js
    if (typeof ORIGINAL_FUNCTIONS !== 'undefined') {
        ORIGINAL_FUNCTIONS.leftCursorClick = window.leftCursorClick;
        ORIGINAL_FUNCTIONS.rightCursorClick = window.rightCursorClick;
    }
    
    // Reinitialize cursor management if it exists
    if (typeof initCursorManagement === 'function') {
        setTimeout(() => {
            try {
                initCursorManagement('chords');
                console.log('Successfully re-initialized cursor management');
            } catch (e) {
                console.error('Error re-initializing cursor management:', e);
            }
        }, 1000);
    }
});
