/**
 * Chord Debug Helper
 * Provides tools for debugging chord navigation and showing useful information
 */

// Global debug mode - set to true to enable debug features
window.DEBUG_MODE = false;

// Initialize debug tools when DOM is loaded
document.addEventListener('DOMContentLoaded', initDebugTools);

// Helper functions
function setupPanelStyles(panel) {
    Object.assign(panel.style, {
        position: 'fixed',
        bottom: '10px',
        right: '10px',
        width: '320px',
        padding: '10px',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        color: '#FFFFFF',
        zIndex: '9999',
        border: '1px solid #00FF00',
        fontFamily: 'monospace',
        fontSize: '12px',
        maxHeight: '400px',
        overflowY: 'auto',
        display: 'none'
    });
}

function addPanelTitle(panel) {
    const title = document.createElement('div');
    Object.assign(title.style, {
        borderBottom: '1px solid #00FF00',
        paddingBottom: '5px',
        marginBottom: '5px',
        fontWeight: 'bold'
    });
    title.textContent = 'Debug Panel (Ctrl+Shift+D)';
    panel.appendChild(title);
}

function createTab(tabName) {
    const tab = document.createElement('button');
    tab.id = `${tabName}-tab`;
    tab.textContent = tabName.charAt(0).toUpperCase() + tabName.slice(1);
    Object.assign(tab.style, {
        padding: '5px 10px',
        backgroundColor: '#333',
        border: '1px solid #666',
        color: '#fff',
        cursor: 'pointer'
    });
    tab.onclick = () => activateTab(tabName);
    return tab;
}

function addTabContainer(panel) {
    const tabContainer = document.createElement('div');
    Object.assign(tabContainer.style, {
        marginBottom: '10px',
        display: 'flex',
        gap: '5px'
    });

    ['validation', 'playability', 'data'].forEach(tabName => {
        const tab = createTab(tabName);
        tabContainer.appendChild(tab);
    });

    panel.appendChild(tabContainer);
}

function addContentContainers(panel) {
    ['validation', 'playability', 'data'].forEach(tabName => {
        const content = document.createElement('div');
        content.id = `${tabName}-content`;
        content.style.display = tabName === 'data' ? 'block' : 'none'; // Default to data tab
        content.style.marginTop = '10px';

        // Add specific structure for each tab
        if (tabName === 'validation') {
            // Status element
            const statusEl = document.createElement('div');
            statusEl.id = 'validation-status';
            statusEl.style.marginBottom = '10px';
            statusEl.textContent = 'Validation status: Pending...';
            content.appendChild(statusEl);

            // Results container with the list
            const resultsContainer = document.createElement('div');
            resultsContainer.id = 'validation-results';
            const errorList = document.createElement('ul');
            errorList.id = 'validation-error-list';
            errorList.style.listStyleType = 'none';
            errorList.style.paddingLeft = '0';
            resultsContainer.appendChild(errorList);
            content.appendChild(resultsContainer);
            // Buttons might be added dynamically later by validation logic

        } else if (tabName === 'playability') {
            // Add elements to display playability metrics
            content.innerHTML = `
                <div>Finger Count: <span id="playability-finger-count">N/A</span></div>
                <div>Fret Span: <span id="playability-fret-span">N/A</span></div>
                <div>String Skip: <span id="playability-string-skip">N/A</span></div>
                <div style="margin-top: 5px; font-size: 10px;">(Lower values generally mean easier)</div>
            `;

        } else if (tabName === 'data') {
            // Add a pre tag for formatted data output
            const pre = document.createElement('pre');
            pre.id = 'debug-data-output';
            pre.style.whiteSpace = 'pre-wrap'; // Allow wrapping
            pre.style.wordBreak = 'break-all'; // Break long words/strings
            pre.textContent = 'Loading data...';
            content.appendChild(pre);
        }

        panel.appendChild(content);
    });
}


function setupKeyboardShortcut(panel) {
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && e.key === 'D') {
            e.preventDefault();
            toggleDebugPanel();
        }
    });
}

function updateActiveTabContent() {
    const playabilityContent = document.getElementById('playability-content');
    const validationContent = document.getElementById('validation-content');
    const dataContent = document.getElementById('data-content');

    if (playabilityContent && playabilityContent.style.display === 'block' && typeof analyzeChordPlayability === 'function') {
        analyzeChordPlayability(); // Update playability if tab is active
    }

    if (validationContent && validationContent.style.display === 'block' && typeof validateChordNotes === 'function') {
        validateChordNotes(); // Update validation if tab is active
    }

    if (dataContent && dataContent.style.display === 'block') {
        updateDebugPanelData(); // Update data if tab is active
    }
}

