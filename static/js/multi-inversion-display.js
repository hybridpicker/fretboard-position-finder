/**
 * Chord display optimizer
 * Enhances chord displays with better visualization and user experience
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize chord display enhancements
    enhanceChordDisplay();
    
    // Add event listener for position changes
    window.addEventListener('popstate', function() {
        setTimeout(function() {
            enhanceChordDisplay();
        }, 200);
    });
    
    // Apply fix on page load after a delay
    setTimeout(function() {
        console.log("Running initial force fix for chord display...");
        if (typeof forceCorrectInversionDisplay === 'function') {
            forceCorrectInversionDisplay();
        }
        
        // Set up auto-recovery for inversion display
        setupAutoRecovery();
    }, 800);
    
    // Listen for chord position activation event
    document.addEventListener('chord-position-activated', function(e) {
        // Wait a moment for the DOM to update, then enhance chord display
        setTimeout(enhanceChordDisplay, 150);
    });
    
    // Listen for cursor navigation events
    document.addEventListener('cursor-navigation-complete', function(e) {
        console.log("Cursor navigation event detected:", e.detail);
        // Wait a moment for the DOM to update, then enhance chord display
        setTimeout(enhanceChordDisplay, 150);
    });
    
    // Listen for the reset event from forceCompleteReset
    document.addEventListener('all-notes-reset', function(e) {
        console.log("All notes reset event detected:", e.detail);
        // Wait longer after a full reset to ensure DOM is fully updated
        setTimeout(function() {
            console.log("Attempting to restore inversion display after reset");
            enhanceChordDisplay();
        }, 200);
    });
});

/**
 * Enhance chord display with active inversion only (no transparent alternatives)
 */
