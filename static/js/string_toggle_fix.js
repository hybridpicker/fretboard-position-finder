/**
 * String Toggle Fix
 * Improved implementation of toggle between 8-string and 6-string guitar configurations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the string configuration
    initializeStringConfig();
    
    // No longer creating visible toggle button
    // Toggling will be done via settings menu only
});

/**
 * Creates a toggle button to switch between 6-string and 8-string configurations
 */
function createStringToggleButton() {
    // Create container for the toggle
    const container = document.createElement('div');
    container.id = 'string-toggle-container';
    container.className = 'string-toggle-container';
    
    // Create the toggle button
    const toggleButton = document.createElement('button');
    toggleButton.id = 'string-toggle-button';
    toggleButton.className = 'string-toggle-button';
    toggleButton.innerHTML = '<span class="toggle-text">6-String</span><span class="toggle-slider"></span><span class="toggle-text">8-String</span>';
    
    // Determine initial state based on cookie or default
    const savedConfig = getStringConfigCookie() || 'six-string';
    toggleButton.setAttribute('data-state', savedConfig);
    
    // Set initial appearance
    if (savedConfig === 'eight-string') {
        toggleButton.classList.add('eight-string-active');
    } else {
        toggleButton.classList.add('six-string-active');
    }
    
    // Add event listener to toggle button
    toggleButton.addEventListener('click', function() {
        toggleStringConfiguration();
    });
    
    // Add button to container
    container.appendChild(toggleButton);
    
    // Add container to the DOM - find the best place to insert it
    const fretboardContainer = document.getElementById('fretboardcontainer');
    if (fretboardContainer) {
        // Insert before the fretboard
        const fretboardParent = fretboardContainer.parentNode;
        if (fretboardParent) {
            fretboardParent.insertBefore(container, fretboardContainer);
        }
    } else {
        // Alternative: Add to a menu or control area
        const menuArea = document.querySelector('.menu-container') || 
                         document.querySelector('.controls') || 
                         document.querySelector('.main-content');
        if (menuArea) {
            menuArea.appendChild(container);
        } else {
            // Last resort: Add to body
            document.body.appendChild(container);
        }
    }
}

/**
 * Initializes the string configuration based on stored preference
 */
function initializeStringConfig() {
    // Get the user's preferred configuration from cookie or localStorage
    const preferredConfig = getStringConfigFromStorage();
    
    // Apply the configuration to the fretboard
    applyStringConfiguration(preferredConfig);
    
    // Also set a cookie to ensure backend can read it
    setStringConfigCookie(preferredConfig, 30);
    console.log(`Initialized string configuration: ${preferredConfig} (set in cookie)`);
}

/**
 * Get string configuration from all possible storage mechanisms
 * @returns {string} Either 'six-string' or 'eight-string'
 */
function getStringConfigFromStorage() {
    // Try cookie first
    const cookieValue = getStringConfigCookie();
    if (cookieValue && (cookieValue === 'six-string' || cookieValue === 'eight-string')) {
        console.log('Found stringConfig in cookie:', cookieValue);
        return cookieValue;
    }
    
    // Try localStorage with both possible keys
    try {
        // Check both possible localStorage keys
        const localValue = localStorage.getItem('stringConfig') || localStorage.getItem('stringConfiguration');
        if (localValue && (localValue === 'six-string' || localValue === 'eight-string')) {
            console.log('Found stringConfig in localStorage:', localValue);
            return localValue;
        }
    } catch (e) {
        console.warn('Could not read from localStorage:', e);
    }
    
    // Default to eight-string if no valid stored config
    console.log('No valid string configuration found, defaulting to eight-string');
    return 'eight-string';
}

/**
 * Get string configuration from all possible storage mechanisms
 * @returns {string} Either 'six-string' or 'eight-string'
 */
function getStringConfigFromStorage() {
    // Try cookie first
    const cookieValue = getStringConfigCookie();
    if (cookieValue && (cookieValue === 'six-string' || cookieValue === 'eight-string')) {
        return cookieValue;
    }
    
    // Try localStorage as fallback
    try {
        const localValue = localStorage.getItem('stringConfig');
        if (localValue && (localValue === 'six-string' || localValue === 'eight-string')) {
            return localValue;
        }
    } catch (e) {
        console.warn('Could not read from localStorage:', e);
    }
    
    // Default to six-string if no valid stored config
    return 'six-string';
}

