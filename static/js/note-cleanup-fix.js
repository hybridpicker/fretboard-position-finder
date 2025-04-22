/**
 * Cursor navigation fix for fretboard-position-finder
 * This script addresses the issue of notes not being properly removed
 * when navigating between chord positions with both left and right cursor clicks
 */

// Wait for the document to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("Cursor navigation fix: Initializing...");
    
    // Give other scripts a chance to load first
    setTimeout(initCursorNavigationFix, 2000);
});

/**
 * Initialize the cursor navigation fix
 */
function initCursorNavigationFix() {
    // NOTE: Disabling aggressive cleanup override to allow proper note activation
    return;
    // Store original functions if they exist
    const originalRightCursorClick = window.rightCursorClick;
    const originalLeftCursorClick = window.leftCursorClick;
    
    // Replace right cursor click with enhanced version
    window.rightCursorClick = function() {
        console.log("Cursor navigation fix: rightCursorClick executed");
        
        // First clean up existing notes before the original function runs
        cleanupBeforeNavigation();
        
        // Then call the original function 
        if (typeof originalRightCursorClick === 'function') {
            console.log("Cursor navigation fix: Calling original rightCursorClick");
            originalRightCursorClick();
        }
        
        // Allow time for the new notes to be activated, then ensure note names are visible
        setTimeout(function() {
            ensureActiveNoteNamesVisible();
            // Also make sure root note is correct
            ensureCorrectRootNote();
        }, 150);
    };
    
    // Replace left cursor click with enhanced version - using a more aggressive approach
    window.leftCursorClick = function() {
        console.log("Cursor navigation fix: leftCursorClick executed");
        
        // First clean up existing notes before the original function runs
        cleanupBeforeNavigation();
        
        // Then call the original function 
        if (typeof originalLeftCursorClick === 'function') {
            console.log("Cursor navigation fix: Calling original leftCursorClick");
            originalLeftCursorClick();
        }
        
        // Multiple cleanup and ensure visible passes with different timing to catch all cases
        setTimeout(cleanupBeforeNavigation, 50);
        setTimeout(function() {
            // Find and fix any mismatched elements (visible tone but hidden notename)
            document.querySelectorAll('img.tone').forEach(toneEl => {
                // Check for lingering styles on tones (specifically the ones in your example)
                if (toneEl.style.border || 
                    toneEl.style.boxShadow || 
                    toneEl.getAttribute('style')?.includes('border') || 
                    toneEl.getAttribute('style')?.includes('box-shadow')) {
                    
                    console.log("Found tone with persistent styling, clearing it");
                    // Reset all styles completely
                    toneEl.style.cssText = '';
                    toneEl.src = '/static/media/yellow_circle.svg';
                    
                    // Make sure the parent note is not active
                    const noteEl = toneEl.closest('.note');
                    if (noteEl) {
                        noteEl.classList.remove('active');
                        
                        // Ensure the notename is hidden
                        const nameEl = noteEl.querySelector('.notename');
                        if (nameEl) {
                            nameEl.style.visibility = 'hidden';
                            nameEl.style.opacity = '0';
                        }
                    }
                }
            });
            
            // Force active notes to have active class
            document.querySelectorAll('.note').forEach(note => {
                // If this note has an active tone image but no active class, add it
                if (note.querySelector('img.tone.active') && !note.classList.contains('active')) {
                    note.classList.add('active');
                }
            });
            
            // Then make active note names visible
            ensureActiveNoteNamesVisible();
            // Also make sure root note is correct
            ensureCorrectRootNote();
        }, 100);
        
        // Another check with longer delay
        setTimeout(function() {
            // Force active appearance one more time
            document.querySelectorAll('img.tone.active').forEach(tone => {
                const noteEl = tone.closest('.note');
                if (noteEl && !noteEl.classList.contains('active')) {
                    noteEl.classList.add('active');
                }
                
                // Make note name visible
                const nameEl = noteEl ? noteEl.querySelector('.notename') : null;
                if (nameEl) {
                    nameEl.style.visibility = 'visible';
                    nameEl.style.opacity = '1';
                }
            });
            
            // Final check for correct root note
            ensureCorrectRootNote();
        }, 250);
    };
    
    // Add direct click handlers to the elements for additional safety
    const rightCursor = document.querySelector('.right-cursor');
    const leftCursor = document.querySelector('.left-cursor');
    
    if (rightCursor) {
        rightCursor.addEventListener('mousedown', function(e) {
            // Ensure we have a clean slate before the normal click handler
            cleanupBeforeNavigation();
        }, true);
    }
    
    if (leftCursor) {
        leftCursor.addEventListener('mousedown', function(e) {
            // Ensure we have a clean slate before the normal click handler
            cleanupBeforeNavigation();
        }, true);
    }
    
    console.log("Cursor navigation fix: Initialized");
}

