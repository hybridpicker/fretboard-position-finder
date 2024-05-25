document.addEventListener("DOMContentLoaded", function() {
  const overlayMenu = document.getElementById('overlayMenu');
  overlayMenu.style.display = 'none';

  customizeSelectField("sfbsfnos");
  customizeSelectField("sfbsfpos");
  customizeSelectField("sfbsf");

  // If the user clicks anywhere outside the select box, close all select boxes
  document.addEventListener("click", closeAllSelect);

  var pos_val = document.getElementById('position_select').value;
  var url_string = window.location.href;
  var url = new URL(url_string);
  pos_val = url.searchParams.get("position_select");
  if (pos_val) {
    getTonesFromDataScales(pos_val);
  } else {
    getTonesFromDataScales('0');
  }
});


function multiple_notes(tone_name, y) {
  var url_string = window.location.href;
  var url = new URL(url_string);
  var pos_val = url.searchParams.get("position_select");

  // Check if positions are clicked
  if (!pos_val) {
    return; // Close Function at the Start
  }
  for (var key in scale_data[y]) {
      if (scale_data[y].hasOwnProperty(key)) {
          for (var z in scale_data[y][key][0]["tones"]) {
              var tone_name = scale_data[y][key][0]["tones"][z];
              var elements = document.querySelectorAll('.' + tone_name + '.active');
              if (elements.length > 2) {
                  var url_string = window.location.href;
                  var url = new URL(url_string);
                  var pos_val = url.searchParams.get("position_select");
                  if (pos_val != 0) {
                      var list_of_strings = [];
                      for (var variable in frets) {
                          for (var string in string_array) {
                              var selector = '.' + frets[variable] + '.' + string_array[string] + ' .' + tone_name + '.active';
                              var activeElements = document.querySelectorAll(selector);
                              if (activeElements.length != 0) {
                                  list_of_strings.push(string_array[string]);
                              }
                          }
                      }
                      if (list_of_strings.length > 1) {
                          var first_string = [];
                          var second_string = [];
                          var available_strings = [];
                          for (var i in list_of_strings) {
                              var string = list_of_strings[i];
                              for (var fret in frets) {
                                  var selector = '.' + string + '.' + frets[fret] + ' .active';
                                  var activeElements = document.querySelectorAll(selector);
                                  if (activeElements.length != 0) {
                                      if (i > 0) {
                                          second_string.push(fret);
                                      } else {
                                          first_string.push(fret);
                                      }
                                      available_strings.push(string);
                                  }
                              }
                          }
                          if (first_string.length > 0 && second_string.length > 0) {
                              var first_string_range = first_string[first_string.length - 1] - first_string[0];
                              var second_string_range = second_string[second_string.length - 1] - second_string[0];
                              var first_string_name = available_strings[0];
                              var second_string_name = available_strings[available_strings.length - 1];

                              if (first_string_range > second_string_range) {
                                  deactivateActiveNotes(first_string_name, tone_name);
                              } else {
                                  deactivateActiveNotes(second_string_name, tone_name);
                              }
                          }
                      }
                  }
              }
          }
      }
  }
}

function deactivateActiveNotes(string, tone_name) {
  var elements = document.querySelectorAll('.' + string + ' .' + tone_name + '.active');
  elements.forEach(function(element) {
      element.classList.remove('active');
  });
}



function avoid_four_notes_on_string(){
  var avoid_strings = [string_array[0], (string_array[string_array.length - 1])]
  for (x in avoid_strings){
    var element = document.querySelectorAll('.' + avoid_strings[x] +' .active > img')
    if (element.length > 3){
      if (avoid_strings[x] == avoid_strings[1]){
        element[0].classList.remove("active")
      }
      else{
        element[3].classList.remove("active")
      }
    }
  }
}

