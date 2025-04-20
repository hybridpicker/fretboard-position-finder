/**
 * Cursor Note Display Fix
 * 
 * This script fixes issues with note visibility and styling when navigating
 * chord inversions using the left and right cursor controls.
 */

// Track the last time we applied fixes to avoid duplicate fixes
window.lastFixTime = 0;
const FIX_COOLDOWN_MS = 200; // Minimum time between applying fixes

/**
 * Applies all display fixes with debouncing to prevent multiple rapid updates
 */
function applyDisplayFixes(source) {
    const now = Date.now();
    // If it's too soon after the last fix, schedule it for later
    if ((now - window.lastFixTime) < FIX_COOLDOWN_MS) {
        console.log(`Fix requested from ${source}, but deferring due to cooldown`);
        setTimeout(() => applyDisplayFixes(`${source} (deferred)`), FIX_COOLDOWN_MS);
        return;
    }
    
    console.log(`Applying display fixes (source: ${source})...`);
    window.lastFixTime = now;
    
    // Apply all fixes in sequence
    // Only reset display if needed (the function has internal protection now)
    resetNoteDisplay();
    
    // Make sure all chord notes are properly displayed
    ensureChordNotesDisplayed();
    
    // Fix root note styling
    fixRootNoteDisplay();
    
    // Hide notenames that should be hidden
    hideInactiveNoteNames();
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Loading cursor note display fix...');

    // Listen for chord-tones-updated event which fires after position changes
    document.addEventListener('chord-tones-updated', function(event) {
        // Use longer delay for this event as it might be fired first
        setTimeout(() => applyDisplayFixes('chord-tones-updated'), 75);
    });

// Add a global debug function for the cursor note display fix
window.debugCursorNoteDisplay = function() {
    console.log('========== CURSOR NOTE DISPLAY DEBUG ==========');
    console.log('Active notes:', document.querySelectorAll('.note.active').length);
    console.log('Active tone images:', document.querySelectorAll('img.tone.active').length);
    console.log('Root notes:', document.querySelectorAll('img.tone.root').length);
    console.log('Visible notenames:', document.querySelectorAll('.notename[style*="visibility: visible"]').length);
    
    // Check if fix functions are available
    console.log('Fix functions available:',
        'resetNoteDisplay: ' + (typeof resetNoteDisplay === 'function'),
        'fixRootNoteDisplay: ' + (typeof fixRootNoteDisplay === 'function'),
        'hideInactiveNoteNames: ' + (typeof hideInactiveNoteNames === 'function'),
        'ensureChordNotesDisplayed: ' + (typeof ensureChordNotesDisplayed === 'function'),
        'applyDisplayFixes: ' + (typeof applyDisplayFixes === 'function')
    );
    
    // Check timings
    console.log('Last reset time:', new Date(window.lastResetTime).toISOString());
    console.log('Last fix time:', new Date(window.lastFixTime).toISOString());
    console.log('Current time:', new Date().toISOString());
    console.log('Time since last reset:', Date.now() - window.lastResetTime, 'ms');
    console.log('Time since last fix:', Date.now() - window.lastFixTime, 'ms');
    
    // Run fixes again if requested
    if (arguments[0] === true) {
        console.log('Reapplying display fixes...');
        applyDisplayFixes('manual debug call');
        
        // Check results after a short delay
        setTimeout(function() {
            console.log('========== AFTER MANUAL FIX ==========');
            console.log('Active notes:', document.querySelectorAll('.note.active').length);
            console.log('Active tone images:', document.querySelectorAll('img.tone.active').length);
            console.log('Root notes:', document.querySelectorAll('img.tone.root').length);
            console.log('Visible notenames:', document.querySelectorAll('.notename[style*="visibility: visible"]').length);
        }, 100);
    }
    
    return 'Debug complete. Call with true argument to reapply fixes: window.debugCursorNoteDisplay(true)';
};

// Expose key functions globally
window.resetNoteDisplay = resetNoteDisplay;
window.fixRootNoteDisplay = fixRootNoteDisplay;
window.hideInactiveNoteNames = hideInactiveNoteNames;
window.ensureChordNotesDisplayed = ensureChordNotesDisplayed;
window.applyDisplayFixes = applyDisplayFixes;
    
    // Also listen for the chord-position-changed event from chord-cursor-fix.js
    document.addEventListener('chord-position-changed', function(event) {
        // This event might fire close to the others, so use debouncing
        applyDisplayFixes('chord-position-changed');
    });
    
    // Listen for chord-inversion-navigated event from cursor-inversion.js
    document.addEventListener('chord-inversion-navigated', function(event) {
        // This event might fire along with position-changed
        applyDisplayFixes('chord-inversion-navigated');
    });

        // Also run on initial page load
    setTimeout(() => applyDisplayFixes('initial page load'), 500);
    
    // Add periodic check to ensure our fixes are running
    setInterval(function() {
        // Look for any missing note displays
        const activeNotesCount = document.querySelectorAll('.note.active').length;
        const activeToneImagesCount = document.querySelectorAll('img.tone.active').length;
        
        // If we have active notes but they're not showing properly
        if (activeNotesCount > 0 && activeNotesCount !== activeToneImagesCount) {
            console.log('Detected note display inconsistency, reapplying fixes...');
            applyDisplayFixes('periodic check');
        }
    }, 2000); // Check every 2 seconds

    // Fix the leftCursorClick and rightCursorClick functions to include display cleanup
    if (typeof window.originalLeftCursorClick === 'undefined' && typeof leftCursorClick === 'function') {
        // Save original function
        window.originalLeftCursorClick = leftCursorClick;
        
        // Override with improved version
        window.leftCursorClick = function() {
            // Clear all note styling first
            resetNoteDisplay();
            
            // Call original function
            window.originalLeftCursorClick.apply(this, arguments);
            
            // Apply additional fixes after a short delay
            setTimeout(function() {
                fixRootNoteDisplay();
                hideInactiveNoteNames();
            }, 100);
        };

        console.log('Overrode leftCursorClick with fixed version');
    }

    if (typeof window.originalRightCursorClick === 'undefined' && typeof rightCursorClick === 'function') {
        // Save original function
        window.originalRightCursorClick = rightCursorClick;
        
        // Override with improved version
        window.rightCursorClick = function() {
            // Clear all note styling first
            resetNoteDisplay();
            
            // Call original function
            window.originalRightCursorClick.apply(this, arguments);
            
            // Apply additional fixes after a short delay
            setTimeout(function() {
                fixRootNoteDisplay();
                hideInactiveNoteNames();
            }, 100);
        };

        console.log('Overrode rightCursorClick with fixed version');
    }
});

