/**
 * Test suite for chord search functionality
 * This ensures all possible data combinations are found correctly
 */
function testChordSearchLogic() {
  console.log('=== STARTING CHORD SEARCH TESTS ===');
  
  // Test configuration
  const testCases = [
    // Test all root notes with a common chord type
    ...generateRootTests('Major'),
    ...generateRootTests('Minor'),
    ...generateRootTests('Dominant 7'),
    
    // Test all chord types with a common root
    ...generateChordTypeTests('C'),
    ...generateChordTypeTests('G'),
    ...generateChordTypeTests('E'),
    
    // Test all positions for specific chord
    ...generatePositionTests('C', 'Major'),
    ...generatePositionTests('G', 'Dominant 7'),
    ...generatePositionTests('A', 'Minor'),
    
    // Test all string ranges
    ...generateRangeTests('C', 'Major', 'Basic Position'),
    ...generateRangeTests('G', 'Dominant 7', 'Second Inversion'),
    
    // Test edge cases
    { root: 'C#', type: 'Augmented', position: 'Basic Position', range: 'e - g', 
      description: 'Enharmonic root with complex chord type' },
    { root: 'Gb', type: 'Diminished 7', position: 'Basic Position', range: 'a - e', 
      description: 'Flat root with complex chord type' },
    { root: 'B', type: 'Minor 7b5', position: 'Third Inversion', range: 'd - e', 
      description: 'Edge position and range' },
    
    // Test alternative name formats (based on normalizations in your code)
    { root: 'C', type: 'min', position: 'Basic Position', range: 'e - g', 
      description: 'Alternative chord type notation "min"' },
    { root: 'D', type: 'M7', position: 'First Inversion', range: 'e - g', 
      description: 'Alternative chord type notation "M7"' },
    { root: 'A', type: 'dom7', position: 'Basic Position', range: 'e - g', 
      description: 'Alternative chord type notation "dom7"' }
  ];
  
  // Run all tests
  let passCount = 0, failCount = 0;
  const fretboard = window.chordFretboard; // Reference to your controller
  
  testCases.forEach((test, index) => {
    console.log(`Running test #${index + 1}: ${test.description || 'Unnamed test'}`);
    console.log(`Parameters: root=${test.root}, type=${test.type}, position=${test.position}, range=${test.range}`);
    
    try {
      // Reset fretboard state
      fretboard.resetFretboard();
      
      // Set up the test chord
      fretboard.setChord(test.root, test.type);
      
      // Store current active note count
      const beforeCount = fretboard.state.activeNotes.size;
      
      // Run the search logic with the given parameters
      fretboard.getTonesFromDataChords(test.range, test.position);
      
      // Check if any notes were found
      const afterCount = fretboard.state.activeNotes.size;
      const notesFound = afterCount > 0;
      const result = notesFound ? 'PASS' : 'FAIL';
      
      // Add to the test results table
      addResultToTable({
        id: index + 1,
        root: test.root,
        type: test.type,
        position: test.position,
        range: test.range,
        description: test.description || '',
        notesFound: afterCount,
        passed: notesFound,
        details: notesFound ? 
          `Found ${afterCount} notes` : 
          `No notes found for this combination`
      });
      
      console.log(`Test result: ${result} - Found ${afterCount} notes`);
      
      if (notesFound) {
        passCount++;
        console.log(`✓ Successfully found chord data`);
      } else {
        failCount++;
        console.log(`✗ Failed to find chord data`);
      }
      
    } catch (error) {
      console.error(`Error during test: ${error.message}`);
      failCount++;
      
      // Add error to results table
      addResultToTable({
        id: index + 1,
        root: test.root,
        type: test.type,
        position: test.position,
        range: test.range,
        description: test.description || '',
        notesFound: 0,
        passed: false,
        details: `ERROR: ${error.message}`
      });
    }
    
    console.log('----------------------------');
  });
  
  // Update summary
  document.getElementById('test-summary').textContent = 
    `TESTS COMPLETED: ${passCount} passed, ${failCount} failed`;
  
  console.log(`=== TEST SUMMARY: ${passCount} passed, ${failCount} failed ===`);
  return { passed: passCount, failed: failCount };
}

/**
 * Generate tests for all root notes with a specific chord type
 */
function generateRootTests(chordType) {
  const roots = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'];
  return roots.map(root => ({
    root,
    type: chordType,
    position: 'Basic Position',
    range: 'e - g',
    description: `${root} ${chordType} in basic position`
  }));
}

/**
 * Generate tests for all chord types with a specific root
 */
