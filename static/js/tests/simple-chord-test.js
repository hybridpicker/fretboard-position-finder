/**
 * Simple test script for chord search logic
 * This directly tests the getTonesFromDataChords method without requiring full initialization
 */

// Simple test data structure that mimics the format from the fixtures
const TEST_CHORD_DATA = {
  // C Major chord in basic position
  'e - g': {
    'Basic Position': {
      'eString': ['e', '3'],
      'bString': ['c', '1'],
      'gString': ['g', '5'],
      'dString': ['e', '3'],
      'aString': ['c', '1'],
      'EString': ['g', '5'],
      'assigned_strings': ['eString', 'bString', 'gString', 'dString', 'aString', 'EString']
    },
    'First Inversion': {
      'eString': ['e', '3'],
      'bString': ['c', '1'],
      'gString': ['g', '5'],
      'dString': ['c', '1'],
      'aString': ['e', '3'],
      'EString': ['c', '1'],
      'assigned_strings': ['eString', 'bString', 'gString', 'dString', 'aString', 'EString']
    }
  },
  // Metadata
  'chord': 'C Major',
  'root': 'C',
  'type': 'Major'
};

// G7 chord data
const G7_CHORD_DATA = {
  'e - g': {
    'Basic Position': {
      'eString': ['g', 'R'],
      'bString': ['f', 'b7'],
      'gString': ['d', '5'],
      'dString': ['g', 'R'],
      'aString': ['b', '3'],
      'EString': ['g', 'R'],
      'assigned_strings': ['eString', 'bString', 'gString', 'dString', 'aString', 'EString']
    }
  },
  'chord': 'G Dominant 7',
  'root': 'G',
  'type': 'Dominant 7'
};

// A minor chord data
const Am_CHORD_DATA = {
  'e - g': {
    'Basic Position': {
      'eString': ['e', '5'],
      'bString': ['c', '3'],
      'gString': ['a', 'R'],
      'dString': ['e', '5'],
      'aString': ['a', 'R'],
      'EString': ['a', 'R'],
      'assigned_strings': ['eString', 'bString', 'gString', 'dString', 'aString', 'EString']
    }
  },
  'chord': 'A Minor',
  'root': 'A',
  'type': 'Minor'
};

/**
 * Simple mock of the controller to test just the search functionality
 */
class MockChordController {
  constructor() {
    this.chordState = {
      voicingData: null,
      rootNote: null,
      chordType: null
    };
    
    this.state = {
      activeNotes: new Map(),
      activeFrets: new Map()
    };
    
    this.performance = {
      start: () => {},
      end: () => {}
    };
    
    // Mock DOM elements we'll use to track "activated" notes
    this.domElements = {};
  }
  
  resetFretboard() {
    this.state.activeNotes.clear();
    this.state.activeFrets.clear();
  }
  
  setChord(root, type) {
    this.chordState.rootNote = root;
    this.chordState.chordType = type;
    
    // Set appropriate test data based on the chord
    if (root === 'C' && type === 'Major') {
      this.chordState.voicingData = TEST_CHORD_DATA;
    } else if (root === 'G' && type === 'Dominant 7') {
      this.chordState.voicingData = G7_CHORD_DATA;
    } else if (root === 'A' && type === 'Minor') {
      this.chordState.voicingData = Am_CHORD_DATA;
    } else {
      // For testing purposes, default to C Major if the chord isn't recognized
      this.chordState.voicingData = TEST_CHORD_DATA;
    }
    
    console.log(`Set chord to ${root} ${type}`);
    return this;
  }
  
