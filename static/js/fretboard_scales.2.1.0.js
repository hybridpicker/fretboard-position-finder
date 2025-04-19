/**
 * Reset the fretboard by removing all active classes and resetting styles
 */
function resetFretboard() {
  console.log("DEBUG: Running resetFretboard"); // Add log

  // Select ALL potentially active elements first
  const allNotes = document.querySelectorAll('.note');
  const allTones = document.querySelectorAll('img.tone');
  const allNotenames = document.querySelectorAll('.notename');

  // Force hide all note names first
  allNotenames.forEach(notename => {
    notename.style.visibility = 'hidden';
    notename.style.opacity = '0';
    notename.classList.remove('active', 'show-name');
  });

  // Force hide all tone images and reset styles/classes
  allTones.forEach(image => {
    // Reset src to default based on octave (existing logic)
    const noteElement = image.closest('.note');
    let defaultSrc = '/static/media/circle_01.svg'; // Default fallback
    if (noteElement) {
      const toneNames = Array.from(noteElement.classList).filter(cls => cls !== 'note' && cls !== 'active');
      if (toneNames.length > 0) {
        const toneName = toneNames[0];
        const octaveMatch = toneName.match(/[a-z]+([0-4])/);
        if (octaveMatch && octaveMatch[1]) {
          const octave = parseInt(octaveMatch[1]);
          switch (octave) {
            case 0: case 1: defaultSrc = '/static/media/circle_01.svg'; break;
            case 2: defaultSrc = '/static/media/circle_02.svg'; break;
            case 3: defaultSrc = '/static/media/circle_03.svg'; break;
            case 4: defaultSrc = '/static/media/circle_04.svg'; break;
          }
        }
      }
    }
    image.setAttribute('src', defaultSrc + '?v=2'); // Ensure version query param if needed

    // Reset styles and classes
    image.style.visibility = 'hidden';
    image.style.opacity = '0';
    image.style.border = '';
    image.style.boxShadow = '';
    image.classList.remove('active', 'root', 'all-positions-note', 'low-fret-note');
  });

  // Force hide all note divs and reset classes/styles
  allNotes.forEach(note => {
    note.style.visibility = 'hidden';
    note.style.opacity = '0';
    note.style.border = '';
    note.style.animation = '';
    note.classList.remove('active', 'all-positions-note', 'low-fret-note', 'auxiliary-note', 'stretch-warning');

    // Remove any tooltip elements
    const tooltip = note.querySelector('.tooltip');
    if (tooltip) {
      note.removeChild(tooltip);
    }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  const overlayMenu = document.getElementById('overlayMenu');
  if (overlayMenu) {
    overlayMenu.style.display = 'none';
  }
  
  // Initialize currentMode to 'scales' for this file
  window.currentMode = 'scales';
  
  // Initialize currentScalePosition from URL
  const currentUrl = new URL(window.location.href);
  window.currentScalePosition = parseInt(currentUrl.searchParams.get('position_select')) || 0;
  
  // Initialize maxScalePosition from select options
  window.maxScalePosition = 0;
  const posSelect = document.getElementById('position_select');
  if (posSelect) {
    for (let i = 0; i < posSelect.options.length; i++) {
      const val = parseInt(posSelect.options[i].value);
      if (!isNaN(val) && val !== 0 && val > window.maxScalePosition) {
        window.maxScalePosition = val;
      }
    }
  }
  console.log("Scales initialization: position=" + window.currentScalePosition + ", max=" + window.maxScalePosition);

  customizeSelectField('sfbsfnos');
  customizeSelectField('sfbsfpos');
  customizeSelectField('sfbsf');

  // If the user clicks anywhere outside the select box, close all select boxes
  document.addEventListener('click', closeAllSelect);

  // Make string_array accessible globally for debug tools
  if (typeof string_array !== 'undefined') {
    window.string_array = string_array;
  }

  var pos_val = document.getElementById('position_select').value;
  var url_string = window.location.href;
  var url = new URL(url_string);
  pos_val = url.searchParams.get('position_select');
  if (pos_val) {
    getTonesFromDataScales(pos_val);
  } else {
    getTonesFromDataScales('0');
  }
  
  // Update cursor visibility based on current state
  if (typeof updateCursorVisibility === 'function') {
    updateCursorVisibility(window.currentScalePosition, window.maxScalePosition);
  }
});

/**
 * Fixed function for processing notes on a specific string
 */
function activateNotesForString(stringName, tonesList, position) {
  console.log(`SCALE DEBUG: Processing string ${stringName} with tones: `, tonesList);

  // For each tone in this string's data
  tonesList.forEach(toneName => {
    // Find all elements with this tone name on this string
    const selector = `.${stringName} .note.${toneName}`; // Target the .note div containing the tone
    const noteElements = document.querySelectorAll(selector);
    console.log(`SCALE DEBUG: Selected ${noteElements.length} note elements with selector \"${selector}\"`);

    // Activate each matching note element
    noteElements.forEach(noteEl => {
      // Mark the note div as active - ENSURE ACTIVE CLASS IS ADDED
      console.log(`SCALE DEBUG: Activated note element: `, noteEl);
      noteEl.classList.add('active');
      
      // Ensure visibility with both CSS class and inline style
      noteEl.style.visibility = 'visible'; 
      noteEl.style.opacity = '1';

      // Find the tone image within the note div
      const toneImage = noteEl.querySelector('img.tone');
      if (toneImage) {
        console.log(`SCALE DEBUG: Activated tone image: `, toneImage);
        // Ensure active class is added to the tone image
        toneImage.classList.add('active');
        
        // Ensure visibility with both class and inline style
        toneImage.style.visibility = 'visible';
        toneImage.style.opacity = '1';

        let isRoot = false; // Declare with let here

        // Determine if this tone is the root note
        if (scale_data.root) {
            const toneBase = toneName.replace(/[0-9]/g, '');
            if (typeof scale_data.root === 'string') {
                isRoot = (toneBase === scale_data.root);
            } else if (typeof scale_data.root === 'object') {
                 isRoot = Object.values(scale_data.root).some(root => {
                    const rootBase = String(root).replace(/[0-9-]/g, '');
                    return rootBase === toneBase;
                 });
            } else {
                 isRoot = false; // Default if root data is weird type
            }
        } else {
             isRoot = false; // Default if root data missing
        }

        // --- Root Note Handling ---
        // 1. Reset root class and get default octave circle
        toneImage.classList.remove('root');
        const octaveMatch = toneName.match(/[a-z]+([0-4])/);
        let defaultSvgSrc = '/static/media/circle_01.svg'; // Default fallback
        if (octaveMatch && octaveMatch[1]) {
            const octave = parseInt(octaveMatch[1]);
            switch (octave) {
                case 0: case 1: defaultSvgSrc = '/static/media/circle_01.svg'; break;
                case 2: defaultSvgSrc = '/static/media/circle_02.svg'; break;
                case 3: defaultSvgSrc = '/static/media/circle_03.svg'; break;
                case 4: defaultSvgSrc = '/static/media/circle_04.svg'; break;
            }
        }

        // 2. Apply the appropriate styling based on root status
        if (isRoot) {
          console.log(`SCALE DEBUG: Setting ${toneName} as root.`);
          // Force the root note to have both classes and the red circle image
          toneImage.classList.add('root');
          toneImage.classList.add('active'); // Ensure active class is added
          
          // IMPORTANT: Set the red circle image with exact format
          toneImage.setAttribute('src', '/static/media/red_circle.svg');
          
          // Set explicit styling to match your desired appearance
          toneImage.style.opacity = '1';
          toneImage.style.border = '2px solid rgb(204, 0, 0)';
          toneImage.style.boxShadow = 'rgba(255, 0, 0, 0.3) 0px 0px 5px';
          
          // Make sure note name is visible and has the right color
          const notename = noteEl.querySelector('.notename');
          if (notename) {
            notename.style.color = '#efede8'; // Set the text color explicitly
            notename.style.visibility = 'visible';
            notename.style.opacity = '1';
            notename.classList.add('active');
            notename.classList.add('show-name');
          }
        } else {
          // It's not the root, set the default octave circle
          toneImage.setAttribute('src', defaultSvgSrc + '?v=2');
        }
        // --- End Root Note Handling ---
      } // End if (toneImage)

      // Find the notename span within the note div
      const notenameSpan = noteEl.querySelector('.notename');
      if (notenameSpan) {
        // Make the notename visible for active notes
        notenameSpan.style.visibility = 'visible';
        notenameSpan.style.opacity = '1';
        // Add a class to help with CSS targeting
        notenameSpan.classList.add('active');
        // Always show note names by adding show-name class
        notenameSpan.classList.add('show-name');
      }
    });
  });
}


/**
 * Main function to display the selected position's notes on the fretboard
 */
function getTonesFromDataScales(y) {
  console.log(`DEBUG: getTonesFromDataScales called with position y = "${y}" (type: ${typeof y})`);
  
  // IMPORTANT: First ensure ALL notes are reset and hidden
  resetFretboard();
  
  // Hide all notes by default - ensure none from previous positions remain visible
  document.querySelectorAll('.note').forEach(note => {
    note.classList.remove('active', 'all-positions-note', 'low-fret-note');
    note.style.visibility = 'hidden';
    note.style.opacity = '0';
    
    // Also hide the tone images and note names
    const toneImg = note.querySelector('img.tone');
    if (toneImg) {
      toneImg.classList.remove('active', 'root');
      toneImg.style.visibility = 'hidden';
      toneImg.style.opacity = '0';
    }
    
    const noteName = note.querySelector('.notename');
    if (noteName) {
      noteName.classList.remove('active', 'show-name');
      noteName.style.visibility = 'hidden';
      noteName.style.opacity = '0';
    }
  });

  // Check if scale_data exists and has the selected position
  if (!scale_data || !scale_data[y]) {
    console.error(`Scale data for position ${y} not found.`);
    // Optionally display "All Positions" or handle the error
    if (y !== '0' && scale_data && scale_data['0']) {
       activateAllPositionsNotes('0'); // Fallback to all positions
    }
    return;
  }

  // Handle "All Positions" (position 0) separately
  if (y === '0') {
    console.log(`DEBUG: Handling position '0'. Calling activateAllPositionsNotes.`);
    activateAllPositionsNotes('0');
    return; // Exit after handling '0'
  }

  // Process each string in this position's data
  for (const stringName in scale_data[y]) {
    console.log(`DEBUG: Processing position "${y}", string "${stringName}". Data:`, scale_data[y][stringName]);
    if (scale_data[y].hasOwnProperty(stringName) &&
        scale_data[y][stringName] &&
        scale_data[y][stringName][0] &&
        scale_data[y][stringName][0].tones) {

      const tonesList = scale_data[y][stringName][0].tones;
      activateNotesForString(stringName, tonesList, y);
    } else {
      console.warn(`No valid tone data for string ${stringName} in position ${y}`);
    }
  }

  // Final processing to avoid too many notes on outer strings
  avoid_four_notes_on_string();

  // Process any duplicate notes that need special handling
  multiple_notes(null, y); // Pass null for tone_name as it iterates through all tones
  
  // Force a final check to ensure all active notes are properly visible
  document.querySelectorAll('.note.active').forEach(note => {
    note.style.visibility = 'visible';
    note.style.opacity = '1';
    
    const toneImg = note.querySelector('img.tone');
    if (toneImg) {
      toneImg.style.visibility = 'visible';
      toneImg.style.opacity = '1';
    }
    
    const noteName = note.querySelector('.notename');
    if (noteName) {
      noteName.classList.add('show-name');
      noteName.style.visibility = 'visible';
      noteName.style.opacity = '1';
    }
  });
}

/**
 * Ensures proper note visibility after all activation is done
 * (Potentially redundant if activateNotesForString handles visibility correctly)
 */
function cleanupNoteVisibility() {
  // Make the active tone circles visible
  const activeTones = document.querySelectorAll('.note.active img.tone');
  activeTones.forEach(tone => {
    tone.style.visibility = 'visible';
    tone.style.opacity = '1';
    tone.classList.add('active'); // Ensure active class is present
  });

  // Make the active note divs visible
  const activeNotes = document.querySelectorAll('.note.active');
  activeNotes.forEach(note => {
    note.style.visibility = 'visible';
    note.style.opacity = '1';

    // Keep notenames hidden unless specifically toggled on
    const notename = note.querySelector('.notename');
    if (notename && !notename.classList.contains('show-name')) { // Check toggle class
      notename.style.visibility = 'hidden';
      notename.style.opacity = '0';
    }
  });
}

// Keep this function as a simplified version in case it's called elsewhere
function toggleNotenames() {
  // Now just make sure all note names are visible (no toggling)
  const notenames = document.querySelectorAll('.note.active .notename');
  
  notenames.forEach(notename => {
    // Make them visible with both inline style and class for robustness
    notename.style.visibility = 'visible';
    notename.style.opacity = '1';
    notename.classList.add('active');
    notename.classList.add('show-name');
  });
}


function multiple_notes(tone_name, y) {
  var url_string = window.location.href;
  var url = new URL(url_string);
  var pos_val = url.searchParams.get('position_select');

  // Only run if a specific position (not '0') is selected
  if (!pos_val || pos_val === '0') {
    return;
  }

  // If tone_name is provided, process only that tone. Otherwise, process all tones in the position.
  const tonesToProcess = new Set();
  if (tone_name) {
      tonesToProcess.add(tone_name);
  } else {
      // Gather all unique tones present in the current position 'y'
      if (scale_data && scale_data[y]) {
          for (const stringName in scale_data[y]) {
              if (scale_data[y].hasOwnProperty(stringName) && scale_data[y][stringName]?.[0]?.tones) {
                  scale_data[y][stringName][0].tones.forEach(t => tonesToProcess.add(t));
              }
          }
      }
  }

  // Process each relevant tone
  tonesToProcess.forEach(currentTone => {
      // Select active notes matching the current tone *within the current position's context*
      // This requires knowing which notes belong to the position, which is tricky here.
      // Let's select all active notes with the tone class first.
      var elements = document.querySelectorAll(`.note.${currentTone}.active`);

      // If we have more than 1 active element with this tone name on *different* strings,
      // we might need to decide which to keep based on position rules.
      if (elements.length > 1) {
          const activeStringsForTone = new Set();
          elements.forEach(el => {
              const stringEl = el.closest('[class*="String"]');
              if (stringEl) {
                  const stringName = Array.from(stringEl.classList).find(cls => cls.endsWith('String'));
                  if (stringName) {
                      activeStringsForTone.add(stringName);
                  }
              }
          });

          // If the same note appears active on multiple strings
          if (activeStringsForTone.size > 1) {
              // --- Refined Logic ---
              // 1. Identify the strings defined for the current position 'y'.
              const stringsInPosition = new Set(Object.keys(scale_data[y] || {}));

              // 2. Deactivate notes on strings NOT part of the current position.
              elements.forEach(element => {
                  const stringEl = element.closest('[class*="String"]');
                  if (stringEl) {
                      const stringName = Array.from(stringEl.classList).find(cls => cls.endsWith('String'));
                      if (stringName && !stringsInPosition.has(stringName)) {
                          deactivateSingleNote(element); // Deactivate this specific note element
                      }
                  }
              });

              // 3. Re-query active elements after initial deactivation.
              elements = document.querySelectorAll(`.note.${currentTone}.active`);
              activeStringsForTone.clear();
              elements.forEach(el => {
                  const stringEl = el.closest('[class*="String"]');
                  if (stringEl) {
                      const stringName = Array.from(stringEl.classList).find(cls => cls.endsWith('String'));
                      if (stringName) {
                          activeStringsForTone.add(stringName);
                      }
                  }
              });

              // 4. If still active on multiple strings *within the position*, apply preference logic.
              if (activeStringsForTone.size > 1) {
                  // Preference: Keep notes on strings closer to the middle of the fretboard.
                  // Sort the strings based on their order in string_array.
                  const orderedStrings = Array.from(activeStringsForTone).sort((a, b) => {
                      const aIdx = string_array.indexOf(a);
                      const bIdx = string_array.indexOf(b);
                      return aIdx - bIdx;
                  });

                  // Determine the "best" string(s) to keep (e.g., the middle one or two).
                  // For simplicity, let's prioritize keeping *one* instance, preferably on a middle string.
                  const middleIndex = Math.floor(orderedStrings.length / 2);
                  const stringToKeep = orderedStrings[middleIndex]; // Keep the middle string

                  // Deactivate notes on other strings within the position.
                  elements.forEach(element => {
                      const stringEl = element.closest('[class*="String"]');
                      if (stringEl) {
                          const stringName = Array.from(stringEl.classList).find(cls => cls.endsWith('String'));
                          if (stringName && stringName !== stringToKeep) {
                              deactivateSingleNote(element);
                          }
                      }
                  });
              }
          }
      }
  });
}


// Helper function to deactivate a single note element and its children
function deactivateSingleNote(noteElement) {
    if (!noteElement) return;

    noteElement.classList.remove('active');
    noteElement.style.visibility = 'hidden';
    noteElement.style.opacity = '0';

    const toneImg = noteElement.querySelector('img.tone');
    if (toneImg) {
        toneImg.classList.remove('active');
        toneImg.style.visibility = 'hidden';
        toneImg.style.opacity = '0';
        // Optionally reset src if needed, but hiding might be enough
    }

    const notename = noteElement.querySelector('.notename');
    if (notename) {
        notename.style.visibility = 'hidden';
        notename.style.opacity = '0';
        notename.classList.remove('show-name');
    }
}


function deactivateActiveNotes(string, tone_name) {
  var elements = document.querySelectorAll(`.${string} .note.${tone_name}.active`); // Target .note divs

  if (elements.length === 0) {
    console.warn(`No active notes found for tone ${tone_name} on string ${string} to deactivate`);
    return;
  }

  elements.forEach(function(noteElement) {
    deactivateSingleNote(noteElement); // Use the helper function
  });
}

function avoid_four_notes_on_string(){
  if (!string_array || string_array.length === 0) return; // Guard clause

  const outerStrings = [string_array[0], string_array[string_array.length - 1]];

  outerStrings.forEach((stringName, index) => {
      if (!stringName) return; // Skip if string name is invalid

      const activeNotesOnString = document.querySelectorAll(`.${stringName} .note.active`);

      if (activeNotesOnString.length > 3) {
          // Convert NodeList to array for sorting based on fret position
          const sortedNotes = Array.from(activeNotesOnString).sort((a, b) => {
              const fretA = getFretNumberFromNote(a);
              const fretB = getFretNumberFromNote(b);
              return fretA - fretB; // Sort by ascending fret number
          });

          // If it's the lowest string (index 0), remove the highest fret note among the >3 notes
          if (index === 0) {
              deactivateSingleNote(sortedNotes[sortedNotes.length - 1]); // Deactivate the last note (highest fret)
          }
          // If it's the highest string (index 1), remove the lowest fret note among the >3 notes
          else {
              deactivateSingleNote(sortedNotes[0]); // Deactivate the first note (lowest fret)
          }
      }
  });
}

// Helper function to get fret number from a note element
function getFretNumberFromNote(noteElement) {
    const fretEl = noteElement.closest('[class*="fret"]');
    if (!fretEl) return Infinity; // Return Infinity if fret element not found, placing it last

    const fretClass = Array.from(fretEl.classList).find(cls => cls.startsWith('fret'));
    if (!fretClass) return Infinity;

    const fretName = fretClass.replace('fret', '');
    const fretMap = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
        'fifteen': 15, 'sixteen': 16, 'seventeen': 17
    };
    return fretMap[fretName] || Infinity; // Return Infinity if fret name is not recognized
}


