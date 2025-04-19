/**
 * A simplified version of playTone that prioritizes playing audio over visual effects
 * This version will always play the tone, even if it can't find the corresponding element
 */
document.addEventListener('DOMContentLoaded', function() {
  console.log("[SimpleFix] Initializing playTone override");
  
  // Store the original function for reference
  window.originalPlayTone = window.playTone;
  
  // Replace with our simplified version
  window.playTone = function(tone, stringName) {
    console.log(`[SimpleFix] PlayTone called with tone=${tone}, stringName=${stringName}`);
    
    // Always create and play the audio
    const audioFile = `static/media/tone_sounds/${tone}.mp3`;
    const audio = new Audio(audioFile);
    
    // Try to play the audio immediately
    audio.play().catch(error => {
      console.warn(`[SimpleFix] Error playing audio for ${tone}: ${error.message}`);
    });
    
    // Try to find an element to highlight (but this is now secondary)
    let foundElement = false;
    
    // First look for any active elements on the string
    if (stringName) {
      const activeElements = document.querySelectorAll(
        `.fret.${stringName} img.active, .${stringName} img.active, .fret.${stringName} .note.active img`
      );
      
      if (activeElements.length > 0) {
        const element = activeElements[0];
        element.classList.add('playing');
        setTimeout(() => element.classList.remove('playing'), 300);
        foundElement = true;
      }
    }
    
    // If no active elements found, try to at least find the tone element
    if (!foundElement) {
      // Try all possible selectors for this tone
      const selectors = [
        `.fret.${stringName} .note.${tone} img`,
        `.${stringName} .note.${tone} img`,
        `.note.${tone} img`,
        `.fret.${stringName} img.tone.${tone}`,
        `.${stringName} img.tone.${tone}`,
        `img.tone.${tone}`
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
    
    return true; // Always return true since we at least played the audio
  };
  
  console.log("[SimpleFix] PlayTone function has been replaced");
});