// Main functions
function initDebugTools() {

    // Check for URL debug parameter
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('debug') && urlParams.get('debug') === 'true') {
        window.DEBUG_MODE = true;
    }

    // Create the unified debug panel if debug mode is enabled
    if (window.DEBUG_MODE) {
        createUnifiedDebugPanel();
        listenForNavigationEvents(); // Assuming this exists elsewhere
    }

    // Initialize playability analysis when chord tones are updated (if function exists)
    if (typeof analyzeChordPlayability === 'function') {
        document.addEventListener('chord-tones-updated', function(e) {
            setTimeout(analyzeChordPlayability, 300);
        });
    }
}

function createUnifiedDebugPanel() {
    // Avoid creating multiple panels
    if (document.getElementById('unified-debug-panel')) {
        return document.getElementById('unified-debug-panel');
    }

    const panel = document.createElement('div');
    panel.id = 'unified-debug-panel';

    setupPanelStyles(panel);
    addPanelTitle(panel);
    addTabContainer(panel);
    addContentContainers(panel); // This now adds the <pre> tag for data

    document.body.appendChild(panel);
    setupKeyboardShortcut(panel);

    // Initial data population and tab activation
    activateTab('data'); // Default to data tab
    updateDebugPanelData(); // Populate data tab initially

    return panel;
}


function toggleDebugPanel() {
    const panel = document.getElementById('unified-debug-panel');
    if (!panel) return;

    const isVisible = panel.style.display !== 'none';
    panel.style.display = isVisible ? 'none' : 'block';

    // Update content of the active tab when panel becomes visible
    if (!isVisible) {
        updateActiveTabContent();
    }
}

function activateTab(tabName) {
    document.querySelectorAll('[id$="-content"]').forEach(content => {
        content.style.display = 'none';
    });

    const selectedContent = document.getElementById(`${tabName}-content`);
    if (selectedContent) {
        selectedContent.style.display = 'block';
    }

    document.querySelectorAll('[id$="-tab"]').forEach(tab => {
        tab.style.backgroundColor = tab.id === `${tabName}-tab` ? '#444' : '#333';
    });

    // Update content when tab is activated
    updateActiveTabContent();
}

/**
 * Builds the validation content when the validation tab is first selected
 * This implements all the validation features from the separate validation panel
 */
function buildValidationContent() {
    // Content structure (status, list, buttons) is now created in addContentContainers
    // This function might be used to add event listeners to buttons if they aren't added elsewhere
    const validationContent = document.getElementById('validation-content');
    if (!validationContent) return;

    // Example: Add button listeners if not done elsewhere
    const validateButton = validationContent.querySelector('#validate-now-button'); // Assuming buttons have IDs
    if (validateButton && typeof validateChordNotes === 'function') {
        validateButton.onclick = validateChordNotes;
    }

    const fixButton = validationContent.querySelector('#auto-fix-button');
    if (fixButton && typeof attemptAutoFix === 'function') {
         fixButton.onclick = attemptAutoFix;
    }
     // Add listeners for other buttons...

    // Run validation immediately when tab content is built/shown
    if (typeof validateChordNotes === 'function') {
        setTimeout(validateChordNotes, 100);
    } else {
        const statusEl = document.getElementById('validation-status');
        if (statusEl) {
            statusEl.textContent = 'Validation status: Function not available';
            statusEl.style.color = '#999';
        }
    }
}

/**
 * Update the debug panel's Data tab with current data
 */
