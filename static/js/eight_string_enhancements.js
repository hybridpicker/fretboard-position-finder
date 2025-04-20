/**
 * Eight-String Guitar Enhancements
 * Improves the UI for 8-string guitar chord and range selection
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Create the enhanced range selector
    createEnhancedRangeSelector();
    
    // Create the inversion visualizer
    createInversionVisualizer();
    
    // Add string indicators for 8 strings
    addStringIndicators();
});

/**
 * Creates a visual range selector to make string selections more intuitive
 */
function createEnhancedRangeSelector() {
    // Get range options from the select element
    const rangeSelect = document.getElementById('note_range');
    if (!rangeSelect) {
        console.warn("Range select element not found");
        return;
    }
    
    // Get all available range options
    const ranges = [];
    for (let i = 0; i < rangeSelect.options.length; i++) {
        ranges.push({
            value: rangeSelect.options[i].value,
            text: rangeSelect.options[i].textContent.trim()
        });
    }
    
    // Get current selected range
    const currentRange = rangeSelect.options[rangeSelect.selectedIndex].value;
    
    // Create the range selector container
    const container = document.createElement('div');
    container.id = 'string-range-selector';
    container.className = 'string-range-selector';
    
    // Add title
    const title = document.createElement('h4');
    title.textContent = 'String Range';
    title.className = 'selector-title';
    container.appendChild(title);
    
    // Create a visual representation of the guitar
    const guitarContainer = document.createElement('div');
    guitarContainer.className = 'guitar-strings-container';
    
    // Add container to the main container
    container.appendChild(guitarContainer);
    
    // Insert after the range select element
    if (rangeSelect.parentNode) {
        rangeSelect.parentNode.insertBefore(container, rangeSelect.nextSibling);
    }
}

/**
 * Creates a visualization for chord inversions
 */
function createInversionVisualizer() {
    // Implementation deferred to multi-inversion-display.js
    
    // Add a chord position helper for 8-string setups
    addChordPositionHelper();
}

/**
 * Adds a chord position helper for 8-string guitar
 * - Provides available positions for each string range
 */
function addChordPositionHelper() {
    // Create a helper object mapping ranges to available positions
    const rangePositionMap = {
        'lowB - highA': ['Root Position', 'First Inversion', 'Second Inversion'],
        'lowB - e': ['Root Position', 'First Inversion', 'Second Inversion'],
        'lowB - b': ['Root Position', 'First Inversion'],
        'E - highA': ['Root Position', 'First Inversion', 'Second Inversion', 'Third Inversion'],
        'A - highA': ['Root Position', 'First Inversion', 'Second Inversion', 'Third Inversion'],
        'A - e': ['Root Position', 'First Inversion', 'Second Inversion', 'Third Inversion'],
        'default': ['Root Position', 'First Inversion', 'Second Inversion', 'Third Inversion']
    };
    
    // Store the map in window scope for other scripts to access
    window.eightStringPositionMap = rangePositionMap;
    
    // Add an event listener for range changes
    const rangeSelect = document.getElementById('note_range');
    if (rangeSelect) {
        rangeSelect.addEventListener('change', function() {
            // Get current range
            const currentRange = this.value;
            
            // Update position select options
            updatePositionSelectOptions(currentRange);
        });
        
        // Also trigger on initial load
        const currentRange = rangeSelect.value;
        updatePositionSelectOptions(currentRange);
    }
    
    /**
     * Update the position select options based on the current range
     */
    function updatePositionSelectOptions(range) {
        const positionSelect = document.getElementById('position_select');
        if (!positionSelect) return;
        
        // Get available positions for this range
        const availablePositions = rangePositionMap[range] || rangePositionMap.default;
        
        // Get current position
        const currentPosition = positionSelect.value;
        
        // Check if current position is valid for the new range
        const isCurrentPositionValid = availablePositions.includes(currentPosition);
        
        // Store original options if not already stored
        if (!window.originalPositionOptions) {
            window.originalPositionOptions = Array.from(positionSelect.options).map(opt => ({
                value: opt.value,
                text: opt.textContent
            }));
        }
        
        // Update the position select options
        if (window.originalPositionOptions) {
            // Clear existing options
            positionSelect.innerHTML = '';
            
            // Add only available positions for this range
            window.originalPositionOptions.forEach(opt => {
                if (availablePositions.includes(opt.value)) {
                    const option = document.createElement('option');
                    option.value = opt.value;
                    option.textContent = opt.text;
                    positionSelect.appendChild(option);
                }
            });
            
            // If current position is invalid, select the first available position
            if (!isCurrentPositionValid && positionSelect.options.length > 0) {
                positionSelect.selectedIndex = 0;
                
                // Trigger a change event
                const event = new Event('change');
                positionSelect.dispatchEvent(event);
            }
        }
    }
}

/**
 * Adds string indicators for 8-string guitar
 */
function addStringIndicators() {
    // Add string indicators if 8-string ranges are available
    const ranges = document.getElementById('note_range');
    if (!ranges) return;
    
    // Check if any 8-string ranges are available
    let has8String = false;
    for (let i = 0; i < ranges.options.length; i++) {
        const range = ranges.options[i].value;
        if (range.includes('lowB') || range.includes('highA')) {
            has8String = true;
            break;
        }
    }
    
    if (has8String) {
        // Add 8-string indicator to the UI
        const indicator = document.createElement('span');
        indicator.className = 'eight-string-indicator';
        indicator.textContent = '8-String';
        
        // Add to a visible element
        const container = document.querySelector('.analysis_container h2');
        if (container) {
            container.appendChild(indicator);
        }
    }
}
