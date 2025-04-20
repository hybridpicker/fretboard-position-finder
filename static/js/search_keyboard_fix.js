/**
 * Search Keyboard Fix
 * 
 * Disables keyboard shortcuts when the search input is focused
 * to prevent accidental triggering while typing in the search field.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Flag to track if keyboard shortcuts should be disabled
    window.keyboardShortcutsDisabled = false;
    
    // Find search inputs
    const searchInputs = document.querySelectorAll('#overlaySearchInput, .search-input, .global-search-input');
    
    // Add focus and blur event listeners to all search inputs
    searchInputs.forEach(input => {
        // When search input gains focus, disable shortcuts
        input.addEventListener('focus', function() {
            window.keyboardShortcutsDisabled = true;
            console.log('Keyboard shortcuts disabled while typing in search');
        });
        
        // When search input loses focus, re-enable shortcuts
        input.addEventListener('blur', function() {
            window.keyboardShortcutsDisabled = false;
            console.log('Keyboard shortcuts re-enabled');
        });
    });

    // Create a list of shortcut keys that should be blocked when search is active
    // Including letters, arrows, and now number keys 1-9
    const shortcutKeys = [
        'i', 'I', 'p', 'P', 'n', 'N',
        'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
        '1', '2', '3', '4', '5', '6', '7', '8', '9'
    ];
    
    // Instead of overriding the global keydown handler, we'll modify base.js behavior
    // by adding an event listener for the specific shortcut keys we want to disable
    document.addEventListener('keydown', function(event) {
        // If shortcuts are disabled (search has focus) AND it's a shortcut key
        if (window.keyboardShortcutsDisabled && shortcutKeys.includes(event.key)) {
            // Stop propagation only for known shortcut keys
            event.stopPropagation();
            // We don't call preventDefault() here, which allows normal typing
            
            console.log('Blocked shortcut key:', event.key);
            return false;
        }
    }, true); // Use capturing phase to ensure this runs before other handlers
    
    // For special case of modifier keys like Ctrl+S, Alt+key shortcuts
    document.addEventListener('keydown', function(event) {
        // If shortcuts are disabled (search has focus) AND it's a key with modifiers
        if (window.keyboardShortcutsDisabled && (event.ctrlKey || event.altKey || event.metaKey)) {
            // Let the browser handle Ctrl+C, Ctrl+V, Ctrl+X, and Ctrl+A for copy/paste/select all
            if (event.ctrlKey && (event.key === 'c' || event.key === 'v' || event.key === 'x' || event.key === 'a')) {
                return true;
            }
            
            // Block other modifier key combinations that might be shortcuts
            event.stopPropagation();
            return false;
        }
    }, true);
});
