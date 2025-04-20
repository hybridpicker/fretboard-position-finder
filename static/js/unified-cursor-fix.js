/**
 * Unified cursor navigation for both scales and chords - DISABLED
 * This script is currently disabled since we're using cursor-functions.js instead
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Unified cursor navigation fix DISABLED - using cursor-functions.js instead");
    
    // Skip initialization - we're using cursor-functions.js instead
    return;

    // NOTE: The code below is kept for reference but is not executed
    /*
    // Wait a short time to ensure other scripts have initialized
    setTimeout(function() {
        // Override the existing cursor click handlers
        const originalLeftCursorClick = window.leftCursorClick;
        const originalRightCursorClick = window.rightCursorClick;
    */
        
        // Helper function to more accurately determine if we're in chord mode
        function isChordModeActive() {
            // Check URL first - most reliable method
            const urlParams = new URLSearchParams(window.location.search);
            const modelSelect = urlParams.get('models_select');
            
            // models_select=3 is for chords
            if (modelSelect === '3') {
                return true;
            }
            
            // Check if voicing_data is defined AND we have chord data in it
            if (typeof window.voicing_data !== 'undefined' && window.voicing_data !== null) {
                // Check if it has chord range keys
                const hasChordRanges = window.voicing_data && 
                                     Object.keys(window.voicing_data).some(key => 
                                        key.includes(' - ') || 
                                        (typeof window.voicing_data[key] === 'object' && 
                                         Object.keys(window.voicing_data[key]).includes('Basic Position')));
                
                if (hasChordRanges) {
                    return true;
                }
            }
            
            // Check if there's a chord select element which is also reliable
            const chordSelect = document.getElementById('chords_options_select');
            if (chordSelect) {
                return true;
            }
            
            // Check if scale_data exists, which would indicate scale mode
            if (typeof window.scale_data !== 'undefined' && window.scale_data !== null) {
                return false;
            }
            
            // Default to false (scale mode) if we can't determine
            return false;
        }
        
        // Define the improved cursor click handlers
        window.leftCursorClick = function() {
            console.log("Unified cursor fix: Left cursor clicked");
            
            // Determine if we're in chord mode
            const chordMode = isChordModeActive();
            console.log("Unified cursor fix: Chord mode detected:", chordMode);
            
            if (chordMode) {
                console.log("Unified cursor fix: Processing chord inversion (left)");
                
                // Get current inversion
                const positionSelect = document.getElementById('position_select');
                const currentPosition = positionSelect ? positionSelect.value : "Basic Position";
                
                // Get the current range
                const rangeSelect = document.getElementById('note_range');
                const currentRange = rangeSelect ? rangeSelect.value : 'e - d';
                
                // Map position names to standard format
                const positionMap = {
                    "Basic Position": "Basic Position",
                    "Root Position": "Basic Position",
                    "0": "Basic Position",
                    "First Inversion": "First Inversion",
                    "1st Inversion": "First Inversion",
                    "1": "First Inversion",
                    "Second Inversion": "Second Inversion", 
                    "2nd Inversion": "Second Inversion",
                    "2": "Second Inversion",
                    "Third Inversion": "Third Inversion",
                    "3rd Inversion": "Third Inversion",
                    "3": "Third Inversion"
                };
                
                // Standard order for positions
                const standardPositions = ["Basic Position", "First Inversion", "Second Inversion", "Third Inversion"];
                
                // Get the normalized current position
                const normalizedPosition = positionMap[currentPosition] || currentPosition;
                let currentIndex = standardPositions.indexOf(normalizedPosition);
                
                // If not found in standard positions, try to parse as number
                if (currentIndex === -1) {
                    currentIndex = parseInt(currentPosition) || 0;
                }
                
                // Get available positions
                let availablePositions = standardPositions;
                
                // Check if we have voicing data for current range
                if (window.voicing_data && window.voicing_data[currentRange]) {
                    const positionKeys = Object.keys(window.voicing_data[currentRange])
                        .filter(key => typeof window.voicing_data[currentRange][key] === 'object');
                    
                    if (positionKeys.length > 0) {
                        availablePositions = positionKeys;
                    }
                }
                
                // Decrement index with wraparound
                currentIndex = (currentIndex - 1 + availablePositions.length) % availablePositions.length;
                
                // Get the next position
                const nextPosition = availablePositions[currentIndex];
                
                console.log("Unified cursor fix: Moving to chord position", nextPosition);
                
                // Update position select
                if (positionSelect) {
                    let found = false;
                    
                    // First try exact match
                    for (let i = 0; i < positionSelect.options.length; i++) {
                        if (positionSelect.options[i].value === nextPosition) {
                            positionSelect.selectedIndex = i;
                            found = true;
                            break;
                        }
                    }
                    
                    // If not found, try normalized match
                    if (!found) {
                        for (let i = 0; i < positionSelect.options.length; i++) {
                            const normalizedOption = positionMap[positionSelect.options[i].value];
                            if (normalizedOption === nextPosition) {
                                positionSelect.selectedIndex = i;
                                found = true;
                                break;
                            }
                        }
                    }
                    
                    // If still not found, try to set by index
                    if (!found && currentIndex < positionSelect.options.length) {
                        positionSelect.selectedIndex = currentIndex;
                    }
                }
                
                // Update display
                if (typeof window.getToneNameFromDataChords === 'function') {
                    console.log("Unified cursor fix: Calling getToneNameFromDataChords with position:", nextPosition, "range:", currentRange);
                    window.getToneNameFromDataChords(nextPosition, currentRange);
                }
                
                // Update URL
                const urlParams = new URLSearchParams(window.location.search);
                urlParams.set('position_select', nextPosition);
                const newUrl = window.location.pathname + '?' + urlParams.toString();
                window.history.replaceState(null, '', newUrl);
            } else {
                console.log("Unified cursor fix: Processing scale position (left)");
                
                // For scales, use currentScalePosition or parse from select
                let currentPosition = 0;
                
                if (typeof window.currentScalePosition !== 'undefined') {
                    currentPosition = window.currentScalePosition;
                } else {
                    const positionSelect = document.getElementById('position_select');
                    if (positionSelect) {
                        currentPosition = parseInt(positionSelect.value) || 0;
                    }
                }
                
                // Decrement position with a minimum of 0
                if (currentPosition > 0) {
                    currentPosition--;
                }
                
                console.log("Unified cursor fix: New scale position:", currentPosition);
                
                // Update window.currentScalePosition if it exists
                if (typeof window.currentScalePosition !== 'undefined') {
                    window.currentScalePosition = currentPosition;
                }
                
                // Update the form element
                const positionSelect = document.getElementById('position_select');
                if (positionSelect) {
                    positionSelect.value = currentPosition;
                }
                
                // Update scale display
                if (typeof window.getTonesFromDataScales === 'function') {
                    console.log("Unified cursor fix: Calling getTonesFromDataScales with position:", currentPosition);
                    window.getTonesFromDataScales(currentPosition.toString());
                }
                
                // Update URL
                const urlParams = new URLSearchParams(window.location.search);
                urlParams.set('position_select', currentPosition);
                const newUrl = window.location.pathname + '?' + urlParams.toString();
                window.history.replaceState(null, '', newUrl);
            }
            
            // Update cursor visibility
            updateCursorVisibility();
            
            // Prevent further handling
            return false;
        };
        
        window.rightCursorClick = function() {
            console.log("Unified cursor fix: Right cursor clicked");
            
            // Determine if we're in chord mode
            const chordMode = isChordModeActive();
            console.log("Unified cursor fix: Chord mode detected:", chordMode);
            
            if (chordMode) {
                console.log("Unified cursor fix: Processing chord inversion (right)");
                
                // Get current inversion
                const positionSelect = document.getElementById('position_select');
                const currentPosition = positionSelect ? positionSelect.value : "Basic Position";
                
                // Get the current range
                const rangeSelect = document.getElementById('note_range');
                const currentRange = rangeSelect ? rangeSelect.value : 'e - d';
                
                // Map position names to standard format
                const positionMap = {
                    "Basic Position": "Basic Position",
                    "Root Position": "Basic Position",
                    "0": "Basic Position",
                    "First Inversion": "First Inversion",
                    "1st Inversion": "First Inversion",
                    "1": "First Inversion",
                    "Second Inversion": "Second Inversion", 
                    "2nd Inversion": "Second Inversion",
                    "2": "Second Inversion",
                    "Third Inversion": "Third Inversion",
                    "3rd Inversion": "Third Inversion",
                    "3": "Third Inversion"
                };
                
                // Standard order for positions
                const standardPositions = ["Basic Position", "First Inversion", "Second Inversion", "Third Inversion"];
                
                // Get the normalized current position
                const normalizedPosition = positionMap[currentPosition] || currentPosition;
                let currentIndex = standardPositions.indexOf(normalizedPosition);
                
                // If not found in standard positions, try to parse as number
                if (currentIndex === -1) {
                    currentIndex = parseInt(currentPosition) || 0;
                }
                
                // Get available positions
                let availablePositions = standardPositions;
                
                // Check if we have voicing data for current range
                if (window.voicing_data && window.voicing_data[currentRange]) {
                    const positionKeys = Object.keys(window.voicing_data[currentRange])
                        .filter(key => typeof window.voicing_data[currentRange][key] === 'object');
                    
                    if (positionKeys.length > 0) {
                        availablePositions = positionKeys;
                    }
                }
                
                // Increment index with wraparound
                currentIndex = (currentIndex + 1) % availablePositions.length;
                
                // Get the next position
                const nextPosition = availablePositions[currentIndex];
                
                console.log("Unified cursor fix: Moving to chord position", nextPosition);
                
                // Update position select
                if (positionSelect) {
                    let found = false;
                    
                    // First try exact match
                    for (let i = 0; i < positionSelect.options.length; i++) {
                        if (positionSelect.options[i].value === nextPosition) {
                            positionSelect.selectedIndex = i;
                            found = true;
                            break;
                        }
                    }
                    
                    // If not found, try normalized match
                    if (!found) {
                        for (let i = 0; i < positionSelect.options.length; i++) {
                            const normalizedOption = positionMap[positionSelect.options[i].value];
                            if (normalizedOption === nextPosition) {
                                positionSelect.selectedIndex = i;
                                found = true;
                                break;
                            }
                        }
                    }
                    
                    // If still not found, try to set by index
                    if (!found && currentIndex < positionSelect.options.length) {
                        positionSelect.selectedIndex = currentIndex;
                    }
                }
                
                // Update display
                if (typeof window.getToneNameFromDataChords === 'function') {
                    console.log("Unified cursor fix: Calling getToneNameFromDataChords with position:", nextPosition, "range:", currentRange);
                    window.getToneNameFromDataChords(nextPosition, currentRange);
                }
                
                // Update URL
                const urlParams = new URLSearchParams(window.location.search);
                urlParams.set('position_select', nextPosition);
                const newUrl = window.location.pathname + '?' + urlParams.toString();
                window.history.replaceState(null, '', newUrl);
            } else {
                console.log("Unified cursor fix: Processing scale position (right)");
                
                // For scales, use currentScalePosition or parse from select
                let currentPosition = 0;
                let maxPosition = 5;  // Default max position
                
                if (typeof window.currentScalePosition !== 'undefined') {
                    currentPosition = window.currentScalePosition;
                    
                    if (typeof window.maxScalePosition !== 'undefined') {
                        maxPosition = window.maxScalePosition;
                    }
                } else {
                    const positionSelect = document.getElementById('position_select');
                    if (positionSelect) {
                        currentPosition = parseInt(positionSelect.value) || 0;
                        
                        // Try to determine max position from select options
                        if (positionSelect.options.length > 0) {
                            let highestOption = 0;
                            for (let i = 0; i < positionSelect.options.length; i++) {
                                const optionValue = parseInt(positionSelect.options[i].value) || 0;
                                highestOption = Math.max(highestOption, optionValue);
                            }
                            maxPosition = highestOption;
                        }
                    }
                }
                
                // Increment position up to the maximum
                if (currentPosition < maxPosition) {
                    currentPosition++;
                }
                
                console.log("Unified cursor fix: New scale position:", currentPosition);
                
                // Update window.currentScalePosition if it exists
                if (typeof window.currentScalePosition !== 'undefined') {
                    window.currentScalePosition = currentPosition;
                }
                
                // Update the form element
                const positionSelect = document.getElementById('position_select');
                if (positionSelect) {
                    positionSelect.value = currentPosition;
                }
                
                // Update scale display
                if (typeof window.getTonesFromDataScales === 'function') {
                    console.log("Unified cursor fix: Calling getTonesFromDataScales with position:", currentPosition);
                    window.getTonesFromDataScales(currentPosition.toString());
                }
                
                // Update URL
                const urlParams = new URLSearchParams(window.location.search);
                urlParams.set('position_select', currentPosition);
                const newUrl = window.location.pathname + '?' + urlParams.toString();
                window.history.replaceState(null, '', newUrl);
            }
            
            // Update cursor visibility
            updateCursorVisibility();
            
            // Prevent further handling
            return false;
        };
        
        // Helper function to update cursor visibility
        function updateCursorVisibility() {
            const leftCursor = document.querySelector('.left-cursor');
            const rightCursor = document.querySelector('.right-cursor');
            
            if (!leftCursor || !rightCursor) {
                console.warn("Unified cursor fix: Cursor elements not found for visibility update");
                return;
            }
            
            // Determine if we're in chord mode
            const chordMode = isChordModeActive();
            
            if (chordMode) {
                // For chords, use the position select value
                const positionSelect = document.getElementById('position_select');
                const currentPosition = positionSelect ? positionSelect.value : "Basic Position";
                
                // Get the current range
                const rangeSelect = document.getElementById('note_range');
                const currentRange = rangeSelect ? rangeSelect.value : 'e - d';
                
                // Map position names to standard format
                const positionMap = {
                    "Basic Position": "Basic Position",
                    "Root Position": "Basic Position",
                    "0": "Basic Position",
                    "First Inversion": "First Inversion",
                    "1st Inversion": "First Inversion",
                    "1": "First Inversion",
                    "Second Inversion": "Second Inversion", 
                    "2nd Inversion": "Second Inversion",
                    "2": "Second Inversion",
                    "Third Inversion": "Third Inversion",
                    "3rd Inversion": "Third Inversion",
                    "3": "Third Inversion"
                };
                
                // Standard order for positions
                const standardPositions = ["Basic Position", "First Inversion", "Second Inversion", "Third Inversion"];
                
                // Get the normalized current position
                const normalizedPosition = positionMap[currentPosition] || currentPosition;
                let currentIndex = standardPositions.indexOf(normalizedPosition);
                
                // If not found in standard positions, try to parse as number
                if (currentIndex === -1) {
                    currentIndex = parseInt(currentPosition) || 0;
                }
                
                // Get available positions
                let availablePositions = standardPositions;
                
                // If voicing_data is available, use its positions
                if (window.voicing_data && window.voicing_data[currentRange]) {
                    const positionKeys = Object.keys(window.voicing_data[currentRange])
                        .filter(key => typeof window.voicing_data[currentRange][key] === 'object');
                    
                    if (positionKeys.length > 0) {
                        availablePositions = positionKeys;
                        currentIndex = positionKeys.indexOf(normalizedPosition);
                        if (currentIndex === -1) {
                            // Try to find a match using the positionMap
                            for (let i = 0; i < positionKeys.length; i++) {
                                if (positionMap[positionKeys[i]] === normalizedPosition) {
                                    currentIndex = i;
                                    break;
                                }
                            }
                        }
                    }
                }
                
                // Ensure currentIndex is valid
                if (currentIndex === -1) {
                    currentIndex = 0;
                }
                
                // Hide left cursor at first position
                leftCursor.style.visibility = (currentIndex <= 0) ? 'hidden' : 'visible';
                
                // Hide right cursor at last position
                rightCursor.style.visibility = (currentIndex >= availablePositions.length - 1) ? 'hidden' : 'visible';
            } else {
                // For scales, use currentScalePosition or position_select
                let currentPosition = 0;
                let maxPosition = 5;  // Default max position
                
                if (typeof window.currentScalePosition !== 'undefined') {
                    currentPosition = window.currentScalePosition;
                    
                    if (typeof window.maxScalePosition !== 'undefined') {
                        maxPosition = window.maxScalePosition;
                    }
                } else {
                    const positionSelect = document.getElementById('position_select');
                    if (positionSelect) {
                        currentPosition = parseInt(positionSelect.value) || 0;
                        
                        // Try to determine max position from select options
                        if (positionSelect.options.length > 0) {
                            let highestOption = 0;
                            for (let i = 0; i < positionSelect.options.length; i++) {
                                const optionValue = parseInt(positionSelect.options[i].value) || 0;
                                highestOption = Math.max(highestOption, optionValue);
                            }
                            maxPosition = highestOption;
                        }
                    }
                }
                
                // Hide left cursor at position 0
                leftCursor.style.visibility = (currentPosition <= 0) ? 'hidden' : 'visible';
                
                // Hide right cursor at max position
                rightCursor.style.visibility = (currentPosition >= maxPosition) ? 'hidden' : 'visible';
            }
        }
        
        // Make updateCursorVisibility globally available
        window.updateUnifiedCursorVisibility = updateCursorVisibility;
        
        console.log("Unified cursor navigation fix would have been loaded");
        
        // Initial visibility update
        //setTimeout(updateCursorVisibility, 1000);
        
    }, 1000); // This code is not executed since we return above
    */
});
