/**
 * Chord Cursor Fix - clean implementation of cursor navigation for chord inversions
 * 
 * This module provides a standalone solution to handle left/right cursor navigation
 * between chord inversions (Root Position, First Inversion, Second Inversion, etc.)
 */

// Create initialization flag to prevent multiple initializations
let chordCursorFixInitialized = false;

/**
 * Initialize the chord cursor navigation system
 */
function initChordCursorNavigation() {
    // Check for scale view flag first (set by scale cursor fix)
    if (window.isScaleView === true) {
        console.log("CURSOR-DEBUG: Scale view detected, chord cursor fix skipped");
        return false;
    }
    
    // Enhanced check to ensure we're on a chord page
    const url = window.location.href.toLowerCase();
    const isScaleOrArpeggioPage = url.includes('scale') || url.includes('arpeggio');
    
    // Don't initialize if we're on a scale or arpeggio page
    if (isScaleOrArpeggioPage) {
        console.log("CURSOR-DEBUG: Scale or arpeggio page detected, chord cursor fix skipped");
        return false;
    }
    
    // Verify we're on a chord page
    const isChordPage = url.includes('chord') || document.querySelector('#chords_options_select');
    
    if (!isChordPage) {
        console.log("CURSOR-DEBUG: Not a chord page, chord cursor fix skipped");
        return false;
    }
    
    // Verify we have voicing_data and not scale_data
    if (typeof voicing_data === 'undefined' || !voicing_data) {
        console.log("CURSOR-DEBUG: No voicing_data available, chord cursor fix skipped");
        return false;
    }
    
    // If scale_data is present but voicing_data is missing, this is likely a scale view
    if (typeof scale_data !== 'undefined' && scale_data && !voicing_data) {
        console.log("CURSOR-DEBUG: Found scale_data but no voicing_data, chord cursor fix skipped");
        return false;
    }
    
    // Set global flag to indicate chord view
    window.isChordView = true;
    window.isScaleView = false;
    
    // Prevent duplicate initialization
    if (chordCursorFixInitialized) {
        console.log("CURSOR-DEBUG: Chord cursor fix already initialized");
        return true;
    }
    
    console.log("Chord cursor fix: Initializing...");
    chordCursorFixInitialized = true;
    
    // Add clean event listeners for cursor controls
    setupCursorEventListeners();
    
    // Ensure the inversions display is updated after navigation
    setupInversionDisplayUpdates();
    
    return true;
}

/**
 * Set up clean event listeners for cursor navigation
 */
