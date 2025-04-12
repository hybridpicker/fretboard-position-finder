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
        content.style.display = tabName === 'validation' ? 'block' : 'none';
        content.style.marginTop = '10px';
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
    
    if (playabilityContent && playabilityContent.style.display === 'block') {
        analyzeChordPlayability();
    }
    
    if (validationContent && 
        validationContent.style.display === 'block' && 
        typeof validateChordNotes === 'function') {
        validateChordNotes(); // Call with no parameters to avoid JSON issues
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
        listenForNavigationEvents();
    }
    
    // Initialize playability analysis when chord tones are updated
    document.addEventListener('chord-tones-updated', function(e) {
        setTimeout(analyzeChordPlayability, 300);
    });
}

function createUnifiedDebugPanel() {
    const panel = document.createElement('div');
    panel.id = 'unified-debug-panel';
    
    setupPanelStyles(panel);
    addPanelTitle(panel);
    addTabContainer(panel);
    addContentContainers(panel);
    
    document.body.appendChild(panel);
    setupKeyboardShortcut(panel);
    updateDebugPanelData();
    
    return panel;
}

function toggleDebugPanel() {
    const panel = document.getElementById('unified-debug-panel');
    if (!panel) return;
    
    const isVisible = panel.style.display !== 'none';
    panel.style.display = isVisible ? 'none' : 'block';
    
    if (!isVisible) {
        updateDebugPanelData();
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
    
    if (tabName === 'validation' && typeof validateChordNotes === 'function') {
        validateChordNotes(); // Call with no parameters to avoid JSON issues
    }
}

/**
 * Builds the validation content when the validation tab is first selected
 * This implements all the validation features from the separate validation panel
 */
function buildValidationContent() {
    const validationContent = document.getElementById('validation-content');
    if (!validationContent || validationContent.childNodes.length > 0) return;
    
    // Status element
    const statusEl = document.createElement('div');
    statusEl.id = 'validation-status';
    statusEl.style.marginBottom = '10px';
    statusEl.textContent = 'Validation status: Running...';
    validationContent.appendChild(statusEl);
    
    // Results container
    const resultsContainer = document.createElement('div');
    resultsContainer.id = 'validation-results';
    validationContent.appendChild(resultsContainer);
    
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
    fixButton.onclick = function() {
        if (typeof attemptAutoFix === 'function') {
            attemptAutoFix();
        } else {
            alert("Auto-fix function not available");
        }
    };
    buttonContainer.appendChild(fixButton);
    
    // Force page reload button
    const reloadButton = document.createElement('button');
    reloadButton.textContent = 'Force Reload';
    reloadButton.onclick = function() {
        if (typeof forcePageReload === 'function') {
            forcePageReload();
        } else {
            if (confirm("This will reload the page with clean URL parameters. Continue?")) {
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
    };
    reloadButton.style.backgroundColor = '#F44336';
    reloadButton.style.color = 'white';
    buttonContainer.appendChild(reloadButton);
    
    validationContent.appendChild(buttonContainer);
    
    // Add another row of buttons
    const buttonContainer2 = document.createElement('div');
    buttonContainer2.style.marginTop = '8px';
    buttonContainer2.style.display = 'flex';
    buttonContainer2.style.justifyContent = 'space-between';
    
    // Fix from voicing data button
    const fixDataButton = document.createElement('button');
    fixDataButton.textContent = 'Fix from Data';
    fixDataButton.onclick = function() {
        if (typeof fixFromVoicingData === 'function') {
            const urlParams = new URLSearchParams(window.location.search);
            const position = urlParams.get('position_select') || 'Root Position';
            const range = urlParams.get('note_range') || 'e - g';
            fixFromVoicingData(position, range);
            setTimeout(validateChordNotes, 300);
        } else {
            alert("Fix from Data function not available");
        }
    };
    buttonContainer2.appendChild(fixDataButton);
    
    // Debug info button
    const debugButton = document.createElement('button');
    debugButton.textContent = 'Log Data';
    debugButton.onclick = function() {
        const urlParams = new URLSearchParams(window.location.search);
        const position = urlParams.get('position_select') || 'Root Position';
        const range = urlParams.get('note_range') || 'e - g';
        if (typeof getActiveNotes === 'function') {
        }
        if (typeof getExpectedNotes === 'function') {
        }
    };
    buttonContainer2.appendChild(debugButton);
    
    validationContent.appendChild(buttonContainer2);
    
    // Run validation immediately
    if (typeof validateChordNotes === 'function') {
        setTimeout(validateChordNotes, 100);
    } else {
        // If validateChordNotes isn't available, show a message
        statusEl.textContent = 'Validation status: Not available';
        statusEl.style.color = '#999';
        
        // Create a note about missing functions
        const missingNote = document.createElement('div');
        missingNote.style.padding = '10px';
        missingNote.style.backgroundColor = 'rgba(50, 50, 60, 0.5)';
        missingNote.style.borderRadius = '4px';
        missingNote.style.marginTop = '10px';
        missingNote.style.marginBottom = '10px';
        missingNote.innerHTML = 'Chord validation functions are not available. Make sure <code>chord_debug_notes.js</code> is loaded.';
        resultsContainer.appendChild(missingNote);
    }
}

/**
 * Add status display to the debug panel
 * This adds information about position, range, active notes, etc.
 */
function addStatusDisplay(panel) {
    // Add status elements
    const statusContainer = document.createElement('div');
    
    // Position info
    const positionInfo = document.createElement('div');
    positionInfo.id = 'debug-position-info';
    positionInfo.textContent = 'Position: ...';
    statusContainer.appendChild(positionInfo);
    
    // Range info
    const rangeInfo = document.createElement('div');
    rangeInfo.id = 'debug-range-info';
    rangeInfo.textContent = 'Range: ...';
    statusContainer.appendChild(rangeInfo);
    
    // Chord info
    const chordInfo = document.createElement('div');
    chordInfo.id = 'debug-chord-info';
    chordInfo.textContent = 'Chord: ...';
    statusContainer.appendChild(chordInfo);
    
    // Type info
    const typeInfo = document.createElement('div');
    typeInfo.id = 'debug-type-info';
    typeInfo.textContent = 'Type: ...';
    statusContainer.appendChild(typeInfo);
    
    // Note count
    const noteCount = document.createElement('div');
    noteCount.id = 'debug-note-count';
    noteCount.textContent = 'Active Notes: 0';
    statusContainer.appendChild(noteCount);
    
    // Root count
    const rootCount = document.createElement('div');
    rootCount.id = 'debug-root-count';
    rootCount.textContent = 'Root Notes: 0';
    statusContainer.appendChild(rootCount);
    
    // Playability score container
    const playabilityContainer = document.createElement('div');
    playabilityContainer.id = 'debug-playability-container';
    playabilityContainer.style.marginTop = '10px';
    playabilityContainer.style.marginBottom = '10px';
    playabilityContainer.style.padding = '8px';
    playabilityContainer.style.backgroundColor = 'rgba(30, 30, 30, 0.7)';
    playabilityContainer.style.border = '1px solid #555';
    playabilityContainer.style.borderRadius = '4px';
    
    // Playability title
    const playabilityTitle = document.createElement('div');
    playabilityTitle.style.fontWeight = 'bold';
    playabilityTitle.style.borderBottom = '1px solid #444';
    playabilityTitle.style.paddingBottom = '4px';
    playabilityTitle.style.marginBottom = '4px';
    playabilityTitle.textContent = 'Playability Analysis';
    playabilityContainer.appendChild(playabilityTitle);
    
    // Playability score
    const playabilityScore = document.createElement('div');
    playabilityScore.id = 'debug-playability-score';
    playabilityScore.style.fontSize = '14px';
    playabilityScore.style.marginBottom = '4px';
    playabilityScore.innerHTML = '<span style="color:#BBB">Score:</span> <span id="playability-score-value" style="font-weight:bold;color:#888">Not analyzed</span>';
    playabilityContainer.appendChild(playabilityScore);
    
    // Fret stretch
    const fretStretch = document.createElement('div');
    fretStretch.id = 'debug-fret-stretch';
    fretStretch.style.marginBottom = '2px';
    fretStretch.innerHTML = '<span style="color:#BBB">Fret stretch:</span> <span id="fret-stretch-value" style="color:#888">--</span>';
    playabilityContainer.appendChild(fretStretch);
    
    // String stretch
    const stringStretch = document.createElement('div');
    stringStretch.id = 'debug-string-stretch';
    stringStretch.style.marginBottom = '2px';
    stringStretch.innerHTML = '<span style="color:#BBB">String stretch:</span> <span id="string-stretch-value" style="color:#888">--</span>';
    playabilityContainer.appendChild(stringStretch);
    
    // Finger count
    const fingerCount = document.createElement('div');
    fingerCount.id = 'debug-finger-count';
    fingerCount.style.marginBottom = '2px';
    fingerCount.innerHTML = '<span style="color:#BBB">Finger count:</span> <span id="finger-count-value" style="color:#888">--</span>';
    playabilityContainer.appendChild(fingerCount);
    
    // Finger suggestions
    const fingerSuggestions = document.createElement('div');
    fingerSuggestions.id = 'debug-finger-suggestions';
    fingerSuggestions.style.marginTop = '6px';
    fingerSuggestions.style.fontSize = '12px';
    fingerSuggestions.innerHTML = '<span style="color:#BBB">Suggestions:</span> <span id="suggestions-value" style="color:#888">--</span>';
    playabilityContainer.appendChild(fingerSuggestions);
    
    // Add playability container to status container
    statusContainer.appendChild(playabilityContainer);
    
    // Event log
    const eventLogTitle = document.createElement('div');
    eventLogTitle.textContent = 'Event Log:';
    eventLogTitle.style.marginTop = '10px';
    eventLogTitle.style.borderBottom = '1px solid #00FF00';
    statusContainer.appendChild(eventLogTitle);
    
    const eventLog = document.createElement('div');
    eventLog.id = 'debug-event-log';
    eventLog.style.height = '200px';
    eventLog.style.overflowY = 'scroll';
    eventLog.style.fontSize = '11px';
    statusContainer.appendChild(eventLog);
    
    // Command buttons
    const buttonContainer = document.createElement('div');
    buttonContainer.style.marginTop = '10px';
    buttonContainer.style.display = 'flex';
    buttonContainer.style.justifyContent = 'space-between';
    
    // Reload button
    const reloadButton = document.createElement('button');
    reloadButton.textContent = 'Reload Page';
    reloadButton.onclick = function() { window.location.reload(); };
    buttonContainer.appendChild(reloadButton);
    
    // Reset button
    const resetButton = document.createElement('button');
    resetButton.textContent = 'Reset State';
    resetButton.onclick = function() { resetChordState(); };
    buttonContainer.appendChild(resetButton);
    
    // Fix button
    const fixButton = document.createElement('button');
    fixButton.textContent = 'Force Reload with URL Fix';
    fixButton.onclick = function() { fixNavigationState(); };
    buttonContainer.appendChild(fixButton);
    
    statusContainer.appendChild(buttonContainer);
    
    // Add status container to panel
    panel.appendChild(statusContainer);
    
    // Add status display to the panel
    addStatusDisplay(panel);
    
    // Add to the document
    document.body.appendChild(panel);
    
    // Update the panel with initial data
    updateDebugPanelData();
    
    return panel;
}

/**
 * Update the debug panel with current data
 */
function updateDebugPanelData() {
    try {
        // First check if the debug panel exists - otherwise don't try to update it
        if (!document.getElementById('debug-position-info')) {
            return;
        }
        
        // Get URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const position = urlParams.get('position_select') || 'Root Position';
        const range = urlParams.get('note_range') || 'e - g';
        
        // Get chord info from voicing_data
        const chord = voicing_data ? voicing_data.chord : 'Unknown';
        const type = voicing_data ? voicing_data.type : 'Unknown';
        
        // Get element counts
        const activeNoteCount = document.querySelectorAll('.note.active').length;
        const rootNoteCount = document.querySelectorAll('img.tone.root').length;
        
        // Check each element before updating to avoid null errors
        const posInfoEl = document.getElementById('debug-position-info');
        if (posInfoEl) posInfoEl.textContent = `Position: ${position}`;
        
        const rangeInfoEl = document.getElementById('debug-range-info');
        if (rangeInfoEl) rangeInfoEl.textContent = `Range: ${range}`;
        
        const chordInfoEl = document.getElementById('debug-chord-info');
        if (chordInfoEl) chordInfoEl.textContent = `Chord: ${chord}`;
        
        const typeInfoEl = document.getElementById('debug-type-info');
        if (typeInfoEl) typeInfoEl.textContent = `Type: ${type}`;
        
        const noteCountEl = document.getElementById('debug-note-count');
        if (noteCountEl) noteCountEl.textContent = `Active Notes: ${activeNoteCount}`;
        
        const rootCountEl = document.getElementById('debug-root-count');
        if (rootCountEl) rootCountEl.textContent = `Root Notes: ${rootNoteCount}`;
        
        // Also log this info
            position, range, chord, type, 
            activeNotes: activeNoteCount,
            rootNotes: rootNoteCount
        });
        
        // Run playability analysis when updating the panel
        analyzeChordPlayability();
    } catch (error) {
        console.error("Error updating debug data:", error);
    }
}

/**
 * Analyze playability of current chord voicing
 * Calculates score based on fret stretch, string spread, and fingering complexity
 */
function analyzeChordPlayability() {
    try {
        
        // Get all active notes on the fretboard
        const activeNotes = document.querySelectorAll('.note.active');
        if (activeNotes.length < 2) {
            updatePlayabilityDisplay({
                score: "N/A",
                fretStretch: 0,
                stringStretch: 0,
                fingerCount: 0,
                suggestions: "Need at least 2 notes for analysis"
            });
            return;
        }
        
        // Store notes by string and fret
        const STRING_MAPPING = {
            'eString': 1,
            'bString': 2,
            'gString': 3,
            'dString': 4,
            'AString': 5,
            'ELowString': 6,
            'lowBString': 7,
            'highAString': 0 // 8-string highest string
        };
        
        // Reverse mapping for output
        const STRING_NAMES = {
            0: 'high A',
            1: 'e',
            2: 'b',
            3: 'g',
            4: 'd',
            5: 'A',
            6: 'E',
            7: 'low B'
        };
        
        // Find the fret and string for each active note
        const fretPositions = [];
        const stringPositions = [];
        const noteData = [];
        
        activeNotes.forEach(note => {
            // Get the string name from parent element class
            const stringElement = note.closest('[class*="String"]');
            if (!stringElement) return;
            
            const stringClass = Array.from(stringElement.classList).find(cls => cls.includes('String'));
            if (!stringClass) return;
            
            // Convert string class to numeric position for calculations
            const stringPosition = STRING_MAPPING[stringClass] || 0;
            
            // Get the fret number from parent fret element
            const fretElement = note.closest('.fret');
            if (!fretElement) return;
            
            // Convert fret class to number
            const fretMap = {
                'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 
                'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
                'ten': 10, 'eleven': 11, 'twelve': 12
            };
            
            let fretNumber = 0;
            for (const cls of fretElement.classList) {
                if (fretMap.hasOwnProperty(cls)) {
                    fretNumber = fretMap[cls];
                    break;
                }
            }
            
            // Store position data for analysis
            fretPositions.push(fretNumber);
            stringPositions.push(stringPosition);
            
            // Build a complete note record for detailed analysis
            noteData.push({
                string: stringPosition,
                stringName: STRING_NAMES[stringPosition],
                fret: fretNumber,
                isRoot: note.querySelector('img.tone.root') !== null
            });
        });
        
        // Calculate basic metrics
        const fretStretch = fretPositions.length > 0 ? 
            Math.max(...fretPositions) - Math.min(...fretPositions) : 0;
            
        const stringStretch = stringPositions.length > 0 ? 
            Math.max(...stringPositions) - Math.min(...stringPositions) : 0;
        
        // Organize notes by string for analysis
        const notesByString = {};
        noteData.forEach(note => {
            if (!notesByString[note.string]) {
                notesByString[note.string] = [];
            }
            notesByString[note.string].push(note);
        });
        
        // Estimate minimum required fingers
        // This is a simplified heuristic - professional voicings would use more complex rules
        let fingerCount = activeNotes.length;
        
        // Apply finger-saving rules:
        // 1. Same fret across strings can potentially use one finger (barre)
        const fretCounts = {};
        noteData.forEach(note => {
            fretCounts[note.fret] = (fretCounts[note.fret] || 0) + 1;
        });
        
        // Find potential barres (same fret across adjacent strings)
        Object.entries(fretCounts).forEach(([fret, count]) => {
            // Only consider as barre if multiple notes on same fret
            if (count >= 2) {
                const fretNum = parseInt(fret, 10);
                
                // Check if strings are adjacent for proper barre
                const stringsAtFret = noteData
                    .filter(n => n.fret === fretNum)
                    .map(n => n.string)
                    .sort((a, b) => a - b);
                
                // Simple adjacency check - if max-min+1 == length, all are adjacent
                const isAdjacent = (Math.max(...stringsAtFret) - Math.min(...stringsAtFret) + 1) === stringsAtFret.length;
                
                if (isAdjacent) {
                    // Potential barre detected - saves fingers
                    fingerCount -= (count - 1); // One finger can play multiple notes
                }
            }
        });
        
        // Calculate playability score (lower is better):
        // Base it on:
        // - Fret stretch (longer stretch is harder)
        // - String stretch (larger string distance is harder)
        // - Required finger count (more fingers needed is harder)
        // - Position on fretboard (higher positions get progressively harder)
        
        let playabilityScore = 100; // Start with perfect score and subtract
        
        // Penalty for fret stretch: each fret of stretch adds a penalty
        if (fretStretch > 3) {
            playabilityScore -= (fretStretch - 3) * 10; // Severe penalty for stretches over 3 frets
        } else if (fretStretch > 0) {
            playabilityScore -= fretStretch * 3; // Milder penalty for small stretches
        }
        
        // Penalty for string stretch: each string of stretch adds a penalty
        if (stringStretch > 3) {
            playabilityScore -= (stringStretch - 3) * 7; // Severe penalty for stretches over 3 strings
        } else if (stringStretch > 0) {
            playabilityScore -= stringStretch * 2; // Milder penalty for small stretches
        }
        
        // Penalty for finger count: more than 4 fingers is impossible
        if (fingerCount > 4) {
            playabilityScore -= 50; // Major penalty for requiring more than 4 fingers
        } else if (fingerCount >= 3) {
            playabilityScore -= (fingerCount - 2) * 5; // Small penalty for 3-4 fingers
        }
        
        // Penalty for high positions - harder to reach
        const averageFretPosition = fretPositions.reduce((sum, fret) => sum + fret, 0) / fretPositions.length;
        if (averageFretPosition > 7) {
            playabilityScore -= (averageFretPosition - 7) * 2; // Penalty for higher positions
        }
        
        // Bonus for open strings
        const openStringCount = fretPositions.filter(fret => fret === 0).length;
        playabilityScore += openStringCount * 3; // Bonus for each open string
        
        // Bonus for using standard positions (1st, 5th, 7th, 9th, 12th)
        const standardPositions = [1, 5, 7, 9, 12];
        const usesStandardPosition = fretPositions.some(fret => standardPositions.includes(fret));
        if (usesStandardPosition) {
            playabilityScore += 5;
        }
        
        // Cap the score between 0-100
        playabilityScore = Math.max(0, Math.min(100, Math.round(playabilityScore)));
        
        // Generate suggestions based on analysis
        let suggestions = [];
        
        if (fingerCount > 4) {
            suggestions.push("Excessive finger stretch - try alternate voicing");
        }
        
        if (fretStretch > 4) {
            suggestions.push("Consider a different position with less fret stretch");
        }
        
        if (stringStretch > 4) {
            suggestions.push("Look for alternatives with less string skipping");
        }
        
        // Add inversion alternatives if appropriate
        const urlParams = new URLSearchParams(window.location.search);
        const position = urlParams.get('position_select') || 'Root Position';
        
        if (playabilityScore < 70 && position === 'Root Position') {
            suggestions.push("Try First Inversion for possible improvement");
        } else if (playabilityScore < 70 && position === 'First Inversion') {
            suggestions.push("Try Second Inversion for possible improvement");
        }
        
        // Special suggestion for barres with stretch
        if (Object.values(fretCounts).some(count => count >= 3) && fretStretch > 2) {
            suggestions.push("Consider focusing on the barre shape at one position");
        }
        
        // If no suggestions needed, give positive feedback
        if (suggestions.length === 0) {
            if (playabilityScore >= 90) {
                suggestions.push("Excellent ergonomic voicing");
            } else if (playabilityScore >= 80) {
                suggestions.push("Good playable voicing");
            } else {
                suggestions.push("Acceptable voicing");
            }
        }
        
        // Update UI
        updatePlayabilityDisplay({
            score: playabilityScore,
            fretStretch,
            stringStretch,
            fingerCount,
            suggestions: suggestions.join("; ")
        });
        
            playabilityScore,
            fretStretch,
            stringStretch,
            fingerCount,
            suggestions
        });
        
        return {
            score: playabilityScore,
            fretStretch,
            stringStretch,
            fingerCount,
            suggestions
        };
    } catch (error) {
        console.error("Error analyzing chord playability:", error);
        return null;
    }
}

