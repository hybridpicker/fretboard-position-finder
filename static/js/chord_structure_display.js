/**
 * Chord Structure Display
 * Visual representation of chord quality, structure, and intervals
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Create the chord structure display
    createChordStructureDisplay();
    
    // Initialize keyboard event handlers
    initKeyboardHandlers();
});

/**
 * Creates a visual display of the chord structure with intervals
 */
function createChordStructureDisplay() {
    // Get chord information
    const rootName = document.querySelector('h2')?.textContent.split(' ')[0] || 'C';
    const chordName = document.querySelector('.chord-quality .detail-value')?.textContent || 'Major';
    const chordType = document.querySelector('.chord-type .detail-value')?.textContent || 'Triads';
    
    // Create container
    const container = document.createElement('div');
    container.id = 'chord-structure-display';
    container.className = 'chord-structure-display';
    
    // Add title
    const title = document.createElement('h4');
    title.textContent = 'Chord Structure';
    title.className = 'structure-title';
    container.appendChild(title);
    
    // Get chord information
    const chordInfo = getChordInfo(rootName, chordName);
    
    // Create interval diagram
    const intervalDiagram = document.createElement('div');
    intervalDiagram.className = 'interval-diagram';
    
    // Create header row with interval labels
    const headerRow = document.createElement('div');
    headerRow.className = 'diagram-row header-row';
    
    const intervals = chordInfo.intervals;
    intervals.forEach(interval => {
        const intervalCell = document.createElement('div');
        intervalCell.className = 'interval-cell';
        intervalCell.textContent = interval.label;
        headerRow.appendChild(intervalCell);
    });
    
    intervalDiagram.appendChild(headerRow);
    
    // Create semitone row
    const semitoneRow = document.createElement('div');
    semitoneRow.className = 'diagram-row semitone-row';
    
    intervals.forEach(interval => {
        const semitoneCell = document.createElement('div');
        semitoneCell.className = 'semitone-cell';
        semitoneCell.textContent = `${interval.semitones} `;
        
        // Add small text for semitones
        const smallText = document.createElement('small');
        smallText.textContent = 'semitones';
        semitoneCell.appendChild(smallText);
        
        semitoneRow.appendChild(semitoneCell);
    });
    
    intervalDiagram.appendChild(semitoneRow);
    
    // Create note row
    const noteRow = document.createElement('div');
    noteRow.className = 'diagram-row note-row';
    
    chordInfo.notes.forEach(note => {
        const noteCell = document.createElement('div');
        noteCell.className = 'note-cell';
        noteCell.textContent = note;
        noteRow.appendChild(noteCell);
    });
    
    intervalDiagram.appendChild(noteRow);
    
    container.appendChild(intervalDiagram);
    
    // Add chord description
    const description = document.createElement('div');
    description.className = 'chord-description';
    description.innerHTML = chordInfo.description;
    container.appendChild(description);
    
    // Add relative keys section if applicable
    if (chordInfo.relatives && chordInfo.relatives.length > 0) {
        const relativesSection = document.createElement('div');
        relativesSection.className = 'relatives-section';
        
        const relativesTitle = document.createElement('h5');
        relativesTitle.textContent = 'Common Uses';
        relativesSection.appendChild(relativesTitle);
        
        const relativesList = document.createElement('ul');
        
        chordInfo.relatives.forEach(relative => {
            const listItem = document.createElement('li');
            listItem.innerHTML = relative;
            relativesList.appendChild(listItem);
        });
        
        relativesSection.appendChild(relativesList);
        container.appendChild(relativesSection);
    }
    
    // Add voicing variations section
    const voicingSection = document.createElement('div');
    voicingSection.className = 'voicing-section';
    
    const voicingTitle = document.createElement('h5');
    voicingTitle.textContent = 'Practical Voicings';
    voicingSection.appendChild(voicingTitle);
    
    // Add some practical voicing patterns
    const voicingText = document.createElement('p');
    voicingText.innerHTML = `
        Experiment with these voicing techniques on the 8-string:
        <ul>
            <li><strong>Drop-2:</strong> Drop the second highest note down an octave</li>
            <li><strong>Spread Triads:</strong> Space notes out across multiple octaves</li>
            <li><strong>Shell Voicings:</strong> Use just the root, 3rd, and 7th for a minimal sound</li>
            <li><strong>Quartal:</strong> Stack notes in 4ths instead of 3rds</li>
        </ul>
    `;
    voicingSection.appendChild(voicingText);
    
    container.appendChild(voicingSection);
    
    // Add styling
    const style = document.createElement('style');
    style.textContent = `
        .chord-structure-display {
            margin: 20px auto;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 600px;
        }
        
        .structure-title {
            margin-bottom: 15px;
            color: #495057;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 5px;
        }
        
        .interval-diagram {
            margin-bottom: 20px;
        }
        
        .diagram-row {
            display: flex;
            justify-content: space-around;
            margin-bottom: 5px;
        }
        
        .header-row {
            font-weight: bold;
            color: #007bff;
        }
        
        .interval-cell, .semitone-cell, .note-cell {
            flex: 1;
            text-align: center;
            padding: 5px;
            border-radius: 4px;
        }
        
        .semitone-cell {
            background-color: #e9ecef;
            font-size: 0.9rem;
        }
        
        .semitone-cell small {
            display: block;
            font-size: 0.7rem;
            color: #6c757d;
        }
        
        .note-cell {
            background-color: #e7f1ff;
            font-weight: bold;
            font-size: 1.2rem;
            color: #212529;
        }
        
        .chord-description {
            margin: 15px 0;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 4px;
            font-size: 0.9rem;
            color: #495057;
        }
        
        .relatives-section, .voicing-section {
            margin-top: 15px;
        }
        
        .relatives-section h5, .voicing-section h5 {
            color: #495057;
            margin-bottom: 5px;
        }
        
        .relatives-section ul, .voicing-section ul {
            margin: 5px 0 0 0;
            padding-left: 20px;
        }
        
        .relatives-section li, .voicing-section li {
            margin-bottom: 3px;
        }
    `;
    
    document.head.appendChild(style);
    
    // Insert after inversion visualizer or range selector
    const targetElement = document.getElementById('inversion-visualizer') || 
                         document.getElementById('string-range-selector') || 
                         document.getElementById('chord-quality-grid') || 
                         document.getElementById('fretboard_form');
    
    if (targetElement) {
        targetElement.parentNode.insertBefore(container, targetElement.nextSibling);
    }
}

