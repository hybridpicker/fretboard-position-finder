document.addEventListener('DOMContentLoaded', function () {
    
    // Ensure the overlay menu is hidden initially
    const overlayMenuChords = document.getElementById('overlayMenuChords');
    if (overlayMenuChords) {
        overlayMenuChords.style.display = 'none';
    }

    /**
     * Gets URL parameters or form values with fallbacks
     * @param {string} paramName - The parameter name to retrieve
     * @param {string} defaultValue - Default value if parameter is not found
     * @returns {string} The parameter value or default
     */
    function getParameter(paramName, defaultValue) {
        const urlParams = new URLSearchParams(window.location.search);
        const urlValue = urlParams.get(paramName);
        if (urlValue) return urlValue;
        
        const element = document.getElementById(paramName);
        return element ? element.value : defaultValue;
    }
    
    /**
     * Extract valid ranges from voicing data
     * @returns {string[]} Array of valid note ranges
     */
    function getValidNoteRanges() {
        if (!voicing_data) return [];
        return Object.keys(voicing_data).filter(key => !['chord', 'type', 'root', 'note_range'].includes(key));
    }
    
    /**
     * Validate and normalize parameters against available data
     * @param {string} positionValue - The position value to validate
     * @param {string} rangeValue - The range value to validate
     * @returns {object} Object with validated position and range values
     */
    function validateParameters(positionValue, rangeValue) {
        const validRanges = getValidNoteRanges();
        let validatedRange = rangeValue;
        let validatedPosition = positionValue;
        
        // Handle numeric position "0" - always map to Root Position
        if (validatedPosition === '0' || validatedPosition === 0) {
            validatedPosition = 'Root Position';
        }
        
        // Handle "Root Position" vs "Basic Position" naming inconsistency before validation
        if (validatedPosition === 'Root Position') {
            validatedPosition = 'Basic Position';
        }
        
        // Validate range
        if (!validRanges.includes(validatedRange) && validRanges.length > 0) {
            validatedRange = validRanges[0];
        }
        
        // Validate position for the given range
        if (voicing_data[validatedRange]) {
            const validPositions = Object.keys(voicing_data[validatedRange]);
            if (!validPositions.includes(validatedPosition) && validPositions.length > 0) {
                validatedPosition = validPositions[0];
            }
        }
        
        return { position: validatedPosition, range: validatedRange };
    }

    // Define navBarFretboardChords function - handles menu interactions
    function navBarFretboardChords(class_name) {
        var elements = document.getElementsByClassName(class_name);
        
        for (var i = 0; i < elements.length; i++) {
            var element = elements[i];

            // Add a click event listener to each element with the specified class name
            element.addEventListener('click', function (e) {
                e.stopPropagation();
                closeAllSelect(this);
                this.classList.toggle('active');

                // When an item is clicked, update the tones from data chords
                var pos_val = getParameter('position_select', 'Basic Position');
                var note_range = getParameter('note_range', 'e - g');

                // Validate and normalize parameters
                const validated = validateParameters(pos_val, note_range);
                
                // Normalize type if needed
                if (voicing_data && voicing_data.type) {
                    voicing_data.type = normalizeVType(voicing_data.type);
                }

                // Update the display
                getTonesFromDataChords(validated.position, validated.range);
            });
        }
    }
    
    // Define closeAllSelect function - manages dropdown UI state
    function closeAllSelect(elmnt) {
        var x = document.getElementsByClassName('slit');
        var y = document.getElementsByClassName('sese');
        var arrNo = [];
        for (var i = 0; i < y.length; i++) {
            if (elmnt == y[i]) {
                arrNo.push(i);
            } else {
                y[i].classList.remove('slar-active');
            }
        }
        for (var i = 0; i < x.length; i++) {
            if (arrNo.indexOf(i) === -1) {
                x[i].classList.add('sehi');
            }
        }
    }
    
    // Initialize navBarFretboardChords for the specified class names
    navBarFretboardChords('sfbsfnr');  // Root note selectors
    navBarFretboardChords('catsfbsf'); // Category selectors
    navBarFretboardChords('sfbsfpos'); // Position selectors

    // Close all select boxes if the user clicks outside of them
    document.addEventListener('click', closeAllSelect);

    // Create a function to initialize the fretboard after a short delay
    function initFretboard() {
        // Only proceed if voicing_data is available
        if (typeof voicing_data === 'undefined') {
            setTimeout(initFretboard, 200);
            return;
        }

        // Get position and range parameters
        var pos_val = getParameter('position_select', 'Basic Position');
        var note_range = getParameter('note_range', 'e - g');

        // Validate parameters
        const validated = validateParameters(pos_val, note_range);
        
        // Normalize V-System type if present
        if (voicing_data && voicing_data.type) {
            voicing_data.type = normalizeVType(voicing_data.type);
        }

        // Now update the fretboard
        getTonesFromDataChords(validated.position, validated.range);
        
        // Use cursor management system if available
        if (typeof initCursorManagement === 'function') {
            initCursorManagement('chords');
        } else {
            // Fallback to basic cursor visibility
            const cursors = {
                left: document.querySelector('.left-cursor'),
                right: document.querySelector('.right-cursor')
            };
    
            if (cursors.left) {
                cursors.left.style.display = 'block';
                cursors.left.style.visibility = 'visible';
                cursors.left.style.opacity = '1';
            }
            
            if (cursors.right) {
                cursors.right.style.display = 'block';
                cursors.right.style.visibility = 'visible';
                cursors.right.style.opacity = '1';
            }
        }
        
        // After position updates, enhance chord display if function exists
        if (typeof enhanceChordDisplay === 'function') {
            setTimeout(enhanceChordDisplay, 100);
        }
    }

    // Start initialization
    initFretboard();
});

