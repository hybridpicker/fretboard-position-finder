/**
 * Unified Fretboard Scale Controller
 * 
 * Scale-specific implementation for the unified fretboard controller.
 * This file builds on fretboard-core.js to provide scale-specific functionality.
 * 
 * @author Cascade AI Assistant
 */

class ScaleFretboardController extends FretboardCore {
  constructor(options = {}) {
    // Call the parent constructor with merged options
    super({
      ...options,
      viewType: 'scale'
    });
    
    // Scale-specific state
    this.scaleState = {
      selectedScale: null,
      positions: [],
      currentPosition: '0',
      scaleData: null,
      allPositionsMode: false,
      lowFretIndicators: false
    };
  }
  
  /**
   * Initialize the scale fretboard controller
   * @param {Object} options - Initialization options
   */
  init(options = {}) {
    // Call parent init
    super.init(options);
    this.log('Initializing scale fretboard controller', 'info');
    
    // Debug the scale data globally
    console.log('SCALE DEBUG: Checking for global scale_data');
    if (typeof scale_data !== 'undefined') {
      console.log('SCALE DEBUG: Found global scale_data:', scale_data);
    } else {
      this.log('No scale data available', 'error');
      console.error('SCALE DEBUG: No scale data available for rendering');
      
      // Check what other data might be available
      if (typeof chord_data !== 'undefined') {
        console.log('SCALE DEBUG: Found chord_data instead of scale_data');
      }
      if (typeof window.scale_data !== 'undefined') {
        console.log('SCALE DEBUG: Found scale_data as window property instead of global var');
      }
    }
    
    // Set up scale-specific handlers
    this._setupScaleUIEvents();
    
    // Load position data
    this._loadPositionData();
    
    return this;
  }
  
  /**
   * Set up event listeners specific to scale view
   * @private
   */
  _setupScaleUIEvents() {
    // Set up position select handler
    document.addEventListener('change', (event) => {
      if (event.target.id === 'position_select') {
        const positionValue = event.target.value;
        this.updatePosition(positionValue);
      }
    });
    
    // Handle root note changes
    const rootSelectors = document.querySelectorAll('.sfbsfnos .slitli');
    rootSelectors.forEach(item => {
      item.addEventListener('click', () => {
        const rootValue = item.getAttribute('data-value') || item.textContent.trim();
        this.changeScaleRoot(rootValue);
      });
    });
    
    // Handle keyboard events for navigation
    document.addEventListener('keydown', (event) => {
      // Arrow keys for navigation
      if (event.key === 'ArrowRight') {
        this.moveToNextPosition();
      }
    });
    
    // Custom UI element handlers
    this._initializeNavigationCursors();
  }
  
  /**
   * Initialize the navigation cursor elements
   * @private
   */
  _initializeNavigationCursors() {
    const rightCursor = document.querySelector('.right-cursor');
    if (rightCursor) {
      rightCursor.addEventListener('click', () => this.moveToNextPosition());
      rightCursor.style.visibility = 'visible';
      rightCursor.style.opacity = '1';
    }
  }
  
  /**
   * Load scale position data and render the fretboard
   * @private
   */
  _loadPositionData() {
    this.performance.start('loadPositionData');
    
    // Get position value from URL or form
    const posValue = this.getParameter('position', '0');
    console.log('SCALE DEBUG: Loading position data for position:', posValue);
    
    // Check if we have the global scale_data from Django view
    if (typeof scale_data !== 'undefined') {
      this.scaleState.scaleData = scale_data;
      this.log(`Scale data loaded with ${Object.keys(scale_data).length} positions`, 'info');
      console.log('SCALE DEBUG: Scale data loaded with positions:', Object.keys(scale_data));
      
      // Set available positions
      this.scaleState.positions = Object.keys(scale_data);
      
      // Render the fretboard
      this.updatePosition(posValue);
    } else {
      this.log('No scale data available', 'error');
      console.error('SCALE DEBUG: No scale data available for rendering');
      
      // Check what other data might be available
      if (typeof chord_data !== 'undefined') {
        console.log('SCALE DEBUG: Found chord_data instead of scale_data');
      }
      if (typeof window.scale_data !== 'undefined') {
        console.log('SCALE DEBUG: Found scale_data as window property instead of global var');
      }
    }
  }
  
