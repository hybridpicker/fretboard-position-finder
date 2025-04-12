/**
 * Minimalistic Fretboard Enhancement Script
 * Simple enhancement with no complex operations that could crash the browser
 */

document.addEventListener('DOMContentLoaded', function() {
  // Simple enhancements only
  initMinimalFretboard();
});

/**
 * Initialize minimal fretboard enhancements
 */
function initMinimalFretboard() {
  // Just add minimal class to fretboard
  const fretboard = document.querySelector('.fretboard');
  if (fretboard && !fretboard.classList.contains('minimal-fretboard')) {
    fretboard.classList.add('minimal-fretboard');
  }
}

// Empty function - no tilt effect
function setupFretboardTilt() {
  return;
}
