/**
 * Unified Menu Initialization Script
 * Ensures proper styling and behavior of the improved overlay menu
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize menu display properties
    const unifiedMenu = document.getElementById('unifiedOverlayMenu');
    if (unifiedMenu) {
        // Set initial display properties
        unifiedMenu.style.display = 'none';
        unifiedMenu.style.opacity = '0';
        
        // Setup CSS variables to match the site color scheme
        const root = document.documentElement;
        
        // Get computed styles from current theme
        const computedStyle = window.getComputedStyle(document.documentElement);
        
        // Apply color scheme to menu CSS variables - with light theme colors
        root.style.setProperty('--menu-bg-color', '#f8f9fa');
        root.style.setProperty('--menu-text-color', '#333333');
        root.style.setProperty('--menu-text-secondary', '#555555');
        
        // Button colors - use teal colors from your scheme
        root.style.setProperty('--button-bg', computedStyle.getPropertyValue('--color-teal-medium'));
        root.style.setProperty('--button-bg-hover', computedStyle.getPropertyValue('--color-teal-dark'));
        root.style.setProperty('--button-bg-selected', computedStyle.getPropertyValue('--color-teal-light'));
        root.style.setProperty('--button-text', '#ffffff');
        
        // Accent colors for categories - use your existing color palette
        root.style.setProperty('--root-accent', computedStyle.getPropertyValue('--color-purple-medium'));
        root.style.setProperty('--scale-accent', computedStyle.getPropertyValue('--color-teal-medium'));
        root.style.setProperty('--chord-accent', computedStyle.getPropertyValue('--color-teal-dark'));
        root.style.setProperty('--arpeggio-accent', computedStyle.getPropertyValue('--color-teal-light'));
        root.style.setProperty('--position-accent', computedStyle.getPropertyValue('--color-yellow-medium'));
        
        // Fix any initially displayed menu items
        const activeSteps = unifiedMenu.querySelectorAll('.step.active-step');
        activeSteps.forEach(step => {
            step.style.display = 'block';
        });
        
        // Ensure the grid items have consistent styling
        const gridItems = unifiedMenu.querySelectorAll('.grid-item');
        gridItems.forEach(item => {
            // Add appropriate class based on context
            const parentId = item.closest('.step')?.id || '';
            
            if (parentId.includes('RootStep')) {
                item.classList.add('root-item');
            } else if (parentId.includes('TypeStep') && parentId.includes('chord')) {
                item.classList.add('chord-type-item');
            } else if (parentId.includes('TypeStep') && parentId.includes('scale')) {
                item.classList.add('scale-type-item');
            } else if (parentId.includes('TypeStep') && parentId.includes('arpeggio')) {
                item.classList.add('arpeggio-type-item');
            } else if (parentId.includes('PositionStep')) {
                item.classList.add('position-item');
            } else if (parentId.includes('RangeStep')) {
                item.classList.add('range-item');
            } else if (parentId.includes('NameStep') && parentId.includes('chord')) {
                item.classList.add('chord-name-item');
            }
        });
    }
    
    // Force hide the menu on initial load (with a small delay to ensure DOM is ready)
    setTimeout(function() {
        if (unifiedMenu) {
            unifiedMenu.style.display = 'none';
            unifiedMenu.style.opacity = '0';
        }
    }, 100);
    
    // Add keyboard support for closing the menu with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const menu = document.getElementById('unifiedOverlayMenu');
            if (menu && (menu.style.display === 'flex' || menu.style.display === 'block')) {
                // Call close function if it exists
                if (typeof closeMenu === 'function') {
                    closeMenu();
                } else {
                    // Fallback close behavior
                    menu.style.opacity = '0';
                    setTimeout(() => {
                        menu.style.display = 'none';
                    }, 300);
                }
            }
        }
    });
    
    // Fix search box behavior
    const searchForm = document.querySelector('.overlay-search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchInput = document.getElementById('overlaySearchInput');
            if (searchInput && searchInput.value.trim()) {
                // Process search query
                const query = searchInput.value.trim().toLowerCase();
                
                // Handle search query parsing
                let searchParams = {};
                
                // Parse for scale queries (e.g., "C major scale")
                if (query.includes('scale')) {
                    const parts = query.split(' ');
                    if (parts.length >= 2) {
                        searchParams.mode = 'scale';
                        searchParams.root = parts[0].toUpperCase();
                        searchParams.type = parts[1];
                    }
                }
                // Parse for chord queries (e.g., "Em7 chord")
                else if (query.includes('chord')) {
                    const parts = query.replace(' chord', '').trim();
                    searchParams.mode = 'chord';
                    // Extract root and type from chord name (e.g., Em7 -> E minor 7)
                    const match = parts.match(/^([A-Ga-g][#b]?)(.*)$/);
                    if (match) {
                        searchParams.root = match[1].toUpperCase();
                        searchParams.type = match[2] || 'Major';
                    }
                }
                // Parse for arpeggio queries (e.g., "Dmaj7 arpeggio")
                else if (query.includes('arpeggio')) {
                    const parts = query.replace(' arpeggio', '').trim();
                    searchParams.mode = 'arpeggio';
                    // Extract root and type from arpeggio name
                    const match = parts.match(/^([A-Ga-g][#b]?)(.*)$/);
                    if (match) {
                        searchParams.root = match[1].toUpperCase();
                        searchParams.type = match[2] || 'Major';
                    }
                }
                
                // Handle the search (for now, just log the parsed params)
                console.log('Search params:', searchParams);
                
                // You can implement actual search redirect or action here
                // ...
            }
        });
        
        // Make search examples clickable
        const searchExamples = document.querySelectorAll('.search-examples li');
        searchExamples.forEach(example => {
            example.addEventListener('click', function() {
                const searchTerm = this.getAttribute('data-search');
                const searchInput = document.getElementById('overlaySearchInput');
                if (searchInput && searchTerm) {
                    searchInput.value = searchTerm;
                    // Trigger form submission
                    searchForm.dispatchEvent(new Event('submit'));
                }
            });
        });
    }
});