function updateDebugPanelData() {
    const dataOutputEl = document.getElementById('debug-data-output');
    if (!dataOutputEl) {
        console.warn("Data output element ('debug-data-output') not found.");
        return;
    }

    let debugData = {};

    try {
        // 1. URL Parameters
        debugData.urlParams = Object.fromEntries(new URLSearchParams(window.location.search).entries());

        // 2. Global Voicing Data
        debugData.voicingData = window.voicing_data || 'Not Available';

        // 3. Expected Notes
        if (typeof getExpectedNotes === 'function') {
            debugData.expectedNotes = getExpectedNotes();
        } else {
            debugData.expectedNotes = 'getExpectedNotes function not available';
        }

        // 4. Actual Notes
        if (typeof getActiveNotes === 'function') {
            // GetActiveNotes returns elements, which don't stringify well. Let's simplify.
            const activeNotesRaw = getActiveNotes();
            const activeNotesSimplified = {};
            for (const stringName in activeNotesRaw) {
                activeNotesSimplified[stringName] = activeNotesRaw[stringName].map(note => ({
                    note: note.note,
                    isRoot: note.isRoot,
                    fret: note.fret,
                    fretNumber: note.fretNumber
                }));
            }
            debugData.actualNotes = activeNotesSimplified;
        } else {
            debugData.actualNotes = 'getActiveNotes function not available';
        }

        // 5. Playability Analysis (if available)
        // Assuming analyzeChordPlayability returns data or updates a global variable
        if (typeof window.lastPlayabilityResult !== 'undefined') { // Check if a global result exists
             debugData.playabilityResult = window.lastPlayabilityResult;
        } else if (typeof analyzeChordPlayability === 'function') {
             // Optionally call it here if it returns data directly, but be mindful of performance
             // debugData.playabilityResult = analyzeChordPlayability();
             debugData.playabilityResult = 'Playability analysis available but result not stored globally.';
        } else {
             debugData.playabilityResult = 'analyzeChordPlayability function not available';
        }


        // 6. Last Validation Result (Raw)
        const lastValidation = window.lastValidationResult;
        if (typeof lastValidation !== 'undefined') {
            debugData.lastValidationRaw = lastValidation;
        } else {
            debugData.lastValidationRaw = 'No validation run yet or result not stored.';
        }

        // 7. Validation Status Summary (New)
        let validationSummary = 'Not run yet';
        if (typeof lastValidation !== 'undefined') {
            if (lastValidation.success) {
                validationSummary = 'Success';
            } else if (lastValidation.error) {
                validationSummary = `Failed: ${lastValidation.error}`;
            } else if (lastValidation.mismatchCount > 0) {
                validationSummary = `Failed: ${lastValidation.mismatchCount} mismatch(es)`;
            } else {
                validationSummary = 'Uncertain Status (Ran, but no success/error/mismatches reported)';
            }
        }
        debugData.validationStatusSummary = validationSummary;


        // 8. Basic Info (already gathered in original function)
        debugData.basicInfo = {
             position: debugData.urlParams.position_select || 'Root Position',
             range: debugData.urlParams.note_range || 'e - g',
             chord: window.voicing_data ? window.voicing_data.chord : 'Unknown',
             type: window.voicing_data ? window.voicing_data.type : 'Unknown',
             activeNoteCountDOM: document.querySelectorAll('.note.active').length,
             rootNoteCountDOM: document.querySelectorAll('img.tone.root').length
        };


        // Format the data as a JSON string with indentation
        // Order the keys for better readability
        const orderedDebugData = {
            validationStatusSummary: debugData.validationStatusSummary,
            basicInfo: debugData.basicInfo,
            urlParams: debugData.urlParams,
            expectedNotes: debugData.expectedNotes,
            actualNotes: debugData.actualNotes,
            lastValidationRaw: debugData.lastValidationRaw,
            playabilityResult: debugData.playabilityResult,
            voicingData: debugData.voicingData // Keep large object last
        };
        const dataString = JSON.stringify(orderedDebugData, null, 2); // 2 spaces indentation

        // Update the <pre> tag content
        dataOutputEl.textContent = dataString;
        dataOutputEl.style.color = ''; // Reset color in case of previous error

    } catch (error) {
        console.error("Error updating debug panel data:", error);
        dataOutputEl.textContent = `Error gathering debug data:\n${error.message}\n\nPartial Data:\n${JSON.stringify(debugData, null, 2)}`;
        dataOutputEl.style.color = '#FF6B6B'; // Indicate error
    }
}


