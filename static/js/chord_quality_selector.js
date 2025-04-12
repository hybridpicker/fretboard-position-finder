/**
 * Enhanced Chord Quality Selector
 * Provides an intuitive graphical interface for selecting chord qualities
 * Supports 8-string guitar chords and enhanced visualization
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Create the enhanced chord quality selector
    createEnhancedChordQualitySelector();
    
    // Initialize chord quality info tooltips
    initChordQualityTooltips();
});

/**
 * Create a visual grid-based chord quality selector
 */
function createEnhancedChordQualitySelector() {
    // Get chord qualities from the select element
    const chordSelect = document.getElementById('chords_options_select');
    if (!chordSelect) {
        console.warn("Chord select element not found");
        return;
    }
    
    // Get all available chord qualities
    const qualities = [];
    for (let i = 0; i < chordSelect.options.length; i++) {
        qualities.push({
            value: chordSelect.options[i].value,
            text: chordSelect.options[i].textContent.trim()
        });
    }
    
    // Get current selected quality
    const currentQuality = chordSelect.options[chordSelect.selectedIndex].value;
    
    // Create the chord quality selector container
    const container = document.createElement('div');
    container.id = 'chord-quality-grid';
    container.className = 'chord-quality-grid';
    
    // Group qualities by type
    const qualityGroups = {
        'Triads': [],
        'Sevenths': [],
        'Extended': [],
        'Altered': []
    };
    
    // Categorize each chord quality
    qualities.forEach(quality => {
        const text = quality.text;
        if (text.includes('Major 7') || text.includes('Minor 7') || 
            text.includes('Dominant 7') || text.includes('MinMaj 7') || 
            text.endsWith('7')) {
            qualityGroups['Sevenths'].push(quality);
        } else if (text.includes('9') || text.includes('11') || text.includes('13')) {
            qualityGroups['Extended'].push(quality);
        } else if (text.includes('#5') || text.includes('b5') || 
                  text.includes('sus') || text.includes('aug') || 
                  text.includes('dim')) {
            qualityGroups['Altered'].push(quality);
        } else {
            qualityGroups['Triads'].push(quality);
        }
    });
    
    // Create group containers and add qualities
    Object.keys(qualityGroups).forEach(groupName => {
        // Skip empty groups
        if (qualityGroups[groupName].length === 0) return;
        
        // Create group container
        const groupContainer = document.createElement('div');
        groupContainer.className = 'quality-group';
        
        // Add group heading
        const heading = document.createElement('h4');
        heading.textContent = groupName;
        groupContainer.appendChild(heading);
        
        // Add qualities grid
        const grid = document.createElement('div');
        grid.className = 'quality-buttons';
        
        // Add each quality button
        qualityGroups[groupName].forEach(quality => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'quality-button';
            button.textContent = quality.text;
            button.dataset.value = quality.value;
            
            // Mark as selected if current
            if (quality.value === currentQuality) {
                button.classList.add('selected');
            }
            
            // Add click handler
            button.addEventListener('click', function() {
                selectChordQuality(quality.value);
            });
            
            // Add color-coding based on chord type
            addChordButtonStyling(button, quality.text);
            
            grid.appendChild(button);
        });
        
        groupContainer.appendChild(grid);
        container.appendChild(groupContainer);
    });
    
    // Add styling
    const style = document.createElement('style');
    style.textContent = `
        .chord-quality-grid {
            margin: 20px auto;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 600px;
        }
        
        .quality-group {
            margin-bottom: 15px;
        }
        
        .quality-group h4 {
            margin-bottom: 8px;
            color: #495057;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 5px;
        }
        
        .quality-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 8px;
        }
        
        .quality-button {
            padding: 8px 12px;
            border: 2px solid #ced4da;
            border-radius: 4px;
            background-color: #fff;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            position: relative;
        }
        
        .quality-button:hover {
            border-color: #adb5bd;
            background-color: #f1f3f5;
        }
        
        .quality-button.selected {
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            font-weight: bold;
        }
        
        /* Color-coding for different chord types */
        .quality-button.major {
            border-left: 4px solid #28a745;
        }
        
        .quality-button.minor {
            border-left: 4px solid #007bff;
        }
        
        .quality-button.dominant {
            border-left: 4px solid #fd7e14;
        }
        
        .quality-button.diminished {
            border-left: 4px solid #dc3545;
        }
        
        .quality-button.augmented {
            border-left: 4px solid #6f42c1;
        }
        
        .quality-button.suspended {
            border-left: 4px solid #20c997;
        }
    `;
    
    document.head.appendChild(style);
    
    // Insert the selector after form or analysis container
    const targetElement = document.querySelector('.analysis_container') || 
                         document.getElementById('fretboard_form');
    
    if (targetElement) {
        targetElement.parentNode.insertBefore(container, targetElement.nextSibling);
    }
}