function enhanceChordDisplay() {
    // Simply reset all inversion styling - we don't want to show alternative inversions anymore
    document.querySelectorAll('.inversion-note, .inversion-tone').forEach(el => {
        el.classList.remove('inversion-note', 'inversion-tone');
        el.style.opacity = '';
        el.style.filter = '';
        el.style.border = '';
        el.removeAttribute('data-inversion');
    });
    
    // Exit early - we only want to show the active inversion
    return;
    console.log("--- enhanceChordDisplay STARTING ---");
    
    // Only proceed if voicing_data is available
    if (typeof voicing_data === 'undefined' || !voicing_data || !voicing_data.note_range) {
        console.log("ERROR: voicing_data is undefined or missing note_range property");
        return;
    }

    // Get the current active range and position
    const currentRange = voicing_data.note_range || '';
    const urlParams = new URLSearchParams(window.location.search);
    let currentPosition = urlParams.get('position_select') || 'Root Position'; // Default to Root Position if not specified
    
    // Handle numeric position values (map 0 → "Root Position", 1 → "First Inversion", etc.)
    if (/^\d+$/.test(currentPosition)) {
        const numPos = parseInt(currentPosition, 10);
        const positionMap = {
            0: 'Root Position',
            1: 'First Inversion',
            2: 'Second Inversion',
            3: 'Third Inversion'
        };
        
        if (positionMap[numPos]) {
            console.log(`Position numeric value ${numPos} converted to "${positionMap[numPos]}"`);
            currentPosition = positionMap[numPos];
        }
    }
    
    // Map 'Root Position' to 'Basic Position' for internal data access if needed
    const internalPosition = currentPosition === 'Root Position' ? 'Basic Position' : currentPosition;


    // --- Root Note Styling Cleanup --- 
    document.querySelectorAll('img.tone.root').forEach(img => {
        img.classList.remove('root', 'inversion-root'); // Remove root classes
        img.src = '/static/media/yellow_circle.svg'; // Reset to default image
        // Reset styles applied specifically for roots
        img.style.opacity = ''; 
        img.style.border = '';
        img.style.boxShadow = '';
        img.removeAttribute('data-root-for'); // Remove data attribute

        // Also reset the corresponding note name element's style if needed
        const noteDiv = img.closest('.note');
        if (noteDiv) {
            const noteNameDiv = noteDiv.querySelector('.notename');
            if (noteNameDiv) {
                noteNameDiv.style.fontWeight = ''; // Reset font weight
            }
        }
    });
    // --- End Root Note Styling Cleanup ---
    
    // First, reset all inversion-note styling
    document.querySelectorAll('.inversion-note, .inversion-tone').forEach(el => {
        el.classList.remove('inversion-note', 'inversion-tone');
        el.style.opacity = ''; // Reset opacity
        el.style.filter = ''; // Reset filter
        el.style.border = ''; // Reset border
        el.removeAttribute('data-inversion'); // Remove data attribute
    });
    
    // Get available positions for this range from voicing_data
    const availablePositions = [];
    if (voicing_data[currentRange]) {
        // Use a defined order if possible, otherwise just keys
        const order = ['Basic Position', 'First Inversion', 'Second Inversion', 'Third Inversion'];
        const availableKeys = Object.keys(voicing_data[currentRange]);
        
        // Process standard string position names
        order.forEach(pos => {
            if (availableKeys.includes(pos)) {
                availablePositions.push(pos);
            }
        });
        
        // Check for numeric position indices (0, 1, 2, 3)
        for (let i = 0; i < 4; i++) {
            if (availableKeys.includes(String(i))) {
                // Map numeric indices to position names
                const positionName = i === 0 ? 'Basic Position' : 
                                    i === 1 ? 'First Inversion' :
                                    i === 2 ? 'Second Inversion' : 'Third Inversion';
                console.log(`Found numeric position "${i}" in data, mapped to "${positionName}"`);
                
                // Only add if we don't already have this position
                if (!availablePositions.includes(positionName)) {
                    availablePositions.push(positionName);
                }
            }
        }
        
        // Add any remaining keys not in the standard order (just in case)
        availableKeys.forEach(key => {
            // Skip numeric keys as we've already processed them
            if (!availablePositions.includes(key) && !/^\d+$/.test(key)) {
                availablePositions.push(key);
            }
        });
    } else {
        console.warn(`[MultiDisplayDebug] No data found for range: ${currentRange}`);
        return;
    }
    
    
    console.log(`Found current range: ${currentRange}, position: ${currentPosition}`);
    console.log(`Available positions: ${availablePositions.join(', ')}`);
    
    // --- Apply Styling Based on Data --- 
    availablePositions.forEach(positionKey => {
        try { // Add try block for the outer loop (each position)
            // FIX: Use positionDataObject, not array
            const positionDataObject = voicing_data[currentRange][positionKey];
            if (!positionDataObject || typeof positionDataObject !== 'object') {
                console.warn(`[MultiDisplayDebug] No valid data object found for position ${positionKey}, skipping.`);
                return;
            }
            
            console.log(`Processing position: ${positionKey} (${positionKey === internalPosition ? 'ACTIVE' : 'inactive'})`);
            const positionStrings = Object.keys(positionDataObject);
            
            positionStrings.forEach(stringKey => {
                // *** ADDED CHECK: Skip processing if the key is 'assigned_strings' ***
                if (stringKey === 'assigned_strings') {
                    return; // Skip to the next stringKey in the forEach
                }
                // *** END ADDED CHECK ***
                try { // Add try block for the inner loop (each string/note)
                    const noteInfo = positionDataObject[stringKey];
                    if (!noteInfo) {
                        return; // Skip this string
                    }

                    let noteName = '';
                    let isRoot = false;

                    if (Array.isArray(noteInfo)) {
                        noteName = (noteInfo[0] || '').toLowerCase();
                        isRoot = noteInfo[3] === true; // Read the boolean is_root flag from Python
                    } else if (typeof noteInfo === 'string') {
                        noteName = noteInfo.toLowerCase();
                        isRoot = false; // Assume not root if only string is provided
                    } else {
                        console.warn(`[MultiDisplayDebug]    Unexpected noteInfo format for ${stringKey} in ${positionKey}:`, noteInfo);
                        return; // Skip if format is unexpected
                    }
                    
                    if (!noteName) {
                        return; // Skip if no note name derived
                    }

                    // Find corresponding elements on the fretboard
                    const noteElements = document.querySelectorAll(`.${stringKey} .note.${noteName}`);
                    const toneElements = document.querySelectorAll(`.${stringKey} img.tone.${noteName}`);
                    
                    if (noteElements.length === 0 || toneElements.length === 0) {
                        return; // Skip if elements not found
                    }

                    // --- Styling Logic --- 
                    if (positionKey === internalPosition) {
                        // Style for the CURRENTLY SELECTED inversion
                        noteElements.forEach(el => {
                            el.classList.add('active');
                            el.classList.remove('inversion-note');
                            el.style.opacity = '';
                            el.style.filter = '';
                            el.style.border = '';
                            const noteNameDiv = el.querySelector('.notename');
                            if (noteNameDiv) noteNameDiv.style.fontWeight = 'bold';
                        });
                        toneElements.forEach(el => {
                            el.classList.add('active');
                            el.classList.remove('inversion-tone');
                            el.style.visibility = 'visible';
                            el.style.opacity = '';
                            el.style.filter = '';
                            el.style.border = '';
                            el.style.boxShadow = ''; 
                            el.removeAttribute('data-inversion');

                            if (isRoot) {
                                el.classList.add('root');
                                el.src = '/static/media/red_circle.svg';
                                el.style.opacity = '1';
                                el.style.border = '2px dashed #AA5500';
                                el.style.boxShadow = '0 0 3px rgba(200, 100, 0, 0.3)';
                                el.setAttribute('data-root-for', positionKey);
                            } else {
                            }
                        });
                    } else {
                        // Style for ALTERNATIVE (not selected) inversions
                        noteElements.forEach(el => {
                            el.classList.add('active', 'inversion-note');
                            el.setAttribute('data-inversion', positionKey);
                            const noteNameDiv = el.querySelector('.notename');
                            if (noteNameDiv) noteNameDiv.style.fontWeight = '';
                        });
                        toneElements.forEach(el => {
                            el.classList.add('active', 'inversion-tone');
                            el.style.visibility = 'visible';
                            el.setAttribute('data-inversion', positionKey);

                            if (isRoot) {
                                el.classList.add('inversion-root');
                                el.setAttribute('data-root-for', positionKey);
                            }
                        });
                    }
                } catch (innerError) {
                    console.error(`[MultiDisplayDebug] Error processing string ${stringKey} in position ${positionKey}:`, innerError);
                }
            }); // End inner string loop
        } catch (outerError) {
            console.error(`[MultiDisplayDebug] Error processing position ${positionKey}:`, outerError);
        }
    }); // End outer position loop
    // --- End Apply Styling Based on Data --- 
    
    // Ensure the CSS style for inversion classes is present
    addInversionDisplayStyle();
    
    // Debug the final counts
    const activeNotes = document.querySelectorAll('.note.active:not(.inversion-note)').length;
    const inversionNotes = document.querySelectorAll('.inversion-note').length;
    const totalActive = document.querySelectorAll('.note.active').length;
    
    console.log(`--- enhanceChordDisplay COMPLETED ---`);
    console.log(`Stats: ${activeNotes} active notes, ${inversionNotes} inversion notes (${totalActive} total active)`);
    
    if (inversionNotes === 0) {
        console.warn("WARNING: No inversion notes were created - opacity effect will not be visible!");
    }
}

