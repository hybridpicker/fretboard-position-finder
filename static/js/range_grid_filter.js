/**
 * Enhanced note range grid filter
 * 1. Hides grid items that include 'a' or 'B' notes when in six-string mode
 * 2. Normalizes range display and ensures consistent range options
 * 3. Prioritizes standard ranges: "e-d", "b-A", "g-E"
 */

document.addEventListener('DOMContentLoaded', function() {
    // Preferred note ranges for six-string guitar (in order of preference)
    const PREFERRED_RANGES_SIX_STRING = ["a - g", "e - d", "b - A", "g - E", "d - B"];
    
    // Preferred ranges for eight-string guitar (in order of preference)
    const PREFERRED_RANGES_EIGHT_STRING = ["a - g", "e - d", "b - A", "g - E", "d - B", "highA - g", "d - lowB"];
    
    // Check if a range contains high 'a' or low 'B' string notes
    function containsEightStringNotes(rangeText) {
        // First, check explicit 8-string ranges
        if (rangeText.includes('highA') || rangeText.includes('lowB')) {
            return true;
        }
        
        // Then do the more detailed check for case-sensitive characters
        const normalizedRange = rangeText.replace(/\s+/g, '').toLowerCase();
        
        // Check for high a string (case sensitive since 'a' is high A, 'A' is A string)
        const hasHighA = normalizedRange.indexOf('a') !== -1 && 
                          normalizedRange !== normalizedRange.toUpperCase();
                          
        // Check for low B string (case sensitive since 'B' is low B, 'b' is B string)
        const hasLowB = normalizedRange.indexOf('B') !== -1 && 
                         normalizedRange !== normalizedRange.toLowerCase();
        
        return hasHighA || hasLowB;
    }
    
    // Normalize range display for consistent presentation
    function normalizeRangeDisplay(gridContainer) {
        if (!gridContainer) return;
        
        const gridItems = gridContainer.querySelectorAll('.grid-item');
        
        // First, normalize formatting of all ranges
        gridItems.forEach(function(item) {
            let rangeText = item.getAttribute('data-value');
            
            // Skip empty values
            if (!rangeText) return;
            
            // Normalize spacing around hyphen
            let normalizedRange = rangeText.replace(/\s*-\s*/g, ' - ');
            
            // Update both data-value and display text if changed
            if (normalizedRange !== rangeText) {
                item.setAttribute('data-value', normalizedRange);
                item.textContent = normalizedRange;
                console.log(`Normalized range: "${rangeText}" -> "${normalizedRange}"`);
            }
        });
    }
    
    // Prioritize standard ranges by moving them to the front
    function prioritizeStandardRanges(gridContainer, stringConfig) {
        if (!gridContainer) return;
        
        // Choose appropriate ranges based on string configuration
        const preferredRanges = stringConfig === 'six-string' ? 
            PREFERRED_RANGES_SIX_STRING : PREFERRED_RANGES_EIGHT_STRING;
            
        if (preferredRanges.length === 0) return;
        
        // Track which preferred ranges exist in the grid
        const existingPreferredItems = [];
        const gridItems = Array.from(gridContainer.querySelectorAll('.grid-item'));
        
        // First pass: identify preferred items
        gridItems.forEach(function(item) {
            const rangeText = item.getAttribute('data-value');
            if (preferredRanges.includes(rangeText)) {
                existingPreferredItems.push(item);
            }
        });
        
        // If we found any preferred items, reorder the grid
        if (existingPreferredItems.length > 0) {
            // Sort the preferred items according to the order in preferredRanges
            existingPreferredItems.sort((a, b) => {
                const rangeA = a.getAttribute('data-value');
                const rangeB = b.getAttribute('data-value');
                return preferredRanges.indexOf(rangeA) - preferredRanges.indexOf(rangeB);
            });
            
            // Remove all items from the grid
            gridItems.forEach(item => gridContainer.removeChild(item));
            
            // Add preferred items first
            existingPreferredItems.forEach(item => gridContainer.appendChild(item));
            
            // Then add non-preferred items
            gridItems.forEach(function(item) {
                if (!existingPreferredItems.includes(item)) {
                    gridContainer.appendChild(item);
                }
            });
            
            console.log('Reordered ranges to prioritize standard ranges');
        }
    }
    
    // Get current string configuration from localStorage or cookie
    function getStringConfig() {
        let stringConfig = 'eight-string'; // Default
        
        // Try to get from localStorage
        stringConfig = localStorage.getItem('stringConfiguration') || 
                       localStorage.getItem('stringConfig');
                       
        if (!stringConfig) {
            // Try cookie
            const cookieName = "stringConfig=";
            const decodedCookie = decodeURIComponent(document.cookie);
            const cookieArray = decodedCookie.split(';');
            
            for (let i = 0; i < cookieArray.length; i++) {
                let cookie = cookieArray[i].trim();
                if (cookie.indexOf(cookieName) === 0) {
                    stringConfig = cookie.substring(cookieName.length, cookie.length);
                    break;
                }
            }
        }
        
        // Default if still not found
        return stringConfig || 'eight-string';
    }
    
    // Main function to filter and normalize grid items
    function processRangeGrid(stringConfig) {
        console.log("Processing range grid for string mode:", stringConfig);
        
        // Get the grid container
        const gridContainer = document.querySelector('#chordRangeStep .grid-container');
        if (!gridContainer) return;
        
        // Normalize ranges display first
        normalizeRangeDisplay(gridContainer);
        
        // Prioritize standard ranges based on current string config
        prioritizeStandardRanges(gridContainer, stringConfig);
        
        // Get all grid items
        const gridItems = gridContainer.querySelectorAll('.grid-item');
        
        // Filter grid items based on string configuration
        gridItems.forEach(function(item) {
            const rangeText = item.getAttribute('data-value');
            
            if (stringConfig === 'six-string') {
                // In six-string mode, hide any ranges with 8-string notes
                if (containsEightStringNotes(rangeText)) {
                    item.style.display = 'none';
                    console.log(`Hiding range item "${rangeText}" in six-string mode`);
                } else {
                    item.style.display = ''; // Reset display to default
                }
            } else {
                // In eight-string mode, show all items
                item.style.display = '';
            }
        });
    }
    
    // Observer for when the chord range step becomes visible
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && 
                mutation.attributeName === 'style' &&
                mutation.target.id === 'chordRangeStep' &&
                mutation.target.style.display === 'block') {
                
                // Get current configuration
                const stringConfig = getStringConfig();
                
                // Process the range grid
                processRangeGrid(stringConfig);
            }
        });
    });
    
    // Begin observing the document body for changes
    observer.observe(document.body, { 
        attributes: true,
        subtree: true,
        attributeFilter: ['style']
    });
    
    // Also run once on load
    const chordRangeStep = document.getElementById('chordRangeStep');
    if (chordRangeStep && chordRangeStep.style.display === 'block') {
        processRangeGrid(getStringConfig());
    }
    
    // Respond to string configuration changes
    window.addEventListener('stringConfigChanged', function(e) {
        console.log('String configuration changed, updating range grid items');
        
        // Get the updated string configuration
        const updatedConfig = e.detail.config || 'eight-string';
        
        // Check if chord range step is visible
        const chordRangeStep = document.getElementById('chordRangeStep');
        if (chordRangeStep && chordRangeStep.style.display === 'block') {
            processRangeGrid(updatedConfig);
        }
    });
});
