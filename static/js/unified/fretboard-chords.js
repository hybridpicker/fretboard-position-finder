/**
 * Unified Fretboard Chord Controller
 * 
 * Chord-specific implementation for the unified fretboard controller.
 * This file builds on fretboard-core.js to provide chord-specific functionality.
 * 
 * @author Cascade AI Assistant
 */

console.log('DEBUGGING: fretboard-chords.js loaded at', new Date().toISOString());

const NOTE_CANONICAL_MAPPING = {
  "C": { id: 1, class: "c" },
  "Db": { id: 2, class: "db" },
  "C#": { id: 3, class: "cs" },
  "D": { id: 4, class: "d" },
  "Eb": { id: 5, class: "eb" },
  "D#": { id: 6, class: "ds" },
  "E": { id: 7, class: "e" },
  "F": { id: 8, class: "f" },
  "Gb": { id: 9, class: "gb" },
  "F#": { id: 10, class: "fs" },
  "G": { id: 11, class: "g" },
  "Ab": { id: 12, class: "ab" },
  "G#": { id: 13, class: "gs" },
  "A": { id: 14, class: "a" },
  "Bb": { id: 15, class: "bb" },
  "A#": { id: 16, class: "as" },
  "B": { id: 17, class: "b" }
};

// Mapping from fret word to number
const FRET_WORD_TO_NUMBER = {
  'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
  'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
  'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
  'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
  'eighteen': 18, 'nineteen': 19, 'twenty': 20
};

// Enhanced fret number extraction to handle both numeric and word-based classes
function getFretNumberFromClassList(classList) {
  // Try numeric first (e.g., fret11)
  let fretClass = Array.from(classList).find(cls => cls.startsWith('fret'));
  console.log('[FretParse] classList:', Array.from(classList));
  if (!fretClass) {
    console.warn('[FretParse] No class starting with "fret" found.', Array.from(classList));
    return -1;
  }
  // Try to extract number at the end (fret11)
  let num = parseInt(fretClass.replace('fret', ''));
  if (!isNaN(num)) {
    console.log('[FretParse] Parsed numeric fret:', num, 'from', fretClass);
    return num;
  }
  // If not numeric, check for word (fret eleven)
  if (fretClass === 'fret') {
    // Look for the next class that is a fret word
    for (const cls of classList) {
      if (FRET_WORD_TO_NUMBER.hasOwnProperty(cls)) {
        console.log('[FretParse] Parsed word fret:', FRET_WORD_TO_NUMBER[cls], 'from', cls);
        return FRET_WORD_TO_NUMBER[cls];
      }
    }
    console.warn('[FretParse] No matching fret word found in classList.', Array.from(classList));
  }
  console.warn('[FretParse] Could not parse fret number from classList.', Array.from(classList));
  return -1;
}

class ChordFretboardController extends FretboardCore {
  constructor(options = {}) {
    // Call the parent constructor with merged options
    super({
      ...options,
      viewType: 'chord'
    });
    
    // Chord-specific state
    this.chordState = {
      selectedChord: null,
      currentPosition: 'Basic Position',
      currentRange: 'e - g',
      voicingData: null,
      rootNote: null,
      chordType: null,
      fretPreferences: null
    };
  }
  
  /**
   * Initialize the chord fretboard controller
   * @param {Object} options - Initialization options
   */
  init(options = {}) {
    // Call parent init
    super.init(options);
    this.log('Initializing chord fretboard controller', 'info');
    
    // Ensure the overlay menu is hidden initially
    const overlayMenuChords = document.getElementById('overlayMenuChords');
    if (overlayMenuChords) {
      overlayMenuChords.style.display = 'none';
    }
    
    // Set up chord-specific handlers
    this._setupChordUIEvents();
    
    // Load voicing data
    this._initFretboard();
    
    return this;
  }
  