/**
 * Normalize V-System type names for consistency
 */
function normalizeVType(type) {
    if (!type) return '';
    
    // Ensure V-System notation is consistent
    const vSystemMatch = type.match(/^v[- ]?(\d+)$/i);
    if (vSystemMatch) {
        return `V-${vSystemMatch[1]}`;
    }
    
    return type;
}

/**
 * Gets tones from data for the given position and range
 * @param {string} position - The chord position/inversion
 * @param {string} range - The string range
 */
function getTonesFromDataChords(position, range) {
    
    // Handle "Root Position" vs "Basic Position" naming inconsistency
    const internalPosition = position === 'Root Position' ? 'Basic Position' : position;
    
    try {
        // Check if data is available
        if (!voicing_data) {
            console.error("voicing_data is not available");
            return;
        }
        
        // Check if range data exists
        if (!voicing_data[range]) {
            console.error(`No data found for range ${range}, available ranges:`, 
                Object.keys(voicing_data).filter(k => k !== 'chord' && k !== 'type' && k !== 'root' && k !== 'note_range'));
            return;
        }
        
        // Check if position data exists in this range
        if (!voicing_data[range][internalPosition]) {
            console.error(`No data found for position ${internalPosition} in range ${range}, available positions:`,
                Object.keys(voicing_data[range]));
            
            // Special handling for Root Position / Basic Position confusion
            if (position === 'Root Position' && voicing_data[range]['Basic Position']) {
            } else if (position === 'Basic Position' && voicing_data[range]['Root Position']) {
                // Set Basic Position equal to Root Position data
                voicing_data[range]['Basic Position'] = voicing_data[range]['Root Position'];
            } else {
                return;
            }
        }
        
        // Get the position data
        let positionData = voicing_data[range][internalPosition];
        
        // If it's an array, use the first item
        if (Array.isArray(positionData)) {
            positionData = positionData[0];
        }
        
        
        // Clear any existing active classes and reset visibility
        document.querySelectorAll('.note.active, .tone.active').forEach(el => {
            el.classList.remove('active');
        });

        // Reset all note names to hidden
        document.querySelectorAll('.notename').forEach(notename => {
            notename.style.visibility = 'hidden';
            notename.style.opacity = '0';
            notename.classList.remove('active');
            notename.classList.remove('show-name');
        });
        
        document.querySelectorAll('.root').forEach(el => {
            el.classList.remove('root');
            if (el.tagName === 'IMG') {
                // Determine octave-appropriate circle
                const noteElement = el.closest('.note');
                if (noteElement) {
                    const toneNames = Array.from(noteElement.classList).filter(cls => cls !== 'note' && cls !== 'active');
                    if (toneNames.length > 0) {
                        const toneName = toneNames[0];
                        const octaveMatch = toneName.match(/[a-z]+([0-4])/);
                        
                        if (octaveMatch && octaveMatch[1]) {
                            const octave = parseInt(octaveMatch[1]);
                            // Set appropriate SVG based on octave
                            let svgSrc = '/static/media/';
                            
                            switch (octave) {
                                case 0: svgSrc += 'circle_01.svg'; break;
                                case 1: svgSrc += 'circle_01.svg'; break;
                                case 2: svgSrc += 'circle_02.svg'; break;
                                case 3: svgSrc += 'circle_03.svg'; break;
                                case 4: svgSrc += 'circle_04.svg'; break;
                                default: svgSrc += 'circle_01.svg';
                            }
                            
                            el.src = svgSrc;
                        } else {
                            el.src = '/static/media/circle_01.svg';
                        }
                    } else {
                        el.src = '/static/media/circle_01.svg';
                    }
                } else {
                    el.src = '/static/media/circle_01.svg';
                }
            }
        });
        
        // Get chord information for intelligent note selection
        const chordRoot = voicing_data.root || '';
        const chordType = voicing_data.type || '';
        
        // Fret preferences by position and string
        const fretPreferences = getPositionFretPreferences(position, chordType);
        
        // Activate tones for each string in this position
        for (const stringName in positionData) {
            if (!positionData.hasOwnProperty(stringName)) continue;
            
            // Get note data
            const noteData = positionData[stringName];
            if (!noteData || !noteData[0]) continue;
            
            
            // Get the note name and handle both array and string formats
            let noteName, isRoot = false;
            
            if (Array.isArray(noteData)) {
                noteName = noteData[0].toLowerCase();
                // Check if this is a root note (marked with "R" or "Root")
                isRoot = noteData.length > 1 && (noteData[1] === 'R' || noteData[1] === 'Root');
            } else if (typeof noteData === 'string') {
                noteName = noteData.toLowerCase();
            } else {
                console.warn(`Unexpected note data format for ${stringName}:`, noteData);
                continue;
            }
            
            // Get base note (remove octave numbers)
            const baseNote = noteName.replace(/[0-9]/g, '');
            
            // Try finding all notes that match on this string
            let candidateElements = document.querySelectorAll(`.${stringName} .note.${baseNote}`);
            
            // If multiple matches, we need to find the best fret position
            let bestElement = null;
            
            if (candidateElements.length === 1) {
                // If only one candidate, use it
                bestElement = candidateElements[0];
            } else if (candidateElements.length > 1) {
                // Use position-specific preferences to select best note
                let bestScore = Infinity;
                
                candidateElements.forEach(el => {
                    // Get fret information
                    const fretEl = el.closest('.fret');
                    if (!fretEl) return;
                    
                    // Get fret number
                    const fretNum = getFretNumber(fretEl);
                    if (fretNum === -1) return;
                    
                    // Calculate score for this note
                    const score = scoreFretPosition(fretNum, stringName, position, fretPreferences, chordType);
                    
                    if (score < bestScore) {
                        bestScore = score;
                        bestElement = el;
                    }
                });
                
            }
            
            // If we found a best element, activate it
            if (bestElement) {
                bestElement.classList.add('active');
                
                // Also activate the tone image
                const toneEl = bestElement.querySelector('img.tone');
                if (toneEl) {
                    toneEl.classList.add('active');
                    
                    // If this is a root note, mark it specially
                    if (isRoot) {
                        toneEl.classList.add('root');
                        toneEl.src = '/static/media/red_circle.svg';
                        
                        // Make the note name visible
                        const noteNameEl = bestElement.querySelector('.notename');
                        if (noteNameEl) {
                            noteNameEl.style.visibility = 'visible';
                            noteNameEl.style.opacity = '1';
                            noteNameEl.classList.add('active');
                            noteNameEl.classList.add('show-name');
                        }
                    } else {
                        // Set appropriate octave-based circle for non-root notes
                        const toneNames = Array.from(bestElement.classList).filter(cls => cls !== 'note' && cls !== 'active');
                        if (toneNames.length > 0) {
                            const toneName = toneNames[0];
                            const octaveMatch = toneName.match(/[a-z]+([0-4])/);
                            
                            if (octaveMatch && octaveMatch[1]) {
                                const octave = parseInt(octaveMatch[1]);
                                let svgSrc = '/static/media/';
                                
                                switch (octave) {
                                    case 0: svgSrc += 'circle_01.svg'; break;
                                    case 1: svgSrc += 'circle_01.svg'; break;
                                    case 2: svgSrc += 'circle_02.svg'; break;
                                    case 3: svgSrc += 'circle_03.svg'; break;
                                    case 4: svgSrc += 'circle_04.svg'; break;
                                    default: svgSrc += 'circle_01.svg';
                                }
                                
                                toneEl.src = svgSrc;
                            }
                        }
                        
                        // Make non-root note names visible too
                        const noteNameEl = bestElement.querySelector('.notename');
                        if (noteNameEl) {
                            noteNameEl.style.visibility = 'visible';
                            noteNameEl.style.opacity = '1';
                            noteNameEl.classList.add('active');
                            noteNameEl.classList.add('show-name');
                        }
                    }
                }
            } else {
                console.warn(`No suitable element found for ${baseNote} on ${stringName}`);
            }
        }
        
        
        // Dispatch an event to notify other components
        document.dispatchEvent(new CustomEvent('chord-tones-updated', {
            detail: { position, range, success: true }
        }));
        
    } catch (error) {
        console.error(`Error updating tones:`, error);
        
        // Dispatch an event to notify other components of the failure
        document.dispatchEvent(new CustomEvent('chord-tones-updated', {
            detail: { position, range, success: false, error }
        }));
    }
}

