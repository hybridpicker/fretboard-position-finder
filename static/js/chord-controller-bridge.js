/**
 * Chord Controller Bridge
 * 
 * This file creates a compatibility layer between the legacy global getTonesFromDataChords function
 * and the new ChordFretboardController class-based implementation.
 */

(function() {
  console.log('BRIDGE: Setting up chord controller bridge');

  // Wait for DOM ready to ensure the controller is initialized
  document.addEventListener('DOMContentLoaded', function() {
    // Ensure we don't run this twice
    if (window._bridgeInitialized) {
      return;
    }
    
    // Expose the global getTonesFromDataChords function that proxies to the controller
    window.getTonesFromDataChords = function(position, range) {
      console.log('BRIDGE: Global getTonesFromDataChords called with', { position, range });
      
      // Find the controller instance
      const controller = window.chordFretboardController;
      
      if (!controller) {
        console.error('BRIDGE: ChordFretboardController not found! Chord display will not work.');
        return;
      }
      
      // Call the controller's method
      console.log('BRIDGE: Forwarding to controller.updateChordDisplay');
      return controller.updateChordDisplay(position, range);
    };
    
    // Mark bridge as initialized
    window._bridgeInitialized = true;
    console.log('BRIDGE: Chord controller bridge successfully initialized');
  });
})();
