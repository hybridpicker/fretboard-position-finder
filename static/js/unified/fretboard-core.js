/**
 * Unified Fretboard Core
 * 
 * Core functionality that powers all fretboard views (scales, arpeggios, chords)
 * This module handles the shared logic and avoids code duplication.
 * 
 * @author Cascade AI Assistant
 */

class FretboardCore {
  constructor(options = {}) {
    // Configuration
    this.config = {
      debugMode: options.debugMode || false,
      enableLogging: options.enableLogging || false,
      performanceMonitoring: options.performanceMonitoring || false,
      viewType: options.viewType || 'scale', // 'scale', 'arpeggio', or 'chord'
      isMobile: /Mobi|Android/i.test(navigator.userAgent),
      suppressEvents: false
    };
    
    // Initialize state
    this.state = {
      initialized: false,
      rootNote: null,
      position: null,
      stringRange: null,
      activeFrets: new Map(), // Map of string → active frets
      activeNotes: new Map(), // Changed from Set to Map
      dataLoaded: false,
      dataSource: null,
      stringArray: window.string_array || ['eString', 'bString', 'gString', 'dString', 'aString', 'EString', 'BbString']
    };
    
    // Performance monitoring
    this.performance = {
      enabled: this.config.performanceMonitoring,
      measures: {},
      start: (operation) => {
        if (!this.performance.enabled) return;
        this.performance.measures[operation] = performance.now();
      },
      end: (operation) => {
        if (!this.performance.enabled || !this.performance.measures[operation]) return 0;
        const duration = performance.now() - this.performance.measures[operation];
        this.log(`[Performance] ${operation}: ${duration.toFixed(2)}ms`, 'debug');
        delete this.performance.measures[operation];
        return duration;
      }
    };
    
    // Create event emitter
    this.events = {
      listeners: {},
      on: (event, callback) => {
        if (!this.events.listeners[event]) {
          this.events.listeners[event] = [];
        }
        this.events.listeners[event].push(callback);
      },
      off: (event, callback) => {
        if (!this.events.listeners[event]) return;
        this.events.listeners[event] = this.events.listeners[event]
          .filter(cb => cb !== callback);
      },
      emit: (event, ...args) => {
        if (this.config.suppressEvents) return;
        
        if (!this.events.listeners[event]) return;
        this.events.listeners[event].forEach(callback => {
          try {
            callback(...args);
          } catch(e) {
            this.log(`Error in event listener for ${event}: ${e}`, 'error');
          }
        });
      }
    };
  }
  
  /**
   * Initialize the fretboard
   * @param {Object} options - Initialization options
   */
  init(options = {}) {
    this.performance.start('init');
    this.log('Initializing fretboard core', 'info');
    
    // Update state with provided options
    Object.assign(this.state, options);
    
    // Register DOM event listeners
    this._registerEventListeners();
    
    // Mark as initialized
    this.state.initialized = true;
    this.events.emit('initialized', this.state);
    
    this.performance.end('init');
    return this;
  }
  
  /**
   * Reset the fretboard to its initial state
   */
  resetFretboard() {
    this.performance.start('resetFretboard');
    this.log('Resetting fretboard', 'info');
    
    // Reset internal state
    this.state.activeFrets = new Map();
    this.state.activeNotes = new Map();
    
    // Reset DOM elements
    this._resetDOMElements();
    
    this.events.emit('fretboardReset');
    this.performance.end('resetFretboard');
    return this;
  }
  
  /**
   * Reset DOM elements for the fretboard
   * @private
   */
  _resetDOMElements() {
    // Reset all active tones
    const images = document.querySelectorAll('img.tone');
    images.forEach(image => {
      // Get the note element
      const noteElement = image.closest('.note');
      if (noteElement) {
        // Get the tone name from class
        const toneNames = Array.from(noteElement.classList)
          .filter(cls => cls !== 'note' && cls !== 'active');
        
        if (toneNames.length > 0) {
          const toneName = toneNames[0];
          const octaveMatch = toneName.match(/[a-z]+([0-4])/);
          
          // Set appropriate SVG based on octave
          if (octaveMatch && octaveMatch[1]) {
            const octave = parseInt(octaveMatch[1]);
            let svgSrc = '/static/media/';
            
            switch (octave) {
              case 0: svgSrc += 'circle_01.svg'; break;
              case 1: svgSrc += 'circle_01.svg'; break;
              case 2: svgSrc += 'circle_02.svg'; break;
              case 3: svgSrc += 'circle_03.svg'; break;
              case 4: svgSrc += 'circle_04.svg'; break;
              default: svgSrc += 'circle_01.svg';
            }
            
            image.setAttribute('src', svgSrc);
          } else {
            image.setAttribute('src', '/static/media/circle_01.svg');
          }
        } else {
          image.setAttribute('src', '/static/media/circle_01.svg');
        }
      } else {
        image.setAttribute('src', '/static/media/circle_01.svg');
      }
      
      // Remove all classes and inline styles
      image.classList.remove('active', 'root', 'all-positions-note', 'low-fret-note');
      image.style.opacity = '';
      image.style.border = '';
      image.style.boxShadow = '';
    });
    
    // Reset all active notes
    const notes = document.querySelectorAll('.note');
    notes.forEach(note => {
      note.classList.remove(
        'active', 'all-positions-note', 'low-fret-note', 'auxiliary-note', 'stretch-warning'
      );
      // Clear any inline styles
      note.style.removeProperty('opacity');
      note.style.removeProperty('border');
      note.style.removeProperty('animation');
      
      // Remove any tooltip elements
      const tooltip = note.querySelector('.tooltip');
      if (tooltip) {
        note.removeChild(tooltip);
      }
    });
  }
  
