document.addEventListener("DOMContentLoaded", function() {
    const menuToggle = document.getElementById('menuToggle');
    const menuCheckbox = document.getElementById('menuCheckbox');
    const menu = document.getElementById('menu');
    
    if (menuToggle && menuCheckbox && menu) {
      console.log("Checkbox and menu found");
  
      menuToggle.addEventListener('click', function(event) {
        console.log("Menu toggle clicked");
        event.stopPropagation(); // Verhindert das Auslösen des Events auf dem Dokument
        menuCheckbox.checked = !menuCheckbox.checked; // Toggle checkbox state
        if (menuCheckbox.checked) {
          console.log("Checkbox is checked");
          menu.style.left = '0';
        } else {
          console.log("Checkbox is not checked");
          menu.style.left = '-300px';
        }
        console.log("Menu style left: ", menu.style.left);
      });
  
      document.addEventListener('click', function() {
        if (menuCheckbox.checked) {
          console.log("Click outside menu");
          menuCheckbox.checked = false;
          menu.style.left = '-300px';
        }
      });
    } else {
      console.log("Checkbox or menu not found");
    }
  });
  