/**
 * Update the playability display with analysis results
 */
function updatePlayabilityDisplay(data) {
    try {
        // Also update the playability indicator in the main UI if it exists
        const indicatorBar = document.getElementById('playability-bar');
        if (indicatorBar && data.score !== "N/A") {
            // Update width based on score
            indicatorBar.style.width = `${data.score}%`;
            
            // Update color based on score
            if (data.score >= 85) {
                indicatorBar.style.backgroundColor = "#4CAF50"; // Green for good
            } else if (data.score >= 70) {
                indicatorBar.style.backgroundColor = "#FFC107"; // Amber for ok
            } else if (data.score >= 50) {
                indicatorBar.style.backgroundColor = "#FF9800"; // Orange for difficult
            } else {
                indicatorBar.style.backgroundColor = "#F44336"; // Red for very hard
            }
        }
        
        // Skip the rest if DEBUG_MODE is not enabled
        if (!window.DEBUG_MODE) return;
        
        // Get UI elements for debug panel
        const scoreElement = document.getElementById('playability-score-value');
        const scoreBar = document.getElementById('playability-score-bar');
        const fretStretchElement = document.getElementById('fret-stretch-value');
        const stringStretchElement = document.getElementById('string-stretch-value');
        const fingerCountElement = document.getElementById('finger-count-value');
        const complexityElement = document.getElementById('position-complexity-value');
        const suggestionsList = document.getElementById('playability-suggestions');
        
        if (!scoreElement || !suggestionsList) return;
        
        // Update score value
        if (data.score === "N/A") {
            scoreElement.textContent = "N/A";
            scoreElement.style.color = "#888";
            
            if (scoreBar) {
                scoreBar.style.width = "0%";
                scoreBar.style.backgroundColor = "#555";
            }
        } else {
            scoreElement.textContent = data.score + "/100";
            
            // Update progress bar
            if (scoreBar) {
                scoreBar.style.width = `${data.score}%`;
                
                // Color based on score
                if (data.score >= 85) {
                    scoreBar.style.backgroundColor = "#4CAF50"; // Green for good
                    scoreElement.style.color = "#4CAF50";
                } else if (data.score >= 70) {
                    scoreBar.style.backgroundColor = "#FFC107"; // Amber for ok
                    scoreElement.style.color = "#FFC107";
                } else if (data.score >= 50) {
                    scoreBar.style.backgroundColor = "#FF9800"; // Orange for difficult
                    scoreElement.style.color = "#FF9800";
                } else {
                    scoreBar.style.backgroundColor = "#F44336"; // Red for very hard
                    scoreElement.style.color = "#F44336";
                }
            }
        }
        
        // Update metrics
        if (fretStretchElement) {
            fretStretchElement.textContent = data.fretStretch + " frets";
            fretStretchElement.style.color = data.fretStretch > 4 ? "#F44336" : 
                                             data.fretStretch > 3 ? "#FF9800" : "#BBB";
        }
        
        if (stringStretchElement) {
            stringStretchElement.textContent = data.stringStretch + " strings";
            stringStretchElement.style.color = data.stringStretch > 4 ? "#F44336" : 
                                              data.stringStretch > 3 ? "#FF9800" : "#BBB";
        }
        
        if (fingerCountElement) {
            const displayText = data.fingerCount > 4 ? 
                               `${data.fingerCount} (excessive)` : 
                               `${data.fingerCount} fingers`;
            fingerCountElement.textContent = displayText;
            fingerCountElement.style.color = data.fingerCount > 4 ? "#F44336" : 
                                            data.fingerCount === 4 ? "#FF9800" : "#BBB";
        }
        
        // Update position complexity
        if (complexityElement) {
            let complexity = "Easy";
            if (data.score < 50) complexity = "Very Difficult";
            else if (data.score < 70) complexity = "Difficult";
            else if (data.score < 85) complexity = "Moderate";
            
            complexityElement.textContent = complexity;
            complexityElement.style.color = data.score >= 85 ? "#4CAF50" : 
                                           data.score >= 70 ? "#FFC107" :
                                           data.score >= 50 ? "#FF9800" : "#F44336";
        }
        
        // Update suggestions list
        if (suggestionsList) {
            // Clear the list
            suggestionsList.innerHTML = '';
            
            if (data.suggestions) {
                // Split the suggestions by semicolon
                const suggestions = data.suggestions.split(';');
                
                // Add each suggestion as a list item
                suggestions.forEach(suggestion => {
                    const trimmed = suggestion.trim();
                    if (trimmed) {
                        const li = document.createElement('li');
                        li.textContent = trimmed;
                        suggestionsList.appendChild(li);
                    }
                });
            } else {
                // No suggestions
                const li = document.createElement('li');
                li.textContent = 'No suggestions available';
                suggestionsList.appendChild(li);
            }
        }
    } catch (error) {
        console.error("Error updating playability display:", error);
    }
}

