/**
 * Chord Note Validation
 * Advanced debugging for chord notes - verifies that the correct notes are active
 */

/**
 * Error handling wrapper for functions
 * Ensures execution continues even if errors occur
 */
function safeExecute(fn, ...args) {
    try {
        return fn(...args);
    } catch (error) {
        console.error(`Error executing function ${fn.name || 'anonymous'}:`, error);
        return null;
    }
}

document.addEventListener('DOMContentLoaded', function() {

    // Add global error handler for unhandled promise rejections
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
    });

    // Add global error handler
    window.addEventListener('error', function(event) {
        console.error('Global error caught:', event.message);
    });

    // Check if the chord data element exists and is properly formatted
    const chordDataElement = document.getElementById('chord-data');
    if (chordDataElement) {

        // Log the content for debugging
        if (chordDataElement.dataset.chordJson) {
                       chordDataElement.dataset.chordJson.substring(0, 100));

            // Check if it's valid JSON
            try {
                // Only try to parse if it starts with { or [
                const jsonStr = chordDataElement.dataset.chordJson.trim();
                if (jsonStr && (jsonStr.startsWith('{') || jsonStr.startsWith('['))) {
                    JSON.parse(jsonStr);
                } else {
                    console.warn("Chord data does not appear to be valid JSON format");
                    // Try to fix the element
                    if (window.voicing_data) {
                        try {
                            // Set the proper JSON string on the element
                            chordDataElement.dataset.chordJson = JSON.stringify(window.voicing_data);
                        } catch (e) {
                            console.error("Failed to update chord-data element:", e);
                        }
                    }
                }
            } catch (error) {
                console.warn("Invalid JSON in chord-data element:", error);
                // Try to fix the element
                if (window.voicing_data) {
                    try {
                        // Set the proper JSON string on the element
                        chordDataElement.dataset.chordJson = JSON.stringify(window.voicing_data);
                    } catch (e) {
                        console.error("Failed to update chord-data element:", e);
                    }
                }
            }
        } else {
            console.warn("Chord data element has no data-chord-json attribute");
            // Try to fix by adding data if possible
            if (window.voicing_data) {
                try {
                    // Set the JSON string on the element
                    chordDataElement.dataset.chordJson = JSON.stringify(window.voicing_data);
                } catch (e) {
                    console.error("Failed to set chord-data element:", e);
                }
            }
        }
    } else {
        console.warn("No chord-data element found in the DOM");
        // Create the element if it doesn't exist and we have data
        if (window.voicing_data) {
            try {
                const newElement = document.createElement('div');
                newElement.id = 'chord-data';
                newElement.style.display = 'none';
                newElement.dataset.chordJson = JSON.stringify(window.voicing_data);
                document.body.appendChild(newElement);
            } catch (e) {
                console.error("Failed to create chord-data element:", e);
            }
        }
    }

    // Initial validation runs after a delay to let the page fully load
    // Let's disable this for now to see if it causes timing issues
    // setTimeout(validateChordNotes, 1000);

    // Also register for chord updates
    document.addEventListener('chord-tones-updated', function(e) {
        // Add a slightly longer delay to ensure DOM updates settle
        setTimeout(validateChordNotes, 600);
    });

    // Add a hotkey for manual validation: Ctrl+Shift+V
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && e.key === 'V') {
            e.preventDefault();

            // If in DEBUG mode, make sure to show the debug panel with validation tab
            if (window.DEBUG_MODE === true) {
                showDebugPanelTab('validation');
            }
            // Explicitly call validation after ensuring tab is shown
            setTimeout(validateChordNotes, 50); // Short delay after showing tab
        }
    });

    // Only create validation panel if NOT in DEBUG mode
    // In DEBUG mode, use the unified debug panel from chord_debug.js
    if (window.DEBUG_MODE !== true) {
        createNoteValidationPanel();
    }
});

/**
 * Helper function to show the debug panel with a specific tab active
 * This can be called from anywhere to ensure the debug panel is visible
 * with the desired tab (validation, playability, etc.) selected
 */
function showDebugPanelTab(tabName) {
    // Skip if not in DEBUG mode
    if (window.DEBUG_MODE !== true) {
        return;
    }

    // First ensure the debug panel is created and visible
    if (typeof createUnifiedDebugPanel === 'function') {
        // Check if panel exists
        let panel = document.getElementById('unified-debug-panel');
        if (!panel) {
            // Create the panel if needed
            panel = createUnifiedDebugPanel();
        }

        // Make sure it's visible
        if (panel) {
            panel.style.display = 'block';
        } else {
             console.error("showDebugPanelTab: Failed to get or create panel.");
             return;
        }

        // Now try to activate the requested tab
        if (typeof activateTab === 'function') {
            activateTab(tabName);
        } else if (tabName) {
            // Fallback - try to click the tab directly
            const tab = document.getElementById(`${tabName}-tab`);
            if (tab) {
                tab.click();
            } else {
                 console.warn(`showDebugPanelTab: Could not find tab element with ID ${tabName}-tab.`);
            }
        }
    } else {
         console.warn("showDebugPanelTab: createUnifiedDebugPanel function not found.");
    }
}

// Globals to track expected and actual notes
let expectedNotes = {};
let actualNotes = {};
let mismatchCount = 0;

/**
 * Extract expected notes from voicing data
 */
