// Add at the top of the file to avoid reference errors
function diagnoseActiveNotes() {
    
    // Check all strings
    const stringOrder = [
        'lowBString', 'ELowString', 'AString', 'dString', 
        'gString', 'bString', 'eString', 'highAString'
    ];
    
    stringOrder.forEach(stringClass => {
        const allNotes = document.querySelectorAll(`.${stringClass} .note`);
        const activeNotes = document.querySelectorAll(`.${stringClass} .active`);
        const activeImages = document.querySelectorAll(`.${stringClass} .active img.tone`);
        
        
        // If active notes exist, log details about the first one
        if (activeNotes.length > 0) {
            ({
                classes: activeNotes[0].className,
                hasImg: !!activeNotes[0].querySelector('img'),
                imgSrc: activeNotes[0].querySelector('img')?.src || 'none'
            });
        }
    });
    
    // Check if any notes are active at all
    const totalActive = document.querySelectorAll('.active').length;
    
    // Check for inversion notes
    const inversionNotes = document.querySelectorAll('.inversion-note').length;
    
    // Check for root notes
    const rootNotes = document.querySelectorAll('.root').length;
    
}

// Define the fallback function with extra diagnostics
// Fix the fallback function to handle root note marking consistently
function fallbackByStringOrder() {
    
    // String order from lowest to highest
    const stringOrder = [
        'lowBString', 'ELowString', 'AString', 'dString',
        'gString', 'bString', 'eString', 'highAString'
    ];
    
    // First try to find C notes specifically (the actual root)
    for (const stringClass of stringOrder) {
        // Look for any C note that's active
        const cNotes = document.querySelectorAll(
            `.${stringClass} .active .note.c1, .${stringClass} .note.c1.active, .${stringClass} .active img.tone.c1`
        );
        
        if (cNotes.length > 0) {
            // Process the C note
            const noteElement = cNotes[0];
            const imgElement = noteElement.tagName === 'IMG' ?
                noteElement : noteElement.querySelector('img.tone');
            
            if (imgElement) {
                // Mark as root
                imgElement.classList.add('root');
                imgElement.src = imgElement.src.replace('yellow_circle.svg', 'red_circle.svg');
                imgElement.style.opacity = '1';
                imgElement.style.border = '2px solid rgb(204, 0, 0)';
                imgElement.style.boxShadow = 'rgba(255, 0, 0, 0.3) 0px 0px 5px';
                
                return;
            }
        }
    }
    
    // If no C note found, try based on string order (lowest string first)
    for (const stringClass of stringOrder) {
        // Get all active notes, even if they're inversion notes
        const activeNotes = document.querySelectorAll(
            `.${stringClass} .active`
        );
        
        if (activeNotes.length > 0) {
            // Look for the img element inside - from diagnostics we know it's a child element
            let imgElement;
            
            // First try to find the lowBString c1 note specifically
            if (stringClass === 'lowBString') {
                const c1Notes = Array.from(activeNotes).filter(el =>
                    el.classList.contains('c1') || el.querySelector('.c1')
                );
                
                if (c1Notes.length > 0) {
                    imgElement = c1Notes[0].querySelector('img.tone');
                }
            }
            
            // If no C1 found, use the first active note
            if (!imgElement) {
                imgElement = activeNotes[0].querySelector('img.tone');
            }
            
            if (imgElement) {
                // Mark as root
                imgElement.classList.add('root');
                imgElement.src = imgElement.src.replace('yellow_circle.svg', 'red_circle.svg');
                imgElement.style.opacity = '1';
                imgElement.style.border = '2px solid rgb(204, 0, 0)';
                imgElement.style.boxShadow = 'rgba(255, 0, 0, 0.3) 0px 0px 5px';
                
                return;
            }
        }
    }
    
}

// Add a dedicated function to consistently mark root notes
function markAsRoot(imgElement) {
    // Ensure the element has the root class
    imgElement.classList.add('root');
    
    // Change the image source to red
    if (imgElement.src && imgElement.src.includes('yellow_circle.svg')) {
        imgElement.src = imgElement.src.replace('yellow_circle.svg', 'red_circle.svg');
    }
    
    // Apply consistent styling
    imgElement.style.opacity = '1';
    imgElement.style.visibility = 'visible';
    imgElement.style.border = '2px solid rgb(204, 0, 0)';
    imgElement.style.boxShadow = 'rgba(255, 0, 0, 0.3) 0px 0px 5px';
    
    // Make sure the parent element is also marked appropriately
    if (imgElement.parentElement) {
        // If parent is a note element, make sure it's visible too
        if (imgElement.parentElement.classList.contains('note')) {
            imgElement.parentElement.style.opacity = '1';
            imgElement.parentElement.style.visibility = 'visible';
        }
        
        // Find and style the note name element
        const noteNameElement = imgElement.parentElement.querySelector('.notename');
        if (noteNameElement) {
            noteNameElement.style.visibility = 'visible';
            noteNameElement.style.opacity = '1';
            noteNameElement.style.fontWeight = 'bold';
            noteNameElement.style.color = '#000';
        }
    }
}

