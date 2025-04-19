/**
 * Direct Chord Navigation
 * Enhances chord position navigation by directly manipulating the DOM
 */

document.addEventListener('DOMContentLoaded', function() {
    // Override the cursor click functions for direct DOM manipulation
    overrideCursorClickFunctions();
    
    // Keyboard shortcuts are handled by cursor_management.js
});

/**
 * Helper function to determine if the current chord is a triad (3-note chord)
 * This allows us to add specific handling for triads vs. larger chords if needed
 * @returns {boolean} True if the current chord is a triad
 */
function isTriadChord() {
    // Check voicing data to see if it has a fourth note
    if (typeof voicing_data !== 'undefined' && voicing_data) {
        // If we can directly check the chord structure
        if (voicing_data.chord_structure) {
            return !voicing_data.chord_structure.includes('7') && 
                   !voicing_data.chord_structure.includes('9') &&
                   !voicing_data.chord_structure.includes('11') &&
                   !voicing_data.chord_structure.includes('13');
        }
        
        // Check the chord/type for common seventh chord indicators
        if (voicing_data.chord && voicing_data.type) {
            const chordFullName = voicing_data.chord + ' ' + voicing_data.type;
            return !chordFullName.includes('7') && 
                   !chordFullName.includes('9') &&
                   !chordFullName.includes('11') &&
                   !chordFullName.includes('13');
        }
        
        // Try checking a range to see if it has a fourth note defined
        const range = getCurrentRange();
        if (voicing_data[range] && typeof voicing_data[range] === 'object') {
            const firstPosition = Object.keys(voicing_data[range])[0];
            if (firstPosition && voicing_data[range][firstPosition]) {
                const posData = Array.isArray(voicing_data[range][firstPosition]) 
                    ? voicing_data[range][firstPosition][0] 
                    : voicing_data[range][firstPosition];
                
                // Count how many strings have notes defined
                const noteCount = Object.keys(posData || {}).length;
                return noteCount <= 3; // 3 or fewer notes = triad
            }
        }
    }
    
    // If we can't determine, we'll use a safer default assuming it's a triad
    return true;
}

/**
 * Override cursor click functions with direct DOM manipulation
 */
function overrideCursorClickFunctions() {
    // Store original functions if they exist
    const originalLeftClick = window.leftCursorClick;
    const originalRightClick = window.rightCursorClick;
    
    // Override left cursor click function
    window.leftCursorClick = function() {
        
        // Get current position and available positions
        const positions = getAvailablePositions();
        const currentPosition = getCurrentPosition();
        
        const currentIndex = positions.indexOf(currentPosition);
        
        if (positions.length === 0 || currentIndex === -1) {
            console.warn(`Cannot navigate left: no positions found or current position "${currentPosition}" not in list:`, positions);
            
            // Safety fallback - use first position if current not found
            if (positions.length > 0) {
                const fallbackPosition = positions[0];
                
                // Update URL and UI
                updatePositionInURL(fallbackPosition);
                updatePositionInUI(fallbackPosition);
                
                // Directly activate notes for this position
                activateNotesForPosition(fallbackPosition);
            }
            return;
        }
        
        // Calculate new position index (cyclical)
        const newIndex = (currentIndex - 1 + positions.length) % positions.length; // Corrected index calculation
        const newPosition = positions[newIndex];
        
        if (newPosition === currentPosition) {
            console.warn(`Navigation would not change position (${currentPosition} to ${newPosition})`);
            
            // Try forcing a different position if we have more than one
            if (positions.length > 1) {
                const forcedIndex = (newIndex - 1 + positions.length) % positions.length;
                const forcedPosition = positions[forcedIndex];
                
                // Update URL and UI
                updatePositionInURL(forcedPosition);
                updatePositionInUI(forcedPosition);
                
                // Directly activate notes for this position
                activateNotesForPosition(forcedPosition);
            }
            return;
        }
        
        
        // Update URL and UI
        updatePositionInURL(newPosition);
        updatePositionInUI(newPosition);
        
        // Directly activate notes for this position
        activateNotesForPosition(newPosition);
        
        // Refresh chord display if needed
        if (typeof getTonesFromDataChords === 'function') {
            setTimeout(() => {
                getTonesFromDataChords(newPosition, getCurrentRange());
            }, 50);
        }
    };
    
    // Override right cursor click function
    window.rightCursorClick = function() {
        
        // Get current position and available positions
        const positions = getAvailablePositions();
        const currentPosition = getCurrentPosition();
        
        const currentIndex = positions.indexOf(currentPosition);
        
        if (positions.length === 0 || currentIndex === -1) {
            console.warn(`Cannot navigate right: no positions found or current position "${currentPosition}" not in list:`, positions);
            
            // Safety fallback - use first position if current not found
            if (positions.length > 0) {
                const fallbackPosition = positions[0];
                
                // Update URL and UI
                updatePositionInURL(fallbackPosition);
                updatePositionInUI(fallbackPosition);
                
                // Directly activate notes for this position
                activateNotesForPosition(fallbackPosition);
            } else {
                // Handle empty positions array by adding a default position
                positions.push('Root Position');
                
                // Update URL and UI for Root Position
                updatePositionInURL('Root Position');
                updatePositionInUI('Root Position');
                
                // Use Root Position as fallback
                activateNotesForPosition('Root Position');
            }
            return;
        }
        
        // Calculate new position index (cyclical)
        const newIndex = (currentIndex + 1) % positions.length; // Corrected index calculation
        const newPosition = positions[newIndex];
        
        if (newPosition === currentPosition) {
            console.warn(`Navigation would not change position (${currentPosition} to ${newPosition})`);
            
            // Try forcing a different position if we have more than one
            if (positions.length > 1) {
                const forcedIndex = (newIndex + 1) % positions.length;
                const forcedPosition = positions[forcedIndex];
                
                // Update URL and UI
                updatePositionInURL(forcedPosition);
                updatePositionInUI(forcedPosition);
                
                // Directly activate notes for this position
                activateNotesForPosition(forcedPosition);
            }
            return;
        }
        
        
        // Update URL and UI
        updatePositionInURL(newPosition);
        updatePositionInUI(newPosition);
        
        // Directly activate notes for this position
        activateNotesForPosition(newPosition);
        
        // Refresh chord display if needed
        if (typeof getTonesFromDataChords === 'function') {
            setTimeout(() => {
                getTonesFromDataChords(newPosition, getCurrentRange());
            }, 50);
        }
    };
}


