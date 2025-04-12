# Eight-String Branch Integration

This branch integrates the eight-string functionality from the `eight-String` branch into the `devel` branch while preserving the note name functionality and other improvements from `devel`.

## Changes Made

1. **String Configuration**
   - Added support for both 6-string and 8-string modes via a toggle
   - Added `highAString` and `lowBString` to the string array
   - Added note definitions for the new strings in the `NOTES` object

2. **UI/UX**
   - Added a button to switch between 6-string and 8-string modes
   - Created different CSS for different string configurations
   - Added appropriate SVG fretboard diagrams for 8-string display

3. **Backend**
   - Updated view helpers to supply correct string data to templates
   - Added `get_string_config` function to handle string configuration requests
   - Modified scale, arpeggio, and chord views to handle 8-string mode

4. **JavaScript**
   - Added height synchronization for the lowest string
   - Added duplicate cursor cleanup to fix UI issues
   - Enhanced note name display to work with 8-string layout

## How to Use

1. Normal 6-string mode is the default
2. Click the "Switch to 8-string mode" button to toggle to 8-string mode
3. The fretboard will update to show the high A and low B strings
4. 'n' shortcut for note names works in both modes

## Technical Details

The implementation uses CSS classes to conditionally show/hide strings and apply the correct fretboard SVG background based on the selected mode. The backend passes the appropriate string names array to the template based on the user's preference.

String heights are synchronized using the `syncLowestStringHeight` function to ensure proper styling regardless of the mode.

## How to Extend

1. For new chord voicings specifically for 8-string, add them to the database with appropriate ranges
2. For different tunings, modify the `NOTES` object in base.js to reflect the new tuning