function getExpectedNotes() {

    const expectedNotes = {};
    let stringCount = 0;

    // Get the chord data from the DOM
    const chordDataElement = document.getElementById('chord-data');
    if (!chordDataElement) {
        console.error("No chord data element found");
        return {};
    }

    try {
        let voicingData;

        // Try to parse the JSON from the data attribute
        if (chordDataElement.dataset.chordJson) {
            const jsonStr = chordDataElement.dataset.chordJson.trim();

            // Only attempt to parse if it looks valid
            if (jsonStr.startsWith('{') || jsonStr.startsWith('[')) {
                try {
                    voicingData = JSON.parse(jsonStr);
                } catch (parseError) {
                    console.error("Error parsing chord data JSON in getExpectedNotes:", parseError);

                    // Fallback to window.voicing_data if available
                    if (window.voicing_data && typeof window.voicing_data === 'object') {
                        voicingData = window.voicing_data;
                    } else {
                        return {};
                    }
                }
            } else {
                // If JSON string doesn't look valid, try window.voicing_data
                if (window.voicing_data && typeof window.voicing_data === 'object') {
                    voicingData = window.voicing_data;
                } else {
                    return {};
                }
            }
        } else {
            // If no data attribute at all, try window.voicing_data
            if (window.voicing_data && typeof window.voicing_data === 'object') {
                voicingData = window.voicing_data;
            } else {
                return {};
            }
        }


        // Get the current position from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const position = urlParams.get('position_select') || 'Root Position';

        // Get the position data
        const positionData = voicingData[position] || {};

        // Process each string's note data
        for (const stringName in positionData) {
            if (!positionData.hasOwnProperty(stringName)) continue;

            // Get note data
            const noteData = positionData[stringName];
            if (!noteData) continue;

            let noteName;
            let isRoot = false;

            try {
                if (Array.isArray(noteData)) {
                    noteName = noteData[0].toLowerCase();
                    // Check if this is a root note (marked with "R" or "Root")
                    isRoot = noteData.length > 1 && (noteData[1] === 'R' || noteData[1] === 'Root');
                } else if (typeof noteData === 'string') {
                    noteName = noteData.toLowerCase();
                    // For Root Position, the root note is on the g-string
                    isRoot = (position === 'Root Position' || position === 'Basic Position') && stringName === 'gString';
                } else {
                    console.warn(`Unexpected note data format for ${stringName}:`, noteData);
                    continue;
                }

                // Get base note (remove octave numbers)
                const baseNote = noteName.replace(/[0-9]/g, '');

                // Verify this is a valid note
                if (!['a', 'as', 'bb', 'b', 'c', 'cs', 'db', 'd', 'ds', 'eb', 'e', 'f', 'fs', 'gb', 'g', 'gs', 'ab']
                    .includes(baseNote)) {
                    console.warn(`Invalid note name: ${baseNote} from ${noteName}`);
                    continue;
                }

                // Store the expected note
                if (!expectedNotes[stringName]) {
                    expectedNotes[stringName] = [];
                }

                expectedNotes[stringName].push({
                    note: noteName, // Use full name with octave
                    baseNote: baseNote, // Store the base note without octave separately
                    isRoot: isRoot,
                    fullName: noteName
                });

                stringCount++;
            } catch (error) {
                console.error(`Error processing note data for ${stringName}:`, error, noteData);
            }
        }
    } catch (error) {
        console.error("Error parsing chord data:", error);
    }

    // Log a warning if we found very few strings with notes
    if (stringCount <= 1) {
        console.warn(`Only found ${stringCount} strings with valid notes. Data may be incomplete.`);
    }

    return expectedNotes;
}

/**
 * Get the actually active notes from the DOM
 */
function getActiveNotes() {

    // Reset active notes
    actualNotes = {};

    // First, let's check which strings we have in the DOM
    const stringElements = document.querySelectorAll('[class*="String"]');
    const stringNames = new Set();

    // Extract string names
    stringElements.forEach(el => {
        const className = el.className;
        const stringMatch = className.match(/[A-Za-z]+String/);
        if (stringMatch) {
            stringNames.add(stringMatch[0]);
        }
    });


    // Now check which notes are active on each string
    stringNames.forEach(stringName => {
        actualNotes[stringName] = [];

        // Get all active notes on this string
        const activeNotes = document.querySelectorAll(`.${stringName} .note.active`);

        activeNotes.forEach(noteEl => {
            // Extract the note name from class
            const noteClasses = noteEl.className.split(' ');
            let noteName = null;

            // Define valid note names explicitly
            const validNoteNames = ['a', 'ab', 'as', 'b', 'bb', 'c', 'cs', 'db', 'd', 'ds', 'eb', 'e', 'f', 'fs', 'gb', 'g', 'gs'];

            // Find the first class that matches a valid note name - handle octave numbers
            for (const cls of noteClasses) {
                // Extract base note without octave
                const baseNote = cls.replace(/[0-9]/g, '');
                if (validNoteNames.includes(baseNote)) {
                    noteName = cls; // Keep the original class with octave
                    break;
                }
            }

            if (!noteName) {
                console.warn(`Could not determine note name for active note on ${stringName}:`, noteEl);
                return;
            }

            // Check if it's a root note
            const toneEl = noteEl.querySelector('img.tone');
            const isRoot = toneEl ? toneEl.classList.contains('root') : false;

            // Get fret information
            const fretEl = noteEl.closest('.fret');
            let fretName = "unknown";
            let fretNumber = -1;

            if (fretEl) {
                const fretClasses = fretEl.className.split(' ');
                const fretMap = {
                    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
                    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
                    'ten': 10, 'eleven': 11, 'twelve': 12
                };

                for (const cls of fretClasses) {
                    if (fretMap.hasOwnProperty(cls)) {
                        fretName = cls;
                        fretNumber = fretMap[cls];
                        break;
                    }
                }
            }

            // Add to active notes
            actualNotes[stringName].push({
                note: noteName,
                isRoot: isRoot,
                fret: fretName,
                fretNumber: fretNumber,
                element: noteEl // Keep element reference if needed for fixes, but don't stringify it
            });
        });
    });

    return actualNotes;
}

/**
 * Compare expected vs actual notes and highlight mismatches
 */