/**
 * Get available positions for the current chord
 */
function getAvailablePositions() {
    // Default positions for most chords - use "Root Position" for UI consistency
    const defaultPositions = ['All Positions', 'Root Position', 'First Inversion', 'Second Inversion', 'Third Inversion'];
    
    // Check if we have a position select element
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
        const positions = Array.from(uniquePositions);
        
        // Make sure we return at least one position
        if (positions.length === 0) {
            positions.push('Root Position');
        }
        
        return positions;
    }
    
    // If we have voicing data, try to get positions from there
    if (typeof voicing_data !== 'undefined' && voicing_data !== null) {
        // Get current range
        const currentRange = getCurrentRange();
        if (voicing_data[currentRange] && typeof voicing_data[currentRange] === 'object') {
            const rawPositions = Object.keys(voicing_data[currentRange])
                .filter(pos => pos && !/^\d+$/.test(pos)); // Filter out numeric-only positions
            
            // Map "Basic Position" to "Root Position" for UI consistency
            const positions = rawPositions.map(pos => 
                pos === 'Basic Position' ? 'Root Position' : pos
            );
            
            if (positions.length > 0) {
                return positions;
            }
        } else {
            console.warn(`No valid data in voicing_data for range: ${currentRange}`);
        }
    } else {
    }
    
    // Handle 8-string scenarios - check if current range contains 8-string indicators
    const currentRange = getCurrentRange();
    const isEightString = currentRange.includes('lowB') || currentRange.includes('highA');
    
    // For 8-string guitars, we might need to limit available positions based on the range
    if (isEightString) {
        
        // Some ranges might not support all inversions on 8-string
        if (currentRange === 'lowB - highA' || currentRange === 'lowB - A') {
            const eightStringPositions = ['Root Position', 'First Inversion', 'Second Inversion'];
            return ['Root Position', 'First Inversion', 'Second Inversion'];
        }
    }
    
    // Fallback to default positions
    const positions = defaultPositions;
    
    // Final safety check to ensure we always return at least one position
    if (!Array.isArray(positions) || positions.length === 0) {
        console.warn("Safety fallback: returning singleton array with Root Position");
        return ['Root Position'];
    }
    
    return positions;
}

/**
 * Get current position
 */
function getCurrentPosition() {
    // Check URL first
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('position_select')) {
        const posValue = urlParams.get('position_select');
        // Handle numeric position values
        if (/^\d+$/.test(posValue)) {
            // Position 0 is "Root Position" mode - for consistent mapping
            // Other numeric positions should be mapped to their corresponding positions
            const numericPosition = parseInt(posValue, 10);
            
            // Map numeric positions to string names
            switch(numericPosition) {
                case 0: return 'Root Position'; // Changed from 'All Positions' to 'Root Position'
                case 1: return 'Root Position';
                case 2: return 'First Inversion';
                case 3: return 'Second Inversion';
                case 4: return 'Third Inversion';
                default: return 'Root Position';
            }
        }
        // Handle Basic Position -> Root Position mapping for consistency
        return posValue === 'Basic Position' ? 'Root Position' : posValue;
    }
    
    // Check position select element
    const positionSelect = document.getElementById('position_select');
    if (positionSelect && positionSelect.selectedIndex >= 0) {
        const posValue = positionSelect.options[positionSelect.selectedIndex].value;
        // If the value is only numbers, return a default position
        if (/^\d+$/.test(posValue)) {
            return 'Root Position';
        }
        // Handle Basic Position -> Root Position mapping for consistency
        return posValue === 'Basic Position' ? 'Root Position' : posValue;
    }
    
    // Default to Root position
    return 'Root Position';
}

/**
 * Get current string range
 */
function getCurrentRange() {
    // Check URL first
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('note_range')) {
        return urlParams.get('note_range');
    }
    
    // Check note range select element
    const noteRangeSelect = document.getElementById('note_range');
    if (noteRangeSelect) {
        return noteRangeSelect.value;
    }
    
    // Default range
    return 'e - g';
}

/**
 * Update position in URL
 */
function updatePositionInURL(position) {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('position_select', position);
    
    // Update URL without reloading page
    const newUrl = window.location.pathname + '?' + urlParams.toString();
    window.history.replaceState(null, null, newUrl);
}

/**
 * Update position in UI elements
 */
function updatePositionInUI(position) {
    // Update position select if it exists
    const positionSelect = document.getElementById('position_select');
    if (positionSelect) {
        positionSelect.value = position;
    }
    
    // Update position text in analysis container
    const positionValue = document.querySelector('.position-value');
    if (positionValue) {
        positionValue.textContent = position;
    }
}

// Track if we've already reset notes recently to avoid rapid resets
let resetInProgress = false;
let lastResetTime = 0;

/**
 * Reset all active notes
 */
