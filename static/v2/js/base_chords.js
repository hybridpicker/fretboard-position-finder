function getQueryParam(param) {
  var url = new URL(window.location.href);
  return parseInt(url.searchParams.get(param));
}

function updatePosition(newPosVal) {
  document.getElementById('position_select').value = newPosVal;
  var note_range = document.getElementById('note_range').value;
  getTonesFromDataChords(newPosVal, note_range);
}

function leftCursorClick() {
  var pos_val = getQueryParam("position_select");

  if (isNaN(pos_val)) {
    pos_val = 0; // Start with Basic Position if parameter is missing or invalid
  }

  var chordType = getChordType();
  var positions = getChordPositions(chordType);
  if (positions === undefined) {
    console.error("Invalid chord type or positions undefined for chord type:", chordType);
    return;
  }
  var current_index = positions.indexOf(getPositionName(pos_val, positions));
  var max_pos = positions.length;

  var new_pos_val = (current_index - 1 + max_pos) % max_pos; // Zyklisch rückwärts

  updatePosition(new_pos_val);
  updateCursorVisibility(new_pos_val, max_pos);
}

function rightCursorClick() {
  var pos_val = getQueryParam("position_select");

  if (isNaN(pos_val)) {
    pos_val = 0; // Start with Basic Position if parameter is missing or invalid
  }

  var chordType = getChordType();
  var positions = getChordPositions(chordType);
  if (positions === undefined) {
    console.error("Invalid chord type or positions undefined for chord type:", chordType);
    return;
  }
  var current_index = positions.indexOf(getPositionName(pos_val, positions));
  var max_pos = positions.length;

  var new_pos_val = (current_index + 1) % max_pos; // Zyklisch vorwärts

  updatePosition(new_pos_val);
  updateCursorVisibility(new_pos_val, max_pos);
}

function getChordType() {
  // Beispielhafte Implementierung, um den Akkordtyp abzurufen
  // Hier könnte die tatsächliche Logik zum Abrufen des Akkordtyps stehen
  var note_range = document.getElementById('note_range').value;
  console.log("Chord type (note range):", note_range);
  return note_range; // Beispielhafter Rückgabewert
}

function getChordPositions(chordType) {
  var chordData = voicing_data[chordType];
  if (!chordData) {
    console.error("Chord data not found for chord type:", chordType);
    return undefined;
  }
  var positions = Object.keys(chordData);
  console.log("Positions for chord type", chordType, ":", positions);
  return positions;
}

function getPositionName(index, positions) {
  return positions[index % positions.length];
}

// Beispielhafte Definition der Funktion updateCursorVisibility (falls benötigt)
function updateCursorVisibility(pos, max) {
  // Logik zur Aktualisierung der Sichtbarkeit des Cursors basierend auf pos und max
}

function getTonesFromDataChords(x, y) {
  resetFretboard();
  /* x sets the id of inversions */
  for (var key in voicing_data[y][x][0]) {
    if (voicing_data[y][x][0].hasOwnProperty(key)) {
      var tone = voicing_data[y][x][0][key][0];
      var tone_name = voicing_data[y][x][0][key][2];

      var QuerySelect = document.querySelector('.' + key + ' img.tone.' + tone);
      QuerySelect.classList.add('active');
      QuerySelect = document.querySelector('.' + key + ' .notename.' + tone);
      QuerySelect.classList.add('active');
      /* Check every note that has a defined Query for not activating all chord tones */
      QuerySelect = document.querySelector('.' + key + ' .note.' + tone);
      QuerySelect.classList.add('active');
    }
  }

  /* Change for RootNote Color */
  for (var key in voicing_data.root) {
    if (voicing_data.root.hasOwnProperty(key)) {
      var root = voicing_data.root[key];
      for (var i = 0; i < string_array.length; i++) {
        var string = string_array[i];
        var root_note_image = document.querySelector('.' + string + ' img.tone.active.' + root);
        if (root_note_image != null) {
          root_note_image.setAttribute('src', '/static/media/red_dot_24.svg');
          root_note_image.classList.add('active');
          root_note_image.classList.add('root');
        }
      }
    }
  }
}

function show_tension_notes_chords() {
  var x = document.getElementById('position_select').value;
  var y = document.getElementById('note_range').value;

  var tension_elements = document.querySelectorAll('.tensionname');
  if (tension_elements != undefined) {
    for (var i = 0; i < tension_elements.length; i++) {
      tension_elements[i].remove();
    }
  }

  for (var key in voicing_data[y][x][0]) {
    if (voicing_data[y][x][0].hasOwnProperty(key)) {
      var tone = voicing_data[y][x][0][key][0];
      var tension_name = voicing_data[y][x][0][key][1];

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
        QuerySelect = document.querySelector('.' + key + ' .notename.' + tone + '.active');
        if (QuerySelect != null) {
          QuerySelect.classList.remove("active");
        }
      }
    }
  }
  /* add class active for showing up */
  var tension_names = document.querySelectorAll('.tensionname');
  for (var i = 0; i < tension_names.length; i++) {
    tension_names[i].classList.add("active");
  }
  var button = document.getElementById("show_tension_button");
  button.setAttribute("onclick", "getToneNameFromDataChords()");
  button.innerHTML = 'Tone Names';
}

// HTML-Buttons für die Cursor-Funktion
document.addEventListener("DOMContentLoaded", function() {
  var leftButton = document.createElement("button");
  leftButton.innerText = "Left";
  leftButton.onclick = leftCursorClick;
  document.body.appendChild(leftButton);

  var rightButton = document.createElement("button");
  rightButton.innerText = "Right";
  rightButton.onclick = rightCursorClick;
  document.body.appendChild(rightButton);
});

function resetFretboard() {
  // Implement the reset logic here
}

function closeAllSelect(elmnt) {
  /* A function that will close all select boxes in the document,
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

document.addEventListener("click", closeAllSelect);
