/**
 * Chord Navigation
 * Handles chord inversion navigation by updating URL parameters
 */

(function() {
    'use strict';
    
    console.log('[ChordNav] Loading...');
    
    // Check if we have chord parameters in URL
    const urlParams = new URLSearchParams(window.location.search);
    const hasChordParams = urlParams.has('chords_options_select');
    
    if (!hasChordParams) {
        console.log('[ChordNav] No chord parameters in URL');
        return;
    }
    
    console.log('[ChordNav] Chord page detected via URL');
    
    // Position mapping
    const positions = ['Root Position', 'First Inversion', 'Second Inversion', 'Third Inversion'];
    
    // Get current position
    let currentPosition = urlParams.get('position_select') || 'Root Position';
    let currentIndex = positions.indexOf(currentPosition);
    if (currentIndex === -1) currentIndex = 0;
    
    console.log('[ChordNav] Current position:', currentPosition, 'Index:', currentIndex);
    
    // Determine max inversions based on chord type
    const chordType = urlParams.get('chords_options_select') || '';
    const maxIndex = (chordType.includes('7') || chordType.includes('9')) ? 3 : 2;
    
    console.log('[ChordNav] Chord type:', chordType, 'Max index:', maxIndex);
    
    // Navigation functions
    function navigateLeft() {
        console.log('[ChordNav] Navigate left');
        currentIndex--;
        if (currentIndex < 0) currentIndex = maxIndex;
        updateURL();
    }
    
    function navigateRight() {
        console.log('[ChordNav] Navigate right');
        currentIndex++;
        if (currentIndex > maxIndex) currentIndex = 0;
        updateURL();
    }
    
    function updateURL() {
        const newPosition = positions[currentIndex];
        console.log('[ChordNav] Updating to position:', newPosition);
        
        // Update URL
        urlParams.set('position_select', newPosition);
        const newURL = window.location.pathname + '?' + urlParams.toString();
        
        console.log('[ChordNav] New URL:', newURL);
        
        // Navigate to new URL
        window.location.href = newURL;
    }
    
    // Override cursor functions
    window.leftCursorClick = navigateLeft;
    window.rightCursorClick = navigateRight;
    
    // Add click handlers to cursors
    setTimeout(() => {
        const leftCursor = document.querySelector('.left-cursor');
        const rightCursor = document.querySelector('.right-cursor');
        
        if (leftCursor) {
            leftCursor.onclick = function(e) {
                e.preventDefault();
                navigateLeft();
            };
            // Don't add any visual indicator - background image handles it
        }
        
        if (rightCursor) {
            rightCursor.onclick = function(e) {
                e.preventDefault();
                navigateRight();
            };
            // Don't add any visual indicator - background image handles it
        }
        
        console.log('[ChordNav] Cursor handlers attached');
    }, 1000);
    
    // Export for testing
    window.chordNav = {
        left: navigateLeft,
        right: navigateRight,
        current: () => currentIndex
    };
    
    console.log('[ChordNav] Ready. Page will reload when navigating.');
})();