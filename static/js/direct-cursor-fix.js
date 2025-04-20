/**
 * Direct Cursor Fix - Minimal solution for chord inversions
 * Directly handles the issue by tracking and managing active states
 */

// Track navigation state
let previousActiveNotes = [];
let newActiveNotes = [];
let isNavigating = false;
let originalRootId = null;

// Debug: log all clicks (capture phase) to inspect targets
document.addEventListener('click', function(e) {
    console.log('DEBUG_CURSOR: captured click on', e.target, 'classes:', e.target.classList);
}, true);

// Debug: log active notes after each click (post-navigation cleanup)
document.addEventListener('click', function(e) {
    setTimeout(function() {
        const activeEls = document.querySelectorAll('.note.active');
        const activeIds = Array.from(activeEls).map(el => getNoteIdentifier(el));
        console.log('DEBUG_CURSOR: active notes after click:', activeIds);
    }, 150);
}, true);

// Debug: ensure script evaluation
console.log('DEBUG_CURSOR: direct-cursor-fix.js script loaded');
overrideCursorFunctions();
console.log('DEBUG_CURSOR: overrideCursorFunctions invoked on load');
setTimeout(fixActiveNotes, 500);

// Set up when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Direct cursor fix: Initializing...');
    
    // Override cursor functions
    //overrideCursorFunctions();
    
    // Apply initial fix
    //setTimeout(fixActiveNotes, 500);
    
    const initRootImg = document.querySelector('img.tone[data-is-root="true"]');
    if (initRootImg) {
        const noteEl = initRootImg.closest('.note');
        if (noteEl) {
            originalRootId = getNoteIdentifier(noteEl);
            console.log('DEBUG_CURSOR: recorded originalRootId:', originalRootId);
        }
    }
});

// Add delegated click listener for cursor elements
document.addEventListener('click', function(e) {
    if (e.target.closest('.left-cursor')) {
        console.log('DEBUG_CURSOR: left-cursor element clicked');
    }
    if (e.target.closest('.right-cursor')) {
        console.log('DEBUG_CURSOR: right-cursor element clicked');
    }
});

// Manual delegate for cursor clicks: intercept at document and ensure cleanup/navigation
document.addEventListener('click', function(e) {
    const left = e.target.closest('.left-cursor');
    const right = e.target.closest('.right-cursor');
    if (!(left || right)) return;
    console.log('DEBUG_CURSOR: manual delegate click', left ? 'left' : 'right');
    // Log active notes prior to deactivation
    document.querySelectorAll('.note.active').forEach(noteEl => {
        const id = getNoteIdentifier(noteEl);
        const name = noteEl.querySelector('.notename')?.textContent;
        const isRootAttr = noteEl.querySelector('img.tone')?.getAttribute('data-is-root');
        console.log(`DEBUG_CURSOR: BEFORE deactivation note id=${id}, name=${name}, data-is-root=${isRootAttr}`);
    });
    e.preventDefault();
    e.stopPropagation();
    // Log root note before deactivation
    const beforeRootImg = document.querySelector('img.tone[data-is-root="true"]');
    if (beforeRootImg) {
        const beforeRootNote = beforeRootImg.closest('.note');
        const beforeRootName = beforeRootNote.querySelector('.notename')?.textContent;
        console.log('DEBUG_CURSOR: ROOT BEFORE DEACTIVATION:', getNoteIdentifier(beforeRootNote), beforeRootName);
    }
    // Clear all active notes
    document.querySelectorAll('.note.active').forEach(noteEl => {
        const id = getNoteIdentifier(noteEl);
        const nameEl = noteEl.querySelector('.notename');
        const noteName = nameEl ? nameEl.textContent : '(none)';
        const imgEl = noteEl.querySelector('img.tone');
        console.log(`DEBUG_CURSOR: BEFORE deactivation: id=${id}, name=${noteName}, src=${imgEl.src}, data-is-root=${imgEl.getAttribute('data-is-root')}`);
        deactivateNote(noteEl);
    });
    // Trigger navigation via fpf* handlers
    const fn = left ? fpfLeftCursorClick : fpfRightCursorClick;
    if (typeof fn === 'function') fn(e);
    setTimeout(() => {
        cleanupNoteDisplay();
        fixActiveNotes();
        console.log('DEBUG_CURSOR: after navigation active notes:');
        document.querySelectorAll('.note.active').forEach(noteEl => {
            const id = getNoteIdentifier(noteEl);
            const name = noteEl.querySelector('.notename')?.textContent;
            const isRootAttr = noteEl.querySelector('img.tone')?.getAttribute('data-is-root');
            console.log(`DEBUG_CURSOR: ACTIVE after nav note id=${id}, name=${name}, data-is-root=${isRootAttr}`);
        });
    }, 150);
}, true);

/**
 * Override cursor click functions with fixed versions
 */
