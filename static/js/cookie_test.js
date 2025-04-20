/**
 * Cookie Test Script
 * This script is used to test cookie functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Create a test button
    const button = document.createElement('button');
    button.id = 'cookie-test-button';
    button.textContent = 'Test Cookie';
    button.style.position = 'fixed';
    button.style.bottom = '20px';
    button.style.right = '20px';
    button.style.zIndex = '9999';
    button.style.padding = '10px';
    button.style.backgroundColor = '#007bff';
    button.style.color = 'white';
    button.style.border = 'none';
    button.style.borderRadius = '5px';
    button.style.cursor = 'pointer';
    
    // Add click event
    button.addEventListener('click', function() {
        // Log current cookies
        console.log('All cookies:', document.cookie);
        
        // Test stringConfig cookie
        function getStringConfigCookie() {
            const name = "stringConfig=";
            const decodedCookie = decodeURIComponent(document.cookie);
            const cookieArray = decodedCookie.split(';');
            
            for (let i = 0; i < cookieArray.length; i++) {
                let cookie = cookieArray[i].trim();
                if (cookie.indexOf(name) === 0) {
                    return cookie.substring(name.length, cookie.length);
                }
            }
            
            return null;
        }
        
        // Get current string config
        const currentConfig = getStringConfigCookie();
        console.log('Current string config from cookie:', currentConfig);
        console.log('Current string config from localStorage:', localStorage.getItem('stringConfig'));
        
        // Toggle config
        const newConfig = currentConfig === 'eight-string' ? 'six-string' : 'eight-string';
        
        // Set the cookie
        const d = new Date();
        d.setTime(d.getTime() + (30 * 24 * 60 * 60 * 1000)); // 30 days
        const expires = "expires=" + d.toUTCString();
        document.cookie = "stringConfig=" + newConfig + ";" + expires + ";path=/;SameSite=Lax";
        
        // Set localStorage
        localStorage.setItem('stringConfig', newConfig);
        
        // Log after setting
        console.log('Set config to:', newConfig);
        console.log('Cookies after setting:', document.cookie);
        console.log('localStorage after setting:', localStorage.getItem('stringConfig'));
        
        // Create alert
        alert(`String config changed to: ${newConfig}\nCheck console for details.`);
        
        // Reload the page to apply changes
        if (confirm('Reload page to apply changes?')) {
            location.reload();
        }
    });
    
    // Add to the document
    document.body.appendChild(button);
    
    // Log all cookies on load
    console.log('All cookies on page load:', document.cookie);
    console.log('String config cookie on load:', getStringConfigCookie());
    console.log('String config in localStorage on load:', localStorage.getItem('stringConfig'));
});