/**
 * Previously added CSS for inversion display - now just removes any existing styling
 */
function addInversionDisplayStyle() {
    // Remove any existing inversion style
    const existingStyle = document.getElementById('inversion-style');
    if (existingStyle) {
        existingStyle.remove();
    }
    
    // We could add this simple style to ensure root notes are properly displayed
    const style = document.createElement('style');
    style.id = 'inversion-style';
    style.textContent = `
        /* Ensure primary root note style is clear */
        img.tone.root {
            opacity: 1 !important; 
            filter: none !important;
            border: 2px solid #CC0000 !important; 
            box-shadow: 0 0 5px rgba(255, 0, 0, 0.3) !important;
        } 
    `;
    document.head.appendChild(style);
}

// Helper function to update chord inversions after navigation
// Can be called from cursor controls or UI events
function updateChordInversions() {
    console.log("updateChordInversions called - will attempt to restore inversions");
    
    // First, check the current state
    const beforeCount = document.querySelectorAll('.inversion-note, .inversion-tone').length;
    console.log(`Initial state: ${beforeCount} inversion elements found`);
    
    // Get current position from URL vs. select element to detect mismatch
    const urlParams = new URLSearchParams(window.location.search);
    const urlPosition = urlParams.get('position_select') || 'Root Position';
    const selectPosition = document.getElementById('position_select')?.value || urlPosition;
    
    // Check if there's a mismatch between URL and select element
    const positionMismatch = urlPosition !== selectPosition;
    if (positionMismatch) {
        console.log(`POSITION MISMATCH DETECTED: URL=${urlPosition}, select=${selectPosition}`);
        console.log("Using force fix to correct inversion display");
        
        // Use the force fix method for direct correction
        forceCorrectInversionDisplay();
        return;
    }
    
    // Regular approach for consistent positions
    setTimeout(function() {
        console.log("First enhanceChordDisplay attempt starting");
        enhanceChordDisplay();
        
        // Double check if it worked - if not, try again with a longer delay
        setTimeout(function() {
            // Check if we have multiple inversions visible
            const activeInversions = document.querySelectorAll('.inversion-note, .inversion-tone');
            console.log(`After first attempt: ${activeInversions.length} inversion elements`);
            
            if (activeInversions.length === 0) {
                console.log("No inversion styling detected, trying force fix...");
                forceCorrectInversionDisplay();
            }
        }, 250);
    }, 100);
}