function overrideCursorFunctions() {
    // Store original functions to call later
    const originalLeftCursorClick = window.leftCursorClick;
    const originalRightCursorClick = window.rightCursorClick;
    
    // Replace left cursor click
    window.leftCursorClick = function(e) {
        console.log('DEBUG_CURSOR: leftCursorClick starting, previousActiveNotes:', previousActiveNotes);
        isNavigating = true;
        
        // Clear all existing notes before navigation
        document.querySelectorAll('.note').forEach(noteEl => { const id = getNoteIdentifier(noteEl); console.log('DEBUG_CURSOR: clearing note', id); deactivateNote(noteEl); });
        
        // Record active notes (now none) if needed
        storeCurrentNotes(); console.log('DEBUG_CURSOR: after storeCurrentNotes, previousActiveNotes:', previousActiveNotes);
        
        // Step 2: Call original function
        if (typeof originalLeftCursorClick === 'function') { originalLeftCursorClick.call(this, e); console.log('DEBUG_CURSOR: after originalLeftCursorClick'); }
        
        // Step 3: Fix note display
        setTimeout(function() {
            console.log('DEBUG_CURSOR: cleanupNoteDisplay start, previousActiveNotes:', previousActiveNotes);
            cleanupNoteDisplay();
            fixActiveNotes();
            console.log('DEBUG_CURSOR: cleanupNoteDisplay end, active count:', document.querySelectorAll('.note.active').length);
            isNavigating = false;
        }, 100);
    };
    
    // Replace right cursor click
    window.rightCursorClick = function(e) {
        console.log('DEBUG_CURSOR: rightCursorClick starting, previousActiveNotes:', previousActiveNotes);
        isNavigating = true;
        
        // Clear all existing notes before navigation
        document.querySelectorAll('.note').forEach(noteEl => { const id = getNoteIdentifier(noteEl); console.log('DEBUG_CURSOR: clearing note', id); deactivateNote(noteEl); });
        
        // Record active notes (now none) if needed
        storeCurrentNotes(); console.log('DEBUG_CURSOR: after storeCurrentNotes, previousActiveNotes:', previousActiveNotes);
        
        // Step 2: Call original function
        if (typeof originalRightCursorClick === 'function') { originalRightCursorClick.call(this, e); console.log('DEBUG_CURSOR: after originalRightCursorClick'); }
        
        // Step 3: Fix note display
        setTimeout(function() {
            console.log('DEBUG_CURSOR: cleanupNoteDisplay start, previousActiveNotes:', previousActiveNotes);
            cleanupNoteDisplay();
            fixActiveNotes();
            console.log('DEBUG_CURSOR: cleanupNoteDisplay end, active count:', document.querySelectorAll('.note.active').length);
            isNavigating = false;
        }, 100);
    };
    
    console.log('Direct cursor fix: Overrode cursor functions');
}

// Monkey-patch fpfLeftCursorClick and fpfRightCursorClick for cleanup and logging
if (typeof fpfLeftCursorClick === 'function') {
    console.log('DEBUG_CURSOR: patching fpfLeftCursorClick');
    const originalFpfLeft = fpfLeftCursorClick;
    fpfLeftCursorClick = function() {
        console.log('DEBUG_CURSOR: fpfLeftCursorClick start');
        document.querySelectorAll('.note').forEach(noteEl => deactivateNote(noteEl));
        originalFpfLeft();
        setTimeout(() => {
            const ids = Array.from(document.querySelectorAll('.note.active')).map(el => getNoteIdentifier(el));
            console.log('DEBUG_CURSOR: fpfLeftCursorClick end, active notes:', ids);
        }, 100);
    };
}
if (typeof fpfRightCursorClick === 'function') {
    console.log('DEBUG_CURSOR: patching fpfRightCursorClick');
    const originalFpfRight = fpfRightCursorClick;
    fpfRightCursorClick = function() {
        console.log('DEBUG_CURSOR: fpfRightCursorClick start');
        document.querySelectorAll('.note').forEach(noteEl => deactivateNote(noteEl));
        originalFpfRight();
        setTimeout(() => {
            const ids = Array.from(document.querySelectorAll('.note.active')).map(el => getNoteIdentifier(el));
            console.log('DEBUG_CURSOR: fpfRightCursorClick end, active notes:', ids);
        }, 100);
    };
}

/**
 * Store information about currently active notes before navigation
 */
function storeCurrentNotes() {
    previousActiveNotes = [];
    
    // Record all currently active notes
    document.querySelectorAll('.note.active').forEach(function(noteElement) {
        const id = getNoteIdentifier(noteElement);
        if (id) previousActiveNotes.push(id);
    });
    console.log('DEBUG_CURSOR: storeCurrentNotes, stored previousActiveNotes:', previousActiveNotes);
}

/**
 * Get a consistent identifier for a note element
 */
function getNoteIdentifier(noteElement) {
    if (!noteElement) return null;
    
    // Traverse up the DOM tree to locate the element that represents the string (e.g. eString, bString …)
    let currentEl = noteElement;
    let stringClass = null;
    while (currentEl && currentEl !== document) {
        stringClass = Array.from(currentEl.classList || []).find(cls => cls.endsWith('String'));
        if (stringClass) break;
        currentEl = currentEl.parentElement;
    }
    if (!stringClass) return null;
    
    // Determine the note class (e.g. c2, f#3). Filter out generic/helper classes.
    const noteClass = Array.from(noteElement.classList).find(cls =>
        cls !== 'note' && cls !== 'active' && !cls.includes('-'));
    if (!noteClass) return null;
    
    return `${stringClass}-${noteClass}`;
}

