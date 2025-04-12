/**
 * Master Cursor Management Module
 * 
 * This file provides centralized cursor and navigation functions
 * to ensure consistent behavior between various chord and scale views.
 */

// Keep track of cursor initialization state
const CURSOR_INIT_STATE = {
    initialized: false,
    target: 'chords' // default target ('chords' or 'scales')
};

// Store original cursor click functions from other modules
const ORIGINAL_FUNCTIONS = {
    leftCursorClick: null,
    rightCursorClick: null
};

/**
 * Initialize the cursor management system
 * @param {string} target - 'chords' or 'scales' depending on what's being displayed
 */
function initCursorManagement(target) {
    // Check if already initialized for the same target
    if (CURSOR_INIT_STATE.initialized && CURSOR_INIT_STATE.target === target) {
        return CURSOR_INIT_STATE;
    }
    
    
    // Save target and mark as initialized
    CURSOR_INIT_STATE.initialized = true;
    CURSOR_INIT_STATE.target = target;
    
    // Save original functions if they exist
    if (typeof window.leftCursorClick === 'function' && ORIGINAL_FUNCTIONS.leftCursorClick === null) {
        ORIGINAL_FUNCTIONS.leftCursorClick = window.leftCursorClick;
    }
    
    if (typeof window.rightCursorClick === 'function' && ORIGINAL_FUNCTIONS.rightCursorClick === null) {
        ORIGINAL_FUNCTIONS.rightCursorClick = window.rightCursorClick;
    }
    
    // Ensure cursors are visible and working
    ensureCursorsVisible();
    hookupCursorEvents();
    
    return CURSOR_INIT_STATE;
}

/**
 * Make sure cursor elements are visible and styled correctly
 */
function ensureCursorsVisible() {
    // Find cursor elements
    const leftCursor = document.querySelector('.left-cursor');
    const rightCursor = document.querySelector('.right-cursor');
    
    if (!leftCursor && !rightCursor) {
        console.warn('Neither left nor right cursor elements found in the DOM');
        return false;
    }
    
    // Style left cursor
    if (leftCursor) {
        leftCursor.style.display = 'flex';
        leftCursor.style.visibility = 'visible';
        leftCursor.style.opacity = '1';
        leftCursor.style.cursor = 'pointer';
        
        // Special styling for chord mode
        if (CURSOR_INIT_STATE.target === 'chords') {
            leftCursor.style.position = 'fixed';
            leftCursor.style.zIndex = '999';
        }
        
        // Clear any content inside to ensure SVG background is visible
        if (leftCursor.innerHTML.trim()) {
            leftCursor.innerHTML = '';
        }
    }
    
    // Style right cursor
    if (rightCursor) {
        rightCursor.style.display = 'flex';
        rightCursor.style.visibility = 'visible';
        rightCursor.style.opacity = '1';
        rightCursor.style.cursor = 'pointer';
        
        // Special styling for chord mode
        if (CURSOR_INIT_STATE.target === 'chords') {
            rightCursor.style.position = 'fixed';
            rightCursor.style.zIndex = '999';
        }
        
        // Clear any content inside to ensure SVG background is visible
        if (rightCursor.innerHTML.trim()) {
            rightCursor.innerHTML = '';
        }
    }
    
    return true;
}

/**
 * Connect event listeners to cursor elements
 */