  /**
   * Register DOM event listeners
   * @private
   */
  _registerEventListeners() {
    // Register common UI listeners for all view types
    document.addEventListener('click', (event) => {
      if (event.target.closest('.toggle-debug-panel')) {
        this.toggleDebugPanel();
      }
    });
    
    // Keyboard controls
    document.addEventListener('keydown', (event) => {
      // Common keyboard shortcuts
      if (event.key === 'Escape') {
        this.closeAllMenus();
      }
    });
  }
  
  /**
   * Get a parameter from URL or from a DOM element
   * @param {string} paramName - Parameter name
   * @param {string} defaultValue - Default value if not found
   * @returns {string} Parameter value
   */
  getParameter(paramName, defaultValue) {
    const urlParams = new URLSearchParams(window.location.search);
    const urlValue = urlParams.get(paramName);
    if (urlValue) return urlValue;
    
    const element = document.getElementById(paramName);
    return element ? element.value : defaultValue;
  }
  
  /**
   * Find all elements with notes of a specific tone and deactivate those not needed
   * @param {Array<HTMLElement>|NodeList} elements - Elements with the tone
   * @param {number} maxToKeep - Maximum number of elements to keep active
   * @returns {Array<HTMLElement>} Kept elements
   */
  optimizeActiveNotes(elements, maxToKeep = 2) {
    // Convert NodeList to Array if needed
    const elementsArray = Array.isArray(elements) ? elements : Array.from(elements);
    
    if (elementsArray.length <= maxToKeep) return elementsArray;
    
    this.performance.start('optimizeActiveNotes');
    this.log(`Optimizing ${elementsArray.length} active notes to ${maxToKeep}`, 'debug');
    
    // Mapping of string names to their position in the guitar (lower = higher string)
    const stringOrder = {};
    this.state.stringArray.forEach((s, i) => stringOrder[s] = i);
    
    // Get string and fret info for each element
    const elementInfo = elementsArray.map(el => {
      const stringEl = el.closest('[class*="String"]');
      const fretEl = el.closest('[class*="fret"]');
      
      const stringName = stringEl ? 
        Array.from(stringEl.classList).find(cls => cls.endsWith('String')) : null;
      
      const fretNumber = fretEl ? 
        parseInt(Array.from(fretEl.classList)
          .find(cls => cls.startsWith('fret'))
          ?.replace('fret', '') || '0') : 0;
      
      return {
        element: el,
        string: stringName,
        stringIndex: stringName ? (stringOrder[stringName] || 999) : 999,
        fret: fretNumber
      };
    });
    
    // Sort elements by preference (prefer specific strings & lower frets)
    const sorted = elementInfo.sort((a, b) => {
      // 1. Prefer specific strings based on view type
      const stringDiff = a.stringIndex - b.stringIndex;
      if (stringDiff !== 0) return stringDiff;
      
      // 2. Prefer lower frets (0-12)
      const aFretValue = a.fret <= 12 ? a.fret : a.fret + 100;
      const bFretValue = b.fret <= 12 ? b.fret : b.fret + 100;
      return aFretValue - bFretValue;
    });
    
    // Keep only the most preferred elements
    const toKeep = sorted.slice(0, maxToKeep);
    const toDeactivate = sorted.slice(maxToKeep);
    
    // Deactivate the less preferred elements
    toDeactivate.forEach(info => {
      const el = info.element;
      el.classList.remove('active');
      
      // Find the associated img and reset it
      const img = el.querySelector('img.tone');
      if (img) {
        img.classList.remove('active', 'root');
        img.style.opacity = '';
      }
    });
    
    this.performance.end('optimizeActiveNotes');
    return toKeep.map(info => info.element);
  }
  
  /**
   * Log a message if logging is enabled
   * @param {string} message - Message to log
   * @param {string} level - Log level (debug, info, warn, error)
   */
  log(message, level = 'debug') {
    if (!this.config.enableLogging && level === 'debug') return;
    if (!console[level]) level = 'log';
    
    const viewType = this.config.viewType.charAt(0).toUpperCase() + this.config.viewType.slice(1);
    console[level](`[${viewType}Fretboard] ${message}`);
  }
  
  /**
   * Toggle debug panel visibility
   */
  toggleDebugPanel() {
    const panelId = `${this.config.viewType}-debug-panel`;
    const panel = document.getElementById(panelId);
    
    if (panel) {
      const isVisible = panel.style.display !== 'none';
      panel.style.display = isVisible ? 'none' : 'block';
      this.log(`Debug panel ${isVisible ? 'hidden' : 'shown'}`, 'info');
    } else {
      this.log('Debug panel not found', 'warn');
    }
  }
  
  /**
   * Close all dropdown menus
   */
  closeAllMenus() {
    const dropdowns = document.querySelectorAll('.sese.slar-active, .slit:not(.sehi)');
    dropdowns.forEach(el => {
      if (el.classList.contains('sese')) {
        el.classList.remove('slar-active');
      } else if (el.classList.contains('slit')) {
        el.classList.add('sehi');
      }
    });
  }
}

// Export the class
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { FretboardCore };
} else {
  window.FretboardCore = FretboardCore;
}
