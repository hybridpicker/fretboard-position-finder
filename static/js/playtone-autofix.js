/**
 * An enhanced version of playTone that works with enharmonic equivalents
 * and handles the special case where a sharp/flat tone is displayed differently
 */
document.addEventListener('DOMContentLoaded', function() {
  console.log("[EnhancedFix] Initializing playTone override");
  
  // Store the original function for reference
  window.originalPlayTone = window.playTone;
  
  // Define enharmonic equivalents mapping
  const enharmonicMap = {
    'cs': 'db', 'db': 'cs',
    'ds': 'eb', 'eb': 'ds',
    'fs': 'gb', 'gb': 'fs',
    'gs': 'ab', 'ab': 'gs',
    'as': 'bb', 'bb': 'as'
  };
  
  // Helper function to get enharmonic equivalent of a tone
  function getEnharmonicEquivalent(tone) {
    // Extract note and octave
    const match = tone.match(/([a-z]+)([0-4])/);
    if (!match) return null;
    
    const [_, note, octave] = match;
    
    // Check if there's an enharmonic equivalent
    if (enharmonicMap[note]) {
      return `${enharmonicMap[note]}${octave}`;
    }
    
    return null;
  }
  
  // Replace with our enhanced version
  window.playTone = function(tone, stringName) {
    console.log(`[EnhancedFix] PlayTone called with tone=${tone}, stringName=${stringName}`);
    
    // Find both the original tone and its enharmonic equivalent
    const enharmonicTone = getEnharmonicEquivalent(tone);
    console.log(`[EnhancedFix] Enharmonic equivalent: ${enharmonicTone}`);
    
    // Array of tones to try playing (original first, then enharmonic)
    const tonesToTry = [tone];
    if (enharmonicTone) tonesToTry.push(enharmonicTone);
    
    // Try to play the audio file for the first available tone
    let audioPlayed = false;
    
    for (const currentTone of tonesToTry) {
      if (audioPlayed) break;
      
      const audioFile = `static/media/tone_sounds/${currentTone}.mp3`;
      const audio = new Audio(audioFile);
      
      try {
        audio.play();
        console.log(`[EnhancedFix] Playing audio for ${currentTone}`);
        audioPlayed = true;
      } catch(error) {
        console.warn(`[EnhancedFix] Error playing audio for ${currentTone}: ${error.message}`);
      }
    }
    
    // Try to find an element to highlight
    let foundElement = false;
    
    // Try both the original tone and its enharmonic equivalent for visual highlight
    for (const currentTone of tonesToTry) {
      if (foundElement) break;
      
      // First check if there are any active elements on this string
      if (stringName) {
        const activeElements = document.querySelectorAll(
          `.fret.${stringName} img.active, .${stringName} img.active, .fret.${stringName} .note.active img`
        );
        
        if (activeElements.length > 0) {
          const element = activeElements[0];
          element.classList.add('playing');
          setTimeout(() => element.classList.remove('playing'), 300);
          foundElement = true;
          break;
        }
      }
      
      // If no active elements found, try to find the specific tone element
      // Try all possible selectors for this tone
      const selectors = [
        `.fret.${stringName} .note.${currentTone} img`,
        `.${stringName} .note.${currentTone} img`,
        `.note.${currentTone} img`,
        `.fret.${stringName} img.tone.${currentTone}`,
        `.${stringName} img.tone.${currentTone}`,
        `img.tone.${currentTone}`
      ];
      
      for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element) {
          // Add visual feedback
          element.classList.add('playing');
          setTimeout(() => element.classList.remove('playing'), 300);
          foundElement = true;
          break;
        }
      }
    }
    
    // If still nothing found, do a more general search for any element
    // This handles the case where the HTML structure has the onclick on a parent
    // but the actual tone class is on a child with a different name
    if (!foundElement) {
      const clickHandlers = document.querySelectorAll(`a[onclick*="playTone('${tone}'"]`);
      
      if (clickHandlers.length > 0) {
        const element = clickHandlers[0];
        // Look for any img inside this element
        const img = element.querySelector('img');
        if (img) {
          img.classList.add('playing');
          setTimeout(() => img.classList.remove('playing'), 300);
          foundElement = true;
        } else {
          // Apply to the element itself as fallback
          element.classList.add('playing');
          setTimeout(() => element.classList.remove('playing'), 300);
          foundElement = true;
        }
      }
    }
    
    console.log(`[EnhancedFix] Visual element found: ${foundElement}`);
    
    return true; // Always return true since we at least attempted to play the audio
  };
  
  console.log("[EnhancedFix] PlayTone function has been replaced");
});
