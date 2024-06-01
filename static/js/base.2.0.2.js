var string_array = ['eString', 'bString', 'gString', 'dString', 'AString', 'ELowString']

var frets = ['one','two','three','four','five','six',
            'seven','eight','nine','ten','eleven', 'twelve',
            'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen']

// Define the NOTES variable
const NOTES = {
    'eString': [['f2'], ['gb2', 'fs2'], ['g2'], ['ab2', 'gs2'], ['a2'], ['bb2', 'as2'], ['b2'], ['c3'], ['db3', 'cs3'], ['d3'], ['eb3', 'ds3'], ['e3'], ['f3'], ['gb3', 'fs3'], ['g3'], ['ab3', 'gs3'], ['a3']],
    'bString': [['c2'], ['db2', 'cs2'], ['d2'], ['eb2', 'ds2'], ['e2'], ['f2'], ['gb2', 'fs2'], ['g2'], ['ab2', 'gs2'], ['a2'], ['bb2', 'as2'], ['b2'], ['c3'], ['db3', 'cs3'], ['d3'], ['eb3', 'ds3'], ['e3']],
    'gString': [['ab1', 'gs1'], ['a1'], ['bb1', 'as1'], ['b1'], ['c2'], ['db2', 'cs2'], ['d2'], ['eb2', 'ds2'], ['e2'], ['f2'], ['gb2', 'fs2'], ['g2'], ['ab2', 'gs2'], ['a2'], ['bb2', 'as2'], ['b2'], ['c3']],
    'dString': [['eb1', 'ds1'], ['e1'], ['f1'], ['gb1', 'fs1'], ['g1'], ['ab1', 'gs1'], ['a1'], ['bb1', 'as1'], ['b1'], ['c2'], ['db2', 'cs2'], ['d2'], ['eb2', 'ds2'], ['e2'], ['f2'], ['gb2', 'fs2'], ['g2']],
    'AString': [['bb0', 'as0'], ['b0'], ['c1'], ['db1', 'cs1'], ['d1'], ['eb1', 'ds1'], ['e1'], ['f1'], ['gb1', 'fs1'], ['g1'], ['ab1', 'gs1'], ['a1'], ['bb1', 'as1'], ['b1'], ['c2'], ['db2', 'cs2'], ['d2']],
    'ELowString': [['f0'], ['gb0', 'fs0'], ['g0'], ['ab0', 'gs0'], ['a0'], ['bb0', 'as0'], ['b0'], ['c1'], ['db1', 'cs1'], ['d1'], ['eb1', 'ds1'], ['e1'], ['f1'], ['gb1', 'fs1'], ['g1'], ['ab1', 'gs1'], ['a1']],
}

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

      const isRoot = activeElement.classList.contains('root');
      const newSrc = isRoot ? '/static/media/red_circle_active_24.svg' : '/static/media/yellow_circle_active_24.svg';
      const revertSrc = isRoot ? '/static/media/red_circle.svg' : '/static/media/yellow_circle.svg';

      activeElement.setAttribute('src', newSrc);
      setTimeout(() => {
          activeElement.setAttribute('src', revertSrc);
      }, 300);
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

  // Reset the 'src' attribute for all tone elements
  const toneElements = document.querySelectorAll('.tone');
  toneElements.forEach(element => element.setAttribute('src', '/static/media/yellow_circle.svg'));
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
});

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

// Keyboard Handlers
document.addEventListener('DOMContentLoaded', function() {
  // Event listener for keydown events
  document.addEventListener('keydown', function(event) {
      // Check if the 'Escape' key is pressed
      if (event.key === 'Escape') {
          var closeButton = document.getElementById('closeOverlay');
          var closeButtonChords = document.getElementById('closeOverlayChords');
          if (closeButton) {
              closeButton.click();
          } else if (closeButtonChords) {
              closeButtonChords.click();
          }
      }
      // Check if the 'i' key is pressed
      if (event.key === 'i' || event.key === 'I') {
          var infoToggle = document.getElementById('infoToggle');
          if (infoToggle) {
              infoToggle.click();
          }
      }
      // Check if the left arrow key is pressed
      if (event.key === 'ArrowLeft') {
          leftCursorClick();
      }
      // Check if the right arrow key is pressed
      if (event.key === 'ArrowRight') {
          rightCursorClick();
      }
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
          var overlayToggle = document.getElementById('overlayToggle');
          var overlayToggleChords = document.getElementById('overlayToggleChords');
          if (overlayToggle) {
              overlayToggle.click();
          } else if (overlayToggleChords) {
              overlayToggleChords.click();
          }
      }
  });
});