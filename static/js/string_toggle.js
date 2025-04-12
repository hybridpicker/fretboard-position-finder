/**
 * String Toggle Functionality
 * Toggle between 8-string and 6-string guitar configurations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Create the toggle button
    createStringToggleButton();
    
    // Initialize the string configuration
    initializeStringConfig();
    
    // Debug: Log the current settings from storage
    console.log('String Config from storage:', getStringConfigCookie());
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
    
    // Determine initial state based on current configuration
    const fretboardContainer = document.getElementById('fretboardcontainer');
    const isEightString = fretboardContainer && fretboardContainer.classList.contains('eight-string-config');
    toggleButton.setAttribute('data-state', isEightString ? 'eight-string' : 'six-string');
    
    // Set initial appearance
    if (isEightString) {
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
    
    // Add container to the DOM
    if (fretboardContainer) {
        // Insert before the fretboard
        const fretboardParent = fretboardContainer.parentNode;
        if (fretboardParent) {
            fretboardParent.insertBefore(container, fretboardContainer);
        }
    }
}

/**
 * Initializes the string configuration based on available ranges and stored preference
 */
function initializeStringConfig() {
    // Check if 8-string ranges are available
    const has8String = checkFor8StringRanges();
    
    // Get the user's preferred configuration from cookie or localStorage
    const preferredConfig = getStringConfigCookie();
    console.log('Retrieved configuration:', preferredConfig);
    
    // Get DOM elements
    const toggleButton = document.getElementById('string-toggle-button');
    const fretboardContainer = document.getElementById('fretboardcontainer');
    
    if (!fretboardContainer) {
        console.warn('Fretboard container not found, cannot initialize string configuration');
        return;
    }
    
    // Determine which configuration to use (stored or default)
    let configState = 'six-string'; // Default to six-string
    
    if (preferredConfig && (preferredConfig === 'six-string' || preferredConfig === 'eight-string')) {
        // Use the valid stored configuration
        configState = preferredConfig;
        console.log('Using stored configuration:', configState);
    } else if (fretboardContainer.classList.contains('eight-string-config')) {
        // If no valid stored config but the container has the class
        configState = 'eight-string';
        console.log('Using class-based configuration:', configState);
    }
    
    // Set the toggle button state
    if (toggleButton) {
        toggleButton.setAttribute('data-state', configState);
        updateToggleButtonAppearance();
    }
    
    // Force apply the configuration to the fretboard
    console.log('Applying configuration:', configState);
    applyStringConfiguration(configState);
    
    // Store the current configuration (ensures consistency)
    setStringConfigCookie(configState, 30);
}

/**
 * Checks if any 8-string ranges are available in the current context
 * @returns {boolean} True if 8-string ranges are available, false otherwise
 */
function checkFor8StringRanges() {
    const ranges = document.getElementById('note_range');
    if (!ranges) return false;
    
    // Check if any 8-string ranges are available
    for (let i = 0; i < ranges.options.length; i++) {
        const range = ranges.options[i].value;
        if (range.includes('BbString') || range.includes('highAString')) {
            return true;
        }
    }
    
    return false;
}

/**
 * Toggles between 6-string and 8-string configurations
 */
function toggleStringConfiguration() {
    const toggleButton = document.getElementById('string-toggle-button');
    if (!toggleButton) return;
    
    // Get current state
    const currentState = toggleButton.getAttribute('data-state');
    
    // Toggle state
    const newState = currentState === 'eight-string' ? 'six-string' : 'eight-string';
    toggleButton.setAttribute('data-state', newState);
    
    // Update button appearance
    updateToggleButtonAppearance();
    
    // Apply the new configuration
    applyStringConfiguration(newState);
    
    // Store preference in a cookie (30 day expiration)
    setStringConfigCookie(newState, 30);
    
    // Trigger a refreshed display of notes
    refreshFretboardDisplay();
}

/**
 * Sets a cookie to store the string configuration preference
 * @param {string} config - Configuration to store ('six-string' or 'eight-string')
 * @param {number} days - Number of days until the cookie expires
 */
function setStringConfigCookie(config, days) {
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
 * Gets the string configuration from cookie or localStorage
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
    
    // If cookie failed, try localStorage
    try {
        const localConfig = localStorage.getItem('stringConfig');
        if (localConfig) {
            return localConfig;
        }
    } catch (e) {
        console.warn('Could not retrieve string configuration from localStorage:', e);
    }
    
    return null;
}

/**
 * Updates the toggle button appearance based on its state
 */
function updateToggleButtonAppearance() {
    const toggleButton = document.getElementById('string-toggle-button');
    if (!toggleButton) return;
    
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
    // Get fretboard container
    const fretboardContainer = document.getElementById('fretboardcontainer');
    if (!fretboardContainer) {
        console.warn('Fretboard container not found, cannot apply configuration');
        return;
    }
    
    console.log('Applying configuration to fretboard:', config);
    
    // Update the fretboard class
    if (config === 'eight-string') {
        fretboardContainer.classList.add('eight-string-config');
        fretboardContainer.classList.remove('six-string-config');
        
        // Update global string_array if it exists to include all 8 strings
        if (typeof window.string_array !== 'undefined') {
            // Use consistent string naming scheme across the application
            window.string_array = ["BbString", "ELowString", "AString", "dString", "gString", "bString", "eString", "highAString"];
            console.log('Updated string_array for 8-string config:', window.string_array);
        }
    } else {
        fretboardContainer.classList.add('six-string-config');
        fretboardContainer.classList.remove('eight-string-config');
        
        // Update global string_array if it exists to include only 6 strings
        if (typeof window.string_array !== 'undefined') {
            // Use consistent string naming scheme
            window.string_array = ["ELowString", "AString", "dString", "gString", "bString", "eString"];
            console.log('Updated string_array for 6-string config:', window.string_array);
        }
    }
    
    // Update available ranges in the dropdown based on the configuration
    updateAvailableRanges(config);
    
    // Store the configuration again to ensure it's saved
    setStringConfigCookie(config, 30);
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
            // Filter out options containing BbString or highAString
            return !opt.value.includes('BbString') && !opt.value.includes('highAString');
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
    // If there's a resetFretboard function available, use it
    if (typeof window.resetFretboard === 'function') {
        window.resetFretboard();
    }
    
    // If there's a getToneNameFromDataChords function, use it for chords
    if (typeof window.getToneNameFromDataChords === 'function') {
        window.getToneNameFromDataChords();
    } else if (typeof window.getNoteNameFromData === 'function') {
        // For scales/arpeggios
        window.getNoteNameFromData();
    }
    
    // Trigger a redraw of the fretboard
    const rangeSelect = document.getElementById('note_range');
    if (rangeSelect) {
        const event = new Event('change');
        rangeSelect.dispatchEvent(event);
    }
}
