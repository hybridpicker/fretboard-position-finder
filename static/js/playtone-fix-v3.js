/**
 * Alternative approach to playTone that focuses on active notes rather than specific selectors
 */
function playTone(tone, stringName) {
  console.log(`[playTone] Called with tone=${tone}, stringName=${stringName}`);
  
  // Create audio element but don't play it yet
  const audioFile = `static/media/tone_sounds/${tone}.mp3`;
  const audio = new Audio(audioFile);
  
  // STRATEGY 1: Check if any notes are active at all on this string
  const allActiveNotes = document.querySelectorAll(`.fret.${stringName} .note.active, .fret.${stringName} img.active`);
  console.log(`[playTone] Found ${allActiveNotes.length} active notes on string ${stringName}`);
  
  if (allActiveNotes.length > 0) {
    // We have active notes, so play the tone regardless of the specific note
    console.log(`[playTone] Active notes found on ${stringName}, playing ${tone}`);
    
    // Play the audio
    audio.play().catch(error => {
      console.warn(`[playTone] Error playing audio: ${error.message}`);
    });
    
    // Add visual feedback to the active note
    const activeElement = allActiveNotes[0];
    activeElement.classList.add('playing');
    
    // Remove the visual feedback after a delay
    setTimeout(() => {
      activeElement.classList.remove('playing');
    }, 300);
    
    return true;
  }
  
  // STRATEGY 2: If no active notes found, check if we can find the specific element
  console.log(`[playTone] Looking for specific tone element ${tone}`);
  
  // Try all possible selector patterns
  const selectors = [
    `.fret.${stringName} .note.${tone}`,
    `.fret.${stringName} .note-click .note.${tone}`,
    `.${stringName} .note.${tone}`,
    `.note.${tone}`,
    `.fret.${stringName} img.tone.${tone}`,
    `img.tone.${tone}`
  ];
  
  let noteElement = null;
  
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element) {
      noteElement = element;
      console.log(`[playTone] Found element with selector ${selector}:`, element);
      break;
    }
  }
  
  if (noteElement) {
    // We found the element, but it's not active, so don't play
    console.log(`[playTone] Found the note element, but it's not active. Not playing.`);
  } else {
    console.warn(`[playTone] Could not find any element for tone ${tone} on string ${stringName}`);
  }
  
  // STRATEGY 3: For debugging, dump information about all note elements on this string
  console.log(`[playTone] Analyzing all notes on string ${stringName}:`);
  
  const allNotes = document.querySelectorAll(`.fret.${stringName} .note`);
  
  console.log(`[playTone] Found ${allNotes.length} notes on string ${stringName}`);
  allNotes.forEach((note, index) => {
    if (index < 5) { // Limit to 5 to avoid console spam
      console.log(`- Note ${index}:`, {
        className: note.className,
        hasActiveClass: note.classList.contains('active'),
        hasThisToneClass: note.classList.contains(tone),
        imgSrc: note.querySelector('img')?.src || 'no img'
      });
    }
  });
  
  return false; // Didn't play any tone
}