function validateChordNotes() {

    const result = {
        mismatchCount: 0,
        expectedTotal: 0,
        actualTotal: 0,
        success: false,
        mismatches: [], // Array to hold detailed mismatch info
        error: null
    };

    try {
        // 1. Get Expected Notes
        const expectedNotesData = getExpectedNotes(); // Format: { stringName: [{ note, baseNote, isRoot, fullName }, ...], ... }
        if (!expectedNotesData) {
            // This case should ideally not happen if getExpectedNotes handles errors, but check anyway
            console.error(">>> validateChordNotes: CRITICAL - getExpectedNotes returned null/undefined.");
            result.error = "Failed to retrieve expected notes data.";
            updateValidationUI(result);
            window.lastValidationResult = result;
            return result;
        }
         // Check if expectedNotesData is empty, which might be valid (e.g., no chord selected)
         if (Object.keys(expectedNotesData).length === 0) {
             console.warn(">>> validateChordNotes: No expected notes data found (potentially valid if no chord selected).");
             // Continue validation to check for unexpected active notes
         } else {
         }


        // 2. Get Actual Notes
        const actualNotesData = getActiveNotes(); // Format: { stringName: [{ note, isRoot, fret, fretNumber, element }, ...], ... }
        if (!actualNotesData) {
            console.error(">>> validateChordNotes: CRITICAL - Failed to get actual notes from DOM.");
            result.error = "Failed to get actual notes from DOM.";
            updateValidationUI(result);
            window.lastValidationResult = result;
            return result;
        } else {
        }

        // 3. Compare Notes
        const allStrings = new Set([...Object.keys(expectedNotesData), ...Object.keys(actualNotesData)]);

        allStrings.forEach(stringName => {
            const expectedOnString = expectedNotesData[stringName] || []; // Expected notes for this string
            const actualOnString = actualNotesData[stringName] || [];   // Actual notes found on this string

            result.expectedTotal += expectedOnString.length;
            result.actualTotal += actualOnString.length;

            // --- Refined Comparison Logic ---

            // Create sets for easier comparison (using full note name + root status)
            // Example item: "c4_root" or "g#3_nonroot"
            const expectedSet = new Set(expectedOnString.map(n => `${n.note}_${n.isRoot ? 'root' : 'nonroot'}`));
            const actualSet = new Set(actualOnString.map(n => `${n.note}_${n.isRoot ? 'root' : 'nonroot'}`));

            // Find Missing Notes (in expected but not in actual)
            expectedOnString.forEach(expNote => {
                const expectedKey = `${expNote.note}_${expNote.isRoot ? 'root' : 'nonroot'}`;
                if (!actualSet.has(expectedKey)) {
                    result.mismatchCount++;
                    // Try to find *any* actual note on the string to report against, otherwise report null
                    const closestActual = actualOnString.find(a => a.note === expNote.note) || actualOnString[0] || null;
                    result.mismatches.push({
                        string: stringName,
                        type: 'Missing or Incorrect Note/Root',
                        expected: expNote, // { note, baseNote, isRoot, fullName }
                        actual: closestActual ? { note: closestActual.note, isRoot: closestActual.isRoot, fret: closestActual.fretNumber } : null, // Report what *was* found, if anything
                        message: `Expected ${expNote.note} (${expNote.isRoot ? 'Root' : 'Non-Root'}) but not found or incorrect.`
                    });
                }
            });

            // Find Unexpected Notes (in actual but not in expected)
            actualOnString.forEach(actNote => {
                const actualKey = `${actNote.note}_${actNote.isRoot ? 'root' : 'nonroot'}`;
                if (!expectedSet.has(actualKey)) {
                    result.mismatchCount++;
                     // Try to find *any* expected note on the string to report against
                    const closestExpected = expectedOnString.find(e => e.note === actNote.note) || expectedOnString[0] || null;
                    result.mismatches.push({
                        string: stringName,
                        type: 'Unexpected or Incorrect Note/Root',
                        expected: closestExpected, // Report what *was* expected, if anything
                        actual: { note: actNote.note, isRoot: actNote.isRoot, fret: actNote.fretNumber }, // { note, isRoot, fret, fretNumber }
                        message: `Found unexpected ${actNote.note} (${actNote.isRoot ? 'Root' : 'Non-Root'}) or incorrect status.`
                    });
                }
            });
        }); // End of loop through strings

        result.success = result.mismatchCount === 0 && result.error === null;

    } catch (error) {
        console.error(">>> validateChordNotes: Error during validation process:", error);
        result.error = `Validation failed: ${error.message}`;
        result.success = false;
    }

    // 4. Update UI
    updateValidationUI(result);

    // Store the last result globally for potential debugging or re-use
    window.lastValidationResult = result;
    return result;
}

/**
 * Helper function to update the validation UI elements (list and status)
 */