/**
 * Add styling to chord buttons based on chord type
 */
function addChordButtonStyling(button, chordName) {
    if (chordName.startsWith('Major') || chordName === 'Augmented') {
        button.classList.add('major');
    } else if (chordName.startsWith('Minor') || chordName.startsWith('MinMaj')) {
        button.classList.add('minor');
    } else if (chordName.startsWith('Dominant') || chordName === '7') {
        button.classList.add('dominant');
    } else if (chordName.includes('dim') || chordName.includes('b5')) {
        button.classList.add('diminished');
    } else if (chordName.includes('aug') || chordName.includes('#5')) {
        button.classList.add('augmented');
    } else if (chordName.includes('sus')) {
        button.classList.add('suspended');
    } else {
        // Default for other types
        button.classList.add('major');
    }
}

/**
 * Initialize tooltips for chord qualities to explain their structure
 */
function initChordQualityTooltips() {
    // Chord quality descriptions
    const chordInfo = {
        'Major': '1-3-5: The basic major triad with a major third and perfect fifth',
        'Minor': '1-b3-5: Minor triad with a minor third and perfect fifth',
        'Diminished': '1-b3-b5: Minor third and diminished fifth',
        'Augmented': '1-3-#5: Major third and augmented fifth',
        'Major 7': '1-3-5-7: Major triad with a major seventh',
        'Dominant 7': '1-3-5-b7: Major triad with a minor seventh',
        'Minor 7': '1-b3-5-b7: Minor triad with a minor seventh',
        'MinMaj 7': '1-b3-5-7: Minor triad with a major seventh',
        'Major 7(#5)': '1-3-#5-7: Augmented triad with a major seventh',
        'Major 7(b5)': '1-3-b5-7: Major third, diminished fifth, major seventh',
        'Minor 7b5': '1-b3-b5-b7: Half-diminished chord (minor third, diminished fifth, minor seventh)',
        'Dominant 7(#5)': '1-3-#5-b7: Augmented triad with a minor seventh',
        'Dominant 7(b5)': '1-3-b5-b7: Major third, diminished fifth, minor seventh'
    };
    
    // Wait for buttons to be created
    setTimeout(() => {
        const qualityButtons = document.querySelectorAll('.quality-button');
        
        qualityButtons.forEach(button => {
            const chordName = button.textContent.trim();
            
            // Add tooltip if info exists
            if (chordInfo[chordName]) {
                button.title = chordInfo[chordName];
                
                // Add info indicator
                const infoIcon = document.createElement('span');
                infoIcon.className = 'info-icon';
                infoIcon.textContent = 'ℹ';
                button.appendChild(infoIcon);
            }
        });
        
        // Add info icon styling
        const style = document.createElement('style');
        style.textContent = `
            
            .quality-button:hover .info-icon {
                color: #007bff;
            }
        `;
        document.head.appendChild(style);
    }, 100);
}

/**
 * Select and apply a chord quality
 */
function selectChordQuality(quality) {
    // Update the select element
    const chordSelect = document.getElementById('chords_options_select');
    if (chordSelect) {
        // Find and select the matching option
        for (let i = 0; i < chordSelect.options.length; i++) {
            if (chordSelect.options[i].value === quality) {
                chordSelect.selectedIndex = i;
                break;
            }
        }
        
        // Update visual selection
        const buttons = document.querySelectorAll('.quality-button');
        buttons.forEach(btn => btn.classList.remove('selected'));
        
        const selectedButton = document.querySelector(`.quality-button[data-value="${quality}"]`);
        if (selectedButton) {
            selectedButton.classList.add('selected');
        }
        
        // Update URL parameters and reload
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set('chords_options_select', quality);
        
        // Preserve other parameters
        preserveEssentialParams(urlParams);
        
        // Navigate to updated URL
        window.location.href = window.location.pathname + '?' + urlParams.toString();
    }
}

/**
 * Preserve essential URL parameters
 */
function preserveEssentialParams(urlParams) {
    // Essential parameters to preserve
    const essentialParams = [
        'models_select', 'root', 'type_options_select',
        'note_range', 'position_select'
    ];
    
    // Get current URL parameters
    const currentParams = new URLSearchParams(window.location.search);
    
    // Copy essential parameters if they exist
    essentialParams.forEach(param => {
        if (currentParams.has(param) && !urlParams.has(param)) {
            urlParams.set(param, currentParams.get(param));
        }
    });
}
