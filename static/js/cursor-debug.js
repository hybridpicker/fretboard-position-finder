/**
 * Cursor Debug Helper
 * This file adds additional debugging for cursor elements and click events
 */

(function() {
  // Wait for DOM to be ready
  document.addEventListener('DOMContentLoaded', function() {
    // Delay execution to ensure other scripts have run
    setTimeout(debugCursors, 1000);
  });

  function debugCursors() {
    console.log('CURSOR_DEBUG_LOG: Running cursor debug helper');
    
    // Look for cursor elements
    const leftCursor = document.querySelector('.left-cursor');
    const rightCursor = document.querySelector('.right-cursor');
    
    console.log('CURSOR_DEBUG_LOG: Left cursor element found:', leftCursor ? 'yes' : 'no');
    console.log('CURSOR_DEBUG_LOG: Right cursor element found:', rightCursor ? 'yes' : 'no');
    
    if (leftCursor) {
      console.log('CURSOR_DEBUG_LOG: Left cursor details:', {
        visibility: leftCursor.style.visibility,
        display: leftCursor.style.display,
        classes: leftCursor.className,
        parentElement: leftCursor.parentElement ? leftCursor.parentElement.tagName : 'none'
      });
      
      // Add explicit click handler
      leftCursor.onclick = function(e) {
        console.log('CURSOR_DEBUG_LOG: Left cursor direct click detected');
        
        if (typeof window.fpfLeftCursorClick === 'function') {
          console.log('CURSOR_DEBUG_LOG: Calling fpfLeftCursorClick');
          window.fpfLeftCursorClick();
        } else {
          console.log('CURSOR_DEBUG_LOG: ERROR - fpfLeftCursorClick function not found');
        }
      };
    }
    
    if (rightCursor) {
      console.log('CURSOR_DEBUG_LOG: Right cursor details:', {
        visibility: rightCursor.style.visibility,
        display: rightCursor.style.display,
        classes: rightCursor.className,
        parentElement: rightCursor.parentElement ? rightCursor.parentElement.tagName : 'none'
      });
      
      // Add explicit click handler
      rightCursor.onclick = function(e) {
        console.log('CURSOR_DEBUG_LOG: Right cursor direct click detected');
        
        if (typeof window.fpfRightCursorClick === 'function') {
          console.log('CURSOR_DEBUG_LOG: Calling fpfRightCursorClick');
          window.fpfRightCursorClick();
        } else {
          console.log('CURSOR_DEBUG_LOG: ERROR - fpfRightCursorClick function not found');
        }
      };
    }
    
    // Force setting cursor mode to 'chords'
    if (window.fpf && window.fpf.cursor) {
      const state = window.fpf.cursor;
      console.log('CURSOR_DEBUG_LOG: Current cursor mode:', state.mode);
      
      // If we're on a chord page but mode is not 'chords', fix it
      if (window.location.href.toLowerCase().includes('chord') && state.mode !== 'chords') {
        console.log('CURSOR_DEBUG_LOG: Correcting mode from', state.mode, 'to chords');
        state.mode = 'chords';
        
        // Determine chord type from controller or voicing_data
        if (window.chordFretboardController && window.chordFretboardController.chordState) {
          state.chordType = window.chordFretboardController.chordState.chordType || 'triad';
        } else if (window.voicing_data && window.voicing_data.chord) {
          state.chordType = window.voicing_data.chord.includes('7') ? 'seventh' : 'triad';
        }
        
        // Set max inversion based on chord type
        state.maxInversion = (state.chordType === 'triad') ? 2 : 3;
        
        console.log('CURSOR_DEBUG_LOG: Updated cursor state:', JSON.parse(JSON.stringify(state)));
        
        // Update cursor visibility with corrected state
        if (typeof window.updateCursorVisibility === 'function') {
          window.updateCursorVisibility();
        }
      }
    }
    
    // Check for click handlers using event listeners
    console.log('CURSOR_DEBUG_LOG: Adding global click interceptor');
    document.body.addEventListener('click', function(e) {
      // Check if cursor was clicked
      if (e.target.closest('.left-cursor') || e.target.closest('.right-cursor')) {
        console.log('CURSOR_DEBUG_LOG: Cursor clicked through event delegation:', 
                   e.target.closest('.left-cursor') ? 'left' : 'right');
      }
    }, true);
    
    // Add keyboard navigation
    console.log('CURSOR_DEBUG_LOG: Adding keyboard navigation');
    document.addEventListener('keydown', function(e) {
      if (e.key === 'ArrowLeft') {
        console.log('CURSOR_DEBUG_LOG: Left arrow key pressed');
        if (typeof window.fpfLeftCursorClick === 'function') {
          window.fpfLeftCursorClick();
        }
      } else if (e.key === 'ArrowRight') {
        console.log('CURSOR_DEBUG_LOG: Right arrow key pressed');
        if (typeof window.fpfRightCursorClick === 'function') {
          window.fpfRightCursorClick();
        }
      }
    });
    
    // Final checks
    console.log('CURSOR_DEBUG_LOG: Checking global functions');
    console.log('CURSOR_DEBUG_LOG: fpfLeftCursorClick exists:', typeof window.fpfLeftCursorClick === 'function');
    console.log('CURSOR_DEBUG_LOG: fpfRightCursorClick exists:', typeof window.fpfRightCursorClick === 'function');
    console.log('CURSOR_DEBUG_LOG: updateCursorVisibility exists:', typeof window.updateCursorVisibility === 'function');
    console.log('CURSOR_DEBUG_LOG: Cursor debug helper complete');
  }
})();