function resetActiveNotes() {
    // Prevent rapid resets (within 500ms) to avoid conflicts
    const now = Date.now();
    
    // If we're handing position "0", use a clean reset to avoid duplicate notes
    const urlParams = new URLSearchParams(window.location.search);
    const currentPos = urlParams.get('position_select'); 
    
    // For position "0", we'll do a proper reset to avoid duplicate inversions
    if (currentPos === '0' || currentPos === 0) {
        
        // First save the current position to properly mark roots later
        const currentPosition = 'Root Position'; // Force Root Position for consistent mapping
        
        // Force a more aggressive reset with inline styles
        forceCompleteReset();
        
        // Return minimal data
        return { 
            existingRoots: [],
            position: currentPosition
        };
    }
    
    if (resetInProgress || (now - lastResetTime < 500)) {
        // Return cached data from last reset if available
        if (window.lastResetData) {
            return window.lastResetData;
        }
        // Otherwise create minimal reset data
        return { 
            existingRoots: [], 
            position: getCurrentPosition() 
        };
    }
    
    resetInProgress = true;
    lastResetTime = now;
    
    // First save the current position to properly mark roots later
    const currentPosition = getCurrentPosition();
    
    // Store the existing root notes before clearing
    const existingRoots = [];
    document.querySelectorAll('img.tone.root').forEach(rootEl => {
        try {
            const stringElement = rootEl.closest('[class*="String"]');
            if (stringElement) {
                const stringClass = stringElement.className.match(/[a-zA-Z]+String/);
                if (stringClass && stringClass[0]) {
                    existingRoots.push({
                        string: stringClass[0],
                        note: Array.from(rootEl.classList).find(cls => ['a', 'ab', 'as', 'b', 'bb', 'c', 'cs', 'db', 'd', 'ds', 'eb', 'e', 'f', 'fs', 'gb', 'g', 'gs'].includes(cls))
                    });
                }
            }
        } catch (e) {
            console.warn('Error processing root note:', e);
        }
    });
    
    // Use the forceful reset to ensure all notes are cleared
    forceCompleteReset();
    
    // Cache the result for potential reuse
    const resetData = { existingRoots, position: currentPosition };
    window.lastResetData = resetData;
    
    // Clear reset flag after a delay
    setTimeout(() => {
        resetInProgress = false;
    }, 200);
    
    return resetData; // Return the data for reuse
}

/**
 * Force a complete reset of all note-related elements
 * This handles both classes and inline styles
 */
function forceCompleteReset() {
    // Use a more aggressive two-phase approach to reset everything

    // PHASE 1: First pass - brutal reset of all relevant properties
    
    // Reset all note elements with a direct style override approach
    document.querySelectorAll('.note').forEach(element => {
        // Remove all classes that could indicate active state
        element.classList.remove('active', 'inversion-note', 'alternative-position', 'ghost', 'show');
        element.removeAttribute('data-inversion');
        element.removeAttribute('data-position');
        
        // Force styles reset with !important to override any inline styles
        element.style.cssText += '; opacity: 1 !important; visibility: visible !important;';
        
        // Then immediately remove these overrides to get to a neutral state
        setTimeout(() => {
            element.style.opacity = '';
            element.style.visibility = '';
        }, 0);
    });
    
    // Reset all tone images to default with force
    document.querySelectorAll('img.tone').forEach(element => {
        // Reset image source
        element.src = '/static/media/yellow_circle.svg';
        
        // Remove all possible active/special classes
        element.classList.remove('active', 'root', 'inversion-root', 'ghost-tone', 
                               'alternative-root', 'alternative-tone');
                               
        // Force reset all styling that might be set inline
        element.style.cssText = 'opacity: 1 !important; border: none !important; box-shadow: none !important;';
        
        // Then neutralize
        setTimeout(() => {
            element.style.opacity = '';
            element.style.border = '';
            element.style.boxShadow = '';
        }, 0);
    });
    
    // PHASE 2: Second pass - targeted cleanup for specific elements that might persist
    setTimeout(() => {
        // 1. Force ALL .active class off every element in the fretboard container
        document.querySelectorAll('#fretboardcontainer .active').forEach(el => {
            el.classList.remove('active');
        });
        
        // 2. Reset specifically all notenames to hidden
        document.querySelectorAll('.notename').forEach(notename => {
            notename.style.cssText = 'visibility: hidden !important; opacity: 0 !important; font-weight: normal !important;';
            notename.classList.remove('active', 'show-name');
        });
        
        // 3. Reset any elements with specific note types that might have been active
        document.querySelectorAll('.note[class*="g2"], .note[class*="bb"], .note[class*="e2"], .note[class*="c2"]').forEach(el => {
            el.classList.remove('active');
            const toneImg = el.querySelector('img.tone');
            if (toneImg) {
                toneImg.classList.remove('active', 'root');
                toneImg.src = '/static/media/yellow_circle.svg';
                toneImg.style.opacity = '';
                toneImg.style.border = '';
                toneImg.style.boxShadow = '';
            }
            
            const noteName = el.querySelector('.notename');
            if (noteName) {
                noteName.style.visibility = 'hidden';
                noteName.style.opacity = '0';
                noteName.style.fontWeight = '';
            }
        });
        
        // 4. Using direct attribute selector for style overrides
        document.querySelectorAll('[style*="visibility"], [style*="opacity"]').forEach(el => {
            if (el.classList.contains('notename') || el.classList.contains('tone') || el.classList.contains('note')) {
                el.style.cssText = 'visibility: hidden !important; opacity: 0 !important;';
                
                setTimeout(() => {
                    if (el.classList.contains('notename')) {
                        el.style.visibility = 'hidden';
                        el.style.opacity = '0';
                    } else {
                        el.style.visibility = '';
                        el.style.opacity = '';
                    }
                }, 10);
            }
        });
        
        // 5. Special handling for root note images
        document.querySelectorAll('img.tone[src*="red_circle"]').forEach(img => {
            img.src = '/static/media/yellow_circle.svg';
            img.classList.remove('root');
            img.style.border = '';
            img.style.boxShadow = '';
        });
    }, 10);
    
    // PHASE 3: Final verification and cleanup after everything else has had a chance to run
    setTimeout(() => {
        // Final verification sweep to catch any elements that might still be active
        const stillActive = document.querySelectorAll('#fretboardcontainer .note.active, #fretboardcontainer img.tone.active, #fretboardcontainer img.tone.root');
        
        if (stillActive.length > 0) {
            console.log(`Final cleanup: Found ${stillActive.length} elements still active`);
            
            // Force cleanup one last time
            stillActive.forEach(el => {
                if (el.classList.contains('note')) {
                    el.classList.remove('active');
                    
                    // Force cleanup any child elements too
                    Array.from(el.children).forEach(child => {
                        child.classList.remove('active', 'root');
                        if (child.tagName === 'IMG') {
                            child.src = '/static/media/yellow_circle.svg';
                            child.style.border = '';
                            child.style.boxShadow = '';
                            child.style.opacity = '';
                        }
                        if (child.classList.contains('notename')) {
                            child.style.visibility = 'hidden';
                            child.style.opacity = '0';
                        }
                    });
                } else {
                    // Direct img.tone cleanup
                    el.classList.remove('active', 'root');
                    el.src = '/static/media/yellow_circle.svg';
                    el.style.border = '';
                    el.style.boxShadow = '';
                    el.style.opacity = '';
                }
            });
        }
        
        // Final check for any notenames still visible
        const visibleNotenames = document.querySelectorAll('#fretboardcontainer .notename[style*="visible"]');
        if (visibleNotenames.length > 0) {
            console.log(`Final cleanup: Found ${visibleNotenames.length} notenames still visible`);
            visibleNotenames.forEach(el => {
                el.style.cssText = 'visibility: hidden !important; opacity: 0 !important;';
            });
        }
    }, 50);
    
    // Dispatch an event for any listeners that need to know about this reset
    document.dispatchEvent(new CustomEvent('all-notes-reset', {
        detail: { timestamp: Date.now() }
    }));
}

