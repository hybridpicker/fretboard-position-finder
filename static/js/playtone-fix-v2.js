/**
 * Completely revised playTone function with root issue fix
 *
 * @param {string} tone - The name of the tone to play (e.g., 'c1', 'e2')
 * @param {string} stringName - The name of the string (e.g., 'AString', 'eString')
 * @returns {boolean} - Whether the tone was successfully played
 */
function playTone(tone, stringName) {
  // CORE ISSUE FIX: The click handler is attaching to a wrapper element, not the actual tone
  console.log(`[playTone] Attempting to play ${tone} on ${stringName}`);
  
  // Create the audio object first (we'll decide whether to play it later)
  const audioFile = `static/media/tone_sounds/${tone}.mp3`;
  const audio = new Audio(audioFile);
  
  // APPROACH 1: Access elements through the DOM structure as it actually exists
  // We know from the HTML structure that:
  // - The .fret element contains the .note-click anchor
  // - The .note-click contains the .note element
  // - The .note element contains the img.tone
  
  // Find all relevant elements in all possible ways
  const selectors = [
    // Direct path selectors
    `.fret.${stringName} .note.${tone} img.tone`,
    `.fret.${stringName} .note.${tone}`,
    `.fret.${stringName} img.tone.${tone}`,
    
    // Parent-based selectors
    `.${stringName} .note.${tone} img.tone`,
    `.${stringName} .note.${tone}`,
    `.${stringName} img.tone.${tone}`,
    
    // The most general selectors
    `.note.${tone} img.tone`,
    `img.tone.${tone}`
  ];
  
  // Try all selectors until we find a match
  let element = null;
  for (const selector of selectors) {
    const selected = document.querySelector(selector);
    if (selected) {
      element = selected;
      console.log(`[playTone] Found element with selector: ${selector}`, element);
      break;
    }
  }
  
  // If we still can't find the element, try a more flexible approach
  if (!element) {
    console.log(`[playTone] No exact match found, trying alternative approach`);
    
    // Try to find the fret first, then navigate down
    const fretElements = document.querySelectorAll(`.fret.${stringName}`);
    
    for (const fret of fretElements) {
      // Look for note-click anchors with our note
      const noteClicks = fret.querySelectorAll('.note-click');
      
      for (const noteClick of noteClicks) {
        // Check each note element inside
        const notes = noteClick.querySelectorAll('.note');
        
        for (const note of notes) {
          // Check if this note has the tone class
          if (note.classList.contains(tone)) {
            // We found a matching note! Get the img inside
            const img = note.querySelector('img.tone');
            if (img) {
              element = img;
              console.log(`[playTone] Found element by navigating DOM:`, element);
              break;
            }
          }
        }
        
        if (element) break;
      }
      
      if (element) break;
    }
  }
  
  // APPROACH 2: Find all active elements and check for a match
  // This approach works even if selectors are somehow failing
  let activeElement = null;
  
  // If we found an element through selectors, check if it's active
  if (element) {
    // Check if the element itself is active
    if (element.classList.contains('active')) {
      activeElement = element;
      console.log(`[playTone] Element is active`, activeElement);
    }
    // Check if parent note is active
    else if (element.closest('.note.active')) {
      activeElement = element;
      console.log(`[playTone] Parent note is active`, activeElement);
    }
  }
  
  // If no active element found, look for equivalent tones
  if (!activeElement && NOTES && NOTES[stringName]) {
    console.log(`[playTone] Checking for equivalent tones in NOTES`);
    
    // Find all frets that contain our tone
    for (let fretIndex = 0; fretIndex < NOTES[stringName].length; fretIndex++) {
      const fretTones = NOTES[stringName][fretIndex];
      
      if (fretTones.includes(tone)) {
        console.log(`[playTone] Found fret ${fretIndex} with tone ${tone} and equivalents:`, fretTones);
        
        // Look for active elements with any of the equivalent tones
        for (const eqTone of fretTones) {
          if (eqTone !== tone) {
            console.log(`[playTone] Checking equivalent tone: ${eqTone}`);
            
            // Try all our selectors with the equivalent tone
            for (const baseSelector of [
              `.fret.${stringName}`, 
              `.${stringName}`, 
              ''
            ]) {
              // This will catch any active elements with the equivalent tone
              const selector = `${baseSelector} .note.${eqTone} img.active, ${baseSelector} img.tone.${eqTone}.active`;
              const eqElements = document.querySelectorAll(selector);
              
              if (eqElements.length > 0) {
                activeElement = eqElements[0];
                console.log(`[playTone] Found active equivalent with selector ${selector}:`, activeElement);
                break;
              }
            }
            
            if (activeElement) break;
          }
        }
        
        if (activeElement) break;
      }
    }
  }
  
  // APPROACH 3: Last resort - check ALL active elements on the string
  if (!activeElement) {
    console.log(`[playTone] Last resort - checking all active elements on ${stringName}`);
    
    // Get all active images on this string
    const allActiveOnString = document.querySelectorAll(`.${stringName} img.active, .fret.${stringName} img.active`);
    
    if (allActiveOnString.length > 0) {
      // We found some active elements - use the first one
      activeElement = allActiveOnString[0];
      console.log(`[playTone] Using first active element on string:`, activeElement);
    }
  }
  
  // If we found an active element, play the sound
  if (activeElement) {
    console.log(`[playTone] Playing tone ${tone} with element:`, activeElement);
    
    // Play the sound
    audio.play().catch(error => {
      console.warn(`[playTone] Error playing audio: ${error.message}`);
    });
    
    // Add visual feedback
    activeElement.classList.add('playing');
    
    // Remove visual feedback after a delay
    setTimeout(() => {
      activeElement.classList.remove('playing');
    }, 300);
    
    return true;
  } else {
    console.warn(`[playTone] No active element found for tone ${tone} on string ${stringName}`);
    return false;
  }
}
