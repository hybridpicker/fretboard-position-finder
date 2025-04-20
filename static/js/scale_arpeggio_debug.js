/**
 * Scale and Arpeggio Debug Helper
 * Provides detailed debugging information for scales and arpeggios
 */

document.addEventListener('DOMContentLoaded', function() {
    // Only initialize debug tools if DEBUG is true
    if (window.DJANGO_DEBUG) {
        
        // Create a debug panel if it doesn't exist
        createScaleArpeggioDebugPanel();
        
        // Listen for various events
        listenForScaleArpeggioEvents();
        
        // Add keyboard shortcut for debug panel: Ctrl+Shift+S
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.shiftKey && e.key === 'S') {
                e.preventDefault();
                toggleScaleArpeggioDebugPanel();
            }
        });
    } else {
    }
});

/**
 * Create a debug panel in the UI
 */
function createScaleArpeggioDebugPanel() {
    // Check if it already exists
    if (document.getElementById('scale-arpeggio-debug-panel')) return;
    
    // Create panel elements
    const panel = document.createElement('div');
    panel.id = 'scale-arpeggio-debug-panel';
    panel.style.position = 'fixed';
    panel.style.top = '10px';
    panel.style.right = '10px';
    panel.style.width = '300px';
    panel.style.padding = '10px';
    panel.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    panel.style.color = '#00FFAA';
    panel.style.zIndex = '9999';
    panel.style.fontFamily = 'monospace';
    panel.style.fontSize = '12px';
    // Only display if DEBUG is true
    panel.style.display = window.DJANGO_DEBUG ? 'block' : 'none';
    panel.style.maxHeight = '80vh';
    panel.style.overflowY = 'auto';
    
    // Add title with close button
    const titleContainer = document.createElement('div');
    titleContainer.style.display = 'flex';
    titleContainer.style.justifyContent = 'space-between';
    titleContainer.style.alignItems = 'center';
    titleContainer.style.paddingBottom = '5px';
    titleContainer.style.marginBottom = '10px';
    
    const title = document.createElement('div');
    title.style.fontWeight = 'bold';
    title.textContent = 'Scale & Arpeggio Debug';
    titleContainer.appendChild(title);
    
    const closeButton = document.createElement('button');
    closeButton.innerHTML = '&times;'; // × symbol
    closeButton.style.background = 'none';
    closeButton.style.border = 'none';
    closeButton.style.color = '#00FFAA';
    closeButton.style.fontSize = '20px';
    closeButton.style.cursor = 'pointer';
    closeButton.style.padding = '0 5px';
    closeButton.onclick = function() { toggleScaleArpeggioDebugPanel(); };
    closeButton.title = 'Close debug panel (Ctrl+Shift+S)';
    titleContainer.appendChild(closeButton);
    
    panel.appendChild(titleContainer);
    
    // Add help text
    const helpText = document.createElement('div');
    helpText.style.marginBottom = '10px';
    helpText.style.fontSize = '11px';
    helpText.style.padding = '5px';
    helpText.style.backgroundColor = 'rgba(0, 100, 80, 0.3)';
    helpText.innerHTML = 'Click section headers to expand/collapse.<br>' +
                      'Use the "Reset State" button to clear active notes.<br>' +
                      'Export button saves debug data as JSON.<br>' +
                      'Press Ctrl+Shift+S to toggle this panel.';
    panel.appendChild(helpText);
    
    // Add sections with collapsible headers
    addDebugSection(panel, 'scale-arpeggio-basic-info', 'Basic Information');
    addDebugSection(panel, 'scale-arpeggio-note-analysis', 'Note Analysis');
    addDebugSection(panel, 'scale-arpeggio-structure', 'Structure Analysis');
    addDebugSection(panel, 'scale-arpeggio-string-info', 'String Information');
    addDebugSection(panel, 'scale-arpeggio-eight-string', 'Eight-String Specifics');
    
    // Event log section
    const eventLogTitle = document.createElement('div');
    eventLogTitle.textContent = 'Event Log:';
    eventLogTitle.style.marginTop = '10px';
    eventLogTitle.style.cursor = 'pointer';
    eventLogTitle.style.color = '#00FFAA';
    eventLogTitle.onclick = function() {
        const log = document.getElementById('scale-arpeggio-event-log');
        log.style.display = log.style.display === 'none' ? 'block' : 'none';
    };
    panel.appendChild(eventLogTitle);
    
    const eventLog = document.createElement('div');
    eventLog.id = 'scale-arpeggio-event-log';
    eventLog.style.height = '150px';
    eventLog.style.overflowY = 'scroll';
    eventLog.style.fontSize = '11px';
    eventLog.style.marginBottom = '10px';
    panel.appendChild(eventLog);
    
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
    resetButton.onclick = function() { resetScaleArpeggioState(); };
    buttonContainer.appendChild(resetButton);
    
    // Export button
    const exportButton = document.createElement('button');
    exportButton.textContent = 'Export Debug Data';
    exportButton.onclick = function() { exportScaleArpeggioDebugData(); };
    buttonContainer.appendChild(exportButton);
    
    panel.appendChild(buttonContainer);
    
    // Add to the document
    document.body.appendChild(panel);
    
    // Update the panel with initial data
    setTimeout(updateScaleArpeggioDebugData, 500);
}