// Track when the last reset was performed to avoid excessive resets
window.lastResetTime = 0;
const RESET_COOLDOWN_MS = 300; // Minimum time between resets

/**
 * Resets all note display properties to prepare for showing a new chord
 * Modified to avoid excessive resets and preserve active notes during navigation
 */
function resetNoteDisplay() {
    // Check if we've reset too recently - if so, skip this reset
    const now = Date.now();
    if ((now - window.lastResetTime) < RESET_COOLDOWN_MS) {
        console.log('Skipping reset - too soon after previous reset');
        return;
    }
    
    console.log('Resetting note display...');
    window.lastResetTime = now;
    
    // Store active notes before reset to preserve them
    const activeNoteElements = [];
    document.querySelectorAll('.note.active').forEach(function(noteElement) {
        activeNoteElements.push(noteElement);
    });
    
    // Only reset inactive notes
    document.querySelectorAll('.note:not(.active)').forEach(function(noteElement) {
        // Reset note container styling
        noteElement.style.opacity = '';
        
        // Reset the tone (circle) image
        const toneImg = noteElement.querySelector('img.tone');
        if (toneImg) {
            toneImg.style.opacity = '';
            toneImg.style.border = '';
            toneImg.style.boxShadow = '';
            toneImg.style.visibility = '';
            
            // Reset image source if data attribute exists
            const noteName = toneImg.getAttribute('data-note-name');
            if (noteName) {
                // Get base octave from note name (e.g. c3 -> 3)
                const octaveMatch = noteName.match(/[a-z]+([0-4])/);
                if (octaveMatch && octaveMatch[1]) {
                    // Use yellow circle for non-root notes
                    toneImg.src = '/static/media/yellow_circle.svg';
                }
            } else {
                // Default to yellow circle
                toneImg.src = '/static/media/yellow_circle.svg';
            }
        }
        
        // Reset the notename element
        const notename = noteElement.querySelector('.notename');
        if (notename) {
            notename.style.visibility = 'hidden';
            notename.style.opacity = '0';
            notename.style.fontWeight = '';
            notename.classList.remove('active');
            notename.classList.remove('show-name');
        }
    });
    
    // If no active notes remain (complete reset requested), reactivate stored notes
    const currentActive = document.querySelectorAll('.note.active');
    if (currentActive.length === 0 && activeNoteElements.length > 0) {
        console.log('Reactivating stored notes after reset');
        activeNoteElements.forEach(function(noteElement) {
            noteElement.classList.add('active');
            
            // Reactivate the tone image 
            const toneImg = noteElement.querySelector('img.tone');
            if (toneImg) {
                toneImg.classList.add('active');
                toneImg.style.opacity = '1';
            }
        });
    }
}

