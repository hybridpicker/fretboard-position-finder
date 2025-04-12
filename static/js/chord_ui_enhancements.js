/**
 * Chord UI Enhancements
 * Adds improved usability features for chord display and navigation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize inversion and range highlighting
    initInversionHighlighting();
    
    // Initialize keyboard shortcuts
    initKeyboardShortcuts();
    
    // Chord diagram initialization removed for consistent UI
});

/**
 * Adds visual indicators to show current inversion structure
 */
function initInversionHighlighting() {
    // Get current position from select element
    const positionSelect = document.getElementById('position_select');
    if (!positionSelect) return;
    
    const currentPosition = positionSelect.value;
    
    // Add a visual indicator in the analysis container
    const positionValue = document.querySelector('.position-value');
    if (positionValue) {
        // Add different styling based on position
        if (currentPosition === 'Basic Position') {
            positionValue.style.color = '#28a745'; // Green for root position
        } else if (currentPosition === 'First Inversion') {
            positionValue.style.color = '#007bff'; // Blue for first inversion
        } else if (currentPosition === 'Second Inversion') {
            positionValue.style.color = '#fd7e14'; // Orange for second inversion
        } else if (currentPosition === 'Third Inversion') {
            positionValue.style.color = '#dc3545'; // Red for third inversion
        }
    }
}

/**
 * Adds keyboard shortcuts for navigation (except arrow keys)
 */
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Up/down arrows for root note
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            increaseRoot();
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            decreaseRoot();
        }
        
        // Number keys 1-4 for positions
        if (e.key >= '1' && e.key <= '4') {
            e.preventDefault();
            selectPositionByNumber(parseInt(e.key));
        }
    });
}

/**
 * Select a position by number (1-4)
 */
function selectPositionByNumber(number) {
    const positionSelect = document.getElementById('position_select');
    if (!positionSelect) return;
    
    const positions = ['Basic Position', 'First Inversion', 'Second Inversion', 'Third Inversion'];
    const targetPosition = positions[number - 1];
    
    if (targetPosition) {
        // Update the select element
        positionSelect.value = targetPosition;
        
        // Update URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set('position_select', targetPosition);
        
        // Get the current note range
        const noteRange = document.getElementById('note_range')?.value || 
                         urlParams.get('note_range') || 'e - g';
        
        // Update the fretboard
        getTonesFromDataChords(targetPosition, noteRange);
        
        // Update the URL without reloading
        window.history.replaceState(null, null, '?' + urlParams.toString());
    }
}

/**
 * Placeholder for chord diagram functionality - removed for consistent UI
 */
function initChordDiagram() {
    // Chord diagram creation removed to maintain consistent design
    // across scales, arpeggios and chords
}