  /**
   * Update the fretboard based on a position
   * @param {string} position - Position ID
   */
  updatePosition(position) {
    this.performance.start('updatePosition');
    this.log(`Updating to position: ${position}`, 'info');
    
    // Store the current position
    this.scaleState.currentPosition = position;
    
    // Reset the fretboard
    this.resetFretboard();
    
    // Special handling for "All Positions"
    if (position === 'All Positions') {
      this.scaleState.allPositionsMode = true;
      this.activateAllPositionNotes();
    } else {
      this.scaleState.allPositionsMode = false;
      
      // Get tones for the position
      this.getTonesFromScaleData(position);
      
      // Handle edge case for low frets
      if (position === '0' || position === '1') {
        this.scaleState.lowFretIndicators = true;
        this.ensureLowFretNotesShown(position);
      } else {
        this.scaleState.lowFretIndicators = false;
      }
    }
    
    // Update cursors
    this.updateCursorVisibility(position);
    
    // Avoid more than 3 notes per string to prevent stretching
    this.avoidFourNotesOnString();
    
    // Emit position updated event
    this.events.emit('positionUpdated', position);
    
    this.performance.end('updatePosition');
    return this;
  }
  
  /**
   * Get tones from scale data and activate them
   * @param {string} position - Position ID
   */
  getTonesFromScaleData(position) {
    this.performance.start('getTonesFromScaleData');
    console.log('SCALE DEBUG: Getting tones for position:', position);
    
    if (!this.scaleState.scaleData || !this.scaleState.scaleData[position]) {
      this.log(`No data for position ${position}`, 'error');
      console.error(`SCALE DEBUG: No scale data for position ${position}`);
      console.log('SCALE DEBUG: Available positions:', this.scaleState.scaleData ? Object.keys(this.scaleState.scaleData) : 'None');
      this.performance.end('getTonesFromScaleData');
      return;
    }
    
    console.log(`SCALE DEBUG: Found position data for ${position}:`, this.scaleState.scaleData[position]);
    
    // Track the tones we need to process for multiple_notes
    const tonesToProcess = new Set();
    
    // Activate notes for each string in this position
    const positionData = this.scaleState.scaleData[position];
    for (const stringName in positionData) {
      if (!positionData.hasOwnProperty(stringName)) continue;
      
      const stringData = positionData[stringName][0];
      if (!stringData.tones) {
        console.log(`SCALE DEBUG: No tones found for string ${stringName}`);
        continue;
      }
      
      console.log(`SCALE DEBUG: Processing string ${stringName} with tones:`, stringData.tones);
      
      // Activate each tone for this string
      for (const tone of stringData.tones) {
        // Skip empty tones
        if (!tone) continue;
        
        // Add to tones to process
        tonesToProcess.add(tone);
        
        // Select the main note container elements for this tone
        const escapedTone = this.escapeNoteForCss(tone); // Use the helper method
        const noteSelector = `.${stringName} .note.${escapedTone}`;
        const noteElements = document.querySelectorAll(noteSelector);

        console.log(`Found ${noteElements.length} elements for tone ${tone}`);
 
        noteElements.forEach(noteElement => {
          console.log(`Activating note element:`, noteElement);
          noteElement.classList.add('active');
          noteElement.style.visibility = 'visible';
          console.log(`SCALE DEBUG: Activated note container:`, noteElement);

          // Activate the tone image within the container
          const img = noteElement.querySelector('img.tone');
          if (img) {
            img.classList.add('active');
            console.log(`SCALE DEBUG: Activated tone image:`, img);

            // Check if root note
            if (stringData.root_note && stringData.root_note.includes(tone)) {
              img.classList.add('root');
              img.setAttribute('src', '/static/media/circle-root.svg');
              console.log(`SCALE DEBUG: Marked ${tone} as root note`);
            }
          }

          // Explicitly activate the notename div
          const noteNameDiv = noteElement.querySelector(`.notename.${escapedTone}`);
          if (noteNameDiv) {
            console.log(`Found notename div:`, noteNameDiv);
            noteNameDiv.classList.add('show-name'); 
            noteNameDiv.style.visibility = 'visible'; // Override inline styles
            noteNameDiv.style.opacity = '1'; // Override inline styles

            // Optionally, adjust text color if it's a root note
            if (stringData.root_note && stringData.root_note.includes(tone)) {
              noteNameDiv.style.color = 'var(--root-note-color)';
            }
          } else {
            console.log(`SCALE DEBUG: Note name div not found for element:`, noteElement);
          }

          // Add to active frets map (using noteElement which is the container)
          const fretEl = noteElement.closest('[class*="fret"]');
          if (fretEl) {
            const fretNum = parseInt(Array.from(fretEl.classList)
              .find(cls => cls.startsWith('fret'))
              ?.replace('fret', '') || '0');

            if (!this.state.activeFrets.has(stringName)) {
              this.state.activeFrets.set(stringName, new Set());
            }
            this.state.activeFrets.get(stringName).add(fretNum);
          }
        });
      }
    }
    
    console.log(`SCALE DEBUG: Processed tones:`, [...tonesToProcess]);
    
    // Process multiple notes after all tones are activated
    for (const tone of tonesToProcess) {
      this.optimizeMultipleNotes(tone, position);
    }
    
    this.performance.end('getTonesFromScaleData');
    return this;
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
  
  /**
   * Optimize multiple instances of the same note
   * @param {string} tone - Tone name
   * @param {string} position - Position ID
   */
  optimizeMultipleNotes(tone, position) {
    const elements = document.querySelectorAll(`.${tone}.active`);
    if (elements.length <= 2) return; // No optimization needed
    
    this.performance.start('optimizeMultipleNotes');
    
    // Create a map of which strings have this tone active
    const stringWithTones = {};
    
    // Collect string and fret information
    for (const element of elements) {
      const stringEl = element.closest(`[class*="String"]`);
      if (!stringEl) continue;
      
      const stringName = Array.from(stringEl.classList)
        .find(cls => cls.endsWith('String'));
      if (!stringName) continue;
      
      if (!stringWithTones[stringName]) {
        stringWithTones[stringName] = [];
      }
      
      const fretEl = element.closest('[class*="fret"]');
      if (fretEl) {
        const fretNumber = Array.from(fretEl.classList)
          .find(cls => cls.startsWith('fret'))
          ?.replace('fret', '') || '';
        
        stringWithTones[stringName].push(fretNumber);
      }
    }
    
    // Determine which strings to keep notes on
    const stringsToKeep = new Set();
    
    // If we have scale data for this position, use it to determine priority strings
    if (position && this.scaleState.scaleData && this.scaleState.scaleData[position]) {
      Object.keys(this.scaleState.scaleData[position]).forEach(key => {
        stringsToKeep.add(key);
      });
    }
    
    // First pass: deactivate notes on strings not in the position data
    for (const stringName of Object.keys(stringWithTones)) {
      if (!stringsToKeep.has(stringName)) {
        this.deactivateNotesOnString(stringName, tone);
      }
    }
    
    // Second pass: if we still have too many active notes, optimize further
    const remainingElements = document.querySelectorAll(`.${tone}.active`);
    if (remainingElements.length > 2) {
      // Use the core optimization function
      this.optimizeActiveNotes(remainingElements, 2);
    }
    
    this.performance.end('optimizeMultipleNotes');
  }
  
  /**
   * Deactivate notes on a specific string
   * @param {string} stringName - String name
   * @param {string} tone - Tone name
   */
  deactivateNotesOnString(stringName, tone) {
    const stringSelector = `.${stringName}`;
    const string = document.querySelector(stringSelector);
    
    if (string) {
      const notesOnString = string.querySelectorAll(`.${tone}.active`);
      notesOnString.forEach(note => {
        note.classList.remove('active');
        
        // Find the associated image
        const img = note.querySelector('img.tone');
        if (img) {
          img.classList.remove('active', 'root');
          img.style.opacity = '';
        }
      });
    }
  }
  
  /**
   * Avoid having four consecutive notes on a string
   * (prevents uncomfortable stretches)
   */
  avoidFourNotesOnString() {
    this.performance.start('avoidFourNotesOnString');
    
    this.state.stringArray.forEach(stringName => {
      const stringElement = document.querySelector(`.${stringName}`);
      if (!stringElement) return;
      
      const activeNotes = Array.from(stringElement.querySelectorAll('.note.active'))
        .map(note => {
          const fretEl = note.closest('[class*="fret"]');
          if (!fretEl) return null;
          
          const fretMatch = Array.from(fretEl.classList)
            .find(cls => cls.startsWith('fret'));
          if (!fretMatch) return null;
          
          const fretNum = parseInt(fretMatch.replace('fret', ''));
          return { note, fretNum };
        })
        .filter(item => item !== null)
        .sort((a, b) => a.fretNum - b.fretNum);
      
      // Look for 4 consecutive frets
      for (let i = 0; i < activeNotes.length - 3; i++) {
        if (activeNotes[i+3].fretNum - activeNotes[i].fretNum === 3) {
          // Found 4 consecutive frets, remove the 2nd note (index i+1)
          const noteToRemove = activeNotes[i+1].note;
          noteToRemove.classList.remove('active');
          
          const img = noteToRemove.querySelector('img.tone');
          if (img) {
            img.classList.remove('active', 'root');
            img.style.opacity = '';
          }
          
          break; // Only remove one to avoid breaking the pattern
        }
      }
    });
    
    this.performance.end('avoidFourNotesOnString');
  }
  
  /**
   * Special handling for "All Positions" mode
   */
  activateAllPositionNotes() {
    this.performance.start('activateAllPositionNotes');
    this.log('Activating all position notes', 'info');
    
    // Define priority patterns for different strings
    const priorityMap = {
      eString: [0, 3, 5, 7, 8, 10, 12],
      bString: [0, 3, 5, 7, 8, 10, 12],
      gString: [0, 2, 4, 5, 7, 9, 12],
      dString: [0, 2, 4, 5, 7, 9, 12],
      aString: [0, 2, 4, 5, 7, 9, 12],
      EString: [0, 3, 5, 7, 8, 10, 12],
      BbString: [0, 3, 5, 7, 8, 10, 12]
    };
    
    // Track all tones to process
    const allTones = new Set();
    
    // Loop through all positions to collect notes
    for (const position in this.scaleState.scaleData) {
      if (!this.scaleState.scaleData.hasOwnProperty(position) || position === 'All Positions') {
        continue;
      }
      
      const positionData = this.scaleState.scaleData[position];
      
      // Process each string in this position
      for (const stringName in positionData) {
        if (!positionData.hasOwnProperty(stringName)) continue;
        
        const stringData = positionData[stringName][0];
        if (!stringData.tones) continue;
        
        // Process each tone for this string
        for (const tone of stringData.tones) {
          if (!tone) continue;
          
          allTones.add(tone);
          
          // Find all elements for this tone
          const elements = document.querySelectorAll(`.${tone}`);
          
          // Process each element
          for (const element of elements) {
            // Get string and fret
            const stringEl = element.closest(`[class*="String"]`);
            if (!stringEl) continue;
            
            const currentStringName = Array.from(stringEl.classList)
              .find(cls => cls.endsWith('String'));
            if (!currentStringName) continue;
            
            const fretEl = element.closest('[class*="fret"]');
            if (!fretEl) continue;
            
            const fretNum = parseInt(fretEl.classList.find(cls => cls.startsWith('fret')).replace('fret', ''));
            
            // Check if this note is in priority frets for this string
            const isPriority = priorityMap[currentStringName] && 
                              priorityMap[currentStringName].includes(fretNum);
            
            // Mark as an all-positions note
            element.classList.add('all-positions-note');
            
            // If it's a priority note or a root note, make it fully active
            if (isPriority || (stringData.root_note && stringData.root_note.includes(tone))) {
              element.classList.add('active');
              
              const img = element.querySelector('img.tone');
              if (img) {
                img.classList.add('active');
                img.style.visibility = 'visible';
                img.style.opacity = '1';
                
                // If root note, show root marker
                if (stringData.root_note && stringData.root_note.includes(tone)) {
                  img.classList.add('root');
                  img.setAttribute('src', '/static/media/circle-root.svg');
                }
              }
            } 
            // Otherwise show as a dimmed note
            else {
              const img = element.querySelector('img.tone');
              if (img) {
                img.style.opacity = '0.4';
              }
            }
            
            // Find and show the note name
            const noteName = element.querySelector('.notename');
            if (noteName) {
              noteName.style.visibility = 'visible';
              noteName.style.opacity = '1';
            }
          }
        }
      }
    }
    
    // Remove duplicate notes in "All Positions" mode
    for (const tone of allTones) {
      this.optimizeMultipleNotes(tone, 'All Positions');
    }
    
    this.performance.end('activateAllPositionNotes');
  }
  
  /**
   * Ensure notes are visible on low frets (positions 0 and 1)
   * @param {string} position - Position ID
   */
  ensureLowFretNotesShown(position) {
    this.performance.start('ensureLowFretNotesShown');
    
    // Get priority frets for low positions
    const lowFretPriority = {
      '0': [0, 1, 2, 3],
      '1': [0, 1, 2, 3, 4, 5]
    };
    
    const priorityFrets = lowFretPriority[position] || [0, 1, 2, 3];
    
    // Process each string
    this.state.stringArray.forEach(stringName => {
      const stringElement = document.querySelector(`.${stringName}`);
      if (!stringElement) return;
      
      // Track notes by fret for this string
      const notesOnFret = {};
      
      // Collect all notes on priority frets
      priorityFrets.forEach(fret => {
        const selector = `.${stringName} .fret${fret} .note`;
        const notes = document.querySelectorAll(selector);
        
        if (notes.length > 0) {
          notesOnFret[fret] = Array.from(notes);
        }
      });
      
      // Process each fret
      for (const fret in notesOnFret) {
        if (!notesOnFret.hasOwnProperty(fret)) continue;
        
        const fretNum = parseInt(fret);
        this.processNotesOnFret(notesOnFret[fret], stringName, fretNum, position, true);
      }
    });
    
    // Fix all note names that might be hidden (across ALL frets and strings)
    const allNoteNames = document.querySelectorAll('.notename');
    allNoteNames.forEach(noteName => {
      // Make all note names visible
      noteName.style.visibility = 'visible';
      noteName.style.opacity = '1';
    });
    
    // Ensure all notes in C Major scale are visible
    if (this.scaleState.scaleData && this.scaleState.scaleData[position]) {
      const positionData = this.scaleState.scaleData[position];
      
      // Check each string in the position data
      for (const stringName in positionData) {
        if (!positionData.hasOwnProperty(stringName)) continue;
        
        const stringData = positionData[stringName][0];
        if (!stringData.tones) continue;
        
        // Process each tone in this string
        for (const tone of stringData.tones) {
          if (!tone) continue;
          
          // Find all elements for this tone on this string
          const elements = document.querySelectorAll(`.${stringName} .${tone}`);
          
          // Make sure they're visible
          elements.forEach(element => {
            // Add active class
            element.classList.add('active');
            
            // Make the element visible
            element.style.visibility = 'visible';
            element.style.opacity = '1';
            
            // Find the img element
            const img = element.querySelector('img.tone');
            if (img) {
              img.classList.add('active');
              img.style.visibility = 'visible';
              img.style.opacity = '1';
              
              // Check if it's a root note
              if (stringData.root_note && stringData.root_note.includes(tone)) {
                img.classList.add('root');
                img.setAttribute('src', '/static/media/circle-root.svg');
              }
            }
            
            // Find and show the note name
            const noteName = element.querySelector('.notename');
            if (noteName) {
              noteName.style.visibility = 'visible';
              noteName.style.opacity = '1';
            }
          });
        }
      }
    }
    
    this.performance.end('ensureLowFretNotesShown');
  }
  
  /**
   * Process notes on a specific fret
   * @param {Array<HTMLElement>} notes - Notes on the fret
   * @param {string} stringName - String name
   * @param {number} fretNum - Fret number
   * @param {string} position - Position ID
   * @param {boolean} isPriority - Whether these notes are priority
   */
  processNotesOnFret(notes, stringName, fretNum, position, isPriority) {
    // Get position data if available
    const positionData = this.scaleState.scaleData[position];
    const inPositionData = positionData && positionData[stringName];
    
    // Process each note on this fret
    notes.forEach(note => {
      // Get tone classes
      const toneClasses = Array.from(note.classList)
        .filter(cls => cls !== 'note' && cls !== 'active' && !cls.includes('String'));
      
      // Skip if no valid tone
      if (toneClasses.length === 0) return;
      
      const tone = toneClasses[0];
      
      // If in position data, activate normally
      if (inPositionData && positionData[stringName][0].tones.includes(tone)) {
        // This note is already activated by the normal position rendering
        return;
      }
      
      // For low fret indicators only:
      if (isPriority) {
        // Mark it as a low fret note
        note.classList.add('low-fret-note');
        
        // If it's in the first 3 frets, make it visible even if not in position
        if (fretNum <= 3) {
          // Show with reduced opacity
          const img = note.querySelector('img.tone');
          if (img) {
            img.style.opacity = '0.5';
          }
        }
      }
    });
  }
  
  /**
   * Update navigation cursor visibility
   * @param {string} position - Current position
   */
  updateCursorVisibility(position) {
    // Hide left cursor as a design choice
    const leftCursor = document.querySelector('.left-cursor');
    if (leftCursor) {
      leftCursor.style.display = 'none';
    }
    
    // Only show right cursor if there are more positions
    const rightCursor = document.querySelector('.right-cursor');
    if (rightCursor) {
      const positions = this.scaleState.positions;
      const currentIndex = positions.indexOf(position);
      const hasNext = currentIndex < positions.length - 1;
      
      rightCursor.style.visibility = hasNext ? 'visible' : 'hidden';
      rightCursor.style.opacity = hasNext ? '1' : '0';
    }
  }
  
  /**
   * Move to the next position
   */
  moveToNextPosition() {
    const positions = this.scaleState.positions;
    const currentPosition = this.scaleState.currentPosition;
    const currentIndex = positions.indexOf(currentPosition);
    
    if (currentIndex < positions.length - 1) {
      const nextPosition = positions[currentIndex + 1];
      this.updatePosition(nextPosition);
      
      // Update select element
      const positionSelect = document.getElementById('position_select');
      if (positionSelect) {
        positionSelect.value = nextPosition;
      }
    }
  }
  
  /**
   * Change the scale root note
   * @param {string} newRoot - New root note
   */
  changeScaleRoot(newRoot) {
    // This would require a server-side call or page reload
    // since scale data is rendered by Django
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set('root_note', newRoot);
    window.location.href = currentUrl.toString();
  }
}

// Initialize the scale fretboard controller when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  if (typeof FretboardCore === 'undefined') {
    console.error('FretboardCore not found. Make sure fretboard-core.js is loaded first.');
    return;
  }
  
  const controller = new ScaleFretboardController({
    debugMode: false,
    enableLogging: true
  });
  
  controller.init();
  
  // Make controller accessible globally for debugging
  window.scaleFretboardController = controller;
});