/**
 * Fixes root note display styling
 */
function fixRootNoteDisplay() {
    console.log('Fixing root note display...');
    
    // First check for elements explicitly marked as root
    let rootFound = false;
    let activeToneFound = false;
    
    // First ensure all active tones are visible
    document.querySelectorAll('img.tone.active').forEach(function(activeTone) {
        activeToneFound = true;
        activeTone.style.opacity = '1';
        activeTone.style.visibility = 'visible';
        
        // Make sure parent note element is active
        const noteElement = activeTone.closest('.note');
        if (noteElement) {
            noteElement.classList.add('active');
        }
    });
    
    // 1. Check for data-is-root attribute
    document.querySelectorAll('img.tone[data-is-root="true"]').forEach(function(rootTone) {
        rootFound = true;
        applyRootStyling(rootTone);
    });
    
    // 2. Check for elements with .root class
    document.querySelectorAll('img.tone.root').forEach(function(rootTone) {
        rootFound = true;
        applyRootStyling(rootTone);
    });
    
    // 3. Check for elements with red circle src
    document.querySelectorAll('img.tone[src*="red_circle"]').forEach(function(rootTone) {
        rootFound = true;
        applyRootStyling(rootTone);
    });
    
    // If no root was found, try to find canonical root note based on data attributes
    if (!rootFound) {
        // Look for notes with canonical name C (typical root note)
        document.querySelectorAll('img.tone[data-canonical-name="C"]').forEach(function(potentialRootTone) {
            if (!rootFound && potentialRootTone.closest('.note.active')) {
                applyRootStyling(potentialRootTone);
                rootFound = true;
            }
        });
        
        // If still no root found, try other canonical names
        if (!rootFound) {
            // Look for any active tone with a canonical name attribute
            document.querySelectorAll('img.tone.active[data-canonical-name]').forEach(function(toneTone) {
                if (!rootFound) {
                    applyRootStyling(toneTone);
                    rootFound = true;
                }
            });
        }
        
        // If still no root found, use the first active tone
        if (!rootFound && activeToneFound) {
            const firstActiveTone = document.querySelector('img.tone.active');
            if (firstActiveTone) {
                applyRootStyling(firstActiveTone);
                rootFound = true;
            }
        }
    }
    
    // Handle all active notes
    document.querySelectorAll('img.tone.active').forEach(function(activeTone) {
        // Make sure the active notes are visible
        activeTone.style.opacity = '1';
        
        // Find parent note element
        const noteElement = activeTone.closest('.note');
        if (noteElement) {
            noteElement.classList.add('active');
        }
    });
}

/**
 * Helper function to apply root note styling to an element
 */
function applyRootStyling(rootTone) {
    // Apply root styling
    rootTone.classList.add('root');
    rootTone.classList.add('active');
    rootTone.src = '/static/media/red_circle.svg';
    rootTone.style.opacity = '1';
    rootTone.style.border = '2px solid rgb(204, 0, 0)';
    rootTone.style.boxShadow = 'rgba(255, 0, 0, 0.3) 0px 0px 5px';
    
    // Find parent note element
    const noteElement = rootTone.closest('.note');
    if (noteElement) {
        noteElement.classList.add('active');
        
        // Make the notename visible for root notes
        const notename = noteElement.querySelector('.notename');
        if (notename) {
            notename.style.visibility = 'visible';
            notename.style.opacity = '1';
            notename.style.fontWeight = 'bold';
            notename.classList.add('show-name');
            notename.classList.add('active');
        }
    }
}