/**
 * Clean up notes before navigation
 * This is less aggressive than a brutal cleanup to avoid interfering with normal operation
 */
function cleanupBeforeNavigation() {
    console.log("Cursor navigation fix: Cleaning up before navigation");
    
    // STEP 1: Remove active classes from notes that shouldn't be active
    
    // Remove active class from note elements
    document.querySelectorAll('.note').forEach(noteEl => {
        noteEl.classList.remove('active');
        
        // Reset opacity but don't touch visibility which might be needed
        noteEl.style.opacity = '';
    });
    
    // Reset all tone images to non-active state - with more thorough style clearing
    document.querySelectorAll('img.tone').forEach(toneEl => {
        toneEl.classList.remove('active', 'root', 'inversion-root', 'ghost-tone');
        toneEl.src = '/static/media/yellow_circle.svg';
        
        // Reset ALL styles that might be affecting appearance
        toneEl.style.cssText = '';  // Clear all inline styles completely
        
        // Specifically target the styles in your example
        toneEl.style.visibility = '';
        toneEl.style.opacity = '';
        toneEl.style.border = 'none';
        toneEl.style.boxShadow = 'none';
    });
    
    // Hide all notenames initially
    document.querySelectorAll('.notename').forEach(nameEl => {
        nameEl.style.visibility = 'hidden';
        nameEl.style.opacity = '0';
    });
    
    // STEP 2: Target specific problem notes from earlier examples
    
    // List of specific notes that had issues
    const problematicNotes = ['g2', 'bb2', 'e2', 'c2', 'c3', 'g3', 'e3'];
    
    // Clean each problematic note
    problematicNotes.forEach(noteClass => {
        document.querySelectorAll(`.note.${noteClass}`).forEach(noteEl => {
            noteEl.classList.remove('active');
            
            // Clean all child elements
            Array.from(noteEl.children).forEach(child => {
                if (child.classList.contains('tone')) {
                    child.classList.remove('active', 'root');
                    child.src = '/static/media/yellow_circle.svg';
                    child.style.opacity = '';
                    child.style.border = '';
                    child.style.boxShadow = '';
                }
                
                if (child.classList.contains('notename')) {
                    child.style.visibility = 'hidden';
                    child.style.opacity = '0';
                }
            });
        });
    });
}

/**
 * Ensure note names are visible for active notes
 * This function makes sure the current chord's notes have visible note names
 */
function ensureActiveNoteNamesVisible() {
    console.log("Cursor navigation fix: Ensuring active note names are visible");
    
    // Find all active notes
    const activeNotes = document.querySelectorAll('.note.active');
    
    // First check for any problems - tones with styling but parent notes not active
    document.querySelectorAll('img.tone[style*="border"], img.tone[style*="box-shadow"]').forEach(toneEl => {
        const noteEl = toneEl.closest('.note');
        if (noteEl && !noteEl.classList.contains('active')) {
            // This is a problem case - either make the note active or clear the tone styling
            console.log("Found inconsistent note state - clearing styles");
            toneEl.style.cssText = '';
            toneEl.src = '/static/media/yellow_circle.svg';
        }
    });
    
    // Make notenames visible for active notes
    activeNotes.forEach(noteEl => {
        const notename = noteEl.querySelector('.notename');
        if (notename) {
            notename.style.visibility = 'visible';
            notename.style.opacity = '1';
        }
    });
    
    // Make sure notes with visible tones are consistently active
    document.querySelectorAll('img.tone.active, img.tone.root, img.tone[src*="red_circle"]').forEach(toneEl => {
        const noteEl = toneEl.closest('.note');
        if (noteEl) {
            noteEl.classList.add('active');
            
            // Ensure notename is visible
            const nameEl = noteEl.querySelector('.notename');
            if (nameEl) {
                nameEl.style.visibility = 'visible';
                nameEl.style.opacity = '1';
            }
        }
    });
    
    // Log how many active notes we found and updated
    console.log(`Cursor navigation fix: Updated ${activeNotes.length} active note names to be visible`);
}

/**
 * Ensure the correct note is marked as root
 * This function identifies the correct root note for the chord and applies proper styling
 */