  /**
   * This is a simplified version of the getTonesFromDataChords method
   * that focuses only on the core search logic
   */
  getTonesFromDataChords(range, position) {
    console.log('Running getTonesFromDataChords with params:', { range, position });
    
    // If no chord data, exit early
    if (!this.chordState.voicingData) {
      console.warn('No chord voicing data available');
      return this;
    }
    
    // IMPORTANT: Clear active notes to prevent accumulation
    this.state.activeNotes.clear();
    
    // SIMPLIFIED DATA HANDLING
    let positionData = null;
    
    // Check for flat structure first (with assigned_strings)
    const hasAssignedStrings = this.chordState.voicingData.hasOwnProperty('assigned_strings');
    const hasStringData = hasAssignedStrings && 
                          this.chordState.voicingData.assigned_strings && 
                          this.chordState.voicingData.assigned_strings.length > 0;
    
    if (hasStringData) {
      // Flat structure (like in some examples)
      positionData = this.chordState.voicingData;
      console.log('Using flat structure for position data');
    }
    // Try the range-position nested structure
    else if (this.chordState.voicingData[range] && this.chordState.voicingData[range][position]) {
      positionData = this.chordState.voicingData[range][position];
      console.log(`Found position data using direct access: range=${range}, position=${position}`);
    } 
    // If position not found in the given range, try other positions for this range
    else if (this.chordState.voicingData[range]) {
      console.log(`Position "${position}" not found in range "${range}", checking alternatives`);
      const availablePositions = Object.keys(this.chordState.voicingData[range]);
      console.log(`Available positions for range "${range}":`, availablePositions);
      
      if (availablePositions.length > 0) {
        // Default to first available position if specified position not found
        const fallbackPosition = availablePositions[0];
        positionData = this.chordState.voicingData[range][fallbackPosition];
        console.log(`Using fallback position "${fallbackPosition}" for range "${range}"`);
      }
    }
    // If not found, loop through all keys that aren't metadata fields
    else {
      console.log('Direct access failed, searching through potential ranges');
      const potentialRanges = Object.keys(this.chordState.voicingData).filter(key => 
        key !== 'chord' && key !== 'type' && key !== 'root' && key !== 'note_range');
      
      console.log('Potential ranges to search:', potentialRanges);
      
      for (const potentialRange of potentialRanges) {
        if (this.chordState.voicingData[potentialRange] && 
            typeof this.chordState.voicingData[potentialRange] === 'object') {
          console.log(`Checking range "${potentialRange}" for position "${position}"`);
          
          // Try exact position match first
          if (this.chordState.voicingData[potentialRange][position]) {
            positionData = this.chordState.voicingData[potentialRange][position];
            console.log(`Found position data for "${position}" in range "${potentialRange}"`);
            break;
          }
          
          // If position not found, try any available position in this range
          const availablePositions = Object.keys(this.chordState.voicingData[potentialRange]);
          if (availablePositions.length > 0) {
            positionData = this.chordState.voicingData[potentialRange][availablePositions[0]];
            console.log(`Using fallback position "${availablePositions[0]}" in range "${potentialRange}"`);
            break;
          }
        }
      }
    }
    
    if (!positionData) {
      console.warn(`No position data found for range: ${range}, position: ${position}`);
      return this;
    }
    
    console.log('Position data found:', positionData);
    
    // Activate notes for each string in the position data
    for (const stringName in positionData) {
      // Skip the assigned_strings array
      if (stringName === 'assigned_strings') {
        continue;
      }
      
      console.log(`Processing string: ${stringName}`);
      
      // Get the note data for this string
      const noteData = positionData[stringName];
      if (!noteData || !noteData.length) {
        console.log(`No note data for string ${stringName}`);
        continue;
      }
      
      // Get the note name and function (e.g., "c", "R" for root)
      const noteName = noteData[0];
      const noteFunction = noteData[1] || '';
      
      console.log(`String ${stringName}: note=${noteName}, function=${noteFunction}`);
      
      if (!noteName) {
        console.log(`No note name for string ${stringName}, skipping`);
        continue;
      }
      
      // For our mock, we just store the active notes
      if (!this.state.activeNotes.has(stringName)) {
        this.state.activeNotes.set(stringName, new Set());
      }
      this.state.activeNotes.get(stringName).add(noteName);
      
      console.log(`Added note ${noteName} on string ${stringName}`);
    }
    
    console.log('==== getTonesFromDataChords COMPLETE ====');
    console.log('Active notes:', this.state.activeNotes);
    
    return this;
  }
  