// --- Playability Analysis ---
// Calculates basic playability metrics based on active notes.
function analyzeChordPlayability() {
    let playabilityData = {
        fingerCount: 'N/A',
        fretSpan: 'N/A',
        stringSkip: 'N/A',
        error: null
    };

    try {
        // Ensure getActiveNotes function exists
        if (typeof getActiveNotes !== 'function') {
            throw new Error("getActiveNotes function is not available.");
        }

        const activeNotesData = getActiveNotes(); // Format: { stringName: [{ note, isRoot, fret, fretNumber, element }, ...], ... }
        if (!activeNotesData) {
            throw new Error("Failed to get active notes data.");
        }

        let frettedNotes = [];
        let stringIndicesPlayed = [];

        // Define standard 6-string tuning order for index mapping
        // Adjust this if supporting different tunings/string counts
        const stringOrder = ['highEString', 'bString', 'gString', 'dString', 'aString', 'eString']; // High to Low

        for (const stringName in activeNotesData) {
            if (activeNotesData.hasOwnProperty(stringName)) {
                const stringIndex = stringOrder.indexOf(stringName);
                if (stringIndex !== -1) { // Only consider strings in our defined order
                    activeNotesData[stringName].forEach(note => {
                        if (note.fretNumber > 0) { // Exclude open strings (fret 0) and errors (-1)
                            frettedNotes.push(note.fretNumber);
                            if (!stringIndicesPlayed.includes(stringIndex)) {
                                stringIndicesPlayed.push(stringIndex);
                            }
                        } else if (note.fretNumber === 0) { // Include open strings for string skip calculation
                             if (!stringIndicesPlayed.includes(stringIndex)) {
                                stringIndicesPlayed.push(stringIndex);
                            }
                        }
                    });
                }
            }
        }

        // 1. Finger Count
        playabilityData.fingerCount = frettedNotes.length;

        // 2. Fret Span
        if (frettedNotes.length > 1) {
            const minFret = Math.min(...frettedNotes);
            const maxFret = Math.max(...frettedNotes);
            playabilityData.fretSpan = maxFret - minFret;
        } else if (frettedNotes.length === 1) {
            playabilityData.fretSpan = 0; // Only one fretted note
        } else {
            playabilityData.fretSpan = 0; // No fretted notes
        }

        // 3. String Skip
        if (stringIndicesPlayed.length > 1) {
            stringIndicesPlayed.sort((a, b) => a - b); // Sort indices numerically (e.g., 0, 1, 3, 5)
            const minStringIndex = stringIndicesPlayed[0];
            const maxStringIndex = stringIndicesPlayed[stringIndicesPlayed.length - 1];
            const expectedStringCount = maxStringIndex - minStringIndex + 1;
            playabilityData.stringSkip = expectedStringCount > stringIndicesPlayed.length ? 'Yes' : 'No';
        } else {
            playabilityData.stringSkip = 'No'; // Not applicable with 0 or 1 string played
        }

    } catch (error) {
        console.error("Error during playability analysis:", error);
        playabilityData.error = error.message;
        // Reset metrics on error
        playabilityData.fingerCount = 'Error';
        playabilityData.fretSpan = 'Error';
        playabilityData.stringSkip = 'Error';
    }

    // Store result globally for the data tab
    window.lastPlayabilityResult = playabilityData;

    // Update the Playability Tab UI
    const fingerCountEl = document.getElementById('playability-finger-count');
    const fretSpanEl = document.getElementById('playability-fret-span');
    const stringSkipEl = document.getElementById('playability-string-skip');

    if (fingerCountEl) fingerCountEl.textContent = playabilityData.fingerCount;
    if (fretSpanEl) fretSpanEl.textContent = playabilityData.fretSpan;
    if (stringSkipEl) stringSkipEl.textContent = playabilityData.stringSkip;

    return playabilityData;
}

// --- Other potential functions (placeholders) ---

function listenForNavigationEvents() {
    // Add event listeners for things that change the chord/position/range
    // e.g., clicks on selectors, URL changes
    // On change, call relevant update functions like updateDebugPanelData, validateChordNotes etc.
}

function logEvent(message) {
    const eventLog = document.getElementById('debug-event-log'); // Assuming this exists
    if (eventLog) {
        const entry = document.createElement('div');
        entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        eventLog.appendChild(entry);
        eventLog.scrollTop = eventLog.scrollHeight; // Scroll to bottom
    }
}

function resetChordState() {
    console.warn("Reset Chord State - Not fully implemented");
    // Logic to reset UI elements and potentially reload data
    logEvent("Chord state reset requested.");
}

function fixNavigationState() {
     console.warn("Fix Navigation State - Not fully implemented");
     // Logic to potentially clean URL parameters and reload
     logEvent("Navigation state fix requested.");
     if (typeof forcePageReload === 'function') { // Assuming forcePageReload exists from chord_debug_notes.js
         forcePageReload();
     }
}