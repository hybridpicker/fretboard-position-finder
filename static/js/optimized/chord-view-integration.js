/**
 * Chord View Integration Script
 * This script integrates the optimized ChordViewController with the existing codebase.
 * It sets up compatibility hooks to ensure all existing features continue to work.
 */

// Wait for DOM content to be loaded and ensure ChordViewController is available
document.addEventListener('DOMContentLoaded', function() {
  // Only proceed if ChordViewController is defined
  if (typeof ChordViewController === 'undefined') {
    console.warn('ChordViewController not found. Skipping initialization.');
    return;
  }
  
  // Get debug mode from Django context if available
  const debugMode = window.DJANGO_DEBUG || false;
  
  // Count strings (support for 6, 7, or 8 string guitars)
  const stringCount = document.querySelector('.BbString') ? 8 : 
                      document.querySelector('.FString') ? 7 : 6;
  
  
  // Create controller with configuration
  try {
    window.chordViewController = new ChordViewController({
      debug: debugMode,
      enableCursors: true,
      enableInversions: true,
      enableKeyboardNavigation: !window.disableKeyboardNavigation,
      stringCount: stringCount
    });
    
    // Set up compatibility with existing functions
    setupCompatibilityLayer();
  } catch (e) {
    console.warn('Failed to initialize ChordViewController:', e);
  }
});

/**
 * Sets up compatibility with the existing codebase
 */
function setupCompatibilityLayer() {
  // Compatibility with getTonesFromDataChords from fretboard_chords.2.0.4.js
  if (typeof getTonesFromDataChords === 'function') {
    window._originalGetTonesFromDataChords = getTonesFromDataChords;
    
    window.getTonesFromDataChords = function(position, range) {
      if (window.chordViewController && window.chordViewController.state.initialized) {
        return window.chordViewController.activatePosition(position, range);
      } else {
        return window._originalGetTonesFromDataChords(position, range);
      }
    };
  }
  
  // Compatibility with cursor management
  if (typeof initCursorManagement === 'function') {
    window._originalInitCursorManagement = initCursorManagement;
    
    window.initCursorManagement = function(target) {
      if (window.chordViewController && window.chordViewController.state.initialized && target === 'chords') {
        // Already handled by the controller
        return { initialized: true, target: target };
      } else {
        return window._originalInitCursorManagement(target);
      }
    };
  }
  
  // Compatibility with inversion functions from chord-inversions-fixed.js
  if (typeof activateChordInversion === 'function') {
    window._originalActivateChordInversion = activateChordInversion;
    
    window.activateChordInversion = function(inversion) {
      if (window.chordViewController && window.chordViewController.state.initialized) {
        // Map between display names and internal names
        const inversionMap = {
          'Root Position': 'Basic Position',
          'Basic Position': 'Basic Position',
          'First Inversion': 'First Inversion',
          'Second Inversion': 'Second Inversion',
          'Third Inversion': 'Third Inversion'
        };
        
        const position = inversionMap[inversion] || inversion;
        return window.chordViewController.activatePosition(position, window.chordViewController.state.currentRange);
      } else {
        return window._originalActivateChordInversion(inversion);
      }
    };
  }
  
  // Listen for custom events
  document.addEventListener('chord-view-initialized', function(e) {
    
    // Dispatch an event for other components that might need to know about the chord view
    document.dispatchEvent(new CustomEvent('chord-system-ready', {
      detail: { controller: e.detail.controller }
    }));
  });
  
}
