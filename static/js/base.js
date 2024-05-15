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
          root_note_image.setAttribute('src', '/static/media/red_dot.svg');
          root_note_image.classList.add('active');
          root_note_image.classList.add('root')
        }
      }
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

function getTonesFromDataChords(x, y){
  resetFretboard()
  /* x sets the id of inversions */
  var i = 0;
  for (var key in voicing_data[y][x][0]) {
    if (voicing_data[y][x][0].hasOwnProperty(key)) {
      var tone = voicing_data[y][x][0][key][0]
      var tone_name = voicing_data[y][x][0][key][2]

      var QuerySelect = document.querySelector('.' + key + ' img.tone.' + tone);
      QuerySelect.classList.add('active');
      var QuerySelect = document.querySelector('.' + key + ' .notename.' + tone);
      QuerySelect.classList.add('active');
      /* Check every note that has a defined Query for not activating all chord tones */
      var QuerySelect = document.querySelector('.' + key + ' .note.' + tone);
      QuerySelect.classList.add('active');
    }
  }

  /* Change for RootNote Color */
  for (var key in voicing_data.root) {
    if (voicing_data.root.hasOwnProperty(key)) {
      var root = voicing_data.root[key]
      for (i = 0; i < string_array.length; i++) {
        string = string_array[i];
        var root_note_image = document.querySelector('.' + string + ' img.tone.active.' + root);
        if (root_note_image != null){
          root_note_image.setAttribute('src', '/static/media/red_dot.svg');
          root_note_image.classList.add('active');
          root_note_image.classList.add('root')
        }
      }
    }
  }
}

function show_tension_notes_chords() {
  var x = document.getElementById('position_select').value
  var y = document.getElementById('note_range').value

  var tension_elements = document.querySelectorAll('.tensionname');
  if (tension_elements != undefined){
    for (var i=0; i<tension_elements.length; i++) {
      tension_elements[i].remove();
    }
  }

  var i = 0;
  for (var key in voicing_data[y][x][0]) {
    if (voicing_data[y][x][0].hasOwnProperty(key)) {
      var tone = voicing_data[y][x][0][key][0]
      var tension_name = voicing_data[y][x][0][key][1]

      var QuerySelect = '.' + key + ' .notename.' + tone + '.active';
      var selection = document.getElementsByClassName("note active " + tone)[0];
      if (typeof selection !== "undefined") {
          /* creating a div for tension notes */
          var node = document.createElement("DIV");
          node.className = "tensionname";
          document.getElementsByClassName("active note " + tone)[0].appendChild(node);
          var textnode = document.createTextNode(tension_name);
          node.appendChild(textnode);
          /* Remove class for not showing Notename */
          var QuerySelect = document.querySelector('.' + key + ' .notename.' + tone + '.active');
          if (QuerySelect != null){
            QuerySelect.classList.remove("active")
          }
      }
    }
    /* add class active for showing up */
    var tension_names = document.querySelectorAll('.tensionname')
    for (var i=0; i<tension_names.length; i++) {
      tension_names[i].classList.add("active");
    }
    var button = document.getElementById("show_tension_button")
    button.setAttribute("onclick","getToneNameFromDataChords()")
    button.innerHTML = 'Tone Names';
  }
}

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
function navBarFretboardChords(class_name){
  var x, i, j, selElmnt, a, b, c;
  /* Look for any elements with the class "sfbsf": */
  x = document.getElementsByClassName(class_name);
  for (i = 0; i < x.length; i++) {
    selElmnt = x[i].getElementsByTagName("select")[0];
    /* For each element, create a new DIV that will act as the selected item: */
    a = document.createElement("DIV");
    a.setAttribute("class", "sese");
    a.innerHTML = selElmnt.options[selElmnt.selectedIndex].innerHTML;
    x[i].appendChild(a);
    /* For each element, create a new DIV that will contain the option list: */
    b = document.createElement("DIV");
    b.setAttribute("class", "slit sehi");
    for (j = 1; j < selElmnt.length; j++) {
      /* For each option in the original select element,
      create a new DIV that will act as an option item: */
      c = document.createElement("DIV");
      c.innerHTML = selElmnt.options[j].innerHTML;
      c.addEventListener("click", function(e) {
        /* When an item is clicked, update the original select box,
        and the selected item: */
        var y, i, k, s, h;
        s = this.parentNode.parentNode.getElementsByTagName("select")[0];
        h = this.parentNode.previousSibling;
        for (i = 0; i < s.length; i++) {
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
        var pos_val = document.getElementById('position_select').value
        var note_range = document.getElementById('note_range').value
        getTonesFromDataChords(pos_val, note_range)
      });
      b.appendChild(c);
    }
    x[i].appendChild(b);
    a.addEventListener("click", function(e) {
      /* When the select box is clicked, close any other select boxes,
      and open/close the current select box: */
      e.stopPropagation();
      closeAllSelect(this);
      this.nextSibling.classList.toggle("sehi");
      this.classList.toggle("slar-active");
    });
  }
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

/* Save Scroll Position when Refreshing Page */
document.addEventListener("DOMContentLoaded", function(event) {
    var scrollpos = localStorage.getItem('scrollpos');
    if (scrollpos) window.scrollTo(0, scrollpos);
});

window.onbeforeunload = function(e) {
    localStorage.setItem('scrollpos', window.scrollY);
};