function updateValidationUI(result) {

    // --- Populate the validation error list ---
    const errorListElement = document.getElementById('validation-error-list');
    if (errorListElement) {
        // Clear previous errors
        errorListElement.innerHTML = '';

        if (result.mismatches && result.mismatches.length > 0) {
            result.mismatches.forEach(mismatch => {
                const listItem = document.createElement('li');
                let expectedText = mismatch.expected ? `${mismatch.expected.note || mismatch.expected.baseNote} (${mismatch.expected.isRoot ? 'Root' : 'Non-root'})` : 'None';
                let actualText = 'None';
                 if (mismatch.actual) {
                     // Avoid stringifying element references if present
                     const actualData = Array.isArray(mismatch.actual) ? mismatch.actual : [mismatch.actual];
                     actualText = actualData.map(n => `${n.note} (Fret ${n.fretNumber})`).join(', ');
                 }

                listItem.textContent = `String ${mismatch.string}: ${mismatch.type} (Expected ${expectedText}, Found ${actualText})`;
                listItem.style.color = '#FF6B6B'; // Style errors in red
                listItem.style.marginBottom = '3px';
                errorListElement.appendChild(listItem);
            });
        } else if (result.success) {
             const listItem = document.createElement('li');
             listItem.textContent = 'Validation successful: All notes match.';
             listItem.style.color = '#6BFF6B'; // Style success in green
             errorListElement.appendChild(listItem);
        } else {
             const listItem = document.createElement('li');
             listItem.textContent = `Validation ${result.error ? 'failed' : 'status uncertain'}. ${result.error || 'No specific mismatches found.'}`;
             listItem.style.color = result.error ? '#FF6B6B' : '#FFFF6B'; // Style uncertain/failed
             errorListElement.appendChild(listItem);
        }
    } else {
        console.warn("[updateValidationUI] Could not find validation-error-list element.");
    }

    // --- Update the validation status text ---
    // Find the status element within the validation content container for robustness
    const validationContent = document.getElementById('validation-content');
    const statusElement = validationContent ? validationContent.querySelector('#validation-status') : null;

    if (statusElement) {
        let statusText = '';
        let statusColor = '#AAAAAA'; // Default grey

        if (result.success) {
            statusText = 'Validation status: Success';
            statusColor = '#6BFF6B'; // Green
        } else if (result.error) {
            statusText = `Validation status: Failed (${result.error})`;
            statusColor = '#FF6B6B'; // Red
        } else if (result.mismatchCount > 0) {
            statusText = `Validation status: Failed (${result.mismatchCount} mismatch${result.mismatchCount > 1 ? 'es' : ''})`;
            statusColor = '#FF6B6B'; // Red
        } else {
            // If no error and no mismatches, but not success
            statusText = 'Validation status: Uncertain';
            statusColor = '#FFFF6B'; // Yellow
        }
        try {
            statusElement.textContent = statusText;
            statusElement.style.color = statusColor;
        } catch (e) {
            console.error("[updateValidationUI] Error updating statusElement:", e);
        }

    } else {
         console.warn("[updateValidationUI] Could not find validation-status element to update.");
    }

    // Update the standalone validation panel if it exists and not in DEBUG mode
    if (window.DEBUG_MODE !== true && typeof updateValidationPanel === 'function') {
        updateValidationPanel(result); // Pass the result object
    }
}


/**
 * Create a panel for displaying validation results
 * This is only used when not in DEBUG_MODE, otherwise
 * the validation goes into the unified debug panel
 */
function createNoteValidationPanel() {
    // If in DEBUG_MODE, we don't create the separate panel at all
    if (window.DEBUG_MODE === true) {
        return;
    }

    // Check if it already exists
    if (document.getElementById('note-validation-panel')) return;

    // Create panel elements
    const panel = document.createElement('div');
    panel.id = 'note-validation-panel';
    panel.style.position = 'fixed';
    panel.style.bottom = '10px';
    panel.style.right = '10px';
    panel.style.width = '320px';
    panel.style.padding = '10px';
    panel.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    panel.style.color = '#FFFFFF';
    panel.style.zIndex = '9999';
    panel.style.border = '1px solid #00FF00';
    panel.style.fontFamily = 'monospace';
    panel.style.fontSize = '12px';
    panel.style.maxHeight = '400px';
    panel.style.overflowY = 'auto';
    panel.style.display = 'none'; // Hidden by default

    // Add title
    const title = document.createElement('div');
    title.style.borderBottom = '1px solid #00FF00';
    title.style.paddingBottom = '5px';
    title.style.marginBottom = '5px';
    title.style.fontWeight = 'bold';
    title.textContent = 'Chord Note Validation (Ctrl+Shift+N)';
    panel.appendChild(title);

    // Status element
    const statusEl = document.createElement('div');
    statusEl.id = 'validation-status'; // Note: ID conflict if unified panel also exists
    statusEl.style.marginBottom = '10px';
    statusEl.textContent = 'Validation status: Not run yet';
    panel.appendChild(statusEl);

    // Results container
    const resultsContainer = document.createElement('div');
    resultsContainer.id = 'validation-results'; // Note: ID conflict if unified panel also exists
    panel.appendChild(resultsContainer);

    // Action buttons
    const buttonContainer = document.createElement('div');
    buttonContainer.style.marginTop = '10px';
    buttonContainer.style.display = 'flex';
    buttonContainer.style.justifyContent = 'space-between';

    // Validate button
    const validateButton = document.createElement('button');
    validateButton.textContent = 'Validate Now';
    validateButton.onclick = validateChordNotes;
    buttonContainer.appendChild(validateButton);

    // Fix button - attempts to automatically correct issues
    const fixButton = document.createElement('button');
    fixButton.textContent = 'Auto-Fix';
    fixButton.onclick = attemptAutoFix;
    buttonContainer.appendChild(fixButton);

    // Force page reload button
    const reloadButton = document.createElement('button');
    reloadButton.textContent = 'Force Reload';
    reloadButton.onclick = forcePageReload;
    reloadButton.style.backgroundColor = '#FF5555';
    reloadButton.style.color = 'white';
    buttonContainer.appendChild(reloadButton);

    // Add another row of buttons
    const buttonContainer2 = document.createElement('div');
    buttonContainer2.style.marginTop = '8px';
    buttonContainer2.style.display = 'flex';
    buttonContainer2.style.justifyContent = 'space-between';

    // Fix from voicing data button
    const fixDataButton = document.createElement('button');
    fixDataButton.textContent = 'Fix from Data';
    fixDataButton.onclick = function() {
        const urlParams = new URLSearchParams(window.location.search);
        const position = urlParams.get('position_select') || 'Root Position';
        const range = urlParams.get('note_range') || 'e - g';
        fixFromVoicingData(position, range);
        setTimeout(validateChordNotes, 300);
    };
    buttonContainer2.appendChild(fixDataButton);

    // Debug info button
    const debugButton = document.createElement('button');
    debugButton.textContent = 'Log Data';
    debugButton.onclick = function() {
        const urlParams = new URLSearchParams(window.location.search);
        const position = urlParams.get('position_select') || 'Root Position';
        const range = urlParams.get('note_range') || 'e - g';
    };
    buttonContainer2.appendChild(debugButton);

    // Toggle visibility button
    const toggleButton = document.createElement('button');
    toggleButton.textContent = 'Hide Panel';
    toggleButton.onclick = function() {
        panel.style.display = 'none';
    };
    buttonContainer2.appendChild(toggleButton);

    panel.appendChild(buttonContainer);
    panel.appendChild(buttonContainer2);

    // Add to the document
    document.body.appendChild(panel);

    // Add keyboard shortcut
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && e.key === 'N') {
            e.preventDefault();
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';

            if (panel.style.display === 'block') {
                validateChordNotes();
            }
        }
    });
}

