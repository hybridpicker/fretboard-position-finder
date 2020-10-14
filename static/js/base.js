var string_array = ['eString', 'bString', 'gString', 'dString', 'AString', 'ELowString']

var frets = ['one','two','three','four','five','six',
            'seven','eight','nine','ten','eleven', 'twelve',
            'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen']

function playtone(x, y){
  var audio = new Audio('static/media/tone_sounds/' + x + '.mp3');
  var string = '.' + y
  audio.play();
  var root_class = document.querySelector(string + ' img.tone.' + x + '.active').classList.contains('root')
  if ( root_class == true ) {
  document.querySelector(string + ' img.tone.' + x + '.active').setAttribute('src', '/static/media/red_dot_active.svg');
  setTimeout(function () {
    document.querySelector(string + ' img.tone.' + x + '.active').setAttribute('src', '/static/media/red_dot.svg');
  }, 300)
  }
  else {
  document.querySelector(string + ' img.tone.' + x + '.active').setAttribute('src', '/static/media/yellow_dot_active.svg');
  setTimeout(function () {
    document.querySelector(string + ' img.tone.' + x + '.active').setAttribute('src', '/static/media/yellow_dot.svg');
  }, 300)
  }
}

function reset_fretboard(){
  var elements = document.querySelectorAll('.active');
  for (var i=0; i<elements.length; i++) {
    elements[i].classList.remove("active");
  }
  var tone_elements = document.querySelectorAll('.tone');
  for (var i=0; i<tone_elements.length; i++) {
    tone_elements[i].setAttribute('src', '/static/media/yellow_dot.svg')
  }
}

function deactivate_active_notes(string, tone_name){
  element = document.querySelectorAll('.' + string + ' .' + tone_name);
  for (x in element){
    /* check if elements in element are natural numbers */
    if (!(isNaN(x))){
      element[x].classList.remove("active");
    }
  }
}

function multiple_notes(tone_name, y){
  for (var key in scale_data[y]) {
    if (scale_data[y].hasOwnProperty(key)) {
        for (var z in scale_data[y][key][0]["tones"]) {
            var tone_name = scale_data[y][key][0]["tones"][z]
            element = document.querySelectorAll('.' + tone_name + '.active');
            if (element.length > 2) {
              var pos_val = document.getElementById('position_select').value
              if (pos_val != 0){
                /* Count String Range of String X and String Y -> Deactivate Tone with wider range on */
                /* 1. Find String Name of Active Notes */
                var multiple_tone = tone_name;
                var list_of_strings = []
                for (variable in frets) {
                  for (string in string_array){
                    if (document.querySelectorAll('.' + frets[variable] + '.' + string_array[string] + ' .' + tone_name + '.active').length != 0 ){
                      /* push string into list */
                      list_of_strings.push(string_array[string])
                    }
                  }
                }
                /* 2. Find Range lowest to highest Note on Strings */
                var first_string = []
                var second_string = []
                var available_strings = []
                for (string in string_array){
                  for (fret in frets){
                    if (document.querySelectorAll('.' + list_of_strings[string] + '.' + frets[fret] + ' .active').length != 0){
                      if (string > 0){
                        second_string.push(fret)
                      }
                      else {
                        first_string.push(fret)
                      }
                      available_strings.push(list_of_strings[string])
                    }
                  }
                }
                var first_string_range = (first_string[first_string.length - 1]) - first_string[0]
                var second_string_range = (second_string[second_string.length - 1]) - second_string[0]
                var first_string = available_strings[1]
                var second_string = available_strings[available_strings.length - 1]
                /* 3. Deactivate Note with longest Range */
                if (first_string_range > second_string_range){
                  deactivate_active_notes(first_string, tone_name)
                }
                else {
                  deactivate_active_notes(second_string, tone_name)
                }
              }
            }
          }
        }
    }
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
  reset_fretboard()
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
  reset_fretboard()
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
