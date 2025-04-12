var string_array = ['highAString', 'eString', 'bString', 'gString', 'dString', 'AString', 'ELowString', 'lowBString'];


var frets = ['one','two','three','four','five','six',
            'seven','eight','nine','ten','eleven', 'twelve',
            'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen']

const NOTES = {
    'eString': [['f2'], ['gb2', 'fs2'], ['g2'], ['ab2', 'gs2'], ['a2'], ['bb2', 'as2'], ['b2'], ['c3'], ['db3', 'cs3'], ['d3'], ['eb3', 'ds3'], ['e3'], ['f3'], ['gb3', 'fs3'], ['g3'], ['ab3', 'gs3'], ['a3']],
    'bString': [['c2'], ['db2', 'cs2'], ['d2'], ['eb2', 'ds2'], ['e2'], ['f2'], ['gb2', 'fs2'], ['g2'], ['ab2', 'gs2'], ['a2'], ['bb2', 'as2'], ['b2'], ['c3'], ['db3', 'cs3'], ['d3'], ['eb3', 'ds3'], ['e3']],
    'gString': [['ab1', 'gs1'], ['a1'], ['bb1', 'as1'], ['b1'], ['c2'], ['db2', 'cs2'], ['d2'], ['eb2', 'ds2'], ['e2'], ['f2'], ['gb2', 'fs2'], ['g2'], ['ab2', 'gs2'], ['a2'], ['bb2', 'as2'], ['b2'], ['c3']],
    'dString': [['eb1', 'ds1'], ['e1'], ['f1'], ['gb1', 'fs1'], ['g1'], ['ab1', 'gs1'], ['a1'], ['bb1', 'as1'], ['b1'], ['c2'], ['db2', 'cs2'], ['d2'], ['eb2', 'ds2'], ['e2'], ['f2'], ['gb2', 'fs2'], ['g2']],
    'AString': [['bb0', 'as0'], ['b0'], ['c1'], ['db1', 'cs1'], ['d1'], ['eb1', 'ds1'], ['e1'], ['f1'], ['gb1', 'fs1'], ['g1'], ['ab1', 'gs1'], ['a1'], ['bb1', 'as1'], ['b1'], ['c2'], ['db2', 'cs2'], ['d2']],
    'ELowString': [['f0'], ['gb0', 'fs0'], ['g0'], ['ab0', 'gs0'], ['a0'], ['bb0', 'as0'], ['b0'], ['c1'], ['db1', 'cs1'], ['d1'], ['eb1', 'ds1'], ['e1'], ['f1'], ['gb1', 'fs1'], ['g1'], ['ab1', 'gs1'], ['a1']],
    'highAString': [['bb2', 'as2'], ['b2'], ['c3'], ['db3', 'cs3'], ['d3'], ['eb3', 'ds3'], ['e3'], ['f3'], ['gb3', 'fs3'], ['g3'], ['ab3', 'gs3'], ['a3'], ['bb3', 'as3'], ['b3'], ['c4'], ['db4', 'cs4'], ['d4']],
    'lowBString': [['c0'], ['db0', 'cs0'], ['d0'], ['eb0', 'ds0'], ['e0'], ['f0'], ['gb0', 'fs0'], ['g0'], ['ab0', 'gs0'], ['a0'], ['bb0', 'as0'], ['b0'], ['c1'], ['db1', 'cs1'], ['d1'], ['eb1', 'ds1'], ['e1']]
};

// --- Height Synchronization Function (Global Scope) ---
function syncLowestStringHeight() {
  const spacingTop = document.querySelector('.fretboard .spacing-top');
  const fretboardContainer = document.querySelector('.fretboardcontainer'); // Assuming this container holds the config class

  if (!spacingTop || !fretboardContainer) {
    console.warn('Required elements for height sync not found.');
    return;
  }

  const isEightString = fretboardContainer.classList.contains('eight-string-config');
  const lowestStringClass = isEightString ? 'lowBString' : 'ELowString';
  const selector = `.fretboard .fret.${lowestStringClass}`;

  console.log(`Height Sync: Detected ${isEightString ? '8-string' : '6-string'} config. Using class: ${lowestStringClass}`);
  console.log(`Height Sync: Using selector: ${selector}`);

  // Select ALL fret divs that belong to the lowest string
  const lowestStringFretDivs = document.querySelectorAll(selector);

  console.log(`Height Sync: Found ${lowestStringFretDivs.length} elements with selector ${selector}`);

  if (lowestStringFretDivs.length > 0) {
    const spacingTopHeight = spacingTop.offsetHeight; // Use offsetHeight for rendered height including padding/border
    console.log(`Height Sync: Measured spacingTop height: ${spacingTopHeight}px`);
    console.log(`Height Sync: Applying height ${spacingTopHeight}px to ${lowestStringFretDivs.length} elements...`);
    lowestStringFretDivs.forEach((div, index) => {
      // Log the first element for verification
      if (index === 0) {
          console.log(`Height Sync: Applying to element:`, div);
      }
      div.style.height = `${spacingTopHeight}px`;
    });
    console.log(`Height Sync: Finished applying height.`);
  } else {
    console.warn(`Height Sync: No fret divs found for the lowest string class (${lowestStringClass}). Height not applied.`);
  }
}
// --- End Height Synchronization Function ---