/**
 * Force a page reload with cleaned parameters
 */
function forcePageReload() {
    if (confirm("This will reload the page. Continue?")) {
        // Get current parameters
        const urlParams = new URLSearchParams(window.location.search);
        const position = urlParams.get('position_select') || 'Root Position';
        const range = urlParams.get('note_range') || 'e - g';
        const chord = urlParams.get('chord_select') || 'C';
        const type = urlParams.get('chords_options_select') || 'Major';

        // Build new clean URL
        const newParams = new URLSearchParams();
        newParams.set('position_select', position);
        newParams.set('note_range', range);
        if (chord) newParams.set('chord_select', chord);
        if (type) newParams.set('chords_options_select', type);

        // Reload with clean URL
        window.location.href = window.location.pathname + '?' + newParams.toString();
    }
}

/**
 * Update the validation panel with the latest results
 * NOTE: This function updates the *standalone* panel, not the unified one.
 * It needs the result object from validateChordNotes.
 */
function updateValidationPanel(result) {
    // Only run if not in DEBUG mode (where unified panel is used)
    if (window.DEBUG_MODE === true) return;

    const panel = document.getElementById('note-validation-panel');
    if (!panel) return;

    const statusEl = panel.querySelector('#validation-status'); // Use querySelector within panel
    const resultsContainer = panel.querySelector('#validation-results'); // Use querySelector within panel

    if (!statusEl || !resultsContainer) return;

    // Update status text and color based on the result object
    if (result) {
        if (result.success) {
            statusEl.textContent = 'Validation status: Success';
            statusEl.style.color = '#6BFF6B';
        } else if (result.error) {
            statusEl.textContent = `Validation status: Failed (${result.error})`;
            statusEl.style.color = '#FF6B6B';
        } else if (result.mismatchCount > 0) {
            statusEl.textContent = `Validation status: Failed (${result.mismatchCount} mismatch${result.mismatchCount > 1 ? 'es' : ''})`;
            statusEl.style.color = '#FF6B6B';
        } else {
            statusEl.textContent = 'Validation status: Uncertain';
            statusEl.style.color = '#FFFF6B';
        }

        // Update results list
        resultsContainer.innerHTML = ''; // Clear previous results
        if (result.mismatches && result.mismatches.length > 0) {
            const list = document.createElement('ul');
            list.style.listStyleType = 'none';
            list.style.paddingLeft = '0';
            result.mismatches.forEach(mismatch => {
                const listItem = document.createElement('li');
                 let expectedText = mismatch.expected ? `${mismatch.expected.note || mismatch.expected.baseNote} (${mismatch.expected.isRoot ? 'Root' : 'Non-root'})` : 'None';
                 let actualText = 'None';
                  if (mismatch.actual) {
                      // Avoid stringifying element references if present
                      const actualData = Array.isArray(mismatch.actual) ? mismatch.actual : [mismatch.actual];
                      actualText = actualData.map(n => `${n.note} (Fret ${n.fretNumber})`).join(', ');
                  }
                 listItem.textContent = `String ${mismatch.string}: ${mismatch.type} (Expected ${expectedText}, Found ${actualText})`;
                 listItem.style.color = '#FF6B6B';
                 listItem.style.marginBottom = '3px';
                 list.appendChild(listItem);
            });
            resultsContainer.appendChild(list);
        } else if (result.success) {
            resultsContainer.textContent = 'All notes match expected data.';
            resultsContainer.style.color = '#6BFF6B';
        } else {
             resultsContainer.textContent = 'No specific mismatches found, but validation did not succeed.';
             resultsContainer.style.color = '#FFFF6B';
        }
    } else {
        // Handle case where validation hasn't run or failed to produce a result
        statusEl.textContent = 'Validation status: Not run or failed.';
        statusEl.style.color = '#AAAAAA';
        resultsContainer.innerHTML = '';
    }
}


/**
 * Attempt to automatically fix chord note issues
 */
function attemptAutoFix() {

    // First, validate to get the current state - call with no parameters
    const results = validateChordNotes();

    if (results.mismatchCount === 0 && results.success) { // Check for success too
        alert("Validation successful, no issues found to fix.");
        return;
    }

    // Check for root position vs basic position mismatch
    const urlParams = new URLSearchParams(window.location.search);
    const position = urlParams.get('position_select') || 'Root Position';
    const range = urlParams.get('note_range') || 'e - g';

    // Check if the main issue is too many notes are active
    // Use the actualCount from the validation result if available
    const activeCount = results.actualCount !== undefined ? results.actualCount : document.querySelectorAll('.note.active').length;

    if (activeCount > 6) { // Assuming 6 strings max, adjust if needed

        // Do a complete reset and rebuild using the direct fix function
        fixFromVoicingData(position, range);
    } else {
        // Quick fix for partial activation issues without full reset
        if (results.mismatchCount > 0 && results.mismatchCount <= 3) {
            // Try to fix simple activation issues first
            fixActivationIssues();

            // Revalidate to see if we resolved the issues - call with no parameters
            const partialResults = validateChordNotes();
            if (partialResults.mismatchCount === 0 && partialResults.success) {
                alert("Fixed issues with partial repairs!");
                return;
            }
        }

        // If quick fixes didn't work or too many mismatches, try intelligent fix
        intelligentNoteFix(position, range);
    }

    // Revalidate after fixes and update UI
    setTimeout(() => {
        const finalResult = validateChordNotes();
        if (finalResult.success) {
            alert("Auto-fix attempted. Validation successful.");
        } else {
             alert(`Auto-fix attempted. Validation failed with ${finalResult.mismatchCount} mismatch(es). Check console for details.`);
        }
        // Update standalone panel if needed
        if (window.DEBUG_MODE !== true && typeof updateValidationPanel === 'function') {
            updateValidationPanel(finalResult);
        }
    }, 300);
}

