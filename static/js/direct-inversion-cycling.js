/**
 * Direct inversion cycling without showing alternatives
 * This script bypasses the chord-inversions.js display system entirely
 * to prevent flashing all inversions when cycling.
 */

(function() {
    
    // Wait for DOM to be ready before initializing
    document.addEventListener('DOMContentLoaded', function() {
        
        // Completely override cursor clicks with our direct versions
        window.leftCursorClick = function() {
            directCycleInversion('next');
        };
        
        window.rightCursorClick = function() {
            directCycleInversion('prev');
        };
        
        // Wait for cursor elements to be created, then attach our handlers
        setTimeout(ensureDirectCursorHandlers, 500);
    });
    
    /**
     * Direct cycle to next/previous inversion without showing all inversions
     */
    function directCycleInversion(direction) {
        // Get current state
        const urlParams = new URLSearchParams(window.location.search);
        const currentPosition = urlParams.get('position_select') || 'Root Position';
        const positions = getAvailablePositions();
        
        if (positions.length <= 1) {
            return;
        }
        
        // Find position in cycle
        const currentIndex = positions.indexOf(currentPosition);
        if (currentIndex === -1) {
            return;
        }
        
        // Calculate next/prev position
        let newIndex;
        if (direction === 'next') {
            newIndex = (currentIndex + 1) % positions.length;
        } else {
            newIndex = (currentIndex - 1 + positions.length) % positions.length;
        }
        
        const newPosition = positions[newIndex];
        
        // Update URL to reflect new position
        urlParams.set('position_select', newPosition);
        const newUrl = window.location.pathname + '?' + urlParams.toString();
        history.pushState({}, '', newUrl);
        
        // We'll try different methods to update the display, but always with direct note activation
        
        // Method 1: Direct activateNotesForPosition from direct_chord_navigation.js
        if (typeof activateNotesForPosition === 'function') {
            try {
                activateNotesForPosition(newPosition);
                return true;
            } catch (error) {
                console.warn("Error using activateNotesForPosition:", error);
            }
        }
        
        // Method 2: getTonesFromDataChords from fretboard_chords.js
        if (typeof getTonesFromDataChords === 'function') {
            try {
                const range = getRange();
                getTonesFromDataChords(newPosition, range);
                return true;
            } catch (error) {
                console.warn("Error using getTonesFromDataChords:", error);
            }
        }
        
        // If we get here, neither method worked, try manual activation
        try {
            manualActivatePosition(newPosition);
            return true;
        } catch (error) {
            console.warn("Error with manual activation:", error);
        }
        
        // Last resort: refresh the page
        window.location.href = newUrl;
    }
    
    /**
     * Manual position activation as last resort
     */
    function manualActivatePosition(position) {
        
        // Clear all active notes first
        document.querySelectorAll('.note.active').forEach(note => {
            note.classList.remove('active');
        });
        
        document.querySelectorAll('.tone.active').forEach(tone => {
            tone.classList.remove('active');
            if (tone.classList.contains('root')) {
                tone.classList.remove('root');
                tone.src = '/static/media/yellow_circle.svg';
            }
        });
        
        // Get position data
        const range = getRange();
        const internalPos = position === 'Root Position' ? 'Basic Position' : position;
        
        if (!window.voicing_data || !window.voicing_data[range] || !window.voicing_data[range][internalPos]) {
            console.warn(`No voicing data for range: ${range}, position: ${internalPos}`);
            return false;
        }
        
        // Get the position data
        let posData = window.voicing_data[range][internalPos];
        if (Array.isArray(posData)) {
            posData = posData[0];
        }
        
        // Activate each note in the position
        for (const stringName in posData) {
            if (!posData.hasOwnProperty(stringName) || stringName === 'assigned_strings') continue;
            
            const noteData = posData[stringName];
            if (!noteData || !noteData[0]) continue;
            
            // Get note info
            let noteName = noteData[0].toLowerCase();
            const isRoot = noteData.length > 1 && (noteData[1] === 'R' || noteData[1] === 'Root' || noteData[3] === true);
            
            // Remove octave numbers
            const baseNote = noteName.replace(/[0-9]/g, '');
            
            // Find and activate the note
            const noteElements = document.querySelectorAll(`.${stringName} .note.${baseNote}`);
            if (noteElements.length === 0) {
                continue;
            }
            
            // Just activate the first matching note for simplicity
            const noteEl = noteElements[0];
            noteEl.classList.add('active');
            
            // Also activate the tone image
            const toneEl = noteEl.querySelector('img.tone');
            if (toneEl) {
                toneEl.classList.add('active');
                
                // Mark root note if applicable
                if (isRoot) {
                    toneEl.classList.add('root');
                    toneEl.src = '/static/media/red_circle.svg';
                }
            }
        }
        
        return true;
    }
    
    /**
     * Get all available positions from voicing data for the current chord
     */
    function getAvailablePositions() {
        // Standard positions (might be filtered by available data)
        let positions = ['Root Position', 'First Inversion', 'Second Inversion', 'Third Inversion'];
        
        // Filter based on what's actually in the data
        if (window.voicing_data) {
            const range = getRange();
            
            if (window.voicing_data[range]) {
                // Build from scratch based on available data
                positions = [];
                
                // Map Basic Position to Root Position for UI consistency
                if (window.voicing_data[range]['Basic Position']) {
                    positions.push('Root Position');
                }
                
                // Add available inversions
                ['First Inversion', 'Second Inversion', 'Third Inversion'].forEach(pos => {
                    if (window.voicing_data[range][pos]) {
                        positions.push(pos);
                    }
                });
            }
        }
        
        return positions;
    }
    
    /**
     * Get the current string range
     */
    function getRange() {
        // Try getting from voicing data first
        if (window.voicing_data && window.voicing_data.note_range) {
            return window.voicing_data.note_range;
        }
        
        // Fall back to URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('note_range') || 'e - g';
    }
    
    /**
     * Ensure cursor elements have our direct handlers
     */
    function ensureDirectCursorHandlers() {
        const leftCursor = document.querySelector('.left-cursor');
        const rightCursor = document.querySelector('.right-cursor');
        
        if (leftCursor) {
            // Remove any onclick attribute to prevent double handling
            leftCursor.removeAttribute('onclick');
            
            // Create a new element to replace it (cleanest way to ensure no existing handlers)
            const newLeftCursor = leftCursor.cloneNode(true);
            leftCursor.parentNode.replaceChild(newLeftCursor, leftCursor);
            
            // Add our direct handler
            newLeftCursor.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                window.leftCursorClick();
            });
            
        }
        
        if (rightCursor) {
            // Remove any onclick attribute to prevent double handling
            rightCursor.removeAttribute('onclick');
            
            // Create a new element to replace it (cleanest way to ensure no existing handlers)
            const newRightCursor = rightCursor.cloneNode(true);
            rightCursor.parentNode.replaceChild(newRightCursor, rightCursor);
            
            // Add our direct handler
            newRightCursor.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                window.rightCursorClick();
            });
            
        }
    }
    
    // Add a debug function for troubleshooting
    window.debugDirectInversionCycling = function() {
        const positions = getAvailablePositions();
        const urlParams = new URLSearchParams(window.location.search);
        const currentPosition = urlParams.get('position_select') || 'Root Position';
        const range = getRange();
        
        
        // Check if our functions are indeed being used
        const isLeftOurs = window.leftCursorClick.toString().includes('directCycleInversion');
        const isRightOurs = window.rightCursorClick.toString().includes('directCycleInversion');
        
        
        return {
            currentPosition,
            range,
            positions,
            voicingData: window.voicing_data,
            usingOurHandlers: {
                left: isLeftOurs,
                right: isRightOurs
            }
        };
    };
})();