/**
 * Toggles between 6-string and 8-string configurations
 */
function toggleStringConfiguration() {
    const toggleButton = document.getElementById('string-toggle-button');
    if (!toggleButton) {
        console.error("Toggle button not found, can't toggle configuration");
        return;
    }
    
    // Get current state
    const currentState = toggleButton.getAttribute('data-state');
    
    // Toggle state
    const newState = currentState === 'eight-string' ? 'six-string' : 'eight-string';
    toggleButton.setAttribute('data-state', newState);
    
    // Update button appearance
    updateToggleButtonAppearance();
    
    // Apply the new configuration
    applyStringConfiguration(newState);
    
    // Store preference in a cookie and localStorage
    setStringConfigCookie(newState, 30);
}

/**
 * Sets a cookie to store the string configuration preference
 * @param {string} config - Configuration to store ('six-string' or 'eight-string')
 * @param {number} days - Number of days until the cookie expires
 */
function setStringConfigCookie(config, days) {
    if (config !== 'six-string' && config !== 'eight-string') {
        console.error("Invalid string configuration:", config);
        config = 'six-string';  // Default to six-string for safety
    }
    
    // Create date for expiration
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = "expires=" + d.toUTCString();
    
    // Set cookie with secure options and SameSite=Lax to ensure it works in modern browsers
    document.cookie = "stringConfig=" + config + ";" + expires + ";path=/;SameSite=Lax";
    
    // Also store in localStorage as a backup mechanism
    try {
        localStorage.setItem('stringConfig', config);
    } catch (e) {
        console.warn('Could not store string configuration in localStorage:', e);
    }
}

/**
 * Gets the string configuration from cookie
 * @returns {string|null} The stored configuration or null if not found
 */
function getStringConfigCookie() {
    // First try to get from cookie
    const name = "stringConfig=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');
    
    for (let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i].trim();
        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
    
    return null;
}

/**
 * Updates the toggle button appearance based on its state
 */
function updateToggleButtonAppearance() {
    const toggleButton = document.getElementById('string-toggle-button');
    if (!toggleButton) {
        console.error("Toggle button not found, can't update appearance");
        return;
    }
    
    // Get current state
    const currentState = toggleButton.getAttribute('data-state');
    
    // Update appearance
    if (currentState === 'eight-string') {
        toggleButton.classList.add('eight-string-active');
        toggleButton.classList.remove('six-string-active');
    } else {
        toggleButton.classList.add('six-string-active');
        toggleButton.classList.remove('eight-string-active');
    }
}

/**
 * Applies the selected string configuration to the fretboard
 * @param {string} config - Either 'six-string' or 'eight-string'
 */
function applyStringConfiguration(config) {
    // Validate input
    if (config !== 'six-string' && config !== 'eight-string') {
        console.warn("Invalid string configuration:", config, "defaulting to six-string");
        config = 'six-string';
    }
    
    // Get fretboard container
    const fretboardContainer = document.getElementById('fretboardcontainer');
    if (!fretboardContainer) {
        console.warn('Fretboard container not found, cannot apply configuration');
        return;
    }
    
    // Update the fretboard class
    if (config === 'eight-string') {
        fretboardContainer.classList.add('eight-string-config');
        fretboardContainer.classList.remove('six-string-config');
        
        // Update global string_array if it exists to include all 8 strings
        if (typeof window.string_array !== 'undefined') {
            window.string_array = ["lowBString", "ELowString", "AString", "dString", "gString", "bString", "eString", "highAString"];
        }
    } else {
        fretboardContainer.classList.add('six-string-config');
        fretboardContainer.classList.remove('eight-string-config');
        
        // Update global string_array if it exists to include only 6 strings
        if (typeof window.string_array !== 'undefined') {
            window.string_array = ["ELowString", "AString", "dString", "gString", "bString", "eString"];
        }
    }
    
    // Update toggle button if it exists
    const toggleButton = document.getElementById('string-toggle-button');
    if (toggleButton) {
        toggleButton.setAttribute('data-state', config);
        updateToggleButtonAppearance();
    }
    
    // Update available ranges in the dropdown based on the configuration
    updateAvailableRanges(config);
    
    // Store the configuration again to ensure it's saved
    setStringConfigCookie(config, 30);
    
    // Refresh the fretboard if needed
    refreshFretboardDisplay();
}