/**
 * Add a collapsible section to the debug panel
 */
function addDebugSection(panel, id, title) {
    const sectionTitle = document.createElement('div');
    sectionTitle.textContent = title;
    sectionTitle.style.marginTop = '10px';
    sectionTitle.style.paddingBottom = '2px';
    sectionTitle.style.cursor = 'pointer';
    sectionTitle.style.color = '#00FFAA';
    sectionTitle.onclick = function() {
        const content = document.getElementById(id);
        content.style.display = content.style.display === 'none' ? 'block' : 'none';
    };
    panel.appendChild(sectionTitle);
    
    const sectionContent = document.createElement('div');
    sectionContent.id = id;
    sectionContent.style.paddingTop = '5px';
    sectionContent.style.paddingBottom = '5px';
    panel.appendChild(sectionContent);
}

/**
 * Toggle debug panel visibility
 */
function toggleScaleArpeggioDebugPanel() {
    const panel = document.getElementById('scale-arpeggio-debug-panel');
    if (panel) {
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        
        // Update data when showing
        if (panel.style.display === 'block') {
            updateScaleArpeggioDebugData();
        }
    }
}

/**
 * Update the debug panel with current data
 */
function updateScaleArpeggioDebugData() {
    try {
        // Get URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        
        // Basic information
        updateBasicInfo(urlParams);
        
        // Note Analysis
        updateNoteAnalysis();
        
        // Structure Analysis
        updateStructureAnalysis();
        
        // String Information
        updateStringInfo();
        
        // Eight-String Specifics
        updateEightStringInfo();
        
        // Log update
        logScaleArpeggioEvent("Debug data updated");
    } catch (error) {
        console.error("Error updating scale/arpeggio debug data:", error);
        logScaleArpeggioEvent("Error updating debug data: " + error.message);
    }
}

/**
 * Update basic information section
 */
