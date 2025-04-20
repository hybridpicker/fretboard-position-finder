/**
 * String Interaction Effects
 * Enhances the visual feedback when strings are played
 */

document.addEventListener('DOMContentLoaded', function() {
  // Get all note click elements
  const noteClickElements = document.querySelectorAll('.note-click');
  
  // Add click event listeners to each note
  noteClickElements.forEach(function(noteElement) {
    noteElement.addEventListener('click', function() {
      // Get the string class from the parent element
      const fretElement = this.closest('.fret');
      if (!fretElement) return;
      
      // Identify which string was clicked
      const stringClasses = [
        'highAString', 'eString', 'bString', 'gString', 
        'dString', 'AString', 'ELowString', 'lowBString'
      ];
      
      let clickedString = null;
      for (const stringClass of stringClasses) {
        if (fretElement.classList.contains(stringClass)) {
          clickedString = stringClass;
          break;
        }
      }
      
      if (!clickedString) return;
      
      // Get all frets with the same string class
      const stringFrets = document.querySelectorAll(`.fret.${clickedString}`);
      
      // Add active class to all frets of this string for visual effect
      stringFrets.forEach(function(fret) {
        fret.classList.add('string-active');
        
        // Remove the class after animation completes
        setTimeout(function() {
          fret.classList.remove('string-active');
        }, 500); // Match this to animation duration
      });
    });
  });
  
  // Also hook into the playTone function if it exists
  if (typeof window.playTone === 'function') {
    // Store the original function
    const originalPlayTone = window.playTone;
    
    // Replace with enhanced version
    window.playTone = function(note, stringName) {
      // Call the original playTone function
      originalPlayTone(note, stringName);
      
      // Add visual feedback
      const stringFrets = document.querySelectorAll(`.fret.${stringName}`);
      stringFrets.forEach(function(fret) {
        fret.classList.add('string-active');
        
        setTimeout(function() {
          fret.classList.remove('string-active');
        }, 500);
      });
    };
  }
});