function getTonesFromDataScales(y){
  /* First find all notes that are active and reset the fretboard*/
  resetFretboard()
  /* x sets the id of inversions */
  var i = 0;
  for (var key in scale_data[y]) {
    if (scale_data[y].hasOwnProperty(key)) {
      for (var z in scale_data[y][key][0]["tones"]) {
        var tone_name = scale_data[y][key][0]["tones"][z]
        var QuerySelect = document.querySelector('.' + key + ' img.tone.' + tone_name);
        if (QuerySelect != null){
          QuerySelect.classList.add('active');
        }
        /* Check every note that has a defined Query for not activating all chord tones */
        var QuerySelect = document.querySelector('.' + key + ' .note.' + tone_name);
        if (QuerySelect != null){
          QuerySelect.classList.add('active');
        }
        element = document.querySelectorAll('.' + tone_name + '.active');
      }
    }
  }

  /*Check if multiple tones are in position */
  multiple_notes(tone_name, y);


  /* Check if not 4 notes on highest or lowest string */
  var pos_val = document.getElementById('position_select').value
  if (pos_val != 0){
    avoid_four_notes_on_string();
  }

  /* Change for RootNote Color */
  for (var key in scale_data.root) {
    if (scale_data.root.hasOwnProperty(key)) {
      var root = scale_data.root[key]
      for (i = 0; i < string_array.length; i++) {
        string = string_array[i];
        var root_note_image = document.querySelector('.' + string + ' img.tone.active.' + root);
        if (root_note_image != null){
          root_note_image.setAttribute('src', '/static/media/red_dot_24.svg');
          root_note_image.classList.add('active');
          root_note_image.classList.add('root')
        }
      }
    }
  }
}


function multiple_notes(tone_name, y) {
  var url_string = window.location.href;
  var url = new URL(url_string);
  var pos_val = url.searchParams.get("position_select");

  // Check if positions are clicked
  if (!pos_val) {
    return; // Close Function at the Start
  }
  for (var key in scale_data[y]) {
      if (scale_data[y].hasOwnProperty(key)) {
          for (var z in scale_data[y][key][0]["tones"]) {
              var tone_name = scale_data[y][key][0]["tones"][z];
              var elements = document.querySelectorAll('.' + tone_name + '.active');
              if (elements.length > 2) {
                  var url_string = window.location.href;
                  var url = new URL(url_string);
                  var pos_val = url.searchParams.get("position_select");
                  if (pos_val != 0) {
                      var list_of_strings = [];
                      for (var variable in frets) {
                          for (var string in string_array) {
                              var selector = '.' + frets[variable] + '.' + string_array[string] + ' .' + tone_name + '.active';
                              var activeElements = document.querySelectorAll(selector);
                              if (activeElements.length != 0) {
                                  list_of_strings.push(string_array[string]);
                              }
                          }
                      }
                      if (list_of_strings.length > 1) {
                          var first_string = [];
                          var second_string = [];
                          var available_strings = [];
                          for (var i in list_of_strings) {
                              var string = list_of_strings[i];
                              for (var fret in frets) {
                                  var selector = '.' + string + '.' + frets[fret] + ' .active';
                                  var activeElements = document.querySelectorAll(selector);
                                  if (activeElements.length != 0) {
                                      if (i > 0) {
                                          second_string.push(fret);
                                      } else {
                                          first_string.push(fret);
                                      }
                                      available_strings.push(string);
                                  }
                              }
                          }
                          if (first_string.length > 0 && second_string.length > 0) {
                              var first_string_range = first_string[first_string.length - 1] - first_string[0];
                              var second_string_range = second_string[second_string.length - 1] - second_string[0];
                              var first_string_name = available_strings[0];
                              var second_string_name = available_strings[available_strings.length - 1];

                              if (first_string_range > second_string_range) {
                                  deactivateActiveNotes(first_string_name, tone_name);
                              } else {
                                  deactivateActiveNotes(second_string_name, tone_name);
                              }
                          }
                      }
                  }
              }
          }
      }
  }
}

function deactivateActiveNotes(string, tone_name) {
  var elements = document.querySelectorAll('.' + string + ' .' + tone_name + '.active');
  elements.forEach(function(element) {
      element.classList.remove('active');
  });
}



function avoid_four_notes_on_string(){
  var avoid_strings = [string_array[0], (string_array[string_array.length - 1])]
  for (x in avoid_strings){
    var element = document.querySelectorAll('.' + avoid_strings[x] +' .active > img')
    if (element.length > 3){
      if (avoid_strings[x] == avoid_strings[1]){
        element[0].classList.remove("active")
      }
      else{
        element[3].classList.remove("active")
      }
    }
  }
}

