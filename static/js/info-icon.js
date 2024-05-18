document.addEventListener("DOMContentLoaded", function() {
    const infoToggle = document.getElementById('infoToggle');
    const analysisContainer = document.querySelector('.analysis_container');

    if (infoToggle && analysisContainer) {
        infoToggle.addEventListener('click', function() {
            // Toggle the display of the analysis container
            if (analysisContainer.style.display === 'none' || analysisContainer.style.display === '') {
                analysisContainer.style.display = 'block';
            } else {
                analysisContainer.style.display = 'none';
            }
        });
    }
});
