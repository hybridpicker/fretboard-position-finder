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

function findActiveStringsForTone(tone_name) {
  return string_array.filter(string => {
    return frets.some(fret => {
      return document.querySelector(`.${fret}.${string}.${tone_name}.active`);
    });
  });
}

function findRangeForStrings(strings, tone_name) {
  return strings.map(string => {
    const activeFrets = frets.filter(fret => document.querySelector(`.${fret}.${string}.${tone_name}.active`));
    return activeFrets.length ? parseInt(activeFrets.slice(-1)) - parseInt(activeFrets[0]) : 0;
  });
}

function multiple_notes(tone_name, y) {
  Object.keys(scale_data[y]).forEach(key => {
    scale_data[y][key][0]["tones"].forEach(tone => {
      const elements = document.querySelectorAll(`.${tone}.active`);
      if (elements.length > 2) {
        const pos_val = document.getElementById('position_select').value;
        if (pos_val != 0) {
          const activeStrings = findActiveStringsForTone(tone);
          const ranges = findRangeForStrings(activeStrings, tone);
          const maxRangeString = activeStrings[ranges.indexOf(Math.max(...ranges))];
          deactivateActiveNotes(maxRangeString, tone);
        }
      }
    });
  });
}


function activateToneElements(key, tone_name) {
  const toneElement = document.querySelector(`.${key} img.tone.${tone_name}`);
  const noteElement = document.querySelector(`.${key} .note.${tone_name}`);
  
  if (toneElement) toneElement.classList.add('active');
  if (noteElement) noteElement.classList.add('active');
}

function setRootNoteColor(root) {
  string_array.forEach(string => {
    const rootElement = document.querySelector(`.${string} img.tone.active.${root}`);
    if (rootElement) {
      rootElement.setAttribute('src', '/static/media/red_dot.svg');
      rootElement.classList.add('active', 'root');
    }
  });
}

function avoid_four_notes_on_string() {
  const avoid_strings = [string_array[0], string_array.slice(-1)[0]];
  
  avoid_strings.forEach(string => {
    const elements = document.querySelectorAll(`.${string} .active > img`);
    if (elements.length > 3) {
      const indexToRemove = (string === avoid_strings[1]) ? 0 : 3;
      elements[indexToRemove].classList.remove('active');
    }
  });
}

function getTonesFromDataScales(y) {
  resetFretboard();
  
  Object.keys(scale_data[y]).forEach(key => {
    scale_data[y][key][0]["tones"].forEach(tone_name => {
      activateToneElements(key, tone_name);
    });
  });
  
  if (document.getElementById('position_select').value != 0) {
    multiple_notes(null, y);
    avoid_four_notes_on_string();
  }
  
  Object.keys(scale_data.root).forEach(key => {
    setRootNoteColor(scale_data.root[key]);
  });
}

function setButtonAttributes(buttonId, onClickFunction, innerText) {
  const button = document.getElementById(buttonId);
  button.setAttribute("onclick", onClickFunction);
  button.innerHTML = innerText;
}

function activateElements(key, tone, tone_name) {
  const toneElement = document.querySelector(`.${key} img.tone.${tone}`);
  const noteNameElement = document.querySelector(`.${key} .notename.${tone}`);
  const noteElement = document.querySelector(`.${key} .note.${tone}`);

  if (toneElement) toneElement.classList.add('active');
  if (noteNameElement) noteNameElement.classList.add('active');
  if (noteElement) noteElement.classList.add('active');
}

function setRootNoteColorForChords(root) {
  string_array.forEach(string => {
    const rootElement = document.querySelector(`.${string} img.tone.active.${root}`);
    if (rootElement) {
      rootElement.setAttribute('src', '/static/media/red_dot.svg');
      rootElement.classList.add('active', 'root');
    }
  });
}

function getToneNameFromDataChords() {
  setButtonAttributes("show_tension_button", "show_tension_notes_chords()", "Show Tensions");
  const pos_val = document.getElementById('position_select').value;
  const note_range = document.getElementById('note_range').value;
  getTonesFromDataChords(pos_val, note_range);
}

function getNoteNameFromData() {
  const y = document.getElementById('position_select').value;
  Object.keys(scale_data[y]).forEach(key => {
    scale_data[y][key][0]["tones"].forEach(tone_name => {
      const image = document.querySelector(`.${key} .${tone_name} img.active`);
      if (image) {
        activateElements(key, null, tone_name);
      }
    });
  });
  setButtonAttributes("show_note_name_button", "getNotePicFromData()", "Only Tones");
}