function ensureCorrectRootNote() {
    // First, check if we have chord data in the global voicing_data
    if (typeof voicing_data === 'undefined' || !voicing_data) {
        console.log("No chord data available to determine root note");
        return;
    }
    
    // Get root note information from voicing_data
    const rootInfo = voicing_data.root || '';
    if (!rootInfo) {
        console.log("No root note specified in voicing_data");
        return;
    }
    
    // Extract the base note name without octave 
    const rootNoteName = rootInfo.toLowerCase().replace(/[0-9]/g, '');
    console.log(`Looking for root note: ${rootNoteName}`);
    
    // Remove any incorrect root markings first
    document.querySelectorAll('img.tone.root').forEach(toneEl => {
        const noteEl = toneEl.closest('.note');
        if (noteEl) {
            // Check if this element has a class matching the root note name
            const noteClasses = Array.from(noteEl.classList);
            const hasRootClass = noteClasses.some(cls => 
                cls.startsWith(rootNoteName) ||
                (rootNoteName === 'bb' && cls.startsWith('as')) ||
                (rootNoteName === 'eb' && cls.startsWith('ds')) ||
                (rootNoteName === 'ab' && cls.startsWith('gs'))
            );
            
            if (!hasRootClass) {
                console.log("Removing incorrect root marking from non-root note");
                toneEl.classList.remove('root');
                toneEl.src = '/static/media/circle_02.svg?v=2';
                toneEl.style.border = '';
                toneEl.style.boxShadow = '';
            }
        }
    });
    
    // Create selectors for root notes with different octave numbers and enharmonic equivalents
    const rootSelectors = [];
    
    // Add basic root note selectors with octaves
    for (let i = 0; i <= 4; i++) {
        rootSelectors.push(`.note.${rootNoteName}${i}.active`);
    }
    // Add selector without octave
    rootSelectors.push(`.note.${rootNoteName}.active`);
    
    // Add enharmonic equivalents based on music theory
    const enharmonics = {
        'c': ['bs'],
        'cs': ['db'],
        'db': ['cs'],
        'ds': ['eb'],
        'eb': ['ds'],
        'e': ['fb'],
        'fb': ['e'],
        'f': ['es'],
        'fs': ['gb'],
        'gb': ['fs'],
        'gs': ['ab'],
        'ab': ['gs'],
        'as': ['bb'],
        'bb': ['as'],
        'b': ['cb'],
        'cb': ['b']
    };
    
    // Add enharmonic equivalents if they exist
    if (enharmonics[rootNoteName]) {
        enharmonics[rootNoteName].forEach(enharmonic => {
            // Add with octaves
            for (let i = 0; i <= 4; i++) {
                rootSelectors.push(`.note.${enharmonic}${i}.active`);
            }
            // Add without octave
            rootSelectors.push(`.note.${enharmonic}.active`);
        });
    }
    
    // Try to find a root note using our selectors
    let rootFound = false;
    let rootElement = null;
    
    // Try each selector
    for (const selector of rootSelectors) {
        const candidates = document.querySelectorAll(selector);
        if (candidates.length > 0) {
            // We found at least one matching note
            rootElement = candidates[0]; // Choose the first match for now
            break;
        }
    }
    
    // If we found a root note, mark it properly
    if (rootElement) {
        const toneEl = rootElement.querySelector('img.tone');
        if (toneEl) {
            // Apply root styling
            toneEl.classList.add('root', 'active');
            toneEl.src = '/static/media/red_circle.svg';
            toneEl.style.opacity = '1';
            toneEl.style.border = '2px solid rgb(204, 0, 0)';
            toneEl.style.boxShadow = 'rgba(255, 0, 0, 0.3) 0px 0px 5px';
            toneEl.style.visibility = 'visible';
            
            // Make sure note name is visible and styled
            const nameEl = rootElement.querySelector('.notename');
            if (nameEl) {
                nameEl.style.visibility = 'visible';
                nameEl.style.opacity = '1';
                nameEl.style.fontWeight = 'bold';
                nameEl.classList.add('active');
            }
            
            rootFound = true;
            console.log("Marked correct root note");
        }
    }
    
    if (!rootFound) {
        console.log("Could not find a suitable root note to mark");
    }
}

// Make functions available globally for debugging
window.cleanupBeforeNavigation = cleanupBeforeNavigation;
window.ensureActiveNoteNamesVisible = ensureActiveNoteNamesVisible;
window.ensureCorrectRootNote = ensureCorrectRootNote;