/**
 * Get fret number from a fret element
 * @param {HTMLElement} fretEl - The fret element
 * @returns {number} The fret number (0-12), or -1 if not determined
 */
function getFretNumber(fretEl) {
    if (!fretEl) return -1;
    
    const fretNames = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 
                       'eight', 'nine', 'ten', 'eleven', 'twelve'];
    
    for (let i = 0; i < fretNames.length; i++) {
        if (fretEl.classList.contains(fretNames[i])) {
            return i;
        }
    }
    
    return -1;
}

/**
 * Get fret preferences for each position and string
 * @param {string} position - The chord position/inversion
 * @param {string} chordType - The chord type (Major, Minor, etc.)
 * @returns {object} Object mapping strings to fret preferences
 */
function getPositionFretPreferences(position, chordType) {
    // Default fret preferences per position and string
    const defaultPreferences = {
        'Root Position': {
            eString: [3, 5, 7],
            bString: [3, 5, 7],
            gString: [2, 4, 6],
            dString: [3, 5, 7],
            aString: [2, 4, 6],
            EString: [3, 5, 0]
        },
        'First Inversion': {
            eString: [8, 10, 3],
            bString: [8, 10, 5],
            gString: [5, 7, 2],
            dString: [5, 7, 3],
            aString: [3, 5, 7],
            EString: [3, 5, 0]
        },
        'Second Inversion': {
            eString: [3, 5, 7],
            bString: [8, 10, 3],
            gString: [7, 9, 4],
            dString: [7, 9, 5],
            aString: [5, 7, 2],
            EString: [5, 7, 0]
        },
        'Third Inversion': {
            eString: [11, 10, 1],
            bString: [3, 5, 8],
            gString: [9, 11, 4],
            dString: [3, 5, 8],
            aString: [8, 10, 5],
            EString: [7, 9, 11]
        }
    };
    
    // Adjust for eighth string if present
    if (document.querySelector('.BbString')) {
        defaultPreferences['Root Position'].BbString = [3, 5, 7];
        defaultPreferences['First Inversion'].BbString = [3, 5, 7];
        defaultPreferences['Second Inversion'].BbString = [7, 9, 2];
        defaultPreferences['Third Inversion'].BbString = [7, 9, 11];
    }
    
    // Handle Basic Position same as Root Position
    if (position === 'Basic Position') {
        return defaultPreferences['Root Position'];
    }
    
    // Special preference adjustments for specific chord types
    if (chordType === 'Major') {
        // For major chords, prefer more open positions in root position
        if (position === 'Root Position' || position === 'Basic Position') {
            return {
                ...defaultPreferences['Root Position'],
                eString: [0, 3, 7],  // Prefer open e string
                bString: [0, 3, 7],  // Prefer open b string
                EString: [0, 3, 7]   // Prefer open E string
            };
        }
    } else if (chordType === 'Minor') {
        // For minor chords, prefer certain fret positions
        if (position === 'Root Position' || position === 'Basic Position') {
            return {
                ...defaultPreferences['Root Position'],
                gString: [3, 5, 7]   // Adjust g string preference
            };
        }
    } else if (chordType && chordType.includes('7')) {
        // For seventh chords, adjust for comfortable fingering
        if (position === 'First Inversion') {
            return {
                ...defaultPreferences['First Inversion'],
                eString: [10, 8, 3]  // Strong preference for higher frets on e string
            };
        } else if (position === 'Second Inversion') {
            return {
                ...defaultPreferences['Second Inversion'],
                bString: [10, 8, 5]  // Strong preference for higher frets on b string
            };
        }
    }
    
    // Return default preferences for this position if no special adjustments
    return defaultPreferences[position] || defaultPreferences['Root Position'];
}