  /**
   * Set up event listeners specific to chord view
   * @private
   */
  _setupChordUIEvents() {
    // Set up navigation elements
    const setupNavElement = (className) => {
      const elements = document.getElementsByClassName(className);
      
      for (let i = 0; i < elements.length; i++) {
        const element = elements[i];
        
        element.addEventListener('click', (e) => {
          e.stopPropagation();
          this._closeAllSelect(element);
          element.classList.toggle('active');
          
          // When clicked, update the chord display
          const posVal = this.getParameter('position_select', 'Basic Position');
          const noteRange = this.getParameter('note_range', 'e - g');
          
          // Validate and normalize parameters
          const validated = this._validateParameters(posVal, noteRange);
          
          // Update the fretboard
          this.updateChordDisplay(validated.position, validated.range);
        });
      }
    };
    
    // Initialize navigation elements
    setupNavElement('sfbsfnr');  // Root note selectors
    setupNavElement('catsfbsf'); // Category selectors
    setupNavElement('sfbsfpos'); // Position selectors
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => this._closeAllSelect(null));
    
    // Handle cursor navigation system
    if (typeof initCursorManagement === 'function') {
      initCursorManagement('chords');
    } else {
      // Show cursors if cursor management is not available
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
    
    // Enhance chord display if available
    if (typeof enhanceChordDisplay === 'function') {
      setTimeout(enhanceChordDisplay, 100);
    }
  }
  
