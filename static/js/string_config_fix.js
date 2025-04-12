/**
 * Fix for string configuration issues with 8-string ranges
 * This script ensures the string configuration is correctly set
 * and the API endpoints know about it.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get the string configuration from localStorage or cookie
    const getStringConfig = function() {
        // Try localStorage first
        let config = localStorage.getItem('stringConfiguration') || localStorage.getItem('stringConfig');
        
        // If not found in localStorage, try cookie
        if (!config) {
            const cookieName = "stringConfig=";
            const decodedCookie = decodeURIComponent(document.cookie);
            const cookieArray = decodedCookie.split(';');
            
            for (let i = 0; i < cookieArray.length; i++) {
                let cookie = cookieArray[i].trim();
                if (cookie.indexOf(cookieName) === 0) {
                    config = cookie.substring(cookieName.length, cookie.length);
                    break;
                }
            }
        }
        
        // Default to eight-string if not found
        return config || 'eight-string';
    };
    
    // Initialize string configuration if not already set
    const initStringConfig = function() {
        const config = getStringConfig();
        console.log("Current string configuration:", config);
        
        // Set cookie and localStorage to ensure consistent configuration
        document.cookie = "stringConfig=" + config + ";path=/;SameSite=Lax";
        try {
            localStorage.setItem('stringConfig', config);
            localStorage.setItem('stringConfiguration', config);
        } catch (e) {
            console.warn('Could not store string configuration in localStorage:', e);
        }
        
        console.log("String configuration initialized:", config);
        
        // Add string configuration to any API calls for chord ranges
        const patchRangesFetch = function() {
            // Store original fetch
            const originalFetch = window.fetch;
            
            // Override fetch to add string_mode parameter to range API calls
            window.fetch = function(url, options) {
                // Check if this is a chord-ranges API call
                if (typeof url === 'string' && url.includes('/api/chord-ranges/')) {
                    // Add string_mode parameter
                    const separator = url.includes('?') ? '&' : '?';
                    url = url + separator + 'string_mode=' + config;
                    console.log("Modified API call:", url);
                }
                
                // Call original fetch with modified URL
                return originalFetch.apply(this, [url, options]);
            };
        };
        
        // Apply fetch patch
        patchRangesFetch();
        
        return config;
    };
    
    // Force detect and update string configuration when range dropdown is shown
    const patchRangeDropdown = function() {
        // Watch for chord range step becoming visible
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && 
                    mutation.attributeName === 'style' &&
                    mutation.target.id === 'chordRangeStep' &&
                    mutation.target.style.display === 'block') {
                    
                    console.log("Chord range step is now visible");
                    
                    // Get current configuration
                    const config = getStringConfig();
                    console.log("Current string config when showing ranges:", config);
                    
                    // If in eight-string mode, make sure 8-string ranges are included
                    if (config === 'eight-string') {
                        // Add a short delay to let the original ranges load
                        setTimeout(function() {
                            const rangeGrid = document.querySelector('#chordRangeStep .grid-container');
                            if (rangeGrid) {
                                // Check if any 8-string ranges are already present
                                const hasEightStringRanges = Array.from(rangeGrid.querySelectorAll('.grid-item'))
                                    .some(item => {
                                        const range = item.getAttribute('data-value');
                                        return range && (range.includes('highA') || range.includes('lowB'));
                                    });
                                
                                if (!hasEightStringRanges) {
                                    console.log("No 8-string ranges found, reloading...");
                                    
                                    // Force reload by going back and forward
                                    const backButton = document.querySelector('#chordRangeStep .back-button');
                                    if (backButton) {
                                        backButton.click();
                                        
                                        // After a short delay, click the selected chord name again
                                        setTimeout(function() {
                                            const selectedChord = document.querySelector('#chordNameStep .grid-item.selected');
                                            if (selectedChord) {
                                                selectedChord.click();
                                            }
                                        }, 100);
                                    }
                                }
                            }
                        }, 100);
                    }
                }
            });
        });
        
        // Start observing
        observer.observe(document.body, { 
            attributes: true,
            subtree: true,
            attributeFilter: ['style']
        });
    };
    
    // Initialize
    const config = initStringConfig();
    
    // Apply range dropdown patch
    patchRangeDropdown();
    
    // Force set the string configuration on the fretboard container
    const fretboardContainer = document.getElementById('fretboardcontainer');
    if (fretboardContainer) {
        if (config === 'eight-string') {
            fretboardContainer.classList.add('eight-string-config');
            fretboardContainer.classList.remove('six-string-config');
        } else {
            fretboardContainer.classList.add('six-string-config');
            fretboardContainer.classList.remove('eight-string-config');
        }
    }
});
