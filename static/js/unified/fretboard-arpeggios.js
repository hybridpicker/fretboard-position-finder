/**
 * Unified Fretboard Arpeggio Controller
 * 
 * Arpeggio-specific implementation for the unified fretboard controller.
 * This file builds on fretboard-core.js to provide arpeggio-specific functionality.
 * 
 * @author Cascade AI Assistant
 */

class ArpeggioFretboardController extends FretboardCore {
  constructor(options = {}) {
    // Call the parent constructor with merged options
    super({
      ...options,
      viewType: 'arpeggio'
    });
    
    // Arpeggio-specific state
    this.arpeggioState = {
      selectedArpeggio: null,
      positions: [],
      currentPosition: '0',
      arpeggioData: null,
      allPositionsMode: false,
      rootNote: null,
      arpeggioType: null
    };
  }
  
  /**
   * Initialize the arpeggio fretboard controller
   * @param {Object} options - Initialization options
   */
  init(options = {}) {
    // Call parent init
    super.init(options);
    this.log('Initializing arpeggio fretboard controller', 'info');
    
    // Set up arpeggio-specific handlers
    this._setupArpeggioUIEvents();
    
    // Load position data
    this._loadPositionData();
    
    return this;
  }
  
  /**
   * Set up event listeners specific to arpeggio view
   * @private
   */
  _setupArpeggioUIEvents() {
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
        this.changeArpeggioRoot(rootValue);
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
   * Load arpeggio position data and render the fretboard
   * @private
   */
  _loadPositionData() {
    // Get position from URL or default to '0'
    const posValue = this.getParameter('position_select', '0');
    
    // Check if we have the global arpeggio_data from Django view
    if (typeof arpeggio_data !== 'undefined') {
      this.arpeggioState.arpeggioData = arpeggio_data;
      this.log(`Arpeggio data loaded with ${Object.keys(arpeggio_data).length} positions`, 'info');
      
      // Extract arpeggio information
      if (arpeggio_data.root) {
        this.arpeggioState.rootNote = arpeggio_data.root;
      }
      
      if (arpeggio_data.arpeggio_type) {
        this.arpeggioState.arpeggioType = arpeggio_data.arpeggio_type;
      }
      
      // Set available positions
      this.arpeggioState.positions = Object.keys(arpeggio_data)
        .filter(key => !['root', 'arpeggio_type'].includes(key));
      
      // Render the fretboard
      this.updatePosition(posValue);
    } else {
      this.log('No arpeggio data available', 'error');
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
    this.arpeggioState.currentPosition = position;
    
    // Reset the fretboard
    this.resetFretboard();
    
    // Special handling for "All Positions"
    if (position === 'All Positions') {
      this.arpeggioState.allPositionsMode = true;
      this.activateAllPositionNotes();
    } else {
      this.arpeggioState.allPositionsMode = false;
      
      // Get tones for the position
      this.getTonesFromArpeggioData(position);
      
      // Handle edge case for low frets
      if (position === '0' || position === '1') {
        this.ensureLowFretNotesShown(position);
      }
    }
    
    // Update cursors
    this.updateCursorVisibility(position);
    
    // Avoid uncomfortable finger stretches
    this.avoidFourNotesOnString();
    
    // Emit position updated event
    this.events.emit('positionUpdated', position);
    
    this.performance.end('updatePosition');
    return this;
  }
  
  /**
   * Get tones from arpeggio data and activate them
   * @param {string} position - Position ID
   */
  getTonesFromArpeggioData(position) {
    this.performance.start('getTonesFromArpeggioData');
    
    if (!this.arpeggioState.arpeggioData || !this.arpeggioState.arpeggioData[position]) {
      this.log(`No data for position ${position}`, 'error');
      this.performance.end('getTonesFromArpeggioData');
      return;
    }
    
    // Track the tones we need to process for multiple_notes
    const tonesToProcess = new Set();
    
    // Activate notes for each string in this position
    const positionData = this.arpeggioState.arpeggioData[position];
    for (const stringName in positionData) {
      if (!positionData.hasOwnProperty(stringName) || stringName === 'root' || stringName === 'arpeggio_type') continue;
      
      const stringData = positionData[stringName][0];
      if (!stringData.tones) continue;
      
      // Activate each tone for this string
      for (const tone of stringData.tones) {
        // Skip empty tones
        if (!tone) continue;
        
        // Add to tones to process
        tonesToProcess.add(tone);
        
        // Select the note elements for this tone
        const elements = document.querySelectorAll(`.${tone}`);
        
        for (const element of elements) {
          // Get the containing string
          const stringEl = element.closest(`[class*="${stringName}"]`);
          if (!stringEl) continue;
          
          // Activate the note
          element.classList.add('active');
          
          // Activate the tone image
          const img = element.querySelector('img.tone');
          if (img) {
            img.classList.add('active');
            
            // Check if root note
            if (stringData.root_note && stringData.root_note.includes(tone)) {
              img.classList.add('root');
              img.setAttribute('src', '/static/media/svg/root_note.svg');
            }
          }
          
          // Add to active frets map
          const fretEl = element.closest('[class*="fret"]');
          if (fretEl) {
            const fretNum = parseInt(Array.from(fretEl.classList)
              .find(cls => cls.startsWith('fret'))
              ?.replace('fret', '') || '0');
            
            if (!this.state.activeFrets.has(stringName)) {
              this.state.activeFrets.set(stringName, new Set());
            }
            this.state.activeFrets.get(stringName).add(fretNum);
          }
        }
      }
    }
    
    // Process multiple notes after all tones are activated
    for (const tone of tonesToProcess) {
      this.optimizeMultipleNotes(tone, position);
    }
    
    this.performance.end('getTonesFromArpeggioData');
    return this;
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
      const stringEl = element.closest('[class*="String"]');
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
    
    // If we have arpeggio data for this position, use it to determine priority strings
    if (position && this.arpeggioState.arpeggioData && this.arpeggioState.arpeggioData[position]) {
      Object.keys(this.arpeggioState.arpeggioData[position])
        .filter(key => key !== 'root' && key !== 'arpeggio_type')
        .forEach(key => {
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
      const string = document.querySelector(`.${stringName}`);
      if (!string) return;
      
      const activeNotes = Array.from(string.querySelectorAll('.note.active'))
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
    for (const position in this.arpeggioState.arpeggioData) {
      if (!this.arpeggioState.arpeggioData.hasOwnProperty(position) || 
          position === 'All Positions' || 
          position === 'root' || 
          position === 'arpeggio_type') {
        continue;
      }
      
      const positionData = this.arpeggioState.arpeggioData[position];
      
      // Process each string in this position
      for (const stringName in positionData) {
        if (!positionData.hasOwnProperty(stringName) || 
            stringName === 'root' || 
            stringName === 'arpeggio_type') continue;
        
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
            
            const fretMatch = Array.from(fretEl.classList)
              .find(cls => cls.startsWith('fret'));
            if (!fretMatch) continue;
            
            const fretNum = parseInt(fretMatch.replace('fret', ''));
            
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
                img.style.opacity = '1';
                
                // If root note, show root marker
                if (stringData.root_note && stringData.root_note.includes(tone)) {
                  img.classList.add('root');
                  img.setAttribute('src', '/static/media/svg/root_note.svg');
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
    const positionData = this.arpeggioState.arpeggioData[position];
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
      const positions = this.arpeggioState.positions;
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
    const positions = this.arpeggioState.positions;
    const currentPosition = this.arpeggioState.currentPosition;
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
   * Change the arpeggio root note
   * @param {string} newRoot - New root note
   */
  changeArpeggioRoot(newRoot) {
    // This would require a server-side call or page reload
    // since arpeggio data is rendered by Django
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set('root_note', newRoot);
    window.location.href = currentUrl.toString();
  }
}

// Initialize the arpeggio fretboard controller when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  if (typeof FretboardCore === 'undefined') {
    console.error('FretboardCore not found. Make sure fretboard-core.js is loaded first.');
    return;
  }
  
  const controller = new ArpeggioFretboardController({
    debugMode: false,
    enableLogging: true
  });
  
  controller.init();
  
  // Make controller accessible globally for debugging
  window.arpeggioFretboardController = controller;
});