/**
 * Play a tone and update the UI based on the 'root' class.
 * @param {string} tone - The name of the tone to play.
 * @param {string} stringName - The name of the string where the tone is played.
 */

// Angepasste playTone Funktion
// Deine playTone Funktion
// Angepasste playTone Funktion
function playTone(tone, stringName = null) {
  let element;
  if (stringName) {
      element = document.querySelector(`.${stringName} img.tone.${tone}`);
  } else {
      element = document.querySelector(`img.tone.${tone}`);
  }
  
  if (!element) {
      console.warn(`Element for tone ${tone} ${stringName ? 'on string ' + stringName : ''} not found.`);
      return;
  }

  let activeElement = null;

  // If stringName is provided, check for equivalent tones within the same string
  if (stringName) {
      const equivalentTones = NOTES[stringName].find(fret => fret.includes(tone));
      const equivalentTone = equivalentTones ? equivalentTones.find(t => t !== tone) : null;
      const equivalentElement = equivalentTone ? document.querySelector(`.${stringName} img.tone.${equivalentTone}`) : null;

      if (element && element.classList.contains('active')) {
          activeElement = element;
      } else if (equivalentElement && equivalentElement.classList.contains('active')) {
          activeElement = equivalentElement;
      }
  } else {
      if (element.classList.contains('active')) {
          activeElement = element;
      }
  }

  if (activeElement) {
      const audio = new Audio(`static/media/tone_sounds/${tone}.mp3`);
      audio.play();

      // Add a class to temporarily brighten the element
      activeElement.classList.add('playing');
      
      // Remove the class after a short duration
      setTimeout(() => {
          activeElement.classList.remove('playing');
      }, 300); // Duration of the brightness effect in milliseconds
  } else {
      console.warn(`Element for tone ${tone} ${stringName ? 'on string ' + stringName : ''} and its equivalent are not active or not found.`);
  }
}


/**
 * Resets the fretboard by removing 'active' class and setting the tone elements back to default.
 */
function resetFretboard() {
  // Remove 'active' class from all active elements
  const activeElements = document.querySelectorAll('.active');
  activeElements.forEach(element => element.classList.remove('active'));

  // Reset the 'src' attribute for all tone elements based on octave
  const toneElements = document.querySelectorAll('.tone');
  toneElements.forEach(element => {
    // Find the note element containing this tone
    const noteElement = element.closest('.note');
    if (noteElement) {
      // Get the tone class which includes octave information
      const toneNames = Array.from(noteElement.classList).filter(cls => cls !== 'note' && cls !== 'active');
      if (toneNames.length > 0) {
        const toneName = toneNames[0];
        const octaveMatch = toneName.match(/[a-z]+([0-4])/);
        
        if (octaveMatch && octaveMatch[1]) {
          const octave = parseInt(octaveMatch[1]);
          
          // Determine which circle to use based on octave
          let svgSrc = '/static/media/';
          switch (octave) {
            case 0: svgSrc += 'circle_01.svg?v=2'; break;
            case 1: svgSrc += 'circle_01.svg?v=2'; break;
            case 2: svgSrc += 'circle_02.svg?v=2'; break;
            case 3: svgSrc += 'circle_03.svg?v=2'; break;
            case 4: svgSrc += 'circle_04.svg?v=2'; break;
            default: svgSrc += 'circle_01.svg?v=2';
          }
          
          element.setAttribute('src', svgSrc);
        } else {
          element.setAttribute('src', '/static/media/circle_01.svg?v=2');
        }
      } else {
        element.setAttribute('src', '/static/media/circle_01.svg');
      }
    } else {
      element.setAttribute('src', '/static/media/circle_01.svg');
    }
  });
}


