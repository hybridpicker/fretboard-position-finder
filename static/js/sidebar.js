document.addEventListener("DOMContentLoaded", function() {
    const menuToggle = document.getElementById('menuToggle');
    const menuCheckbox = document.getElementById('menuCheckbox');
    const menu = document.getElementById('menu');
    const leftCursor = document.querySelector('.left-cursor');
    
    if (menuToggle && menuCheckbox && menu) {
        menuToggle.addEventListener('click', function(event) {
            event.stopPropagation(); // Prevent the event from triggering on the document
            menuCheckbox.checked = !menuCheckbox.checked; // Toggle checkbox state
            if (menuCheckbox.checked) {
                menu.style.left = '0';
                leftCursor.style.zIndex = 'unset';
            } else {
                menu.style.left = '-300px';
                leftCursor.style.zIndex = '10';
            }
        });

        document.addEventListener('click', function(event) {
            // Only close the menu if clicking outside of it
            if (menuCheckbox.checked && !menuToggle.contains(event.target) && !menu.contains(event.target)) {
                menuCheckbox.checked = false;
                menu.style.left = '-300px';
                leftCursor.style.zIndex = '10';
            }
        });
    }
});