function updateBasicInfo(urlParams) {
    const container = document.getElementById('scale-arpeggio-basic-info');
    if (!container) return;
    
    // Clear previous content
    container.innerHTML = '';
    
    // Get parameters
    const root = urlParams.get('root') || '1';
    const modelSelect = urlParams.get('models_select') || '1';
    const notesOptions = urlParams.get('notes_options_select') || '1';
    const position = urlParams.get('position_select') || '0';
    
    // Determine mode based on models_select
    let mode = 'Scale';
    if (modelSelect === '2') mode = 'Arpeggio';
    else if (modelSelect === '3') mode = 'Chord';
    
    // Get additional data from the page
    const analysisContainer = document.querySelector('.analysis_container');
    const displayedName = analysisContainer?.querySelector('h2')?.textContent.trim() || 'Unknown';
    const noteCount = document.querySelectorAll('.note.active').length;
    const rootCount = document.querySelectorAll('.note.root').length;
    
    // Append info
    addInfoRow(container, 'Mode', mode);
    addInfoRow(container, 'Root ID', root);
    addInfoRow(container, 'Notes Option', notesOptions);
    addInfoRow(container, 'Position', position);
    addInfoRow(container, 'Displayed Name', displayedName);
    addInfoRow(container, 'Active Notes', noteCount);
    addInfoRow(container, 'Root Notes', rootCount);
    
    // Add instrument info
    const stringCount = getStringCount();
    addInfoRow(container, 'String Count', stringCount);
    addInfoRow(container, 'Tuning', getCurrentTuning(stringCount));
}

/**
 * Update note analysis section
 */
function updateNoteAnalysis() {
    const container = document.getElementById('scale-arpeggio-note-analysis');
    if (!container) return;
    
    // Clear previous content
    container.innerHTML = '';
    
    // Get all active notes and count by string
    const activeNotes = document.querySelectorAll('.note.active');
    const rootNotes = document.querySelectorAll('.note.root');
    
    // Get strings from the context or fallback to standard 6 strings
    const stringNames = window.string_array || ['eString', 'bString', 'gString', 'dString', 'AString', 'ELowString', 'BString', 'FString'].reverse();
    
    // Count notes by string
    const notesByString = {};
    
    for (let i = 0; i < stringNames.length; i++) {
        const stringName = stringNames[i];
        notesByString[stringName] = document.querySelectorAll('.' + stringName + ' .note.active').length;
    }
    
    // Count by fret
    const notesByFret = {};
    for (let i = 0; i <= 24; i++) {
        const count = document.querySelectorAll('.fret' + i + ' .note.active').length;
        if (count > 0) {
            notesByFret[i] = count;
        }
    }
    
    // Display stats
    addInfoRow(container, 'Total Active Notes', activeNotes.length);
    addInfoRow(container, 'Root Notes', rootNotes.length);
    
    // Display notes by string
    const stringInfo = document.createElement('div');
    stringInfo.style.marginTop = '5px';
    stringInfo.style.marginBottom = '5px';
    stringInfo.innerHTML = '<b>Notes Per String:</b>';
    
    const stringTable = document.createElement('table');
    stringTable.style.width = '100%';
    stringTable.style.fontSize = '11px';
    
    // Create table header
    const headerRow = document.createElement('tr');
    
    const stringHeader = document.createElement('th');
    stringHeader.textContent = 'String';
    stringHeader.style.textAlign = 'left';
    headerRow.appendChild(stringHeader);
    
    const countHeader = document.createElement('th');
    countHeader.textContent = 'Notes';
    countHeader.style.textAlign = 'right';
    headerRow.appendChild(countHeader);
    
    stringTable.appendChild(headerRow);
    
    // Add rows for each string
    for (let i = 0; i < stringNames.length; i++) {
        const stringName = stringNames[i];
        const row = document.createElement('tr');
        
        const stringCell = document.createElement('td');
        stringCell.textContent = stringName;
        row.appendChild(stringCell);
        
        const countCell = document.createElement('td');
        countCell.textContent = notesByString[stringName] || 0;
        countCell.style.textAlign = 'right';
        row.appendChild(countCell);
        
        stringTable.appendChild(row);
    }
    
    stringInfo.appendChild(stringTable);
    container.appendChild(stringInfo);
    
    // Display fret distribution
    const fretInfo = document.createElement('div');
    fretInfo.style.marginTop = '10px';
    fretInfo.innerHTML = '<b>Fret Distribution:</b>';
    
    const fretKeys = Object.keys(notesByFret).sort((a, b) => parseInt(a) - parseInt(b));
    if (fretKeys.length > 0) {
        const fretList = document.createElement('div');
        fretList.style.display = 'flex';
        fretList.style.flexWrap = 'wrap';
        fretList.style.gap = '5px';
        fretList.style.marginTop = '3px';
        
        fretKeys.forEach(fret => {
            const fretBadge = document.createElement('span');
            fretBadge.style.backgroundColor = '#004433';
            fretBadge.style.padding = '2px 5px';
            fretBadge.textContent = `Fret ${fret}: ${notesByFret[fret]}`;
            fretList.appendChild(fretBadge);
        });
        
        fretInfo.appendChild(fretList);
    } else {
        fretInfo.innerHTML += ' <i>No active frets</i>';
    }
    
    container.appendChild(fretInfo);
}