/**
 * Deactivate notes that are currently active on a given string.
 * @param {string} string - The name of the string to check.
 * @param {string} toneName - The name of the tone to deactivate.
 */
function deactivateActiveNotes(string, toneName) {
  // Query all elements that match the given string and tone name
  const elements = document.querySelectorAll(`.${string} .${toneName}`);
  
  // Iterate through the NodeList
  for (let x in elements) {
    // Check if the index is a natural number
    if (!isNaN(x)) {
      // Remove the 'active' class from the element
      elements[x].classList.remove('active');
    }
  }
}

/* IMPORTANT */
function getToneNameFromDataChords() {
  var button = document.getElementById('show_tension_button')
  button.setAttribute('onclick','show_tension_notes_chords()')
  button.innerHTML = 'Show Tensions';
  var pos_val = document.getElementById('position_select').value
  var note_range = document.getElementById('note_range').value
  getTonesFromDataChords(pos_val, note_range)
}

/* Function For Getting Note Names on Dots */
function getNoteNameFromData(){
  /* x sets the id of inversions */
  y = document.getElementById('position_select').value
  var i = 0;
  for (var key in scale_data[y]) {
    if (scale_data[y].hasOwnProperty(key)) {
      for (var z in scale_data[y][key][0]['tones']) {
        var tone_name = scale_data[y][key][0]['tones'][z]
        var QuerySelect = document.querySelector('.' + key + ' .notename.' + tone_name);
        var image = document.querySelector('.' + key + ' .' + tone_name + ' img.active');
        if (image){
          if (QuerySelect != null){
            QuerySelect.classList.add('active')
          }
        }
      }
    }
  }
  var button = document.getElementById('show_note_name_button')
  button.setAttribute('onclick','getNotePicFromData()')
  button.innerHTML = 'Only Tones';
}
 // Function For Getting Note Names on Dots
 function getNoteNameFromData() {
  var noteNames = document.querySelectorAll('.note .notename');
  noteNames.forEach(function(noteName) {
    var parentNote = noteName.closest('.note');
    var activeImage = parentNote.querySelector('img.active');
    if (activeImage) {
      noteName.classList.add('active');
      noteName.style.visibility = 'visible'; // Ensure visibility
    }
  });
  var button = document.getElementById('show_note_name_button');
  button.setAttribute('onclick', 'hideNoteNames()');
  button.innerHTML = 'Only Tones';
}

// Function For Hiding Note Names on Dots
function hideNoteNames() {
  var notenames = document.querySelectorAll('.notename.active');
  notenames.forEach(function(n) {
    n.classList.remove('active');
    n.style.visibility = 'hidden'; // Hide visibility
  });
  var button = document.getElementById('show_note_name_button');
  button.setAttribute('onclick', 'getNoteNameFromData()');
  button.innerHTML = 'Show Note Names';
}

/* Function For Deleting Note Names */
function getNotePicFromData(){
  /* x sets the id of inversions */
  var notename_elements = document.querySelectorAll('.notename');
  if (notename_elements != undefined){
    for (var i=0; i<notename_elements.length; i++) {
      notename_elements[i].classList.remove('active');
    }
  }
  var button = document.getElementById('show_note_name_button')
  button.setAttribute('onclick','getNoteNameFromData()')
  button.innerHTML = 'Show Note Names';
}

function closeAllSelect(elmnt) {
  /*  Close all select boxes in the document,
  except the current select box: */
  var x, y, i, arrNo = [];
  x = document.getElementsByClassName('slit');
  y = document.getElementsByClassName('sese');
  for (i = 0; i < y.length; i++) {
    if (elmnt == y[i]) {
      arrNo.push(i)
    } else {
      y[i].classList.remove('slar-active');
    }
  }
  for (i = 0; i < x.length; i++) {
    if (arrNo.indexOf(i)) {
      x[i].classList.add('sehi');
    }
  }
}

/* Save Scroll Position when Refreshing Page */
document.addEventListener('DOMContentLoaded', function(event) {
    var scrollpos = localStorage.getItem('scrollpos');
    if (scrollpos) window.scrollTo(0, scrollpos);
    
    // Fix duplicate cursors with delay to ensure all scripts have run
    setTimeout(() => {
        cleanupDuplicateCursors();
        
        // Set up observer to prevent future duplication
        setupCursorMutationObserver();
    }, 500);
});

