/**
 * Enhanced search functionality for fretboard position finder
 * Implementation of search via overlay
 */
document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality for existing search results
    const tabButtons = document.querySelectorAll('.tab-button');
    const resultSections = document.querySelectorAll('.result-section');
    
    if (tabButtons.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Remove active class from all tabs
                tabButtons.forEach(btn => btn.classList.remove('active'));
                
                // Hide all result sections
                resultSections.forEach(section => {
                    section.style.display = 'none';
                });
                
                // Add active class to clicked tab
                button.classList.add('active');
                
                // Show corresponding section
                const category = button.getAttribute('data-category');
                const sectionId = category + '-section';
                const section = document.getElementById(sectionId);
                
                if (section) {
                    section.style.display = 'block';
                }
            });
        });
    }
    
    // Search overlay toggle functionality
    const searchOverlay = document.getElementById('searchOverlay');
    const closeSearchOverlay = document.getElementById('closeSearchOverlay');
    const overlaySearchInput = document.getElementById('overlaySearchInput');
    
    // Function to open search overlay
    const openSearchOverlay = () => {
        if (searchOverlay) {
            searchOverlay.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
            
            // Focus the search input
            if (overlaySearchInput) {
                setTimeout(() => {
                    overlaySearchInput.focus();
                }, 100);
            }
        }
    };
    
    // Open search overlay buttons
    const openSearchButtons = document.querySelectorAll('.open-search-overlay, .global-search-button');
    if (openSearchButtons.length > 0 && searchOverlay) {
        openSearchButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                openSearchOverlay();
            });
        });
    }
    
    // Add event listener for the search icon
    const searchIconTrigger = document.getElementById('searchIconTrigger');
    if (searchIconTrigger && searchOverlay) {
        searchIconTrigger.addEventListener('click', function() {
            openSearchOverlay();
        });
    }
    
    // Global search input should also open overlay on focus
    const globalSearchInput = document.querySelector('.global-search-input');
    if (globalSearchInput) {
        globalSearchInput.addEventListener('focus', (e) => {
            e.preventDefault();
            openSearchOverlay();
        });
    }
    
    // Close search overlay functionality
    if (closeSearchOverlay && searchOverlay) {
        closeSearchOverlay.addEventListener('click', () => {
            searchOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
        
        // Also close on ESC key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
                searchOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
        
        // Close if clicked outside the content
        searchOverlay.addEventListener('click', function(e) {
            if (e.target === searchOverlay) {
                searchOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
    
    // Example search functionality in overlay
    const exampleSearches = document.querySelectorAll('.search-examples li');
    if (exampleSearches.length > 0) {
        exampleSearches.forEach(example => {
            example.addEventListener('click', () => {
                const searchQuery = example.getAttribute('data-search') || example.textContent.trim();
                
                // Get the search input value to send to autocomplete
                if (overlaySearchInput) {
                    overlaySearchInput.value = searchQuery;
                    // Trigger autocomplete search to find matching items
                    overlaySearchInput.dispatchEvent(new Event('input'));
                }
            });
        });
    }
    
    // Intercept search form submissions to redirect to fretboard directly
    const searchForms = document.querySelectorAll('.search-overlay-form, .search-form');
    if (searchForms.length > 0) {
        searchForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const query = form.querySelector('input[name="q"]').value.trim();
                
                if (query) {
                    // Fetch search results to get the first match
                    fetch(`/api/search/direct-match/?q=${encodeURIComponent(query)}`)
                        .then(response => {
                            // Log the raw text first
                            return response.text().then(text => {
                                console.log('Raw API response text:', text);
                                try {
                                    return JSON.parse(text); // Manually parse JSON
                                } catch (e) {
                                    console.error('Error parsing JSON:', e, text);
                                    return { url: null, debug: { error: 'JSON parse error' } }; // Return a default object on error
                                }
                            });
                        })
                        .then(data => {
                            console.log('Parsed data object:', data); // Log the whole parsed object
                            if (data && data.debug) {
                                console.log('Direct match API debug info:', data.debug); // Log the debug part separately
                            } else {
                                console.log('No data or data.debug found.');
                            }

                            if (data && data.url) {
                                // Redirect to the matched URL
                                window.location.href = data.url;
                            } else {
                                // Fall back to autocomplete if no direct match
                                fetch(`/api/search/autocomplete/?q=${encodeURIComponent(query)}`)
                                    .then(response => response.json())
                                    .then(autocompleteData => {
                                        if (autocompleteData.results && autocompleteData.results.length > 0) {
                                            // Use the first result's URL
                                            window.location.href = autocompleteData.results[0].url;
                                        } else {
                                            // If no matches, go to the homepage
                                            window.location.href = '/';
                                        }
                                    });
                            }
                        })
                        .catch(error => {
                            console.error('Error fetching or processing search results:', error);
                        });
                }
            });
        });
    }
    
    // Autocomplete functionality for overlay search
    setupAutocomplete(
        document.getElementById('overlaySearchInput'), 
        document.getElementById('overlayAutocompleteContainer')
    );
    
    // Also support normal search input if it exists (for search results page)
    setupAutocomplete(
        document.getElementById('searchInput'), 
        document.getElementById('autocompleteContainer')
    );
    
    function setupAutocomplete(searchInput, autocompleteContainer) {
        if (!searchInput || !autocompleteContainer) return;
        
        let debounceTimer;
        let selectedIndex = -1;
        let suggestions = [];
        
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value.trim();
                
                if (query.length < 2) {
                    autocompleteContainer.innerHTML = '';
                    autocompleteContainer.style.display = 'none';
                    return;
                }
                
                fetch(`/api/search/autocomplete/?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        suggestions = data.results;
                        renderSuggestions(searchInput, autocompleteContainer, suggestions, selectedIndex);
                    })
                    .catch(error => {
                        console.error('Error fetching autocomplete data:', error);
                    });
            }, 300); // 300ms debounce
        });
        
        searchInput.addEventListener('keydown', function(e) {
            if (!suggestions.length) return;
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, suggestions.length - 1);
                renderSuggestions(searchInput, autocompleteContainer, suggestions, selectedIndex);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                renderSuggestions(searchInput, autocompleteContainer, suggestions, selectedIndex);
            } else if (e.key === 'Enter' && selectedIndex >= 0) {
                e.preventDefault();
                selectSuggestion(searchInput, suggestions[selectedIndex], autocompleteContainer);
            } else if (e.key === 'Escape') {
                autocompleteContainer.innerHTML = '';
                autocompleteContainer.style.display = 'none';
                selectedIndex = -1;
            }
        });
        
        // Hide autocomplete on click outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !autocompleteContainer.contains(e.target)) {
                autocompleteContainer.innerHTML = '';
                autocompleteContainer.style.display = 'none';
                selectedIndex = -1;
            }
        });
    }
    
    function renderSuggestions(searchInput, autocompleteContainer, suggestions, selectedIndex) {
        autocompleteContainer.innerHTML = '';
        
        if (suggestions.length === 0) {
            autocompleteContainer.style.display = 'none';
            return;
        }
        
        const ul = document.createElement('ul');
        ul.className = 'autocomplete-list';
        
        suggestions.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = 'autocomplete-item';
            if (index === selectedIndex) {
                li.classList.add('selected');
            }
            
            // Create item name
            const nameSpan = document.createElement('span');
            nameSpan.className = 'item-name';
            nameSpan.textContent = item.name;
            
            // Create item type indicator
            const typeSpan = document.createElement('span');
            typeSpan.className = 'item-type ' + item.type;
            typeSpan.textContent = item.type;
            
            li.appendChild(nameSpan);
            li.appendChild(typeSpan);
            
            li.addEventListener('click', function() {
                selectSuggestion(searchInput, item, autocompleteContainer);
            });
            
            ul.appendChild(li);
        });
        
        autocompleteContainer.appendChild(ul);
        autocompleteContainer.style.display = 'block';
    }
    
    function selectSuggestion(searchInput, item, autocompleteContainer) {
        searchInput.value = item.name;
        autocompleteContainer.innerHTML = '';
        autocompleteContainer.style.display = 'none';
        
        // Log the URL before navigating
        console.log('[SEARCH_JS] Navigating to URL from suggestion:', item.url);
        
        // Navigate to the URL
        window.location.href = item.url;
    }
    
    // Initialize the correct tab on page load for search results page
    function initializeTabs() {
        // If we have a category filter specified, select that tab
        const urlParams = new URLSearchParams(window.location.search);
        
        const category = urlParams.get('category');
        
        if (category && tabButtons.length > 0) {
            const targetTab = Array.from(tabButtons).find(tab => 
                tab.getAttribute('data-category') === category
            );
            
            if (targetTab) {
                targetTab.click();
            }
        }
    }
    
    // Initialize everything
    initializeTabs();
});
