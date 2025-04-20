# Ted Greene's V-System API

This API extension provides powerful chord voicing generation for 6, 7, and 8-string guitars based on Ted Greene's V-System.

## Features

- Complete support for all V-System voicing groups (V-1 through V-14)
- Compatible with 6, 7, and 8-string guitars
- Multiple string set combinations for each instrument
- Advanced playability scoring and filtering
- Interval structure tagging
- Low register "muddiness" detection
- Performance optimized with caching

## API Endpoints

### Chord Voicings
`GET /api/chord-voicings/`

Generate chord voicings with the following query parameters:
- `chord`: Chord name (e.g., G7, Cmaj7)
- `voicing_group`: V-System pattern (e.g., V-2)
- `instrument`: Instrument type (6-string, 7-string, 8-string)
- `string_set`: String set to use (e.g., 6-3, 8-5)

Example response:
```json
{
  "voicing_group": "V-2",
  "instrument": "8-string",
  "string_set": "6-3",
  "chord": "G7",
  "voicings": [
    {
      "frets": [3, 5, 3, 5, -1, -1, -1, -1],
      "intervals": ["Root", "7", "3", "5"],
      "score": 0.91,
      "playable": true
    },
    ...
  ]
}
```

### Other Endpoints

- `GET /api/tuning-options/` - List available tunings and string sets
- `GET /api/voicing-groups/` - List V-System voicing patterns
- `GET /api/chord-types/` - List available chord types and their intervals

## V-System API Tester

A visual testing interface is available at `/api/tester/`. This provides:
- Interactive controls for all API parameters
- Visual fretboard diagrams for generated voicings
- Raw API response display

## Implementation Notes

- Maximum fret span is constrained to 5 frets for playability
- V-13 and V-14 patterns are automatically skipped if fret span > 7
- Low register voicings are flagged as potentially muddy
- Results are cached for performance (15 minute default)

## Usage Example

```javascript
fetch('/api/chord-voicings/?chord=G7&voicing_group=V-2&instrument=8-string&string_set=6-3')
  .then(response => response.json())
  .then(data => {
    console.log(data);
    // Process the voicings
  });
```
