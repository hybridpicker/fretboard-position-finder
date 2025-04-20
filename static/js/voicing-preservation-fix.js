/**
 * Voicing Preservation Fix
 * 
 * This script ensures chord voicings remain visible during cursor navigation.
 * It ONLY manages styling without deactivating any notes.
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Voicing preservation fix loaded');
    
    // Override cursor functions
    overrideCursorFunctions();
    
    // Run initial fix after page loads
    setTimeout(fixVoicingDisplays, 500);
});

/**
 * Override cursor click functions with fixed versions
 */
function overrideCursorFunctions() {
    // Store original functions to call later
    const originalLeftCursorClick = window.leftCursorClick;
    const originalRightCursorClick = window.rightCursorClick;
    
    // Replace left cursor click
    window.leftCursorClick = function(e) {
        // Call original function first
        if (typeof originalLeftCursorClick === 'function') {
            originalLeftCursorClick.call(this, e);
        }
        
        // Apply our fix after a short delay
        setTimeout(fixVoicingDisplays, 50);
    };
    
    // Replace right cursor click
    window.rightCursorClick = function(e) {
        // Call original function first
        if (typeof originalRightCursorClick === 'function') {
            originalRightCursorClick.call(this, e);
        }
        
        // Apply our fix after a short delay
        setTimeout(fixVoicingDisplays, 50);
    };
    
    console.log('Cursor functions overridden');
}

/**
 * Fix the display of chord voicings
 * IMPORTANT: This function doesn't deactivate any notes,
 * it only ensures proper styling is applied
 */
function fixVoicingDisplays() {
    console.log('Fixing voicing displays...');
    
    // Step 1: Ensure all active notes have visible tone images
    document.querySelectorAll('.note.active').forEach(function(noteElement) {
        const toneImg = noteElement.querySelector('img.tone');
        if (toneImg) {
            toneImg.classList.add('active');
            toneImg.style.opacity = '1';
            toneImg.style.visibility = 'visible';
        }
    });
    
    // Step 2: Fix root note styling and show its name
    let rootFound = false;
    
    // Try data-is-root attribute first
    document.querySelectorAll('.note.active img.tone[data-is-root="true"]').forEach(function(rootTone) {
        applyRootStyling(rootTone);
        rootFound = true;
    });
    
    // Also check for root class
    if (!rootFound) {
        document.querySelectorAll('.note.active img.tone.root').forEach(function(rootTone) {
            applyRootStyling(rootTone);
            rootFound = true;
        });
    }
    
    // If still no root found, try finding the first active note
    if (!rootFound) {
        const firstActive = document.querySelector('.note.active img.tone');
        if (firstActive) {
            applyRootStyling(firstActive);
        }
    }
    
    // Step 3: Hide note names for non-root notes
    document.querySelectorAll('.note.active').forEach(function(noteElement) {
        const toneImg = noteElement.querySelector('img.tone');
        if (toneImg && !toneImg.classList.contains('root')) {
            // Make sure non-root note has standard styling
            toneImg.src = '/static/media/yellow_circle.svg';
            toneImg.style.border = '';
            toneImg.style.boxShadow = '';
            
            // Hide note name
            const noteName = noteElement.querySelector('.notename');
            if (noteName) {
                noteName.style.visibility = 'hidden';
                noteName.style.opacity = '0';
            }
        }
    });
    
    console.log('Voicing displays fixed');
}

/**
 * Apply styling to a root note
 */
function applyRootStyling(rootTone) {
    // Set root class and styling
    rootTone.classList.add('root');
    rootTone.src = '/static/media/red_circle.svg';
    rootTone.style.opacity = '1';
    rootTone.style.border = '2px solid rgb(204, 0, 0)';
    rootTone.style.boxShadow = 'rgba(255, 0, 0, 0.3) 0px 0px 5px';
    
    // Make the notename visible
    const noteElement = rootTone.closest('.note');
    if (noteElement) {
        const noteName = noteElement.querySelector('.notename');
        if (noteName) {
            noteName.style.visibility = 'visible';
            noteName.style.opacity = '1';
            noteName.style.fontWeight = 'bold';
        }
    }
}

// Make the function available globally
window.fixVoicingDisplays = fixVoicingDisplays;