  /**
   * Get the size of the active notes map (total number of notes)
   */
  getActiveNotesCount() {
    let count = 0;
    this.state.activeNotes.forEach(noteSet => {
      count += noteSet.size;
    });
    return count;
  }
}

/**
 * Run tests for the chord search functionality
 */
function runChordSearchTests() {
  console.log('=== STARTING SIMPLIFIED CHORD SEARCH TESTS ===');
  
  // Create a mock controller
  const controller = new MockChordController();
  
  // Test cases
  const testCases = [
    { root: 'C', type: 'Major', position: 'Basic Position', range: 'e - g', 
      expectedNotes: 6, description: 'C Major in basic position' },
    { root: 'C', type: 'Major', position: 'First Inversion', range: 'e - g', 
      expectedNotes: 6, description: 'C Major in first inversion' },
    { root: 'G', type: 'Dominant 7', position: 'Basic Position', range: 'e - g', 
      expectedNotes: 6, description: 'G7 chord' },
    { root: 'A', type: 'Minor', position: 'Basic Position', range: 'e - g', 
      expectedNotes: 6, description: 'A minor chord' },
    // Test fallback position search
    { root: 'C', type: 'Major', position: 'Non-existent Position', range: 'e - g', 
      expectedNotes: 6, description: 'Test fallback to basic position' },
    // Test fallback range search
    { root: 'C', type: 'Major', position: 'Basic Position', range: 'non-existent-range', 
      expectedNotes: 6, description: 'Test fallback to available range' }
  ];
  
  // Run the tests
  let passCount = 0, failCount = 0;
  const results = [];
  
  testCases.forEach((test, index) => {
    console.log(`Running test #${index + 1}: ${test.description}`);
    
    // Reset the controller
    controller.resetFretboard();
    
    // Set up the test chord
    controller.setChord(test.root, test.type);
    
    // Run the search logic
    controller.getTonesFromDataChords(test.range, test.position);
    
    // Check the results
    const notesFound = controller.getActiveNotesCount();
    const passed = notesFound === test.expectedNotes;
    
    // Store the result
    results.push({
      ...test,
      notesFound,
      passed,
      details: passed ? 
        `Found expected ${notesFound} notes` : 
        `Expected ${test.expectedNotes} notes, found ${notesFound}`
    });
    
    // Count passes and failures
    if (passed) {
      passCount++;
      console.log(`✓ Test passed - Found ${notesFound} notes`);
    } else {
      failCount++;
      console.log(`✗ Test failed - Expected ${test.expectedNotes} notes, found ${notesFound}`);
    }
    
    console.log('----------------------------');
  });
  
  // Display the summary
  console.log(`=== TEST SUMMARY: ${passCount} passed, ${failCount} failed ===`);
  
  // Add to the test results table if it exists
  const table = document.getElementById('test-results-table');
  if (table) {
    results.forEach((result, index) => {
      const row = document.createElement('tr');
      
      // Set row color based on test result
      row.className = result.passed ? 'pass-row' : 'fail-row';
      
      // Add cells
      row.innerHTML = `
        <td>${index + 1}</td>
        <td>chord</td>
        <td>${result.root}</td>
        <td>${result.type}</td>
        <td>${result.position}</td>
        <td>${result.description}</td>
        <td>${result.notesFound}</td>
        <td>${result.passed ? 'PASS' : 'FAIL'}</td>
        <td>${result.details}</td>
        <td>-</td>
      `;
      
      table.querySelector('tbody').appendChild(row);
    });
    
    // Update summary
    const summary = document.getElementById('test-summary');
    if (summary) {
      summary.textContent = `CHORD TESTS: ${passCount} passed, ${failCount} failed`;
    }
  }
  
  return { passed: passCount, failed: failCount, results };
}

// Run the tests if in a browser environment
if (typeof window !== 'undefined') {
  document.addEventListener('DOMContentLoaded', function() {
    // If test button exists, hook up to it
    const testButton = document.getElementById('run-chord-tests');
    if (testButton) {
      testButton.addEventListener('click', runChordSearchTests);
    } else {
      // Otherwise run automatically
      console.log('Running tests automatically...');
      runChordSearchTests();
    }
  });
}