/**
 * Find alternative voicings for the current chord
 * This is a placeholder function that will be completed in future versions
 */
function findAlternativeVoicings() {
    alert("Finding alternative voicings is not implemented yet. This will be available in a future version.");
    
    // Log to console for debugging
        voicingData: window.voicing_data,
        urlParams: new URLSearchParams(window.location.search),
        activeNotes: document.querySelectorAll('.note.active').length
    });
}

/**
 * Listen for navigation and other events to log in the debug panel
 */
function listenForNavigationEvents() {
    try {
        // Only set up listeners if debug panel exists
        if (!document.getElementById('debug-event-log')) {
            return;
        }
        
        // Listen for left cursor clicks
        document.addEventListener('chord-position-activated', function(e) {
            try {
                logEvent(`Position activated: ${e.detail.position} (success: ${e.detail.success})`);
                updateDebugPanelData();
            } catch (eventError) {
                console.error("Error in chord-position-activated handler:", eventError);
            }
        });
        
        // Listen for chord tones update
        document.addEventListener('chord-tones-updated', function(e) {
            try {
                logEvent(`Tones updated: ${e.detail.position}, ${e.detail.range} (success: ${e.detail.success})`);
                updateDebugPanelData();
            } catch (eventError) {
                console.error("Error in chord-tones-updated handler:", eventError);
            }
        });
    } catch (error) {
        console.error("Error setting up navigation event listeners:", error);
    }
    
    // Listen for any clicks on cursor navigation elements
    document.querySelectorAll('.left-cursor, .right-cursor').forEach(cursor => {
        cursor.addEventListener('click', function() {
            logEvent(`Cursor clicked: ${this.className}`);
            // Update after a short delay to allow navigation to complete
            setTimeout(updateDebugPanelData, 300);
        });
    });
}