/**
 * Fix simple activation issues without resetting all notes
 */
function fixActivationIssues() {

    // Ensure all active notes have active tones
    document.querySelectorAll('.note.active').forEach(note => {
        const tone = note.querySelector('img.tone');
        if (tone && !tone.classList.contains('active')) {
            tone.classList.add('active');
        }
    });

    // Ensure all active tones have active note parents
    document.querySelectorAll('img.tone.active').forEach(tone => {
        const noteParent = tone.closest('.note');
        if (noteParent && !noteParent.classList.contains('active')) {
            noteParent.classList.add('active');
        }
    });

    // Fix visibility issues
    document.querySelectorAll('.note.active').forEach(note => {
        // Fix note visibility
        if (note.style.display === 'none' || note.style.visibility === 'hidden' || note.style.opacity === '0') {
            note.style.display = '';
            note.style.visibility = 'visible';
            note.style.opacity = '1';
        }

        // Fix tone visibility
        const tone = note.querySelector('img.tone');
        if (tone && (tone.style.display === 'none' || tone.style.visibility === 'hidden' || tone.style.opacity === '0')) {
            tone.style.display = '';
            tone.style.visibility = 'visible';
            tone.style.opacity = '1';
        }
    });

    // Ensure we have at least one root note if none exists
    const rootNotes = document.querySelectorAll('img.tone.active.root');
    if (rootNotes.length === 0) {

        // Get the expected notes
        const expected = getExpectedNotes();

        // Find a note that should be root
        let rootFound = false;
        for (const stringName in expected) {
            for (const expectedNote of expected[stringName]) {
                if (expectedNote.isRoot) {
                    // Find this note in the DOM
                    const stringElements = document.querySelectorAll(`.${stringName} .note.${expectedNote.note}.active`);
                    if (stringElements.length > 0) {
                        const noteElement = stringElements[0];
                        const toneImg = noteElement.querySelector('img.tone');
                        if (toneImg) {
                            toneImg.classList.add('root');
                            toneImg.src = '/static/media/red_circle.svg';
                            rootFound = true;
                            break;
                        }
                    }
                }
            }
            if (rootFound) break;
        }

        // If no expected root was found, just mark the first active note
        if (!rootFound) {
            const firstActiveTone = document.querySelector('img.tone.active');
            if (firstActiveTone) {
                firstActiveTone.classList.add('root');
                firstActiveTone.src = '/static/media/red_circle.svg';
            }
        }
    }
}

/**
 * Intelligently fix notes based on chord type and position
 */
function intelligentNoteFix(position, range) {

    // First, clear ALL active notes to avoid the situation where we have extras
    document.querySelectorAll('.note.active, .tone.active').forEach(el => {
        el.classList.remove('active');
    });

    document.querySelectorAll('.root').forEach(el => {
        el.classList.remove('root');
        if (el.tagName === 'IMG') {
            el.src = '/static/media/yellow_circle.svg';
        }
    });

    // Get the expected notes again
    const expected = getExpectedNotes();

    // Check if we have any expected notes
    let totalExpectedNotes = 0;
    for (const stringName in expected) {
        totalExpectedNotes += expected[stringName].length;
    }

    if (totalExpectedNotes === 0) {
        console.error("No expected notes found in data, trying direct approach with voicing data");
        fixFromVoicingData(position, range);
        return;
    }

    // Get chord information
    const chordRoot = voicing_data ? voicing_data.root : '';
    const chordType = voicing_data ? voicing_data.type : '';


    // Inversion-specific fret preferences
    const fretPreferences = {
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
        fretPreferences['Root Position'].BbString = [3, 5, 7];
        fretPreferences['First Inversion'].BbString = [3, 5, 7];
        fretPreferences['Second Inversion'].BbString = [7, 9, 2];
        fretPreferences['Third Inversion'].BbString = [7, 9, 11];
    }

    // For each expected note, find the best match in the DOM
    for (const stringName in expected) {
        for (const expectedNote of expected[stringName]) {

            // Find all candidate notes on this string
            const noteElements = document.querySelectorAll(`.${stringName} .note.${expectedNote.note}`);

            if (noteElements.length === 0) {
                console.error(`Cannot find any ${expectedNote.note} notes on ${stringName}`);
                continue;
            }

            // If we have multiple options, try to pick the best one
            let bestElement = null;
            let bestScore = Infinity;

            // If there's only one candidate, use it
            if (noteElements.length === 1) {
                bestElement = noteElements[0];
            } else {
                // Get fret preferences for this string and position
                const preferences = fretPreferences[position] && fretPreferences[position][stringName] ?
                    fretPreferences[position][stringName] : [3, 5, 7]; // Default preferences

                // Score each note element based on fret position
                for (const noteEl of noteElements) {
                    // Get the fret number
                    const fretEl = noteEl.closest('.fret');
                    if (!fretEl) continue;

                    // Extract fret number
                    const fretNames = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
                                       'eight', 'nine', 'ten', 'eleven', 'twelve'];
                    let fretNum = -1;

                    for (let i = 0; i < fretNames.length; i++) {
                        if (fretEl.classList.contains(fretNames[i])) {
                            fretNum = i;
                            break;
                        }
                    }

                    if (fretNum === -1) continue;

                    // Calculate score (lower is better)
                    let score = Infinity;

                    // Check against preferences
                    for (let i = 0; i < preferences.length; i++) {
                        const prefFret = preferences[i];
                        const prefScore = Math.abs(fretNum - prefFret) + (i * 0.1); // Add a small penalty for lower preference

                        if (prefScore < score) {
                            score = prefScore;
                        }
                    }

                    // Apply additional rules

                    // For seventh chords, prefer specific fret patterns
                    if (chordType && chordType.includes('7')) {
                        // Seventh chords often need higher frets for certain inversions
                        if (position === 'First Inversion' && stringName === 'eString') {
                            score -= (fretNum >= 8) ? 2 : 0;
                        } else if (position === 'Second Inversion' && stringName === 'bString') {
                            score -= (fretNum >= 8) ? 2 : 0;
                        }
                    }

                    // For Major chords in root position, prefer standard shapes
                    if (chordType === 'Major' && position === 'Root Position') {
                        if (stringName === 'eString' && fretNum === 0) {
                            score -= 1; // Prefer open E for E-shaped chords
                        }
                    }

                    // For Minor chords, prefer certain fret positions
                    if (chordType === 'Minor') {
                        if (position === 'Root Position' && stringName === 'gString') {
                            score -= (fretNum === 3) ? 1 : 0;
                        }
                    }

                    // Update best element if this is better
                    if (score < bestScore) {
                        bestScore = score;
                        bestElement = noteEl;
                    }
                }
            }

            // If we found a suitable element, activate it
            if (bestElement) {

                // Activate the note
                bestElement.classList.add('active');

                // Find and activate the tone element
                const toneEl = bestElement.querySelector('img.tone');
                if (toneEl) {
                    toneEl.classList.add('active');

                    // Mark as root if needed
                    if (expectedNote.isRoot) {
                        toneEl.classList.add('root');
                        toneEl.src = '/static/media/red_circle.svg';
                    }
                }
            }
        }
    }

    // Ensure at least one root note is present
    const rootNotes = document.querySelectorAll('img.tone.active.root');
    if (rootNotes.length === 0) {
        // Try to find a suitable root note
        const firstActive = document.querySelector('img.tone.active');
        if (firstActive) {
            firstActive.classList.add('root');
            firstActive.src = '/static/media/red_circle.svg';
        }
    }

    // Dispatch an event to notify other components
    document.dispatchEvent(new CustomEvent('chord-tones-updated', {
        detail: { position, range, success: true, source: 'auto-fix' }
    }));
}

