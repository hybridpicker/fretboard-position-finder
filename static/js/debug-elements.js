// Debug script to print out the complete HTML structure of note elements
document.addEventListener('DOMContentLoaded', function() {
  console.log("DEBUG: Starting element structure analysis");
  
  // Examine string structure
  const strings = ['highAString', 'eString', 'bString', 'gString', 'dString', 'AString', 'ELowString', 'lowBString'];
  
  // Check which strings actually exist in the DOM
  console.log("DEBUG: Checking which strings exist in the DOM");
  strings.forEach(stringName => {
    const stringElements = document.querySelectorAll(`.${stringName}`);
    console.log(`String ${stringName}: ${stringElements.length} elements found`);
  });
  
  // Looking for specific problematic tones
  const problematicTones = [
    { tone: 'c1', string: 'AString' },
    { tone: 'd1', string: 'AString' },
    { tone: 'e2', string: 'bString' },
    { tone: 'c3', string: 'eString' },
    { tone: 'a1', string: 'dString' },
    { tone: 'd3', string: 'eString' }
  ];
  
  console.log("DEBUG: Analyzing problematic tones");
  problematicTones.forEach(({tone, string}) => {
    // Try different selector patterns
    const directImgSelector = `.${string} img.tone.${tone}`;
    const noteSelector = `.${string} .note.${tone}`;
    const fretNoteSelector = `.fret.${string} .note.${tone}`;
    const fretImgSelector = `.fret.${string} img.tone.${tone}`;
    
    console.log(`\nDEBUG: Checking tone ${tone} on string ${string}`);
    console.log(`- Direct img selector "${directImgSelector}": ${document.querySelectorAll(directImgSelector).length} found`);
    console.log(`- Note selector "${noteSelector}": ${document.querySelectorAll(noteSelector).length} found`);
    console.log(`- Fret note selector "${fretNoteSelector}": ${document.querySelectorAll(fretNoteSelector).length} found`);
    console.log(`- Fret img selector "${fretImgSelector}": ${document.querySelectorAll(fretImgSelector).length} found`);
    
    // Get a sample element if available to inspect structure
    const anyToneElement = document.querySelector(`.${string} img.tone`);
    if (anyToneElement) {
      const parent = anyToneElement.closest('.note');
      if (parent) {
        console.log(`- Sample note structure for ${string}:`, parent.outerHTML);
      }
    }
    
    // Check the tone classes more specifically
    const allToneImgs = document.querySelectorAll(`.${string} img.tone`);
    console.log(`- All tone imgs in ${string}: ${allToneImgs.length} found`);
    console.log("- Checking classes on each image:");
    allToneImgs.forEach((img, index) => {
      if (index < 5) { // Limit to first 5 to avoid console spam
        console.log(`  ${index}: ${img.className}, Parent: ${img.parentElement.className}`);
      }
    });
    
    // Check notes data structure
    if (window.NOTES && window.NOTES[string]) {
      console.log(`- NOTES data for ${string} contains ${tone}?`, 
                 NOTES[string].some(fret => fret.includes(tone)));
    }
  });
  
  // Overall structure sample
  const noteElement = document.querySelector('.note');
  if (noteElement) {
    console.log("\nDEBUG: Sample note element structure:", noteElement.outerHTML);
  }
  
  const fretElement = document.querySelector('.fret');
  if (fretElement) {
    console.log("\nDEBUG: Sample fret element structure:", fretElement.outerHTML);
  }
  
  console.log("DEBUG: Element structure analysis complete");
});
