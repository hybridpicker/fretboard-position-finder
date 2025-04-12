/**
 * Comprehensive Test Suite for Fretboard Search Functionality
 * 
 * This test suite covers all three fretboard types:
 * - Scales
 * - Arpeggios
 * - Chords
 * 
 * It ensures that the search logic finds as much data as possible from the fixtures.
 */

// Global test state
const testState = {
  currentType: null, // 'scale', 'arpeggio', or 'chord'
  results: {
    scale: { passed: 0, failed: 0, tests: [] },
    arpeggio: { passed: 0, failed: 0, tests: [] },
    chord: { passed: 0, failed: 0, tests: [] }
  }
};

// =======================================================
// COMMON TEST FRAMEWORK
// =======================================================

/**
 * Run all tests for all fretboard types
 */
function runAllTests() {
  resetResults();
  
  // Run tests for each type
  runChordTests();
  runScaleTests();
  runArpeggioTests();
  
  // Show summary
  displayTestSummary();
}

/**
 * Reset all test results
 */
function resetResults() {
  // Clear the results table
  document.getElementById('test-results-table').querySelector('tbody').innerHTML = '';
  
  // Reset results tracking
  testState.results = {
    scale: { passed: 0, failed: 0, tests: [] },
    arpeggio: { passed: 0, failed: 0, tests: [] },
    chord: { passed: 0, failed: 0, tests: [] }
  };
  
  // Clear visual test container
  document.getElementById('visual-test-container').innerHTML = '';
  
  // Clear summary
  document.getElementById('test-summary').textContent = '';
}

/**
 * Add a test result to the results table
 */
function addResultToTable(result) {
  const table = document.getElementById('test-results-table');
  const row = document.createElement('tr');
  
  // Set row color based on test result
  row.className = result.passed ? 'pass-row' : 'fail-row';
  
  // Add data attributes for filtering
  row.setAttribute('data-type', result.type);
  
  // Add cells
  row.innerHTML = `
    <td>${result.id}</td>
    <td>${result.type}</td>
    <td>${result.root || '-'}</td>
    <td>${result.name || '-'}</td>
    <td>${result.position || '-'}</td>
    <td>${result.description}</td>
    <td>${result.notesFound}</td>
    <td>${result.passed ? 'PASS' : 'FAIL'}</td>
    <td>${result.details}</td>
    <td>
      <button onclick="runVisualTest('${result.type}', '${result.root || ''}', '${result.name || ''}', '${result.position || ''}')">
        View
      </button>
    </td>
  `;
  
  table.querySelector('tbody').appendChild(row);
}

/**
 * Display the overall test summary
 */
function displayTestSummary() {
  const summary = document.getElementById('test-summary');
  const total = {
    passed: testState.results.scale.passed + testState.results.arpeggio.passed + testState.results.chord.passed,
    failed: testState.results.scale.failed + testState.results.arpeggio.failed + testState.results.chord.failed
  };
  
  summary.innerHTML = `
    <div>Total: ${total.passed} passed, ${total.failed} failed</div>
    <div>Scales: ${testState.results.scale.passed} passed, ${testState.results.scale.failed} failed</div>
    <div>Arpeggios: ${testState.results.arpeggio.passed} passed, ${testState.results.arpeggio.failed} failed</div>
    <div>Chords: ${testState.results.chord.passed} passed, ${testState.results.chord.failed} failed</div>
  `;
}

/**
 * Filter the results table by type
 */
