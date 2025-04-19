// Fixed playTone Function
function playTone(tone, stringName = null) {
  // First, check if tone sounds file exists to avoid errors
  const audioFile = `static/media/tone_sounds/${tone}.mp3`;
  const audio = new Audio(audioFile);

  // Based on the template structure in fretboard_fretboard.html
  // The note elements are structured as:
  // <div class="note c1">
  //   <img class="tone c1" src="...">
  //   <div class="notename c1">...</div>
  // </div>

  // Find all possible elements for this tone on this string
  let noteElement, imgElement;
  
  if (stringName) {
    // First try looking for the note div with the tone class in the specified string
    noteElement = document.querySelector(`.fret.${stringName} .note.${tone}`);
    
    // Also look for the img with the tone class
    imgElement = document.querySelector(`.fret.${stringName} img.tone.${tone}`);
  } else {
    // Look across all strings if no specific string was provided
    noteElement = document.querySelector(`.note.${tone}`);
    imgElement = document.querySelector(`img.tone.${tone}`);
  }

  // Debug what we found
  console.log(`Looking for tone ${tone} on string ${stringName || 'any'}`);
  console.log(`Found noteElement:`, noteElement);
  console.log(`Found imgElement:`, imgElement);

  // Try to find an active element
  let activeElement = null;

  // If the note div has an active image inside it, use that
  if (noteElement) {
    const activeImg = noteElement.querySelector('img.active');
    if (activeImg) {
      activeElement = activeImg;
    }
    // Otherwise, if the note itself has active class
    else if (noteElement.classList.contains('active')) {
      // Get the img inside this note
      const img = noteElement.querySelector('img.tone');
      if (img) {
        activeElement = img;
      }
    }
  }

  // If we found the img element directly and it's active, use it
  if (!activeElement && imgElement && imgElement.classList.contains('active')) {
    activeElement = imgElement;
  }

  // If no active element was found, check for equivalent tones using NOTES
  if (!activeElement && stringName && NOTES[stringName]) {
    try {
      console.log(`Looking for equivalent tones for ${tone} on ${stringName}`);
      
      // Find which fret contains our tone
      let targetFret = -1;
      let equivalentTones = [];
      
      for (let fretIndex = 0; fretIndex < NOTES[stringName].length; fretIndex++) {
        if (NOTES[stringName][fretIndex].includes(tone)) {
          targetFret = fretIndex;
          equivalentTones = NOTES[stringName][fretIndex];
          break;
        }
      }
      
      if (targetFret >= 0) {
        console.log(`Found tone ${tone} at fret ${targetFret} with equivalents:`, equivalentTones);
        
        // Look for active elements with any of the equivalent tones
        for (const eqTone of equivalentTones) {
          if (eqTone !== tone) {
            console.log(`Checking equivalent tone: ${eqTone}`);
            
            const eqNote = document.querySelector(`.fret.${stringName} .note.${eqTone}`);
            const eqImg = document.querySelector(`.fret.${stringName} img.tone.${eqTone}`);
            
            // First check if the equivalent note has an active image
            if (eqNote) {
              const activeEqImg = eqNote.querySelector('img.active');
              if (activeEqImg) {
                activeElement = activeEqImg;
                console.log(`Found active equivalent image for ${eqTone}`);
                break;
              }
              // Or if the note itself is active
              else if (eqNote.classList.contains('active')) {
                const img = eqNote.querySelector('img.tone');
                if (img) {
                  activeElement = img;
                  console.log(`Found active equivalent note for ${eqTone}`);
                  break;
                }
              }
            }
            
            // Check the img directly
            if (!activeElement && eqImg && eqImg.classList.contains('active')) {
              activeElement = eqImg;
              console.log(`Found active equivalent img for ${eqTone}`);
              break;
            }
          }
        }
      }
    } catch (error) {
      console.error('Error looking for equivalent tones:', error);
    }
  }

  // Play the tone and show visual feedback if we found an active element
  if (activeElement) {
    console.log(`Playing tone ${tone} with element:`, activeElement);
    
    audio.play().catch(error => {
      console.warn(`Error playing audio for tone ${tone}: ${error.message}`);
    });

    // Add a class to temporarily brighten the element
    activeElement.classList.add('playing');
    
    // Remove the class after a short duration
    setTimeout(() => {
      activeElement.classList.remove('playing');
    }, 300); // Duration of the brightness effect in milliseconds
    
    return true; // Successfully played
  } else {
    console.warn(`Element for tone ${tone} on string ${stringName} and its equivalent are not active or not found.`);
    return false; // Failed to play
  }
}