// Then define the main function to fix root notes
// Define the main function with simplified logic
let isUpdatingNoteVisibility = false;
let isFixingRootNotes = false;

function updateNoteNameVisibility() {
    
    // Prevent recursive calls
    if (isUpdatingNoteVisibility) {
        return;
    }
    
    isUpdatingNoteVisibility = true;
    
    try {
        // First ensure non-active notes are hidden
        document.querySelectorAll('.note:not(.active)').forEach(noteEl => {
            const nameEl = noteEl.querySelector('.notename');
            if (nameEl) {
                nameEl.style.visibility = 'hidden';
                nameEl.style.opacity = '0';
            }
            
            // Also ensure tone visibility matches note visibility
            const toneEl = noteEl.querySelector('img.tone');
            if (toneEl && !toneEl.classList.contains('active')) {
                toneEl.style.visibility = 'hidden';
                toneEl.style.opacity = '0';
            }
        });
        
        // Get all note name elements
        const allNoteNames = document.querySelectorAll('.notename');
        const activeNotes = document.querySelectorAll('.note.active');
        const inversionNotes = document.querySelectorAll('.inversion-note');
        
        // First pass: Make all note names for active notes visible
        activeNotes.forEach(noteEl => {
            const nameEl = noteEl.querySelector('.notename');
            if (nameEl) {
                nameEl.style.visibility = 'visible';
                nameEl.style.display = 'block';
                
                // The current position should have full opacity
                if (!noteEl.classList.contains('inversion-note')) {
                    nameEl.style.opacity = '1';
                } else {
                    // Inversion notes should be semi-transparent
                    nameEl.style.opacity = '0.4';
                }
            }
            
            // Also ensure tone is visible
            const toneEl = noteEl.querySelector('img.tone');
            if (toneEl) {
                toneEl.style.visibility = 'visible';
                toneEl.style.opacity = '1';
                
                // Non-root notes get yellow circles
                if (!toneEl.classList.contains('root')) {
                    toneEl.src = '/static/media/yellow_circle.svg';
                }
            }
        });
        
        // Make sure root note names are always visible
        const rootNotes = document.querySelectorAll('img.root, img.tone.root');
        rootNotes.forEach(rootImg => {
            const noteEl = rootImg.closest('.note');
            const nameEl = noteEl ? noteEl.querySelector('.notename') : null;
            
            if (nameEl) {
                nameEl.style.visibility = 'visible';
                nameEl.style.opacity = '1';
                nameEl.style.fontWeight = 'bold';
                nameEl.style.display = 'block';
            }
            
            // Make sure root image is properly styled
            rootImg.style.visibility = 'visible';
            rootImg.style.opacity = '1';
            rootImg.src = '/static/media/red_circle.svg';
        });
        
    } finally {
        // Reset the flag after a delay to prevent frequent updates
        setTimeout(() => {
            isUpdatingNoteVisibility = false;
        }, 100);
    }
}

function fixRootNoteMarking(position) {
    // Prevent recursive calls
    if (isFixingRootNotes) {
        return;
    }
    
    isFixingRootNotes = true;
    
    // Clear existing root markings
    document.querySelectorAll('.root').forEach(el => {
        el.classList.remove('root');
        if (el.src && el.src.includes('red_circle.svg')) {
            el.src = el.src.replace('red_circle.svg', 'yellow_circle.svg');
        }
    });
    
    // Go straight to fallback since we know the structure from diagnostics
    fallbackByStringOrder();
    
    // Wait a bit before updating note visibility to avoid triggering more mutations
    setTimeout(() => {
        updateNoteNameVisibility();
        isFixingRootNotes = false;
    }, 50);
}