function hookupCursorEvents() {
    
    // Find cursor elements
    const leftCursor = document.querySelector('.left-cursor');
    const rightCursor = document.querySelector('.right-cursor');
    
    // Create master click handlers
    const masterLeftClick = function(e) {
        if (e) e.preventDefault();
        
        // Add visual feedback
        if (leftCursor) {
            leftCursor.classList.add('active');
            setTimeout(() => leftCursor.classList.remove('active'), 200);
        }
        
        // Call appropriate function
        if (typeof window.leftCursorClick === 'function') {
            try {
                window.leftCursorClick();
            } catch (error) {
                console.error('Error in leftCursorClick:', error);
                // Try original function as fallback
                if (ORIGINAL_FUNCTIONS.leftCursorClick) {
                    ORIGINAL_FUNCTIONS.leftCursorClick();
                }
            }
        } else if (ORIGINAL_FUNCTIONS.leftCursorClick) {
            ORIGINAL_FUNCTIONS.leftCursorClick();
        } else {
            console.warn('No left cursor click function available');
        }
        
        // Dispatch custom event for other components to listen to
        document.dispatchEvent(new CustomEvent('cursor-navigation-complete', {
            detail: { direction: 'left' }
        }));
    };
    
    const masterRightClick = function(e) {
        if (e) e.preventDefault();
        
        // Add visual feedback
        if (rightCursor) {
            rightCursor.classList.add('active');
            setTimeout(() => rightCursor.classList.remove('active'), 200);
        }
        
        // Call appropriate function
        if (typeof window.rightCursorClick === 'function') {
            try {
                window.rightCursorClick();
            } catch (error) {
                console.error('Error in rightCursorClick:', error);
                // Try original function as fallback
                if (ORIGINAL_FUNCTIONS.rightCursorClick) {
                    ORIGINAL_FUNCTIONS.rightCursorClick();
                }
            }
        } else if (ORIGINAL_FUNCTIONS.rightCursorClick) {
            ORIGINAL_FUNCTIONS.rightCursorClick();
        } else {
            console.warn('No right cursor click function available');
        }
        
        // Dispatch custom event for other components to listen to
        document.dispatchEvent(new CustomEvent('cursor-navigation-complete', {
            detail: { direction: 'right' }
        }));
    };
    
    // Remove any existing listeners to prevent duplicates
    if (leftCursor) {
        const newLeftCursor = leftCursor.cloneNode(true);
        leftCursor.parentNode.replaceChild(newLeftCursor, leftCursor);
        
        // Add click listener
        newLeftCursor.addEventListener('click', masterLeftClick);
    }
    
    if (rightCursor) {
        const newRightCursor = rightCursor.cloneNode(true);
        rightCursor.parentNode.replaceChild(newRightCursor, rightCursor);
        
        // Add click listener
        newRightCursor.addEventListener('click', masterRightClick);
    }
    
    // Keyboard navigation has been disabled
    
}

/**
 * Initialize cursor system when document is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-detect target based on URL or page content
    let target = 'chords'; // Default
    
    // Check URL for target hints
    const url = window.location.href.toLowerCase();
    if (url.includes('scale') || url.includes('arpeggio')) {
        target = 'scales';
    }
    
    // Or check page content
    const scaleElements = document.querySelectorAll('.scale-name, .scale-type, .scale-root');
    if (scaleElements.length > 0) {
        target = 'scales';
    }
    
    // Initialize with detected target
    initCursorManagement(target);
    
    // Add debugging command for the browser console
    window.debugCursorSystem = function() {
        
        const leftCursor = document.querySelector('.left-cursor');
        const rightCursor = document.querySelector('.right-cursor');
        
        
        return {
            state: CURSOR_INIT_STATE,
            originals: ORIGINAL_FUNCTIONS,
            leftCursor,
            rightCursor
        };
    };
    
    // Fix for direct-chord-navigation issue
    if (typeof activateNotesForPosition === 'function') {
        const originalActivateNotes = activateNotesForPosition;
        window.activateNotesForPosition = function(position) {
            try {
                originalActivateNotes(position);
            } catch (error) {
                console.error('Error in activateNotesForPosition:', error);
                // Try to recover
                try {
                    // Manual approach to activate at least some notes
                    const urlParams = new URLSearchParams(window.location.search);
                    const range = urlParams.get('note_range') || 'e - g';
                    if (typeof getTonesFromDataChords === 'function') {
                        getTonesFromDataChords(position, range);
                    }
                } catch (recoveryError) {
                    console.error('Recovery also failed:', recoveryError);
                }
            }
        };
    }
});

/**
 * Function to handle cursor clicks with better error recovery
 */