function generateChordTypeTests(root) {
  const chordTypes = [
    'Major', 'Minor', 'Dominant 7', 'Major 7', 'Minor 7', 
    'Diminished', 'Augmented', 'Minor 7b5', 'Diminished 7'
  ];
  
  return chordTypes.map(type => ({
    root,
    type,
    position: 'Basic Position',
    range: 'e - g',
    description: `${root} ${type} chord test`
  }));
}

/**
 * Generate tests for all positions of a specific chord
 */
function generatePositionTests(root, type) {
  const positions = [
    'Basic Position', 'First Inversion', 'Second Inversion', 
    'Third Inversion', 'Drop 2', 'Drop 3'
  ];
  
  return positions.map(position => ({
    root,
    type,
    position,
    range: 'e - g',
    description: `${root} ${type} in ${position} position`
  }));
}

/**
 * Generate tests for all string ranges with a specific chord and position
 */
function generateRangeTests(root, type, position) {
  const ranges = ['e - g', 'd - e', 'a - e', 'e - D', 'A - D'];
  
  return ranges.map(range => ({
    root,
    type,
    position,
    range,
    description: `${root} ${type} in ${position} with range ${range}`
  }));
}

/**
 * Add a test result to the results table
 */
function addResultToTable(result) {
  const table = document.getElementById('test-results-table');
  const row = document.createElement('tr');
  
  // Set row color based on test result
  row.className = result.passed ? 'pass-row' : 'fail-row';
  
  // Add cells
  row.innerHTML = `
    <td>${result.id}</td>
    <td>${result.root}</td>
    <td>${result.type}</td>
    <td>${result.position}</td>
    <td>${result.range}</td>
    <td>${result.description}</td>
    <td>${result.notesFound}</td>
    <td>${result.passed ? 'PASS' : 'FAIL'}</td>
    <td>${result.details}</td>
    <td>
      <button onclick="visualTestMode('${result.root}', '${result.type}', '${result.position}', '${result.range}')">
        View
      </button>
    </td>
  `;
  
  table.querySelector('tbody').appendChild(row);
}

/**
 * Run a visual test of a specific chord combination
 */
function visualTestMode(root, type, position, range) {
  // Clear previous visual test
  document.getElementById('visual-test-container').innerHTML = '';
  
  const fretboard = window.chordFretboard;
  
  // Reset fretboard state
  fretboard.resetFretboard();
  
  // Set up chord
  fretboard.setChord(root, type);
  
  // Run search
  fretboard.getTonesFromDataChords(range, position);
  
  // Get found notes
  const foundNotes = [];
  fretboard.state.activeNotes.forEach(note => {
    foundNotes.push(`${note.string}: ${note.name} (${note.function || 'unknown'})`);
  });
  
  // Build visual test report
  const report = `
    <h3>Visual Test: ${root} ${type}</h3>
    <p><strong>Position:</strong> ${position}</p>
    <p><strong>Range:</strong> ${range}</p>
    <p><strong>Found ${foundNotes.length} notes:</strong></p>
    <ul class="note-list">
      ${foundNotes.map(note => `<li>${note}</li>`).join('')}
    </ul>
  `;
  
  document.getElementById('visual-test-container').innerHTML = report;
  
  // Highlight this combination in the results table
  const rows = document.querySelectorAll('#test-results-table tbody tr');
  rows.forEach(row => row.classList.remove('selected-test'));
  
  // Find matching row and highlight it
  for (const row of rows) {
    const cells = row.querySelectorAll('td');
    if (cells[1].textContent === root && 
        cells[2].textContent === type && 
        cells[3].textContent === position && 
        cells[4].textContent === range) {
      row.classList.add('selected-test');
      // Scroll to the selected row
      row.scrollIntoView({ behavior: 'smooth', block: 'center' });
      break;
    }
  }
}

/**
 * Run a single test with the provided parameters
 */
function runSingleTest() {
  const root = document.getElementById('custom-root').value;
  const type = document.getElementById('custom-type').value;
  const position = document.getElementById('custom-position').value;
  const range = document.getElementById('custom-range').value;
  
  if (!root || !type || !position || !range) {
    alert('Please fill in all fields');
    return;
  }
  
  visualTestMode(root, type, position, range);
}

/**
 * Clear all test results
 */
function clearResults() {
  document.getElementById('test-results-table').querySelector('tbody').innerHTML = '';
  document.getElementById('test-summary').textContent = '';
  document.getElementById('visual-test-container').innerHTML = '';
}
