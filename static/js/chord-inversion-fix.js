/**
 * Chord Inversion Fix
 * A minimal solution that ensures chord inversions display correctly
 */

// Wait for the document to be ready
document.addEventListener('DOMContentLoaded', function() {
  console.log('Chord inversion fix loaded');
  
  // Only override cursor functions if we're on a chord page
  if (isChordPage()) {
    overrideCursorFunctions();
  }
});

/**
 * Check if we're on a chord page
 */
function isChordPage() {
  return window.location.href.toLowerCase().includes('chord') || 
         document.querySelector('#chords_options_select') !== null;
}

/**
 * Override cursor click functions
 */
function overrideCursorFunctions() {
  // Store original functions
  const originalLeftClick = window.leftCursorClick;
  const originalRightClick = window.rightCursorClick;
  
  // Replace with our fixed versions
  window.leftCursorClick = function(e) {
    // Call original function first
    if (typeof originalLeftClick === 'function') {
      originalLeftClick.call(this, e);
    }
    
    // Apply our fix after a short delay
    setTimeout(fixChordDisplay, 50);
  };
  
  window.rightCursorClick = function(e) {
    // Call original function first
    if (typeof originalRightClick === 'function') {
      originalRightClick.call(this, e);
    }
    
    // Apply our fix after a short delay
    setTimeout(fixChordDisplay, 50);
  };
  
  console.log('Cursor functions overridden');
  
  // Also run our fix on page load
  setTimeout(fixChordDisplay, 500);
}

/**
 * Fix chord display after navigation
 */
function fixChordDisplay() {
  console.log('Fixing chord display...');
  
  // Step 1: Make sure all active notes have active tone images
  document.querySelectorAll('.note.active').forEach(function(noteEl) {
    const toneImg = noteEl.querySelector('img.tone');
    if (toneImg) {
      toneImg.classList.add('active');
      toneImg.style.opacity = '1';
    }
  });
  
  // Step 2: Find and style root notes correctly
  let rootFound = false;
  document.querySelectorAll('.note.active').forEach(function(noteEl) {
    const toneImg = noteEl.querySelector('img.tone');
    if (!toneImg) return;
    
    // Check if this is a root note (multiple detection methods)
    const isRoot = toneImg.getAttribute('data-is-root') === 'true' || 
                  toneImg.classList.contains('root') ||
                  (toneImg.dataset.noteFunction && toneImg.dataset.noteFunction === 'R');
    
    if (isRoot) {
      rootFound = true;
      toneImg.classList.add('root');
      toneImg.src = '/static/media/red_circle.svg';
      toneImg.style.opacity = '1';
      toneImg.style.border = '2px solid rgb(204, 0, 0)';
      toneImg.style.boxShadow = 'rgba(255, 0, 0, 0.3) 0px 0px 5px';
      
      // Make root note name visible
      const noteNameEl = noteEl.querySelector('.notename');
      if (noteNameEl) {
        noteNameEl.style.visibility = 'visible';
        noteNameEl.style.opacity = '1';
        noteNameEl.classList.add('show-name');
        noteNameEl.style.fontWeight = 'bold';
      }
    } else {
      // Non-root notes should have standard styling
      toneImg.classList.remove('root');
      toneImg.src = '/static/media/yellow_circle.svg';
      toneImg.style.border = '';
      toneImg.style.boxShadow = '';
      
      // Hide note names for non-root notes
      const noteNameEl = noteEl.querySelector('.notename');
      if (noteNameEl) {
        noteNameEl.style.visibility = 'hidden';
        noteNameEl.style.opacity = '0';
        noteNameEl.classList.remove('show-name');
      }
    }
  });
  
  // Step 3: If no root found, try to mark the first note as root
  if (!rootFound) {
    const firstNoteEl = document.querySelector('.note.active');
    if (firstNoteEl) {
      const toneImg = firstNoteEl.querySelector('img.tone');
      if (toneImg) {
        toneImg.classList.add('root');
        toneImg.src = '/static/media/red_circle.svg';
        toneImg.style.opacity = '1';
        toneImg.style.border = '2px solid rgb(204, 0, 0)';
        toneImg.style.boxShadow = 'rgba(255, 0, 0, 0.3) 0px 0px 5px';
        
        // Make first note name visible as root
        const noteNameEl = firstNoteEl.querySelector('.notename');
        if (noteNameEl) {
          noteNameEl.style.visibility = 'visible';
          noteNameEl.style.opacity = '1';
          noteNameEl.classList.add('show-name');
          noteNameEl.style.fontWeight = 'bold';
        }
      }
    }
  }
  
  console.log('Chord display fixed');
}

// Make the fix function available globally
window.fixChordDisplay = fixChordDisplay;