function getTonesFromDataChords(x, y) {
  resetFretboard();
  Object.keys(voicing_data[y][x][0]).forEach(key => {
    const tone = voicing_data[y][x][0][key][0];
    const tone_name = voicing_data[y][x][0][key][2];
    activateElements(key, tone, tone_name);
  });

  Object.keys(voicing_data.root).forEach(key => {
    setRootNoteColorForChords(voicing_data.root[key]);
  });
}
function toggleElements(elements, className, action = 'add') {
  elements.forEach(element => element.classList[action](className));
}

function setButtonAttributes(buttonId, onClickFunction, innerText) {
  const button = document.getElementById(buttonId);
  button.setAttribute("onclick", onClickFunction);
  button.innerHTML = innerText;
}

function show_tension_notes_chords() {
  const position = document.getElementById('position_select').value;
  const noteRange = document.getElementById('note_range').value;
  const tensionElements = document.querySelectorAll('.tensionname');

  toggleElements(tensionElements, 'active', 'remove');

  Object.keys(voicing_data[noteRange][position][0]).forEach(key => {
    const tone = voicing_data[noteRange][position][0][key][0];
    const tensionName = voicing_data[noteRange][position][0][key][1];
    const selection = document.querySelector(`.note.active.${tone}`);

    if (selection) {
      const tensionDiv = document.createElement("DIV");
      tensionDiv.className = "tensionname";
      selection.appendChild(tensionDiv);
      const textNode = document.createTextNode(tensionName);
      tensionDiv.appendChild(textNode);

      const noteNameElement = document.querySelector(`.${key} .notename.${tone}.active`);
      if (noteNameElement) noteNameElement.classList.remove("active");
    }
  });

  toggleElements(document.querySelectorAll('.tensionname'), 'active');
  setButtonAttributes("show_tension_button", "getToneNameFromDataChords()", "Tone Names");
}

function getNotePicFromData() {
  const noteNameElements = document.querySelectorAll('.notename');
  toggleElements(noteNameElements, 'active', 'remove');
  setButtonAttributes("show_note_name_button", "getNoteNameFromData()", "Note Name");
}
function createOptionDiv(selElmnt, containerDiv) {
  const optionDiv = document.createElement("DIV");
  optionDiv.innerHTML = selElmnt.options[selElmnt.selectedIndex].innerHTML;
  optionDiv.addEventListener("click", function(e) {
    toggleSelectBoxes(this, containerDiv);
  });
  containerDiv.appendChild(optionDiv);
  return optionDiv;
}

function populateOptions(selElmnt, optionListDiv) {
  for (let j = 1; j < selElmnt.length; j++) {
    const optionDiv = document.createElement("DIV");
    optionDiv.innerHTML = selElmnt.options[j].innerHTML;
    optionDiv.addEventListener("click", function() {
      updateSelection(this, selElmnt, optionListDiv);
    });
    optionListDiv.appendChild(optionDiv);
  }
}

function updateSelection(clickedDiv, selElmnt, optionListDiv) {
  const selectedDiv = optionListDiv.previousSibling;
  for (let i = 0; i < selElmnt.length; i++) {
    if (selElmnt.options[i].innerHTML === clickedDiv.innerHTML) {
      selElmnt.selectedIndex = i;
      selectedDiv.innerHTML = clickedDiv.innerHTML;
      break;
    }
  }
  selectedDiv.click();
  const posVal = document.getElementById('position_select').value;
  const noteRange = document.getElementById('note_range').value;
  getTonesFromDataChords(posVal, noteRange);
}

function toggleSelectBoxes(clickedDiv, containerDiv) {
  closeAllSelect(clickedDiv);
  clickedDiv.nextSibling.classList.toggle("sehi");
  clickedDiv.classList.toggle("slar-active");
}

function navBarFretboardChords(class_name) {
  const elements = document.getElementsByClassName(class_name);
  Array.from(elements).forEach(element => {
    const selElmnt = element.getElementsByTagName("select")[0];
    const selectedDiv = createOptionDiv(selElmnt, element);
    const optionListDiv = document.createElement("DIV");
    optionListDiv.setAttribute("class", "slit sehi");
    populateOptions(selElmnt, optionListDiv);
    element.appendChild(optionListDiv);
  });
}

// ... (Rest des Codes bleibt unverändert)
