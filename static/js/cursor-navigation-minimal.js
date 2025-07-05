/**
 * Minimalist Cursor Navigation System v2.2
 * Enhanced with comprehensive debugging for development environments
 */

(function() {
    'use strict';

    // Global state object
    const CursorNav = {
        mode: null,          // 'scales' or 'chords'
        position: 0,         // Current position/inversion
        maxPosition: 6,      // Maximum position for scales
        initialized: false,
        debug: false,        // Enable debug logging
        version: '2.2',      // Version for debugging
        
        // Core navigation functions
        navigate: {
            scales: null,
            chords: null
        },
        
        // Debug statistics
        stats: {
            navigationCount: 0,
            leftClicks: 0,
            rightClicks: 0,
            keyboardNavs: 0,
            errors: 0,
            initTime: null,
            lastNavTime: null
        }
    };

    // Enhanced logging utility with levels and styling
    const Logger = {
        // Check if in development environment
        isDev: function() {
            const hostname = window.location.hostname;
            const pathname = window.location.pathname;
            const search = window.location.search;
            
            return hostname === 'localhost' || 
                   hostname === '127.0.0.1' || 
                   hostname.includes('.local') ||
                   pathname.includes('devel') ||
                   search.includes('debug=true') ||
                   search.includes('debug=1') ||
                   CursorNav.debug === true;
        },
        
        // Styled console output
        log: function(level, ...args) {
            if (!this.isDev()) return;
            
            const timestamp = new Date().toISOString().substr(11, 12);
            const prefix = `[CursorNav ${timestamp}]`;
            
            switch(level) {
                case 'info':
                    console.log(`%c${prefix}`, 'color: #0066cc', ...args);
                    break;
                case 'success':
                    console.log(`%c${prefix}`, 'color: #00aa00; font-weight: bold', ...args);
                    break;
                case 'warn':
                    console.warn(`%c${prefix}`, 'color: #ff6600', ...args);
                    break;
                case 'error':
                    console.error(`%c${prefix}`, 'color: #ff0000; font-weight: bold', ...args);
                    CursorNav.stats.errors++;
                    break;
                case 'debug':
                    console.log(`%c${prefix}`, 'color: #666666; font-style: italic', ...args);
                    break;
                case 'group':
                    console.group(`%c${prefix} ${args[0]}`, 'color: #0066cc; font-weight: bold');
                    break;
                case 'groupEnd':
                    console.groupEnd();
                    break;
                case 'table':
                    console.log(`%c${prefix}`, 'color: #0066cc', args[0]);
                    console.table(args[1]);
                    break;
            }
        },
        
        // Convenience methods
        info: function(...args) { this.log('info', ...args); },
        success: function(...args) { this.log('success', ...args); },
        warn: function(...args) { this.log('warn', ...args); },
        error: function(...args) { this.log('error', ...args); },
        debug: function(...args) { this.log('debug', ...args); },
        group: function(name) { this.log('group', name); },
        groupEnd: function() { this.log('groupEnd'); },
        table: function(label, data) { this.log('table', label, data); }
    };

    // Alias for backward compatibility
    const log = Logger.info.bind(Logger);

    // Utility functions with enhanced logging
    const Utils = {
        // Get URL parameter
        getParam: function(name) {
            try {
                const params = new URLSearchParams(window.location.search);
                const value = params.get(name);
                Logger.debug(`URL param '${name}' = '${value}'`);
                return value;
            } catch (e) {
                Logger.error('Error getting URL param:', e);
                return null;
            }
        },

        // Update URL parameter
        setParam: function(name, value) {
            try {
                const params = new URLSearchParams(window.location.search);
                const oldValue = params.get(name);
                params.set(name, value);
                const newUrl = window.location.pathname + '?' + params.toString();
                window.history.replaceState(null, '', newUrl);
                
                Logger.debug(`URL param updated: '${name}' from '${oldValue}' to '${value}'`);
                return true;
            } catch (e) {
                Logger.error('Error setting URL param:', e);
                return false;
            }
        },

        // Detect page mode with detailed logging
        detectMode: function() {
            Logger.group('Mode Detection');
            
            // Priority 1: Check URL patterns
            const url = window.location.href.toLowerCase();
            const pathname = window.location.pathname.toLowerCase();
            
            Logger.debug('URL:', url);
            Logger.debug('Pathname:', pathname);
            
            if (url.includes('chord') || pathname.includes('chord')) {
                Logger.success('Mode detected from URL: chords');
                Logger.groupEnd();
                return 'chords';
            }
            if (url.includes('scale') || url.includes('arpeggio') || 
                pathname.includes('scale') || pathname.includes('arpeggio')) {
                Logger.success('Mode detected from URL: scales');
                Logger.groupEnd();
                return 'scales';
            }
            
            // Priority 2: Check for data objects
            Logger.debug('Checking data objects...');
            if (typeof window.voicing_data !== 'undefined' && window.voicing_data !== null) {
                Logger.info('Found voicing_data:', Object.keys(window.voicing_data || {}));
                Logger.success('Mode detected from voicing_data: chords');
                Logger.groupEnd();
                return 'chords';
            }
            if (typeof window.scale_data !== 'undefined' && window.scale_data !== null) {
                Logger.info('Found scale_data:', Object.keys(window.scale_data || {}));
                Logger.success('Mode detected from scale_data: scales');
                Logger.groupEnd();
                return 'scales';
            }
            
            // Priority 3: Check DOM elements
            Logger.debug('Checking DOM elements...');
            const hasChordElements = document.querySelector('.chord-type, .chord-root, #chords_options_select') !== null;
            const hasScaleElements = document.querySelector('.scale-name, .arpeggio-name, .scale-root') !== null;
            
            Logger.debug('Has chord elements:', hasChordElements);
            Logger.debug('Has scale elements:', hasScaleElements);
            
            if (hasChordElements && !hasScaleElements) {
                Logger.success('Mode detected from DOM: chords');
                Logger.groupEnd();
                return 'chords';
            }
            if (hasScaleElements && !hasChordElements) {
                Logger.success('Mode detected from DOM: scales');
                Logger.groupEnd();
                return 'scales';
            }
            
            Logger.warn('Could not detect mode');
            Logger.groupEnd();
            return null;
        },

        // Get max position for scales with detailed logging
        getMaxScalePosition: function() {
            Logger.group('Detecting Max Scale Position');
            
            const select = document.getElementById('position_select');
            if (!select || select.options.length === 0) {
                Logger.warn('No position_select found, using default max position');
                Logger.groupEnd();
                return 6;
            }
            
            Logger.debug(`Found position_select with ${select.options.length} options`);
            
            let max = 0;
            const positions = [];
            
            for (let i = 0; i < select.options.length; i++) {
                const val = parseInt(select.options[i].value);
                const text = select.options[i].text;
                positions.push({ value: select.options[i].value, text, parsed: val });
                
                if (!isNaN(val) && val > max) {
                    max = val;
                }
            }
            
            Logger.table('Position Options', positions);
            
            // Validate reasonable bounds
            if (max < 1) {
                max = 6;  // Default if no valid positions found
                Logger.warn('No valid positions found, using default:', max);
            }
            if (max > 20) {
                Logger.warn('Unusually high max position detected:', max);
                max = 20; // Reasonable upper limit
            }
            
            Logger.success('Max position detected:', max);
            Logger.groupEnd();
            return max;
        },

        // Get chord inversion info with detailed logging
        getChordInfo: function() {
            Logger.group('Getting Chord Info');
            
            const select = document.getElementById('chords_options_select');
            let chordType = 'Major'; // Default
            
            if (select && select.value) {
                chordType = select.value;
                Logger.debug('Chord type from select:', chordType);
            } else {
                // Try to get from URL
                const urlChordType = Utils.getParam('chords_options_select');
                if (urlChordType) {
                    chordType = urlChordType;
                    Logger.debug('Chord type from URL:', chordType);
                } else {
                    Logger.debug('Using default chord type:', chordType);
                }
            }
            
            const isFourNote = chordType.includes('7') || chordType.includes('9') || 
                              chordType.includes('11') || chordType.includes('13') ||
                              chordType.toLowerCase().includes('seventh');
            
            const result = {
                type: chordType,
                maxInversion: isFourNote ? 3 : 2,
                isFourNote: isFourNote
            };
            
            Logger.info('Chord info:', result);
            Logger.groupEnd();
            return result;
        }
    };

    // Navigation handlers with enhanced logging
    const Handlers = {
        // Handle scale navigation
        scales: function(direction) {
            const startPos = CursorNav.position;
            const newPosition = CursorNav.position + direction;
            
            Logger.group(`Scale Navigation ${direction > 0 ? 'Right' : 'Left'}`);
            Logger.debug('Current position:', startPos);
            Logger.debug('Target position:', newPosition);
            Logger.debug('Max position:', CursorNav.maxPosition);
            
            // Boundary check
            if (newPosition < 0 || newPosition > CursorNav.maxPosition) {
                Logger.warn('Navigation blocked at boundary');
                Logger.debug(`Attempted: ${startPos} → ${newPosition}`);
                Logger.groupEnd();
                return false;
            }
            
            CursorNav.position = newPosition;
            Logger.success(`Position updated: ${startPos} → ${newPosition}`);
            
            // Update UI
            const select = document.getElementById('position_select');
            if (select) {
                const oldValue = select.value;
                select.value = String(newPosition);
                
                // Verify the option exists
                if (select.value !== String(newPosition)) {
                    Logger.warn('Position option not found, searching for closest match...');
                    // Find closest valid option
                    let found = false;
                    for (let i = 0; i < select.options.length; i++) {
                        if (select.options[i].value === String(newPosition)) {
                            select.selectedIndex = i;
                            found = true;
                            Logger.success('Found matching option at index:', i);
                            break;
                        }
                    }
                    if (!found) {
                        Logger.error('No matching option found for position:', newPosition);
                    }
                } else {
                    Logger.debug('Select updated successfully');
                }
                
                // Trigger change event only if value actually changed
                if (oldValue !== select.value) {
                    Logger.debug('Dispatching change event');
                    const event = new Event('change', { bubbles: true });
                    select.dispatchEvent(event);
                } else {
                    Logger.debug('Value unchanged, skipping change event');
                }
            } else {
                Logger.warn('position_select element not found');
            }
            
            // Update URL
            if (Utils.setParam('position_select', newPosition)) {
                Logger.debug('URL parameter updated');
            }
            
            // Call the scale update function if available
            if (typeof CursorNav.navigate.scales === 'function') {
                try {
                    Logger.debug('Calling scale navigation function...');
                    CursorNav.navigate.scales(String(newPosition));
                    Logger.success('Scale navigation function called successfully');
                } catch (e) {
                    Logger.error('Error calling scale navigation function:', e);
                }
            } else {
                Logger.warn('Scale navigation function not available');
                Logger.debug('Expected function at: window.getTonesFromDataScales');
                
                // Try direct call if the function exists
                if (typeof window.getTonesFromDataScales === 'function') {
                    Logger.debug('Calling getTonesFromDataScales directly...');
                    window.getTonesFromDataScales(String(newPosition));
                }
            }
            
            Logger.groupEnd();
            return true;
        },

        // Handle chord navigation
        chords: function(direction) {
            Logger.group(`Chord Navigation ${direction > 0 ? 'Right' : 'Left'}`);
            
            const info = Utils.getChordInfo();
            const startPos = CursorNav.position;
            let newPosition = CursorNav.position + direction;
            
            Logger.debug('Current inversion:', startPos);
            Logger.debug('Direction:', direction);
            Logger.debug('Max inversion:', info.maxInversion);
            
            // Wrap around
            if (newPosition < 0) {
                newPosition = info.maxInversion;
                Logger.debug('Wrapping to max inversion:', newPosition);
            }
            if (newPosition > info.maxInversion) {
                newPosition = 0;
                Logger.debug('Wrapping to root position');
            }
            
            CursorNav.position = newPosition;
            Logger.success(`Inversion updated: ${startPos} → ${newPosition}`);
            
            // Convert to position name
            const positionNames = ['Root Position', 'First Inversion', 'Second Inversion', 'Third Inversion'];
            const positionName = positionNames[newPosition] || 'Root Position';
            Logger.debug('Position name:', positionName);
            
            // Update UI
            const select = document.getElementById('position_select');
            if (select) {
                let found = false;
                const oldIndex = select.selectedIndex;
                
                Logger.debug(`Searching for position in ${select.options.length} options...`);
                
                // Log all options for debugging
                const options = [];
                for (let i = 0; i < select.options.length; i++) {
                    options.push({
                        index: i,
                        value: select.options[i].value,
                        text: select.options[i].text
                    });
                }
                Logger.table('Available Options', options);
                
                // Try exact match first
                for (let i = 0; i < select.options.length; i++) {
                    const optionValue = select.options[i].value;
                    if (optionValue === positionName || 
                        (positionName === 'Root Position' && 
                         (optionValue === 'Basic Position' || optionValue === 'Root'))) {
                        select.selectedIndex = i;
                        found = true;
                        Logger.success(`Found matching option at index ${i}: "${optionValue}"`);
                        break;
                    }
                }
                
                if (!found) {
                    Logger.error('Could not find position option for:', positionName);
                }
                
                // Trigger change event only if selection changed
                if (oldIndex !== select.selectedIndex) {
                    Logger.debug('Select index changed, dispatching event');
                    const event = new Event('change', { bubbles: true });
                    select.dispatchEvent(event);
                } else {
                    Logger.debug('Select index unchanged');
                }
            } else {
                Logger.warn('position_select element not found');
            }
            
            // Update URL
            if (Utils.setParam('position_select', positionName)) {
                Logger.debug('URL parameter updated');
            }
            
            // Get range for chord update
            const range = Utils.getParam('note_range') || 
                         document.getElementById('note_range')?.value || 
                         'e - g';
                         
            Logger.debug('Note range:', range);
            
            // Call the chord update function if available
            if (typeof CursorNav.navigate.chords === 'function') {
                try {
                    Logger.debug('Calling chord navigation function...');
                    Logger.debug(`Arguments: position="${positionName}", range="${range}"`);
                    CursorNav.navigate.chords(positionName, range);
                    Logger.success('Chord navigation function called successfully');
                } catch (e) {
                    Logger.error('Error calling chord navigation function:', e);
                }
            } else {
                Logger.warn('Chord navigation function not available');
                Logger.debug('Expected function at: window.getTonesFromDataChords');
            }
            
            Logger.groupEnd();
            return true;
        }
    };

    // Cursor UI management with enhanced logging
    const CursorUI = {
        // Create cursor elements
        create: function() {
            Logger.group('Creating Cursor UI');
            
            // Remove any existing cursors first
            const existingCursors = document.querySelectorAll('.left-cursor, .right-cursor');
            if (existingCursors.length > 0) {
                Logger.debug(`Removing ${existingCursors.length} existing cursor elements`);
                existingCursors.forEach(el => el.remove());
            }
            
            // Check if we should create cursors (might be disabled on mobile, etc.)
            if (window.innerWidth < 768 && !window.location.search.includes('force-cursors')) {
                Logger.info(`Not creating cursors on small screen (width: ${window.innerWidth}px)`);
                Logger.groupEnd();
                return null;
            }
            
            // Create container for better positioning
            const existingContainer = document.getElementById('cursor-nav-container');
            if (existingContainer) {
                existingContainer.remove();
                Logger.debug('Removed existing container');
            }
            
            const container = document.createElement('div');
            container.id = 'cursor-nav-container';
            container.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                pointer-events: none;
                z-index: 999;
            `;
            
            Logger.debug('Created container element');
            
            // Create left cursor
            const leftCursor = document.createElement('div');
            leftCursor.className = 'left-cursor';
            leftCursor.setAttribute('role', 'button');
            leftCursor.setAttribute('aria-label', 'Previous position');
            // Don't add innerHTML - CSS handles the cursor image
            leftCursor.style.cssText = `
                position: absolute;
                top: 50%;
                left: -20px;
                width: 44px;
                height: 44px;
                transform: translateY(-50%);
                background-color: transparent;
                color: transparent;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                user-select: none;
                pointer-events: auto;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                opacity: 0;
            `;
            
            // Create right cursor
            const rightCursor = document.createElement('div');
            rightCursor.className = 'right-cursor';
            rightCursor.setAttribute('role', 'button');
            rightCursor.setAttribute('aria-label', 'Next position');
            // Don't add innerHTML - CSS handles the cursor image
            rightCursor.style.cssText = `
                position: absolute;
                top: 50%;
                right: -60px;
                width: 44px;
                height: 44px;
                transform: translateY(-50%);
                background-color: transparent;
                color: transparent;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                user-select: none;
                pointer-events: auto;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                opacity: 0;
            `;
            
            Logger.debug('Created cursor elements');
            
            // Add hover effects
            const addHoverEffects = (cursor, name) => {
                cursor.addEventListener('mouseenter', () => {
                    if (cursor.style.opacity !== '0') {
                        cursor.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
                        cursor.style.transform = 'translateY(-50%) scale(1.1)';
                        cursor.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.4)';
                        Logger.debug(`${name} cursor hover enter`);
                    }
                });
                cursor.addEventListener('mouseleave', () => {
                    cursor.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                    cursor.style.transform = 'translateY(-50%) scale(1)';
                    cursor.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.3)';
                    Logger.debug(`${name} cursor hover leave`);
                });
            };
            
            addHoverEffects(leftCursor, 'Left');
            addHoverEffects(rightCursor, 'Right');
            
            // Add click handlers with event prevention
            leftCursor.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                Logger.info('Left cursor clicked');
                CursorNav.stats.leftClicks++;
                CursorNav.navigate.left();
            });
            
            rightCursor.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                Logger.info('Right cursor clicked');
                CursorNav.stats.rightClicks++;
                CursorNav.navigate.right();
            });
            
            // Try to append to fretboardcontainer first, otherwise use our container
            const fretboardContainer = document.querySelector('.fretboardcontainer, #fretboardcontainer');
            if (fretboardContainer) {
                // Add directly to fretboard container
                fretboardContainer.appendChild(leftCursor);
                fretboardContainer.appendChild(rightCursor);
                Logger.debug('Appended cursors to fretboard container');
            } else {
                // Fall back to our container
                container.appendChild(leftCursor);
                container.appendChild(rightCursor);
                document.body.appendChild(container);
                Logger.debug('Appended cursors to custom container');
            }
            
            Logger.success('Cursor UI created successfully');
            
            // Fade in cursors with transitions after initial positioning
            setTimeout(() => {
                if (leftCursor) {
                    leftCursor.style.transition = 'opacity 0.2s ease';
                    leftCursor.style.opacity = '1';
                }
                if (rightCursor) {
                    rightCursor.style.transition = 'opacity 0.2s ease';
                    rightCursor.style.opacity = '1';
                }
                Logger.debug('Cursors faded in');
                
                // Enable full transitions after fade-in
                setTimeout(() => {
                    if (leftCursor) {
                        leftCursor.style.transition = 'all 0.3s ease';
                    }
                    if (rightCursor) {
                        rightCursor.style.transition = 'all 0.3s ease';
                    }
                    Logger.debug('Full transitions enabled');
                }, 200);
            }, 50);
            
            Logger.groupEnd();
            
            return { leftCursor, rightCursor, container };
        },

        // Update cursor visibility
        update: function() {
            Logger.group('Updating Cursor Visibility');
            
            const leftCursor = document.querySelector('.left-cursor');
            const rightCursor = document.querySelector('.right-cursor');
            
            if (!leftCursor || !rightCursor) {
                Logger.error('Cursors not found for update');
                Logger.groupEnd();
                return;
            }
            
            Logger.debug('Mode:', CursorNav.mode);
            Logger.debug('Position:', CursorNav.position);
            Logger.debug('Max Position:', CursorNav.maxPosition);
            
            if (CursorNav.mode === 'scales') {
                // Hide left at position 0, right at max
                const hideLeft = CursorNav.position <= 0;
                const hideRight = CursorNav.position >= CursorNav.maxPosition;
                
                leftCursor.style.opacity = hideLeft ? '0' : '1';
                leftCursor.style.pointerEvents = hideLeft ? 'none' : 'auto';
                leftCursor.style.cursor = hideLeft ? 'default' : 'pointer';
                
                rightCursor.style.opacity = hideRight ? '0' : '1';
                rightCursor.style.pointerEvents = hideRight ? 'none' : 'auto';
                rightCursor.style.cursor = hideRight ? 'default' : 'pointer';
                
                Logger.info(`Scale cursors - Left: ${hideLeft ? 'hidden' : 'visible'}, Right: ${hideRight ? 'hidden' : 'visible'}`);
            } else if (CursorNav.mode === 'chords') {
                // Always visible for chords (they wrap)
                leftCursor.style.opacity = '1';
                leftCursor.style.pointerEvents = 'auto';
                leftCursor.style.cursor = 'pointer';
                
                rightCursor.style.opacity = '1';
                rightCursor.style.pointerEvents = 'auto';
                rightCursor.style.cursor = 'pointer';
                
                Logger.info('Chord cursors - Both visible (wrapping enabled)');
            }
            
            Logger.groupEnd();
        }
    };

    // Main navigation functions with statistics
    CursorNav.navigate.left = function() {
        Logger.group('Navigation: Left');
        
        if (!CursorNav.initialized) {
            Logger.error('Navigation called before initialization');
            Logger.groupEnd();
            return false;
        }
        
        CursorNav.stats.navigationCount++;
        CursorNav.stats.lastNavTime = new Date();
        
        const handler = CursorNav.mode === 'scales' ? Handlers.scales : Handlers.chords;
        const result = handler(-1);
        
        if (result) {
            CursorUI.update();
            
            // Dispatch custom event
            const event = new CustomEvent('cursornavigation', {
                detail: {
                    direction: 'left',
                    mode: CursorNav.mode,
                    position: CursorNav.position,
                    timestamp: CursorNav.stats.lastNavTime
                }
            });
            document.dispatchEvent(event);
            Logger.debug('Custom event dispatched');
        }
        
        Logger.groupEnd();
        return result;
    };

    CursorNav.navigate.right = function() {
        Logger.group('Navigation: Right');
        
        if (!CursorNav.initialized) {
            Logger.error('Navigation called before initialization');
            Logger.groupEnd();
            return false;
        }
        
        CursorNav.stats.navigationCount++;
        CursorNav.stats.lastNavTime = new Date();
        
        const handler = CursorNav.mode === 'scales' ? Handlers.scales : Handlers.chords;
        const result = handler(1);
        
        if (result) {
            CursorUI.update();
            
            // Dispatch custom event
            const event = new CustomEvent('cursornavigation', {
                detail: {
                    direction: 'right',
                    mode: CursorNav.mode,
                    position: CursorNav.position,
                    timestamp: CursorNav.stats.lastNavTime
                }
            });
            document.dispatchEvent(event);
            Logger.debug('Custom event dispatched');
        }
        
        Logger.groupEnd();
        return result;
    };

    // Initialize system with comprehensive logging
    CursorNav.init = function() {
        if (CursorNav.initialized) {
            Logger.warn('Already initialized, skipping...');
            return;
        }
        
        // Prevent infinite retry loops
        if (!CursorNav.initRetryCount) CursorNav.initRetryCount = 0;
        if (CursorNav.initRetryCount >= 5) {
            Logger.error('Init failed after 5 retries, giving up');
            return;
        }
        
        Logger.group('System Initialization');
        Logger.info(`Version: ${CursorNav.version}`);
        Logger.info(`Environment: ${Logger.isDev() ? 'Development' : 'Production'}`);
        Logger.info(`URL: ${window.location.href}`);
        Logger.info(`User Agent: ${navigator.userAgent}`);
        
        CursorNav.stats.initTime = new Date();
        
        // Detect mode
        CursorNav.mode = Utils.detectMode();
        if (!CursorNav.mode) {
            CursorNav.initRetryCount++;
            Logger.warn(`Could not detect mode, deferring initialization (retry ${CursorNav.initRetryCount}/5)`);
            Logger.groupEnd();
            // Try again later with increasing delay
            setTimeout(CursorNav.init, 500 * CursorNav.initRetryCount);
            return;
        }
        
        Logger.success(`Mode detected: ${CursorNav.mode}`);
        
        // Set up initial state based on mode
        if (CursorNav.mode === 'scales') {
            CursorNav.maxPosition = Utils.getMaxScalePosition();
            const posParam = Utils.getParam('position_select');
            CursorNav.position = posParam !== null ? parseInt(posParam) : 0;
            
            // Validate position
            if (isNaN(CursorNav.position) || CursorNav.position < 0) {
                Logger.warn('Invalid position, resetting to 0');
                CursorNav.position = 0;
            }
            if (CursorNav.position > CursorNav.maxPosition) {
                Logger.warn(`Position ${CursorNav.position} exceeds max ${CursorNav.maxPosition}, capping`);
                CursorNav.position = CursorNav.maxPosition;
            }
            
            // Find scale navigation function
            const scaleFunctions = [
                'getTonesFromDataScales',
                'updateScalePosition',
                'activateScalePosition'
            ];
            
            for (const funcName of scaleFunctions) {
                if (typeof window[funcName] === 'function') {
                    CursorNav.navigate.scales = window[funcName];
                    Logger.success(`Found scale navigation function: window.${funcName}`);
                    break;
                }
            }
            
            if (!CursorNav.navigate.scales) {
                Logger.warn('No scale navigation function found');
                Logger.debug('Searched for:', scaleFunctions);
            }
            
            Logger.info('Scale mode initialized:', {
                position: CursorNav.position,
                maxPosition: CursorNav.maxPosition,
                hasNavigationFunction: !!CursorNav.navigate.scales
            });
        } else {
            const info = Utils.getChordInfo();
            const posParam = Utils.getParam('position_select');
            
            // Map position name to index
            const positions = ['Root Position', 'First Inversion', 'Second Inversion', 'Third Inversion'];
            let posIndex = 0;
            
            if (posParam) {
                Logger.debug('Position from URL:', posParam);
                
                // Try exact match
                posIndex = positions.indexOf(posParam);
                
                // Try alternatives
                if (posIndex === -1) {
                    if (posParam === 'Basic Position') posIndex = 0;
                    else if (posParam.includes('1st')) posIndex = 1;
                    else if (posParam.includes('2nd')) posIndex = 2;
                    else if (posParam.includes('3rd')) posIndex = 3;
                    
                    if (posIndex !== -1) {
                        Logger.debug(`Mapped "${posParam}" to index ${posIndex}`);
                    }
                }
                
                // Default to 0 if not found
                if (posIndex === -1) {
                    Logger.warn(`Unknown position "${posParam}", defaulting to 0`);
                    posIndex = 0;
                }
            }
            
            CursorNav.position = posIndex;
            
            // Find chord navigation function
            const chordFunctions = [
                'getTonesFromDataChords',
                'updateChordPosition',
                'activateChordPosition'
            ];
            
            for (const funcName of chordFunctions) {
                if (typeof window[funcName] === 'function') {
                    CursorNav.navigate.chords = window[funcName];
                    Logger.success(`Found chord navigation function: window.${funcName}`);
                    break;
                }
            }
            
            if (!CursorNav.navigate.chords) {
                Logger.warn('No chord navigation function found yet, will retry...');
                Logger.debug('Searched for:', chordFunctions);
                
                // Set up a limited retry mechanism for chord pages
                let retryCount = 0;
                const retryInterval = setInterval(() => {
                    retryCount++;
                    let found = false;
                    for (const funcName of chordFunctions) {
                        if (typeof window[funcName] === 'function') {
                            CursorNav.navigate.chords = window[funcName];
                            Logger.success(`Found chord navigation function on retry ${retryCount}: window.${funcName}`);
                            clearInterval(retryInterval);
                            found = true;
                            break;
                        }
                    }
                    
                    if (!found && retryCount >= 5) {
                        Logger.error('Failed to find chord navigation function after 5 retries, giving up');
                        clearInterval(retryInterval);
                    }
                }, 200);
            }
            
            Logger.info('Chord mode initialized:', {
                position: CursorNav.position,
                chordType: info.type,
                maxInversion: info.maxInversion,
                hasNavigationFunction: !!CursorNav.navigate.chords
            });
        }
        
        // Create UI elements
        const ui = CursorUI.create();
        if (ui) {
            CursorUI.update();
            Logger.success('UI elements created and updated');
        } else {
            Logger.warn('UI elements not created (possibly on mobile)');
        }
        
        // Set up keyboard navigation
        const keyHandler = (e) => {
            // Check if user is typing in an input
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }
            
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                Logger.info('Keyboard navigation: Left arrow');
                CursorNav.stats.keyboardNavs++;
                CursorNav.navigate.left();
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                Logger.info('Keyboard navigation: Right arrow');
                CursorNav.stats.keyboardNavs++;
                CursorNav.navigate.right();
            }
        };
        
        document.removeEventListener('keydown', keyHandler); // Remove if exists
        document.addEventListener('keydown', keyHandler);
        Logger.debug('Keyboard navigation enabled');
        
        // Export global functions for compatibility
        window.leftCursorClick = CursorNav.navigate.left;
        window.rightCursorClick = CursorNav.navigate.right;
        window.fpfLeftCursorClick = CursorNav.navigate.left;
        window.fpfRightCursorClick = CursorNav.navigate.right;
        
        Logger.debug('Global compatibility functions exported');
        
        CursorNav.initialized = true;
        
        const initDuration = new Date() - CursorNav.stats.initTime;
        Logger.success(`Initialization complete in ${initDuration}ms`);
        
        // Log final state
        Logger.table('Initial State', {
            mode: CursorNav.mode,
            position: CursorNav.position,
            maxPosition: CursorNav.maxPosition,
            hasScaleFunction: !!CursorNav.navigate.scales,
            hasChordFunction: !!CursorNav.navigate.chords,
            uiCreated: !!ui,
            debug: Logger.isDev()
        });
        
        // Dispatch initialization event
        document.dispatchEvent(new CustomEvent('cursornavigationready', {
            detail: { 
                mode: CursorNav.mode, 
                position: CursorNav.position,
                version: CursorNav.version,
                initDuration: initDuration
            }
        }));
        
        Logger.groupEnd();
        
        // Print statistics function for development
        if (Logger.isDev()) {
            Logger.info('Tip: Use CursorNav.printStats() to see navigation statistics');
        }
        
        // Initialize the display for the current position
        setTimeout(() => {
            if (CursorNav.mode === 'scales' && typeof window.getTonesFromDataScales === 'function') {
                Logger.info('Initializing scale display for current position...');
                const currentPos = Utils.getParam('position_select') || '0';
                window.getTonesFromDataScales(currentPos);
            } else if (CursorNav.mode === 'chords' && typeof window.getTonesFromDataChords === 'function') {
                Logger.info('Initializing chord display for current position...');
                const currentPos = Utils.getParam('position_select') || 'Root Position';
                window.getTonesFromDataChords(currentPos);
            }
        }, 100);
    };

    // Reset function for testing
    CursorNav.reset = function() {
        Logger.group('System Reset');
        
        CursorNav.initialized = false;
        CursorNav.mode = null;
        CursorNav.position = 0;
        CursorNav.maxPosition = 6;
        CursorNav.navigate.scales = null;
        CursorNav.navigate.chords = null;
        
        // Remove UI elements
        const container = document.getElementById('cursor-nav-container');
        if (container) {
            container.remove();
            Logger.debug('Container removed');
        }
        
        // Remove any stray cursors
        const strayCursors = document.querySelectorAll('.left-cursor, .right-cursor');
        strayCursors.forEach(el => {
            el.remove();
            Logger.debug('Removed stray cursor element');
        });
        
        Logger.success('System reset complete');
        Logger.groupEnd();
    };

    // Print statistics (for development)
    CursorNav.printStats = function() {
        Logger.group('Navigation Statistics');
        
        const stats = {
            'Total Navigations': CursorNav.stats.navigationCount,
            'Left Clicks': CursorNav.stats.leftClicks,
            'Right Clicks': CursorNav.stats.rightClicks,
            'Keyboard Navigations': CursorNav.stats.keyboardNavs,
            'Errors Encountered': CursorNav.stats.errors,
            'Initialization Time': CursorNav.stats.initTime ? CursorNav.stats.initTime.toLocaleTimeString() : 'Not initialized',
            'Last Navigation': CursorNav.stats.lastNavTime ? CursorNav.stats.lastNavTime.toLocaleTimeString() : 'Never',
            'Session Duration': CursorNav.stats.initTime ? `${Math.round((new Date() - CursorNav.stats.initTime) / 1000)}s` : 'N/A'
        };
        
        Logger.table('Statistics', stats);
        
        const state = {
            'Mode': CursorNav.mode,
            'Position': CursorNav.position,
            'Max Position': CursorNav.maxPosition,
            'Initialized': CursorNav.initialized,
            'Debug Mode': Logger.isDev()
        };
        
        Logger.table('Current State', state);
        Logger.groupEnd();
    };

    // Enable debug mode programmatically
    CursorNav.enableDebug = function() {
        CursorNav.debug = true;
        Logger.success('Debug mode enabled');
        Logger.info('Refresh the page to see full initialization logs');
    };


    // Simple initialization
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            Logger.info('DOM loaded, initializing...');
            CursorNav.init();
        });
    } else {
        // DOM already loaded
        Logger.info('DOM already loaded, initializing...');
        CursorNav.init();
    }
    
    // MutationObserver disabled to prevent infinite loops
    function startNoteVisibilityGuard() {
        Logger.info('Note visibility guard disabled to prevent infinite loops');
    }
    
    // Export for debugging and testing
    window.CursorNav = CursorNav;
    
    // Log initial load
    if (Logger.isDev()) {
        console.log('%c[CursorNav] Cursor Navigation System v2.2 loaded', 'color: #00aa00; font-weight: bold');
        console.log('%c[CursorNav] Debug mode enabled (development environment detected)', 'color: #0066cc');
        console.log('%c[CursorNav] Available commands:', 'color: #666666');
        console.log('%c  CursorNav.printStats()     - Show navigation statistics', 'color: #666666');
        console.log('%c  CursorNav.enableDebug()    - Enable debug mode', 'color: #666666');
        console.log('%c  CursorNav.reset()          - Reset the system', 'color: #666666');
        console.log('%c  CursorNav                  - Inspect current state', 'color: #666666');
    }
})();