// Add function for deeper diagnosis of note visibility
function diagnoseNoteNameVisibility() {
    
    // Check active notes and their note names
    const activeNotes = document.querySelectorAll('.active');
    
    if (activeNotes.length > 0) {
        // Check a sample of active notes
        for (let i = 0; i < Math.min(5, activeNotes.length); i++) {
            const note = activeNotes[i];
            const noteName = note.querySelector('.notename');
            
            ({
                classes: note.className,
                parentClasses: note.parentElement?.className || 'no parent',
                hasNoteName: !!noteName,
                noteNameVisible: noteName ? getComputedStyle(noteName).visibility : 'N/A',
                noteNameOpacity: noteName ? getComputedStyle(noteName).opacity : 'N/A',
                noteNameDisplay: noteName ? getComputedStyle(noteName).display : 'N/A',
                noteNameHTML: noteName ? noteName.outerHTML : 'N/A'
            });
        }
        
        // Force visibility on all note names in the DOM
        document.querySelectorAll('.notename').forEach(nameEl => {
            nameEl.style.visibility = 'visible';
            nameEl.style.opacity = '1';
            nameEl.style.display = 'block';
        });
        
    }
    
}

// Add cursor click functions that integrate with the cursor management system
function setupCursorControls() {
    
    // Listen for the cursor-navigation-complete event that's dispatched by cursor_management.js
    document.addEventListener('cursor-navigation-complete', function(e) {
        
        // Use a longer timeout to ensure all other code has run
        setTimeout(() => {
            // Find all active notes and update their visibility
            const activeNotes = document.querySelectorAll('.note.active');
            const inversionNotes = document.querySelectorAll('.note.active.inversion-note');
            
            // Make regular active notes fully visible
            activeNotes.forEach(note => {
                if (!note.classList.contains('inversion-note')) {
                    note.style.opacity = '1';
                    
                    // Find and make the note name visible
                    const noteName = note.querySelector('.notename');
                    if (noteName) {
                        noteName.style.visibility = 'visible';
                        noteName.style.opacity = '1';
                    }
                }
            });
            
            // Make inversion notes semi-transparent
            inversionNotes.forEach(note => {
                note.style.opacity = '0.6';
                
                // Find and make the note name semi-transparent
                const noteName = note.querySelector('.notename');
                if (noteName) {
                    noteName.style.visibility = 'visible';
                    noteName.style.opacity = '0.4';
                }
            });
            
            // Make root notes always visible
            const rootNotes = document.querySelectorAll('img.root, img.tone.root');
            rootNotes.forEach(rootImg => {
                rootImg.style.opacity = '1';
                rootImg.style.visibility = 'visible';
                
                // Find the parent note element
                const noteEl = rootImg.closest('.note');
                if (noteEl) {
                    // Find and make the note name visible
                    const nameEl = noteEl.querySelector('.notename');
                    if (nameEl) {
                        nameEl.style.visibility = 'visible';
                        nameEl.style.opacity = '1';
                        nameEl.style.fontWeight = 'bold';
                    }
                }
            });
            
        }, 300);
    });
    
    // Dispatch the event once to ensure initial visibility is correct
    setTimeout(() => {
        document.dispatchEvent(new CustomEvent('cursor-navigation-complete'));
    }, 1000);
}

// Attach to MutationObserver to handle timing issues
function setupRootObserver() {
    // Only set up once
    if (window.rootObserverActive) return;
    window.rootObserverActive = true;
    
    
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0 || mutation.attributeName === 'class') {
                updateNoteNameVisibility();
            }
        });
    });
    
    // Observe the entire document for changes to class attributes
    observer.observe(document.body, { 
        attributes: true, 
        childList: true, 
        subtree: true, 
        attributeFilter: ['class'] 
    });
}

