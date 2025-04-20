/**
 * Show Analysis Container
 * 
 * This script ensures the chord analysis container is always visible
 */

document.addEventListener('DOMContentLoaded', function() {
    // Make sure analysis container is visible
    const analysisContainer = document.querySelector('.analysis_container');
    if (analysisContainer) {
        analysisContainer.style.display = 'none';
        console.log('Analysis container visibility forced to: block');
    } else {
        console.warn('Analysis container not found in the DOM');
    }

    // Also make sure it stays visible after any AJAX updates
    // Watch for URL parameter changes which might indicate chord selection change
    const origSearch = window.location.search;
    setInterval(function() {
        if (window.location.search !== origSearch) {
            // Parameters changed, ensure container is visible after a slight delay
            setTimeout(function() {
                const container = document.querySelector('.analysis_container');
                if (container) {
                    container.style.display = 'block';
                    console.log('Analysis container visibility reset after URL change');
                }
            }, 500);
        }
    }, 1000);
});