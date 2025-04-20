/**
 * Simple Cursor Navigation Fix
 * Tracks active notes between inversions to ensure clean transitions
 */

// Store state for the current chord display
let currentActiveNotes = [];
let isNavigating = false;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Loading simple cursor navigation fix...');
    
    // Override the cursor click functions if available
    overrideCursorFunctions();
    
    // Add event listeners for navigation events
    setupNavigationListeners();
    
    // Initial fix after page is loaded
    setTimeout(function() {
        ensureRootNoteNamesVisible();
    }, 500);
});

// Also run on window load to catch any late initialization
window.addEventListener('load', function() {
    setTimeout(function() {
        ensureRootNoteNamesVisible();
    }, 300);
});

/**
 * Overrides existing cursor functions with our fixed versions
 */
function overrideCursorFunctions() {
    // Store original functions
    const originalLeftCursorClick = window.leftCursorClick;
    const originalRightCursorClick = window.rightCursorClick;
    
    // Override with fixed versions
    window.leftCursorClick = function(e) {
        // Start navigation sequence
        isNavigating = true;
        
        // Store current active notes before navigating
        storeActiveNotes();
        
        // Call original function if it exists
        if (typeof originalLeftCursorClick === 'function') {
            originalLeftCursorClick.call(this, e);
        }
        
        // Apply our fixes after a short delay
        setTimeout(function() {
            cleanupPreviousNotes();
            isNavigating = false;
        }, 100);
    };
    
    window.rightCursorClick = function(e) {
        // Start navigation sequence
        isNavigating = true;
        
        // Store current active notes before navigating
        storeActiveNotes();
        
        // Call original function if it exists
        if (typeof originalRightCursorClick === 'function') {
            originalRightCursorClick.call(this, e);
        }
        
        // Apply our fixes after a short delay
        setTimeout(function() {
            cleanupPreviousNotes();
            isNavigating = false;
        }, 100);
    };
    
    console.log('Cursor functions overridden with fixed versions');
}

/**
 * Store currently active notes before navigation
 */
function storeActiveNotes() {
    // Reset the array
    currentActiveNotes = [];
    
    // Store all active note elements by their CSS selector path
    document.querySelectorAll('.note.active').forEach(function(noteElement) {
        // Get string and note class
        const stringClass = Array.from(noteElement.parentElement.classList).find(cls => 
            cls.includes('String'));
        
        const noteClass = Array.from(noteElement.classList).find(cls => 
            !['note', 'active'].includes(cls));
        
        if (stringClass && noteClass) {
            currentActiveNotes.push(`.${stringClass} .note.${noteClass}`);
        }
    });
    
    console.log(`Stored ${currentActiveNotes.length} active notes before navigation`);
}

/**
 * Clean up previous inversion's notes
 */
function cleanupPreviousNotes() {
    // Deactivate previously active notes that shouldn't be active now
    currentActiveNotes.forEach(function(selector) {
        const noteElement = document.querySelector(selector);
        if (noteElement) {
            // Only deactivate if this note wasn't reactivated by the new inversion
            if (!noteElement.dataset.newlyActivated) {
                noteElement.classList.remove('active');
                
                // Reset the note image
                const toneImg = noteElement.querySelector('img.tone');
                if (toneImg) {
                    toneImg.classList.remove('active');
                    toneImg.classList.remove('root');
                    toneImg.style.opacity = '';
                    toneImg.style.border = '';
                    toneImg.style.boxShadow = '';
                    toneImg.src = '/static/media/yellow_circle.svg';
                }
                
                // Hide note name
                const noteNameEl = noteElement.querySelector('.notename');
                if (noteNameEl) {
                    noteNameEl.style.visibility = 'hidden';
                    noteNameEl.style.opacity = '0';
                    noteNameEl.classList.remove('active');
                    noteNameEl.classList.remove('show-name');
                }
            }
        }
    });
    
    // Clear "newly activated" flags
    document.querySelectorAll('.note[data-newly-activated]').forEach(function(noteElement) {
        delete noteElement.dataset.newlyActivated;
    });
    
    // Clear stored notes
    currentActiveNotes = [];
    
    // Final step: ensure root notes have visible note names
    ensureRootNoteNamesVisible();
    
    console.log('Cleaned up previous inversion notes');
}