// Function to clean up duplicate cursors - enhanced with complete removal and recreation
function cleanupDuplicateCursors() {
    // REMOVE ALL CURSORS AND RECREATE THEM
    // This is the most reliable approach to prevent duplicates
    
    // First, remove all existing cursors
    const allLeftCursors = document.querySelectorAll('.left-cursor');
    const allRightCursors = document.querySelectorAll('.right-cursor');
    
    
    allLeftCursors.forEach(cursor => {
        if (cursor.parentNode) {
            cursor.parentNode.removeChild(cursor);
        }
    });
    
    allRightCursors.forEach(cursor => {
        if (cursor.parentNode) {
            cursor.parentNode.removeChild(cursor);
        }
    });
    
    // Now recreate a single set of cursors in the proper container
    const fretboardContainer = document.querySelector('.fretboardcontainer');
    if (fretboardContainer) {
        // Create new left cursor
        const newLeftCursor = document.createElement('div');
        newLeftCursor.className = 'left-cursor';
        newLeftCursor.setAttribute('onclick', 'leftCursorClick()');
        
        // Create new right cursor
        const newRightCursor = document.createElement('div');
        newRightCursor.className = 'right-cursor';
        newRightCursor.setAttribute('onclick', 'rightCursorClick()');
        
        // Insert at the beginning of the fretboard container
        const firstChild = fretboardContainer.firstChild;
        if (firstChild) {
            fretboardContainer.insertBefore(newLeftCursor, firstChild);
            fretboardContainer.insertBefore(newRightCursor, firstChild);
        } else {
            fretboardContainer.appendChild(newLeftCursor);
            fretboardContainer.appendChild(newRightCursor);
        }
        
        // Make them visible
        setTimeout(() => {
            newLeftCursor.style.display = 'flex';
            newLeftCursor.style.visibility = 'visible';
            newLeftCursor.style.opacity = '1';
            newLeftCursor.style.position = 'absolute';
            
            newRightCursor.style.display = 'flex';
            newRightCursor.style.visibility = 'visible';
            newRightCursor.style.opacity = '1';
            newRightCursor.style.position = 'absolute';
            
            // Clear any content inside to ensure SVG background images are visible
            newLeftCursor.innerHTML = '';
            newRightCursor.innerHTML = '';
            
            // Trigger any custom cursor initialization that might be available
            if (typeof initCustomCursors === 'function') {
                initCustomCursors();
            }
        }, 100);
    }
}

// Add a MutationObserver to detect and fix cursor issues dynamically
function setupCursorMutationObserver() {
    // Create an observer instance
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' && 
                (mutation.addedNodes.length > 0 || mutation.removedNodes.length > 0)) {
                // Check if we have duplicate cursors after DOM changes
                const leftCursors = document.querySelectorAll('.left-cursor');
                const rightCursors = document.querySelectorAll('.right-cursor');
                
                if (leftCursors.length > 1 || rightCursors.length > 1) {
                    cleanupDuplicateCursors();
                }
            }
        });
    });
    
    // Start observing the document body for DOM changes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Store observer reference to potentially disconnect later
    window.cursorMutationObserver = observer;
}

window.onbeforeunload = function(e) {
    localStorage.setItem('scrollpos', window.scrollY);
};

// Info Icon
document.addEventListener('DOMContentLoaded', function() {
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

// Sidebar
document.addEventListener('DOMContentLoaded', function() {
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
              document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
                  const label = document.querySelector(`label[for='${toggle.id}']`);
                  if (label) {
                      label.removeAttribute('style'); // Remove all inline styles
                  }
              });
          }
      });

      document.addEventListener('click', function(event) {
          // Only close the menu if clicking outside of it
          if (menuCheckbox.checked && !menuToggle.contains(event.target) && !menu.contains(event.target)) {
              menuCheckbox.checked = false;
              menu.style.left = '-300px';
              leftCursor.style.zIndex = '10';
              document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
                  const label = document.querySelector(`label[for='${toggle.id}']`);
                  if (label) {
                      label.removeAttribute('style'); // Remove all inline styles
                  }
              });
          }
      });

      document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
          toggle.addEventListener('click', function() {
              document.querySelectorAll('.dropdown-toggle').forEach(innerToggle => {
                  const label = document.querySelector(`label[for='${innerToggle.id}']`);
                  if (innerToggle.checked && label) {
                      label.style.color = '#FF877A'; // Change color when active
                  } else if (label) {
                      label.removeAttribute('style'); // Remove all inline styles
                  }
              });
          });
      });
  }
});




