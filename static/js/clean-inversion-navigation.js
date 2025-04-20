/**
 * Clean Inversion Navigation - Defensive version
 * Uses try-catch blocks to prevent crashes
 */

// Prevent multiple initializations 
let cleanInversionInitialized = false;

// Store original functions if they exist
let originalLeftCursorClick;
let originalRightCursorClick;

// Store active note information for cleanup
let activeNoteTracker = {
  activeNotes: [], // Stores references to active note elements
  rootNotes: [],   // Stores references to root note elements
  notesVisible: [] // Stores references to notes with visible names
};

// Wrap everything in a try-catch to prevent full crashes
try {
  document.addEventListener('DOMContentLoaded', function() {
    try {
      // Prevent multiple initializations
      if (cleanInversionInitialized) {
        return;
      }
      
      cleanInversionInitialized = true;
      
      // Only store original functions - don't override them yet
      if (typeof window.leftCursorClick === 'function') {
        originalLeftCursorClick = window.leftCursorClick;
      }
      
      if (typeof window.rightCursorClick === 'function') {
        originalRightCursorClick = window.rightCursorClick;
      }
      
      // Add a console log to help with debugging
      console.log('Clean inversion navigation initialized, but not yet active');
      
      // Instead of immediately overriding, wait a moment to ensure other scripts initialize properly
      setTimeout(function() {
        try {
          console.log('Attempting to apply cursor handlers in a safe way');
          setupSafeCursorHandlers();
        } catch (err) {
          console.error('Error setting up cursor handlers:', err);
        }
      }, 2000);
    } catch (err) {
      console.error('Error in DOMContentLoaded:', err);
    }
  });
} catch (err) {
  console.error('Critical error in script:', err);
}

/**
 * A safer way to set up cursor handlers that doesn't override existing functions
 * but rather enhances them
 */
function setupSafeCursorHandlers() {
  // Find cursor elements
  const leftCursor = document.querySelector('.left-cursor');
  const rightCursor = document.querySelector('.right-cursor');
  
  // Instead of replacing the existing functions, add event listeners to the cursor elements
  if (leftCursor) {
    // Use a separate listener that runs before the original click
    leftCursor.addEventListener('click', function(e) {
      try {
        console.log('Safe left cursor handler executed');
        // Store active notes
        storeActiveNotes();
        // Cleanup will happen after the original click
        setTimeout(function() {
          cleanupAfterNavigation();
        }, 200);
      } catch (err) {
        console.error('Error in left cursor handler:', err);
      }
    }, true);  // true = capture phase, run this before other handlers
  }
  
  if (rightCursor) {
    // Use a separate listener that runs before the original click
    rightCursor.addEventListener('click', function(e) {
      try {
        console.log('Safe right cursor handler executed');
        // Store active notes
        storeActiveNotes();
        // Cleanup will happen after the original click
        setTimeout(function() {
          cleanupAfterNavigation();
        }, 200);
      } catch (err) {
        console.error('Error in right cursor handler:', err);
      }
    }, true);  // true = capture phase, run this before other handlers
  }
}

/**
 * Store information about currently active notes
 * so we can properly clean them up later
 */
function storeActiveNotes() {
  try {
    // Reset the tracker
    activeNoteTracker.activeNotes = [];
    activeNoteTracker.rootNotes = [];
    activeNoteTracker.notesVisible = [];
    
    // Find all active notes
    const activeNotes = document.querySelectorAll('.note.active');
    activeNotes.forEach(note => {
      activeNoteTracker.activeNotes.push(note);
      
      // Check if this note has a visible notename
      const noteName = note.querySelector('.notename');
      if (noteName && (noteName.style.visibility === 'visible' || noteName.style.opacity > 0)) {
        activeNoteTracker.notesVisible.push(noteName);
      }
      
      // Check if this note has a root note image
      const rootImg = note.querySelector('img.tone.root');
      if (rootImg) {
        activeNoteTracker.rootNotes.push(rootImg);
      }
    });
    
    // Also find any active tone images that might not be in active notes
    const activeTones = document.querySelectorAll('img.tone.active');
    activeTones.forEach(tone => {
      // Check if this tone is a root
      if (tone.classList.contains('root')) {
        activeNoteTracker.rootNotes.push(tone);
      }
    });
  } catch (err) {
    console.error('Error storing active notes:', err);
  }
}

/**
 * Final cleanup after navigation has completed
 * This catches any notes that might still be visible
 */
function cleanupAfterNavigation() {
  try {
    console.log('Running cleanup after navigation');
    
    // Ensure we don't have any leftover active notes from previous position
    
    // Get active notes that are not inversion notes
    const activeNotes = document.querySelectorAll('.note.active:not(.inversion-note)');
    
    // Log count for debugging
    console.log(`Found ${activeNotes.length} active notes to clean up`);
    
    // Make sure active notes are fully visible
    activeNotes.forEach(note => {
      note.style.opacity = '1';
      
      // Make sure the tone image is visible
      const toneImg = note.querySelector('img.tone');
      if (toneImg) {
        toneImg.style.opacity = '1';
        toneImg.style.visibility = 'visible';
      }
    });
    
    // Get inversion notes - these should stay visible but with reduced opacity
    const inversionNotes = document.querySelectorAll('.inversion-note');
    
    // Make sure inversion notes are semi-transparent
    inversionNotes.forEach(note => {
      note.style.opacity = '0.4';
      
      // Make tone image semi-transparent too
      const toneImg = note.querySelector('img.tone');
      if (toneImg) {
        toneImg.style.opacity = '0.4';
      }
    });
    
    // Make sure root notes are properly styled
    const rootNotes = document.querySelectorAll('img.tone.root');
    rootNotes.forEach(root => {
      // Set correct image source - only if it's not already set
      if (!root.src.includes('red_circle.svg')) {
        root.src = '/static/media/red_circle.svg';
      }
      
      // Set root styling
      root.style.opacity = '1';
      root.style.border = '2px solid #CC0000';
      root.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.3)';
      
      // Make parent note fully visible
      const parentNote = root.closest('.note');
      if (parentNote) {
        parentNote.style.opacity = '1';
        
        // Find and style the note name
        const noteName = parentNote.querySelector('.notename');
        if (noteName) {
          noteName.style.visibility = 'visible';
          noteName.style.opacity = '1';
          noteName.style.fontWeight = 'bold';
        }
      }
    });
    
    // Also ensure inversion roots are properly styled
    const inversionRoots = document.querySelectorAll('img.tone.inversion-root');
    inversionRoots.forEach(root => {
      root.style.opacity = '0.7';
      root.style.border = '2px dashed #AA5500';
      root.style.boxShadow = '0 0 3px rgba(200, 100, 0, 0.3)';
    });
    
    // Check for any notenames still visible that shouldn't be
    const nonRootNotes = document.querySelectorAll('.note:not(.active)');
    nonRootNotes.forEach(note => {
      const noteName = note.querySelector('.notename');
      if (noteName) {
        noteName.style.visibility = 'hidden';
        noteName.style.opacity = '0';
      }
    });
    
    // Reset tracking data
    activeNoteTracker.activeNotes = [];
    activeNoteTracker.rootNotes = [];
    activeNoteTracker.notesVisible = [];
    
  } catch (err) {
    console.error('Error in cleanup after navigation:', err);
  }
}