/**
 * Score a fret position for a particular string and position
 * @param {number} fretNum - The fret number to score
 * @param {string} stringName - The string name (eString, bString, etc.)
 * @param {string} position - The chord position/inversion
 * @param {object} preferences - The fret preferences
 * @param {string} chordType - The chord type
 * @returns {number} Score (lower is better)
 */
function scoreFretPosition(fretNum, stringName, position, preferences, chordType) {
    // Basic validity check
    if (fretNum === -1) return Infinity;
    
    // Get the preferences for this string or use defaults
    const stringPrefs = preferences[stringName] || [3, 5, 7];
    
    // Start with a high score
    let score = Infinity;
    
    // Calculate score based on preferences (lower is better)
    for (let i = 0; i < stringPrefs.length; i++) {
        const prefFret = stringPrefs[i];
        // Add a small penalty for lower preference order
        const prefScore = Math.abs(fretNum - prefFret) + (i * 0.1);
        
        if (prefScore < score) {
            score = prefScore;
        }
    }
    
    // Apply special bonuses or penalties based on chord type and position
    
    // For seventh chords, strongly prefer higher frets for certain strings
    if (chordType && chordType.includes('7')) {
        if (position === 'First Inversion' && stringName === 'eString') {
            score -= (fretNum >= 8) ? 2 : 0;
        } else if (position === 'Second Inversion' && stringName === 'bString') {
            score -= (fretNum >= 8) ? 2 : 0;
        }
    }
    
    // For Major chords in root position, prefer standard shapes
    if (chordType === 'Major' && (position === 'Root Position' || position === 'Basic Position')) {
        if (stringName === 'eString' || stringName === 'EString' || stringName === 'bString') {
            score -= (fretNum === 0) ? 1 : 0; // Prefer open strings for shape chords
        }
    }
    
    // For Minor chords, prefer certain fret positions
    if (chordType === 'Minor') {
        if ((position === 'Root Position' || position === 'Basic Position') && stringName === 'gString') {
            score -= (fretNum === 3) ? 1 : 0;
        }
    }
    
    // Penalize very high frets (12+) slightly 
    score += (fretNum > 12) ? 0.5 : 0;
    
    // Prefer more consistent fingering patterns (avoid extreme jumps between strings)
    if (fretNum > 7 && ['aString', 'EString'].includes(stringName)) {
        score += 0.5; // Penalize high frets on low strings
    }
    
    return score;
}

