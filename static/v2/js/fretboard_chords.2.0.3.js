document.addEventListener('DOMContentLoaded', function() {
    // Ensure the overlay menu is hidden initially
    const overlayMenuChords = document.getElementById('overlayMenuChords');
    overlayMenuChords.style.display = 'none';
    
    // Initialize navBarFretboardChords for the specified class names
    navBarFretboardChords('sfbsfnr');
    navBarFretboardChords('catsfbsf');
    navBarFretboardChords('sfbsfpos');

    // Close all select boxes if the user clicks outside of them
    document.addEventListener('click', closeAllSelect);

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

     // Set the display style for cursor elements
     var leftCursor = document.querySelector('.left-cursor');
     var rightCursor = document.querySelector('.right-cursor');
 
     if (leftCursor) {
         leftCursor.style.display = 'block';
     }
 
     if (rightCursor) {
         rightCursor.style.display = 'block';
     }
});


function navBarFretboardChords(class_name) {
    var elements = document.getElementsByClassName(class_name);
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];

        // Add a click event listener to each element with the specified class name
        element.addEventListener('click', function(e) {
            e.stopPropagation();
            closeAllSelect(this);
            this.classList.toggle('active');

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
    var x = document.getElementsByClassName('slit');
    var y = document.getElementsByClassName('sese');
    var arrNo = [];
    for (var i = 0; i < y.length; i++) {
        if (elmnt == y[i]) {
            arrNo.push(i);
        } else {
            y[i].classList.remove('slar-active');
        }
    }
    for (var i = 0; i < x.length; i++) {
        if (arrNo.indexOf(i) === -1) {
            x[i].classList.add('sehi');
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
                    console.error('Invalid selector for key or tone:', validKey, validTone, error);
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


function leftCursorClick() {
    var pos_val = getQueryParam('position_select');
    var note_range = getQueryParam('note_range');

    if (pos_val === null || pos_val === undefined || !isNaN(pos_val)) {
        pos_val = 'Basic Position'; // Start with Basic Position if parameter is missing or invalid
    }
    
    var chordType = getChordType();

    var positions = getChordPositions(chordType);

    if (positions === undefined || positions.length === 0) {
        console.error('Invalid chord type or positions undefined for chord type:', chordType);
        return;
    }
    var current_index = positions.indexOf(pos_val);

    if (current_index === -1) {
        current_index = 0; // Fallback if the current position is not found in positions
    }
    var max_pos = positions.length;

    var new_pos_val = (current_index - 1 + max_pos) % max_pos; // Zyklisch rückwärts

    updatePosition(positions[new_pos_val]);
    getTonesFromDataChords(positions[new_pos_val], note_range); // Update tones
}

function rightCursorClick() {
    var pos_val = getQueryParam('position_select');
    var note_range = getQueryParam('note_range');

    if (pos_val === null || pos_val === undefined || !isNaN(pos_val)) {
        pos_val = 'Basic Position'; // Start with Basic Position if parameter is missing or invalid
    }
    
    var chordType = getChordType();

    var positions = getChordPositions(chordType);

    if (positions === undefined || positions.length === 0) {
        console.error('Invalid chord type or positions undefined for chord type:', chordType);
        return;
    }
    var current_index = positions.indexOf(pos_val);

    if (current_index === -1) {
        current_index = 0; // Fallback if the current position is not found in positions
    }
    var max_pos = positions.length;

    var new_pos_val = (current_index + 1) % max_pos; // Zyklisch vorwärts

    updatePosition(positions[new_pos_val]);
    getTonesFromDataChords(positions[new_pos_val], note_range); // Update tones
}

// Helper functions

function getQueryParam(param) {
    var urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

function getChordType() {
    return voicing_data.type; // Example implementation, modify as needed
}

function getChordPositions(chordType) {
    var positions = [];
    var validPositions = ['Basic Position', 'First Inversion', 'Second Inversion', 'Third Inversion']; // Define valid positions

    for (var noteRange in voicing_data) {
        if (voicing_data.hasOwnProperty(noteRange) && typeof voicing_data[noteRange] === 'object') {
            for (var position in voicing_data[noteRange]) {
                if (voicing_data[noteRange].hasOwnProperty(position) && validPositions.includes(position)) {
                    if (!positions.includes(position)) {
                        positions.push(position);
                    }
                }
            }
        }
    }
    return positions;
}

function updatePosition(new_pos_val) {
    var urlParams = new URLSearchParams(window.location.search);
    urlParams.set('position_select', new_pos_val);
    window.history.replaceState(null, null, '?' + urlParams.toString());
}

// Change Root Note
const noteMapping = {
    1: 'C', 3: 'Db', 4: 'D', 6: 'Eb', 7: 'E', 8: 'F', 10: 'Gb', 11: 'G', 13: 'Ab', 14: 'A', 16: 'Bb', 17: 'B'
};
const validRoots = Object.keys(noteMapping).map(Number); // [1, 3, 4, 6, 7, 8, 10, 11, 13, 14, 16, 17]

function changeRoot(noteChange) {
    var urlParams = new URLSearchParams(window.location.search);
    var root = parseInt(urlParams.get('root')) || 1; // Fallback to 1 if 'root' param is missing or invalid

    // Find the current index in validRoots
    var currentIndex = validRoots.indexOf(root);

    // Calculate new index cyclically
    var newIndex = (currentIndex + noteChange + validRoots.length) % validRoots.length;

    var newRoot = validRoots[newIndex];
    urlParams.set('root', newRoot);
    window.history.replaceState(null, null, '?' + urlParams.toString());

    // Only update tones if pos_val is specified
    if (urlParams.has('position_select')) {
        var pos_val = urlParams.get('position_select');
        var note_range = urlParams.get('note_range') || (document.getElementById('note_range') ? document.getElementById('note_range').value : null);
        getTonesFromDataChords(pos_val, note_range);
    }

    // Reload the page with new URL parameters
    window.location.search = urlParams.toString();
}

function increaseRoot() {
    changeRoot(1);
}

function decreaseRoot() {
    changeRoot(-1);
}
