/**
 * Chord Inversions Display
 * Shows all possible inversions for the current string set
 * - Selected inversion at full opacity (100%)
 * - Other inversions at reduced opacity (50%) to indicate available alternatives
 */

// Track if we're having recursion issues
let antiRecursionCounter = 0;

// Create initialization flag to prevent multiple initializations
let chordInversionsInitialized = false;

// Global flags attached to window object
window.isSettingUpInversions = false;
window.lastSetupTime = 0;
window.rootMarkingInProgress = false;

document.addEventListener('DOMContentLoaded', function() {
    
    // Prevent duplicate initialization
    if (chordInversionsInitialized) {
        return;
    }
    
    chordInversionsInitialized = true;
    
    // Use a single initialization sequence
    // Delay initialization to ensure other systems load first
    setTimeout(() => {
        
        // First check if another system has already set up roots and active notes
        const activeNotes = document.querySelectorAll('.note.active');
        const rootNotes = document.querySelectorAll('img.tone.root');
        
        
        // Only proceed if we have active notes but no root notes
        if (activeNotes.length > 0 && rootNotes.length === 0 && antiRecursionCounter < 2) {
            // Setup display only if needed
            setupInversionDisplay();
            
            // Then check for root notes after the display is set up
            setTimeout(() => {
                // Only do root marking if still needed
                const updatedRootNotes = document.querySelectorAll('img.tone.root');
                if (updatedRootNotes.length === 0) {
                    forceRootNoteMarking();
                    antiRecursionCounter++; // Increment to prevent excessive attempts
                } else {
                }
                
                // Reset antiRecursionCounter after a delay
                setTimeout(() => {
                    antiRecursionCounter = 0;
                }, 5000);
            }, 300);
        } else if (activeNotes.length === 0) {
        } else {
        }
    }, 1500); // Longer delay to ensure other systems initialize first
    
    // Add event listeners to cursor controls
    var leftCursor = document.querySelector('.left-cursor');
    var rightCursor = document.querySelector('.right-cursor');
    
    if (leftCursor) {
        var originalLeftClick = leftCursor.onclick;
        leftCursor.onclick = function(e) {
            if (originalLeftClick) originalLeftClick.call(this, e);
            setTimeout(setupInversionDisplay, 100);
        };
    }
    
    if (rightCursor) {
        var originalRightClick = rightCursor.onclick;
        rightCursor.onclick = function(e) {
            if (originalRightClick) originalRightClick.call(this, e);
            setTimeout(setupInversionDisplay, 100);
        };
    }
    
    // Keep track of the last event time to prevent loops
    let lastEventTime = 0;
    let eventDebounceCount = 0;
    let eventHandlingInProgress = false;
    
    // Listen for custom navigation events with debouncing
    document.addEventListener('chord-position-activated', function(e) {
        // Prevent handling event if we're already processing one
        if (eventHandlingInProgress) {
            return;
        }
        
        const now = Date.now();
        
        // Check for rapid-fire events (possible loop)
        if (now - lastEventTime < 300) {
            eventDebounceCount++;
            
            // If we detect an event loop, break it
            if (eventDebounceCount > 3) {
                console.warn("Event loop detected - breaking cycle");
                
                // Completely interrupt event handling for a longer period
                setTimeout(() => {
                    eventDebounceCount = 0; 
                    eventHandlingInProgress = false;
                }, 1000);
                
                return; // Don't proceed with the event
            }
        } else {
            // Reset counter if events aren't too rapid
            eventDebounceCount = 0;
        }
        
        lastEventTime = now;
        eventHandlingInProgress = true;
        
        // Add a small delay to allow state to settle
        setTimeout(() => {
            setupInversionDisplay();
            
            // Release the event handling lock
            setTimeout(() => {
                eventHandlingInProgress = false;
            }, 300);
        }, 100);
    });
    
    // Add listeners for the custom navigation buttons
    const prevInversionButton = document.querySelector('.nav-button.prev-inversion');
    if (prevInversionButton) {
        prevInversionButton.addEventListener('click', function() {
            setTimeout(setupInversionDisplay, 100);
        });
    }
    
    const nextInversionButton = document.querySelector('.nav-button.next-inversion');
    if (nextInversionButton) {
        nextInversionButton.addEventListener('click', function() {
            setTimeout(setupInversionDisplay, 100);
        });
    }
    
    // Keyboard navigation has been disabled
    
    // Use a more robust debounced observer approach to prevent excessive callbacks
    let observerTimeout = null;
    let rootCheckCount = 0;
    let lastObservedTime = 0;
    let observationFrequency = 0;
    let lastRootRecoveryTime = 0;
    
    const observer = new MutationObserver(function(mutations) {
        // Check if relevant mutations that might affect root notes
        const relevantMutations = mutations.filter(mutation => {
            // Look for class changes on .note elements or src changes on img.tone elements
            if (mutation.type === 'attributes') {
                if (mutation.attributeName === 'class' && 
                    mutation.target.classList.contains('note')) {
                    return true;
                }
                if (mutation.attributeName === 'src' && 
                    mutation.target.tagName === 'IMG' && 
                    mutation.target.classList.contains('tone')) {
                    return true;
                }
            }
            return false;
        });
        
        // Only proceed if there are relevant mutations
        if (relevantMutations.length === 0) {
            return;
        }
        
        // Check if mutations are happening too frequently (potential loop)
        const now = Date.now();
        if (now - lastObservedTime < 200) {
            observationFrequency++;
            
            // If we're getting lots of rapid changes, we might be in a loop
            if (observationFrequency > 5) {
                
                // Temporarily disconnect the observer
                observer.disconnect();
                
                // Reconnect after a cool-down period
                setTimeout(() => {
                    observationFrequency = 0;
                    const fretboard = document.querySelector('.fretboard');
                    if (fretboard) {
                        observer.observe(fretboard, { 
                            attributes: true, 
                            childList: true, 
                            subtree: true,
                            attributeFilter: ['class', 'src']
                        });
                    }
                }, 2000);
                
                return;
            }
        } else {
            // Reset counter when changes aren't rapid
            observationFrequency = 0;
        }
        lastObservedTime = now;
        
        // Clear any pending timeout
        if (observerTimeout) {
            clearTimeout(observerTimeout);
        }
        
        // Only check root nodes at most once per 1500ms to reduce frequency
        // Also limit frequency of root recovery to prevent thrashing
        if (now - lastRootRecoveryTime < 3000) {
            return; // Don't check again if we recently did a recovery
        }
        
        observerTimeout = setTimeout(function() {
            // First, check if active notes exist
            const activeNotes = document.querySelectorAll('.note.active');
            if (activeNotes.length === 0) {
                return;
            }
            
            // Limit the maximum number of checks to prevent infinite loops
            if (rootCheckCount > 3) {
                observer.disconnect();
                
                // Reconnect after a longer delay
                setTimeout(() => {
                    rootCheckCount = 0;
                    const fretboard = document.querySelector('.fretboard');
                    if (fretboard) {
                        observer.observe(fretboard, { 
                            attributes: true, 
                            childList: true, 
                            subtree: true,
                            attributeFilter: ['class', 'src']
                        });
                    }
                }, 4000);
                return;
            }
            
            // Check if root notes are present
            const rootNotes = document.querySelectorAll('img.tone.root');
            
            if (rootNotes.length === 0) {
                rootCheckCount++;
                lastRootRecoveryTime = Date.now();
                forceRootNoteMarking();
            } else {
                rootCheckCount = 0; // Reset the counter when roots are found
            }
        }, 1500); // Increased to 1500ms
    });
    
    // Start observing the fretboard element
    const fretboard = document.querySelector('.fretboard');
    if (fretboard) {
        observer.observe(fretboard, { 
            attributes: true, 
            childList: true, 
            subtree: true,
            attributeFilter: ['class', 'src']
        });
    }
});

