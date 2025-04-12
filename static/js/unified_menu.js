// Function to force hide the menu - can be called from anywhere
function forceHideUnifiedMenu() {
    const menu = document.getElementById('unifiedOverlayMenu');
    if (menu) {
        menu.style.opacity = '0';
        setTimeout(() => {
            menu.style.display = 'none';
        }, 200);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Force hide the menu when the page loads
    setTimeout(forceHideUnifiedMenu, 100);
    const unifiedMenu = document.getElementById('unifiedOverlayMenu');
    const closeButton = document.getElementById('closeUnifiedOverlay');
    const toggleButton = document.getElementById('unifiedMenuToggle');
    
    // Check if the unified menu exists on the page
    if (!unifiedMenu) {
        console.warn('Unified overlay menu not found on page');
        return;
    }

    // Apply saved string configuration on load
    const savedConfig = localStorage.getItem('stringConfiguration');
    if (savedConfig) {
        console.log(`Applying saved string configuration: ${savedConfig}`);
        applyStringConfiguration(savedConfig); // Apply the saved setting
    } else {
        console.log('No saved string configuration found, using default.');
        applyStringConfiguration('eight-string'); // Apply default if nothing saved
    }
    
    // Set a cookie too, to ensure backend can read it
    if (savedConfig) {
        document.cookie = "stringConfig=" + savedConfig + ";path=/;SameSite=Lax";
        console.log(`Set stringConfig cookie to: ${savedConfig}`);
    } else {
        document.cookie = "stringConfig=eight-string;path=/;SameSite=Lax";
        console.log('Set stringConfig cookie to default: eight-string');
    }

    // Add toggle button event listener
    if (toggleButton) {
        toggleButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // Check if menu is currently visible
            const isVisible = unifiedMenu.style.display === 'flex' || unifiedMenu.style.display === 'block';
            
            if (!isVisible) {
                openMenu();
            } else {
                closeMenu();
            }
        });
    }

    const initialStep = document.getElementById('initialStep');
    const scaleStepsContainer = document.getElementById('scaleStepsContainer');
    const arpeggioStepsContainer = document.getElementById('arpeggioStepsContainer');
    const chordStepsContainer = document.getElementById('chordStepsContainer');

    const selectModeScaleButton = document.getElementById('selectModeScale');
    const selectModeArpeggioButton = document.getElementById('selectModeArpeggio');
    const selectModeChordButton = document.getElementById('selectModeChord');

    // --- State Management ---
    let currentSelection = {
        mode: null, // 'scale', 'arpeggio', 'chord'
        root: null, // Root ID
        type: null, // Scale/Arpeggio Notes ID OR Chord Type Name
        chordName: null, // Chord Name string
        range: null, // Chord Range string
        chordNotesId: null, // Specific ChordNotes ID for selected range
        position: null, // Position order number (0 for 'All Notes') or Chord Inversion Order string
    };

    // --- Helper Functions ---
    function showStep(stepElement) {
        if (!stepElement) {
            console.error('Step element is required for showStep');
            return;
        }

        // Hide sibling steps within the same container
        const container = stepElement.closest('.steps-container') || stepElement.parentElement;
        if (container) {
            container.querySelectorAll('.step.active-step').forEach(active => {
                if (active !== stepElement) {
                    hideStep(active);
                }
            });
        }
        
        stepElement.style.display = 'block';
        stepElement.classList.add('active-step');
    }

    function hideStep(stepElement) {
        if (stepElement) {
            stepElement.style.display = 'none';
            stepElement.classList.remove('active-step');
        }
    }

    function showContainer(containerElement) {
        if (containerElement) containerElement.style.display = 'block';
    }

    function hideContainer(containerElement) {
         if (containerElement) containerElement.style.display = 'none';
    }

    function resetActiveSteps() {
        unifiedMenu.querySelectorAll('.step.active-step').forEach(step => {
            hideStep(step);
        });
         unifiedMenu.querySelectorAll('.steps-container').forEach(container => {
            hideContainer(container);
        });
    }

    function openMenu() {
        // Reset active steps and prepare the menu
        resetActiveSteps();
        showStep(initialStep);
        
        // Set display first
        unifiedMenu.style.display = 'flex';
        
        // Then set opacity after a small delay
        requestAnimationFrame(() => {
            unifiedMenu.style.opacity = '1';
        });
    }

    function closeMenu() {
        // Fade out first
        unifiedMenu.style.opacity = '0';
        
        // Then hide after animation
        setTimeout(() => {
            unifiedMenu.style.display = 'none';
            // Reset state after closure animation begins
            currentSelection = { 
                mode: null, 
                root: null, 
                type: null, 
                chordName: null, 
                range: null, 
                chordNotesId: null, 
                position: null 
            };
            resetActiveSteps();
        }, 200);
    }

    function navigateToMode(mode, containerToShow, firstStepToShow) {
        currentSelection = { mode: mode, root: null, type: null, chordName: null, range: null, chordNotesId: null, position: null }; // Reset specific selections
        hideStep(initialStep);
        hideContainer(scaleStepsContainer);
        hideContainer(arpeggioStepsContainer);
        hideContainer(chordStepsContainer);
        showContainer(containerToShow);
        showStep(firstStepToShow);
    }

    function clearGrid(gridContainer) {
        if (gridContainer) {
            gridContainer.innerHTML = ''; // Remove all child elements
        } else {
            console.error("Attempted to clear a null grid container");
        }
    }

    function populateGrid(gridContainer, items, valueKey, textKey, idKey = null) {
        if (!gridContainer) {
            console.error("Target grid container not found for population.");
            return;
        }
        clearGrid(gridContainer);
        if (!items || items.length === 0) {
            gridContainer.innerHTML = '<p>No options available.</p>';
            return;
        }

        // Filter out invalid items and duplicates
        const uniqueItems = [];
        const seenValues = new Set();
        const seenTexts = new Set();
        
        items.forEach(item => {
            // Skip invalid items
            if (!item || item[valueKey] === undefined || item[textKey] === undefined) {
                console.warn('Skipping invalid item:', item);
                return;
            }

            const value = item[valueKey];
            const text = item[textKey];
            
            // Skip if value or text is undefined/null
            if (value === undefined || value === null || text === undefined || text === null) {
                console.warn('Skipping item with undefined/null value or text:', item);
                return;
            }
            
            // Only add if we haven't seen this value/text combination before
            const key = `${value}-${text}`;
            if (!seenValues.has(key) && !seenTexts.has(text)) {
                seenValues.add(key);
                seenTexts.add(text);
                uniqueItems.push(item);
            }
        });
        

        // Create grid items for unique items
        uniqueItems.forEach(item => {
            const div = document.createElement('div');
            div.classList.add('grid-item');
            const value = item[valueKey];
            const text = item[textKey];
            div.setAttribute('data-value', value);
            
            // Store the ID separately if needed
            if (idKey && item[idKey]) {
                div.setAttribute('data-id', item[idKey]);
            }
            
            // Add specific classes based on the container
            const containerId = gridContainer.closest('.step')?.id || '';
            
            if (containerId.includes('chordNameStep')) {
                div.classList.add('chord-name-item');
            } else if (containerId.includes('scaleTypeStep')) {
                div.classList.add('scale-type-item');
            } else if (containerId.includes('arpeggioTypeStep')) {
                div.classList.add('arpeggio-type-item');
            } else if (containerId.includes('chordTypeStep')) {
                div.classList.add('chord-type-item');
            } else if (containerId.includes('RootStep')) {
                div.classList.add('root-item');
            } else if (containerId.includes('PositionStep')) {
                div.classList.add('position-item');
            } else if (containerId.includes('RangeStep')) {
                div.classList.add('range-item');
            }
            
            // Set text content and ensure it's not empty
            if (containerId.includes('PositionStep')) {
                div.textContent = text || value || 'All Positions';
            } else {
                div.textContent = text || value || 'Unnamed Option';
            }
            
            // Add click handler
            div.addEventListener('click', handleGridItemClick);
            gridContainer.appendChild(div);
        });
    }

    // Helper function to fetch options from a given URL with parameters
    async function fetchOptions(url, params, gridContainer, nextStepElement, valueKey, textKey, idKey) {
        try {
            // Get CSRF token from cookie
            const csrfToken = getCookie('csrftoken');
            if (!csrfToken) {
                console.warn('No CSRF token found, request might fail');
            }

            // Construct the full URL with query parameters
            const queryString = new URLSearchParams(params).toString();
            const fullUrl = `${url}${queryString ? '?' + queryString : ''}`;
            
            
            // Show loading indicator
            const loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'loading-spinner';
            loadingIndicator.innerHTML = '<div class="spinner"></div>';
            gridContainer.appendChild(loadingIndicator);
            
            // Make the request with CSRF token
            const response = await fetch(fullUrl, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': csrfToken || '',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            try {
                const data = await response.json();
                processSuccessfulResponse(data, false, gridContainer, nextStepElement, valueKey, textKey, idKey);
            } catch (jsonError) {
                console.error('Error parsing JSON response:', jsonError);
                // Use fallback if JSON parsing fails
                generateFallbackGrid(gridContainer, nextStepElement);
            }
            
        } catch (error) {
            console.error('Error fetching options:', error);
            // Remove loading indicator if it exists
            const loadingIndicator = gridContainer.querySelector('.loading-spinner');
            if (loadingIndicator) {
                loadingIndicator.remove();
            }
            
            // Generate fallback grid
            generateFallbackGrid(gridContainer, nextStepElement);
        }
    }

    // Helper function to get CSRF token from cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Helper function to process a successful response
    function processSuccessfulResponse(data, isBackup, gridContainer, nextStepElement, valueKey, textKey, idKey, message = "Using default positions. Some data may be unavailable.") {
        if (!gridContainer) {
            console.error('Grid container is required for processSuccessfulResponse');
            return;
        }

        // Remove loading indicator
        const loadingIndicator = document.querySelector('.loading-spinner');
        if (loadingIndicator && loadingIndicator.parentNode) {
            loadingIndicator.parentNode.removeChild(loadingIndicator);
        }
        
        // Handle both array and object responses
        let items = [];
        if (Array.isArray(data)) {
            items = data;
        } else if (typeof data === 'object' && data !== null) {
            // Handle different response formats
            if (data.chord_names) {
                if (Array.isArray(data.chord_names)) {
                    if (data.chord_names.length > 0) {
                        if (typeof data.chord_names[0] === 'string') {
                            // Format: ['Major', 'Minor', ...]
                            items = data.chord_names.map(name => ({ [valueKey]: name, [textKey]: name }));
                        } else if (typeof data.chord_names[0] === 'object') {
                            // Format: [{ chord_name: 'Major' }, ...]
                            items = data.chord_names;
                        }
                    } else {
                        console.warn("Empty chord_names array received");
                        // Fallback for empty array
                        items = [
                            { [valueKey]: 'Major', [textKey]: 'Major' },
                            { [valueKey]: 'Minor', [textKey]: 'Minor' }
                        ];
                    }
                } else {
                    console.warn("chord_names is not an array:", data.chord_names);
                    // Fallback for invalid format
                    items = [
                        { [valueKey]: 'Major', [textKey]: 'Major' },
                        { [valueKey]: 'Minor', [textKey]: 'Minor' }
                    ];
                }
            } else if (data.ranges) {
                items = data.ranges;
            } else if (data.positions) {
                items = data.positions;
            } else {
                const dataKey = Object.keys(data)[0];
                if (data[dataKey]) {
                    items = data[dataKey];
                }
            }
        }
        
        
        if (items && items.length > 0) {
            // Transform items if needed
            const transformedItems = items.map(item => {
                if (typeof item === 'string') {
                    return { [valueKey]: item, [textKey]: item };
                }
                return item;
            });
            
            populateGrid(gridContainer, transformedItems, valueKey, textKey, idKey);
            
            // Add a notification if using backup data
            if (isBackup) {
                const existingNote = document.querySelector('.backup-notification');
                if (existingNote) {
                    existingNote.innerHTML = `<strong>Note:</strong> ${message}`;
                } else {
                    const noteDiv = document.createElement('div');
                    noteDiv.className = 'backup-notification';
                    noteDiv.innerHTML = `<strong>Note:</strong> ${message}`;
                    gridContainer.parentNode.insertBefore(noteDiv, gridContainer.nextSibling);
                }
            }
            
            if (nextStepElement) {
                showStep(nextStepElement); // Show next step only after successful population
            }
        } else {
            console.error("Invalid data structure or empty items:", data);
            clearGrid(gridContainer);
            generateFallbackGrid(gridContainer, nextStepElement);
        }
    }

    // Helper function to generate fallback grid
    function generateFallbackGrid(gridContainer, nextStepElement) {
        if (!gridContainer) {
            console.error('Grid container is required for generateFallbackGrid');
            return;
        }

        // Clear existing content
        gridContainer.innerHTML = '';

        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.style.color = '#721c24';
        errorDiv.style.backgroundColor = '#f8d7da';
        errorDiv.style.padding = '15px';
        errorDiv.style.borderRadius = '5px';
        errorDiv.style.marginBottom = '20px';
        errorDiv.innerHTML = '<p>Error loading options.</p>';
        gridContainer.appendChild(errorDiv);

        // Add default position items
        const defaultItems = [
            { value: '0', text: 'All Notes' },
            { value: '1', text: 'Position 1' },
            { value: '2', text: 'Position 2' },
            { value: '3', text: 'Position 3' },
            { value: '4', text: 'Position 4' },
            { value: '5', text: 'Position 5' }
        ];

        defaultItems.forEach(item => {
            const div = document.createElement('div');
            div.classList.add('grid-item', 'position-item');
            div.setAttribute('data-value', item.value);
            div.textContent = item.text;
            div.addEventListener('click', handleGridItemClick);
            gridContainer.appendChild(div);
        });

        // Only try to show next step if it exists
        if (nextStepElement) {
            showStep(nextStepElement);
        }
    }

    // --- Event Listeners ---
    if (closeButton) {
        closeButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            closeMenu();
        });
    } else {
        console.warn('Close button not found');
    }

    // Close the menu when clicking outside the menu content
    unifiedMenu.addEventListener('click', (event) => {
        if (event.target === unifiedMenu) {
            closeMenu();
        }
    });

    // Mode selection buttons
    if (selectModeScaleButton) {
        selectModeScaleButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            navigateToMode('scale', scaleStepsContainer, document.getElementById('scaleRootStep'));
        });
    }

    if (selectModeArpeggioButton) {
        selectModeArpeggioButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            navigateToMode('arpeggio', arpeggioStepsContainer, document.getElementById('arpeggioRootStep'));
        });
    }

    if (selectModeChordButton) {
        selectModeChordButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            navigateToMode('chord', chordStepsContainer, document.getElementById('chordRootStep'));
        });
    }
    
    // Settings button
    const selectModeSettingsButton = document.getElementById('selectModeSettings');
    const settingsContainer = document.getElementById('settingsContainer');
    const settingsStep = document.getElementById('settingsStep');
    
    if (selectModeSettingsButton && settingsContainer && settingsStep) {
        selectModeSettingsButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            navigateToMode('settings', settingsContainer, settingsStep);
        });
    }

    // Back buttons
    unifiedMenu.querySelectorAll('.back-button').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();
            const currentStep = event.target.closest('.step');
            const targetStepId = event.target.getAttribute('data-target');
            const targetStep = document.getElementById(targetStepId);
            hideStep(currentStep);
            showStep(targetStep);
            if (targetStepId === 'initialStep') {
                hideContainer(currentStep.closest('.steps-container'));
            }
        });
    });

    // Initial grid item listeners
    unifiedMenu.querySelectorAll('.grid-item').forEach(item => {
        item.addEventListener('click', handleGridItemClick);
    });
    
    // Settings apply button
    const applySettingsButton = document.getElementById('applySettings');
    if (applySettingsButton) {
        applySettingsButton.addEventListener('click', (e) => {
            console.log('Apply Settings button clicked.'); // Debug log
            e.preventDefault();
            e.stopPropagation();
            applySettings();
        });
    }

    // --- Main Grid Item Click Handler ---
    function handleGridItemClick(event) {
        const clickedItem = event.target;
        const currentStep = clickedItem.closest('.step');
        const value = clickedItem.getAttribute('data-value');
        const id = clickedItem.getAttribute('data-id');
        const stepId = currentStep.id;


        // Highlight selection
        currentStep.querySelectorAll('.grid-item.selected').forEach(selected => selected.classList.remove('selected'));
        clickedItem.classList.add('selected');

        hideStep(currentStep); // Hide current step immediately

        // --- Logic based on current step ---
        if (stepId === 'scaleRootStep' || stepId === 'arpeggioRootStep' || stepId === 'chordRootStep') {
            currentSelection.root = value;
            const nextStepId = stepId.replace('Root', 'Type');
            const nextStep = document.getElementById(nextStepId);
            const grid = nextStep.querySelector('.grid-container');
            
            // Add appropriate class to grid items
            grid.querySelectorAll('.grid-item').forEach(item => {
                if (nextStepId === 'chordTypeStep') {
                    item.classList.add('chord-type-item');
                } else if (nextStepId === 'scaleTypeStep') {
                    item.classList.add('scale-type-item');
                } else if (nextStepId === 'arpeggioTypeStep') {
                    item.classList.add('arpeggio-type-item');
                }
            });
            
            showStep(nextStep);

        } else if (stepId === 'scaleTypeStep') {
            currentSelection.type = value; // notes_id for scale
            const nextStep = document.getElementById('scalePositionStep');
            const grid = nextStep.querySelector('.grid-container');
            
            // Add position class to grid items
            grid.querySelectorAll('.grid-item').forEach(item => {
                item.classList.add('position-item');
            });
            
            // Fetch positions for the selected scale type
            fetchOptions('/api/scale-positions/', { 
                notes_id: value,
                root: currentSelection.root
            }, grid, nextStep, 'position_order', 'position_order');

        } else if (stepId === 'chordTypeStep') {
            currentSelection.type = value; // type_name for chord
            const nextStep = document.getElementById('chordNameStep');
            const grid = nextStep.querySelector('.grid-container');
            
            // Add chord type class to grid items
            grid.querySelectorAll('.grid-item').forEach(item => {
                item.classList.add('chord-name-item');
            });
            
            
            // Fetch chord names based on the selected type
            fetchOptions('/api/chord-names/', { type_name: value }, grid, nextStep, 'chord_name', 'chord_name');

        } else if (stepId === 'arpeggioTypeStep') {
            currentSelection.type = value; // notes_id for arpeggio
            const nextStep = document.getElementById('arpeggioPositionStep');
            const grid = nextStep.querySelector('.grid-container');
            
            // Add position class to grid items
            grid.querySelectorAll('.grid-item').forEach(item => {
                item.classList.add('position-item');
            });
            
            // Fetch positions for the selected arpeggio type
            fetchOptions('/api/arpeggio-positions/', { 
                notes_id: value,
                root: currentSelection.root
            }, grid, nextStep, 'position_order', 'position_order');

        } else if (stepId === 'chordNameStep') {
            // Make sure we have a valid value
            if (!value || value === 'undefined') {
                console.warn("Invalid chord name, using 'Major' as default");
                value = 'Major';
            }
            
            currentSelection.chordName = value;
            const nextStep = document.getElementById('chordRangeStep');
            const grid = nextStep.querySelector('.grid-container');
            
            // Pass type AND name to get ranges (and their IDs)
            fetchOptions('/api/chord-ranges/', { 
                type_name: currentSelection.type, 
                chord_name: value 
            }, grid, nextStep, 'range', 'range', 'id');

        } else if (stepId === 'chordRangeStep') {
            currentSelection.range = value;
            // Make sure we have a valid ID
            if (!id || id === 'undefined' || id === 'null') {
                console.warn("Invalid chord notes ID, using '1' as default");
                id = '1';
            }
            
            currentSelection.chordNotesId = id;
            const nextStep = document.getElementById('chordPositionStep');
            const grid = nextStep.querySelector('.grid-container');
            
            // Add class to grid items
            grid.querySelectorAll('.grid-item').forEach(item => {
                item.classList.add('position-item');
            });
            
            // Fetch positions for the selected chord range
            fetchOptions('/api/chord-positions/', { 
                chord_notes_id: id 
            }, grid, nextStep, 'inversion_order', 'inversion_order');

        } else if (stepId === 'scalePositionStep' || stepId === 'arpeggioPositionStep' || stepId === 'chordPositionStep') {
            // Final selection step
            currentSelection.position = value;
            
            try {
                submitSelection();
                closeMenu();
            } catch (error) {
                console.error('Error submitting selection:', error);
                alert('There was a problem applying your selection. Please try again.');
            }
        }
    }


    // --- Submission Logic (Redirect with GET parameters) ---
    function submitSelection() {
        const params = new URLSearchParams();

        // Default values to ensure we always have something valid
        const defaults = {
            root: '1',
            scaleType: '1',      // Default scale notes_id
            arpeggioType: '2',   // Default arpeggio notes_id 
            chordType: 'Triads', // Default chord type
            chordName: 'Major',  // Default chord name
            chordRange: 'e - g', // Default chord range
            position: '0'        // Default to 'All Notes'
        };

        // Set root, defaulting if missing
        if (currentSelection.root) {
            params.set('root', currentSelection.root);
        } else {
            console.warn('No root selected, using default');
            params.set('root', defaults.root);
        }

        let targetUrl = '/'; // Default URL

        if (currentSelection.mode === 'scale') {
            targetUrl = '/'; // Main URL for unified view
            params.set('models_select', '1'); // category_id for scales
            
            // Set type, defaulting if missing
            if (currentSelection.type) {
                params.set('notes_options_select', currentSelection.type);
            } else {
                console.warn('No scale type selected, using default');
                params.set('notes_options_select', defaults.scaleType);
            }
            
            // Set position, defaulting if missing
            if (currentSelection.position !== null && currentSelection.position !== undefined) {
                params.set('position_select', currentSelection.position);
            } else {
                console.warn('No position selected, using default');
                params.set('position_select', defaults.position);
            }

        } else if (currentSelection.mode === 'arpeggio') {
            targetUrl = '/'; // Use unified view URL
            params.set('models_select', '2'); // category_id for arpeggios
            
            // Set type, defaulting if missing
            if (currentSelection.type) {
                params.set('notes_options_select', currentSelection.type);
            } else {
                console.warn('No arpeggio type selected, using default');
                params.set('notes_options_select', defaults.arpeggioType);
            }
            
            // Set position, defaulting if missing
            if (currentSelection.position !== null && currentSelection.position !== undefined) {
                params.set('position_select', currentSelection.position);
            } else {
                console.warn('No position selected, using default');
                params.set('position_select', defaults.position);
            }

        } else if (currentSelection.mode === 'chord') {
            targetUrl = '/'; // Use unified view URL
            params.set('models_select', '3'); // category_id for chords
            
            // Set chord type, defaulting if missing
            if (currentSelection.type) {
                params.set('type_options_select', currentSelection.type);
            } else {
                console.warn('No chord type selected, using default');
                params.set('type_options_select', defaults.chordType);
            }
            
            // Set chord name, defaulting if missing or invalid
            if (currentSelection.chordName && currentSelection.chordName !== 'undefined') {
                params.set('chords_options_select', currentSelection.chordName);
            } else {
                console.warn('No chord name selected, using default');
                params.set('chords_options_select', defaults.chordName);
            }
            
            // Set chord range, defaulting if missing
            if (currentSelection.range && currentSelection.range !== 'undefined') {
                params.set('note_range', currentSelection.range);
            } else {
                console.warn('No chord range selected, using default');
                params.set('note_range', defaults.chordRange);
            }
            
            // Set position/inversion, defaulting if missing
            if (currentSelection.position !== null && currentSelection.position !== undefined) {
                params.set('position_select', currentSelection.position);
            } else {
                console.warn('No position selected, using default');
                params.set('position_select', defaults.position);
            }
        }

        // Add final console log to show the URL we're redirecting to
        const finalUrl = `${targetUrl}?${params.toString()}`;
        
        if (targetUrl !== '/') {
            window.location.href = finalUrl;
        } else {
            window.location.href = finalUrl;
        }
    }
    
    // Function to apply settings
    function applySettings() {
        console.log('applySettings function started.'); // Debug log
        const stringConfig = document.getElementById('string-config').value;
        
        // Apply string configuration
        applyStringConfiguration(stringConfig);
        
        // Close the menu after applying settings
        closeMenu();

        // Reload the page to ensure all changes take effect
        console.log('Attempting page reload...'); // Debug log
        location.reload();
    }
    
    // Function to apply string configuration
    function applyStringConfiguration(config) {
        // Get fretboard container
        const fretboardContainer = document.getElementById('fretboardcontainer');
        if (!fretboardContainer) return;
        
        // Default to eight-string if no config specified
        if (!config) {
            config = 'eight-string';
        }
        
        // Update the fretboard class
        if (config === 'eight-string') {
            fretboardContainer.classList.add('eight-string-config');
            fretboardContainer.classList.remove('six-string-config');
            
            // Update global string_array if it exists to include all 8 strings
            if (typeof window.string_array !== 'undefined') {
                // Check if lowBString and highAString are present
                if (!window.string_array.includes('lowBString')) {
                    window.string_array = ["lowBString", "ELowString", "AString", "dString", "gString", "bString", "eString", "highAString"];
                }
            }
        } else {
            fretboardContainer.classList.add('six-string-config');
            fretboardContainer.classList.remove('eight-string-config');
            
            // Update global string_array if it exists to include only 6 strings
            if (typeof window.string_array !== 'undefined') {
                // Filter to 6 strings
                window.string_array = ["ELowString", "AString", "dString", "gString", "bString", "eString"];
            }
        }
        
        // Update available ranges in the dropdown based on the configuration
        updateAvailableRanges(config);

        // Save the chosen configuration to localStorage
        localStorage.setItem('stringConfiguration', config);
        console.log(`Saved string configuration: ${config}`);

        // Refresh the fretboard display
        refreshFretboardDisplay();

        // Re-sync the lowest string height after applying changes, with a small delay
        // to allow DOM updates from refreshFretboardDisplay to complete.
        setTimeout(() => {
            if (typeof syncLowestStringHeight === 'function') {
                console.log('Calling syncLowestStringHeight after config change (with delay)...');
                syncLowestStringHeight();
            } else {
                console.warn('syncLowestStringHeight function not found when trying to call after config change.');
            }
        }, 100); // 100ms delay
    }
    
    // Function to update available ranges
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
                // Filter out options containing lowB or highA
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
    
    // Function to refresh the fretboard display
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

});