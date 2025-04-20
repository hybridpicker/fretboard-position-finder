/**
 * Chord display optimizer
 * Enhances chord displays with better visualization and user experience
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize optimization for chords with simplified UI
    enhanceChordDisplay();
    
    // All chord UI elements removed for consistent design
    // addChordVoicingIndicators(); - removed
    // addChordToneExplanation(); - removed
    // addChordNavigation(); - removed
    // colorCodeChordTones(); - removed
});

/**
 * Enhance the chord display with additional information and styling
 */
function enhanceChordDisplay() {
    // Entire chord diagram creation disabled per user request
}


/**
 * Add chord voicing indicators (dots for each available voicing)
 */
function addChordVoicingIndicators() {
    // Only proceed if voicing_data is available
    if (typeof voicing_data === 'undefined') {
        return;
    }

    // Find the chord diagram added previously
    const chordDiagram = document.querySelector('.chord-diagram');
    if (!chordDiagram) {
        console.warn('Chord diagram not found, cannot add voicing indicators.');
        return;
    }

    // Remove existing indicators if present
    const existingIndicators = chordDiagram.querySelector('.chord-voicing-indicators');
    if (existingIndicators) {
        existingIndicators.remove();
    }


    // Create voicing indicators container
    const voicingIndicators = document.createElement('div');
    voicingIndicators.className = 'chord-voicing-indicators';

    // Get all available ranges (keys that represent range data)
    const ranges = Object.keys(voicing_data).filter(key =>
        typeof voicing_data[key] === 'object' &&
        voicing_data[key] !== null &&
        key !== 'chord' && key !== 'type' && key !== 'root' && key !== 'note_range'
    );

    if (ranges.length === 0) {
        console.warn('No valid ranges found to create voicing indicators.');
        return;
    }

    // Get current range
    const currentRange = voicing_data.note_range || ranges[0]; // Fallback to first range if not set

    // Create dots for each range
    ranges.forEach(range => {
        const dot = document.createElement('span');
        dot.className = 'chord-voicing-dot';
        dot.setAttribute('data-range', range); // Store range for potential use

        // Determine chord type category based on name
        const chordName = voicing_data.chord || '';
        if (chordName.match(/(7|9|11|13)/)) { // Simplified check for extended chords
            dot.classList.add('extended'); // Use a more general class?
        } else if (chordName.match(/(m|min)/i)) { // Check for minor explicitly
             dot.classList.add('minor');
        } else if (chordName.match(/(Maj|maj)/i) || chordName === '') { // Major or basic triad
             dot.classList.add('major');
        } else {
            dot.classList.add('other'); // Diminished, augmented, sus etc.
        }

        // Check if this is an 8-string voicing based on range name
        if (range.includes('highA') || range.includes('lowB')) {
            dot.classList.add('eight-string');
        }

        // Mark the current range
        if (range === currentRange) {
            dot.classList.add('current');
        }

        // Add tooltip with range information
        const info = document.createElement('span');
        info.className = 'chord-voicing-info';
        info.textContent = `${range} voicing`; // Keep it simple
        dot.appendChild(info);

        // Add click handler to navigate to this range
        dot.addEventListener('click', function() {
            const rangeSelect = document.getElementById('note_range');
            const form = document.getElementById('fretboard_form');

            if (rangeSelect && form) {
                // Check if the range exists as an option
                let rangeExists = false;
                for (let i = 0; i < rangeSelect.options.length; i++) {
                    if (rangeSelect.options[i].value === range) {
                        rangeExists = true;
                        break;
                    }
                }

                if (rangeExists) {
                    // Set the selected range
                    rangeSelect.value = range;
                    // Submit the form
                    form.submit();
                } else {
                    console.warn(`Range "${range}" not found in select options.`);
                    // Optionally provide user feedback here
                }
            } else {
                 console.error('Range select (#note_range) or form (#fretboard_form) not found.');
            }
        });

        voicingIndicators.appendChild(dot);
    });

    // Append voicing indicators to the chord diagram
    chordDiagram.appendChild(voicingIndicators);
}


/**
 * Add chord tone explanation (color-coded legend for root, third, fifth, etc)
 */
