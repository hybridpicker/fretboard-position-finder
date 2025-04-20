/**
 * Fretboard position optimizer
 * This script improves the scale position display and provides better user experience
 */

// Define resetFretboard function if it doesn't exist globally
if (typeof resetFretboard !== 'function') {
    window.resetFretboard = function() {
        var elements = document.querySelectorAll('.active');
        elements.forEach(function(element) {
            element.classList.remove('active');
        });
        
        var rootElements = document.querySelectorAll('.root');
        rootElements.forEach(function(element) {
            element.classList.remove('root');
        });
        
        var redCircles = document.querySelectorAll('img[src*="red_circle.svg"]');
        redCircles.forEach(function(element) {
            element.setAttribute('src', '/static/media/yellow_circle.svg');
        });
    };
}
document.addEventListener('DOMContentLoaded', function() {
    // Initialize optimization after the fretboard is loaded
    optimizeScalePositions();
    
    // Add highlight effect on hover for notes
    addNoteHoverEffects();
    
    // Add position navigation enhancement
    enhancePositionNavigation();
    
    // Add octave color indicators
    addOctaveColorIndicators();
});

/**
 * Optimize the scale positions for better ergonomics and playability
 */
function optimizeScalePositions() {
    // Get all active notes
    const activeNotes = document.querySelectorAll('.note.active');
    
    // Optimize note visibility
    activeNotes.forEach(note => {
        // Make note names always visible when the note is active
        const noteName = note.querySelector('.notename');
        if (noteName) {
            noteName.style.visibility = 'visible';
            
            // Add transition effect for smoother appearance
            noteName.style.transition = 'opacity 0.2s ease-in-out';
        }
    });
    
    // Identify clusters and optimize them
    identifyAndOptimizeClusters();
    
    // Check for ergonomic issues and resolve them
    checkErgonomicIssues();
}

/**
 * Identify clusters of notes that may be difficult to play and optimize them
 */
function identifyAndOptimizeClusters() {
    // Get all string elements
    const strings = {};
    string_array.forEach(string => {
        strings[string] = document.querySelectorAll('.' + string + ' .note.active');
    });
    
    // For each string, identify notes that are too close to each other
    for (const stringName in strings) {
        const notes = strings[stringName];
        // If there are 4 or more notes on a string, we may need to optimize
        if (notes.length >= 4) {
            // Get positions (fret numbers)
            const positions = Array.from(notes).map(note => {
                const fretClass = note.closest('.fret').className.match(/\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen)\b/);
                return fretClass ? fretClass[0] : null;
            }).filter(pos => pos !== null);
            
            // If the positions span more than 5 frets, deactivate some notes
            if (positions.length >= 4) {
                optimizeStringNotes(stringName, positions, notes);
            }
        }
    }
}

/**
 * Optimize notes on a string to make them more playable
 * @param {string} stringName - Name of the string
 * @param {Array} positions - Array of position names
 * @param {NodeList} notes - NodeList of note elements
 */
function optimizeStringNotes(stringName, positions, notes) {
    // Map position names to numeric values for comparison
    const positionValues = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
        'fifteen': 15, 'sixteen': 16, 'seventeen': 17
    };
    
    // Convert position names to numeric values
    const numericPositions = positions.map(pos => positionValues[pos]);
    
    // If the range exceeds 5 frets, deactivate outlier notes
    if (Math.max(...numericPositions) - Math.min(...numericPositions) > 5) {
        // Find outliers (notes that are far from the others)
        const outliers = findOutliers(numericPositions);
        
        // Deactivate outlier notes
        outliers.forEach(outlierIndex => {
            if (notes[outlierIndex]) {
                // Make the note visible but slightly different to indicate auxiliary status
                notes[outlierIndex].style.opacity = '0.85';
                
                // Add a different class to indicate it's an auxiliary note
                notes[outlierIndex].classList.add('auxiliary-note');
                
                // Add a border to distinguish it (instead of reducing opacity)
                notes[outlierIndex].style.border = '1px dashed #888';
                
                // Add tooltip to explain why this note is greyed out
                const tooltipSpan = document.createElement('span');
                tooltipSpan.className = 'tooltip';
                tooltipSpan.textContent = 'Auxiliary note (outside comfortable finger span)';
                notes[outlierIndex].appendChild(tooltipSpan);
            }
        });
    }
}