// Add a dedicated function to properly handle root notes during position changes
function updateRootNotes(position) {
    
    // FIXED: Only clear root markings if we're sure we can add them back
    // Check if we have active notes first
    const activeNotes = document.querySelectorAll('.note.active');
    if (activeNotes.length === 0) {
        return;
    }
    
    // Store original root notes for recovery if needed
    const originalRootNotes = document.querySelectorAll('img.root, img.tone.root, img.inversion-root');
    const originalRootData = Array.from(originalRootNotes).map(rootImg => {
        const noteEl = rootImg.closest('.note');
        return {
            element: rootImg,
            classes: rootImg.className,
            src: rootImg.src,
            opacity: rootImg.style.opacity,
            border: rootImg.style.border,
            boxShadow: rootImg.style.boxShadow,
            parentClasses: noteEl ? noteEl.className : ''
        };
    });
    
    // Now clear root markings conditionally
    const allRootNotes = document.querySelectorAll('img.root, img.tone.root, img.inversion-root');
    
    allRootNotes.forEach(rootImg => {
        // Remove root class
        rootImg.classList.remove('root');
        
        // Remove data-root-for attribute
        rootImg.removeAttribute('data-root-for');
        
        // Remove styling
        rootImg.style.opacity = '';
        rootImg.style.border = '';
        rootImg.style.boxShadow = '';
        
        // Also clear inversion-root if present
        if (rootImg.classList.contains('inversion-root')) {
            rootImg.classList.remove('inversion-root');
        }
        
        // Reset the note name styling
        const noteEl = rootImg.closest('.note');
        if (noteEl) {
            const nameEl = noteEl.querySelector('.notename');
            if (nameEl) {
                nameEl.style.fontWeight = '';
            }
        }
    });
    
    // Then find and mark the proper root notes for the current position
    // For Basic Position/Root Position, we mark notes with the root note name
    // For inversions, we mark notes based on their position in the chord
    const internalPosition = position === 'Root Position' ? 'Basic Position' : position;
    
    // Track if we successfully marked any root notes
    let rootsMarked = false;
    
    // Get root note info from the voicing data if available
    if (window.voicing_data) {
        const range = getCurrentRange();
        if (window.voicing_data[range] && window.voicing_data[range][internalPosition]) {
            const positionData = window.voicing_data[range][internalPosition];
            
            // Handle both array and object formats of voicing data
            if (Array.isArray(positionData)) {
                positionData.forEach(noteData => {
                    const success = markRootNotesFromData(noteData, position);
                    if (success) rootsMarked = true;
                });
            } else {
                const success = markRootNotesFromData(positionData, position);
                if (success) rootsMarked = true;
            }
        }
    }
    
    // If we didn't successfully mark any root notes, use fallback
    if (!rootsMarked) {
        fallbackByStringOrder();
        
        // Check if fallback worked
        const rootsAfterFallback = document.querySelectorAll('img.root, img.tone.root');
        if (rootsAfterFallback.length === 0 && originalRootData && originalRootData.length > 0) {
            // Restore original root markings as last resort
            
            originalRootData.forEach(rootInfo => {
                const element = rootInfo.element;
                if (element) {
                    // Restore root class
                    element.classList.add('root');
                    
                    // Restore styling
                    element.src = rootInfo.src;
                    element.style.opacity = rootInfo.opacity || '1';
                    element.style.border = rootInfo.border || '2px solid #CC0000';
                    element.style.boxShadow = rootInfo.boxShadow || '0 0 5px rgba(255, 0, 0, 0.3)';
                }
            });
        }
    }
    
    // Update visibility for all notes
    updateNoteNameVisibility();
    
    // Count and log the number of root notes
    const newRootNotes = document.querySelectorAll('img.root, img.tone.root, img.inversion-root');
}