/**
 * Log an event to the debug panel
 */
function logEvent(message) {
    try {
        const logElement = document.getElementById('debug-event-log');
        if (!logElement) {
            return;
        }
        
        // Create timestamp
        const now = new Date();
        const timestamp = now.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            fractionalSecondDigits: 3
        });
        
        // Create log entry
        const entry = document.createElement('div');
        entry.textContent = `[${timestamp}] ${message}`;
        
        // Add to log and scroll to bottom
        logElement.appendChild(entry);
        logElement.scrollTop = logElement.scrollHeight;
        
        // Keep log size manageable
        while (logElement.childNodes.length > 50) {
            logElement.removeChild(logElement.firstChild);
        }
        
        // Also log to console for debugging
    } catch (error) {
        console.error("Error logging event:", error);
    }
}

/**
 * Reset chord state by clearing classes and reloading current position
 */
function resetChordState() {
    logEvent("Resetting chord state...");
    
    // Clear all active classes
    document.querySelectorAll('.active').forEach(el => {
        el.classList.remove('active');
    });
    
    document.querySelectorAll('.root').forEach(el => {
        el.classList.remove('root');
        if (el.tagName === 'IMG') {
            el.src = '/static/media/yellow_circle.svg';
        }
    });
    
    document.querySelectorAll('.inversion-note, .inversion-tone').forEach(el => {
        el.classList.remove('inversion-note', 'inversion-tone');
    });
    
    // Get current position and range
    const urlParams = new URLSearchParams(window.location.search);
    const position = urlParams.get('position_select') || 'Root Position';
    const range = urlParams.get('note_range') || 'e - g';
    
    // Try to reactivate the correct position
    logEvent(`Reactivating position: ${position}, range: ${range}`);
    
    if (typeof getTonesFromDataChords === 'function') {
        setTimeout(() => getTonesFromDataChords(position, range), 100);
    }
    
    // Update debug panel
    setTimeout(updateDebugPanelData, 200);
}