/**
 * When right cursor is clicked, ensure no notes remain visible
 * This is a failsafe function that will be attached to document body
 */
function ensureRightCursorCleanup() {
    // Look for any event handlers that might be attaching to the right cursor
    try {
        const rightCursor = document.querySelector('.right-cursor');
        if (rightCursor) {
            // Create and dispatch a custom event after right cursor events
            rightCursor.addEventListener('click', function() {
                // Let normal handlers run first, then force cleanup
                setTimeout(() => {
                    forceCompleteReset();
                    
                    // Double verification of cleanup
                    setTimeout(() => {
                        const remainingActive = document.querySelectorAll('.note.active, img.tone.active, img.tone.root');
                        if (remainingActive.length > 0) {
                            console.log(`Post-cursor cleanup: Found ${remainingActive.length} elements still active, forcing cleanup`);
                            forceCompleteReset();
                        }
                    }, 100);
                }, 50);
            });
        }
    } catch (err) {
        console.error('Error setting up right cursor cleanup:', err);
    }
}

// Initialize the failsafe handler when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    ensureRightCursorCleanup();
    
    // Also handle any dynamically added cursors
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                for (let i = 0; i < mutation.addedNodes.length; i++) {
                    const node = mutation.addedNodes[i];
                    if (node.classList && node.classList.contains('right-cursor')) {
                        ensureRightCursorCleanup();
                        break;
                    }
                }
            }
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
});

/**
 * Directly activate notes for a specific chord position
 */