function addChordToneExplanation() {
    // Only proceed if voicing_data is available
    if (typeof voicing_data === 'undefined') {
        return;
    }

    // Find the chord diagram
    const chordDiagram = document.querySelector('.chord-diagram');
    if (!chordDiagram) {
         console.warn('Chord diagram not found, cannot add tone explanation.');
        return;
    }

    // Remove existing explanation if present
    const existingExplanation = chordDiagram.querySelector('.chord-tone-explanation');
    if (existingExplanation) {
        existingExplanation.remove();
    }

    // Create tone explanation container
    const toneExplanation = document.createElement('div');
    toneExplanation.className = 'chord-tone-explanation';

    // Define standard tone types and associated classes (match CSS)
    const toneMap = {
        'Root': 'root',
        '3rd': 'third', // Major 3rd
        'b3rd': 'third', // Minor 3rd - often same color, differentiate by context if needed
        '5th': 'fifth',
        'b5th': 'fifth', // Diminished 5th
        '#5th': 'fifth', // Augmented 5th
        '7th': 'seventh', // Major 7th
        'b7th': 'seventh', // Minor 7th / Dominant 7th
        '9th': 'extension', // Could be b9, 9, #9
        '11th': 'extension', // Could be 11, #11
        '13th': 'extension' // Could be b13, 13
    };

    // Determine relevant tones based on chord name (this is an approximation)
    const chordName = (voicing_data.chord || '').toLowerCase();
    let relevantTones = ['Root', '5th']; // Assume root and 5th are usually present

    if (chordName.includes('min') || chordName.includes('m') || chordName.includes('dim')) {
        relevantTones.push('b3rd');
    } else {
        relevantTones.push('3rd'); // Major, Aug, Dom, Sus (sus replaces 3rd)
    }

    if (chordName.includes('7') || chordName.includes('9') || chordName.includes('11') || chordName.includes('13')) {
        if (chordName.includes('maj7')) {
            relevantTones.push('7th');
        } else {
             relevantTones.push('b7th'); // Minor 7, Dominant 7
        }
    }
     if (chordName.includes('dim')) {
        relevantTones = relevantTones.filter(t => t !== '5th'); // Remove perfect 5th
        relevantTones.push('b5th');
        if (chordName.includes('dim7')) {
             // Dim7 has bb7 (enharmonically a 6th), often just shown as '7th' color
             // Keeping b7th for simplicity unless specific color needed
        }
    }
     if (chordName.includes('aug')) {
        relevantTones = relevantTones.filter(t => t !== '5th'); // Remove perfect 5th
        relevantTones.push('#5th');
    }

    if (chordName.includes('9')) relevantTones.push('9th');
    if (chordName.includes('11')) relevantTones.push('11th');
    if (chordName.includes('13')) relevantTones.push('13th');

     // Filter for unique class names to avoid duplicate legend items if multiple tones use the same class
     const addedClasses = new Set();
     const uniqueToneTypes = [];
     relevantTones.forEach(tone => {
         const className = toneMap[tone];
         if (className && !addedClasses.has(className)) {
             // Choose representative name for the class
             let displayName = tone;
             if (className === 'extension') displayName = 'Extensions';
             else if (className === 'third' && relevantTones.includes('b3rd')) displayName = '3rd (Major/Minor)';
             else if (className === 'seventh' && relevantTones.includes('b7th')) displayName = '7th (Major/Minor)';
              else if (className === 'fifth' && (relevantTones.includes('b5th') || relevantTones.includes('#5th'))) displayName = '5th (Perfect/Altered)';

             uniqueToneTypes.push({ name: displayName, className: className });
             addedClasses.add(className);
         } else if (!className) {
              console.warn(`No class mapping found for tone: ${tone}`);
         }
     });


    // Create legend items
    uniqueToneTypes.forEach(type => {
        const toneItem = document.createElement('div');
        toneItem.className = 'chord-tone';

        const toneColor = document.createElement('div');
        // Make sure the class name exists and is valid
        if (type.className && typeof type.className === 'string') {
            toneColor.className = `chord-tone-color ${type.className}`;
        } else {
             toneColor.className = 'chord-tone-color unknown'; // Fallback style
             console.warn(`Invalid className for tone type:`, type);
        }


        const toneName = document.createElement('span');
        toneName.textContent = type.name;

        toneItem.appendChild(toneColor);
        toneItem.appendChild(toneName);
        toneExplanation.appendChild(toneItem);
    });

    // Append tone explanation to the chord diagram if there are items to show
    if (uniqueToneTypes.length > 0) {
        chordDiagram.appendChild(toneExplanation);
    } else {
        console.warn('No relevant tones determined for legend.');
    }
}