/**
 * Special handling for "All Positions" mode (position '0')
 */
function activateAllPositionsNotes(positionId) { // positionId is '0' here
  if (typeof scale_data === 'undefined' || !scale_data) {
    console.error('Scale data not available.');
    return;
  }
  if (typeof string_array === 'undefined' || !string_array || !string_array.length) {
    console.error('String array not defined or empty.');
    return;
  }

  // --- Step 1: Gather all unique note locations (string-fret-tone) from all defined scale positions ---
  const validScaleNoteLocations = new Set();
  const positions = Object.keys(scale_data).filter(key => key !== 'root' && key !== '0' && !isNaN(parseInt(key))); // Get actual position numbers

  positions.forEach(pos => {
    if (!scale_data[pos]) return; // Skip if position data doesn't exist

    Object.keys(scale_data[pos]).forEach(stringName => {
      if (!scale_data[pos][stringName]?.[0]?.tones) return;

      scale_data[pos][stringName][0].tones.forEach(toneName => {
        // Find the DOM elements for this tone on this string to get fret info
        const noteElements = document.querySelectorAll(`.${stringName} .note.${toneName}`);
        noteElements.forEach(noteEl => {
          const fretEl = noteEl.closest('[class*="fret"]');
          if (fretEl) {
            const fretName = Array.from(fretEl.classList).find(c => c.includes('fret'));
            if (fretName) {
              // Store a unique identifier for this specific note location
              const noteId = `${stringName}-${fretName}-${toneName}`;
              validScaleNoteLocations.add(noteId);
            }
          }
        });
      });
    });
  });

  // --- Step 2: Iterate through all DOM note elements and activate if they match a valid scale location ---
  const allNoteElements = document.querySelectorAll('.note');

  allNoteElements.forEach(noteEl => {
    const stringEl = noteEl.closest('[class*="String"]');
    const fretEl = noteEl.closest('[class*="fret"]');

    if (stringEl && fretEl) {
      const stringName = Array.from(stringEl.classList).find(c => c.endsWith('String'));
      const fretName = Array.from(fretEl.classList).find(c => c.includes('fret'));

      // Find the tone class (e.g., 'c4', 'gs2') associated with this note div
      const toneClass = Array.from(noteEl.classList).find(cls =>
        cls !== 'note' && cls !== 'active' && cls !== 'all-positions-note' && cls !== 'low-fret-note' && !cls.includes('String') && !cls.includes('fret') && cls.match(/^[a-z]+[s|b]?[0-4]$/) // More specific regex for tone names
      );

      if (stringName && fretName && toneClass) {
        const noteId = `${stringName}-${fretName}-${toneClass}`;

        // Check if this specific note location is part of the scale (found in any position)
        if (validScaleNoteLocations.has(noteId)) {
          // Activate the note div
          noteEl.classList.add('active', 'all-positions-note');
          noteEl.style.visibility = 'visible';
          noteEl.style.opacity = '1'; // Use full opacity for clarity in "All" view

          // Activate the tone image inside
          const toneImage = noteEl.querySelector('img.tone');
          if (toneImage) {
            toneImage.classList.add('active');
            toneImage.style.visibility = 'visible';
            toneImage.style.opacity = '1'; // Full opacity

            // Check if it's a root note
            const isRoot = scale_data.root && Object.values(scale_data.root).some(root =>
              root.replace(/[0-9]/g, '') === toneClass.replace(/[0-9]/g, '')
            );

            if (isRoot) {
              toneImage.classList.add('root');
              toneImage.classList.add('active');
              // Explicitly set the red circle image with no query parameters
              toneImage.setAttribute('src', '/static/media/red_circle.svg');
              // Apply explicit styling for consistent appearance
              toneImage.style.opacity = '1';
              toneImage.style.border = '2px solid rgb(204, 0, 0)';
              toneImage.style.boxShadow = 'rgba(255, 0, 0, 0.3) 0px 0px 5px';
              
              // Make sure the notename is visible and has correct color
              const notename = noteEl.querySelector('.notename');
              if (notename) {
                notename.style.color = '#efede8'; // Set the text color explicitly
                notename.style.visibility = 'visible';
                notename.style.opacity = '1';
              }
            } else {
               // Ensure non-roots get the correct octave-based image
               toneImage.classList.remove('root');
               const octaveMatch = toneClass.match(/[a-z]+([0-4])/);
               if (octaveMatch && octaveMatch[1]) {
                   const octave = parseInt(octaveMatch[1]);
                   let svgSrc = '/static/media/';
                   switch (octave) {
                       case 0: svgSrc += 'circle_01.svg'; break;
                       case 1: svgSrc += 'circle_01.svg'; break;
                       case 2: svgSrc += 'circle_02.svg'; break;
                       case 3: svgSrc += 'circle_03.svg'; break;
                       case 4: svgSrc += 'circle_04.svg'; break;
                       default: svgSrc += 'circle_01.svg';
                   }
                   toneImage.setAttribute('src', svgSrc);
               } else {
                   toneImage.setAttribute('src', '/static/media/circle_01.svg');
               }
            }
          }

          // Make notenames visible for active notes
          const notename = noteEl.querySelector('.notename');
          if (notename) {
            notename.style.visibility = 'visible';
            notename.style.opacity = '1';
            notename.classList.add('active');
            // Always show note names
            notename.classList.add('show-name');
          }
        }
      }
    }
  });

  // Optional: Apply constraints like avoid_four_notes_on_string if desired for "All Positions"
  // avoid_four_notes_on_string();
}