function activateNotesForPosition(position) {
    
    // Handle numeric or string position "0" consistently
    if (position === '0' || position === 0) {
        position = 'Root Position';
    }
    
    // Reset all active notes first, but save root notes data
    const { existingRoots, position: oldPosition } = resetActiveNotes();
    
    // Track if we successfully activated the notes
    let activationSuccess = false;
    
    // Special handling for "All Positions" or numeric position "0"
    if (position === 'All Positions' || position === '0' || position === 0) {
        
        // For these special modes, we'll activate Root Position first as a fallback
        // and then optionally show other inversions as shadows
        const fallbackPosition = 'Root Position';
        
        // If we have voicing data, activate multiple positions
        if (typeof voicing_data !== 'undefined' && voicing_data !== null) {
            // Get current range
            const range = getCurrentRange();
            
            // Try to activate Root Position first
            const rootSuccess = activatePositionNotes('Root Position', range, true);
            activationSuccess = rootSuccess;
            
            // Then optionally show other inversions as shadows
            if (rootSuccess) {
                setTimeout(() => {
                    // Get available positions for this range
                    const positions = getAvailablePositions();
                    
                    // Show other positions with reduced opacity
                    positions.forEach(otherPos => {
                        if (otherPos !== 'Root Position' && otherPos !== 'All Positions') {
                            activatePositionNotes(otherPos, range, false, true);
                        }
                    });
                }, 100);
            }
        }
        
        // If we didn't succeed with voicing data, fall back to pattern-based activation
        if (!activationSuccess) {
            activateNotesUsingDOMPatterns(fallbackPosition);
            activationSuccess = true;
        }
        
        // After activating notes, ensure we have root notes marked
        setTimeout(() => {
            const rootMarked = document.querySelectorAll('img.tone.root').length > 0;
            if (!rootMarked) {
                ensureRootNoteMarked('Root Position');
            }
        }, 100);
        
        // Fire completion event and exit early
        const event = new CustomEvent('chord-position-activated', {
            detail: { 
                position: position, 
                success: activationSuccess,
                rootMarked: true
            }
        });
        document.dispatchEvent(event);
        return;
    }
    
    // Fix position naming inconsistency
    let internalPosition;
    if (position === 'Root Position') {
        internalPosition = 'Basic Position';
    } else if (position === '0' || position === 0) {
        internalPosition = 'Basic Position';
    } else {
        internalPosition = position;
    }
    
    // Try to get position data from voicing_data
    try {
        const range = getCurrentRange();
        
        // Double check position "0" handling
        if (position === '0' || position === 0) {
            // This should have been normalized earlier, but as extra protection:
            position = 'Root Position';
            internalPosition = 'Basic Position';
        }
        
        if (typeof voicing_data === 'undefined' || voicing_data === null) {
            console.warn("voicing_data is undefined or null");
        } else if (!voicing_data[range]) {
            console.warn(`No data found for range ${range} in voicing_data`);
        } else if (!voicing_data[range][internalPosition]) {
            console.warn(`No data found for position ${internalPosition} in range ${range}`);
            
            // Special handling for position "0" - always map to Basic Position first
            if (position === '0' || position === 0) {
                if (voicing_data[range]['Basic Position']) {
                    internalPosition = 'Basic Position';
                    activationSuccess = true;
                } else if (voicing_data[range]['Root Position']) {
                    internalPosition = 'Root Position';
                    activationSuccess = true;
                }
            } 
            // If not position 0 or if the special handling didn't work, try general fallback
            if (!activationSuccess) {
                // FIXED: Fall back to an available position if current one doesn't exist
                const availablePositions = Object.keys(voicing_data[range]);
                if (availablePositions.length > 0) {
                    // Try to map position logically - if Third Inversion is missing,
                    // try Second Inversion, then First Inversion, then Basic Position
                    let fallbackPosition = availablePositions[0]; // Default to first available
                    
                    // Try to find the closest available position to the requested one
                    if (position === 'Third Inversion' && availablePositions.includes('Second Inversion')) {
                        fallbackPosition = 'Second Inversion';
                    } else if (position === 'Second Inversion' && availablePositions.includes('First Inversion')) {
                        fallbackPosition = 'First Inversion';
                    } else if ((position === 'First Inversion' || position === 'Second Inversion') && 
                              (availablePositions.includes('Basic Position') || availablePositions.includes('Root Position'))) {
                        fallbackPosition = availablePositions.includes('Basic Position') ? 'Basic Position' : 'Root Position';
                    }
                    
                    
                    // Redirect to the fallback position (without recursion to avoid loops)
                    activationSuccess = true;
                    
                    // We'll proceed with the fallback position data below
                    internalPosition = fallbackPosition;
                }
            }
        } else {
            let positionData = voicing_data[range][internalPosition];
            
            // Handle array format
            if (Array.isArray(positionData)) {
                positionData = positionData[0];
            }
            
            // Activate each string in the position data
            if (positionData && typeof positionData === 'object') {
                let activatedNotes = 0;
                
                for (const stringKey in positionData) {
                    if (positionData.hasOwnProperty(stringKey)) {
                        // Skip the assigned_strings property - it's not a string with notes
                        if (stringKey === 'assigned_strings') {
                            continue;
                        }
                        
                        // Get note data
                        const noteData = positionData[stringKey];
                        if (!noteData) {
                            continue;
                        }
                        
                        // Handle different data formats
                        let noteName, isRoot;
                        
                        if (Array.isArray(noteData)) {
                            noteName = noteData[0];
                            
                            // Enhanced root detection - check all array positions for 'R' or 'Root'
                            isRoot = false;
                            for (let i = 0; i < noteData.length; i++) {
                                if (noteData[i] === 'R' || noteData[i] === 'Root') {
                                    isRoot = true;
                                    break;
                                }
                            }
                            
                        } else if (typeof noteData === 'string') {
                            noteName = noteData;
                            
                            // Default root detection for string format
                            isRoot = false;
                            
                        } else {
                            console.warn(`Unexpected note data format for ${stringKey}:`, noteData);
                            continue;
                        }
                        
                        if (!noteName) {
                            console.warn(`No valid note name for ${stringKey}`);
                            continue;
                        }
                        
                        // Extract base note without octave
                        const baseNote = noteName.replace(/[0-9]/g, '').toLowerCase();
                        
                        // Define valid note names explicitly for validation
                        const validNoteNames = ['a', 'ab', 'as', 'b', 'bb', 'c', 'cs', 'db', 'd', 'ds', 'eb', 'e', 'f', 'fs', 'gb', 'g', 'gs'];
                        
                        // Validate the note name
                        if (!validNoteNames.includes(baseNote)) {
                            console.warn(`Invalid note name: ${baseNote} from ${noteName}`);
                            continue;
                        }
                        
                        // Use original note name with octave for DOM selection
                        // Find all elements matching this note on this string
                        const noteElements = document.querySelectorAll(`.${stringKey} .note.${noteName.toLowerCase()}`);
                        
                        // If we have notes, try to find the best one to display
                        if (noteElements.length > 0) {
                            // If it's a third inversion and we need the high notes, look for them on the d-string
                            let bestElement = noteElements[0]; // Default to first element
                            
                            // For CMaj7 third inversion we need to ensure we can see the high G on d-string
                            if (position === 'Third Inversion' && stringKey === 'dString' && baseNote === 'g') {
                                // Try to find the highest fret g note for d-string in third inversion
                                // This is usually at fret 17
                                for (let i = 0; i <noteElements.length; i++) {
                                    const noteEl = noteElements[i];
                                    const fretEl = noteEl.closest('[class*="fret"]');
                                    
                                    if (fretEl && fretEl.classList.contains('seventeen')) {
                                        bestElement = noteEl;
                                        break;
                                    }
                                }
                            }
                            
                            // Activate the selected element
                            bestElement.classList.add('active');
                            
                            // Find corresponding tone element
                            const toneElement = bestElement.querySelector('img.tone');
                            if (toneElement) {
                                toneElement.classList.add('active');
                                
                                // Mark as root if needed - with extra visibility
                                if (isRoot) {
                                    toneElement.classList.add('root');
                                    
                                    // If this is part of an alternative inversion, mark it specially
                                    if (toneElement.classList.contains('inversion-tone')) {
                                        toneElement.classList.add('inversion-root');
                                        toneElement.src = '/static/media/red_circle.svg';
                                        toneElement.style.opacity = '0.7';
                                        toneElement.style.border = '2px dashed #AA5500';
                                        toneElement.style.boxShadow = '0 0 3px rgba(200, 100, 0, 0.3)';
                                    } else {
                                        // This is the active inversion's root
                                        toneElement.src = '/static/media/red_circle.svg';
                                        toneElement.style.opacity = '1';
                                        toneElement.style.border = '2px solid #CC0000';
                                        toneElement.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
                                    }
                                }
                            }
                            
                            activatedNotes++;
                        } else {
                            console.warn(`Could not find ${baseNote} elements for ${stringKey}`);
                        }
                    }
                }
                
                activationSuccess = activatedNotes > 0;
            } else {
                console.warn("Invalid position data structure:", positionData);
            }
        }
    } catch (error) {
        console.error('Error activating notes:', error);
    }
    
    // Fallback activation method using DOM traversal
    if (!activationSuccess || document.querySelectorAll('.active').length === 0) {
        activateNotesUsingDOMPatterns(position);
    }
    
    // Execute the appropriate code to mark root notes
    // First check if we have any root notes
    const rootMarked = document.querySelectorAll('img.tone.root').length > 0;
    if (!rootMarked) {
        
        // Assemble the root note information based on the position
        let rootData = {};
        if (position === 'Root Position' || position === 'Basic Position') {
            rootData = {
                preferredStrings: ['gString'], 
                noteNames: ['c', 'c1', 'c2', 'c3', 'c4']
            };
        } else if (position === 'First Inversion') {
            rootData = {
                preferredStrings: ['eString'], 
                noteNames: ['e', 'e1', 'e2', 'e3', 'e4']
            };
        } else if (position === 'Second Inversion') {
            rootData = {
                preferredStrings: ['bString'], 
                noteNames: ['g', 'g1', 'g2', 'g3', 'g4']
            };
        } else if (position === 'Third Inversion') {
            rootData = {
                preferredStrings: ['gString', 'dString'], 
                noteNames: ['bb', 'bb1', 'bb2', 'bb3', 'as', 'as1', 'as2', 'as3']
            };
        }
        
        // Try finding the correct note
        let rootFound = false;
        for (const string of rootData.preferredStrings || []) {
            for (const note of rootData.noteNames || []) {
                // Find all notes matching that criteria
                const matchingNotes = document.querySelectorAll(`.${string} .note.${note}.active img.tone`);
                if (matchingNotes.length > 0) {
                    matchingNotes[0].classList.add('root');
                    matchingNotes[0].src = '/static/media/red_circle.svg';
                    matchingNotes[0].style.opacity = '1';
                    matchingNotes[0].style.border = '2px solid #CC0000';
                    matchingNotes[0].style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
                    
                    // Make the note name visible too
                    const noteName = matchingNotes[0].nextElementSibling;
                    if (noteName && noteName.classList.contains('notename')) {
                        noteName.style.visibility = 'visible';
                        noteName.style.opacity = '1';
                        noteName.style.fontWeight = 'bold';
                    }
                    rootFound = true;
                    break;
                }
            }
            if (rootFound) break;
        }
        
        // If still not found, fallback to any active note
        if (!rootFound) {
            // For C Major chord in different positions, try these specific notes
            const positionSpecificNotes = {
                'Root Position': ['c1', 'c2', 'c3', 'e1', 'e2', 'e3', 'g1', 'g2', 'g3'],
                'Basic Position': ['c1', 'c2', 'c3', 'e1', 'e2', 'e3', 'g1', 'g2', 'g3'],
                'First Inversion': ['e1', 'e2', 'e3', 'g1', 'g2', 'g3', 'c1', 'c2', 'c3'],
                'Second Inversion': ['g1', 'g2', 'g3', 'c1', 'c2', 'c3', 'e1', 'e2', 'e3'],
                'Third Inversion': ['bb1', 'bb2', 'bb3', 'c1', 'c2', 'c3', 'e1', 'e2', 'e3', 'g1', 'g2', 'g3']
            };
            
            // Try finding any of these notes
            const preferredNotes = positionSpecificNotes[position] || ['c', 'e', 'g'];
            for (const note of preferredNotes) {
                const anyMatch = document.querySelector(`.note.${note}.active img.tone`);
                if (anyMatch) {
                    anyMatch.classList.add('root');
                    anyMatch.src = '/static/media/red_circle.svg';
                    anyMatch.style.opacity = '1';
                    anyMatch.style.border = '2px solid #CC0000';
                    anyMatch.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
                    rootFound = true;
                    break;
                }
            }
            
            // Last resort - just pick any active note
            if (!rootFound) {
                const anyNote = document.querySelector('.note.active img.tone');
                if (anyNote) {
                    anyNote.classList.add('root');
                    anyNote.src = '/static/media/red_circle.svg';
                    anyNote.style.opacity = '1';
                    anyNote.style.border = '2px solid #CC0000';
                    anyNote.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
                }
            }
        }
    }
    
    // Fire an event to notify that we've completed the activation
    const event = new CustomEvent('chord-position-activated', {
        detail: { 
            position: position, 
            success: activationSuccess,
            rootMarked: rootMarked
        }
    });
    document.dispatchEvent(event);
}