// Helper function to mark root notes based on voicing data
function markRootNotesFromData(noteData, position) {
    if (!noteData) return false;
    
    let success = false;
    
    // Handle the case where assigned_strings might not exist
    // First check if we have normal string data
    if (!noteData.assigned_strings) {
        // Try to find any string data directly
        const stringKeys = Object.keys(noteData).filter(key => 
            key.includes('String') || ['eString', 'bString', 'gString', 'dString', 'aString', 'EString', 'AString', 'lowBString', 'highAString'].includes(key)
        );
        
        if (stringKeys.length > 0) {
            
            // Process each string found
            for (const stringName of stringKeys) {
                const stringData = noteData[stringName];
                if (!stringData) continue;
                
                // For simpler data structure, check if this is a root for this position
                let isRoot = false;
                
                // Check array format
                if (Array.isArray(stringData)) {
                    isRoot = stringData.includes('R') || stringData.includes('Root');
                    
                    // Also check position-specific logic
                    if (!isRoot) {
                        // For first position/root position/basic position, C notes are roots
                        if ((position === 'Root Position' || position === 'Basic Position') && 
                            stringData[0] && stringData[0].toLowerCase().startsWith('c')) {
                            isRoot = true;
                        }
                        // For first inversion, E notes are roots
                        else if (position === 'First Inversion' && 
                                stringData[0] && stringData[0].toLowerCase().startsWith('e')) {
                            isRoot = true;
                        }
                        // For second inversion, G notes are roots
                        else if (position === 'Second Inversion' && 
                                stringData[0] && stringData[0].toLowerCase().startsWith('g')) {
                            isRoot = true;
                        }
                    }
                    
                    if (isRoot) {
                        
                        // Try to find this note on the fretboard
                        const noteName = stringData[0];
                        const baseNote = noteName.replace(/[0-9]/g, '').toLowerCase();
                        
                        // Find by exact note name first, then by base note
                        let noteElements = document.querySelectorAll(`.${stringName} .note.${noteName.toLowerCase()}`);
                        if (noteElements.length === 0) {
                            noteElements = document.querySelectorAll(`.${stringName} .note.${baseNote}`);
                        }
                        
                        // If we found matching elements, mark them as roots
                        if (noteElements.length > 0) {
                            noteElements.forEach(noteEl => {
                                const imgElement = noteEl.querySelector('img.tone');
                                if (imgElement) {
                                    markAsRoot(imgElement);
                                    imgElement.setAttribute('data-root-for', position);
                                    
                                    if (position !== 'Basic Position' && position !== 'Root Position') {
                                        imgElement.classList.add('inversion-root');
                                    }
                                    success = true;
                                }
                            });
                        }
                    }
                }
            }
            
            return success;
        }
        
        // If we didn't find any string keys, return false
        return false;
    }
    
    // Handle the normal case with assigned_strings
    // Iterate through each string in the note data
    noteData.assigned_strings.forEach(stringName => {
        const stringData = noteData[stringName];
        if (!stringData) return;
        
        // Check if this note is marked as a root note - accept various formats
        let isRoot = false;
        
        if (Array.isArray(stringData)) {
            isRoot = stringData.includes('R') || stringData.includes('Root');
            
            // Also handle case with explicit flag
            if (stringData.length >= 3 && stringData[2] === true && 
                (stringData[1] === 'R' || stringData[1] === 'Root')) {
                isRoot = true;
            }
            
            // Also check position-specific logic as a fallback
            if (!isRoot) {
                // For first position/root position/basic position, C notes are roots
                if ((position === 'Root Position' || position === 'Basic Position') && 
                    stringData[0] && stringData[0].toLowerCase().startsWith('c')) {
                    isRoot = true;
                }
                // For first inversion, E notes are roots
                else if (position === 'First Inversion' && 
                        stringData[0] && stringData[0].toLowerCase().startsWith('e')) {
                    isRoot = true;
                }
                // For second inversion, G notes are roots
                else if (position === 'Second Inversion' && 
                        stringData[0] && stringData[0].toLowerCase().startsWith('g')) {
                    isRoot = true;
                }
            }
        }
        
        if (isRoot) {
            
            // Get the note name
            const noteName = stringData[0];
            const baseNote = noteName.replace(/[0-9]/g, '').toLowerCase();
            
            // Find by exact note name first, then by base note
            let noteElements = document.querySelectorAll(`.${stringName} .note.${noteName.toLowerCase()}`);
            if (noteElements.length === 0) {
                noteElements = document.querySelectorAll(`.${stringName} .note.${baseNote}`);
            }
            
            // If we found matching elements, mark them as roots
            if (noteElements.length > 0) {
                noteElements.forEach(noteEl => {
                    const imgElement = noteEl.querySelector('img.tone');
                    if (imgElement) {
                        markAsRoot(imgElement);
                        imgElement.setAttribute('data-root-for', position);
                        
                        if (position !== 'Basic Position' && position !== 'Root Position') {
                            imgElement.classList.add('inversion-root');
                        }
                        success = true;
                    }
                });
            }
        }
    });
    
    return success;
}

// Get the current range from URL or defaults
function getCurrentRange() {
    if (window.voicing_data && window.voicing_data.note_range) {
        return window.voicing_data.note_range;
    }
    
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('note_range') || 'e - g';
}

// Add initialization flag to prevent multiple initializations
let chordInversionsFixedInitialized = false;

// Initialize as soon as possible
document.addEventListener('DOMContentLoaded', () => {
    if (chordInversionsFixedInitialized) {
        return;
    }
    
    chordInversionsFixedInitialized = true;
    
    // Delay setup to ensure fretboard and other components are initialized first
    setTimeout(() => {
        // Set up cursor controls
        setupCursorControls();
        
        // Check for active notes
        diagnoseActiveNotes(); // Diagnostic only - will not mark roots
        
        // Ensure we have at least one root note marked
        const rootNotes = document.querySelectorAll('img.tone.root');
        if (rootNotes.length === 0) {
            
            // Get current position
            const urlParams = new URLSearchParams(window.location.search);
            const position = urlParams.get('position_select') || 'Root Position';
            
            // Fix root notes after a short delay
            setTimeout(() => {
                fixRootNoteMarking(position);
                updateNoteNameVisibility();
            }, 200);
        }
    }, 700); // Wait for other initializations to complete
});
