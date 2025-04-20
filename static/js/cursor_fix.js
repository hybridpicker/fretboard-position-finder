/**
 * Cursor Fix
 * Provides fallback definitions for cursor functions that might be missing
 */

// Define the cursor click functions immediately to ensure they're always available
window.leftCursorClick = function() {
    // Try to find and trigger the appropriate function if it exists
    if (typeof window.navigatePrevious === 'function') {
        window.navigatePrevious();
    } else if (typeof window.previousChord === 'function') {
        window.previousChord();
    } else if (typeof window.moveLeft === 'function') {
        window.moveLeft();
    } else {
        // Fallback behavior - try to go to previous position
        const positionSelect = document.getElementById('position_select');
        if (positionSelect && positionSelect.selectedIndex > 0) {
            positionSelect.selectedIndex = positionSelect.selectedIndex - 1;
            positionSelect.dispatchEvent(new Event('change'));
        }
    }
};

window.rightCursorClick = function() {
    // Try to find and trigger the appropriate function if it exists
    if (typeof window.navigateNext === 'function') {
        window.navigateNext();
    } else if (typeof window.nextChord === 'function') {
        window.nextChord();
    } else if (typeof window.moveRight === 'function') {
        window.moveRight();
    } else {
        // Fallback behavior - try to go to next position
        const positionSelect = document.getElementById('position_select');
        if (positionSelect && positionSelect.selectedIndex < positionSelect.options.length - 1) {
            positionSelect.selectedIndex = positionSelect.selectedIndex + 1;
            positionSelect.dispatchEvent(new Event('change'));
        }
    }
};

// Make sure the click handlers are properly attached when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Ensure cursor click handlers are properly attached
    const leftCursor = document.querySelector('.left-cursor');
    const rightCursor = document.querySelector('.right-cursor');
    
    if (leftCursor) {
        leftCursor.onclick = function() {
            window.leftCursorClick();
        };
    }
    
    if (rightCursor) {
        rightCursor.onclick = function() {
            window.rightCursorClick();
        };
    }
    
    // Also update any existing inline event handlers on cursor elements
    const allLeftCursors = document.querySelectorAll('.left-cursor');
    const allRightCursors = document.querySelectorAll('.right-cursor');
    
    allLeftCursors.forEach(cursor => {
        if (cursor.hasAttribute('onclick')) {
            cursor.setAttribute('onclick', 'leftCursorClick()');
        }
    });
    
    allRightCursors.forEach(cursor => {
        if (cursor.hasAttribute('onclick')) {
            cursor.setAttribute('onclick', 'rightCursorClick()');
        }
    });
});

// Add a MutationObserver to handle new cursor elements that might be added later
document.addEventListener('DOMContentLoaded', function() {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Check if any added nodes are cursors or contain cursors
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        // Check if this is a cursor element
                        if (node.classList && (node.classList.contains('left-cursor') || 
                                             node.classList.contains('right-cursor'))) {
                            attachCursorHandler(node);
                        }
                        
                        // Check children for cursor elements
                        const cursors = node.querySelectorAll('.left-cursor, .right-cursor');
                        cursors.forEach(attachCursorHandler);
                    }
                });
            }
        });
    });
    
    function attachCursorHandler(cursorElement) {
        if (cursorElement.classList.contains('left-cursor')) {
            cursorElement.onclick = function() {
                window.leftCursorClick();
            };
            if (cursorElement.hasAttribute('onclick')) {
                cursorElement.setAttribute('onclick', 'leftCursorClick()');
            }
        } else if (cursorElement.classList.contains('right-cursor')) {
            cursorElement.onclick = function() {
                window.rightCursorClick();
            };
            if (cursorElement.hasAttribute('onclick')) {
                cursorElement.setAttribute('onclick', 'rightCursorClick()');
            }
        }
    }
    
    // Start observing the entire document for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
