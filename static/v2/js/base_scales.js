
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

// Event listener for keyboard inputs
document.addEventListener('keydown', function(event) {
  if (event.key === 'ArrowLeft') { // Left arrow key
    leftCursorClick();
  } else if (event.key === 'ArrowRight') { // Right arrow key
    rightCursorClick();
  }
});
