/**
 * Custom cursor styling enhancement
 * This script ensures that the SVG cursor images are applied correctly
 * by using the SVG files in static/media/svg/cursor_left.svg and cursor_right.svg
 */

// Override the default cursor_controls.css styles with our SVG-based cursors
(function() {
  // Create a style element to override CSS properties
  const style = document.createElement('style');
  document.head.appendChild(style);
  
  // Add CSS to ensure our custom-cursors.css styles take precedence
  style.textContent = `
    /* Ensure background-color is transparent for cursors */
    .left-cursor, .right-cursor {
      background-color: transparent !important;
    }
    
    /* Hide arrow indicators completely */
    .left-cursor::before, .right-cursor::before {
      display: none !important;
    }
  `;
})();

// Flag to track if custom cursors have been initialized
let customCursorsInitialized = false;

/**
 * Initialize custom cursor styling
 */
function initCustomCursors() {
  // Prevent multiple initializations
  if (customCursorsInitialized) {
    return;
  }
  
  // Find cursor elements
  const leftCursor = document.querySelector('.left-cursor');
  const rightCursor = document.querySelector('.right-cursor');
  
  if (!leftCursor && !rightCursor) {
    console.warn('Neither left nor right cursor elements found in the DOM');
    return false;
  }
  
  // Apply custom styling to cursors
  if (leftCursor) {
    // Remove the default triangle indicator by clearing innerHTML
    if (leftCursor.innerHTML.trim()) {
      leftCursor.innerHTML = '';
    }
  }
  
  if (rightCursor) {
    // Remove the default triangle indicator by clearing innerHTML
    if (rightCursor.innerHTML.trim()) {
      rightCursor.innerHTML = '';
    }
  }
  
  // Mark as initialized
  customCursorsInitialized = true;
  console.log('Custom cursor styling initialized');
  
  return true;
}

/**
 * Reset custom cursor styling (useful if DOM changes)
 */
function resetCustomCursors() {
  customCursorsInitialized = false;
  initCustomCursors();
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
  // Add a slight delay to ensure other scripts have run
  setTimeout(initCustomCursors, 500);
  
  // Set up observer to initialize custom cursors when new ones are added
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'childList' && 
          (mutation.addedNodes.length > 0 || mutation.removedNodes.length > 0)) {
        
        // If new cursors are added or old ones removed, reinitialize
        const leftCursor = document.querySelector('.left-cursor');
        const rightCursor = document.querySelector('.right-cursor');
        
        if ((leftCursor && !leftCursor.classList.contains('custom-cursor')) || 
            (rightCursor && !rightCursor.classList.contains('custom-cursor'))) {
          resetCustomCursors();
        }
      }
    });
  });
  
  // Start observing the document body for DOM changes
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  // Store observer reference to potentially disconnect later
  window.customCursorObserver = observer;
});

// Enhanced cursor recreation function that integrates with base.js
function enhancedCleanupDuplicateCursors() {
  // Call the original function if it exists
  if (typeof cleanupDuplicateCursors === 'function') {
    cleanupDuplicateCursors();
  }
  
  // Apply our custom styling
  resetCustomCursors();
}

// Replace the original function if possible
if (typeof cleanupDuplicateCursors === 'function') {
  const originalCleanup = cleanupDuplicateCursors;
  window.cleanupDuplicateCursors = function() {
    originalCleanup();
    resetCustomCursors();
  };
}
