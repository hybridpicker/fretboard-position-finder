/**
 * Utility functions for the chord view controller 
 */

// Default fret preferences for chord inversions and string combinations
function getDefaultFretPreferences() {
  return {
    'Root Position': {
      eString: [3, 5, 7],
      bString: [3, 5, 7],
      gString: [2, 4, 6],
      dString: [3, 5, 7],
      aString: [2, 4, 6],
      EString: [3, 5, 0]
    },
    'Basic Position': {
      eString: [3, 5, 7],
      bString: [3, 5, 7],
      gString: [2, 4, 6],
      dString: [3, 5, 7],
      aString: [2, 4, 6],
      EString: [3, 5, 0]
    },
    'First Inversion': {
      eString: [8, 10, 3],
      bString: [8, 10, 5],
      gString: [5, 7, 2],
      dString: [5, 7, 3],
      aString: [3, 5, 7],
      EString: [3, 5, 0]
    },
    'Second Inversion': {
      eString: [3, 5, 7],
      bString: [8, 10, 3],
      gString: [7, 9, 4],
      dString: [7, 9, 5],
      aString: [5, 7, 2],
      EString: [5, 7, 0]
    },
    'Third Inversion': {
      eString: [11, 10, 1],
      bString: [3, 5, 8],
      gString: [9, 11, 4],
      dString: [3, 5, 8],
      aString: [8, 10, 5],
      EString: [7, 9, 11]
    }
  };
}

// Add 8-string support to fret preferences
function add8StringSupport(preferences) {
  preferences['Root Position'].BbString = [3, 5, 7];
  preferences['Basic Position'].BbString = [3, 5, 7];
  preferences['First Inversion'].BbString = [3, 5, 7];
  preferences['Second Inversion'].BbString = [7, 9, 2];
  preferences['Third Inversion'].BbString = [7, 9, 11];
  return preferences;
}

// Get fret preferences for specific chord types
function getChordSpecificFretPreferences(position, chordType, defaultPreferences) {
  // For major chords, prefer more open positions in root position
  if (chordType === 'Major') {
    if (position === 'Root Position' || position === 'Basic Position') {
      return {
        ...defaultPreferences[position],
        eString: [0, 3, 7],  // Prefer open e string
        bString: [0, 3, 7],  // Prefer open b string
        EString: [0, 3, 7]   // Prefer open E string
      };
    }
  } 
  // For minor chords, prefer certain fret positions
  else if (chordType === 'Minor') {
    if (position === 'Root Position' || position === 'Basic Position') {
      return {
        ...defaultPreferences[position],
        gString: [3, 5, 7]   // Adjust g string preference
      };
    }
  } 
  // For seventh chords, adjust for comfortable fingering
  else if (chordType && chordType.includes('7')) {
    if (position === 'First Inversion') {
      return {
        ...defaultPreferences['First Inversion'],
        eString: [10, 8, 3]  // Strong preference for higher frets on e string
      };
    } else if (position === 'Second Inversion') {
      return {
        ...defaultPreferences['Second Inversion'],
        bString: [10, 8, 5]  // Strong preference for higher frets on b string
      };
    }
  }
  
  // Return default preferences for this position if no special adjustments
  return defaultPreferences[position] || defaultPreferences['Basic Position'];
}

// Score a fret position for optimal fingering
function scoreFretPosition(fretNum, stringName, position, preferences, chordType) {
  // Basic validity check
  if (fretNum === -1) return Infinity;
  
  // Get the preferences for this string or use defaults
  const stringPrefs = preferences[stringName] || [3, 5, 7];
  
  // Start with a high score (lower is better)
  let score = Infinity;
  
  // Calculate score based on preferences (lower is better)
  for (let i = 0; i < stringPrefs.length; i++) {
    const prefFret = stringPrefs[i];
    // Add a small penalty for lower preference order
    const prefScore = Math.abs(fretNum - prefFret) + (i * 0.1);
    
    if (prefScore < score) {
      score = prefScore;
    }
  }
  
  // Apply special bonuses or penalties based on chord type and position
  
  // For seventh chords, strongly prefer higher frets for certain strings
  if (chordType && chordType.includes('7')) {
    if (position === 'First Inversion' && stringName === 'eString') {
      score -= (fretNum >= 8) ? 2 : 0;
    } else if (position === 'Second Inversion' && stringName === 'bString') {
      score -= (fretNum >= 8) ? 2 : 0;
    }
  }
  
  // For Major chords in root position, prefer standard shapes
  if (chordType === 'Major' && (position === 'Root Position' || position === 'Basic Position')) {
    if (stringName === 'eString' || stringName === 'EString' || stringName === 'bString') {
      score -= (fretNum === 0) ? 1 : 0; // Prefer open strings for shape chords
    }
  }
  
  // For Minor chords, prefer certain fret positions
  if (chordType === 'Minor') {
    if ((position === 'Root Position' || position === 'Basic Position') && stringName === 'gString') {
      score -= (fretNum === 3) ? 1 : 0;
    }
  }
  
  // Penalize very high frets (12+) slightly 
  score += (fretNum > 12) ? 0.5 : 0;
  
  // Prefer more consistent fingering patterns (avoid extreme jumps between strings)
  if (fretNum > 7 && ['aString', 'EString'].includes(stringName)) {
    score += 0.5; // Penalize high frets on low strings
  }
  
  return score;
}

// Performance monitoring utility
class PerformanceMonitor {
  constructor(enabled = false) {
    this.enabled = enabled;
    this.measures = {};
  }
  
  start(operation) {
    if (!this.enabled) return;
    this.measures[operation] = performance.now();
  }
  
  end(operation) {
    if (!this.enabled || !this.measures[operation]) return 0;
    
    const duration = performance.now() - this.measures[operation];
    delete this.measures[operation];
    return duration;
  }
}

// Throttle a function to limit execution frequency
function throttle(func, wait) {
  let lastCall = 0;
  return function(...args) {
    const now = Date.now();
    if (now - lastCall >= wait) {
      lastCall = now;
      return func.apply(this, args);
    }
  };
}

// Debug logger with controlled output
function debugLog(enabled, message, level = 'debug') {
  if (!enabled && level === 'debug') return;
  
  const timestamp = new Date().toISOString().substring(11, 23);
  console[level](`[${timestamp}][ChordView] ${message}`);
}