function filterResults(type) {
  const rows = document.querySelectorAll('#test-results-table tbody tr');
  
  if (type === 'all') {
    rows.forEach(row => row.style.display = '');
  } else {
    rows.forEach(row => {
      if (row.getAttribute('data-type') === type) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  }
}

/**
 * Run a visual test for any fretboard type
 */
function runVisualTest(type, root, name, position) {
  const container = document.getElementById('visual-test-container');
  container.innerHTML = '';
  
  const fretboard = getFretboardForType(type);
  if (!fretboard) {
    container.innerHTML = `<div class="alert alert-danger">Fretboard controller for ${type} not found!</div>`;
    return;
  }
  
  // Reset the fretboard
  fretboard.resetFretboard();
  
  try {
    // Set up with the specified parameters
    switch (type) {
      case 'scale':
        fretboard.setScale(root, name);
        fretboard.setPosition(position);
        break;
      case 'arpeggio':
        fretboard.setArpeggio(root, name);
        fretboard.setPosition(position);
        break;
      case 'chord':
        fretboard.setChord(root, name);
        fretboard.updateChordDisplay(position, 'e - g');
        break;
    }
    
    // Get found notes from active notes
    const foundNotes = [];
    fretboard.state.activeNotes.forEach((fret, string) => {
      foundNotes.push(`${string}: ${fret}`);
    });
    
    // Build visual test report
    const report = `
      <div class="card-header">
        <h3>Visual Test: ${type.charAt(0).toUpperCase() + type.slice(1)}</h3>
      </div>
      <div class="card-body">
        <p><strong>Root:</strong> ${root || 'N/A'}</p>
        <p><strong>Name:</strong> ${name || 'N/A'}</p>
        <p><strong>Position:</strong> ${position || 'N/A'}</p>
        <p><strong>Found ${foundNotes.length} notes:</strong></p>
        <ul class="note-list">
          ${foundNotes.length > 0 
            ? foundNotes.map(note => `<li>${note}</li>`).join('') 
            : '<li>No notes found</li>'}
        </ul>
      </div>
    `;
    
    container.innerHTML = report;
    
  } catch (error) {
    container.innerHTML = `
      <div class="card-header">
        <h3>Test Error</h3>
      </div>
      <div class="card-body">
        <div class="alert alert-danger">${error.message}</div>
      </div>
    `;
  }
}

/**
 * Get the appropriate fretboard controller for a given type
 */
function getFretboardForType(type) {
  switch (type) {
    case 'scale': return window.scaleFretboard;
    case 'arpeggio': return window.arpeggioFretboard;
    case 'chord': return window.chordFretboard;
    default: return null;
  }
}

// =======================================================
// CHORD TESTS
// =======================================================

/**
 * Run all tests for chord search functionality
 */
function runChordTests() {
  console.log('=== STARTING CHORD SEARCH TESTS ===');
  testState.currentType = 'chord';
  
  // Test configuration
  const testCases = [
    // Test all root notes with a common chord type
    ...generateChordRootTests('Major'),
    ...generateChordRootTests('Minor'),
    ...generateChordRootTests('Dominant 7'),
    
    // Test all chord types with a common root
    ...generateChordTypeTests('C'),
    ...generateChordTypeTests('G'),
    ...generateChordTypeTests('E'),
    
    // Test all positions for specific chord
    ...generateChordPositionTests('C', 'Major'),
    ...generateChordPositionTests('G', 'Dominant 7'),
    ...generateChordPositionTests('A', 'Minor'),
    
    // Test edge cases
    { root: 'C#', type: 'Augmented', position: 'Basic Position',
      description: 'Enharmonic root with complex chord type' },
    { root: 'Gb', type: 'Diminished 7', position: 'Basic Position', 
      description: 'Flat root with complex chord type' },
    { root: 'B', type: 'Minor 7b5', position: 'Third Inversion', 
      description: 'Edge position' },
    
    // Test alternative name formats
    { root: 'C', type: 'min', position: 'Basic Position', 
      description: 'Alternative chord type notation "min"' },
    { root: 'D', type: 'M7', position: 'First Inversion', 
      description: 'Alternative chord type notation "M7"' },
    { root: 'A', type: 'dom7', position: 'Basic Position', 
      description: 'Alternative chord type notation "dom7"' }
  ];
  
  // Run all chord tests
  runTestCases(testCases, 'chord');
  
  console.log(`=== CHORD TEST SUMMARY: ${testState.results.chord.passed} passed, ${testState.results.chord.failed} failed ===`);
}

/**
 * Generate tests for all root notes with a specific chord type
 */
function generateChordRootTests(type) {
  const roots = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'];
  return roots.map(root => ({
    root,
    type,
    position: 'Basic Position',
    description: `${root} ${type} in basic position`
  }));
}

/**
 * Generate tests for all chord types with a specific root
 */
function generateChordTypeTests(root) {
  const types = [
    'Major', 'Minor', 'Dominant 7', 'Major 7', 'Minor 7', 
    'Diminished', 'Augmented', 'Minor 7b5', 'Diminished 7'
  ];
  
  return types.map(type => ({
    root,
    type,
    position: 'Basic Position',
    description: `${root} ${type} chord test`
  }));
}

/**
 * Generate tests for all positions of a specific chord
 */
function generateChordPositionTests(root, type) {
  const positions = [
    'Basic Position', 'First Inversion', 'Second Inversion', 
    'Third Inversion', 'Drop 2', 'Drop 3'
  ];
  
  return positions.map(position => ({
    root,
    type,
    position,
    description: `${root} ${type} in ${position} position`
  }));
}

/**
 * Run a set of chord test cases
 */
function runTestCases(testCases, type) {
  const fretboard = getFretboardForType(type);
  
  if (!fretboard) {
    console.error(`Fretboard controller for ${type} not found!`);
    return;
  }
  
  testCases.forEach((test, index) => {
    const testId = `${type}-${index + 1}`;
    console.log(`Running ${type} test #${index + 1}: ${test.description || 'Unnamed test'}`);
    
    try {
      // Reset fretboard state
      fretboard.resetFretboard();
      
      // Set up the test parameters
      switch (type) {
        case 'chord':
          fretboard.setChord(test.root, test.type);
          fretboard.updateChordDisplay(test.position, 'e - g');
          break;
        case 'scale':
          fretboard.setScale(test.root, test.name);
          fretboard.setPosition(test.position || '0');
          break;
        case 'arpeggio':
          fretboard.setArpeggio(test.root, test.type);
          fretboard.setPosition(test.position || '0');
          break;
      }
      
      // Check if any notes were found
      const notesCount = fretboard.state.activeNotes.size;
      const notesFound = notesCount > 0;
      const result = notesFound ? 'PASS' : 'FAIL';
      
      // Add to test results
      addResultToTable({
        id: testId,
        type: type,
        root: test.root,
        name: test.type || test.name,
        position: test.position,
        description: test.description || '',
        notesFound: notesCount,
        passed: notesFound,
        details: notesFound ? 
          `Found ${notesCount} notes` : 
          `No notes found for this combination`
      });
      
      console.log(`Test result: ${result} - Found ${notesCount} notes`);
      
      // Update stats
      if (notesFound) {
        testState.results[type].passed++;
        testState.results[type].tests.push({ ...test, result: 'pass' });
        console.log(`✓ Successfully found ${type} data`);
      } else {
        testState.results[type].failed++;
        testState.results[type].tests.push({ ...test, result: 'fail' });
        console.log(`✗ Failed to find ${type} data`);
      }
      
    } catch (error) {
      console.error(`Error during test: ${error.message}`);
      testState.results[type].failed++;
      
      // Add error to results table
      addResultToTable({
        id: testId,
        type: type,
        root: test.root,
        name: test.type || test.name,
        position: test.position,
        description: test.description || '',
        notesFound: 0,
        passed: false,
        details: `ERROR: ${error.message}`
      });
    }
    
    console.log('----------------------------');
  });
}

// =======================================================
// SCALE TESTS
// =======================================================

/**
 * Run all tests for scale search functionality
 */
function runScaleTests() {
  console.log('=== STARTING SCALE SEARCH TESTS ===');
  testState.currentType = 'scale';
  
  // Test configuration
  const testCases = [
    // Test all root notes with common scale types
    ...generateScaleRootTests('Major'),
    ...generateScaleRootTests('Minor'),
    ...generateScaleRootTests('Pentatonic'),
    ...generateScaleRootTests('Blues Scale'),
    
    // Test all scale types with common roots
    ...generateScaleTypeTests('C'),
    ...generateScaleTypeTests('G'),
    ...generateScaleTypeTests('E'),
    
    // Test all positions
    ...generateScalePositionTests('C', 'Major'),
    ...generateScalePositionTests('A', 'Minor'),
    ...generateScalePositionTests('E', 'Pentatonic'),
    
    // Test edge cases
    { root: 'F#', name: 'Dorian', position: '3',
      description: 'F# Dorian mode' },
    { root: 'Bb', name: 'Lydian', position: '2',
      description: 'Flat root with Lydian mode' },
    { root: 'G#', name: 'Whole Tone', position: '0',
      description: 'Sharp root with whole tone scale' }
  ];
  
  // Run all scale tests
  runTestCases(testCases, 'scale');
  
  console.log(`=== SCALE TEST SUMMARY: ${testState.results.scale.passed} passed, ${testState.results.scale.failed} failed ===`);
}

/**
 * Generate tests for all root notes with a specific scale type
 */
function generateScaleRootTests(name) {
  const roots = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'];
  return roots.map(root => ({
    root,
    name,
    position: '0',
    description: `${root} ${name} scale position 0`
  }));
}

/**
 * Generate tests for all scale types with a specific root
 */
function generateScaleTypeTests(root) {
  const scaleTypes = [
    'Major', 'Minor', 'Pentatonic', 'Blues Scale', 'Dorian',
    'Phrygian', 'Lydian', 'Mixolydian', 'Aeloian', 'Locrian',
    'Harmonic Minor', 'Melodic Minor', 'Whole Tone', 'Diminished'
  ];
  
  return scaleTypes.map(name => ({
    root,
    name,
    position: '0',
    description: `${root} ${name} scale test`
  }));
}

/**
 * Generate tests for all positions of a specific scale
 */
function generateScalePositionTests(root, name) {
  // Test positions 0-5 for scales
  const positions = ['0', '1', '2', '3', '4', '5'];
  
  return positions.map(position => ({
    root,
    name,
    position,
    description: `${root} ${name} in position ${position}`
  }));
}

// =======================================================
// ARPEGGIO TESTS
// =======================================================

/**
 * Run all tests for arpeggio search functionality
 */
function runArpeggioTests() {
  console.log('=== STARTING ARPEGGIO SEARCH TESTS ===');
  testState.currentType = 'arpeggio';
  
  // Test configuration
  const testCases = [
    // Test all root notes with common arpeggio types
    ...generateArpeggioRootTests('Major Triad'),
    ...generateArpeggioRootTests('Minor Triad'),
    ...generateArpeggioRootTests('Major 7'),
    
    // Test all arpeggio types with common roots
    ...generateArpeggioTypeTests('C'),
    ...generateArpeggioTypeTests('G'),
    ...generateArpeggioTypeTests('E'),
    
    // Test all positions
    ...generateArpeggioPositionTests('C', 'Major Triad'),
    ...generateArpeggioPositionTests('A', 'Minor Triad'),
    ...generateArpeggioPositionTests('E', 'Dominant 7'),
    
    // Test edge cases
    { root: 'F#', type: 'Diminished 7', position: '3',
      description: 'F# Diminished 7 arpeggio' },
    { root: 'Bb', type: 'Augmented Triad', position: '2',
      description: 'Flat root with Augmented Triad' },
    { root: 'G#', type: 'Minor 7b5', position: '0',
      description: 'Sharp root with Minor 7b5 arpeggio' }
  ];
  
  // Run all arpeggio tests
  runTestCases(testCases, 'arpeggio');
  
  console.log(`=== ARPEGGIO TEST SUMMARY: ${testState.results.arpeggio.passed} passed, ${testState.results.arpeggio.failed} failed ===`);
}

/**
 * Generate tests for all root notes with a specific arpeggio type
 */
function generateArpeggioRootTests(type) {
  const roots = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'];
  return roots.map(root => ({
    root,
    type,
    position: '0',
    description: `${root} ${type} arpeggio position 0`
  }));
}

/**
 * Generate tests for all arpeggio types with a specific root
 */
function generateArpeggioTypeTests(root) {
  const arpeggioTypes = [
    'Major Triad', 'Minor Triad', 'Diminished Triad', 'Augmented Triad',
    'Major 7', 'Minor 7', 'Dominant 7', 'Minor 7b5', 'Diminished 7',
    'Major add 9'
  ];
  
  return arpeggioTypes.map(type => ({
    root,
    type,
    position: '0',
    description: `${root} ${type} arpeggio test`
  }));
}

/**
 * Generate tests for all positions of a specific arpeggio
 */
function generateArpeggioPositionTests(root, type) {
  // Test positions 0-5 for arpeggios
  const positions = ['0', '1', '2', '3', '4', '5'];
  
  return positions.map(position => ({
    root,
    type,
    position,
    description: `${root} ${type} in position ${position}`
  }));
}

/**
 * Run a custom test with user-specified parameters
 */
function runCustomTest() {
  const type = document.getElementById('custom-type-select').value;
  const root = document.getElementById('custom-root').value;
  const name = document.getElementById('custom-name').value;
  const position = document.getElementById('custom-position').value;
  
  if (!type || !root || !name) {
    alert('Please fill in the type, root note, and name/type fields');
    return;
  }
  
  // Run the visual test with the specified parameters
  runVisualTest(type, root, name, position);
}