// ensureLowFretNotesShown and processNotesOnFret might be redundant if the main logic correctly
// identifies notes based on scale_data across all positions for the 'All Positions' view.
// Commenting them out for now. If low fret notes are missing in 'All Positions', revisit this.
/*
function ensureLowFretNotesShown(positionId) { ... }
function processNotesOnFret(notesOnFret, stringName, fret, positionId, isPriority) { ... }
*/

function updateCursorVisibility(pos_val, max_pos) {
  var leftCursor = document.querySelector('.left-cursor'); // Use class selector
  var rightCursor = document.querySelector('.right-cursor'); // Use class selector

  // If cursor elements aren't found (e.g., dynamically added later or not relevant),
  // simply exit without erroring.
  if (!leftCursor || !rightCursor) {
    return;
  }

  // Convert pos_val to number for comparison
  const currentPos = parseInt(pos_val);

  // Always show cursors when "All Positions" (0) is selected
  if (currentPos === 0) {
    leftCursor.style.display = 'block';
    rightCursor.style.display = 'block';
  } else {
    // Hide left cursor if at the first position (1)
    leftCursor.style.display = (currentPos <= 1) ? 'none' : 'block';
    // Hide right cursor if at the last position
    rightCursor.style.display = (currentPos >= max_pos) ? 'none' : 'block';
  }
}