function setupCursorEventListeners() {
    // Find cursor elements
    const leftCursor = document.querySelector('.left-cursor');
    const rightCursor = document.querySelector('.right-cursor');
    
    if (!leftCursor || !rightCursor) {
        console.warn('Chord cursor fix: Cursor elements not found in the DOM');
        
        // Setup a delayed retry - cursor elements might be added later by another script
        setTimeout(() => {
            const leftCursorRetry = document.querySelector('.left-cursor');
            const rightCursorRetry = document.querySelector('.right-cursor');
            
            if (leftCursorRetry || rightCursorRetry) {
                setupCursorEventListeners(); // Try again
            }
        }, 1000);
        
        return;
    }
    
    console.log("Chord cursor fix: Found cursor elements");
    
    // Create clean replacements of cursor elements to remove all existing event handlers
    const newLeftCursor = leftCursor.cloneNode(true);
    const newRightCursor = rightCursor.cloneNode(true);
    
    // Replace elements with clean copies
    leftCursor.parentNode.replaceChild(newLeftCursor, leftCursor);
    rightCursor.parentNode.replaceChild(newRightCursor, rightCursor);
    
    // Add clean event listeners
    newLeftCursor.addEventListener('click', handleLeftCursorClick);
    newRightCursor.addEventListener('click', handleRightCursorClick);
    
    // Override global cursor click functions to prevent circular references
    // Safe overriding of global cursor functions, only if we're in chord view
    if (!window.isScaleView) {
        const originalLeftClick = window.leftCursorClick;
        window.leftCursorClick = function(e) {
            // Skip in scale view
            if (window.isScaleView === true) {
                console.log("CURSOR-DEBUG: Scale view detected, chord leftCursorClick skipped");
                return originalLeftClick ? originalLeftClick(e) : undefined;
            }
            
            console.log("CURSOR-DEBUG: Chord leftCursorClick executed");
            window.lastChordHandlerTime = Date.now(); // Set timestamp to prevent scale handler interference
            handleLeftCursorClick(e || new Event('click'));
        };
        
        const originalRightClick = window.rightCursorClick;
        window.rightCursorClick = function(e) {
            // Skip in scale view
            if (window.isScaleView === true) {
                console.log("CURSOR-DEBUG: Scale view detected, chord rightCursorClick skipped");
                return originalRightClick ? originalRightClick(e) : undefined;
            }
            
            console.log("CURSOR-DEBUG: Chord rightCursorClick executed");
            window.lastChordHandlerTime = Date.now(); // Set timestamp to prevent scale handler interference
            handleRightCursorClick(e || new Event('click'));
        };
        
        // Also override the functions from cursor-inversion.js with safety checks
        const originalFpfLeft = window.fpfLeftCursorClick;
        window.fpfLeftCursorClick = function(context) {
            // Skip in scale view or if context indicates scales
            if (window.isScaleView === true || (context && context.currentMode === 'scales')) {
                console.log("CURSOR-DEBUG: Scale view detected, chord fpfLeftCursorClick skipped");
                return originalFpfLeft ? originalFpfLeft(context) : undefined;
            }
            
            console.log("CURSOR-DEBUG: Chord fpfLeftCursorClick executed");
            window.lastChordHandlerTime = Date.now(); // Set timestamp
            handleLeftCursorClick(new Event('click'));
        };
        
        const originalFpfRight = window.fpfRightCursorClick;
        window.fpfRightCursorClick = function(context) {
            // Skip in scale view or if context indicates scales
            if (window.isScaleView === true || (context && context.currentMode === 'scales')) {
                console.log("CURSOR-DEBUG: Scale view detected, chord fpfRightCursorClick skipped");
                return originalFpfRight ? originalFpfRight(context) : undefined;
            }
            
            console.log("CURSOR-DEBUG: Chord fpfRightCursorClick executed");
            window.lastChordHandlerTime = Date.now(); // Set timestamp
            handleRightCursorClick(new Event('click'));
        };
    }
    
    console.log("Chord cursor fix: Added clean event listeners to cursor elements");
}

/**
 * Handler for left cursor click - moves to previous inversion
 */
function handleLeftCursorClick(e) {
    e.preventDefault();
    navigateChordPosition('prev');
    
    // Dispatch a custom event that chord-inversions.js can listen for
    document.dispatchEvent(new CustomEvent('chord-inversion-navigated', {
        detail: { direction: 'prev' }
    }));
}

/**
 * Handler for right cursor click - moves to next inversion
 */
function handleRightCursorClick(e) {
    e.preventDefault();
    navigateChordPosition('next');
    
    // Dispatch a custom event that chord-inversions.js can listen for
    document.dispatchEvent(new CustomEvent('chord-inversion-navigated', {
        detail: { direction: 'next' }
    }));
}

/**
 * Main navigation function for chord positions/inversions
 * @param {string} direction - 'next' or 'prev'
 */
function navigateChordPosition(direction) {
    // Get current position and chord type from URL
    const urlParams = new URLSearchParams(window.location.search);
    const currentPosition = urlParams.get('position_select') || 'Root Position';
    const currentRange = urlParams.get('note_range') || 'e - g';
    
    // Get chord type to determine available inversions
    const chordType = urlParams.get('chords_options_select') || 
                     (document.getElementById('chords_options_select') ? 
                      document.getElementById('chords_options_select').value : 'Major');
    
    console.log(`Navigating ${direction} from: ${currentPosition} in chord type: ${chordType}`);
    
    // Determine available positions based on chord type
    let positions = getAvailablePositions(chordType);
    
    // Find current index
    const currentIndex = findPositionIndex(currentPosition, positions);
    if (currentIndex === -1) {
        console.warn(`Chord cursor fix: Current position "${currentPosition}" not found in available positions`);
        return;
    }
    
    // Calculate new index based on direction
    let newIndex;
    if (direction === 'next') {
        newIndex = (currentIndex + 1) % positions.length;
    } else {
        newIndex = (currentIndex - 1 + positions.length) % positions.length;
    }
    
    const newPosition = positions[newIndex];
    console.log(`Chord cursor fix: Navigating from ${currentPosition} to ${newPosition}`);
    
    // Update URL and select element
    updatePositionInUI(newPosition);
    updatePositionInURL(newPosition);
    
    // Call our direct implementation of activateNotesForPosition to avoid recursion
    activateNotesForPosition(newPosition, currentRange);
    
    // Dispatch event for other components to respond to the change
    document.dispatchEvent(new CustomEvent('chord-position-changed', { 
        detail: { 
            direction: direction,
            oldPosition: currentPosition,
            newPosition: newPosition
        }
    }));
}