/**
 * Ensure a root note is always marked for the current position
 */
function ensureRootNoteMarked(position) {
    // Get appropriate string based on position
    let targetString = 'gString'; // Default for Root/Basic position
    
    if (position === 'First Inversion') {
        targetString = 'eString';
    } else if (position === 'Second Inversion') {
        targetString = 'bString';
    } else if (position === 'Third Inversion') {
        targetString = 'gString';
    }
    
    // Find active note on target string
    const activeNote = document.querySelector(`.${targetString} .note.active:not(.inversion-note) img.tone`);
    
    if (activeNote) {
        activeNote.classList.add('root');
        activeNote.src = '/static/media/red_circle.svg';
        activeNote.style.opacity = '1';
        activeNote.style.border = '2px solid #CC0000';
        activeNote.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
        return true;
    } else {
        // Try other strings if target string doesn't have an active note
        const anyActiveNote = document.querySelector('.note.active:not(.inversion-note) img.tone');
        if (anyActiveNote) {
            anyActiveNote.classList.add('root');
            anyActiveNote.src = '/static/media/red_circle.svg';
            anyActiveNote.style.opacity = '1';
            anyActiveNote.style.border = '2px solid #CC0000';
            anyActiveNote.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
            return true;
        }
    }
    
    return false;
}

/**
 * Fallback method to activate notes based on DOM patterns
 */
