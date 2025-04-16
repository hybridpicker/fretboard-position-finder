// FRETMarker: Script loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get all the fret cells
    const fretCells = document.querySelectorAll('.fretboard .fret');
    
    // Find the fretboard container
    const fretboard = document.querySelector('.fretboard');
    const fretboardContainer = document.getElementById('fretboardcontainer');
    
    // Create a container for the inlays
    const inlayContainer = document.createElement('div');
    inlayContainer.className = 'inlay-container';
    inlayContainer.style.position = 'absolute';
    inlayContainer.style.top = '0';
    inlayContainer.style.left = '0';
    inlayContainer.style.width = '100%';
    inlayContainer.style.height = '100%';
    inlayContainer.style.pointerEvents = 'none';
    inlayContainer.style.zIndex = '1';
    
    // Enhanced minimalistic fret markers for 6- and 8-string guitars
    // Fret numbers: III, V, VII, IX, XII, XV, XVII
    // Compatible with both 6- and 8-string visualizations
    const FRET_MARKERS = [3, 5, 7, 9, 12, 15, 17];
    // Map fret numbers to class names used in your HTML
    const FRET_CLASS_MAP = {
        3: 'three',
        5: 'five',
        7: 'seven',
        9: 'nine',
        12: 'twelve',
        15: 'fifteen',
        17: 'seventeen'
    };

    // Find all fret cells for the relevant string
    function getStringCells(stringName) {
        return Array.from(fretCells).filter(cell => cell.className.split(' ').includes(stringName));
    }

    // Get all string names based on the fret cells in the DOM
    function getStringNames() {
        const stringNames = Array.from(new Set(
            Array.from(fretCells)
                .map(cell => {
                    // Find the string class (ends with 'String')
                    return (cell.className.split(' ').find(cls => cls.endsWith('String')));
                })
                .filter(Boolean)
        ));
        return stringNames;
    }

    // Determine if we're in 6-string or 8-string mode based on container class
    function getStringMode() {
        // Check the fretboardcontainer class
        let isEightString = false;
        
        if (fretboardContainer) {
            // Primary check: Does the container have the eight-string-config class?
            isEightString = fretboardContainer.classList.contains('eight-string-config');
            
            // Or check if six-string-config class is missing (default is 8-string)
            if (!isEightString && !fretboardContainer.classList.contains('six-string-config')) {
                // Secondary check: check cookie or localstorage for configuration
                try {
                    // Check cookie for config
                    const configCookie = document.cookie
                        .split('; ')
                        .find(row => row.startsWith('stringConfig='));
                    
                    if (configCookie) {
                        isEightString = configCookie.split('=')[1] === 'eight-string';
                    } else if (localStorage.getItem('stringConfig')) {
                        // Check localStorage
                        isEightString = localStorage.getItem('stringConfig') === 'eight-string';
                    }
                } catch (e) {
                    // In case of errors, fall back to string count
                    const stringNames = getStringNames();
                    isEightString = stringNames.length >= 8;
                }
            }
        } else {
            // Fallback: if container not found, check string count
            const stringNames = getStringNames();
            isEightString = stringNames.length >= 8;
        }
        
        // Get all string names for reference
        const stringNames = getStringNames();
        
        return {
            isEightString,
            numStrings: isEightString ? 8 : 6,
            stringNames
        };
    }

    // Helper to get the vertical center of the fretboard container
    function getPlayableVerticalCenter() {
        // Try to find the top of the first string and center of the last string
        let firstStringFret = fretboard.querySelector('.fret.one.ELowString') || fretboard.querySelector('.fret.one.lowBString');
        let lastStringFret = fretboard.querySelector('.fret.one.eString');
        const boardRect = fretboard.getBoundingClientRect();
        const NUDGE_UP = 6; // px, tweak as needed

        if (firstStringFret && lastStringFret) {
            const firstRect = firstStringFret.getBoundingClientRect();
            const lastRect = lastStringFret.getBoundingClientRect();
            // Top of first string relative to fretboard
            const firstTop = firstRect.top - boardRect.top;
            // Center of last string relative to fretboard
            const lastCenter = lastRect.top - boardRect.top + (lastRect.height / 2);
            // Midpoint between first string top and last string center, nudged upward
            return firstTop + ((lastCenter - firstTop) * 0.5) - NUDGE_UP;
        }
        // Fallback: use visual center of fretboard
        return boardRect.height / 2 - NUDGE_UP;
    }

    function addMinimalisticInlay(fretNumber) {
        const { isEightString, numStrings } = getStringMode();
        const yCenter = getPlayableVerticalCenter();
        const markerColor = 'var(--color-cream)';
        const markerSize = 13;
        
        // Use appropriate offsets for double dot markers based on guitar type
        // 70px for 8-string, 35px for 6-string
        const xiiOffset = isEightString ? 70 : 35;
        
        // Find the middle string for placing markers
        const stringNames = getStringNames();
        const middleStringIndex = Math.floor(stringNames.length / 2);
        let midString = stringNames[middleStringIndex];
        
        if (fretNumber === 12) {
            // Place two markers: one above and one below the playable center
            let targetFrets = getStringCells(midString).filter(cell => 
                cell.className.includes(FRET_CLASS_MAP[fretNumber])
            );
            
            if (targetFrets.length > 0) {
                // Use the first found fret cell as reference
                const refCell = targetFrets[0];
                const rect = refCell.getBoundingClientRect();
                const boardRect = fretboard.getBoundingClientRect();
                
                // Place two dots: one above, one below center (relative to fretboard)
                [yCenter - xiiOffset, yCenter + xiiOffset].forEach((cy, i) => {
                    const inlay = document.createElement('div');
                    inlay.className = 'fret-inlay';
                    inlay.style.position = 'absolute';
                    inlay.style.width = `${markerSize}px`;
                    inlay.style.height = `${markerSize}px`;
                    inlay.style.backgroundColor = markerColor;
                    inlay.style.opacity = '0.85';
                    inlay.style.borderRadius = '50%';
                    inlay.style.left = `${rect.left - boardRect.left + rect.width / 2}px`;
                    inlay.style.top = `${cy}px`;
                    inlay.style.transform = 'translate(-50%, -50%)';
                    inlay.title = 'XII marker';
                    inlayContainer.appendChild(inlay);
                });
            } else {
                // Try with another string as fallback
                const fallbackString = isEightString ? 'gString' : 'dString';
                targetFrets = getStringCells(fallbackString).filter(cell => 
                    cell.className.includes(FRET_CLASS_MAP[fretNumber])
                );
                
                if (targetFrets.length > 0) {
                    const refCell = targetFrets[0];
                    const rect = refCell.getBoundingClientRect();
                    const boardRect = fretboard.getBoundingClientRect();
                    
                    [yCenter - xiiOffset, yCenter + xiiOffset].forEach((cy, i) => {
                        const inlay = document.createElement('div');
                        inlay.className = 'fret-inlay';
                        inlay.style.position = 'absolute';
                        inlay.style.width = `${markerSize}px`;
                        inlay.style.height = `${markerSize}px`;
                        inlay.style.backgroundColor = markerColor;
                        inlay.style.opacity = '0.85';
                        inlay.style.borderRadius = '50%';
                        inlay.style.left = `${rect.left - boardRect.left + rect.width / 2}px`;
                        inlay.style.top = `${cy}px`;
                        inlay.style.transform = 'translate(-50%, -50%)';
                        inlay.title = 'XII marker';
                        inlayContainer.appendChild(inlay);
                    });
                }
            }
        } else {
            // Single dot: playable vertical center
            let targetFret = getStringCells(midString).find(cell => 
                cell.className.includes(FRET_CLASS_MAP[fretNumber])
            );
            
            if (targetFret) {
                const rect = targetFret.getBoundingClientRect();
                const boardRect = fretboard.getBoundingClientRect();
                const inlay = document.createElement('div');
                inlay.className = 'fret-inlay';
                inlay.style.position = 'absolute';
                inlay.style.width = `${markerSize}px`;
                inlay.style.height = `${markerSize}px`;
                inlay.style.backgroundColor = markerColor;
                inlay.style.opacity = '0.7';
                inlay.style.borderRadius = '50%';
                inlay.style.left = `${rect.left - boardRect.left + rect.width / 2}px`;
                inlay.style.top = `${yCenter}px`;
                inlay.style.transform = 'translate(-50%, -50%)';
                inlay.title = `${fretNumber} marker`;
                inlayContainer.appendChild(inlay);
            } else {
                // Try with another string as fallback
                const fallbackString = isEightString ? 'gString' : 'dString';
                targetFret = getStringCells(fallbackString).find(cell => 
                    cell.className.includes(FRET_CLASS_MAP[fretNumber])
                );
                
                if (targetFret) {
                    const rect = targetFret.getBoundingClientRect();
                    const boardRect = fretboard.getBoundingClientRect();
                    const inlay = document.createElement('div');
                    inlay.className = 'fret-inlay';
                    inlay.style.position = 'absolute';
                    inlay.style.width = `${markerSize}px`;
                    inlay.style.height = `${markerSize}px`;
                    inlay.style.backgroundColor = markerColor;
                    inlay.style.opacity = '0.7';
                    inlay.style.borderRadius = '50%';
                    inlay.style.left = `${rect.left - boardRect.left + rect.width / 2}px`;
                    inlay.style.top = `${yCenter}px`;
                    inlay.style.transform = 'translate(-50%, -50%)';
                    inlay.title = `${fretNumber} marker`;
                    inlayContainer.appendChild(inlay);
                }
            }
        }
    }

    // Remove old inlays if any
    inlayContainer.innerHTML = '';
    
    // Add new inlays with appropriate timeout
    setTimeout(() => {
        FRET_MARKERS.forEach(fret => {
            addMinimalisticInlay(fret);
        });
    }, 300);

    // Add the inlay container to the fretboard
    if (fretboard) {
        fretboard.appendChild(inlayContainer);
    }

    // Handle window resize and orientation changes
    window.addEventListener('resize', updateInlays);
    window.addEventListener('orientationchange', updateInlays);
    
    // Listen for changes in the string configuration
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && 
                mutation.attributeName === 'class' && 
                fretboardContainer === mutation.target) {
                // Class changed on fretboard container - likely string config change
                updateInlays();
            }
        });
    });
    
    if (fretboardContainer) {
        observer.observe(fretboardContainer, { attributes: true });
    }
    
    // Function to update inlays
    function updateInlays() {
        // Clear existing inlays
        inlayContainer.innerHTML = '';
        // Add new inlays with recalculated positions
        setTimeout(() => {
            FRET_MARKERS.forEach(fret => {
                addMinimalisticInlay(fret);
            });
        }, 300);
    }
    
    // Also update inlays when the string toggle is used (if that feature exists)
    const stringToggle = document.getElementById('string-toggle-button');
    if (stringToggle) {
        stringToggle.addEventListener('click', function() {
            // Wait a bit longer to ensure DOM updates are complete
            setTimeout(updateInlays, 500);
        });
    }
});