# Implementing Ted Greene's V-System in Fretboard Position Finder

This guide provides step-by-step instructions for implementing and using the V-System in the Fretboard Position Finder application.

## Setup Instructions

### 1. Activate Your Virtual Environment

First, ensure your Django virtual environment is activated:

```
source venv/bin/activate
```

### 2. Fix Any Missing Dependencies

If you encounter module import errors, make sure all dependencies are installed:

```
pip install -r requirements.txt
```

### 3. Generate V-System Voicings

Generate the V-System chord voicings using the management command. Important: Due to database constraints, we can only use 6-string ranges (not 8-string ranges):

```
# Generate all V1 (close position) voicings with a 6-string range
python manage.py generate_vsystem --v-system=v1 --clean --string-set="e-b"

# Generate all V2 (drop-2) voicings with a 6-string range
python manage.py generate_vsystem --v-system=v2 --string-set="e-b"

# Generate a specific chord
python manage.py generate_vsystem --v-system=v1 --root=0 --chord-type="Major 7" --string-set="g-A"
```

**Important note:** Due to the database schema, string ranges containing "highA" or "lowB" (8-string ranges) cannot be used for V-System chords because they exceed the character limit in the database. Stick to standard 6-string ranges like:
- "e-b" (top 4 strings)
- "g-A" (middle 4 strings)
- "d-E" (bottom 4 strings)

### 4. Common Troubleshooting Steps

If the generator fails, try these debugging steps:

1. **Error**: `cannot import name 'get_note_for_position'`
   **Solution**: This function was referenced but doesn't exist. The code has been updated to remove this dependency.

2. **Error**: `Note range not found in valid ranges`
   **Solution**: Check if the string range you're using is valid in the `string_choices.py` file.

3. **Error**: Database issues
   **Solution**: Make sure migrations are applied: `python manage.py migrate`

4. **Error**: `ValueError: Unsupported chord type`
   **Solution**: Check that the chord type is in the supported list in `v_system_generator.py`

## Using the V-System in the Application

1. Start the Django development server:
   ```
   python manage.py runserver
   ```

2. Navigate to the chord finder page in your browser

3. From the Type dropdown, select either "V1" or "V2"

4. Choose your desired chord quality (Major 7, Dominant 7, etc.)

5. Select your root note

6. Explore different string sets using the Range dropdown

## Extending the V-System

To add more V-System voicing types (V3-V14):

1. In `v_system_generator.py`, add new methods similar to `generate_v1_voicing` and `generate_v2_voicing` for each new voicing type

2. Update the dropdown options in `views_chords.py` to include the new voicing types

3. Generate the new voicings with the management command:
   ```
   python manage.py generate_vsystem --v-system=v3
   ```

## Debugging Tips

If you need to debug voicing generation:

1. Add `print()` statements in the generator methods to track the notes being generated

2. Use the Django shell to test individual voicing creation:
   ```
   python manage.py shell
   
   # In the shell:
   from positionfinder.v_system_generator import VoicingSystem
   vs = VoicingSystem()
   chord = vs.generate_v1_voicing(0, "Major 7", "e-b")
   print(chord)
   ```

3. Check the database directly to verify voicings:
   ```
   from positionfinder.models_chords import ChordNotes
   ChordNotes.objects.filter(type_name="V1", chord_name="Major 7")
   ```