// SCALE-SPECIFIC CURSOR CLICK HANDLERS - Separated into implementation and interface functions

/**
 * Implementation of left cursor click for scales
 * This handles the actual navigation logic
 * @returns {boolean} Success indicator
 */
function leftCursorClickHandler() {
  console.log("SCALE MODE: leftCursorClick handler executing");
  
  try {
    // Set timestamp to prevent chord handler interference
    window.lastScaleHandlerTime = Date.now();
    
    console.log("CURSOR-DEBUG: leftCursorClickHandler executing");
    
    // Verify we have the right data for scale view
    if (typeof scale_data === 'undefined' || !scale_data) {
      console.log("CURSOR-DEBUG: WARNING - scale_data is not available!");
      
      if (typeof voicing_data !== 'undefined' && voicing_data) {
        console.log("CURSOR-DEBUG: ERROR - voicing_data found but not scale_data. Likely chord view misidentified as scale view.");
        return false;
      }
    }
    
    // Get current position from select element directly
    const posSelect = document.getElementById('position_select');
    let currentPosition = 0;
    
    if (posSelect) {
      currentPosition = parseInt(posSelect.value) || 0;
      console.log(`CURSOR-DEBUG: Current position from select: ${currentPosition}`);
    } else {
      // Fallback to URL
      const urlParams = new URLSearchParams(window.location.search);
      currentPosition = parseInt(urlParams.get('position_select')) || 0;
      console.log(`CURSOR-DEBUG: Current position from URL: ${currentPosition}`);
    }
    
    // Determine new position (decrement, but not below 0)
    let newPosition = currentPosition;
    if (currentPosition > 0) {
      newPosition = currentPosition - 1;
    }
    
    console.log(`SCALE NAVIGATION: ${currentPosition} → ${newPosition}`);
    
    // Update position in select if it exists
    if (posSelect) {
      posSelect.value = String(newPosition);
      
      // Update custom select UI if present
      const displayDiv = document.querySelector('.select-selected');
      if (displayDiv) {
        for (let i = 0; i < posSelect.options.length; i++) {
          if (posSelect.options[i].value == newPosition) {
            displayDiv.innerHTML = posSelect.options[i].innerHTML;
            break;
          }
        }
      }
      
      // Force change event on select
      const event = new Event('change', { bubbles: true });
      posSelect.dispatchEvent(event);
    }
    
    // Update URL parameter directly
    const urlObj = new URL(window.location.href);
    urlObj.searchParams.set('position_select', newPosition);
    window.history.replaceState(null, '', urlObj);
    
    // Update global state for other components
    window.currentScalePosition = newPosition;
    
    // Force refresh of the fretboard
    resetFretboard();
    getTonesFromDataScales(String(newPosition));
    
    // Update cursor visibility
    const maxPos = window.maxScalePosition || 5;
    updateCursorVisibility(newPosition, maxPos);
    
    return true;
  } catch (error) {
    console.error("Error in scale leftCursorClick:", error);
    return false;
  }
}

