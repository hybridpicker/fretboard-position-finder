/**
 * Landing Page Interaction Scripts
 * Handles button animations and search functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Animation for all buttons
    const allButtons = document.querySelectorAll('.main-button-primary, .main-button-settings, .main-button-about');
    
    allButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 6px 12px rgba(0,0,0,0.15)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
        
        button.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(-1px)';
            this.style.boxShadow = '0 3px 6px rgba(0,0,0,0.1)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 6px 12px rgba(0,0,0,0.15)';
        });
    });
    
    // Handle settings button - open overlay menu
    const settingsButton = document.getElementById('mainSettingsButton');
    if (settingsButton) {
        settingsButton.addEventListener('click', function() {
            // Check if overlay menu functions are available
            if (typeof window.openMenu === 'function' && typeof window.navigateToMode === 'function') {
                // First open the menu
                window.openMenu();
                
                // Then navigate to settings after a small delay to ensure menu is visible
                setTimeout(() => {
                    const settingsContainer = document.getElementById('settingsContainer');
                    const settingsStep = document.getElementById('settingsStep');
                    
                    if (settingsContainer && settingsStep) {
                        window.navigateToMode('settings', settingsContainer, settingsStep);
                    }
                }, 100);
            }
        });
    }
    
    // Handle search examples
    const searchExamples = document.querySelectorAll('.main-search-example');
    const searchInput = document.querySelector('.main-search-input');
    const searchForm = document.querySelector('.main-search-form');
    
    searchExamples.forEach(example => {
        example.addEventListener('click', function() {
            const searchTerm = this.getAttribute('data-search');
            if (searchInput && searchTerm) {
                searchInput.value = searchTerm;
                // Submit the form
                if (searchForm) {
                    searchForm.submit();
                }
            }
        });
    });
    
    // Focus animation for search input
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.style.borderColor = '#3d7876';
            this.style.boxShadow = '0 0 0 3px rgba(61, 120, 118, 0.2)';
        });
        
        searchInput.addEventListener('blur', function() {
            this.style.borderColor = '';
            this.style.boxShadow = '';
        });
    }
});

// Make these functions available globally for other scripts to use
window.openMenu = function() {
    const unifiedMenu = document.getElementById('unifiedOverlayMenu');
    if (unifiedMenu) {
        // Reset display properties
        unifiedMenu.style.display = 'none';
        unifiedMenu.style.opacity = '0';
        
        // Reset active steps and prepare the menu
        if (typeof window.resetActiveSteps === 'function') {
            window.resetActiveSteps();
        }
        
        const initialStep = document.getElementById('initialStep');
        if (initialStep) {
            initialStep.style.display = 'block';
            initialStep.classList.add('active-step');
        }
        
        // Show the menu
        unifiedMenu.style.display = 'flex';
        
        // Set opacity after a small delay to trigger transition
        setTimeout(() => {
            unifiedMenu.style.opacity = '1';
        }, 10);
    }
};

window.navigateToMode = function(mode, containerToShow, firstStepToShow) {
    const initialStep = document.getElementById('initialStep');
    const scaleStepsContainer = document.getElementById('scaleStepsContainer');
    const arpeggioStepsContainer = document.getElementById('arpeggioStepsContainer');
    const chordStepsContainer = document.getElementById('chordStepsContainer');
    const settingsContainer = document.getElementById('settingsContainer');
    
    // Hide all steps first
    if (initialStep) initialStep.style.display = 'none';
    if (scaleStepsContainer) scaleStepsContainer.style.display = 'none';
    if (arpeggioStepsContainer) arpeggioStepsContainer.style.display = 'none';
    if (chordStepsContainer) chordStepsContainer.style.display = 'none';
    if (settingsContainer) settingsContainer.style.display = 'none';
    
    // Show the target container
    if (containerToShow) containerToShow.style.display = 'block';
    
    // Show the first step in the container
    if (firstStepToShow) {
        firstStepToShow.style.display = 'block';
        firstStepToShow.classList.add('active-step');
    }
};