/**
 * Find outlier indices in an array of numeric positions
 * @param {Array} positions - Array of numeric positions
 * @returns {Array} - Array of outlier indices
 */
function findOutliers(positions) {
    // Calculate median position
    const sortedPositions = [...positions].sort((a, b) => a - b);
    const median = sortedPositions[Math.floor(sortedPositions.length / 2)];
    
    // Calculate distances from median
    const distances = positions.map(pos => Math.abs(pos - median));
    
    // Find the furthest note
    const maxDistance = Math.max(...distances);
    const outlierIndex = distances.indexOf(maxDistance);
    
    return [outlierIndex];
}

/**
 * Check for ergonomic issues and resolve them
 */
function checkErgonomicIssues() {
    // Get all active notes
    const activeNotes = document.querySelectorAll('.note.active');
    
    // Map of string indices to make it easier to check adjacent strings
    const stringIndices = {};
    string_array.forEach((string, index) => {
        stringIndices[string] = index;
    });
    
    // Check for notes that require difficult finger stretches
    activeNotes.forEach(note => {
        const fretElement = note.closest('.fret');
        const stringClass = Array.from(fretElement.classList).find(cls => string_array.includes(cls));
        
        if (stringClass && stringIndices[stringClass] !== undefined) {
            const currentStringIndex = stringIndices[stringClass];
            const fretClass = Array.from(fretElement.classList).find(cls => 
                ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 
                 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen'].includes(cls)
            );
            
            if (fretClass) {
                // Check adjacent strings for notes that would require difficult stretches
                checkAdjacentStringNotes(currentStringIndex, fretClass, note);
            }
        }
    });
}

/**
 * Check adjacent string notes for ergonomic issues
 * @param {number} currentStringIndex - Index of the current string
 * @param {string} fretClass - Class name of the current fret
 * @param {HTMLElement} currentNote - Current note element
 */
function checkAdjacentStringNotes(currentStringIndex, fretClass, currentNote) {
    // Define fret numbers for comparison
    const fretNumbers = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
        'fifteen': 15, 'sixteen': 16, 'seventeen': 17
    };
    
    const currentFretNumber = fretNumbers[fretClass];
    
    // Check adjacent strings (+/- 1 string)
    for (let offset of [-1, 1]) {
        const adjacentStringIndex = currentStringIndex + offset;
        
        if (adjacentStringIndex >= 0 && adjacentStringIndex < string_array.length) {
            const adjacentString = string_array[adjacentStringIndex];
            
            // Find adjacent string notes
            const adjacentNotes = document.querySelectorAll('.' + adjacentString + ' .note.active');
            
            adjacentNotes.forEach(adjacentNote => {
                const adjacentFretElement = adjacentNote.closest('.fret');
                const adjacentFretClass = Array.from(adjacentFretElement.classList).find(cls => 
                    ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 
                     'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen'].includes(cls)
                );
                
                if (adjacentFretClass) {
                    const adjacentFretNumber = fretNumbers[adjacentFretClass];
                    
                    // Check if the distance between frets is too large (greater than 5 frets is usually a stretch)
                    if (Math.abs(currentFretNumber - adjacentFretNumber) > 5) {
                        // Add a class to indicate a difficult stretch
                        currentNote.classList.add('stretch-warning');
                        adjacentNote.classList.add('stretch-warning');
                        
                        // Add a pulsing effect to highlight the difficult stretch
                        currentNote.style.animation = 'pulse 2s infinite';
                        adjacentNote.style.animation = 'pulse 2s infinite';
                    }
                }
            });
        }
    }
}

/**
 * Add hover effects to notes for better user experience
 */
function addNoteHoverEffects() {
    const allNotes = document.querySelectorAll('.note');
    
    allNotes.forEach(note => {
        // Add hover effect to show note name
        note.addEventListener('mouseenter', function() {
            const noteName = this.querySelector('.notename');
            if (noteName) {
                noteName.style.visibility = 'visible';
                noteName.style.opacity = '1';
            }
        });
        
        note.addEventListener('mouseleave', function() {
            const noteName = this.querySelector('.notename');
            if (noteName && !this.classList.contains('active')) {
                noteName.style.visibility = 'hidden';
                noteName.style.opacity = '0';
            }
        });
    });
}

/**
 * Enhance position navigation with visual cues (no keyboard controls)
 */