/**
 * Get available positions based on chord type
 * Standardizes naming and includes appropriate number of inversions
 */
function getAvailablePositions(chordType) {
    // Default positions for triads
    let positions = ['Root Position', 'First Inversion', 'Second Inversion'];
    
    // Check if this is a seventh chord or extended chord
    if (chordType && (chordType.includes('7') || chordType.includes('9') || 
                     chordType.includes('11') || chordType.includes('13'))) {
        positions.push('Third Inversion');
    }
    
    // Try to get positions from select element if it exists
    const positionSelect = document.getElementById('position_select');
    if (positionSelect && positionSelect.options.length > 0) {
        // Get options from DOM, filtering out numeric-only values
        const selectPositions = [];
        for (let i = 0; i < positionSelect.options.length; i++) {
            const value = positionSelect.options[i].value;
            if (value && !/^\d+$/.test(value)) {
                selectPositions.push(value);
            }
        }
        
        // Use DOM options if we found valid ones
        if (selectPositions.length > 0) {
            return selectPositions;
        }
    }
    
    return positions;
}

/**
 * Find the index of a position in the available positions array
 * Handles position name variations
 */
function findPositionIndex(position, positions) {
    // Direct match
    const directIndex = positions.indexOf(position);
    if (directIndex !== -1) {
        return directIndex;
    }
    
    // Normalize the position name and try again
    const normalizedPosition = normalizePositionName(position);
    for (let i = 0; i < positions.length; i++) {
        if (normalizePositionName(positions[i]) === normalizedPosition) {
            return i;
        }
    }
    
    // Default to first position if not found
    return 0;
}

/**
 * Normalize position names to handle variations
 */
function normalizePositionName(position) {
    if (!position) return 'Root Position';
    
    // Handle various ways root position might be named
    if (position === 'Root Position' || position === 'Basic Position' || 
        position === '0' || position.includes('Basic') || position.includes('Root')) {
        return 'Root Position';
    }
    
    // Handle first inversion variants
    if (position.includes('First Inv') || position === '1st Inversion' || 
        position === '1' || position === 'First Inversion') {
        return 'First Inversion';
    }
    
    // Handle second inversion variants
    if (position.includes('Second Inv') || position === '2nd Inversion' || 
        position === '2' || position === 'Second Inversion') {
        return 'Second Inversion';
    }
    
    // Handle third inversion variants
    if (position.includes('Third Inv') || position === '3rd Inversion' || 
        position === '3' || position === 'Third Inversion') {
        return 'Third Inversion';
    }
    
    return position;
}

/**
 * Update the position in the UI (select element)
 */
function updatePositionInUI(position) {
    const positionSelect = document.getElementById('position_select');
    if (!positionSelect) {
        console.warn("Chord cursor fix: Could not find position_select element");
        return;
    }
    
    // Normalize for consistent comparison
    const normalizedPosition = normalizePositionName(position);
    
    // Find and select matching option
    let found = false;
    for (let i = 0; i < positionSelect.options.length; i++) {
        const optionValue = positionSelect.options[i].value;
        const normalizedOption = normalizePositionName(optionValue);
        
        if (normalizedOption === normalizedPosition) {
            positionSelect.selectedIndex = i;
            found = true;
            break;
        }
    }
    
    if (!found) {
        console.warn(`Chord cursor fix: Could not find matching option for "${position}"`);
        return;
    }
    
    // Trigger change event to update any listeners
    positionSelect.dispatchEvent(new Event('change'));
    
    console.log(`Chord cursor fix: Updated position_select to ${position}`);
}

/**
 * Update the position in the URL without reloading the page
 */