/**
 * Implementation of right cursor click for scales
 * This handles the actual navigation logic
 * @returns {boolean} Success indicator
 */
function rightCursorClickHandler() {
  console.log("SCALE MODE: rightCursorClick handler executing");
  
  try {
    // Set timestamp to prevent chord handler interference
    window.lastScaleHandlerTime = Date.now();
    
    console.log("CURSOR-DEBUG: rightCursorClickHandler executing");
    
    // Verify we have the right data for scale view
    if (typeof scale_data === 'undefined' || !scale_data) {
      console.log("CURSOR-DEBUG: WARNING - scale_data is not available!");
      
      if (typeof voicing_data !== 'undefined' && voicing_data) {
        console.log("CURSOR-DEBUG: ERROR - voicing_data found but not scale_data. Likely chord view misidentified as scale view.");
        return false;
      }
    }
    
    // Get current position from select element directly
    const posSelect = document.getElementById('position_select');
    let currentPosition = 0;
    let maxPosition = window.maxScalePosition || 5; // Use global if available
    
    if (posSelect) {
      currentPosition = parseInt(posSelect.value) || 0;
      console.log(`CURSOR-DEBUG: Current position from select: ${currentPosition}`);
      
      // Determine maximum position from select options if not already available
      if (!maxPosition) {
        for (let i = 0; i < posSelect.options.length; i++) {
          const optVal = parseInt(posSelect.options[i].value);
          if (!isNaN(optVal) && optVal !== 0 && optVal > maxPosition) {
            maxPosition = optVal;
          }
        }
        console.log(`CURSOR-DEBUG: Calculated max position: ${maxPosition}`);
      }
    } else {
      // Fallback to URL
      const urlParams = new URLSearchParams(window.location.search);
      currentPosition = parseInt(urlParams.get('position_select')) || 0;
      console.log(`CURSOR-DEBUG: Current position from URL: ${currentPosition}`);
    }
    
    // Determine new position
    let newPosition = currentPosition;
    if (currentPosition === 0) {
      // From "All Positions" (0) go to position 1
      newPosition = 1;
    } else if (currentPosition < maxPosition) {
      // Increment but don't exceed maximum
      newPosition = currentPosition + 1;
    }
    
    console.log(`SCALE NAVIGATION: ${currentPosition} → ${newPosition}`);
    
    // Update position in select if it exists
    if (posSelect) {
      posSelect.value = String(newPosition);
      
      // Update custom select UI if present
      const displayDiv = document.querySelector('.select-selected');
      if (displayDiv) {
        for (let i = 0; i < posSelect.options.length; i++) {
          if (posSelect.options[i].value == newPosition) {
            displayDiv.innerHTML = posSelect.options[i].innerHTML;
            break;
          }
        }
      }
      
      // Force change event on select
      const event = new Event('change', { bubbles: true });
      posSelect.dispatchEvent(event);
    }
    
    // Update URL parameter directly
    const urlObj = new URL(window.location.href);
    urlObj.searchParams.set('position_select', newPosition);
    window.history.replaceState(null, '', urlObj);
    
    // Update global state for other components
    window.currentScalePosition = newPosition;
    
    // Force refresh of the fretboard
    resetFretboard();
    getTonesFromDataScales(String(newPosition));
    
    // Update cursor visibility
    updateCursorVisibility(newPosition, maxPosition);
    
    return true;
  } catch (error) {
    console.error("Error in scale rightCursorClick:", error);
    return false;
  }
}