/**
 * Get detailed chord information based on chord name and root
 */
function getChordInfo(rootName, chordName) {
    // Default chord info structure for major triad
    const defaultInfo = {
        intervals: [
            { label: 'R', semitones: 0 },
            { label: '3', semitones: 4 },
            { label: '5', semitones: 7 }
        ],
        notes: [rootName],
        description: 'A standard major triad consisting of root, major third, and perfect fifth.',
        relatives: []
    };
    
    // Calculate notes based on root and intervals
    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const rootIndex = notes.indexOf(rootName);
    
    if (rootIndex === -1) return defaultInfo;
    
    // Calculate the actual notes for the chord
    const chordNotes = defaultInfo.intervals.map(interval => {
        const noteIndex = (rootIndex + interval.semitones) % 12;
        return notes[noteIndex];
    });
    
    // Update the notes array with the calculated notes
    defaultInfo.notes = chordNotes;
    
    // Add relative key information
    defaultInfo.relatives = [
        `<strong>I chord</strong> in ${rootName} major key`,
        `<strong>IV chord</strong> in ${getNoteAtInterval(rootName, 5)} major key`,
        `<strong>V chord</strong> in ${getNoteAtInterval(rootName, 7)} major key`
    ];
    
    return defaultInfo;
}

/**
 * Get note at specified interval from root
 */
function getNoteAtInterval(rootNote, semitones) {
    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const rootIndex = notes.indexOf(rootNote);
    
    if (rootIndex === -1) return 'C';
    
    const targetIndex = (rootIndex + semitones) % 12;
    return notes[targetIndex];
}

/**
 * Initialize keyboard event handlers for navigation
 */
function initKeyboardHandlers() {
    document.addEventListener('keydown', function(e) {
        // Keyboard shortcuts for common chord qualities
        if (e.ctrlKey || e.metaKey) {
            // Prevent default action
            if (['m', 'M', '7', 'd', 'a'].includes(e.key)) {
                e.preventDefault();
            }
            
            // Select chord quality based on key
            if (e.key === 'M') {
                selectChordQualityByName('Major');
            } else if (e.key === 'm') {
                selectChordQualityByName('Minor');
            } else if (e.key === '7') {
                selectChordQualityByName('Dominant 7');
            } else if (e.key === 'd') {
                selectChordQualityByName('Diminished');
            } else if (e.key === 'a') {
                selectChordQualityByName('Augmented');
            }
        }
    });
}

/**
 * Select a chord quality by name
 */
function selectChordQualityByName(qualityName) {
    const chordSelect = document.getElementById('chords_options_select');
    if (!chordSelect) return;
    
    // Find the option with matching text
    for (let i = 0; i < chordSelect.options.length; i++) {
        if (chordSelect.options[i].textContent.trim() === qualityName) {
            chordSelect.selectedIndex = i;
            
            // Update URL parameters and reload
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('chords_options_select', chordSelect.options[i].value);
            
            // Preserve other parameters
            ['models_select', 'root', 'type_options_select', 'note_range', 'position_select'].forEach(param => {
                const currentValue = urlParams.get(param);
                if (!currentValue) {
                    const currentParams = new URLSearchParams(window.location.search);
                    if (currentParams.has(param)) {
                        urlParams.set(param, currentParams.get(param));
                    }
                }
            });
            
            // Navigate to updated URL - always use root path for unified view
            window.location.href = '/' + '?' + urlParams.toString();
            break;
        }
    }
}