function safeLeftCursorClick() {
    
    try {
        // Attempt to use available functions in order of preference
        if (typeof window.leftCursorClick === 'function' && window.leftCursorClick !== safeLeftCursorClick) {
            window.leftCursorClick();
        } else if (ORIGINAL_FUNCTIONS.leftCursorClick) {
            ORIGINAL_FUNCTIONS.leftCursorClick();
        } else {
            // Fallback to basic behavior
            const urlParams = new URLSearchParams(window.location.search);
            const position = urlParams.get('position_select') || 'Root Position';
            const range = urlParams.get('note_range') || 'e - g';
            
            // Get available positions
            let positions = ['Root Position', 'First Inversion', 'Second Inversion', 'Third Inversion'];
            if (typeof getChordPositions === 'function') {
                positions = getChordPositions() || positions;
            }
            
            // Find current position index
            const currentIndex = positions.indexOf(position);
            if (currentIndex === -1) return;
            
            // Calculate new position
            const newIndex = (currentIndex - 1 + positions.length) % positions.length;
            const newPosition = positions[newIndex];
            
            // Update position
            if (typeof updatePosition === 'function') {
                updatePosition(newPosition);
            } else {
                // Fallback update
                const positionSelect = document.getElementById('position_select');
                if (positionSelect) positionSelect.value = newPosition;
                
                // Update URL
                const newParams = new URLSearchParams(window.location.search);
                newParams.set('position_select', newPosition);
                window.history.replaceState(null, '', window.location.pathname + '?' + newParams.toString());
            }
            
            // Update tones
            if (typeof getTonesFromDataChords === 'function') {
                getTonesFromDataChords(newPosition, range);
            }
        }
    } catch (error) {
        console.error('Error in safe left cursor click:', error);
    }
}

/**
 * Function to handle right cursor clicks with better error recovery
 */
function safeRightCursorClick() {
    
    try {
        // Attempt to use available functions in order of preference
        if (typeof window.rightCursorClick === 'function' && window.rightCursorClick !== safeRightCursorClick) {
            window.rightCursorClick();
        } else if (ORIGINAL_FUNCTIONS.rightCursorClick) {
            ORIGINAL_FUNCTIONS.rightCursorClick();
        } else {
            // Fallback to basic behavior
            const urlParams = new URLSearchParams(window.location.search);
            const position = urlParams.get('position_select') || 'Root Position';
            const range = urlParams.get('note_range') || 'e - g';
            
            // Get available positions
            let positions = ['Root Position', 'First Inversion', 'Second Inversion', 'Third Inversion'];
            if (typeof getChordPositions === 'function') {
                positions = getChordPositions() || positions;
            }
            
            // Find current position index
            const currentIndex = positions.indexOf(position);
            if (currentIndex === -1) return;
            
            // Calculate new position
            const newIndex = (currentIndex + 1) % positions.length;
            const newPosition = positions[newIndex];
            
            // Update position
            if (typeof updatePosition === 'function') {
                updatePosition(newPosition);
            } else {
                // Fallback update
                const positionSelect = document.getElementById('position_select');
                if (positionSelect) positionSelect.value = newPosition;
                
                // Update URL
                const newParams = new URLSearchParams(window.location.search);
                newParams.set('position_select', newPosition);
                window.history.replaceState(null, '', window.location.pathname + '?' + newParams.toString());
            }
            
            // Update tones
            if (typeof getTonesFromDataChords === 'function') {
                getTonesFromDataChords(newPosition, range);
            }
        }
    } catch (error) {
        console.error('Error in safe right cursor click:', error);
    }
}

// Expose safe cursor functions for global use
window.safeLeftCursorClick = safeLeftCursorClick;
window.safeRightCursorClick = safeRightCursorClick;