/**
 * Ensures all active notes from the chord are displayed properly
 */
function ensureChordNotesDisplayed() {
    console.log('Ensuring all chord notes are displayed...');
    
    // Look for active tones that should be visible
    const activeTones = document.querySelectorAll('img.tone.active');
    
    if (activeTones.length === 0) {
        // If we don't find any active tones, look for voicing data to determine which should be active
        if (window.voicing_data) {
            // Extract current position and range from URL
            const urlParams = new URLSearchParams(window.location.search);
            const currentPosition = urlParams.get('position_select') || 'Root Position';
            const currentRange = urlParams.get('note_range') || 'e - g';
            
            try {
                // Get position data
                let positionName = currentPosition;
                if (positionName === 'Root Position') {
                    positionName = 'Basic Position';
                }
                
                // Try to get voicing data for this position
                if (window.voicing_data[currentRange] && 
                    window.voicing_data[currentRange][positionName]) {
                    
                    let positionData = window.voicing_data[currentRange][positionName];
                    if (Array.isArray(positionData)) {
                        positionData = positionData[0];
                    }
                    
                    // Make missing notes visible
                    for (const stringName in positionData) {
                        if (!positionData.hasOwnProperty(stringName)) continue;
                        
                        const noteData = positionData[stringName];
                        let noteName = '';
                        let isRoot = false;
                        
                        if (Array.isArray(noteData)) {
                            noteName = noteData[0].toLowerCase();
                            isRoot = noteData.includes('R') || noteData.includes('Root');
                        } else if (typeof noteData === 'string') {
                            noteName = noteData.toLowerCase();
                        } else {
                            continue;
                        }
                        
                        // Find the note element for this string
                        const noteSelector = `.${stringName} .note.${noteName.replace(/[0-9]/g, '')}`;
                        const noteElements = document.querySelectorAll(noteSelector);
                        
                        noteElements.forEach(function(noteElement) {
                            // Make the note active
                            noteElement.classList.add('active');
                            
                            // Find and activate the tone
                            const toneEl = noteElement.querySelector('img.tone');
                            if (toneEl) {
                                toneEl.classList.add('active');
                                toneEl.style.opacity = '1';
                                
                                // Mark root if needed
                                if (isRoot) {
                                    toneEl.classList.add('root');
                                    toneEl.src = '/static/media/red_circle.svg';
                                    
                                    // Show note name for root
                                    const noteNameEl = noteElement.querySelector('.notename');
                                    if (noteNameEl) {
                                        noteNameEl.style.visibility = 'visible';
                                        noteNameEl.style.opacity = '1';
                                        noteNameEl.classList.add('active');
                                        noteNameEl.classList.add('show-name');
                                    }
                                }
                            }
                        });
                    }
                    
                    console.log(`Activated notes from voicing data for ${currentPosition}`);
                }
            } catch (error) {
                console.error('Error reactivating notes from voicing data:', error);
            }
        }
    } else {
        // Make sure all active tones are visible
        activeTones.forEach(function(toneEl) {
            toneEl.style.opacity = '1';
            
            // Find parent note element
            const noteElement = toneEl.closest('.note');
            if (noteElement) {
                noteElement.classList.add('active');
                
                // Show note name for root elements
                if (toneEl.classList.contains('root') || 
                    toneEl.src.includes('red_circle')) {
                    
                    const noteNameEl = noteElement.querySelector('.notename');
                    if (noteNameEl) {
                        noteNameEl.style.visibility = 'visible';
                        noteNameEl.style.opacity = '1';
                        noteNameEl.classList.add('active');
                        noteNameEl.classList.add('show-name');
                    }
                }
            }
        });
    }
}

/**
 * Hides notenames that should be hidden
 */
function hideInactiveNoteNames() {
    console.log('Hiding inactive note names...');
    
    // Find all notename elements that are not in an active note
    document.querySelectorAll('.notename').forEach(function(notename) {
        const noteElement = notename.closest('.note');
        if (!noteElement || !noteElement.classList.contains('active')) {
            notename.style.visibility = 'hidden';
            notename.style.opacity = '0';
            notename.classList.remove('show-name');
        }
    });
}