function activateNotesUsingDOMPatterns(position) {
    
    // Make an educated guess about which notes to activate based on position
    const stringNames = ['highAString', 'eString', 'bString', 'gString', 'dString', 'AString', 'ELowString', 'lowBString'];
    const usableStrings = stringNames.filter(name => document.querySelector('.' + name) !== null);
    
    // Get root notes (if any are already marked)
    const rootNotes = document.querySelectorAll('img.tone.root');
    const rootNotesExist = rootNotes.length > 0;
    
    // Detect if we're dealing with 8-string
    const isEightString = usableStrings.includes('lowBString') || usableStrings.includes('highAString');
    
    // Check for valid positions in 8-string mode
    if (isEightString && position === 'Third Inversion') {
        // Get the current range
        const range = getCurrentRange();
        
        // Some specific 8-string ranges don't support Third Inversion
        const restrictedRanges = ['lowB - highA', 'lowB - b', 'lowB - e', 'lowB - A'];
        
        if (restrictedRanges.includes(range)) {
            position = 'Second Inversion';
        }
    }
    
    // Create pattern definitions for different positions and string sets
    const patternDefinitions = {
        // Standard 6-string patterns
        standard: {
            'Root Position': {
                'gString': [3, 5, 7],
                'dString': [5, 7, 3],
                'AString': [3, 5, 7]
            },
            'First Inversion': {
                'eString': [3, 5, 7],
                'bString': [5, 7, 3],
                'gString': [5, 3, 7]
            },
            'Second Inversion': {
                'bString': [3, 5, 7],
                'gString': [5, 7, 3],
                'dString': [3, 5, 7]
            },
            'Third Inversion': {
                'bString': [6, 8, 10],
                'gString': [7, 9, 5],
                'dString': [7, 9, 5]
            }
        },
        // 8-string patterns - additional patterns for extended range
        eightString: {
            'Root Position': {
                'lowBString': [3, 5, 7],
                'ELowString': [3, 5, 7],
                'AString': [5, 7, 3],
                'dString': [5, 7, 3]
            },
            'First Inversion': {
                'ELowString': [3, 5, 7],
                'AString': [3, 5, 7],
                'dString': [5, 7, 3],
                'gString': [5, 3, 7]
            },
            'Second Inversion': {
                'AString': [3, 5, 7],
                'dString': [3, 5, 7],
                'gString': [5, 7, 3],
                'bString': [3, 5, 7]
            }
        }
    };
    
    // Select the appropriate pattern set
    const patternSet = isEightString ? patternDefinitions.eightString : patternDefinitions.standard;
    
    // Fallback to standard if position not defined in 8-string patterns
    const activePatterns = patternSet[position] || patternDefinitions.standard[position];
    
    // Apply the patterns for the current position
    if (activePatterns) {
        // Track how many notes we've activated successfully
        let activatedNotes = 0;
        
        // Process each string in the pattern
        Object.keys(activePatterns).forEach(stringKey => {
            // Skip if this string doesn't exist in the current layout
            if (!usableStrings.includes(stringKey)) {
                return;
            }
            
            // Get preferred frets for this string
            const preferredFrets = activePatterns[stringKey];
            
            // Try each preferred fret until we find a note
            for (const fret of preferredFrets) {
                const fretName = numberToEnglishFret(fret);
                const noteElement = document.querySelector(`.${stringKey} .fret.${fretName} .note`);
                
                if (noteElement) {
                    noteElement.classList.add('active');
                    activatedNotes++;
                    
                    // Get tone element
                    const toneElement = noteElement.querySelector('img.tone');
                    if (toneElement) {
                        toneElement.classList.add('active');
                        
                        // Mark as root based on position and string
                        let isRoot = false;
                        
                        // Root note marking logic
                        if (position === 'Root Position' || position === 'Basic Position') {
                            isRoot = stringKey === 'gString' || stringKey === 'lowBString';
                        } else if (position === 'First Inversion') {
                            isRoot = stringKey === 'eString' || stringKey === 'ELowString';
                        } else if (position === 'Second Inversion') {
                            isRoot = stringKey === 'bString' || stringKey === 'AString';
                        } else if (position === 'Third Inversion') {
                            isRoot = stringKey === 'gString' || stringKey === 'dString';
                        }
                        
                        // Apply root styling if applicable and no roots exist yet
                        if (!rootNotesExist && isRoot) {
                            toneElement.classList.add('root');
                            toneElement.src = '/static/media/red_circle.svg';
                            toneElement.style.opacity = '1';
                            toneElement.style.border = '2px solid #CC0000';
                            toneElement.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
                        }
                    }
                    
                    // We found a note for this string, so move to the next string
                    break;
                }
            }
        });
        
        
        // If we didn't activate enough notes, try a more general approach
        if (activatedNotes < 3) {
            activateNotesUsingGenericPatterns(position, usableStrings, rootNotesExist);
        }
    } else {
        activateNotesUsingGenericPatterns(position, usableStrings, rootNotesExist);
    }
}

/**
 * Fallback to very generic patterns when specific patterns fail
 */