/* Look for any elements with the class "custom-select": */
// Add event listeners for custom select fields
document.addEventListener('DOMContentLoaded', function() {
  customizeSelectField('sfbsfnos'); // Scale/Fretboard/ScaleForm/NotesOptionSelect
  customizeSelectField('sfbsfpos'); // Scale/Fretboard/ScaleForm/PositionSelect
  customizeSelectField('sfbsf'); // Scale/Fretboard/ScaleForm/RootSelect

  // Initial cursor visibility update based on loaded position
  const initialPosVal = new URL(window.location.href).searchParams.get('position_select') || '0';
  let maxPos = 0;
  const selectElement = document.getElementById('position_select');
  if (selectElement) {
      const options = selectElement.getElementsByTagName('option');
      for (let i = 0; i < options.length; i++) {
          const val = parseInt(options[i].value);
          if (!isNaN(val) && val !== 0 && val > maxPos) {
              maxPos = val;
          }
      }
  }
  updateCursorVisibility(initialPosVal, maxPos);

  // Enhanced cursor fix that prevents chord-cursor-fix.js from interfering
  setTimeout(function() {
    console.log("CURSOR-DEBUG: Initializing scale view cursor handlers");
    
    // Set explicit flag to indicate we're in scale view
    window.isScaleView = true;
    window.isChordView = false;
    
    // First check if we're truly in scale view
    const url = window.location.href.toLowerCase();
    const isScaleOrArpeggio = url.includes('scale') || url.includes('arpeggio') || !url.includes('chord');
    
    if (!isScaleOrArpeggio) {
      console.log("CURSOR-DEBUG: Not in scale or arpeggio view, skipping cursor fix");
      return;
    }
    
    console.log("CURSOR-DEBUG: Confirmed scale/arpeggio view, applying fixes");
    
    // Make sure chord cursor fix doesn't run for scale views
    if (typeof window.handleChordCursorClick === 'function') {
      const origChordCursorHandler = window.handleChordCursorClick;
      window.handleChordCursorClick = function(direction, e) {
        // Skip if we're in scale view
        if (window.isScaleView) {
          console.log("CURSOR-DEBUG: Blocking chord cursor handler in scale view");
          return false;
        }
        return origChordCursorHandler(direction, e);
      };
    }
    
    // Override global click handlers
    const originalLeftClick = window.leftCursorClick;
    const originalRightClick = window.rightCursorClick;
    
    // Global function that will be called by inline onclick
    window.leftCursorClick = function(e) {
      console.log("CURSOR-DEBUG: Left cursor click detected");
      if (e) e.preventDefault();
      
      // Skip if chord handler already handled it
      if (typeof window.lastChordHandlerTime === 'number' && 
          (Date.now() - window.lastChordHandlerTime < 100)) {
        console.log("CURSOR-DEBUG: Skipping - chord handler recently fired");
        return false;
      }
      
      // Call our enhanced scale-specific handler for scale views
      if (window.isScaleView) {
        console.log("CURSOR-DEBUG: Handling left click in scale view");
        return leftCursorClickHandler();
      }
      
      // Otherwise call original handler
      console.log("CURSOR-DEBUG: Using original left click handler");
      if (typeof originalLeftClick === 'function') {
        return originalLeftClick(e);
      }
    };
    
    window.rightCursorClick = function(e) {
      console.log("CURSOR-DEBUG: Right cursor click detected");
      if (e) e.preventDefault();
      
      // Skip if chord handler already handled it
      if (typeof window.lastChordHandlerTime === 'number' && 
          (Date.now() - window.lastChordHandlerTime < 100)) {
        console.log("CURSOR-DEBUG: Skipping - chord handler recently fired");
        return false;
      }
      
      // Call our enhanced scale-specific handler for scale views
      if (window.isScaleView) {
        console.log("CURSOR-DEBUG: Handling right click in scale view");
        return rightCursorClickHandler();
      }
      
      // Otherwise call original handler
      console.log("CURSOR-DEBUG: Using original right click handler");
      if (typeof originalRightClick === 'function') {
        return originalRightClick(e);
      }
    };
    
    // Fix any fpf variants from cursor-inversion.js
    if (typeof window.fpfLeftCursorClick === 'function') {
      const origFpfLeft = window.fpfLeftCursorClick;
      window.fpfLeftCursorClick = function(context) {
        console.log("CURSOR-DEBUG: fpfLeftCursorClick called with context:", context);
        
        // Skip if we're in scale view and the context indicates scales
        if (window.isScaleView && context && context.currentMode === 'scales') {
          return leftCursorClickHandler();
        }
        
        // Otherwise use original
        return origFpfLeft(context);
      };
    }
    
    if (typeof window.fpfRightCursorClick === 'function') {
      const origFpfRight = window.fpfRightCursorClick;
      window.fpfRightCursorClick = function(context) {
        console.log("CURSOR-DEBUG: fpfRightCursorClick called with context:", context);
        
        // Skip if we're in scale view and the context indicates scales
        if (window.isScaleView && context && context.currentMode === 'scales') {
          return rightCursorClickHandler();
        }
        
        // Otherwise use original
        return origFpfRight(context);
      };
    }
    
    // Fix cursor elements to ensure they have proper events
    const leftCursor = document.querySelector('.left-cursor');
    const rightCursor = document.querySelector('.right-cursor');
    
    if (leftCursor && rightCursor) {
      console.log("CURSOR-DEBUG: Found cursor elements, updating...");
      
      // Remove inline onclick attributes to avoid conflicts
      leftCursor.removeAttribute('onclick');
      rightCursor.removeAttribute('onclick');
      
      // Attach direct event listeners
      leftCursor.addEventListener('click', function(e) {
        console.log("CURSOR-DEBUG: Direct left cursor click");
        e.preventDefault();
        e.stopPropagation();
        window.isScaleView ? leftCursorClickHandler() : window.leftCursorClick(e);
      });
      
      rightCursor.addEventListener('click', function(e) {
        console.log("CURSOR-DEBUG: Direct right cursor click");
        e.preventDefault();
        e.stopPropagation();
        window.isScaleView ? rightCursorClickHandler() : window.rightCursorClick(e);
      });
      
      console.log("CURSOR-DEBUG: Cursor event listeners updated");
    }
    
    console.log("CURSOR-DEBUG: Scale cursor fix fully applied");
  }, 200); // Slightly longer delay to ensure all other scripts have initialized
});

