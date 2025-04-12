// Add at the beginning of the file, right after other initializations
window.currentVoicingData = {}; // Global object to store voicing data

// Hook into the direct_chord_navigation.js activation function to capture voicing data
(function() {
    // Look for the original activate function (it might be in direct_chord_navigation.js)
    // Need to wait for the DOM to be ready or for the original script to load
    document.addEventListener('DOMContentLoaded', () => {
        // Check periodically if the function exists
        const checkInterval = setInterval(() => {
            // Ensure window.activateNotesForPosition exists before trying to patch
            if (typeof window.activateNotesForPosition === 'function') {
                clearInterval(checkInterval); // Stop checking once found

                // Check if already patched to prevent multiple patches
                if (!window.activateNotesForPosition.isPatched) {
                    const originalActivateFunction = window.activateNotesForPosition;

                    window.activateNotesForPosition = function(range, position, stringData) {
                        // Store the voicing data for later use in root marking
                        if (!window.currentVoicingData) window.currentVoicingData = {};
                        // Ensure the position entry is initialized as an array if it doesn't exist
                        if (!window.currentVoicingData[position]) window.currentVoicingData[position] = [];
                        // Store the stringData (assuming it's the first element of the array for that position)
                        window.currentVoicingData[position][0] = stringData;


                        // Call the original function
                        return originalActivateFunction.apply(this, arguments);
                    };
                    // Mark as patched
                    window.activateNotesForPosition.isPatched = true;
                } else {
                }

            }
        }, 100); // Check every 100ms

        // Timeout after a few seconds if the function is never found
        setTimeout(() => {
            clearInterval(checkInterval);
            if (typeof window.activateNotesForPosition !== 'function') {
                 console.warn("activateNotesForPosition function not found for patching after timeout.");
            }
        }, 5000); // Stop checking after 5 seconds
    });
})();

// Removed outdated patching logic for fixRootNoteMarking, fallbackRootMarking, and setupInversionDisplay
