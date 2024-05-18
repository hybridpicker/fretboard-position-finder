// This function adds or removes the 'change' class and toggles the display of the overlay
function toggleOverlay() {
    var overlay = document.getElementById('overlayMenu');
    var icon = document.getElementById('hamburgerIcon');
    
    // Check if the overlay is currently displayed
    var isOverlayOpen = overlay.style.display === 'block';

    // Toggle the display of the overlay and the hamburger icon class
    overlay.style.display = isOverlayOpen ? 'none' : 'block';
    icon.classList.toggle('change');
    
    // Toggle the onclick event function
    icon.onclick = isOverlayOpen ? openOverlay : closeOverlay;
}

// The original openOverlay function used when the page is first loaded
function openOverlay() {
    // Log that the overlay is being opened
    document.getElementById('overlayMenu').style.display = 'block';
    document.getElementById('hamburgerIcon').classList.add('change');
    document.getElementById('hamburgerIcon').onclick = closeOverlay; // Set the handler to closeOverlay
}

// The closeOverlay function closes the overlay and changes the onclick event back to openOverlay
function closeOverlay() {
    // Log that the overlay is being closed
    document.getElementById('overlayMenu').style.display = 'none';
    document.getElementById('hamburgerIcon').classList.remove('change');
    document.getElementById('hamburgerIcon').onclick = openOverlay; // Set the handler back to openOverlay
}

// Add event listener when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set initial event handler for the hamburger icon
    var icon = document.getElementById('hamburgerIcon');
    icon.onclick = openOverlay;
});