/**
 * Alternative approach to fix from raw voicing data when expected notes fails
 */
function fixFromVoicingData(position, range) {

    // First, log what's currently active to help diagnose issues
    document.querySelectorAll('.note.active').forEach(note => {
        // Get string and note info
        const stringElement = note.closest('[class*="String"]');
        const stringName = stringElement ? Array.from(stringElement.classList).find(cls => cls.includes('String')) : 'unknown';

        // Define valid note names explicitly
        const validNoteNames = ['a', 'ab', 'as', 'b', 'bb', 'c', 'cs', 'db', 'd', 'ds', 'eb', 'e', 'f', 'fs', 'gb', 'g', 'gs'];

        // Get note name - handle note classes with octave numbers
        const noteClasses = Array.from(note.classList);
        const noteClass = noteClasses.find(cls => {
            // Extract base note without octave if present
            const baseNote = cls.replace(/[0-9]/g, '');
            return validNoteNames.includes(baseNote);
        });

    });

    // Ensure all notes are cleared - more forceful approach
    document.querySelectorAll('.note').forEach(el => {
        el.classList.remove('active');
    });

    document.querySelectorAll('img.tone').forEach(el => {
        el.classList.remove('active');
        el.classList.remove('root');
        el.src = '/static/media/yellow_circle.svg';
    });

    // Handle "Root Position" vs "Basic Position" naming inconsistency
    const internalPosition = position === 'Root Position' ? 'Basic Position' : position;

    // Check if we have valid data
    if (!window.voicing_data) {
        console.error("No voicing data available");
        return;
    }

    // Check if we have the requested range
    if (!voicing_data[range]) {
        console.error(`No data found for range ${range}`);
        // Show available ranges
            k !== 'chord' && k !== 'type' && k !== 'root' && k !== 'note_range'));
        return;
    }

    // Check if we have the requested position in this range
    if (!voicing_data[range][internalPosition]) {
        console.error(`No position data found for ${internalPosition} in range ${range}`);

        // Show available positions for this range

        // Special handling for Root/Basic position confusion
        if (internalPosition === 'Basic Position' && voicing_data[range]['Root Position']) {
            // Clone the data to prevent reference issues
            voicing_data[range]['Basic Position'] = JSON.parse(JSON.stringify(voicing_data[range]['Root Position']));
        } else if (internalPosition === 'Root Position' && voicing_data[range]['Basic Position']) {
            // Create a reference to Basic Position
            position = 'Basic Position';
            internalPosition = 'Basic Position';
        } else {
            // No suitable fallback found
            return;
        }
    }

    // Get the position data
    let positionData = voicing_data[range][internalPosition];

    // If it's an array, use the first item
    if (Array.isArray(positionData)) {
        positionData = positionData[0];
    }


    // Hard-coded fret preferences by string and position
    const fretPreferences = {
        'Basic Position': {
            eString: [0, 3, 5],
            bString: [0, 3, 5],
            gString: [0, 3, 5],
            dString: [0, 3, 5],
            aString: [0, 3, 5],
            EString: [0, 3, 5]
        },
        'First Inversion': {
            eString: [8, 3, 5],
            bString: [5, 3, 8],
            gString: [5, 3, 7],
            dString: [5, 3, 7],
            aString: [5, 3, 7],
            EString: [5, 3, 0]
        },
        'Second Inversion': {
            eString: [3, 5, 7],
            bString: [8, 5, 3],
            gString: [7, 5, 3],
            dString: [7, 5, 3],
            aString: [7, 5, 3],
            EString: [7, 5, 0]
        }
    };

    // Set Root Position to use same preferences as Basic Position
    fretPreferences['Root Position'] = fretPreferences['Basic Position'];

    // Process each string in the position data
    for (const stringName in positionData) {
        if (!positionData.hasOwnProperty(stringName)) continue;

        // Get the note data for this string
        const noteData = positionData[stringName];
        if (!noteData || !noteData[0]) continue;

        // Parse the note info
        let noteName, isRoot = false;

        if (Array.isArray(noteData)) {
            noteName = noteData[0].toLowerCase();
            isRoot = noteData.length > 1 && (noteData[1] === 'R' || noteData[1] === 'Root');
        } else if (typeof noteData === 'string') {
            noteName = noteData.toLowerCase();
        } else {
            console.warn(`Unexpected note data format for ${stringName}:`, noteData);
            continue;
        }

        // Extract base note name (without octave)
        const baseNote = noteName.replace(/[0-9]/g, '');

        // Find all matching notes on this string
        const noteElements = document.querySelectorAll(`.${stringName} .note.${baseNote}`);

        if (noteElements.length === 0) {
            console.error(`Could not find any ${baseNote} notes on ${stringName}`);
            continue;
        }

        // Select the best note based on position and fret preferences
        let bestElement = null;
        let bestScore = Infinity;

        // Get the preferences for this string and position
        const preferences = fretPreferences[internalPosition]?.[stringName] || [3, 5, 7];

        for (const noteEl of noteElements) {
            // Get the fret
            const fretEl = noteEl.closest('.fret');
            if (!fretEl) continue;

            // Determine fret number
            const fretNames = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
                               'eight', 'nine', 'ten', 'eleven', 'twelve'];
            let fretNum = -1;

            for (let i = 0; i < fretNames.length; i++) {
                if (fretEl.classList.contains(fretNames[i])) {
                    fretNum = i;
                    break;
                }
            }

            if (fretNum === -1) continue;

            // Score based on preferences
            let score = Infinity;

            for (let i = 0; i < preferences.length; i++) {
                const prefFret = preferences[i];
                const prefScore = Math.abs(fretNum - prefFret) + (i * 0.1);

                if (prefScore < score) {
                    score = prefScore;
                }
            }

            // Update if better
            if (score < bestScore) {
                bestScore = score;
                bestElement = noteEl;
            }
        }

        // If we found a suitable element, activate it
        if (bestElement) {

            // Activate the note
            bestElement.classList.add('active');

            // Find and activate the tone element
            const toneEl = bestElement.querySelector('img.tone');
            if (toneEl) {
                toneEl.classList.add('active');

                // Mark as root if needed
                if (isRoot) {
                    toneEl.classList.add('root');
                    toneEl.src = '/static/media/red_circle.svg';
                }
            }
        }
    }

    // Ensure at least one root note
    const rootNotes = document.querySelectorAll('img.tone.active.root');
    if (rootNotes.length === 0) {
        const firstActive = document.querySelector('img.tone.active');
        if (firstActive) {
            firstActive.classList.add('root');
            firstActive.src = '/static/media/red_circle.svg';
        }
    }

    // Special check for incorrect notes

    // Build a list of expected note classes based on activated notes
    const expectedClassNotes = {};
    for (const stringName in positionData) {
        if (!positionData.hasOwnProperty(stringName)) continue;

        // Get the note data
        const noteData = positionData[stringName];
        if (!noteData) continue;

        let noteName;
        if (Array.isArray(noteData)) {
            noteName = noteData[0].toLowerCase();
        } else if (typeof noteData === 'string') {
            noteName = noteData.toLowerCase();
        } else {
            continue;
        }

        // Get base note name
        const baseNote = noteName.replace(/[0-9]/g, '');
        expectedClassNotes[stringName] = baseNote;
    }

    // Now check for any active notes that aren't in our list
    document.querySelectorAll('.note.active').forEach(noteEl => {
        // Get string and note info
        const stringElement = noteEl.closest('[class*="String"]');
        if (!stringElement) return;

        const stringName = Array.from(stringElement.classList).find(cls => cls.includes('String'));
        if (!stringName) return;

        // Define valid note names explicitly
        const validNoteNames = ['a', 'ab', 'as', 'b', 'bb', 'c', 'cs', 'db', 'd', 'ds', 'eb', 'e', 'f', 'fs', 'gb', 'g', 'gs'];

        // Get note class
        const noteClasses = Array.from(noteEl.classList);
        const noteClass = noteClasses.find(cls => validNoteNames.includes(cls));
        if (!noteClass) {
            return;
        }

        // Check if this is an expected note for this string
        const expectedNote = expectedClassNotes[stringName];

        if (!expectedNote) {
            // This string shouldn't have any active notes
            noteEl.classList.remove('active');

            // Also remove active state from tone
            const toneEl = noteEl.querySelector('img.tone');
            if (toneEl) {
                toneEl.classList.remove('active');
                toneEl.classList.remove('root');
                toneEl.src = '/static/media/yellow_circle.svg';
            }
        } else {
            // Check if base notes match (ignoring octave)
            const baseNoteClass = noteClass.replace(/[0-9]/g, '');
            const baseNoteExpected = expectedNote.replace(/[0-9]/g, '');

            if (baseNoteClass !== baseNoteExpected) {
                // Wrong note is active on this string
                noteEl.classList.remove('active');

                // Also remove active state from tone
                const toneEl = noteEl.querySelector('img.tone');
                if (toneEl) {
                    toneEl.classList.remove('active');
                    toneEl.classList.remove('root');
                    toneEl.src = '/static/media/yellow_circle.svg';
                }
            }
        }
    });

    // Dispatch an event to notify other components
    document.dispatchEvent(new CustomEvent('chord-tones-updated', {
        detail: { position, range, success: true, source: 'direct-fix' }
    }));
}

/**
 * Helper to convert fret number to name
 */
function getFretName(fretNum) {
    const fretNames = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
                       'eight', 'nine', 'ten', 'eleven', 'twelve'];
    return fretNum >= 0 && fretNum < fretNames.length ? fretNames[fretNum] : '';
}