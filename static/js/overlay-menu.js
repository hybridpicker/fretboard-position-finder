document.addEventListener("DOMContentLoaded", function() {
    const overlayToggle = document.getElementById('overlayToggle');
    const overlayMenu = document.getElementById('overlayMenu');
    const closeOverlay = document.getElementById('closeOverlay');

    if (overlayToggle && overlayMenu && closeOverlay) {
        // Ensure the overlay menu is hidden initially
        overlayMenu.style.display = 'none';
        
        overlayToggle.addEventListener('click', function() {
            overlayMenu.style.display = 'flex'; // Show overlay menu when the toggle is clicked
        });

        closeOverlay.addEventListener('click', function() {
            overlayMenu.style.display = 'none'; // Hide overlay menu when the close button is clicked
        });

        // Optional: Close overlay when clicking outside the content
        overlayMenu.addEventListener('click', function(event) {
            if (event.target === overlayMenu) {
                overlayMenu.style.display = 'none';
            }
        });
    }
});