function activateNotesUsingGenericPatterns(position, usableStrings, rootNotesExist) {
    // Very generic patterns that should work on most fretboard layouts
    if (position === 'Basic Position' || position === 'Root Position') {
        // For basic position, try to find notes in middle positions of lower strings
        for (let i = Math.min(3, usableStrings.length - 1); i >= 0; i--) {
            const stringName = usableStrings[i];
            const middleFrets = [7, 5, 3, 10, 8, 12];
            
            for (const fret of middleFrets) {
                const fretName = numberToEnglishFret(fret);
                const noteElement = document.querySelector(`.${stringName} .fret.${fretName} .note`);
                if (noteElement) {
                    noteElement.classList.add('active');
                    
                    // Mark lowest string as root if no roots exist
                    const toneElement = noteElement.querySelector('img.tone');
                    if (toneElement) {
                        toneElement.classList.add('active');
                        if (!rootNotesExist && i === 3) {
                            toneElement.classList.add('root');
                            toneElement.src = '/static/media/red_circle.svg';
                            toneElement.style.opacity = '1';
                            toneElement.style.border = '2px solid #CC0000';
                            toneElement.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
                        }
                    }
                    break;
                }
            }
        }
    } else if (position === 'First Inversion' || position === 'Second Inversion' || position === 'Third Inversion') {
        // Use similar patterns for all inversions, but adjust which string gets the root note
        for (let i = Math.min(4, usableStrings.length - 1); i >= 0; i--) {
            const stringName = usableStrings[i];
            const preferredFrets = [5, 7, 3, 8, 10, 12];
            
            for (const fret of preferredFrets) {
                const fretName = numberToEnglishFret(fret);
                const noteElement = document.querySelector(`.${stringName} .fret.${fretName} .note`);
                if (noteElement) {
                    noteElement.classList.add('active');
                    
                    // Mark appropriate string as root based on inversion
                    const toneElement = noteElement.querySelector('img.tone');
                    if (toneElement) {
                        toneElement.classList.add('active');
                        
                        // Select root string index based on inversion
                        let rootStringIndex;
                        if (position === 'First Inversion') rootStringIndex = 2;
                        else if (position === 'Second Inversion') rootStringIndex = 1;
                        else if (position === 'Third Inversion') rootStringIndex = 0;
                        
                        if (!rootNotesExist && i === rootStringIndex) {
                            toneElement.classList.add('root');
                            toneElement.src = '/static/media/red_circle.svg';
                            toneElement.style.opacity = '1';
                            toneElement.style.border = '2px solid #CC0000';
                            toneElement.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
                        }
                    }
                    break;
                }
            }
        }
    }
}

/**
 * Convert number to English fret name
 */
function numberToEnglishFret(num) {
    const fretNames = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 
                      'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 
                      'fifteen', 'sixteen', 'seventeen'];
    
    // Make sure we handle integers, strings, and any edge cases
    const fretNum = parseInt(num);
    
    // Handle out of range or NaN values
    if (isNaN(fretNum) || fretNum < 1 || fretNum > fretNames.length) {
        console.warn(`Attempted to convert invalid fret number: ${num}. Valid range is 1-${fretNames.length}.`);
        return '';
    }
    
    // Return the English name for this fret number
    return fretNames[fretNum - 1];
}

/**
 * Helper function to activate notes for a specific position
 * Used by activateNotesForPosition for regular and "All Positions" mode
 * 
 * @param {string} position - The position to activate
 * @param {string} range - The note range
 * @param {boolean} isPrimary - Whether this is the primary position (vs shadow)
 * @param {boolean} isShadow - Whether to show as shadow/alternative position
 * @returns {boolean} - Whether activation was successful
 */
function activatePositionNotes(position, range, isPrimary = true, isShadow = false) {
    // Skip if range or position is invalid
    if (!range || !position) return false;
    
    // Handle numeric or string position "0" consistently
    if (position === '0' || position === 0) {
        position = 'Root Position';
    }
    
    // Map position names for internal consistency
    let internalPosition;
    if (position === 'Root Position') {
        internalPosition = 'Basic Position';
    } else if (position === '0' || position === 0) {
        internalPosition = 'Basic Position';
    } else {
        internalPosition = position;
    }
    
    try {
        // Check if we have data for this position
        if (!voicing_data[range] || !voicing_data[range][internalPosition]) {
            return false;
        }
        
        let positionData = voicing_data[range][internalPosition];
        
        // Handle array format
        if (Array.isArray(positionData)) {
            positionData = positionData[0];
        }
        
        // Ensure we have valid data
        if (!positionData || typeof positionData !== 'object') {
            return false;
        }
        
        // Count how many notes we activate
        let activatedNotes = 0;
        
        // Process each string in the position data
        for (const stringKey in positionData) {
            if (!positionData.hasOwnProperty(stringKey) || stringKey === 'assigned_strings') {
                continue;
            }
            
            // Get note data
            const noteData = positionData[stringKey];
            if (!noteData) continue;
            
            // Extract note name and root status
            let noteName, isRoot;
            
            if (Array.isArray(noteData)) {
                noteName = noteData[0];
                isRoot = noteData.includes('R') || noteData.includes('Root');
                
            } else if (typeof noteData === 'string') {
                noteName = noteData;
                
                // Default root detection for string format
                isRoot = false;
                
            } else {
                continue;
            }
            
            // Validate the note name
            const baseNote = noteName.replace(/[0-9]/g, '').toLowerCase();
            const validNoteNames = ['a', 'ab', 'as', 'b', 'bb', 'c', 'cs', 'db', 'd', 'ds', 'eb', 'e', 'f', 'fs', 'gb', 'g', 'gs'];
            
            if (!validNoteNames.includes(baseNote)) {
                continue;
            }
            
            // Use original note name with octave for DOM selection
            // Find the note elements in the DOM
            const noteElements = document.querySelectorAll(`.${stringKey} .note.${noteName.toLowerCase()}`);
            
            if (noteElements.length > 0) {
                // For shadow positions, add a special class
                if (isShadow) {
                    noteElements[0].classList.add('alternative-position');
                    noteElements[0].setAttribute('data-position', position);
                } else {
                    // Otherwise just activate normally
                    noteElements[0].classList.add('active');
                }
                
                // Handle tone element styling
                const toneElement = noteElements[0].querySelector('img.tone');
                if (toneElement) {
                    if (isShadow) {
                        toneElement.classList.add('alternative-tone');
                        toneElement.style.opacity = '0.4';
                        
                        // If this is a root note in the alternative position
                        if (isRoot) {
                            toneElement.classList.add('alternative-root');
                            toneElement.style.border = '1px dashed #CC0000';
                        }
                    } else {
                        toneElement.classList.add('active');
                        
                        // Mark as root if needed
                        if (isRoot && isPrimary) {
                            toneElement.classList.add('root');
                            toneElement.src = '/static/media/red_circle.svg';
                            toneElement.style.opacity = '1';
                            toneElement.style.border = '2px solid #CC0000';
                            toneElement.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
                        }
                    }
                }
                
                activatedNotes++;
            }
        }
        
        return activatedNotes > 0;
    } catch (error) {
        console.error('Error activating notes for position:', error);
        return false;
    }
}
