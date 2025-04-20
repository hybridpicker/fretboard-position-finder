// Enhanced Info Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
  // Get reference to the info toggle button and analysis container
  const infoToggle = document.getElementById('infoToggle');
  const analysisContainer = document.querySelector('.analysis_container');

  if (infoToggle && analysisContainer) {
    // Enhance the existing click handler to also toggle a visual class
    infoToggle.addEventListener('click', function() {
      // Toggle an active class on the info button for visual feedback
      infoToggle.classList.toggle('active');
    });
  }
});