/**
 * Set up the inversion display - active inversion fully visible, others 80% opacity
 */
function setupInversionDisplay(voicingData, currentRange, currentPositionInternal) {
    // Prevent recursive calls and rapid repeated calls
    const now = Date.now();
    if (window.isSettingUpInversions || (now - window.lastSetupTime < 300)) {
        return;
    }
    
    window.isSettingUpInversions = true;
    window.lastSetupTime = now;
    
    // Store the voicing data for later use in root marking
    // Use the passed voicingData if available, otherwise try window.voicing_data
    const effectiveVoicingData = voicingData || window.voicing_data;
    window.currentVoicingData = effectiveVoicingData; // Store globally

    // Get current position from URL if not passed
    const urlParams = new URLSearchParams(window.location.search);
    const currentPosition = urlParams.get('position_select') || 'Root Position';

    // Use passed internal position if available, otherwise map it
    let internalPos = currentPositionInternal;
    if (!internalPos) {
        if (currentPosition === 'Root Position' || currentPosition === '0' || currentPosition.includes('Basic')) {
            internalPos = 'Basic Position';
        } else if (currentPosition.includes('First Root') || currentPosition.includes('First Basic')) {
            internalPos = 'Basic Position';
        } else if (currentPosition.includes('First Inv')) {
            internalPos = 'First Inversion';
        } else if (currentPosition.includes('Second Inv')) {
            internalPos = 'Second Inversion';
        } else if (currentPosition.includes('Third Inv')) {
            internalPos = 'Third Inversion';
        } else {
            internalPos = currentPosition;
        }
    }

    // Use passed range if available, otherwise get from URL or default
    let range = currentRange;
     if (!range) {
        if (effectiveVoicingData && effectiveVoicingData.note_range) {
            range = effectiveVoicingData.note_range;
        } else {
            range = urlParams.get('note_range') || urlParams.get('range') || 'e - g';
        }
    }


    // Extract root info directly from the effective voicingData
    let rootCount = 0;
    let rootInfo = [];

    if (effectiveVoicingData && typeof effectiveVoicingData === 'object' && effectiveVoicingData[range] && effectiveVoicingData[range][internalPos]) {
        const activePositionData = effectiveVoicingData[range][internalPos];
        const stringData = activePositionData ? activePositionData[0] : null;

        if (stringData && typeof stringData === 'object') {
            Object.keys(stringData).forEach(key => {
                // Skip non-string data
                if (key === 'assigned_strings') return;

                const noteData = stringData[key];
                // Check for root flag (4th element is true)
                if (Array.isArray(noteData) && noteData.length >= 4 && noteData[3] === true) {
                    rootCount++;
                    rootInfo.push({
                        note: noteData[0],  // e.g., "c1"
                        string: key           // e.g., "lowBString"
                    });
                }
            });
        } else {
        }
    } else {
    }


    // Store root info for later use in fixRootNoteMarking
    window.rootInfoForMarking = rootInfo;

    // REST OF THE ORIGINAL FUNCTION LOGIC (from line 361 onwards in the original file)
    // First, reset all styling to ensure clean state
    document.querySelectorAll('.inversion-note, .inversion-tone').forEach(el => {
        el.classList.remove('inversion-note', 'inversion-tone');
        el.removeAttribute('data-inversion');
        el.style.opacity = '';
        el.style.border = '';
        el.style.boxShadow = '';
        el.style.filter = '';
    });

    // Re-apply root note styling
    // Primary root note (for active inversion)
    document.querySelectorAll('img.tone.root:not(.inversion-root)').forEach(el => {
        el.style.opacity = '1';
        el.style.border = '2px solid #CC0000';
        el.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
    });

    // Alternative inversion root notes
    document.querySelectorAll('img.tone.root.inversion-root').forEach(el => {
        el.style.opacity = '0.7';
        el.style.border = '2px dashed #AA5500';
        el.style.boxShadow = '0 0 3px rgba(200, 100, 0, 0.3)';
    });

    // Add CSS style for inversions if not already present
    if (!document.getElementById('inversion-style')) {
        const style = document.createElement('style');
        style.id = 'inversion-style';
        style.textContent = `
            .inversion-note.active,
            .inversion-tone.active {
                opacity: 0.4 !important;
                filter: brightness(0.9);
                transition: all 0.2s ease;
                border: 1px dashed rgba(100, 100, 255, 0.5);
            }

            /* Make alternative inversions visible on hover */
            .inversion-note.active:hover,
            .inversion-tone.active:hover {
                opacity: 0.7 !important;
                filter: brightness(1);
                cursor: pointer;
                border: 1px solid rgba(100, 100, 255, 0.8);
            }
        `;
        document.head.appendChild(style);
    }

    // Get available positions for this range
    const availablePositions = [];
    if (effectiveVoicingData && effectiveVoicingData[range]) {
        for (const pos in effectiveVoicingData[range]) {
            if (effectiveVoicingData[range].hasOwnProperty(pos) && pos && !/^\d+$/.test(pos)) {
                availablePositions.push(pos);
            }
        }
    }


    // Debug the active notes

    // Get tone elements for all positions
    availablePositions.forEach(position => {
        // Skip the current position from being marked as an alternative inversion
        if (position === internalPos ||
            (position === 'Basic Position' && internalPos === 'Root Position')) { // Adjust comparison
            return;
        }

        let rootStringForPosition = '';

        // Determine which string should have the root note based on position
        if (position === 'Basic Position' || position === 'Root Position') {
            rootStringForPosition = 'gString';
        } else if (position === 'First Inversion') {
            rootStringForPosition = 'eString';
        } else if (position === 'Second Inversion') {
            rootStringForPosition = 'bString';
        } else if (position === 'Third Inversion') {
            rootStringForPosition = 'gString';
        }

        // Get the position data
        const positionData = effectiveVoicingData[range][position];
        if (!positionData || !positionData[0]) return;

        // For each string in the position
        Object.keys(positionData[0]).forEach(stringKey => {
            // Extract note name
            let noteName = '';

            if (Array.isArray(positionData[0][stringKey])) {
                noteName = (positionData[0][stringKey][0] || '').toLowerCase();
            } else if (typeof positionData[0][stringKey] === 'string') {
                noteName = positionData[0][stringKey].toLowerCase();
            } else {
                return;
            }

            if (!noteName) return;

            // Find and activate notes for this inversion
            const noteElements = document.querySelectorAll(`.${stringKey} .note.${noteName}`);
            const toneElements = document.querySelectorAll(`.${stringKey} .tone.${noteName}, .${stringKey} img.tone.${noteName}`);

            // First, add the active class
            noteElements.forEach(el => {
                el.classList.add('active');

                // Then explicitly mark as alternative inversion
                el.classList.add('inversion-note');

                // Add a data attribute to make it clear this is an alternative inversion
                el.setAttribute('data-inversion', position);
            });

            toneElements.forEach(el => {
                el.classList.add('active');

                // Then explicitly mark as alternative inversion
                el.classList.add('inversion-tone');

                // Add a data attribute to make it clear this is an alternative inversion
                el.setAttribute('data-inversion', position);

                // If this is the root string for this inversion, mark it as a special "inversion-root" but not a full "root"
                if (stringKey === rootStringForPosition) {
                    // Instead of adding the main 'root' class, we'll use a special class for inversion roots
                    el.classList.add('inversion-root-candidate');

                    // Store the inversion this is a candidate root for
                    el.setAttribute('data-root-for', position);
                }
            });
        });
    });

    // After processing all positions, finalize the inversion root markings
    document.querySelectorAll('.inversion-root-candidate').forEach(el => {
        // Only mark if it's not already the main root
        if (!el.classList.contains('root')) {
            el.classList.add('inversion-root');
            el.style.opacity = '0.7';
            el.style.border = '2px dashed #AA5500';
            el.style.boxShadow = '0 0 3px rgba(200, 100, 0, 0.3)';
        }
        el.classList.remove('inversion-root-candidate');
    });

    // Debug the active notes after processing

    // Update navigation buttons based on whether inversions are available
    updateInversionNavigationButtons(availablePositions.length > 1);
    
    // Force mark a root note if none exists after all this processing
    setTimeout(() => {
        const rootCount = document.querySelectorAll('img.tone.root').length;
        if (rootCount === 0) {
            // Use the fallback approach which is more reliable
            fallbackPositionBasedRootMarking(internalPos);
        }
        
        // Clear the setup flag after a short delay to allow DOM to settle
        setTimeout(() => {
            window.isSettingUpInversions = false;
        }, 200);
    }, 100);
}