/**
 * Updates the available ranges in the dropdown based on the string configuration
 * @param {string} config - Either 'six-string' or 'eight-string'
 */
function updateAvailableRanges(config) {
    const rangeSelect = document.getElementById('note_range');
    if (!rangeSelect) return;
    
    // Get current selected range
    const currentRange = rangeSelect.value;
    
    // Store original options if not already stored
    if (!window.originalRangeOptions) {
        window.originalRangeOptions = Array.from(rangeSelect.options).map(opt => ({
            value: opt.value,
            text: opt.textContent
        }));
    }
    
    // Filter options based on configuration
    const filteredOptions = window.originalRangeOptions.filter(opt => {
        if (config === 'six-string') {
            // Filter out options containing lowB or highA strings
            return !opt.value.includes('lowB') && !opt.value.includes('highA');
        }
        return true; // Keep all options for 8-string
    });
    
    // Clear existing options
    rangeSelect.innerHTML = '';
    
    // Add filtered options
    filteredOptions.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt.value;
        option.textContent = opt.text;
        rangeSelect.appendChild(option);
    });
    
    // Try to set previous selection, or select first available
    let selectionExists = false;
    for (let i = 0; i < rangeSelect.options.length; i++) {
        if (rangeSelect.options[i].value === currentRange) {
            rangeSelect.selectedIndex = i;
            selectionExists = true;
            break;
        }
    }
    
    // If previous selection doesn't exist, select first available
    if (!selectionExists && rangeSelect.options.length > 0) {
        rangeSelect.selectedIndex = 0;
        
        // Trigger change event to update the UI
        const event = new Event('change');
        rangeSelect.dispatchEvent(event);
    }
}

/**
 * Refresh the fretboard display to reflect the current string configuration
 */
function refreshFretboardDisplay() {
    try {
        // If there's a resetFretboard function available, use it
        if (typeof window.resetFretboard === 'function') {
            window.resetFretboard();
        }
        
        // Safe wrapper for getToneNameFromDataChords to handle the button error
        if (typeof window.getToneNameFromDataChords === 'function') {
            try {
                // Create a backup of the original function
                const originalGetToneNameFromDataChords = window.getToneNameFromDataChords;
                
                // Temporarily replace with a wrapped version that handles missing elements
                window.getToneNameFromDataChords = function() {
                    try {
                        return originalGetToneNameFromDataChords.apply(this, arguments);
                    } catch (innerError) {
                        if (innerError instanceof TypeError && innerError.message.includes("setAttribute")) {
                            // Try to recover by checking if we need to create the missing elements
                            const notesContainer = document.getElementById('notes_container');
                            if (notesContainer) {
                                // Force redraw the container in a simpler way
                                const chordTonesData = window.chord_tones_data || {};
                                if (chordTonesData.name) {
                                    // Update any UI text that might display the chord name
                                    const nameDisplay = document.getElementById('chord_name_display');
                                    if (nameDisplay) {
                                        nameDisplay.textContent = chordTonesData.name;
                                    }
                                }
                            }
                        } else {
                            console.error("Error in getToneNameFromDataChords:", innerError);
                        }
                    }
                };
                
                // Call the wrapped function
                window.getToneNameFromDataChords();
                
                // Restore the original function
                window.getToneNameFromDataChords = originalGetToneNameFromDataChords;
            } catch (wrapError) {
                console.error("Error wrapping getToneNameFromDataChords:", wrapError);
            }
        }
        
        // Trigger a redraw of the fretboard
        const rangeSelect = document.getElementById('note_range');
        if (rangeSelect) {
            try {
                const event = new Event('change');
                rangeSelect.dispatchEvent(event);
            } catch (error) {
                console.error("Error triggering range change event:", error);
            }
        }
    } catch (error) {
        console.error('Error refreshing fretboard display:', error);
    }
}
