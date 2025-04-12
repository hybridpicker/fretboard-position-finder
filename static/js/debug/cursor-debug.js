/**
 * Cursor Debug Utility
 * 
 * This script can be loaded in a browser console to diagnose cursor click issues.
 * Copy and paste this entire script into the browser console and execute it to inspect cursor behavior.
 */

// Create namespace to prevent global scope pollution
const CursorDebug = {
    init: function() {
        console.log('Cursor Debug Utility Initialized');
        
        // Find cursor elements
        this.leftCursor = document.querySelector('.left-cursor');
        this.rightCursor = document.querySelector('.right-cursor');
        
        if (!this.leftCursor || !this.rightCursor) {
            console.error('Cursor elements not found!');
            return false;
        }
        
        console.log('Cursor Elements:', {
            left: this.leftCursor,
            right: this.rightCursor
        });
        
        // Check event handlers
        this.checkEventHandlers();
        
        // Check position state
        this.checkPositionState();
        
        // Add diagnostic listeners
        this.addDiagnosticListeners();
        
        return true;
    },
    
    checkEventHandlers: function() {
        console.log('Left cursor onclick:', this.leftCursor.onclick);
        console.log('Right cursor onclick:', this.rightCursor.onclick);
        
        // Check if global functions exist
        console.log('leftCursorClick function:', typeof window.leftCursorClick);
        console.log('rightCursorClick function:', typeof window.rightCursorClick);
        console.log('fpfLeftCursorClick function:', typeof window.fpfLeftCursorClick);
        console.log('fpfRightCursorClick function:', typeof window.fpfRightCursorClick);
        console.log('safeLeftCursorClick function:', typeof window.safeLeftCursorClick);
        console.log('safeRightCursorClick function:', typeof window.safeRightCursorClick);
    },
    
    checkPositionState: function() {
        // Try to extract current position from URL
        const urlParams = new URLSearchParams(window.location.search);
        const position = urlParams.get('position_select');
        
        // Check position in select element
        const positionSelect = document.getElementById('position_select');
        let selectedPosition = positionSelect ? positionSelect.value : null;
        
        console.log('Position State:', {
            urlPosition: position,
            selectPosition: selectedPosition
        });
        
        // Check modal window state
        console.log('Current Mode:', window.currentMode);
        console.log('Current Inversion:', window.currentInversion);
        console.log('Current Chord Type:', window.currentChordType);
    },
    
    addDiagnosticListeners: function() {
        const self = this;
        
        // Add temporary diagnostic click listeners
        if (this.leftCursor) {
            this.leftCursor.addEventListener('click', function(e) {
                console.log('LEFT CURSOR CLICKED');
                console.log('Event:', e);
                console.log('Target:', e.target);
                console.log('Current Target:', e.currentTarget);
                console.log('Original onclick:', self.leftCursor.onclick);
                
                // Don't prevent default to allow normal handling
            });
        }
        
        if (this.rightCursor) {
            this.rightCursor.addEventListener('click', function(e) {
                console.log('RIGHT CURSOR CLICKED');
                console.log('Event:', e);
                console.log('Target:', e.target);
                console.log('Current Target:', e.currentTarget);
                console.log('Original onclick:', self.rightCursor.onclick);
                
                // Don't prevent default to allow normal handling
            });
        }
        
        // Listen for position changes
        if (positionSelect) {
            positionSelect.addEventListener('change', function() {
                console.log('Position changed to:', this.value);
            });
        }
        
        console.log('Diagnostic listeners added');
    },
    
    fixCursors: function() {
        // This is a last resort function to completely replace cursor handling
        
        console.log('Applying emergency cursor fix...');
        
        // Get cursor elements
        const leftCursor = document.querySelector('.left-cursor');
        const rightCursor = document.querySelector('.right-cursor');
        
        if (!leftCursor || !rightCursor) {
            console.error('Cursor elements not found!');
            return false;
        }
        
        // Create clean replacements to remove all event handlers
        const newLeftCursor = leftCursor.cloneNode(true);
        const newRightCursor = rightCursor.cloneNode(true);
        
        leftCursor.parentNode.replaceChild(newLeftCursor, leftCursor);
        rightCursor.parentNode.replaceChild(newRightCursor, rightCursor);
        
        // Add clean handlers
        newLeftCursor.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Emergency navigation
            const urlParams = new URLSearchParams(window.location.search);
            const currentPosition = urlParams.get('position_select') || 'Root Position';
            const currentRange = urlParams.get('note_range') || 'e - g';
            
            // Simple navigation logic
            let newPosition;
            if (currentPosition === 'Root Position') {
                newPosition = 'Second Inversion';
            } else if (currentPosition === 'First Inversion') {
                newPosition = 'Root Position';
            } else if (currentPosition === 'Second Inversion') {
                newPosition = 'First Inversion';
            } else if (currentPosition === 'Third Inversion') {
                newPosition = 'Second Inversion';
            } else {
                newPosition = 'Root Position';
            }
            
            // Update URL
            urlParams.set('position_select', newPosition);
            window.history.replaceState(null, '', window.location.pathname + '?' + urlParams.toString());
            
            // Update select element
            const positionSelect = document.getElementById('position_select');
            if (positionSelect) {
                for (let i = 0; i < positionSelect.options.length; i++) {
                    if (positionSelect.options[i].value === newPosition) {
                        positionSelect.selectedIndex = i;
                        break;
                    }
                }
                
                // Trigger change event
                positionSelect.dispatchEvent(new Event('change'));
            }
            
            // Update notes display
            if (typeof window.getTonesFromDataChords === 'function') {
                window.getTonesFromDataChords(newPosition, currentRange);
            }
            
            console.log(`Emergency navigation: ${currentPosition} -> ${newPosition}`);
        });
        
        newRightCursor.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Emergency navigation
            const urlParams = new URLSearchParams(window.location.search);
            const currentPosition = urlParams.get('position_select') || 'Root Position';
            const currentRange = urlParams.get('note_range') || 'e - g';
            
            // Simple navigation logic
            let newPosition;
            if (currentPosition === 'Root Position') {
                newPosition = 'First Inversion';
            } else if (currentPosition === 'First Inversion') {
                newPosition = 'Second Inversion';
            } else if (currentPosition === 'Second Inversion') {
                newPosition = 'Third Inversion';
            } else if (currentPosition === 'Third Inversion') {
                newPosition = 'Root Position';
            } else {
                newPosition = 'Root Position';
            }
            
            // Update URL
            urlParams.set('position_select', newPosition);
            window.history.replaceState(null, '', window.location.pathname + '?' + urlParams.toString());
            
            // Update select element
            const positionSelect = document.getElementById('position_select');
            if (positionSelect) {
                for (let i = 0; i < positionSelect.options.length; i++) {
                    if (positionSelect.options[i].value === newPosition) {
                        positionSelect.selectedIndex = i;
                        break;
                    }
                }
                
                // Trigger change event
                positionSelect.dispatchEvent(new Event('change'));
            }
            
            // Update notes display
            if (typeof window.getTonesFromDataChords === 'function') {
                window.getTonesFromDataChords(newPosition, currentRange);
            }
            
            console.log(`Emergency navigation: ${currentPosition} -> ${newPosition}`);
        });
        
        console.log('Emergency cursor fix applied');
        return true;
    }
};

// Initialize on load
CursorDebug.init();

// Expose to global scope for console access
window.CursorDebug = CursorDebug;

console.log('Cursor Debug Utility loaded.');
console.log('To apply emergency fix, run: CursorDebug.fixCursors()');
