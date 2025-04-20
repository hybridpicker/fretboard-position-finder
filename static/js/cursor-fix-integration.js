/**
 * Cursor Fix Integration Script
 * This script ensures our cursor functions are properly integrated with the application
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Cursor fix integration script loaded");
    
    // Wait a short time for other scripts to finish initialization
    setTimeout(function() {
        integrateCursorFunctions();
    }, 500);
    
    // Also integrate on any cursor cleanup
    const originalCleanupFunction = window.cleanupDuplicateCursors;
    if (typeof originalCleanupFunction === 'function') {
        window.cleanupDuplicateCursors = function() {
            // Call the original function first
            originalCleanupFunction.apply(this, arguments);
            
            // Then integrate our cursor functions
            setTimeout(integrateCursorFunctions, 100);
        };
        console.log("Overrode cleanupDuplicateCursors function for integration");
    }
});

function integrateCursorFunctions() {
    console.log("Integrating cursor functions");
    
    // Find all cursor elements
    const leftCursors = document.querySelectorAll('.left-cursor');
    const rightCursors = document.querySelectorAll('.right-cursor');
    
    // Apply to left cursors
    leftCursors.forEach(cursor => {
        // Remove existing click handlers by cloning
        const newCursor = cursor.cloneNode(true);
        if (cursor.parentNode) {
            cursor.parentNode.replaceChild(newCursor, cursor);
        }
        
        // Add our click handler
        newCursor.addEventListener('click', leftCursorClick);
        
        // Ensure proper visibility
        newCursor.style.display = 'flex';
        newCursor.style.visibility = 'visible';
        newCursor.style.opacity = '1';
        newCursor.style.position = 'absolute';
    });
    
    // Apply to right cursors
    rightCursors.forEach(cursor => {
        // Remove existing click handlers by cloning
        const newCursor = cursor.cloneNode(true);
        if (cursor.parentNode) {
            cursor.parentNode.replaceChild(newCursor, cursor);
        }
        
        // Add our click handler
        newCursor.addEventListener('click', rightCursorClick);
        
        // Ensure proper visibility
        newCursor.style.display = 'flex';
        newCursor.style.visibility = 'visible';
        newCursor.style.opacity = '1';
        newCursor.style.position = 'absolute';
    });
    
    console.log(`Cursor functions integrated: ${leftCursors.length} left cursors, ${rightCursors.length} right cursors`);
    
    // Update display and visibility based on current state
    if (typeof updateDisplay === 'function') {
        updateDisplay();
    }
    
    if (typeof updateCursorVisibility === 'function') {
        updateCursorVisibility();
    }
}

// Create Event Listeners for keyboard navigation (optional enhancement)
document.addEventListener('keydown', function(event) {
    // Left arrow key
    if (event.key === 'ArrowLeft') {
        if (typeof leftCursorClick === 'function') {
            leftCursorClick();
        }
    }
    
    // Right arrow key
    if (event.key === 'ArrowRight') {
        if (typeof rightCursorClick === 'function') {
            rightCursorClick();
        }
    }
});