function getTonesFromDataScales(y){
  /* First find all notes that are active and reset the fretboard*/
  resetFretboard()
  /* x sets the id of inversions */
  var i = 0;
  for (var key in scale_data[y]) {
    if (scale_data[y].hasOwnProperty(key)) {
      for (var z in scale_data[y][key][0]["tones"]) {
        var tone_name = scale_data[y][key][0]["tones"][z]
        var QuerySelect = document.querySelector('.' + key + ' img.tone.' + tone_name);
        if (QuerySelect != null){
          QuerySelect.classList.add('active');
        }
        /* Check every note that has a defined Query for not activating all chord tones */
        var QuerySelect = document.querySelector('.' + key + ' .note.' + tone_name);
        if (QuerySelect != null){
          QuerySelect.classList.add('active');
        }
        element = document.querySelectorAll('.' + tone_name + '.active');
      }
    }
  }

  /*Check if multiple tones are in position */
  multiple_notes(tone_name, y);


  /* Check if not 4 notes on highest or lowest string */
  var pos_val = document.getElementById('position_select').value
  if (pos_val != 0){
    avoid_four_notes_on_string();
  }

  /* Change for RootNote Color */
  for (var key in scale_data.root) {
    if (scale_data.root.hasOwnProperty(key)) {
      var root = scale_data.root[key]
      for (i = 0; i < string_array.length; i++) {
        string = string_array[i];
        var root_note_image = document.querySelector('.' + string + ' img.tone.active.' + root);
        if (root_note_image != null){
          root_note_image.setAttribute('src', '/static/media/red_dot_24.svg');
          root_note_image.classList.add('active');
          root_note_image.classList.add('root')
        }
      }
    }
  }
}

// Position Cursor Functions
function updateCursorVisibility(pos_val, max_pos) {
var leftCursor = document.querySelector('.left-cursor');
var rightCursor = document.querySelector('.right-cursor');

// Update visibility based on pos_val and max_pos
if (pos_val > 0) {
  leftCursor.style.display = 'block';
} else {
  leftCursor.style.display = 'none';
}

if (pos_val < max_pos - 1) {
  rightCursor.style.display = 'block';
} else {
  rightCursor.style.display = 'none';
}
}

function leftCursorClick() {
var url_string = window.location.href;
var url = new URL(url_string);
var pos_val = parseInt(url.searchParams.get("position_select")); // Convert pos_val to a number

// Filter the keys to count only numeric keys
var max_pos = Object.keys(scale_data).filter(key => !isNaN(key)).length; // Number of numeric positions in the scale_data object

if (pos_val > 0) { // Ensure the new position is not less than 0
  var new_pos_val = pos_val - 1;
  document.getElementById('position_select').value = new_pos_val;
  document.getElementById("fretboard_form").submit();
  updateCursorVisibility(new_pos_val, max_pos);
} else {
  return;
}
}

function rightCursorClick() {
var url_string = window.location.href;
var url = new URL(url_string);
var pos_val = url.searchParams.get("position_select"); // Get the position value from the URL

// Check if the URL is empty and set pos_val to 0 if true
if (pos_val === null || pos_val === "") {
  pos_val = 0;
} else {
  pos_val = parseInt(pos_val); // Convert pos_val to a number
}

// Filter the keys to count only numeric keys
var max_pos = Object.keys(scale_data).filter(key => !isNaN(key)).length; // Number of numeric positions in the scale_data object

if (pos_val < max_pos - 1) { // Ensure the new position is not greater than max_pos - 1
  var new_pos_val = pos_val + 1;
  document.getElementById('position_select').value = new_pos_val;
  document.getElementById("fretboard_form").submit();
  updateCursorVisibility(new_pos_val, max_pos);
} else {
  return;
}
}