function customizeSelectField(className) {
  var x, i, j, l, ll, selElmnt, a, b, c;
  /* Look for any elements with the class name: */
  x = document.getElementsByClassName(className);
  l = x.length;
  for (i = 0; i < l; i++) {
    selElmnt = x[i].getElementsByTagName("select")[0];
    if (!selElmnt) continue; // Skip if select element is not found
    ll = selElmnt.length;
    /* For each element, create a new DIV that will act as the selected item: */
    a = document.createElement("DIV");
    a.setAttribute("class", "select-selected");
    a.innerHTML = selElmnt.options[selElmnt.selectedIndex].innerHTML;
    x[i].appendChild(a);
    /* For each element, create a new DIV that will contain the option list: */
    b = document.createElement("DIV");
    b.setAttribute("class", "select-items select-hide");
    for (j = 1; j < ll; j++) { // Start from 1 to skip the placeholder option if it exists
      /* For each option in the original select element,
      create a new DIV that will act as an option item: */
      c = document.createElement("DIV");
      c.innerHTML = selElmnt.options[j].innerHTML;
      // Store the actual value from the option
      c.setAttribute('data-value', selElmnt.options[j].value);

      c.addEventListener("click", function(e) {
          /* When an item is clicked, update the original select box,
          and the selected item: */
          var y, i, k, s, h, sl, yl;
          s = this.parentNode.parentNode.getElementsByTagName("select")[0];
          sl = s.length;
          h = this.parentNode.previousSibling; // The 'select-selected' div
          for (i = 0; i < sl; i++) {
            // Match based on the stored value
            if (s.options[i].value == this.getAttribute('data-value')) {
              s.selectedIndex = i;
              h.innerHTML = this.innerHTML; // Update display text
              y = this.parentNode.getElementsByClassName("same-as-selected");
              yl = y.length;
              for (k = 0; k < yl; k++) {
                y[k].removeAttribute("class");
              }
              this.setAttribute("class", "same-as-selected");

              // Trigger the change event on the original select element
              var event = new Event('change', { 'bubbles': true });
              s.dispatchEvent(event);

              break;
            }
          }
          h.click(); // Close the select box by simulating a click on the selected item div
      });
      b.appendChild(c);
    }
    x[i].appendChild(b);
    a.addEventListener("click", function(e) {
      /* When the select box is clicked, close any other select boxes,
      and open/close the current select box: */
      e.stopPropagation();
      closeAllSelect(this);
      this.nextSibling.classList.toggle("select-hide");
      this.classList.toggle("select-arrow-active");
    });
  }
}