/**
 * Make sure root note names are visible
 */
function ensureRootNoteNamesVisible() {
    // Find notes with root indicators
    document.querySelectorAll('img.tone[data-is-root="true"], img.tone.root, img.tone[src*="red_circle"]').forEach(function(rootTone) {
        // Find parent note element
        const noteElement = rootTone.closest('.note');
        if (noteElement) {
            noteElement.classList.add('active');
            
            // Make sure note name is visible
            const noteName = noteElement.querySelector('.notename');
            if (noteName) {
                noteName.style.visibility = 'visible';
                noteName.style.opacity = '1';
                noteName.classList.add('active');
                noteName.classList.add('show-name');
                noteName.style.fontWeight = 'bold';
            }
        }
    });
}

/**
 * Set up listeners for navigation events
 */
function setupNavigationListeners() {
    // Intercept when new chord notes are activated
    const originalGetTonesFromDataChords = window.getTonesFromDataChords;
    
    if (typeof originalGetTonesFromDataChords === 'function') {
        window.getTonesFromDataChords = function(position, range) {
            // Call the original function
            originalGetTonesFromDataChords.call(this, position, range);
            
            // Mark the newly activated notes and ensure their proper display
            if (isNavigating) {
                document.querySelectorAll('.note.active').forEach(function(noteElement) {
                    // Mark as newly activated
                    noteElement.dataset.newlyActivated = 'true';
                    
                    // Ensure proper styling for active notes
                    const toneImg = noteElement.querySelector('img.tone');
                    if (toneImg) {
                        toneImg.classList.add('active');
                        toneImg.style.opacity = '1';
                        
                        // Special handling for root notes
                        if (toneImg.getAttribute('data-is-root') === 'true' || 
                            toneImg.src.includes('red_circle')) {
                            
                            // Style as root
                            toneImg.classList.add('root');
                            toneImg.src = '/static/media/red_circle.svg';
                            toneImg.style.border = '2px solid rgb(204, 0, 0)';
                            toneImg.style.boxShadow = 'rgba(255, 0, 0, 0.3) 0px 0px 5px';
                            
                            // Make note name visible
                            const noteName = noteElement.querySelector('.notename');
                            if (noteName) {
                                noteName.style.visibility = 'visible';
                                noteName.style.opacity = '1';
                                noteName.classList.add('active');
                                noteName.classList.add('show-name');
                                noteName.style.fontWeight = 'bold';
                            }
                        }
                    }
                });
                
                // Extra call to ensure root note names are visible
                setTimeout(ensureRootNoteNamesVisible, 50);
            }
        };
        
        console.log('Intercepted getTonesFromDataChords function');
    }
    
    // Also listen for the chord-position-changed event
    document.addEventListener('chord-position-changed', function() {
        // Just in case our cursor handlers miss something
        if (!isNavigating) {
            storeActiveNotes();
            
            setTimeout(function() {
                cleanupPreviousNotes();
            }, 100);
        }
    });
    
    // Also listen for any chord-tones-updated events
    document.addEventListener('chord-tones-updated', function() {
        // Short delay to let the chord update finish
        setTimeout(ensureRootNoteNamesVisible, 100);
    });
    
    console.log('Navigation listeners set up');
}

// Add a debug function that can be called from console
window.debugSimpleCursorNavigation = function() {
    console.log('===== SIMPLE CURSOR NAVIGATION DEBUG =====');
    console.log('Is navigating:', isNavigating);
    console.log('Stored active notes:', currentActiveNotes);
    console.log('Current active notes:', document.querySelectorAll('.note.active').length);
    console.log('Active tone images:', document.querySelectorAll('img.tone.active').length);
    console.log('Root notes:', document.querySelectorAll('img.tone.root').length);
    
    return 'Debug complete';
};