function enhancePositionNavigation() {
    // Keyboard navigation has been disabled
    
    // Add position indicator dots
    addPositionIndicatorDots();
}

/**
 * Add position indicator dots to show available positions with difficulty levels
 */
function addPositionIndicatorDots() {
    // Only proceed if scale_data is available
    if (typeof scale_data === 'undefined') {
        return;
    }
    
    // Create position indicators container
    const positionIndicators = document.createElement('div');
    positionIndicators.className = 'position-indicators';
    
    // Count the number of positions
    const positionCount = Object.keys(scale_data).filter(key => !isNaN(key)).length;
    
    // Get current position
    const url = new URL(window.location.href);
    const currentPosition = parseInt(url.searchParams.get('position_select') || '0');
    
    // Create dots for each position
    for (let i = 0; i < positionCount; i++) {
        const dot = document.createElement('span');
        dot.className = 'position-dot';
        
        // Add descriptive tooltip
        const info = document.createElement('span');
        info.className = 'position-info';
        
        // Set description based on position number
        let description = '';
        let difficulty = '';
        
        // Add click handler to navigate to position
        dot.addEventListener('click', function() {
            document.getElementById('position_select').value = i;
            document.getElementById('fretboard_form').submit();
        });
        
        positionIndicators.appendChild(dot);
    }
    
    // Append position indicators to fretboard container
    const fretboardContainer = document.getElementById('fretboardcontainer');
    fretboardContainer.appendChild(positionIndicators);
    
}

/**
 * Add octave color indicators to help distinguish different octaves
 */
function addOctaveColorIndicators() {
    // Add style for different octaves
    const style = document.createElement('style');
    style.textContent = `
        
        /* Position indicators and labels */
        .position-indicators {
            display: flex;
            justify-content: center;
            margin-top: 10px;
        }
        
        .position-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: #ccc;
            margin: 0 5px;
            cursor: pointer;
            transition: transform 0.2s ease-in-out, background-color 0.2s ease-in-out;
        }
        
        .position-dot:hover {
            transform: scale(1.2);
            background-color: #aaa;
        }
        
        .position-dot.current {
            background-color: #FF877A;
            transform: scale(1.2);
        }
        
        .position-label {
            text-align: center;
            margin-top: 5px;
            font-size: 12pt;
            color: #666;
        }
        
        /* Pulse animation for stretch warnings */
        @keyframes pulse {
            0% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
            100% {
                transform: scale(1);
            }
        }
        
        /* Tooltip styling */
        .tooltip {
            position: absolute;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 5px;
            border-radius: 3px;
            font-size: 10px;
            width: 150px;
            top: -30px;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
            z-index: 1000;
        }
        
        .auxiliary-note:hover .tooltip {
            opacity: 1;
        }
    `;
    
    document.head.appendChild(style);
    
    // Update SVG sources based on octave
    const notes = document.querySelectorAll('.note');
    notes.forEach(note => {
        // Try to identify the octave from the tone class name
        const toneNames = Array.from(note.classList).filter(cls => cls !== 'note' && cls !== 'active');
        
        if (toneNames.length > 0) {
            const toneName = toneNames[0];
            const octaveMatch = toneName.match(/[a-z]+([0-4])/);
            
            if (octaveMatch && octaveMatch[1]) {
                const octave = parseInt(octaveMatch[1]);
                const toneImg = note.querySelector('.tone');
                
                if (toneImg && !toneImg.classList.contains('root')) {
                    // Set appropriate SVG based on octave
                    let svgSrc = '/static/media/';
                    
                    // Determine which circle SVG to use based on octave
                    switch (octave) {
                        case 0:
                            svgSrc += 'circle_01.svg?v=2';
                            break;
                        case 1:
                            svgSrc += 'circle_01.svg?v=2';
                            break;
                        case 2:
                            svgSrc += 'circle_02.svg?v=2';
                            break;
                        case 3:
                            svgSrc += 'circle_03.svg?v=2';
                            break;
                        case 4:
                            svgSrc += 'circle_04.svg?v=2';
                            break;
                        default:
                            svgSrc += 'circle_01.svg?v=2';
                    }
                    
                    // Update the image source
                    if (toneImg.src.includes('yellow_circle.svg')) {
                        toneImg.src = svgSrc;
                    }
                }
            }
        }
    });
}