/**
 * Create synthetic V-System voicing data if missing
 */
function createSyntheticVSystemData(vType, chordType) {
    // Notes to use for chord construction
    const rootNote = voicing_data.root ? voicing_data.root[0] : 'c4';
    const rootName = rootNote.replace(/[0-9]/g, '').toLowerCase();
    
    // Get each range
    const rangeKeys = Object.keys(voicing_data).filter(
        key => !['chord', 'type', 'root', 'note_range'].includes(key)
    );
    
    // For each range
    for (const range of rangeKeys) {
        // For each position (Basic Position, First Inversion, etc.)
        if (voicing_data[range]) {
            const positions = Object.keys(voicing_data[range]);
            
            for (const pos of positions) {
                // Get the position data array
                let positionData = voicing_data[range][pos];
                
                // Convert to array format if needed
                if (!Array.isArray(positionData)) {
                    positionData = [positionData];
                    voicing_data[range][pos] = positionData;
                }
                
                // Create position object if empty
                if (!positionData[0]) {
                    positionData[0] = {};
                }
                
                // Count the note data we have
                const noteCount = Object.keys(positionData[0]).length;
                
                // For 7th chords, we need 4 notes
                if (chordType.includes('7') && noteCount < 4) {
                    
                    // Generate default voicings based on instrument
                    const voicing = createDefaultVoicing(vType, chordType, range, rootName);
                    if (voicing) {
                        // Use the synthetic voicing data
                        voicing_data[range][pos] = [voicing];
                    }
                }
            }
        }
    }
}