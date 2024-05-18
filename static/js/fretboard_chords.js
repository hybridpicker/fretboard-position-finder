// Initialize the fretboard for chords
window.onload = function() {
  navBarFretboardChords("sfbsfnr");
  navBarFretboardChords("catsfbsf");
  navBarFretboardChords("sfbsfpos");

  // If the user clicks anywhere outside the select box, close all select boxes
  document.addEventListener("click", closeAllSelect);

  // Get all elements with the class "sfbsf" and customize the select boxes
  var x = document.getElementsByClassName("sfbsf");
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

  // Get tones from function 0=Template
  var pos_val = document.getElementById('position_select').value;
  var note_range = document.getElementById('note_range').value;
  getTonesFromDataChords(pos_val, note_range);
};

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

function getTonesFromDataChords(x, y) {
  resetFretboard();
  /* x sets the id of inversions */
  var i = 0;
  for (var key in voicing_data[y][x][0]) {
      if (voicing_data[y][x][0].hasOwnProperty(key)) {
          var tone = voicing_data[y][x][0][key][0];
          var tone_name = voicing_data[y][x][0][key][2];

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
          var root = voicing_data.root[key];
          for (i = 0; i < string_array.length; i++) {
              string = string_array[i];
              var root_note_image = document.querySelector('.' + string + ' img.tone.active.' + root);
              if (root_note_image != null) {
                  root_note_image.setAttribute('src', '/static/media/red_dot.svg');
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

  var i = 0;
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
              var QuerySelect = document.querySelector('.' + key + ' .notename.' + tone + '.active');
              if (QuerySelect != null) {
                  QuerySelect.classList.remove("active");
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
}

function navBarFretboardChords(class_name) {
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
              var pos_val = document.getElementById('position_select').value;
              var note_range = document.getElementById('note_range').value;
              getTonesFromDataChords(pos_val, note_range);
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