/**
 * Update structure analysis section
 */
function updateStructureAnalysis() {
    const container = document.getElementById('scale-arpeggio-structure');
    if (!container) return;
    
    // Clear previous content
    container.innerHTML = '';
    
    // Get note names from the page
    const noteNames = [];
    const noteNameElements = document.querySelectorAll('.analysis_container b');
    
    noteNameElements.forEach(el => {
        const text = el.textContent.trim();
        if (text && text.length <= 3 && !text.includes('Show')) {
            noteNames.push(text);
        }
    });
    
    // Filter to unique note names
    const uniqueNoteNames = [...new Set(noteNames)];
    
    // Get scale/arpeggio name
    const analysisContainer = document.querySelector('.analysis_container');
    let scaleOrArpeggioName = 'Unknown';
    if (analysisContainer) {
        const h2 = analysisContainer.querySelector('h2');
        if (h2) {
            scaleOrArpeggioName = h2.textContent.trim();
        }
    }
    
    // Display info
    addInfoRow(container, 'Name', scaleOrArpeggioName);
    addInfoRow(container, 'Note Count', uniqueNoteNames.length);
    
    // Note names
    const notesInfo = document.createElement('div');
    notesInfo.style.marginTop = '5px';
    notesInfo.innerHTML = '<b>Notes:</b> ' + uniqueNoteNames.join(', ');
    container.appendChild(notesInfo);
    
    // Add tensions from context
    try {
        let tensionsInfo = '';
        // Look for tensions in the analysis container
        const tensionElements = document.querySelectorAll('.analysis_container > b');
        if (tensionElements.length > 0) {
            const tensions = [];
            tensionElements.forEach(el => {
                const text = el.textContent.trim();
                if (text.match(/^(b9|9|#9|b11|11|#11|b13|13)$/)) {
                    tensions.push(text);
                }
            });
            if (tensions.length > 0) {
                tensionsInfo = tensions.join(', ');
            }
        }
        
        if (tensionsInfo) {
            const tensionsDisplay = document.createElement('div');
            tensionsDisplay.style.marginTop = '5px';
            tensionsDisplay.innerHTML = '<b>Tensions:</b> ' + tensionsInfo;
            container.appendChild(tensionsDisplay);
        }
    } catch (error) {
        console.error("Error getting tensions:", error);
    }
    
    // Data source check
    try {
        const dataSourceInfo = document.createElement('div');
        dataSourceInfo.style.marginTop = '10px';
        
        // Check if we have scale_data
        let dataSource = 'Unknown';
        if (typeof scale_data !== 'undefined') {
            dataSource = 'scale_data';
        }
        
        dataSourceInfo.innerHTML = '<b>Data Source:</b> ' + dataSource;
        container.appendChild(dataSourceInfo);
        
        // Show scale_data structure if available
        if (dataSource === 'scale_data') {
            const positionCount = Object.keys(scale_data).filter(k => !isNaN(k)).length;
            const rootInfo = scale_data.root ? Object.values(scale_data.root).join(', ') : 'Not found';
            
            const dataInfo = document.createElement('div');
            dataInfo.style.marginTop = '5px';
            dataInfo.innerHTML = `<b>Positions:</b> ${positionCount}<br>`;
            dataInfo.innerHTML += `<b>Root:</b> ${rootInfo}`;
            container.appendChild(dataInfo);
        }
    } catch (error) {
        console.error("Error analyzing data source:", error);
    }
}

/**
 * Update string information section
 */
function updateStringInfo() {
    const container = document.getElementById('scale-arpeggio-string-info');
    if (!container) return;
    
    // Clear previous content
    container.innerHTML = '';
    
    // Get strings from the context or fallback to standard 6 strings
    const stringNames = window.string_array || ['eString', 'bString', 'gString', 'dString', 'AString', 'ELowString', 'BString', 'FString'].reverse();
    
    // Create table
    const table = document.createElement('table');
    table.style.width = '100%';
    table.style.fontSize = '11px';
    
    // Header
    const header = document.createElement('tr');
    
    const stringHeader = document.createElement('th');
    stringHeader.textContent = 'String';
    stringHeader.style.textAlign = 'left';
    header.appendChild(stringHeader);
    
    const tuningHeader = document.createElement('th');
    tuningHeader.textContent = 'Notes';
    tuningHeader.style.textAlign = 'center';
    header.appendChild(tuningHeader);
    
    const rangeHeader = document.createElement('th');
    rangeHeader.textContent = 'Range';
    rangeHeader.style.textAlign = 'right';
    header.appendChild(rangeHeader);
    
    table.appendChild(header);
    
    // Add rows for each string
    for (let i = 0; i < stringNames.length; i++) {
        const stringName = stringNames[i];
        const row = document.createElement('tr');
        
        // String name
        const stringCell = document.createElement('td');
        stringCell.textContent = stringName;
        row.appendChild(stringCell);
        
        // Notes count
        const activeNotes = document.querySelectorAll('.' + stringName + ' .note.active').length;
        const notesCell = document.createElement('td');
        notesCell.textContent = activeNotes;
        notesCell.style.textAlign = 'center';
        row.appendChild(notesCell);
        
        // Fret range
        const fretRange = getStringFretRange(stringName);
        const rangeCell = document.createElement('td');
        rangeCell.textContent = fretRange;
        rangeCell.style.textAlign = 'right';
        row.appendChild(rangeCell);
        
        table.appendChild(row);
    }
    
    container.appendChild(table);
    
    // Add pattern analysis
    const patternAnalysis = analyzeNotePattern(stringNames);
    if (patternAnalysis) {
        const patternDiv = document.createElement('div');
        patternDiv.style.marginTop = '10px';
        patternDiv.innerHTML = `<b>Pattern Analysis:</b> ${patternAnalysis}`;
        container.appendChild(patternDiv);
    }
}

/**
 * Update eight-string specific information
 */
function updateEightStringInfo() {
    const container = document.getElementById('scale-arpeggio-eight-string');
    if (!container) return;
    
    // Clear previous content
    container.innerHTML = '';
    
    // Get strings from the context
    const stringNames = window.string_array || ['eString', 'bString', 'gString', 'dString', 'AString', 'ELowString', 'BString', 'FString'].reverse();
    
    // Only show this section for 8-string guitars
    if (stringNames.length < 7) {
        container.innerHTML = '<i>Not an 8-string guitar</i>';
        return;
    }
    
    // Get extended range statistics
    const lowStrings = stringNames.slice(0, 2); // First two strings are the lowest ones (7th and 8th)
    let lowStringCount = 0;
    lowStrings.forEach(stringName => {
        lowStringCount += document.querySelectorAll('.' + stringName + ' .note.active').length;
    });
    
    const standardStrings = stringNames.slice(2);
    let standardStringCount = 0;
    standardStrings.forEach(stringName => {
        standardStringCount += document.querySelectorAll('.' + stringName + ' .note.active').length;
    });
    
    // Calculate percentage of usage
    const totalActiveNotes = lowStringCount + standardStringCount;
    const lowStringPercentage = totalActiveNotes === 0 ? 0 : Math.round((lowStringCount / totalActiveNotes) * 100);
    
    // Display statistics
    addInfoRow(container, 'Extended Range Notes', lowStringCount);
    addInfoRow(container, 'Standard Range Notes', standardStringCount);
    addInfoRow(container, 'Extended Range Usage', lowStringPercentage + '%');
    
    // Extended range tuning
    addInfoRow(container, 'Extended Strings', lowStrings.join(', '));
    
    // Pattern analysis for extended range
    if (lowStringCount > 0) {
        // Check if there are root notes on extended strings
        let hasRootInExtended = false;
        lowStrings.forEach(stringName => {
            if (document.querySelectorAll('.' + stringName + ' .note.active.root').length > 0) {
                hasRootInExtended = true;
            }
        });
        
        const extendedInfo = document.createElement('div');
        extendedInfo.style.marginTop = '10px';
        
        if (hasRootInExtended) {
            extendedInfo.innerHTML = '<b>Extended Range Info:</b> Contains root notes (important for low-register playing)';
        } else {
            extendedInfo.innerHTML = '<b>Extended Range Info:</b> Used for extension tones (adds depth to standard positions)';
        }
        
        container.appendChild(extendedInfo);
    }
}

/**
 * Add an info row to a container
 */
function addInfoRow(container, label, value) {
    const row = document.createElement('div');
    row.style.display = 'flex';
    row.style.justifyContent = 'space-between';
    row.style.marginBottom = '3px';
    
    const labelSpan = document.createElement('span');
    labelSpan.textContent = label + ': ';
    labelSpan.style.fontWeight = 'bold';
    
    const valueSpan = document.createElement('span');
    valueSpan.textContent = value;
    
    row.appendChild(labelSpan);
    row.appendChild(valueSpan);
    
    container.appendChild(row);
}

/**
 * Get the number of strings in the current view
 */
function getStringCount() {
    return window.string_array ? window.string_array.length : 6;
}

/**
 * Get the current tuning based on string count
 */
function getCurrentTuning(stringCount) {
    if (stringCount === 8) {
        return 'F#, B, E, A, D, G, B, E';
    } else if (stringCount === 7) {
        return 'B, E, A, D, G, B, E';
    } else {
        return 'E, A, D, G, B, E';
    }
}

/**
 * Get the fret range for a specific string
 */
function getStringFretRange(stringName) {
    const activeNotes = document.querySelectorAll('.' + stringName + ' .note.active');
    
    if (activeNotes.length === 0) {
        return 'None';
    }
    
    let minFret = 24;
    let maxFret = 0;
    
    activeNotes.forEach(note => {
        // Find the fret by class name or parent element
        const fretClasses = Array.from(note.parentNode.classList).filter(c => c.startsWith('fret'));
        if (fretClasses.length > 0) {
            const fretNumber = parseInt(fretClasses[0].replace('fret', ''));
            minFret = Math.min(minFret, fretNumber);
            maxFret = Math.max(maxFret, fretNumber);
        }
    });
    
    return `${minFret} - ${maxFret}`;
}

/**
 * Analyze the pattern of notes across strings
 */
function analyzeNotePattern(stringNames) {
    // Count notes per string
    const notesByString = {};
    
    for (let i = 0; i < stringNames.length; i++) {
        const stringName = stringNames[i];
        notesByString[stringName] = document.querySelectorAll('.' + stringName + ' .note.active').length;
    }
    
    // Check if we have at least 3 notes on each string (typical for positional playing)
    let isPositional = true;
    let hasNotes = false;
    
    for (let i = 2; i < stringNames.length - 2; i++) { // Exclude outer strings
        const stringName = stringNames[i];
        if (notesByString[stringName] > 0) {
            hasNotes = true;
            if (notesByString[stringName] < 2) {
                isPositional = false;
                break;
            }
        }
    }
    
    if (!hasNotes) return null;
    
    if (isPositional) {
        return "Positional pattern (consistent notes across strings)";
    }
    
    // Check if notes are concentrated on a few adjacent strings
    const activeStrings = stringNames.filter(name => notesByString[name] > 0);
    if (activeStrings.length <= 3) {
        return "String-focused pattern (notes concentrated on few strings)";
    }
    
    return "Standard distribution across strings";
}

/**
 * Reset scale/arpeggio state
 */
function resetScaleArpeggioState() {
    logScaleArpeggioEvent("Resetting scale/arpeggio state...");
    
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
    
    // Get current position
    const urlParams = new URLSearchParams(window.location.search);
    const position = urlParams.get('position_select') || '0';
    
    // Try to reactivate the correct position
    logScaleArpeggioEvent(`Reactivating position: ${position}`);
    
    if (typeof getTonesFromDataScales === 'function') {
        setTimeout(() => getTonesFromDataScales(position), 100);
    }
    
    // Update debug panel
    setTimeout(updateScaleArpeggioDebugData, 300);
}

/**
 * Export debug data to console
 */
function exportScaleArpeggioDebugData() {
    try {
        // Collect data
        const urlParams = new URLSearchParams(window.location.search);
        const root = urlParams.get('root') || '1';
        const modelSelect = urlParams.get('models_select') || '1';
        const notesOptions = urlParams.get('notes_options_select') || '1';
        const position = urlParams.get('position_select') || '0';
        
        const activeNotes = document.querySelectorAll('.note.active').length;
        const rootNotes = document.querySelectorAll('.note.root').length;
        
        // Get strings and active notes per string
        const stringNames = window.string_array || ['eString', 'bString', 'gString', 'dString', 'AString', 'ELowString', 'BString', 'FString'].reverse();
        const notesByString = {};
        
        for (let i = 0; i < stringNames.length; i++) {
            const stringName = stringNames[i];
            notesByString[stringName] = document.querySelectorAll('.' + stringName + ' .note.active').length;
        }
        
        // Create debug report
        const debugData = {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            parameters: {
                root,
                modelSelect,
                notesOptions,
                position
            },
            notes: {
                total: activeNotes,
                roots: rootNotes,
                byString: notesByString
            },
            name: document.querySelector('.analysis_container h2')?.textContent.trim() || 'Unknown'
        };
        
        // Log to console and display message
        logScaleArpeggioEvent("Debug data exported to console (press F12 to view)");
        
        // Create downloadable file
        const blob = new Blob([JSON.stringify(debugData, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        
        // Create download link
        const a = document.createElement('a');
        a.href = url;
        a.download = `scale-debug-${new Date().toISOString().slice(0,10)}.json`;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
    } catch (error) {
        console.error("Error exporting debug data:", error);
        logScaleArpeggioEvent("Error exporting debug data: " + error.message);
    }
}

/**
 * Log an event to the debug panel
 */
function logScaleArpeggioEvent(message) {
    const logElement = document.getElementById('scale-arpeggio-event-log');
    if (!logElement) return;
    
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
}

/**
 * Listen for events specific to scales and arpeggios
 */
function listenForScaleArpeggioEvents() {
    // Listen for cursor navigation
    document.querySelectorAll('.left-cursor, .right-cursor').forEach(cursor => {
        cursor.addEventListener('click', function() {
            logScaleArpeggioEvent(`Cursor clicked: ${this.className}`);
            // Update after a short delay to allow navigation to complete
            setTimeout(updateScaleArpeggioDebugData, 300);
        });
    });
    
    // Listen for form submissions
    const form = document.getElementById('fretboard_form');
    if (form) {
        form.addEventListener('submit', function() {
            logScaleArpeggioEvent('Form submitted - updating position');
            // Can't update here as the page will reload
        });
    }
    
    // Listen for user interactions with UI controls
    document.querySelectorAll('select').forEach(select => {
        select.addEventListener('change', function() {
            logScaleArpeggioEvent(`Selection changed: ${this.name} = ${this.value}`);
        });
    });
}