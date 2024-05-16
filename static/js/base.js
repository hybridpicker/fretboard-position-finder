var string_array = ['eString', 'bString', 'gString', 'dString', 'AString', 'ELowString']

var frets = ['one','two','three','four','five','six',
            'seven','eight','nine','ten','eleven', 'twelve',
            'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen']

/**
 * Play a tone and update the UI based on the 'root' class.
 * @param {string} tone - The name of the tone to play.
 * @param {string} stringName - The name of the string where the tone is played.
 */

function playTone(tone, stringName) {

  // Determine the element to update
  const element = document.querySelector(`.${stringName} img.tone.${tone}.active`);
  
  // Check if element exists and is active
  if (element && element.classList.contains('active')) {
    // Initialize audio and play
    const audio = new Audio(`static/media/tone_sounds/${tone}.mp3`);
    audio.play();

    const isRoot = element.classList.contains('root');
    const newSrc = isRoot ? '/static/media/red_dot_active.svg' : '/static/media/yellow_dot_active.svg';
    const revertSrc = isRoot ? '/static/media/red_dot.svg' : '/static/media/yellow_dot.svg';

    // Update the UI
    element.setAttribute('src', newSrc);
    setTimeout(() => {
      element.setAttribute('src', revertSrc);
    }, 300);
  } else {
    console.warn(`Element for tone ${tone} on string ${stringName} is not active or not found.`);
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
  toneElements.forEach(element => element.setAttribute('src', '/static/media/yellow_dot.svg'));
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
      elements[x].classList.remove("active");
    }
  }
}

function getToneNameFromDataChords() {
  var button = document.getElementById("show_tension_button")
  button.setAttribute("onclick","show_tension_notes_chords()")
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
      for (var z in scale_data[y][key][0]["tones"]) {
        var tone_name = scale_data[y][key][0]["tones"][z]
        var QuerySelect = document.querySelector('.' + key + ' .notename.' + tone_name);
        var image = document.querySelector('.' + key + ' .' + tone_name + ' img.active');
        if (image){
          if (QuerySelect != null){
            QuerySelect.classList.add("active")
          }
        }
      }
    }
  }
  var button = document.getElementById("show_note_name_button")
  button.setAttribute("onclick","getNotePicFromData()")
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
  var button = document.getElementById("show_note_name_button")
  button.setAttribute("onclick","getNoteNameFromData()")
  button.innerHTML = 'Note Name';
}

function closeAllSelect(elmnt) {
  /*  Close all select boxes in the document,
  except the current select box: */
  var x, y, i, arrNo = [];
  x = document.getElementsByClassName("slit");
  y = document.getElementsByClassName("sese");
  for (i = 0; i < y.length; i++) {
    if (elmnt == y[i]) {
      arrNo.push(i)
    } else {
      y[i].classList.remove("slar-active");
    }
  }
  for (i = 0; i < x.length; i++) {
    if (arrNo.indexOf(i)) {
      x[i].classList.add("sehi");
    }
  }
}


function leftCursorClick() {
  var url_string = window.location.href;
  var url = new URL(url_string);
  var pos_val = parseInt(url.searchParams.get("position_select")); // Convert pos_val to a number
  console.log(pos_val);

  // Filter the keys to count only numeric keys
  var max_pos = Object.keys(scale_data).filter(key => !isNaN(key)).length; // Number of numeric positions in the scale_data object

  if (pos_val > 0) { // Ensure the new position is not less than 0
    var new_pos_val = pos_val - 1;
    console.log('Decremented position to', new_pos_val);
    document.getElementById('position_select').value = new_pos_val;
    document.getElementById("fretboard_form").submit();
  } else {
    console.log('Already at the lowest position, cannot decrement further');
  }
}

function rightCursorClick() {
  var url_string = window.location.href;
  var url = new URL(url_string);
  var pos_val = parseInt(url.searchParams.get("position_select")); // Convert pos_val to a number
  console.log(pos_val);

  // Filter the keys to count only numeric keys
  var max_pos = Object.keys(scale_data).filter(key => !isNaN(key)).length; // Number of numeric positions in the scale_data object

  if (pos_val < max_pos - 1) { // Ensure the new position is not greater than max_pos - 1
    var new_pos_val = pos_val + 1;
    console.log('Incremented position to', new_pos_val);
    document.getElementById('position_select').value = new_pos_val;
    document.getElementById("fretboard_form").submit();
  } else {
    console.log('Already at the highest position, cannot increment further');
  }
}

// Event listener for keyboard inputs
document.addEventListener('keydown', function(event) {
  if (event.key === 'ArrowLeft') { // Left arrow key
    leftCursorClick();
  } else if (event.key === 'ArrowRight') { // Right arrow key
    rightCursorClick();
  }
});


/* Save Scroll Position when Refreshing Page */
document.addEventListener("DOMContentLoaded", function(event) {
    var scrollpos = localStorage.getItem('scrollpos');
    if (scrollpos) window.scrollTo(0, scrollpos);
});

window.onbeforeunload = function(e) {
    localStorage.setItem('scrollpos', window.scrollY);
};