/**
 * Ensure that the root note is always marked for the current position
 */
function ensureRootNoteIsMarked(positionName, activePositionData) {

    // Skip if root marking is already in progress
    if (window.rootMarkingInProgress) {
        return;
    }
    
    window.rootMarkingInProgress = true;
    
    // If we already have root notes, don't clear them
    const existingRoots = document.querySelectorAll('img.tone.root');
    if (existingRoots.length > 0) {
        window.rootMarkingInProgress = false;
        return;
    }

    // 1. Check if we have valid data for the active position
    if (!activePositionData || !Array.isArray(activePositionData) || activePositionData.length === 0 || typeof activePositionData[0] !== 'object') {
        console.warn(`No valid activePositionData provided for ${positionName}. Cannot determine root from data.`);
        
        // Fall back to position-based root marking
        fallbackPositionBasedRootMarking(positionName);
        window.rootMarkingInProgress = false;
        return;
    }

    const notes = activePositionData[0];
    let rootFoundInData = false;

    // 3. Iterate through the notes in the active position data
    for (const stringKey in notes) {
        if (notes.hasOwnProperty(stringKey) && stringKey !== 'assigned_strings') { // Exclude metadata key
            const noteData = notes[stringKey]; // Should be [noteName, tension, isAssigned, isRoot]

            // Check if this note is the root according to the backend data
            if (Array.isArray(noteData) && noteData.length >= 4 && noteData[3] === true) {
                const noteNameWithOctave = noteData[0]; // e.g., "c1", "b1"
                // Need to extract the base note name for class selection (e.g., "c", "b")
                // This assumes note names in classes don't include octaves, or we need a more robust selector.
                // Let's assume classes are like '.c', '.b', '.bb', '.as' etc.
                const baseNoteName = noteNameWithOctave.replace(/[0-9#b]/g, '').toLowerCase(); // Basic extraction
                const noteClassSelector = noteNameWithOctave.toLowerCase(); // Use the full name like 'c1' for more specific selection if classes exist like that


                // 4. Find the corresponding DOM element for the *active* note
                // We need to find the specific active note for THIS position, not an alternative inversion note.
                // Selector needs to target the note on the correct string, with the correct class, and ensure it's part of the main active display.
                // This assumes the main active notes do NOT have '.inversion-note' or '.inversion-tone'.
                // Let's try finding the parent .note element first.
                const noteElement = document.querySelector(`.${stringKey} .note.${noteClassSelector}.active:not(.inversion-note)`);

                if (noteElement) {
                    const toneElement = noteElement.querySelector('img.tone');
                    if (toneElement) {
                         // 5. Apply root styling
                         toneElement.classList.add('root');
                         toneElement.src = '/static/media/red_circle.svg';
                         toneElement.style.opacity = '1';
                         toneElement.style.border = '2px solid #CC0000';
                         toneElement.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';

                         // Make the note name visible too
                         const noteNameEl = toneElement.nextElementSibling;
                         if (noteNameEl && noteNameEl.classList.contains('notename')) {
                             noteNameEl.style.visibility = 'visible';
                             noteNameEl.style.opacity = '1';
                             noteNameEl.style.fontWeight = 'bold';
                         }
                         rootFoundInData = true;
                         break; // Found the root, no need to check further notes
                    } else {
                        console.warn(`Could not find img.tone within .note element for ${noteNameWithOctave} on ${stringKey}`);
                    }
                } else {
                    console.warn(`Could not find active .note element for ${noteNameWithOctave} (selector: .${stringKey} .note.${noteClassSelector}.active:not(.inversion-note))`);
                     // Attempt fallback selector without octave if classes are just base notes like '.c'
                     const fallbackNoteElement = document.querySelector(`.${stringKey} .note.${baseNoteName}.active:not(.inversion-note)`);
                     if (fallbackNoteElement) {
                         const toneElement = fallbackNoteElement.querySelector('img.tone');
                         if (toneElement) {
                             toneElement.classList.add('root');
                             toneElement.src = '/static/media/red_circle.svg';
                             toneElement.style.opacity = '1';
                             toneElement.style.border = '2px solid #CC0000';
                             toneElement.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
                             rootFoundInData = true;
                             break;
                         }
                     }
                }
            }
        }
    }

    // 6. Log if no root was found in the data
    if (!rootFoundInData) {
        console.warn(`No note with is_root=true found in the provided data for position ${positionName}. Root note will not be marked based on data.`);
        // Consider if a fallback is truly needed here. If the backend is correct, this shouldn't happen.
        // Calling forceRootNoteMarking() here would re-introduce the original bug.
    }

    // Check final count
    const rootCount = document.querySelectorAll('img.tone.root').length;
}

/**
 * Force the marking of a root note even if none is marked
 * This is a direct implementation that doesn't call ensureRootNoteIsMarked to avoid recursion
 */
function forceRootNoteMarking() {
    // Prevent recursive calls
    if (window.rootMarkingInProgress) {
        return;
    }
    
    // Use a timeout to make sure we don't get stuck in root marking mode
    const rootMarkingTimeout = setTimeout(() => {
        window.rootMarkingInProgress = false;
    }, 1000);
    
    window.rootMarkingInProgress = true;

    // Check if we already have root notes - if so, no need to continue
    const existingRoots = document.querySelectorAll('img.tone.root');
    if (existingRoots.length > 0) {
        window.rootMarkingInProgress = false; // Release the flag
        clearTimeout(rootMarkingTimeout);
        return;
    }

    // Get current range and position information
    const urlParams = new URLSearchParams(window.location.search);
    let currentRange = '';
    if (typeof voicing_data !== 'undefined' && voicing_data && voicing_data.note_range) {
        currentRange = voicing_data.note_range;
    } else {
        currentRange = urlParams.get('note_range') || urlParams.get('range') || (document.getElementById('note_range') ? document.getElementById('note_range').value : 'e - g');
    }
    if (!currentRange || typeof currentRange !== 'string') {
        currentRange = 'e - g';
    }

    const currentPosition = urlParams.get('position_select') || 'Root Position';
    
    // Extract numeric position if needed
    let numericPosition = null;
    if (/^\d+$/.test(currentPosition)) {
        numericPosition = parseInt(currentPosition, 10);
    }
    
    // Map position values
    let internalPosition;
    if (numericPosition === 0 || currentPosition === 'Root Position' || currentPosition.includes('Basic')) {
        internalPosition = 'Basic Position';
    } else if (numericPosition === 2 || currentPosition.includes('First Inv')) {
        internalPosition = 'First Inversion';
    } else if (numericPosition === 3 || currentPosition.includes('Second Inv')) {
        internalPosition = 'Second Inversion';
    } else if (numericPosition === 4 || currentPosition.includes('Third Inv')) {
        internalPosition = 'Third Inversion';
    } else {
        internalPosition = currentPosition;
    }

    // Check for active notes first - if none, we can't mark anything
    const activeNotes = document.querySelectorAll('.note.active');
    if (activeNotes.length === 0) {
        window.rootMarkingInProgress = false;
        clearTimeout(rootMarkingTimeout);
        return;
    }


    // Skip ensureRootNoteIsMarked and go directly to reliable fallback
    fallbackPositionBasedRootMarking(internalPosition);
    
    // Verify root marking worked
    setTimeout(() => {
        const rootCount = document.querySelectorAll('img.tone.root').length;
        if (rootCount === 0) {
            const firstActiveNote = document.querySelector('.note.active img.tone');
            if (firstActiveNote) {
                firstActiveNote.classList.add('root');
                firstActiveNote.src = '/static/media/red_circle.svg';
                firstActiveNote.style.opacity = '1';
                firstActiveNote.style.border = '2px solid #CC0000';
                firstActiveNote.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
                
                // Make parent note element visible
                const noteElement = firstActiveNote.closest('.note');
                if (noteElement) {
                    noteElement.style.opacity = '1';
                    
                    // Make note name visible
                    const noteName = noteElement.querySelector('.notename');
                    if (noteName) {
                        noteName.style.visibility = 'visible';
                        noteName.style.opacity = '1';
                    }
                }
            }
        }
        
        // Clear the root marking flag
        window.rootMarkingInProgress = false;
        clearTimeout(rootMarkingTimeout);
    }, 200);
}
/**
 * Fallback strategy to mark root notes based on position when data isn't available
 */
function fallbackPositionBasedRootMarking(positionName) {
    
    // Determine which string and notes are roots based on position
    let targetString = 'gString';
    let targetNoteNames = ['c', 'c1', 'c2', 'c3', 'c4'];
    
    if (positionName === 'First Inversion') {
        targetString = 'eString';
        targetNoteNames = ['e', 'e1', 'e2', 'e3', 'e4'];
    } else if (positionName === 'Second Inversion') {
        targetString = 'bString';
        targetNoteNames = ['g', 'g1', 'g2', 'g3', 'g4'];
    } else if (positionName === 'Third Inversion') {
        targetString = 'dString';
        targetNoteNames = ['bb', 'bb1', 'bb2', 'bb3', 'bb4', 'as', 'as1', 'as2', 'as3', 'as4'];
    }
    
    
    // Try to find an active note of the target type
    let foundRoot = false;
    for (const noteName of targetNoteNames) {
        const noteSelector = `.${targetString} .note.${noteName}.active:not(.inversion-note)`;
        const noteElement = document.querySelector(noteSelector);
        
        if (noteElement) {
            const toneElement = noteElement.querySelector('img.tone');
            if (toneElement) {
                toneElement.classList.add('root');
                toneElement.src = '/static/media/red_circle.svg';
                toneElement.style.opacity = '1';
                toneElement.style.border = '2px solid #CC0000';
                toneElement.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
                
                // Make note name visible too
                const noteNameEl = noteElement.querySelector('.notename');
                if (noteNameEl) {
                    noteNameEl.style.visibility = 'visible';
                    noteNameEl.style.opacity = '1';
                    noteNameEl.style.fontWeight = 'bold';
                }
                
                foundRoot = true;
                break;
            }
        }
    }
    
    // If no root found on the target string, try any active note
    if (!foundRoot) {
        const anyActiveNote = document.querySelector('.note.active:not(.inversion-note)');
        if (anyActiveNote) {
            const toneElement = anyActiveNote.querySelector('img.tone');
            if (toneElement) {
                toneElement.classList.add('root');
                toneElement.src = '/static/media/red_circle.svg';
                toneElement.style.opacity = '1';
                toneElement.style.border = '2px solid #CC0000';
                toneElement.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
            }
        }
    }
    
    // Final check
    const finalRootCount = document.querySelectorAll('img.tone.root').length;
}

// Note: The helper function markAsRoot is no longer needed within forceRootNoteMarking
// as the logic is now handled by ensureRootNoteIsMarked.

/**
 * Update the visibility and state of inversion navigation buttons
 */
function updateInversionNavigationButtons(hasInversions) {
    const prevButton = document.querySelector('.nav-button.prev-inversion');
    const nextButton = document.querySelector('.nav-button.next-inversion');
    
    if (prevButton && nextButton) {
        // Show buttons if we have inversions, otherwise hide them
        if (hasInversions) {
            prevButton.style.display = 'flex';
            nextButton.style.display = 'flex';
            prevButton.disabled = false;
            nextButton.disabled = false;
            
            // Add event listeners to make sure we refresh root markings
            if (!prevButton.dataset.rootHandlerAdded) {
                prevButton.addEventListener('click', function() {
                    setTimeout(() => {
                        const urlParams = new URLSearchParams(window.location.search);
                        const position = urlParams.get('position_select') || 'Root Position';
                        ensureRootNoteIsMarked(position);
                    }, 200);
                });
                prevButton.dataset.rootHandlerAdded = 'true';
            }
            
            if (!nextButton.dataset.rootHandlerAdded) {
                nextButton.addEventListener('click', function() {
                    setTimeout(() => {
                        const urlParams = new URLSearchParams(window.location.search);
                        const position = urlParams.get('position_select') || 'Root Position';
                        ensureRootNoteIsMarked(position);
                    }, 200);
                });
                nextButton.dataset.rootHandlerAdded = 'true';
            }
        } else {
            prevButton.style.display = 'none';
            nextButton.style.display = 'none';
        }
    }
}