/**
 * Clean up the note display after navigation
 */
function cleanupNoteDisplay() {
    console.log('DEBUG_CURSOR: cleanupNoteDisplay start, previousActiveNotes:', previousActiveNotes);
    const rawActive = Array.from(document.querySelectorAll('.note.active')).map(el => getNoteIdentifier(el));
    console.log('DEBUG_CURSOR: cleanup raw active IDs:', rawActive);
    newActiveNotes = [];
    
    // Log img.tone[data-is-root] elements detection
    document.querySelectorAll('img.tone[data-is-root="true"]').forEach(img => {
        const noteEl = img.closest('.note');
        const id = getNoteIdentifier(noteEl);
        const name = noteEl.querySelector('.notename') ? noteEl.querySelector('.notename').textContent : '(none)';
        console.log(`DEBUG_CURSOR: cleanup root-image detect: id=${id}, name=${name}, src=${img.src}`);
    });
    
    document.querySelectorAll('.note.active').forEach(function(noteElement) {
        const id = getNoteIdentifier(noteElement);
        const toneImg = noteElement.querySelector('img.tone');
        const noteName = noteElement.querySelector('.notename')?.textContent;
        const isRootAttr = toneImg.getAttribute('data-is-root') === 'true';
        console.log(`DEBUG_CURSOR: cleanup active note id=${id}, name=${noteName}, isRootAttr=${isRootAttr}`);
        if (previousActiveNotes.includes(id) && !newActiveNotes.includes(id)) {
            deactivateNote(noteElement);
        }
        newActiveNotes.push(id);
    });
    
    console.log('DEBUG_CURSOR: cleanupNoteDisplay end, newActiveNotes:', newActiveNotes);
}

/**
 * Deactivate a note completely
 */
function deactivateNote(noteElement) {
    const id = getNoteIdentifier(noteElement) || 'unknown';
    console.log('DEBUG_CURSOR: deactivateNote for:', id);
    // Remove active class
    noteElement.classList.remove('active');
    // Reset container visibility
    noteElement.style.opacity = '';
    
    // Reset the note image
    const toneImg = noteElement.querySelector('img.tone');
    if (toneImg) {
        toneImg.classList.remove('active', 'root');
        toneImg.src = '/static/media/yellow_circle.svg';
        toneImg.style.opacity = '';
        toneImg.style.border = '';
        toneImg.style.boxShadow = '';
        toneImg.style.visibility = '';
    }
    
    // Hide the note name
    const noteName = noteElement.querySelector('.notename');
    if (noteName) {
        noteName.style.visibility = 'hidden';
        noteName.style.opacity = '0';
        noteName.style.fontWeight = '';
        noteName.classList.remove('active', 'show-name');
    }
}

/**
 * Fix active notes - can be called directly to fix display issues
 */
function fixActiveNotes() {
    console.log('DEBUG_CURSOR: fixActiveNotes start');
    const rawActiveFix = Array.from(document.querySelectorAll('.note.active')).map(el => getNoteIdentifier(el));
    console.log('DEBUG_CURSOR: fix raw active IDs:', rawActiveFix);
    
    // Log img.tone[data-is-root] elements detection during fix
    document.querySelectorAll('img.tone[data-is-root="true"]').forEach(img => {
        const noteEl = img.closest('.note');
        const id = getNoteIdentifier(noteEl);
        const name = noteEl.querySelector('.notename') ? noteEl.querySelector('.notename').textContent : '(none)';
        console.log(`DEBUG_CURSOR: fix root-image detect: id=${id}, name=${name}, src=${img.src}`);
    });
    
    document.querySelectorAll('.note.active').forEach(function(noteElement) {
        const id = getNoteIdentifier(noteElement);
        const toneImg = noteElement.querySelector('img.tone');
        const noteName = noteElement.querySelector('.notename')?.textContent;
        const isRootAttr = toneImg.getAttribute('data-is-root') === 'true';
        console.log(`DEBUG_CURSOR: fix styling note id=${id}, name=${noteName}, isRootAttr=${isRootAttr}`);
        toneImg.classList.add('active');
        toneImg.style.opacity = '1';
        if (isRootAttr) {
            toneImg.classList.add('root');
            toneImg.src = '/static/media/red_circle.svg';
            toneImg.style.border = '2px solid rgb(204, 0, 0)';
            toneImg.style.boxShadow = 'rgba(255, 0, 0, 0.3) 0px 0px 5px';
        }
    });
    
    console.log('DEBUG_CURSOR: fixActiveNotes end');
}

// Add debug helper
window.directCursorFix = {
    previousNotes: function() { return previousActiveNotes; },
    newNotes: function() { return newActiveNotes; },
    fix: fixActiveNotes,
    cleanup: cleanupNoteDisplay
};
