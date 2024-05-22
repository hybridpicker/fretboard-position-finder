window.onload = function() {
    // Initialize navBarFretboardChords for the specified class names
    navBarFretboardChords("sfbsfnr");
    navBarFretboardChords("catsfbsf");
    navBarFretboardChords("sfbsfpos");

    // Close all select boxes if the user clicks outside of them
    document.addEventListener("click", closeAllSelect);

    // Retrieve tones for chords from data
    var urlParams = new URLSearchParams(window.location.search);
    var pos_val = urlParams.get('position_select') || (document.getElementById('position_select') ? document.getElementById('position_select').value : null);
    var note_range = urlParams.get('note_range') || (document.getElementById('note_range') ? document.getElementById('note_range').value : null);

    // Extract valid note ranges from voicing_data
    var validNoteRanges = Object.keys(voicing_data).filter(key => !['chord', 'type', 'root', 'note_range'].includes(key));

    // Validate pos_val and note_range against voicing_data
    if (!validNoteRanges.includes(note_range)) {
        note_range = validNoteRanges[0];
    }

    if (voicing_data[note_range] && !Object.keys(voicing_data[note_range]).includes(pos_val)) {
        pos_val = Object.keys(voicing_data[note_range])[0];
    }

    getTonesFromDataChords(pos_val, note_range);
};

function navBarFretboardChords(class_name) {
    var elements = document.getElementsByClassName(class_name);
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];

        // Add a click event listener to each element with the specified class name
        element.addEventListener("click", function(e) {
            e.stopPropagation();
            closeAllSelect(this);
            this.classList.toggle("active");

            // When an item is clicked, update the tones from data chords
            var urlParams = new URLSearchParams(window.location.search);
            var pos_val = urlParams.get('position_select') || (document.getElementById('position_select') ? document.getElementById('position_select').value : null);
            var note_range = urlParams.get('note_range') || (document.getElementById('note_range') ? document.getElementById('note_range').value : null);

            // Extract valid note ranges from voicing_data
            var validNoteRanges = Object.keys(voicing_data).filter(key => !['chord', 'type', 'root', 'note_range'].includes(key));

            // Validate pos_val and note_range against voicing_data
            if (!validNoteRanges.includes(note_range)) {
                note_range = validNoteRanges[0];
            }

            if (voicing_data[note_range] && !Object.keys(voicing_data[note_range]).includes(pos_val)) {
                pos_val = Object.keys(voicing_data[note_range])[0];
            }

            getTonesFromDataChords(pos_val, note_range);
        });
    }
}

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

    // Extract valid note ranges from voicing_data
    var validNoteRanges = Object.keys(voicing_data).filter(key => !['chord', 'type', 'root', 'note_range'].includes(key));

    // Ensure pos_val and note_range exist, otherwise use fallback values
    if (!validNoteRanges.includes(note_range)) {
        note_range = validNoteRanges[0];
    }
    if (voicing_data[note_range] && !Object.keys(voicing_data[note_range]).includes(pos_val)) {
        pos_val = Object.keys(voicing_data[note_range])[0];
    }

    // Set the id of inversions
    for (var key in voicing_data[note_range][pos_val][0]) {
        if (voicing_data[note_range][pos_val][0].hasOwnProperty(key)) {
            var tone = voicing_data[note_range][pos_val][0][key][0];
            var tone_name = voicing_data[note_range][pos_val][0][key][2];

            // Validate key and tone
            if (key && tone) {
                try {
                    var validKey = key.replace(/[^a-zA-Z0-9-_]/g, '');
                    var validTone = tone.replace(/[^a-zA-Z0-9-_]/g, '');
                    var QuerySelect = document.querySelector('.' + validKey + ' img.tone.' + validTone);
                    if (QuerySelect) {
                        QuerySelect.classList.add('active');
                    }
                    QuerySelect = document.querySelector('.' + validKey + ' .note.' + validTone);
                    if (QuerySelect) {
                        QuerySelect.classList.add('active');
                    }
                } catch (error) {
                    console.error("Invalid selector for key or tone:", validKey, validTone, error);
                }
            }
        }
    }

    // Change for RootNote Color
    for (var key in voicing_data.root) {
        if (voicing_data.root.hasOwnProperty(key)) {
            var root = voicing_data.root[key];
            for (var i = 0; i < string_array.length; i++) {
                var string = string_array[i];
                var validString = string.replace(/[^a-zA-Z0-9-_]/g, '');
                var validRoot = root.replace(/[^a-zA-Z0-9-_]/g, '');
                var root_note_image = document.querySelector('.' + validString + ' img.tone.active.' + validRoot);
                if (root_note_image != null) {
                    root_note_image.setAttribute('src', '/static/media/red_dot_24.svg');
                    root_note_image.classList.add('active');
                    root_note_image.classList.add('root');
                }
            }
        }
    }
}

function resetFretboard() {
    var activeElements = document.querySelectorAll('.active');
    activeElements.forEach(function(element) {
        element.classList.remove('active');
    });
}
