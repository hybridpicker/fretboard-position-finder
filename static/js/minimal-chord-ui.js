/**
 * Chord Menu Match Arpeggios
 * Makes the chord page match arpeggios page exactly
 */
document.addEventListener('DOMContentLoaded', function() {
    // Only apply to the chord page (using models_select instead of URL path)
    const urlParams = new URLSearchParams(window.location.search);
    const modelSelect = urlParams.get('models_select');
    
    if (modelSelect === '3' || window.location.pathname.includes('/chords')) {
        
        // Add the CSS stylesheet that matches arpeggios styling
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = '/static/css/minimal-chord-ui.css';
        document.head.appendChild(link);
        
        // Set up the hamburger menu toggle exactly like arpeggios page
        setupHamburgerMenu();
        
        // Fix select element attributes to match
        fixSelectElements();
        
        // Fix button styling
        fixButtonStyling();
    }
});

/**
 * Sets up the hamburger menu toggle like on the arpeggios page
 */
function setupHamburgerMenu() {
    const hamburgerIcon = document.getElementById('hamburgerIcon');
    const overlay = document.getElementById('overlayMenu');
    
    if (!hamburgerIcon || !overlay) return;
    
    // Add click event to toggle the menu
    hamburgerIcon.addEventListener('click', function() {
        this.classList.toggle('open');
        
        if (this.classList.contains('open')) {
            overlay.style.height = '100%';
        } else {
            overlay.style.height = '0%';
        }
    });
    
    // Close menu when clicking outside
    overlay.addEventListener('click', function(e) {
        if (e.target === this) {
            hamburgerIcon.classList.remove('open');
            overlay.style.height = '0%';
        }
    });
    
    // Ensure the overlay starts closed
    overlay.style.height = '0%';
}

/**
 * Fixes select elements to match arpeggios page exactly
 */
function fixSelectElements() {
    // Fix the form structure
    const form = document.getElementById('fretboard_form');
    if (!form) return;
    
    // Get all parent divs of selects
    const selectParents = form.querySelectorAll('.sfbsf, .sfbsfnr, .sfbsfpos, .range-selection, .inversion-selection');
    
    // Update classes to match arpeggios form - make all of them look consistent
    selectParents.forEach(parent => {
        if (parent.classList.contains('sfbsfnr') || parent.classList.contains('range-selection')) {
            parent.className = 'sfbsfnos'; // Match arpeggios class
        } else if (parent.classList.contains('sfbsfpos') || parent.classList.contains('inversion-selection')) {
            parent.className = 'sfbsfpos'; // Match arpeggios class
        } else if (parent.id === 'catsfbsf') {
            parent.className = 'sfbsf';
            parent.id = 'catsfbsf';
        } else {
            parent.className = 'sfbsf'; // Default class
        }
        
        // Reset all inline styles
        parent.removeAttribute('style');
        
        // Remove any child elements that don't exist in arpeggios page
        const infoIcons = parent.querySelectorAll('.range-info-icon, .inversion-info-icon');
        infoIcons.forEach(icon => icon.remove());
        
        const navigation = parent.querySelector('.inversion-navigation');
        if (navigation) navigation.remove();
    });
    
    // Update select IDs and names to match arpeggios
    const typeSelect = form.querySelector('#type_options_select');
    if (typeSelect) {
        typeSelect.name = 'notes_options_select';
        typeSelect.id = 'notes_options_select';
    }
    
    const chordSelect = form.querySelector('#chords_options_select');
    if (chordSelect) {
        chordSelect.name = 'notes_options_select';
        chordSelect.id = 'notes_options_select';
    }
    
    const rangeSelect = form.querySelector('#note_range');
    if (rangeSelect) {
        rangeSelect.name = 'notes_options_select';
        rangeSelect.id = 'notes_options_select';
    }
    
    // Update position select to match arpeggios formatting
    const positionSelect = form.querySelector('#position_select');
    if (positionSelect) {
        // Make sure it has the right name and ID
        positionSelect.name = 'position_select';
        positionSelect.id = 'position_select';
        
        // Update each option text
        Array.from(positionSelect.options).forEach(option => {
            if (option.value === '0' || option.value === 'Basic Position') {
                option.value = '0';
                option.text = 'All Notes';
            } else if (!option.text.includes('Position:')) {
                option.text = 'Position: ' + option.text;
            }
        });
    }
    
    // Remove any extra select elements that aren't in arpeggios page
    const selects = form.querySelectorAll('select');
    selects.forEach(select => {
        // If it's not one of the recognized selects, remove it
        if (!['models_select', 'root', 'notes_options_select', 'position_select'].includes(select.name)) {
            const parent = select.parentElement;
            if (parent) parent.remove();
        }
    });
}

/**
 * Fixes button styling to match arpeggios page
 */
function fixButtonStyling() {
    // Get the tension button and update styling
    const tensionButton = document.getElementById('show_tension_button');
    if (tensionButton) {
        tensionButton.style.width = '8em';
        tensionButton.style.backgroundColor = '#007bff';
        tensionButton.style.color = 'white';
        tensionButton.style.border = 'none';
        tensionButton.style.borderRadius = '4px';
        tensionButton.style.padding = '5px 10px';
        tensionButton.style.cursor = 'pointer';
    }
    
    // Fix cursor styling
    const leftCursor = document.querySelector('.left-cursor');
    const rightCursor = document.querySelector('.right-cursor');
    
    if (leftCursor && rightCursor) {
        leftCursor.style.display = 'inline-block';
        rightCursor.style.display = 'inline-block';
    }
}