function closeAllSelect(elmnt) {
  /* A function that will close all select boxes in the document,
  except the current select box: */
  var x, y, i, xl, yl, arrNo = [];
  x = document.getElementsByClassName("select-items");
  y = document.getElementsByClassName("select-selected");
  xl = x.length;
  yl = y.length;
  for (i = 0; i < yl; i++) {
    if (elmnt == y[i]) {
      arrNo.push(i)
    } else {
      y[i].classList.remove("select-arrow-active");
    }
  }
  for (i = 0; i < xl; i++) {
    // Check if the index is NOT in arrNo (meaning it's not the clicked element's dropdown)
    let shouldClose = true;
    for (let k = 0; k < arrNo.length; k++) {
        if (i === arrNo[k]) {
            shouldClose = false;
            break;
        }
    }
    if (shouldClose) {
        x[i].classList.add("select-hide");
    }
  }
}

function numberToEnglishFret(num) {
    const fretMap = {
        1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
        6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
        11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen',
        15: 'fifteen', 16: 'sixteen', 17: 'seventeen'
        // Add more if needed
    };
    return fretMap[num] || '';
}


// Function to handle changing the scale root note
function changeScaleRoot(noteChange) {
    const url = new URL(window.location.href);
    let currentRoot = parseInt(url.searchParams.get('root')) || 1; // Default to 1 (C) if not set

    // Assuming root notes are numbered 1-12 (C to B)
    const maxRoot = 12;
    const minRoot = 1;

    currentRoot += noteChange;

    // Wrap around
    if (currentRoot > maxRoot) {
        currentRoot = minRoot;
    } else if (currentRoot < minRoot) {
        currentRoot = maxRoot;
    }

    url.searchParams.set('root', currentRoot);
    window.location.href = url.toString();
}

// Keyboard listener for root note changes (right arrow key functionality removed)
document.addEventListener('keydown', function(event) {
    // Right arrow key functionality has been removed
});