function updatePositionInURL(position) {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('position_select', position);
    const newUrl = window.location.pathname + '?' + urlParams.toString();
    window.history.replaceState(null, '', newUrl);
    
    console.log(`Chord cursor fix: Updated URL with position=${position}`);
}

/**
 * Activate notes for the selected position
 */
function activateNotesForPosition(position, range) {
    console.log(`Chord cursor fix: Activating notes for position ${position} with range ${range}`);
    
    // DIRECT IMPLEMENTATION to break recursive loop
    try {
        // Get current position from URL if not provided
        const urlParams = new URLSearchParams(window.location.search);
        const currentRange = range || urlParams.get('note_range') || 'e - g';
        
        // Make sure we have voicing data
        if (typeof window.voicing_data === 'undefined' || !window.voicing_data) {
            console.warn("Chord cursor fix: No voicing_data available");
            return;
        }
        
        // Get the correct position data
        if (!window.voicing_data[currentRange]) {
            console.warn(`Chord cursor fix: No data for range ${currentRange}`);
            return;
        }
        
        // Normalize position name for lookup
        let lookupPosition = position;
        if (position === 'Root Position') {
            lookupPosition = 'Basic Position';
        }
        
        // Try both position names
        let positionData = window.voicing_data[currentRange][position];
        if (!positionData && position === 'Root Position') {
            positionData = window.voicing_data[currentRange]['Basic Position'];
        } else if (!positionData && position === 'Basic Position') {
            positionData = window.voicing_data[currentRange]['Root Position'];
        }
        
        if (!positionData) {
            console.warn(`Chord cursor fix: No position data for ${position} in range ${currentRange}`);
            return;
        }
        
        // Reset all active elements
        document.querySelectorAll('.active').forEach(el => {
            el.classList.remove('active');
        });
        
        document.querySelectorAll('img.tone.root').forEach(el => {
            el.classList.remove('root');
            el.src = '/static/media/yellow_circle.svg';
        });
        
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
                // Check various positions for root flag
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
        
        // Update inversion display if available
        if (typeof window.setupInversionDisplay === 'function') {
            setTimeout(() => window.setupInversionDisplay(), 100);
        }
        
        console.log(`Chord cursor fix: Successfully activated notes for ${position}`);
    } catch (error) {
        console.error(`Chord cursor fix: Error activating notes: ${error.message}`);
    }
}

/**
 * Set up updates to the inversions display after navigation
 */
function setupInversionDisplayUpdates() {
    // Listen for navigation events and update inversion display
    document.addEventListener('chord-inversion-navigated', function(e) {
        // Wait for DOM updates to complete
        setTimeout(() => {
            if (typeof window.setupInversionDisplay === 'function') {
                window.setupInversionDisplay();
            }
        }, 100);
    });
    
    // Also listen for position_select changes
    const positionSelect = document.getElementById('position_select');
    if (positionSelect) {
        positionSelect.addEventListener('change', function() {
            // Wait for DOM updates to complete
            setTimeout(() => {
                if (typeof window.setupInversionDisplay === 'function') {
                    window.setupInversionDisplay();
                }
            }, 100);
        });
    }
}

// Initialize when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait for other scripts to load first
    setTimeout(initChordCursorNavigation, 1500);
    
    // Add a later check to ensure our fix is active
    setTimeout(() => {
        // Check if cursors have the expected listeners
        const leftCursor = document.querySelector('.left-cursor');
        const rightCursor = document.querySelector('.right-cursor');
        
        if (leftCursor && rightCursor) {
            // Re-apply our event listeners to ensure they're active
            setupCursorEventListeners();
            console.log("Chord cursor fix: Re-applied event listeners as a safety check");
        }
    }, 3000);
});

// Add a special listener for when the page is fully loaded
window.addEventListener('load', function() {
    // Wait a bit to ensure all dynamic elements are created
    setTimeout(() => {
        // Run our fix one more time
        if (!chordCursorFixInitialized) {
            initChordCursorNavigation();
        } else {
            // Just refresh the event listeners
            setupCursorEventListeners();
        }
        console.log("Chord cursor fix: Applied from window.load event");
    }, 1000);
});

// Create helper for manual initialization from console
window.initChordCursorNavigation = initChordCursorNavigation;