// Expose the function globally so it can be called from other scripts
window.updateChordInversions = updateChordInversions;

/**
 * Simplified diagnostic function for the new single-inversion display
 */
function diagnoseInversionDisplay() {
    console.log("=== CHORD DISPLAY DIAGNOSTIC REPORT ===");
    
    // Check if voicing_data is available
    if (typeof voicing_data === 'undefined' || !voicing_data) {
        console.error("ERROR: voicing_data is undefined");
        return "ERROR: Missing voicing data";
    }
    
    // Get current range and position
    const currentRange = voicing_data.note_range || '';
    const urlParams = new URLSearchParams(window.location.search);
    let currentPosition = urlParams.get('position_select') || 'Root Position';
    
    console.log(`Current state: range=${currentRange}, position=${currentPosition}`);
    
    // Check DOM elements
    const stats = {
        activeNotes: document.querySelectorAll('.note.active').length,
        activeTones: document.querySelectorAll('img.tone.active').length,
        rootNotes: document.querySelectorAll('img.tone.root').length,
        // These should be 0 in the new approach
        inversionNotes: document.querySelectorAll('.inversion-note').length,
        inversionTones: document.querySelectorAll('.inversion-tone').length
    };
    
    console.log("DOM element counts:", stats);
    
    // Simple check for potential issues
    let issues = [];
    
    if (stats.activeNotes === 0) {
        issues.push("No active notes found - chord display may be empty");
    }
    
    if (stats.inversionNotes > 0 || stats.inversionTones > 0) {
        issues.push("Found inversion styling classes that should have been removed");
        // Auto-fix this issue
        document.querySelectorAll('.inversion-note, .inversion-tone').forEach(el => {
            el.classList.remove('inversion-note', 'inversion-tone');
            el.style.opacity = '';
        });
    }
    
    // Generate report
    if (issues.length > 0) {
        console.log("ISSUES FOUND:");
        issues.forEach(issue => console.log(`- ${issue}`));
    } else {
        console.log("No issues detected - display showing active inversion only");
    }
    
    console.log("=== END DIAGNOSTIC REPORT ===");
    
    return {
        state: { range: currentRange, position: currentPosition },
        elementStats: stats,
        issuesFound: issues
    };
}

// Expose diagnostic function globally
window.diagnoseInversionDisplay = diagnoseInversionDisplay;

/**
 * Force the correct inversion display based on the URL
 * Now simplified to only show active inversion (no opacity effect)
 */
function forceCorrectInversionDisplay() {
    // Just ensure all inversion-related classes are removed
    document.querySelectorAll('.inversion-note, .inversion-tone').forEach(el => {
        el.classList.remove('inversion-note', 'inversion-tone');
        el.style.opacity = '';
        el.style.filter = '';
        el.style.border = '';
        el.removeAttribute('data-inversion');
    });
    
    // Log completion
    console.log("Removed all alternative inversion styling - showing active inversion only");
}

// Expose the function globally
window.forceCorrectInversionDisplay = forceCorrectInversionDisplay;

/**
 * Set up auto-recovery - simplified version
 * Now just ensures all inversion styling is removed
 */
function setupAutoRecovery() {
    // We don't need the recovery watcher anymore 
    // since we're not showing alternative inversions
    
    // Just perform a one-time cleanup to ensure no inversion styling remains
    document.querySelectorAll('.inversion-note, .inversion-tone').forEach(el => {
        el.classList.remove('inversion-note', 'inversion-tone');
        el.style.opacity = '';
        el.style.filter = '';
        el.style.border = '';
        el.removeAttribute('data-inversion');
    });
    
    console.log("Inversion display simplified - alternative inversions disabled");
}