  /**
   * Close all select boxes except the current one
   * @param {HTMLElement} element - The element to keep open
   * @private
   */
  _closeAllSelect(element) {
    const x = document.getElementsByClassName('slit');
    const y = document.getElementsByClassName('sese');
    const arrNo = [];
    
    for (let i = 0; i < y.length; i++) {
      if (element === y[i]) {
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
   * Initialize the fretboard with chord data
   * @private
   */
  _initFretboard() {
    // Wait for voicing_data to be available
    if (typeof voicing_data === 'undefined') {
      this.log('Waiting for voicing_data to be available...', 'debug');
      setTimeout(() => this._initFretboard(), 200);
      return;
    }
    
    this.log('voicing_data loaded, initializing fretboard', 'info');
    
    // Store voicing data
    this.chordState.voicingData = voicing_data;
    
    // Extract chord information
    this.chordState.rootNote = voicing_data.root || 'Unknown';
    this.chordState.chordType = voicing_data.type || 'Unknown';
    
    // Get valid note ranges
    const validRanges = this._getValidNoteRanges();
    
    this.log(`Available chord data: ${voicing_data.chord || 'Unknown'} ${voicing_data.type || 'Unknown'} (${voicing_data.root || 'Unknown'})`, 'info');
    
    // Get position and range parameters
    const posVal = this.getParameter('position_select', 'Basic Position');
    const noteRange = this.getParameter('note_range', 'e - g');
    
    // Validate parameters
    const validated = this._validateParameters(posVal, noteRange);
    
    // Normalize V-System type if present
    if (voicing_data && voicing_data.type) {
      voicing_data.type = this._normalizeVType(voicing_data.type);
      this.log(`Normalized chord type to ${voicing_data.type}`, 'debug');
    }
    
    // Initialize fret preferences
    this._initializeFretPreferences();
    
    // Update the fretboard
    this.updateChordDisplay(validated.position, validated.range);
  }
  
  /**
   * Initialize fret preferences for optimal chord fingering
   * @private
   */
  _initializeFretPreferences() {
    // Default preferences
    this.chordState.fretPreferences = {
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
    
    // Add 8-string support
    if (this.state.stringArray.includes('BbString')) {
      this.chordState.fretPreferences['Root Position'].BbString = [3, 5, 7];
      this.chordState.fretPreferences['Basic Position'].BbString = [3, 5, 7];
      this.chordState.fretPreferences['First Inversion'].BbString = [3, 5, 7];
      this.chordState.fretPreferences['Second Inversion'].BbString = [7, 9, 2];
      this.chordState.fretPreferences['Third Inversion'].BbString = [7, 9, 11];
    }
  }
  
  /**
   * Gets valid note ranges from voicing data
   * @returns {string[]} Array of valid note ranges
   * @private
   */
  _getValidNoteRanges() {
    if (!this.chordState.voicingData) return [];
    return Object.keys(this.chordState.voicingData)
      .filter(key => !['chord', 'type', 'root', 'note_range'].includes(key));
  }
  
  /**
   * Validate and normalize parameters against available data
   * @param {string} positionValue - The position value to validate
   * @param {string} rangeValue - The range value to validate
   * @returns {object} Object with validated position and range values
   * @private
   */
  _validateParameters(positionValue, rangeValue) {
    const validRanges = this._getValidNoteRanges();
    let validatedRange = rangeValue;
    let validatedPosition = positionValue;
    
    // Handle numeric position "0" - always map to Root Position
    if (validatedPosition === '0' || validatedPosition === 0) {
      this.log('Converting numeric position "0" to Root Position', 'debug');
      validatedPosition = 'Root Position';
    }
    
    // Handle "Root Position" vs "Basic Position" naming inconsistency
    if (validatedPosition === 'Root Position') {
      this.log('Converting Root Position to Basic Position for internal use', 'debug');
      validatedPosition = 'Basic Position';
    }
    
    // Validate range
    if (!validRanges.includes(validatedRange) && validRanges.length > 0) {
      this.log(`Invalid range ${validatedRange}, using ${validRanges[0]} instead`, 'warn');
      validatedRange = validRanges[0];
    }
    
    // Validate position for the given range
    if (this.chordState.voicingData[validatedRange]) {
      const validPositions = Object.keys(this.chordState.voicingData[validatedRange]);
      if (!validPositions.includes(validatedPosition) && validPositions.length > 0) {
        this.log(`Invalid position ${validatedPosition}, using ${validPositions[0]} instead`, 'warn');
        validatedPosition = validPositions[0];
      }
    }
    
    return { position: validatedPosition, range: validatedRange };
  }
  
  /**
   * Normalize V-System type names for consistency
   * @param {string} type - The chord type to normalize
   * @returns {string} Normalized chord type
   * @private
   */
  _normalizeVType(type) {
    if (!type) return '';
    
    // Ensure V-System notation is consistent
    const vSystemMatch = type.match(/^v[- ]?(\d+)$/i);
    if (vSystemMatch) {
      return `V${vSystemMatch[1]}`;
    }
    
    // Handle common chord quality normalizations
    const normalizations = {
      'M': 'Major',
      'Maj': 'Major',
      'm': 'Minor',
      'min': 'Minor',
      '7': 'Dominant 7',
      'dom7': 'Dominant 7',
      'M7': 'Major 7',
      'Maj7': 'Major 7',
      'm7': 'Minor 7',
      'min7': 'Minor 7'
    };
    
    return normalizations[type] || type;
  }
  
  /**
   * Update the chord display based on position and range
   * @param {string} position - The chord position/inversion
   * @param {string} range - The string range
   */
  updateChordDisplay(position, range) {
    this.performance.start('updateChordDisplay');
    
    console.log(`Updating chord display to position=${position}, range=${range}`);
    
    // Reset the fretboard
    this.resetFretboard();
    
    // Get tones for the chord
    this.getTonesFromDataChords(range, position);
    
    // Emit update event
    this.events.emit('chordUpdated', { position, range });
    
    this.performance.end('updateChordDisplay');
    return this;
  }
  
  /**
   * Get notes to display for a chord position
   * @param {string} range - Note range value
   * @param {string} position - Position value
   * @param {Object} options - Preferences for note selection
   */
  getTonesFromDataChords(range, position, options = {}) {
    this.performance.start('getTonesFromDataChords');
    
    console.log('==== getTonesFromDataChords DEBUG ====');
    console.log('Input parameters:', { 
      position, 
      range, 
      options 
    });
    console.log('Voicing data structure:', this.chordState.voicingData);
    
    // If no chord data, exit early
    if (!this.chordState.voicingData) {
      console.warn('No chord voicing data available');
      return this;
    }
    
    // IMPORTANT: Clear active notes to prevent accumulation
    this.state.activeNotes.clear();
    
    // Clear previous root markers before activating new notes
    this._clearAllRootMarkers();
    
    // IMPROVED DATA STRUCTURE HANDLING
    let positionData = null;
    
    // 1. Check if we have a flat structure with string data directly at root level
    const hasAssignedStrings = this.chordState.voicingData.hasOwnProperty('assigned_strings');
    const hasStringData = hasAssignedStrings && 
                         this.chordState.voicingData.assigned_strings && 
                         this.chordState.voicingData.assigned_strings.length > 0;
    
    console.log('Data structure analysis:', {
      hasAssignedStrings,
      hasStringData,
      voicingDataKeys: Object.keys(this.chordState.voicingData)
    });
    
    if (hasStringData) {
      // We have a flat structure
      positionData = this.chordState.voicingData;
      console.log('Using flat structure for position data');
    }
    // 2. Try nested structure with EXACT match for range and position
    else if (this.chordState.voicingData[range] && 
             this.chordState.voicingData[range][position]) {
      positionData = this.chordState.voicingData[range][position];
      console.log(`Found exact position match: range=${range}, position=${position}`);
    } 
    // 3. Try to find ANY position in the specified range
    else if (this.chordState.voicingData[range]) {
      console.log(`Position "${position}" not found in range "${range}", trying alternatives`);
      const availablePositions = Object.keys(this.chordState.voicingData[range]);
      console.log(`Available positions for range "${range}":`, availablePositions);
      
      if (availablePositions.length > 0) {
        // Default to first available position if specified position not found
        const fallbackPosition = availablePositions[0];
        positionData = this.chordState.voicingData[range][fallbackPosition];
        console.log(`Using fallback position "${fallbackPosition}" for range "${range}"`);
      }
    }
    // 4. Try to find the specified position in ANY range
    else {
      console.log('Range not found, searching all available ranges');
      
      // Filter out metadata fields to get just the range keys
      const metadataFields = ['chord', 'type', 'root', 'note_range'];
      const potentialRanges = Object.keys(this.chordState.voicingData)
        .filter(key => !metadataFields.includes(key));
      
      console.log('Potential ranges to search:', potentialRanges);
      
      // First try to find the requested position in any range
      for (const potentialRange of potentialRanges) {
        if (typeof this.chordState.voicingData[potentialRange] === 'object') {
          // Try to find the specified position in this range
          if (this.chordState.voicingData[potentialRange][position]) {
            positionData = this.chordState.voicingData[potentialRange][position];
            console.log(`Found position "${position}" in range "${potentialRange}"`);
            break;
          }
        }
      }
      
      // If still not found, use ANY position from ANY range
      if (!positionData) {
        console.log('Specified position not found in any range, using any available position');
        
        for (const potentialRange of potentialRanges) {
          if (typeof this.chordState.voicingData[potentialRange] === 'object') {
            const availablePositions = Object.keys(this.chordState.voicingData[potentialRange]);
            
            if (availablePositions.length > 0) {
              const fallbackPosition = availablePositions[0];
              positionData = this.chordState.voicingData[potentialRange][fallbackPosition];
              console.log(`Using fallback position "${fallbackPosition}" in range "${potentialRange}"`);
              break;
            }
          }
        }
      }
    }
    
    if (!positionData) {
      console.warn(`No position data found for range: ${range}, position: ${position}`);
      return this;
    }
    
    console.log('Position data found:', positionData);
    
    // Store active position data for other components
    window.activeChordPositionData = positionData;
    
    // Clear active frets for each string before adding new ones
    this.state.activeFrets.clear();
    
    // Activate notes for each string in the position data
    for (const stringName in positionData) {
      // Skip the assigned_strings array
      if (stringName === 'assigned_strings') {
        console.log(`[LoopDebug] Skipping '${stringName}'`);
        continue;
      }
      
      console.log(`Processing string: ${stringName}`);
      
      // Get the note data for this string
      const noteData = positionData[stringName];
      if (!noteData || !noteData.length) {
        console.log(`[LoopDebug] No note data for string ${stringName}, continuing.`);
        continue;
      }
      
      // Get the note name and function (e.g., "c", "R" for root)
      const noteName = noteData[0];
      const noteFunction = noteData[1] || '';
      
      console.log(`String ${stringName}: note=${noteName}, function=${noteFunction}`);
      
      if (!noteName) {
        console.log(`[LoopDebug] No note name for string ${stringName}, continuing.`);
        continue;
      }
      
      // IMPORTANT: Track active notes even if we can't find DOM elements
      if (!this.state.activeNotes.has(stringName)) {
        this.state.activeNotes.set(stringName, new Map());
      }
      this.state.activeNotes.get(stringName).set(noteName, {
        noteName,
        noteFunction,
        active: false // Will be set to true if DOM element is found
      });
      
      try {
        // Properly escape note name for CSS selector using the class method
        const escapedNote = this.escapeNoteForCss(noteName);
        const noteSelector = `.${stringName} .${escapedNote}`;
        
        console.log(`Looking for note with selector: "${noteSelector}"`);
        const noteElements = document.querySelectorAll(noteSelector);
        
        console.log(`Selector "${noteSelector}" matched ${noteElements.length} elements`);
        
        if (noteElements.length === 0) {
          console.warn(`No matching elements found for ${noteName} on ${stringName}`);
          // We continue because we've already added the note to activeNotes above
          continue;
        }
        
        // For multiple options on the same string, score each one and pick the best
        if (noteElements.length > 1) {
          console.log(`Multiple options (${noteElements.length}) found for ${noteName} on ${stringName}, scoring each`);
          
          // Score each element by its fret position
          const scoredElements = Array.from(noteElements).map(el => {
            const fretEl = el.closest('[class*="fret"]');
            const fretNum = this._getFretNumber(fretEl);
            
            // Get position-specific preferences
            const preferences = this._getPositionFretPreferences(position, this.chordState.chordType);
            
            // Score this position
            const score = this._scoreFretPosition(
              fretNum, stringName, position, preferences, this.chordState.chordType
            );
            
            console.log(`Option on fret ${fretNum} has score ${score}`);
            
            return { element: el, fretNum, score };
          });
          
          // Sort by score (lower is better) and pick the best one
          scoredElements.sort((a, b) => a.score - b.score);
          const bestNote = scoredElements[0];
          
          console.log(`Selected best note on fret ${bestNote.fretNum} with score ${bestNote.score}`);
          
          // Activate only the best note
          console.log(`[ActivationCheck] About to call _activateNote for BEST NOTE:`, { element: bestNote.element, noteName, noteFunction });
          this._activateNote(bestNote.element, noteName, noteFunction);
          
          // Store the active fret
          if (!this.state.activeFrets.has(stringName)) {
            this.state.activeFrets.set(stringName, new Set());
          }
          this.state.activeFrets.get(stringName).add(bestNote.fretNum);
        } 
        // If there's only one option, use it
        else {
          console.log(`Single option for ${noteName} on ${stringName}`);
          console.log(`[ActivationCheck] About to call _activateNote for SINGLE NOTE:`, { element: noteElements[0], noteName, noteFunction });
          this._activateNote(noteElements[0], noteName, noteFunction);
          
          // Store the active fret
          const fretEl = noteElements[0].closest('[class*="fret"]');
          const fretNum = this._getFretNumber(fretEl);
          console.log(`Activating fret ${fretNum} for ${stringName}`);
          
          if (!this.state.activeFrets.has(stringName)) {
            this.state.activeFrets.set(stringName, new Set());
          }
          this.state.activeFrets.get(stringName).add(fretNum);
        }
      } catch (error) {
        console.error(`Error caught processing note ${noteName} on string ${stringName}:`, error);
        // Continue to the next note - we've already tracked this one in activeNotes
      }
    }
    
    console.log('==== getTonesFromDataChords COMPLETE ====');
    console.log('Final active frets:', Object.fromEntries([...this.state.activeFrets.entries()].map(
      ([key, value]) => [key, [...value]]
    )));
    console.log('Active notes:', [...this.state.activeNotes.entries()].map(
      ([string, notes]) => `${string}: ${[...notes.entries()].map(([key, value]) => `${key}: ${value.noteName} (${value.noteFunction})`).join(', ')}`
    ));
    
    // Check for multiple root notes
    setTimeout(() => {
      console.log('[RootCheck] All elements with .root class after activation:');
      document.querySelectorAll('.root').forEach(el => {
        console.log(el, el.className, el.getAttribute('data-note-name'), el.getAttribute('data-is-root'));
      });
    }, 0);
    
    this.performance.end('getTonesFromDataChords');
    return this;
  }
  
  /**
   * Remove all root markers from the fretboard before activating new notes
   * Ensures only the current root is marked
   */
  _clearAllRootMarkers() {
    // Remove 'root' class and related attributes from all .tone images
    const rootImgs = document.querySelectorAll('img.tone.root');
    rootImgs.forEach(img => {
      img.classList.remove('root');
      if (img.getAttribute('src') === '/static/media/circle-root.svg') {
        img.setAttribute('src', '/static/media/circle.svg');
      }
      img.removeAttribute('data-is-root');
      img.removeAttribute('data-note-name');
      img.removeAttribute('data-note-class');
      img.removeAttribute('data-note-id');
      img.removeAttribute('data-canonical-name');
    });
    // Remove 'root' class from all .note elements (in case it was applied there)
    document.querySelectorAll('.note.root').forEach(note => {
      note.classList.remove('root');
      note.removeAttribute('data-is-root');
      note.removeAttribute('data-note-name');
      note.removeAttribute('data-note-class');
      note.removeAttribute('data-note-id');
      note.removeAttribute('data-canonical-name');
    });
  }
  
  /**
   * Activate a note for chord display
   * @param {HTMLElement} element - Note element to activate
   * @param {string} noteName - Name of the note
   * @param {string} noteFunction - Function of the note (R, 3, 5, etc.)
   * @private
   */
  _activateNote(element, noteName, noteFunction) {
    console.log('[NoteActivation] Activating note:', { 
      noteName, 
      noteFunction, 
      element,
      img: element.querySelector('img.tone')
    });

    // Activate the note element and set the active flag in our data structure
    element.classList.add('active');
    element.setAttribute('data-note-active', 'true');
    element.setAttribute('data-note-function', noteFunction || '');
    
    // Add to active notes map
    if (this.state.activeNotes.has(element.closest('[class*="String"]').className)) {
      const stringMap = this.state.activeNotes.get(element.closest('[class*="String"]').className);
      stringMap.set(noteName, {
        noteName, 
        noteFunction, 
        element,
        active: true
      });
    }

    // Find and activate the note name display
    const noteNameDiv = element.querySelector('.notename');
    if (noteNameDiv) {
      noteNameDiv.classList.add('active'); // Add 'active' class
      // Explicitly set styles to ensure visibility, overriding potential inline styles
      noteNameDiv.style.visibility = 'visible';
      noteNameDiv.style.opacity = '1';
      
      // Add note function to display if available
      if (noteFunction) {
        noteNameDiv.setAttribute('data-note-function', noteFunction);
      }
    } else {
      console.warn(`No .notename found for note ${noteName}`);
    }

    // Get the tone image
    const img = element.querySelector('img.tone');
    if (!img) {
      console.warn(`No img.tone found for note ${noteName}`);
      return;
    }
    
    // Activate the tone image and set attributes
    img.classList.add('active');
    img.setAttribute('data-note-name', noteName);
    img.setAttribute('data-note-function', noteFunction || '');
    
    // Get the fret element (parent of note element)
    const fretEl = element.closest('[class*="fret"]');
    if (fretEl) {
      console.log('[NoteActivation] fretElement:', { 
        fretElement: fretEl,
        classList: Array.from(fretEl.classList),
        fretNum: this._getFretNumber(fretEl),
        stringName: this._getStringNameFromElement(fretEl)
      });
      
      // Add active class to the fret
      fretEl.classList.add('active-fret');
    }
    
    // Special styling for root notes
    if (noteFunction === 'R') {
      // --- LOGGING: root note logic start ---
      console.log('[RootMarking] Attempting to mark root:', {noteName, element, img});
      const canonicalInfo = getCanonicalNoteInfo(noteName);
      let canonicalClass = canonicalInfo ? canonicalInfo.class : null;
      let canonicalId = canonicalInfo ? canonicalInfo.id : null;
      let canonicalName = canonicalInfo ? canonicalInfo.canonical : null;
      console.log('[RootMarking] canonicalInfo:', {noteName, canonicalInfo});
      
      if (!canonicalInfo) {
        console.warn('[RootMarking] No canonical mapping found for noteName:', noteName);
      }
      
      // Apply root styling to both the image and the note element
      img.classList.add('root');
      element.classList.add('root-note');
      
      // Use the root circle image
      img.setAttribute('src', '/static/media/circle-root.svg');
      
      // Set all root data attributes
      img.setAttribute('data-is-root', 'true');
      img.setAttribute('data-note-name', noteName);
      element.setAttribute('data-is-root', 'true');
      element.setAttribute('data-note-name', noteName);
      
      // Add canonical information if available
      if (canonicalClass) {
        img.setAttribute('data-note-class', canonicalClass);
        element.setAttribute('data-note-class', canonicalClass);
      }
      if (canonicalId) {
        img.setAttribute('data-note-id', canonicalId);
        element.setAttribute('data-note-id', canonicalId);
      }
      if (canonicalName) {
        img.setAttribute('data-canonical-name', canonicalName);
        element.setAttribute('data-canonical-name', canonicalName);
      }
    } else {
      // Ensure non-root notes have the proper image
      if (img.getAttribute('src').includes('circle-root.svg')) {
        img.setAttribute('src', '/static/media/circle.svg');
      }
    }
    
    // IMPORTANT: Force a repaint to ensure styles are applied
    void element.offsetWidth;
    
    // Add to active elements set for tracking
    this.activeElements.add(element);
  }
  
  /**
   * Helper to get string name from an element
   * @param {HTMLElement} element - Element to get string name from
   * @returns {string|null} String name or null if not found
   * @private
   */
  _getStringNameFromElement(element) {
    if (!element) return null;
    
    // Find class that ends with "String"
    const stringClass = Array.from(element.classList).find(cls => 
      cls.endsWith('String')
    );
    
    return stringClass || null;
  }
  
  /**
   * Get fret number from a fret element
   * @param {HTMLElement} fretEl - The fret element
   * @returns {number} The fret number (0-12), or -1 if not determined
   * @private
   */
  _getFretNumber(fretEl) {
    if (!fretEl) return -1;
    return getFretNumberFromClassList(fretEl.classList);
  }
  
  /**
   * Get fret preferences for each position and string
   * @param {string} position - The chord position/inversion
   * @param {string} chordType - The chord type (Major, Minor, etc.)
   * @returns {object} Object mapping strings to fret preferences
   * @private
   */
  _getPositionFretPreferences(position, chordType) {
    // Start with default preferences for this position
    const defaultPrefs = this.chordState.fretPreferences[position] || 
                         this.chordState.fretPreferences['Basic Position'];
    
    // Customize preferences for specific chord types
    if (chordType === 'Major' && 
        (position === 'Root Position' || position === 'Basic Position')) {
      // For major chords, prefer more open positions in root position
      return {
        ...defaultPrefs,
        eString: [0, 3, 7],  // Prefer open e string
        bString: [0, 3, 7],  // Prefer open b string
        EString: [0, 3, 7]   // Prefer open E string
      };
    } 
    // For minor chords, prefer certain fret positions
    else if (chordType === 'Minor' && 
            (position === 'Root Position' || position === 'Basic Position')) {
      return {
        ...defaultPrefs,
        gString: [3, 5, 7]   // Adjust g string preference
      };
    } 
    // For seventh chords, adjust for comfortable fingering
    else if (chordType && chordType.includes('7')) {
      if (position === 'First Inversion') {
        return {
          ...defaultPrefs,
          eString: [10, 8, 3]  // Strong preference for higher frets on e string
        };
      } else if (position === 'Second Inversion') {
        return {
          ...defaultPrefs,
          bString: [10, 8, 5]  // Strong preference for higher frets on b string
        };
      }
    }
    
    // Return default preferences if no special case matches
    return defaultPrefs;
  }
  
  /**
   * Score a fret position for optimal fingering
   * @param {number} fretNum - The fret number to score
   * @param {string} stringName - The string name (eString, bString, etc.)
   * @param {string} position - The chord position/inversion
   * @param {object} preferences - The fret preferences
   * @param {string} chordType - The chord type
   * @returns {number} Score (lower is better)
   * @private
   */
  _scoreFretPosition(fretNum, stringName, position, preferences, chordType) {
    // Basic validity check
    if (fretNum === -1) return Infinity;
    
    // Get position-specific preferences
    const positionPrefs = preferences || this.chordState.fretPreferences[position] || 
                         this.chordState.fretPreferences['Basic Position'] || {};
                         
    // Get the preferences for this string or use defaults
    const stringPrefs = positionPrefs[stringName] || [3, 5, 7];
    
    // Start with a high score (lower is better)
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
    if (chordType === 'Major' && 
        (position === 'Root Position' || position === 'Basic Position')) {
      if (stringName === 'eString' || stringName === 'EString' || stringName === 'bString') {
        score -= (fretNum === 0) ? 1 : 0; // Prefer open strings for shape chords
      }
    }
    
    // For Minor chords, prefer certain fret positions
    if (chordType === 'Minor') {
      if ((position === 'Root Position' || position === 'Basic Position') && 
          stringName === 'gString') {
        score -= (fretNum === 3) ? 1 : 0;
      }
    }
    
    // Penalize very high frets (12+) slightly 
    score += (fretNum > 12) ? 0.5 : 0;
    
    // Prefer more consistent fingering patterns (avoid extreme jumps between strings)
    if (fretNum > 7 && ['aString', 'EString'].includes(stringName)) {
      score += 0.5; // Penalize high frets on low strings
    }
    
    // Prefer positions that match the specified position type
    if (position === 'Basic Position' || position === 'Root Position') {
      // Prefer lower frets for basic positions
      score += (fretNum > 5) ? 0.3 * (fretNum - 5) : 0;
    } else if (position === 'First Inversion') {
      // For first inversion, prefer positions around frets 3-7
      score += (fretNum < 3 || fretNum > 7) ? 0.4 : 0;
    } else if (position === 'Second Inversion') {
      // For second inversion, prefer positions around frets 5-9
      score += (fretNum < 5 || fretNum > 9) ? 0.4 : 0;
    }
    
    return score;
  }
  
  /**
   * Helper function to escape special characters in CSS selectors
   * Specifically escapes '#' for use in class names.
   * @param {string} note - The note name (e.g., 'cs3', 'bb2')
   * @returns {string} Escaped note name suitable for CSS class selectors
   */
  escapeNoteForCss(note) {
    if (typeof note !== 'string') return '';
    // Only escape '#' as '\#'. Do not escape 'b'.
    return note.replace(/#/g, '\\#');
  }
}

// Utility: Normalize note name to canonical mapping (preserve original accidental)
function getCanonicalNoteInfo(noteName) {
  // Remove octave if present
  const match = noteName.match(/^([a-gA-G][b#]?)/);
  if (!match) return null;
  let base = match[1].toUpperCase().replace('S', '#');
  if (NOTE_CANONICAL_MAPPING[base]) {
    return { ...NOTE_CANONICAL_MAPPING[base], canonical: base };
  }
  // Only use enharmonic equivalents if the original is not present
  if (base.endsWith('B')) { // e.g., Db
    const sharp = base[0] + '#';
    if (NOTE_CANONICAL_MAPPING[sharp]) return { ...NOTE_CANONICAL_MAPPING[sharp], canonical: base };
  }
  if (base.endsWith('#')) { // e.g., C#
    const nextChar = String.fromCharCode(base.charCodeAt(0) + 1);
    const flat = nextChar + 'b';
    if (NOTE_CANONICAL_MAPPING[flat]) return { ...NOTE_CANONICAL_MAPPING[flat], canonical: base };
  }
  return null;
}

// Initialize the chord fretboard controller when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  if (typeof FretboardCore === 'undefined') {
    console.error('FretboardCore not found. Make sure fretboard-core.js is loaded first.');
    return;
  }
  
  const controller = new ChordFretboardController({
    debugMode: false,
    enableLogging: true
  });
  
  controller.init();
  
  // Make controller accessible globally for debugging
  window.chordFretboardController = controller;
});
