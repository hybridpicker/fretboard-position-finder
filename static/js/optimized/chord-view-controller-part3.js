  /**
   * Update the chord display UI
   */
  updateChordDisplay() {
    this.performance.start('updateChordDisplay');
    
    // Update chord name display
    if (this.elements.chordDisplay) {
      const chordName = this.getChordDisplayName();
      this.elements.chordDisplay.textContent = chordName;
    }
    
    // Update inversion controls
    this.updateInversionDisplay(this.state.currentPosition);
    
    // Update position selector
    if (this.elements.positionSelector) {
      this.elements.positionSelector.value = this.state.currentPosition;
    }
    
    // Update range selector
    if (this.elements.rangeSelector) {
      this.elements.rangeSelector.value = this.state.currentRange;
    }
    
    this.performance.end('updateChordDisplay');
  }
  
  /**
   * Update the inversion display UI
   * @param {string} position - Current position
   */
  updateInversionDisplay(position) {
    const invertedDisplayName = position === 'Basic Position' ? 'Root Position' : position;
    
    // Update inversion controls if they exist
    document.querySelectorAll('.inversion-control').forEach(control => {
      const inversionType = control.dataset.inversion;
      
      if (inversionType === invertedDisplayName) {
        control.classList.add('active');
      } else {
        control.classList.remove('active');
      }
    });
    
    // Update inversion display if it exists
    const inversionDisplay = document.querySelector('.current-inversion');
    if (inversionDisplay) {
      inversionDisplay.textContent = invertedDisplayName;
    }
  }
  
  /**
   * Update available inversions for the current chord
   */
  updateAvailableInversions() {
    if (!this.state.currentChord) return;
    
    const chordType = this.state.currentChord.type;
    const range = this.state.currentRange;
    
    // Default inversions
    let inversions = ['Basic Position'];
    
    // For triads, add first and second inversions
    if (['Major', 'Minor', 'Diminished', 'Augmented'].includes(chordType)) {
      inversions = ['Basic Position', 'First Inversion', 'Second Inversion'];
    } 
    // For seventh chords, add first, second, and third inversions
    else if (chordType.includes('7')) {
      inversions = ['Basic Position', 'First Inversion', 'Second Inversion', 'Third Inversion'];
    }
    
    // Filter to only include inversions that have data
    const availableInversions = inversions.filter(inv => {
      const internalPos = inv === 'Root Position' ? 'Basic Position' : inv;
      return voicing_data && voicing_data[range] && voicing_data[range][internalPos];
    });
    
    this.components.inversions.availableInversions = availableInversions;
    
    // Update inversion controls visibility
    document.querySelectorAll('.inversion-control').forEach(control => {
      const inversionType = control.dataset.inversion;
      
      if (availableInversions.includes(inversionType) || 
          (inversionType === 'Root Position' && availableInversions.includes('Basic Position'))) {
        control.style.display = 'block';
      } else {
        control.style.display = 'none';
      }
    });
    
    this.log(`Available inversions for ${chordType}: ${availableInversions.join(', ')}`);
  }
  
  /**
   * Get the chord display name
   * @returns {string} Formatted chord name
   */
  getChordDisplayName() {
    if (!this.state.currentChord) return '';
    
    const { root, type, name } = this.state.currentChord;
    
    // If a complete chord name is provided, use it
    if (name) return name;
    
    // Otherwise construct from root and type
    let rootName = '';
    if (Array.isArray(root) && root.length > 0) {
      // Get root name without octave
      rootName = root[0].replace(/[0-9]/g, '');
      // Capitalize first letter
      rootName = rootName.charAt(0).toUpperCase() + rootName.slice(1);
    }
    
    return `${rootName} ${type}`;
  }
  
  /**
   * Get URL parameters or form values with fallbacks
   * @param {string} paramName - The parameter name to retrieve
   * @param {string} defaultValue - Default value if parameter is not found
   * @returns {string} The parameter value or default
   */
  getParameter(paramName, defaultValue) {
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
  getValidNoteRanges() {
    if (!voicing_data) return [];
    return Object.keys(voicing_data).filter(key => 
      !['chord', 'type', 'root', 'note_range'].includes(key));
  }
  
  /**
   * Validate and normalize parameters against available data
   * @param {string} positionValue - The position value to validate
   * @param {string} rangeValue - The range value to validate
   * @returns {object} Object with validated position and range values
   */
  validateParameters(positionValue, rangeValue) {
    const validRanges = this.getValidNoteRanges();
    let validatedRange = rangeValue;
    let validatedPosition = positionValue;
    
    // Handle numeric position "0" - always map to Root Position
    if (validatedPosition === '0' || validatedPosition === 0) {
      this.log(`Converting numeric position "0" to Root Position`);
      validatedPosition = 'Root Position';
    }
    
    // Validate range
    if (!validRanges.includes(validatedRange) && validRanges.length > 0) {
      this.log(`Invalid range ${validatedRange}, using ${validRanges[0]} instead`);
      validatedRange = validRanges[0];
    }
    
    // Handle "Root Position" vs "Basic Position" naming inconsistency
    const internalPosition = validatedPosition === 'Root Position' ? 'Basic Position' : validatedPosition;
    
    // Validate position for the given range
    if (voicing_data && voicing_data[validatedRange]) {
      const validPositions = Object.keys(voicing_data[validatedRange]);
      if (!validPositions.includes(internalPosition) && validPositions.length > 0) {
        this.log(`Invalid position ${validatedPosition}, using ${validPositions[0]} instead`);
        validatedPosition = validPositions[0];
      }
    }
    
    return { position: validatedPosition, range: validatedRange };
  }
  
  /**
   * Normalize V-System type names for consistency
   * @param {string} type - The V-System type to normalize
   * @returns {string} Normalized V-System type
   */
  normalizeVType(type) {
    if (!type) return '';
    
    // Ensure V-System notation is consistent
    const vSystemMatch = type.match(/^v[- ]?(\d+)$/i);
    if (vSystemMatch) {
      return `V-${vSystemMatch[1]}`;
    }
    
    return type;
  }
  
  /**
   * Get fret number from a fret element
   * @param {HTMLElement} fretEl - The fret element
   * @returns {number} The fret number (0-12), or -1 if not determined
   */
  getFretNumber(fretEl) {
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
  getPositionFretPreferences(position, chordType) {
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
      'Basic Position': {
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
      defaultPreferences['Basic Position'].BbString = [3, 5, 7];
      defaultPreferences['First Inversion'].BbString = [3, 5, 7];
      defaultPreferences['Second Inversion'].BbString = [7, 9, 2];
      defaultPreferences['Third Inversion'].BbString = [7, 9, 11];
    }
    
    // Special preference adjustments for specific chord types
    if (chordType === 'Major') {
      // For major chords, prefer more open positions in root position
      if (position === 'Root Position' || position === 'Basic Position') {
        return {
          ...defaultPreferences[position],
          eString: [0, 3, 7],  // Prefer open e string
          bString: [0, 3, 7],  // Prefer open b string
          EString: [0, 3, 7]   // Prefer open E string
        };
      }
    } else if (chordType === 'Minor') {
      // For minor chords, prefer certain fret positions
      if (position === 'Root Position' || position === 'Basic Position') {
        return {
          ...defaultPreferences[position],
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
    return defaultPreferences[position] || defaultPreferences['Basic Position'];
  }
  
  /**
   * Score a fret position for a particular string and position
   * @param {number} fretNum - The fret number to score
   * @param {string} stringName - The string name (eString, bString, etc.)
   * @param {string} position - The chord position/inversion
   * @param {object} preferences - The fret preferences
   * @returns {number} Score (lower is better)
   */
  scoreFretPosition(fretNum, stringName, position, preferences) {
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
    const chordType = this.state.currentChord?.type || '';
    
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
   * Close all select dropdowns except the one provided
   * @param {HTMLElement} [exceptElement] - Element to exclude from closing
   */
  closeAllSelect(exceptElement) {
    const x = document.getElementsByClassName('slit');
    const y = document.getElementsByClassName('sese');
    const arrNo = [];
    
    for (let i = 0; i < y.length; i++) {
      if (exceptElement === y[i]) {
        arrNo.push(i);
      } else {
        y[i].classList.remove('slar-active');
      }
    }
    
    for (let i = 0; i < x.length; i++) {
      if (arrNo.indexOf(i) === -1) {
        x[i].classList.add('sehi');
      }
    }
  }
  
  /**
   * Remove existing cursors from the DOM
   */
  removeCursors() {
    // Count cursors before removal for debugging
    const leftCursors = document.querySelectorAll('.left-cursor');
    const rightCursors = document.querySelectorAll('.right-cursor');
    
    this.log(`Removing ${leftCursors.length} left cursors and ${rightCursors.length} right cursors`);
    
    // Remove all cursors
    leftCursors.forEach(cursor => {
      if (cursor.parentNode) {
        cursor.parentNode.removeChild(cursor);
      }
    });
    
    rightCursors.forEach(cursor => {
      if (cursor.parentNode) {
        cursor.parentNode.removeChild(cursor);
      }
    });
    
    // Clear cursor arrays
    this.components.cursor.leftCursors = [];
    this.components.cursor.rightCursors = [];
  }
  
  /**
   * Throttle a function to limit execution frequency
   * @param {Function} func - The function to throttle
   * @param {number} wait - Wait time in milliseconds
   * @returns {Function} Throttled function
   */
  throttle(func, wait) {
    let lastCall = 0;
    return (...args) => {
      const now = Date.now();
      if (now - lastCall >= wait) {
        lastCall = now;
        return func.apply(this, args);
      }
    };
  }
  
  /**
   * Debug logger
   * @param {string} message - Message to log
   * @param {string} [level='debug'] - Log level (debug, info, warn, error)
   */
  log(message, level = 'debug') {
    if (!this.config.debug && level === 'debug') return;
    
    const timestamp = new Date().toISOString().substring(11, 23);
    console[level](`[${timestamp}][ChordView] ${message}`);
  }
}

/**
 * Performance monitoring utility class
 */
class PerformanceMonitor {
  /**
   * Create a new PerformanceMonitor
   * @param {boolean} enabled - Whether to enable monitoring
   */
  constructor(enabled = false) {
    this.enabled = enabled;
    this.measures = {};
  }
  
  /**
   * Start timing an operation
   * @param {string} operation - Operation name
   */
  start(operation) {
    if (!this.enabled) return;
    this.measures[operation] = performance.now();
  }
  
  /**
   * End timing an operation and log results
   * @param {string} operation - Operation name
   * @returns {number} Duration in milliseconds
   */
  end(operation) {
    if (!this.enabled || !this.measures[operation]) return 0;
    
    const duration = performance.now() - this.measures[operation];
    delete this.measures[operation];
    return duration;
  }
}

// Initialize the controller when the document is ready
document.addEventListener('DOMContentLoaded', () => {
  // Get debug mode from Django context if available
  const debugMode = window.DJANGO_DEBUG || false;
  
  // Count strings
  const stringCount = document.querySelector('.BbString') ? 8 : 
                      document.querySelector('.FString') ? 7 : 6;
  
  // Create controller with configuration
  window.chordViewController = new ChordViewController({
    debug: debugMode,
    enableCursors: true,
    enableInversions: true,
    enableKeyboardNavigation: true,
    stringCount: stringCount
  });
});