/**
 * Fix navigation state by reloading the page with proper URL parameters
 */
function fixNavigationState() {
    logEvent("Fixing navigation state with page reload...");
    
    // Create a clean URL with the proper parameters
    const urlParams = new URLSearchParams(window.location.search);
    
    // Get position but ensure it's a known value
    let position = urlParams.get('position_select') || 'Root Position';
    if (!['Root Position', 'First Inversion', 'Second Inversion', 'Third Inversion'].includes(position)) {
        position = 'Root Position';
    }
    
    // Get range but ensure it's valid
    let range = urlParams.get('note_range') || 'e - g';
    const validRanges = voicing_data ? 
        Object.keys(voicing_data).filter(k => k !== 'chord' && k !== 'type' && k !== 'root' && k !== 'note_range') :
        ['e - g', 'e - d', 'b - d', 'g - A'];
    
    if (!validRanges.includes(range)) {
        range = validRanges[0] || 'e - g';
    }
    
    // Build new URL
    const newParams = new URLSearchParams();
    
    // Preserve existing parameters except position
    for (const [key, value] of urlParams.entries()) {
        if (key !== 'position_select' && key !== 'note_range') {
            newParams.set(key, value);
        }
    }
    
    // Set clean position and range values
    newParams.set('position_select', position);
    newParams.set('note_range', range);
    
    // Reload with new URL
    window.location.href = window.location.pathname + '?' + newParams.toString();
}