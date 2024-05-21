window.onload = function() {
    navBarFretboardChords("sfbsfnr");
    navBarFretboardChords("catsfbsf");
    navBarFretboardChords("sfbsfpos");

    // Wenn der Benutzer irgendwo außerhalb der Auswahlbox klickt, alle Auswahlboxen schließen
    document.addEventListener("click", closeAllSelect);

    // Alle Elemente mit der Klasse "sfbsf" holen und die Auswahlboxen anpassen
    var x = document.getElementsByClassName("sfbsf");
    for (var i = 0; i < x.length; i++) {
        var selElmnt = x[i].getElementsByTagName("select")[0];
        if (selElmnt && selElmnt.options && selElmnt.options.length > 0 && selElmnt.selectedIndex >= 0) {
            var a = document.createElement("DIV");
            a.setAttribute("class", "sese");
            a.innerHTML = selElmnt.options[selElmnt.selectedIndex].innerHTML;
            x[i].appendChild(a);

            var b = document.createElement("DIV");
            b.setAttribute("class", "slit sehi");
            for (var j = 0; j < selElmnt.length; j++) {
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
                    var pos_val = document.getElementById('position_select') ? document.getElementById('position_select').value : null;
                    var note_range = document.getElementById('note_range') ? document.getElementById('note_range').value : null;
                    getTonesFromDataChords(pos_val, note_range);
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
        } else {
            
        }
    }

    // Töne aus Daten für Akkorde holen
    var pos_val = document.getElementById('position_select') ? document.getElementById('position_select').value : null;
    var note_range = document.getElementById('note_range') ? document.getElementById('note_range').value : null;
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
        if (arrNo.indexOf(i) === -1) {
            x[i].classList.add("sehi");
        }
    }
}

function getTonesFromDataChords(pos_val, note_range) {
    resetFretboard();

    // Sicherstellen, dass pos_val und note_range existieren, andernfalls Fallback-Werte verwenden
    if (!note_range || !voicing_data[note_range]) {
        note_range = Object.keys(voicing_data)[0];
    }
    if (!pos_val || !voicing_data[note_range][pos_val]) {
        pos_val = Object.keys(voicing_data[note_range])[0];
    }

    /* x sets the id of inversions */
    var i = 0;
    for (var key in voicing_data[note_range][pos_val][0]) {
        if (voicing_data[note_range][pos_val][0].hasOwnProperty(key)) {
            var tone = voicing_data[note_range][pos_val][0][key][0];
            var tone_name = voicing_data[note_range][pos_val][0][key][2];

            var QuerySelect = document.querySelector('.' + key + ' img.tone.' + tone);
            if (QuerySelect) {
                QuerySelect.classList.add('active');
            } else {
            }
            QuerySelect = document.querySelector('.' + key + ' .notename.' + tone);
            if (QuerySelect) {
                QuerySelect.classList.add('active');
            } else {
            }
            QuerySelect = document.querySelector('.' + key + ' .note.' + tone);
            if (QuerySelect) {
                QuerySelect.classList.add('active');
            } else {
            }
        }
    }

    /* Change for RootNote Color */
    for (var key in voicing_data.root) {
        if (voicing_data.root.hasOwnProperty(key)) {
            var root = voicing_data.root[key];
            for (i = 0; i < string_array.length; i++) {
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
    var x = document.getElementById('position_select') ? document.getElementById('position_select').value : null;
    var y = document.getElementById('note_range') ? document.getElementById('note_range').value : null;

    var tension_elements = document.querySelectorAll('.tensionname');
    if (tension_elements != undefined) {
        for (var i = 0; i < tension_elements.length; i++) {
            tension_elements[i].remove();
        }
    }

    // Sicherstellen, dass pos_val und note_range existieren, andernfalls Fallback-Werte verwenden
    if (!y || !voicing_data[y]) {
        y = Object.keys(voicing_data)[0];
    }
    if (!x || !voicing_data[y][x]) {
        x = Object.keys(voicing_data[y])[0];
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
        if (selElmnt && selElmnt.options && selElmnt.options.length > 0 && selElmnt.selectedIndex >= 0) {
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
                    var pos_val = document.getElementById('position_select') ? document.getElementById('position_select').value : null;
                    var note_range = document.getElementById('note_range') ? document.getElementById('note_range').value : null;
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
        } else {
        }
    }
}
