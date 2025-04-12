/**
 * Integration between landing page buttons and overlay menu
 * Provides global functions to open the menu and navigate to specific sections
 */

// Make sure these functions are available globally
window.openMenu = function() {
    const unifiedMenu = document.getElementById('unifiedOverlayMenu');
    if (unifiedMenu) {
        // Reset display properties forcibly
        unifiedMenu.style.display = 'none';
        unifiedMenu.style.opacity = '0';
        
        // Reset active steps
        document.querySelectorAll('#unifiedOverlayMenu .step.active-step').forEach(step => {
            if (step.id !== 'initialStep') {
                step.classList.remove('active-step');
                step.style.display = 'none';
            }
        });
        
        document.querySelectorAll('#unifiedOverlayMenu .steps-container').forEach(container => {
            container.style.display = 'none';
        });
        
        // Show the initial step
        const initialStep = document.getElementById('initialStep');
        if (initialStep) {
            initialStep.classList.add('active-step');
            initialStep.style.display = 'block';
        }
        
        // Display the menu
        unifiedMenu.style.display = 'flex';
        
        // Set opacity with small delay to ensure transition works
        setTimeout(() => {
            unifiedMenu.style.opacity = '1';
        }, 10);
    }
};

window.navigateToMode = function(mode, containerToShow, firstStepToShow) {
    // First hide initial step
    const initialStep = document.getElementById('initialStep');
    if (initialStep) {
        initialStep.classList.remove('active-step');
        initialStep.style.display = 'none';
    }
    
    // Hide all containers
    document.querySelectorAll('#unifiedOverlayMenu .steps-container').forEach(container => {
        container.style.display = 'none';
    });
    
    // Show the selected container
    if (containerToShow) {
        containerToShow.style.display = 'block';
    }
    
    // Show the first step of the container
    if (firstStepToShow) {
        document.querySelectorAll('#unifiedOverlayMenu .step.active-step').forEach(step => {
            step.classList.remove('active-step');
            step.style.display = 'none';
        });
        
        firstStepToShow.classList.add('active-step');
        firstStepToShow.style.display = 'block';
    }
};

// Handle main settings button click
document.addEventListener('DOMContentLoaded', function() {
    const mainSettingsButton = document.getElementById('mainSettingsButton');
    if (mainSettingsButton) {
        mainSettingsButton.addEventListener('click', function() {
            openMenu();
            
            // Allow the menu to open before navigating
            setTimeout(() => {
                const settingsContainer = document.getElementById('settingsContainer');
                const settingsStep = document.getElementById('settingsStep');
                if (settingsContainer && settingsStep) {
                    navigateToMode('settings', settingsContainer, settingsStep);
                }
            }, 100);
        });
    }
});
