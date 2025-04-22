/**
 * Root Note Keyboard Controls
 * 
 * Implements Up/Down arrow keys to change root note
 * - Up Arrow: Increase root note one half step
 * - Down Arrow: Decrease root note one half step
 */

document.addEventListener('DOMContentLoaded', function() {
    // Set up keyboard navigation for root notes
    setupRootNoteKeyboardNavigation();
});

/**
 * Set up keyboard navigation for changing root notes
 */
function setupRootNoteKeyboardNavigation() {
    document.addEventListener('keydown', function(event) {
        // Handle Up/Down arrow keys for root note changes
        if (event.key === 'ArrowUp') {
            event.preventDefault();
            changeRootNote(1); // Increase by half step
        } else if (event.key === 'ArrowDown') {
            event.preventDefault();
            changeRootNote(-1); // Decrease by half step
        }
    });
}

/**
 * Change the root note by moving up or down in the select element
 * @param {number} direction - 1 for up, -1 for down
 */
function changeRootNote(direction) {
    const rootSelect = document.getElementById('root');
    if (!rootSelect) return;
    
    const options = rootSelect.options;
    const currentIndex = rootSelect.selectedIndex;
    
    // Get the current value (ID) and handle special wrap-around cases
    const currentValue = parseInt(rootSelect.value);
    
    // Special handling for wrapping from 1 to 17 and vice versa
    let newIndex;
    if (direction === 1 && currentValue === 17) {
        // Wrap from 17 to 1
        for (let i = 0; i < options.length; i++) {
            if (parseInt(options[i].value) === 1) {
                newIndex = i;
                break;
            }
        }
    } else if (direction === -1 && currentValue === 1) {
        // Wrap from 1 to 17
        for (let i = 0; i < options.length; i++) {
            if (parseInt(options[i].value) === 17) {
                newIndex = i;
                break;
            }
        }
    } else {
        // Normal case - calculate new index with wrapping
        newIndex = (currentIndex + direction + options.length) % options.length;
    }
    
    // Update selection
    rootSelect.selectedIndex = newIndex;
    
    // Trigger a change event to update the UI
    const event = new Event('change');
    rootSelect.dispatchEvent(event);
    
    // Submit the form to update the display
    const form = document.getElementById('fretboard_form');
    if (form) {
        form.submit();
    }
}

// Define the global functions for compatibility with existing code
window.rootNoteUp = function() {
    changeRootNote(1);
};

window.rootNoteDown = function() {
    changeRootNote(-1);
};

// Legacy aliases for compatibility
window.increaseRoot = window.rootNoteUp;
window.decreaseRoot = window.rootNoteDown;