/**
 * Enhance chord navigation with buttons for inversions and voicing types
 */
function enhanceChordNavigation() {
    // Only proceed if voicing_data is available
    if (typeof voicing_data === 'undefined') {
        return;
    }

     // Find the chord diagram
    const chordDiagram = document.querySelector('.chord-diagram');
    if (!chordDiagram) {
         console.warn('Chord diagram not found, cannot add navigation.');
        return;
    }

    // Remove existing navigation if present
    const existingNavigation = chordDiagram.querySelector('.chord-navigation');
    if (existingNavigation) {
        existingNavigation.remove();
    }
    const existingQualitySelector = chordDiagram.querySelector('.chord-quality-selector');
     if (existingQualitySelector) {
        existingQualitySelector.remove();
    }

    // Create main navigation container
    const navigation = document.createElement('div');
    navigation.className = 'chord-navigation';

    // --- Inversion Navigation ---
    const inversionNav = document.createElement('div');
    inversionNav.className = 'chord-nav-section';

    const inversionTitle = document.createElement('h4');
    inversionTitle.textContent = 'Inversions / Positions'; // More general term
    inversionNav.appendChild(inversionTitle);

    const inversionButtons = document.createElement('div');
    inversionButtons.className = 'chord-nav-buttons';

    // Get available inversions/positions dynamically
    let positions = [];
    const positionSelect = document.getElementById('position_select'); // Assuming this ID exists for positions/inversions
    const form = document.getElementById('fretboard_form'); // Need the form to submit

    if (positionSelect && positionSelect.options) {
        for (let i = 0; i < positionSelect.options.length; i++) {
            if (positionSelect.options[i].value) { // Ensure value is not empty
                 positions.push(positionSelect.options[i].value);
            }
        }
    }
    // Fallback: try getting from voicing_data for the current range
    else if (voicing_data) {
        const currentRange = voicing_data.note_range || '';
        if (currentRange && voicing_data[currentRange] && typeof voicing_data[currentRange] === 'object') {
            positions = Object.keys(voicing_data[currentRange]);
        }
    }

    // Fallback: try finding interactive elements if no select/data
    if (positions.length === 0) {
        // Example: Look for elements with data-value in a specific container
        const positionGrid = document.querySelector('#positionStepChords .grid-container'); // Adjust selector
        if (positionGrid) {
            const positionItems = positionGrid.querySelectorAll('[data-value]'); // More generic selector
            positionItems.forEach(item => {
                const value = item.getAttribute('data-value');
                if (value) {
                    positions.push(value);
                }
            });
        }
    }

    // Get current inversion/position (needs a reliable source)
    // Try the select element first, then URL param, then first available position
    let currentPosition = '';
    if (positionSelect) {
        currentPosition = positionSelect.value;
    } else {
        const urlParams = new URLSearchParams(window.location.search);
        // Use the name attribute of the select if known, or guess common names
        currentPosition = urlParams.get('position_select') || urlParams.get('inversion_select') || urlParams.get('position') || (positions.length > 0 ? positions[0] : '');
    }

     if (positions.length <= 1 && !currentPosition) {
     } else {
        // If positions array is empty but we have a current position, add it
        if (positions.length === 0 && currentPosition) {
            positions.push(currentPosition);
        }

        // Create inversion/position buttons
        positions.forEach(position => {
            const button = document.createElement('button');
            button.className = 'chord-nav-button inversion-button'; // Add specific class
            button.textContent = position.replace('Inversion', 'Inv').replace('Position', 'Pos'); // Shorten common terms
            button.setAttribute('data-position', position);

            // Mark current position/inversion
            if (position === currentPosition) {
                button.disabled = true;
                button.classList.add('current');
            }

            // Add click handler
            button.addEventListener('click', function() {
                if (positionSelect && form) {
                    // Set the selected position
                    positionSelect.value = position;
                    // Submit the form
                    form.submit();
                } else {
                    // Fallback: Modify URL if select/form not found (less reliable)
                     console.warn('Position select or form not found. Attempting URL navigation.');
                     const urlParams = new URLSearchParams(window.location.search);
                     // Try setting common parameter names
                     urlParams.set('position_select', position); // Assume this is the primary name
                     urlParams.set('position', position); // Common alternative
                     urlParams.set('inversion', position); // Another common alternative
                     const newUrl = window.location.pathname + '?' + urlParams.toString();
                     window.location.href = newUrl;
                }
            });

            inversionButtons.appendChild(button);
        });

        inversionNav.appendChild(inversionButtons);
        navigation.appendChild(inversionNav); // Add section to main navigation
    }


    // --- Voicing Type Navigation ---
    const voicingNav = document.createElement('div');
    voicingNav.className = 'chord-nav-section';

    const voicingTitle = document.createElement('h4');
    voicingTitle.textContent = 'Voicing Types';
    voicingNav.appendChild(voicingTitle);

    const voicingButtons = document.createElement('div');
    voicingButtons.className = 'chord-nav-buttons';

    // Get voicing types from available options
    let voicingTypes = [];
    const typeSelect = document.getElementById('type_options_select'); // Assumed ID for type selector

    if (typeSelect && typeSelect.options) {
        for (let i = 0; i < typeSelect.options.length; i++) {
             if (typeSelect.options[i].value) { // Ensure value is not empty
                voicingTypes.push(typeSelect.options[i].value);
            }
        }
    }
    // Fallback: try finding interactive elements
    else {
        const typeGrid = document.querySelector('#typeStepChords .grid-container'); // Adjust selector
        if (typeGrid) {
            const typeItems = typeGrid.querySelectorAll('[data-value]');
            typeItems.forEach(item => {
                const value = item.getAttribute('data-value');
                if (value) {
                    voicingTypes.push(value);
                }
            });
        }
    }


    // Get current type
    const currentType = voicing_data.type || (typeSelect ? typeSelect.value : '');

     if (voicingTypes.length <= 1 && !currentType) {
     } else {
         // If types array is empty but we have a current type, add it
         if (voicingTypes.length === 0 && currentType) {
             voicingTypes.push(currentType);
         }
          const currentRange = voicing_data.note_range || '';
          const isOn8String = currentRange.includes('highA') || currentRange.includes('lowB');


        voicingTypes.forEach(type => {
            // Basic filtering for 8-string types if not on an 8-string range
            if ((type === 'V8_1' || type === 'V8_2' || type.toLowerCase().includes('8str')) && !isOn8String) {
                return; // Skip this button
            }

            const button = document.createElement('button');
            button.className = 'chord-nav-button type-button'; // Add specific class
            button.textContent = type;
            button.setAttribute('data-type', type);

            // Mark current type
            if (type === currentType) {
                button.disabled = true;
                 button.classList.add('current');
            }

            // Add click handler
            button.addEventListener('click', function() {
                if (typeSelect && form) {
                    // Set the selected type
                    typeSelect.value = type;
                    // Submit the form
                    form.submit();
                } else {
                     // Fallback: Modify URL
                     console.warn('Type select or form not found. Attempting URL navigation.');
                     const urlParams = new URLSearchParams(window.location.search);
                     urlParams.set('type_options_select', type); // Assume this name
                     urlParams.set('type', type); // Common alternative
                     const newUrl = window.location.pathname + '?' + urlParams.toString();
                     window.location.href = newUrl;
                }
            });

            voicingButtons.appendChild(button);
        });

        voicingNav.appendChild(voicingButtons);
        navigation.appendChild(voicingNav); // Add section to main navigation
     }


    // --- Chord Quality Selector ---
    const qualitySelector = document.createElement('div');
    qualitySelector.className = 'chord-quality-selector'; // Use a distinct class name

    const qualityTitle = document.createElement('h4');
    qualityTitle.textContent = 'Chord Quality';
    qualitySelector.appendChild(qualityTitle);

    const qualityOptions = document.createElement('div');
    qualityOptions.className = 'chord-quality-options';

    // Get chord qualities/names from available options
    let chordQualities = [];
    const chordSelect = document.getElementById('chords_options_select'); // Assumed ID for chord name/quality select

    if (chordSelect && chordSelect.options) {
        for (let i = 0; i < chordSelect.options.length; i++) {
             if (chordSelect.options[i].value) {
                 chordQualities.push(chordSelect.options[i].value);
             }
        }
    }
    // Fallback: try interactive elements
    else {
        const chordGrid = document.querySelector('#chordStep .grid-container'); // Adjust selector
        if (chordGrid) {
            const chordItems = chordGrid.querySelectorAll('[data-value]');
            chordItems.forEach(item => {
                const value = item.getAttribute('data-value');
                if (value) {
                    chordQualities.push(value);
                }
            });
        }
    }


    // Get current quality/chord name
    const currentQuality = voicing_data.chord || (chordSelect ? chordSelect.value : '');


     if (chordQualities.length <= 1 && !currentQuality) {
     } else {
         // If qualities array is empty but we have a current one, add it
         if (chordQualities.length === 0 && currentQuality) {
             chordQualities.push(currentQuality);
         }

        chordQualities.forEach(quality => {
            const option = document.createElement('div'); // Use div or button as appropriate
            option.className = 'chord-quality-option';
            option.textContent = quality;
            option.setAttribute('data-quality', quality);

            // Mark current quality
            if (quality === currentQuality) {
                option.classList.add('selected'); // Use 'selected' or 'current' based on styling needs
            }

            // Add click handler
            option.addEventListener('click', function() {
                 if (quality === currentQuality) return; // Don't do anything if clicking the current one

                if (chordSelect && form) {
                    // Update the select and submit the form
                     chordSelect.value = quality;
                     form.submit();
                } else {
                     // Fallback: Update URL parameter
                     console.warn('Chord select or form not found. Attempting URL navigation.');
                     const urlParams = new URLSearchParams(window.location.search);
                     // Use the correct parameter name (might be 'chord', 'quality', 'chords_options_select', etc.)
                     urlParams.set('chords_options_select', quality); // Best guess
                     urlParams.set('chord', quality); // Common alternative
                     const newUrl = window.location.pathname + '?' + urlParams.toString();
                     window.location.href = newUrl;
                }
            });
            // *** THE FIX IS HERE: This line is now correctly inside the loop ***
            qualityOptions.appendChild(option);
        }); // End of chordQualities.forEach

        // *** THE FIX IS HERE: This line is now correctly after the loop ***
        qualitySelector.appendChild(qualityOptions);
     } // End else block for chord qualities


    // --- Fingerboard Position (Example - commented out) ---
    /*
    const fingerboardNav = document.createElement('div');
    fingerboardNav.className = 'chord-nav-section';

    const fingerboardTitle = document.createElement('h4');
    fingerboardTitle.textContent = 'Fingerboard Position';
    fingerboardNav.appendChild(fingerboardTitle);

    const fingerboardButtons = document.createElement('div');
    fingerboardButtons.className = 'chord-nav-buttons';

    const positions = ['Open', 'Fretted', 'Barre']; // Example positions
    positions.forEach(position => {
        const button = document.createElement('button');
        button.className = 'chord-nav-button fingerboard-button';
        button.textContent = position;
        button.addEventListener('click', function() {
            alert(`${position} position feature TBD`);
            // Implementation would likely involve setting a parameter and submitting form/reloading
        });
        fingerboardButtons.appendChild(button);
    });
    fingerboardNav.appendChild(fingerboardButtons);
    navigation.appendChild(fingerboardNav); // Add to main navigation if uncommented
    */


    // Append navigation elements to the chord diagram
    // Only append if they have content
    if (navigation.hasChildNodes()) { // Check if any sections were added
        chordDiagram.appendChild(navigation);
    }
    if (qualitySelector.querySelector('.chord-quality-options')?.hasChildNodes()) { // Check if quality options were added
        chordDiagram.appendChild(qualitySelector);
    }
}