// Sidebar Script
function toggleDropdown(currentCheckbox) {
  const dropdowns = document.querySelectorAll('.dropdown-toggle');
  dropdowns.forEach(dropdown => {
      if (dropdown !== currentCheckbox) {
          dropdown.checked = false;
      }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  // Function to set a cookie
  function setCookie(name, value, days) {
    var expires = "";
    if (days) {
      var date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Lax";
  }

  // Function to get a cookie value
  function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  }

  // Function to erase a cookie
  function eraseCookie(name) {
    document.cookie = name + '=; Max-Age=-99999999; path=/; SameSite=Lax';
  }

  // Function For Getting Note Names on Dots
  function getNoteNameFromData() {
    var noteNames = document.querySelectorAll('.note .notename');
    noteNames.forEach(function(noteName) {
      var parentNote = noteName.closest('.note');
      var activeImage = parentNote.querySelector('img.active');
      if (activeImage) {
        noteName.classList.add('active');
        noteName.style.visibility = 'visible'; // Ensure visibility
      }
    });
    document.body.classList.add('show-notes');
    var button = document.getElementById('show_note_name_button');
    button.setAttribute('onclick', 'hideNoteNames()');
    button.innerHTML = 'Only Tones';
  }

  // Function For Hiding Note Names on Dots
  function hideNoteNames() {
    var notenames = document.querySelectorAll('.notename.active');
    notenames.forEach(function(n) {
      n.classList.remove('active');
      n.style.visibility = 'hidden'; // Hide visibility
    });
    document.body.classList.remove('show-notes');
    var button = document.getElementById('show_note_name_button');
    button.setAttribute('onclick', 'getNoteNameFromData()');
    button.innerHTML = 'Show Note Names';
  }

  // Check if the 'showNoteName' cookie is set to 'true' AND the button state allows it
  // NOTE: Removing the automatic call based on cookie for scale/arpeggio views.
  // The button state should be the source of truth after initial load.
  /*
  if (getCookie('showNoteName') === 'true') {
     // Check button state before activating? Might be complex due to timing.
     // Let's disable automatic activation for now. User can click the button.
     // getNoteNameFromData();
  }
  */
  // Event listener for keydown events
  document.addEventListener('keydown', function(event) {
    // Check if the 'Escape' key is pressed
    if (event.key === 'Escape') {
      var closeUnifiedButton = document.getElementById('closeUnifiedOverlay');
      if (closeUnifiedButton) {
        closeUnifiedButton.click();
      } else {
        // Fallback to toggling the menu closed
        var menu = document.getElementById('unifiedOverlayMenu');
        if (menu && (menu.style.display === 'flex' || menu.style.display === 'block')) {
          // Use global toggle function
          toggleUnifiedMenu();
        }
      }
    }
    // Check if the 'i' key is pressed
    if (event.key === 'i' || event.key === 'I') {
      var infoToggle = document.getElementById('infoToggle');
      if (infoToggle) {
        infoToggle.click();
      }
    }
    // Right arrow key functionality has been removed
    // Check if the up arrow key is pressed
    if (event.key === 'ArrowUp') { 
      increaseRoot();
    }
    // Check if the down arrow key is pressed
    if (event.key === 'ArrowDown') {
      decreaseRoot();
    }
    // Check if the 'p' key is pressed
    if (event.key === 'p' || event.key === 'P') {
      var unifiedToggle = document.getElementById('unifiedMenuToggle');
      if (unifiedToggle) {
        unifiedToggle.click();
      }
    }
    // Check if the 'n' key is pressed
    if (event.key === 'n' || event.key === 'N') {
      if (document.body.classList.contains('show-notes')) {
        hideNoteNames();
        eraseCookie('showNoteName');
      } else {
        getNoteNameFromData();
        setCookie('showNoteName', 'true', 7); // Set cookie to remember the state for 7 days
      }
    }
  });

  // Add click event listener to the button
  var showNoteNameButton = document.getElementById('show_note_name_button');
  if (showNoteNameButton) {
    showNoteNameButton.addEventListener('click', function() {
      if (document.body.classList.contains('show-notes')) {
        hideNoteNames();
        eraseCookie('showNoteName');
      } else {
        getNoteNameFromData();
        setCookie('showNoteName', 'true', 7); // Set cookie to remember the state for 7 days
      }
    });
  }
  // Function to sync the height of the lowest string div with spacing-top
  // Function definition moved to global scope

  // Initial sync removed - now handled by unified_menu.js after config is applied

  // Sync again on window resize
  window.addEventListener('resize', syncLowestStringHeight);

});