// Initial setup based on current position value
document.addEventListener('DOMContentLoaded', function() {
var url_string = window.location.href;
var url = new URL(url_string);
var pos_val = url.searchParams.get("position_select"); // Get the position value from the URL

// Check if the URL is empty and set pos_val to 0 if true
if (pos_val === null || pos_val === "") {
  pos_val = 0;
} else {
  pos_val = parseInt(pos_val); // Convert pos_val to a number
}

// Filter the keys to count only numeric keys
var max_pos = Object.keys(scale_data).filter(key => !isNaN(key)).length; // Number of numeric positions in the scale_data object

updateCursorVisibility(pos_val, max_pos);
});


  /**
   * Customize the select field by creating custom dropdown elements
   */
  function customizeSelectField(className) {
    var x = document.getElementsByClassName(className);
    for (var i = 0; i < x.length; i++) {
      var selElmnt = x[i].getElementsByTagName("select")[0];
      var a = document.createElement("DIV");
      a.setAttribute("class", "sese");
      a.innerHTML = selElmnt.options[selElmnt.selectedIndex].innerHTML;
      x[i].appendChild(a);
  
      var b = document.createElement("DIV");
      b.setAttribute("class", "slit sehi");
      for (var j = 1; j < selElmnt.length; j++) {
        var c = document.createElement("DIV");
        c.innerHTML = selElmnt.options[j].innerHTML;
        c.addEventListener("click", function(e) {
          var y, k, s, h;
          s = this.parentNode.parentNode.getElementsByTagName("select")[0];
          h = this.parentNode.previousSibling;
          for (var i = 0; i < s.length; i++) {
            if (s.options[i].innerHTML == this.innerHTML) {
              s.selectedIndex = i;
              h.innerHTML = this.innerHTML;
              y = this.parentNode.getElementsByClassName("swasd");
              for (k = 0; k < y.length; k++) {
                y[k].removeAttribute("class");
              }
              this.setAttribute("class", "swasd");
              break;
            }
          }
          h.click();
          document.getElementById("fretboard_form").submit();
        });
        b.appendChild(c);
      }
      x[i].appendChild(b);
      a.addEventListener("click", function(e) {
        e.stopPropagation();
        closeAllSelect(this);
        this.nextSibling.classList.toggle("sehi");
        this.classList.toggle("slar-active");
      });
    }
  }
  
  /**
   * Close all select boxes in the document, except the current select box
   */
  function closeAllSelect(elmnt) {
    var x = document.getElementsByClassName("slit");
    var y = document.getElementsByClassName("sese");
    var arrNo = [];
    for (var i = 0; i < y.length; i++) {
      if (elmnt == y[i]) {
        arrNo.push(i);
      } else {
        y[i].classList.remove("slar-active");
      }
    }
    for (var i = 0; i < x.length; i++) {
      if (arrNo.indexOf(i)) {
        x[i].classList.add("sehi");
      }
    }
  }
  
  const notes = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];
const validRoots = Array.from({length: 17}, (_, i) => i + 1).filter(n => ![2, 5, 9, 12, 15].includes(n)); // [1, 3, 4, 6, 7, 8, 10, 11, 13, 14, 16, 17]

function changeScaleRoot(noteChange) {
    var urlParams = new URLSearchParams(window.location.search);
    var root = parseInt(urlParams.get('root')) || 1; // Fallback to 1 if 'root' param is missing or invalid

    // Find the current index in validRoots
    var currentIndex = validRoots.indexOf(root);

    // Calculate new index cyclically
    var newIndex = (currentIndex + noteChange + validRoots.length) % validRoots.length;

    var newRoot = validRoots[newIndex];
    urlParams.set('root', newRoot);
    window.history.replaceState(null, null, "?" + urlParams.toString());

    // Only update tones if pos_val is specified
    if (urlParams.has('position_select')) {
        var pos_val = urlParams.get('position_select');
        var note_range = urlParams.get('note_range') || (document.getElementById('note_range') ? document.getElementById('note_range').value : null);
        getTonesFromDataScales(pos_val);
    }

    // Reload the page with new URL parameters
    window.location.search = urlParams.toString();
}

function increaseRoot() {
    changeScaleRoot(1);
}

function decreaseRoot() {
    changeScaleRoot(-1);
}