/**
 * Apply color coding to chord tones on the fretboard (Basic Example)
 * NOTE: This is a basic implementation and might need significant refinement
 * based on how notes and their functions are represented in your HTML/data.
 */
function colorCodeChordTones() {
    // Only proceed if voicing_data is available
    if (typeof voicing_data === 'undefined') {
        return;
    }

    // Get the root note name (without octave)
    let rootName = '';
     if (voicing_data.root && Array.isArray(voicing_data.root) && voicing_data.root.length > 0) {
        rootName = voicing_data.root[0].replace(/[0-9]/g, '').toUpperCase();
    }
    if (!rootName) {
        console.warn('Cannot determine root note for color coding.');
        return;
    }

    // Simplified interval detection based on chord name
    const chordName = (voicing_data.chord || '').toLowerCase();
    let intervals = {}; // Map note names (relative to root) to function class

    // This is highly simplified - a robust solution needs proper music theory logic
    // Map interval numbers (semitones from root) to class names
    const intervalToClass = {
         0: 'root',    // Root
         3: 'third',   // Minor 3rd
         4: 'third',   // Major 3rd
         7: 'fifth',   // Perfect 5th
        10: 'seventh', // Minor 7th
        11: 'seventh'  // Major 7th
        // Add more intervals (b5, #5, 9, 11, 13 etc.) and classes as needed
    };

     // Basic chord type definitions (semitones from root)
     let chordIntervals = [];
     if (chordName.includes('maj')) { // Major, Major 7
         chordIntervals = [0, 4, 7];
         if (chordName.includes('7')) chordIntervals.push(11);
     } else if (chordName.includes('min') || chordName === 'm') { // Minor, Minor 7
         chordIntervals = [0, 3, 7];
         if (chordName.includes('7')) chordIntervals.push(10);
     } else if (chordName.includes('dom') || chordName === '7') { // Dominant 7
         chordIntervals = [0, 4, 7, 10];
     } else { // Default to major triad if unknown
         chordIntervals = [0, 4, 7];
     }
      // Add extensions crudely (needs refinement)
     if (chordName.includes('9')) chordIntervals.push(2); // 9th is 14 semitones (14%12 = 2)
     if (chordName.includes('11')) chordIntervals.push(5); // 11th is 17 semitones (17%12 = 5)
     if (chordName.includes('13')) chordIntervals.push(9); // 13th is 21 semitones (21%12 = 9)


    // Get all active notes on the fretboard
    const activeNotes = document.querySelectorAll('.note.active'); // Adjust selector if needed

    if (activeNotes.length === 0) {
        return;
    }

    // --- Music Theory Helper (Simple) ---
    const noteSequence = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const noteValue = (noteName) => {
        // Handle flats by converting to sharps for consistency in this simple map
        const name = noteName.toUpperCase().replace('DB', 'C#').replace('EB', 'D#').replace('GB', 'F#').replace('AB', 'G#').replace('BB', 'A#');
        return noteSequence.indexOf(name);
    };
    const getInterval = (root, target) => {
        const rootVal = noteValue(root);
        const targetVal = noteValue(target);
        if (rootVal === -1 || targetVal === -1) return -1; // Note not found
        return (targetVal - rootVal + 12) % 12; // Interval in semitones (0-11)
    };
    // --- End Helper ---


    activeNotes.forEach(noteElement => {
        // Find the note name. This depends HEAVILY on your HTML structure.
        // Option 1: From a specific class name (e.g., <div class="note active csharp">)
        let noteName = '';
        noteElement.classList.forEach(cls => {
            if (cls !== 'note' && cls !== 'active' && noteValue(cls) !== -1) { // Check if class is a valid note name
                noteName = cls.toUpperCase();
            }
        });

        // Option 2: From a data attribute (e.g., <div class="note active" data-note="C#">)
        // if (!noteName && noteElement.dataset.note) {
        //     noteName = noteElement.dataset.note.toUpperCase();
        // }

        // Option 3: From text content (e.g., <div class="note active"><span>C#</span></div>)
        // if (!noteName) {
        //    const textSpan = noteElement.querySelector('span'); // Adjust selector
        //    if (textSpan) noteName = textSpan.textContent.trim().toUpperCase();
        // }

        if (!noteName) {
            // console.warn('Could not determine note name for element:', noteElement);
            return; // Skip if note name can't be found
        }

        // Calculate interval from the chord root
        const interval = getInterval(rootName, noteName);

        if (interval !== -1) {
             // Find the class based on the calculated interval and chord type
             let functionClass = '';
             if (chordIntervals.includes(interval)) {
                 functionClass = intervalToClass[interval] || 'extension'; // Default to extension if specific interval not mapped
             } else {
                 // Note is active but not technically in the basic chord structure (e.g., passing tone?)
                 // Or could be an altered tone not yet handled.
                 functionClass = 'other-tone'; // Assign a default class for non-chord tones if needed
             }

             // Remove previous function classes before adding new one
             noteElement.classList.remove('root', 'third', 'fifth', 'seventh', 'extension', 'other-tone');

             // Apply the class
             if (functionClass) {
                 noteElement.classList.add(functionClass);
             }
        } else {
             console.warn(`Could not calculate interval for note: ${noteName}`);
        }
    });
}