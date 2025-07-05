/**
 * Chord Controller Bridge
 * 
 * This file creates a compatibility layer between the legacy global getTonesFromDataChords function
 * and the new ChordFretboardController class-based implementation.
 */

(function() {
  console.log('BRIDGE: Setting up chord controller bridge');

  // Initialize immediately and also on DOM ready
  function initializeBridge() {
    // Ensure we don't run this twice
    if (window._bridgeInitialized) {
      return;
    }
    
    console.log('BRIDGE: Initializing getTonesFromDataChords function');
    
    // Expose the global getTonesFromDataChords function that proxies to the controller
    window.getTonesFromDataChords = function(position, range) {
      console.log('BRIDGE: Global getTonesFromDataChords called with', { position, range });
      
      // Find the controller instance
      // Try multiple possible names
      const controller = window.chordFretboardController || 
                        window.chordViewController || 
                        window.controller;
      
      if (!controller) {
        console.error('BRIDGE: Chord controller not found! Trying fallback...');
        
        // Try to find it in the global scope
        for (let key in window) {
          if (key.toLowerCase().includes('chord') && key.toLowerCase().includes('controller')) {
            console.log('BRIDGE: Found potential controller:', key);
            const ctrl = window[key];
            if (ctrl && typeof ctrl.updateChordDisplay === 'function') {
              console.log('BRIDGE: Using controller:', key);
              return ctrl.updateChordDisplay(position, range);
            }
          }
        }
        
        console.error('BRIDGE: No suitable chord controller found');
        return;
      }
      
      // Call the controller's method
      console.log('BRIDGE: Forwarding to controller.updateChordDisplay');
      return controller.updateChordDisplay(position, range);
    };
    
    // Mark bridge as initialized
    window._bridgeInitialized = true;
    console.log('BRIDGE: Chord controller bridge successfully initialized');
  }
  
  // Initialize immediately
  initializeBridge();
  
  // Also initialize on DOM ready as backup
  document.addEventListener('DOMContentLoaded', initializeBridge);
})();
