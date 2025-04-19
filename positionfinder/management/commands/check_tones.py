import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path

class Command(BaseCommand):
    help = 'Checks if all tones defined in the JavaScript data structure exist as audio files and are properly mapped.'

    def handle(self, *args, **options):
        """
        Command handler that performs the tone validation.
        """
        self.stdout.write(self.style.SUCCESS('Starting tone validation...'))
        
        # Get the static directory
        static_dir = Path(settings.BASE_DIR) / 'static'
        tone_dir = static_dir / 'media' / 'tone_sounds'
        js_dir = static_dir / 'js'
        
        if not tone_dir.exists():
            self.stdout.write(self.style.ERROR(f'Tone directory not found: {tone_dir}'))
            return
        
        # String config for the fretboard
        string_array = [
            'highAString', 'eString', 'bString', 'gString', 
            'dString', 'AString', 'ELowString', 'lowBString'
        ]
        
        # Expected NOTES structure from base.2.0.4.js
        # This could be read directly from the JS file but for simplicity we're defining it here
        expected_notes = {
            'eString': [['f2'], ['gb2', 'fs2'], ['g2'], ['ab2', 'gs2'], ['a2'], ['bb2', 'as2'], ['b2'], ['c3'], ['db3', 'cs3'], ['d3'], ['eb3', 'ds3'], ['e3'], ['f3'], ['gb3', 'fs3'], ['g3'], ['ab3', 'gs3'], ['a3']],
            'bString': [['c2'], ['db2', 'cs2'], ['d2'], ['eb2', 'ds2'], ['e2'], ['f2'], ['gb2', 'fs2'], ['g2'], ['ab2', 'gs2'], ['a2'], ['bb2', 'as2'], ['b2'], ['c3'], ['db3', 'cs3'], ['d3'], ['eb3', 'ds3'], ['e3']],
            'gString': [['ab1', 'gs1'], ['a1'], ['bb1', 'as1'], ['b1'], ['c2'], ['db2', 'cs2'], ['d2'], ['eb2', 'ds2'], ['e2'], ['f2'], ['gb2', 'fs2'], ['g2'], ['ab2', 'gs2'], ['a2'], ['bb2', 'as2'], ['b2'], ['c3']],
            'dString': [['eb1', 'ds1'], ['e1'], ['f1'], ['gb1', 'fs1'], ['g1'], ['ab1', 'gs1'], ['a1'], ['bb1', 'as1'], ['b1'], ['c2'], ['db2', 'cs2'], ['d2'], ['eb2', 'ds2'], ['e2'], ['f2'], ['gb2', 'fs2'], ['g2']],
            'AString': [['bb0', 'as0'], ['b0'], ['c1'], ['db1', 'cs1'], ['d1'], ['eb1', 'ds1'], ['e1'], ['f1'], ['gb1', 'fs1'], ['g1'], ['ab1', 'gs1'], ['a1'], ['bb1', 'as1'], ['b1'], ['c2'], ['db2', 'cs2'], ['d2']],
            'ELowString': [['f0'], ['gb0', 'fs0'], ['g0'], ['ab0', 'gs0'], ['a0'], ['bb0', 'as0'], ['b0'], ['c1'], ['db1', 'cs1'], ['d1'], ['eb1', 'ds1'], ['e1'], ['f1'], ['gb1', 'fs1'], ['g1'], ['ab1', 'gs1'], ['a1']],
            'highAString': [['bb2', 'as2'], ['b2'], ['c3'], ['db3', 'cs3'], ['d3'], ['eb3', 'ds3'], ['e3'], ['f3'], ['gb3', 'fs3'], ['g3'], ['ab3', 'gs3'], ['a3'], ['bb3', 'as3'], ['b3'], ['c4'], ['db4', 'cs4'], ['d4']],
            'lowBString': [['c0'], ['db0', 'cs0'], ['d0'], ['eb0', 'ds0'], ['e0'], ['f0'], ['gb0', 'fs0'], ['g0'], ['ab0', 'gs0'], ['a0'], ['bb0', 'as0'], ['b0'], ['c1'], ['db1', 'cs1'], ['d1'], ['eb1', 'ds1'], ['e1']]
        }
            
        # 1. Check if all strings in string_array have entries in NOTES
        self.stdout.write('Checking string definitions...')
        missing_strings = []
        for string_name in string_array:
            if string_name not in expected_notes:
                missing_strings.append(string_name)
        
        if missing_strings:
            self.stdout.write(self.style.ERROR(f'Missing strings in NOTES data: {", ".join(missing_strings)}'))
        else:
            self.stdout.write(self.style.SUCCESS('All strings defined correctly'))
        
        # 2. Get a flat list of all expected tones
        all_expected_tones = []
        for string_name, frets in expected_notes.items():
            for fret in frets:
                for tone in fret:
                    if tone not in all_expected_tones:
                        all_expected_tones.append(tone)
        
        self.stdout.write(f'Found {len(all_expected_tones)} unique tones in the NOTES data structure')
        
        # 3. Check if tone files exist
        self.stdout.write('Checking tone files...')
        missing_files = []
        existing_files = []
        
        for tone in all_expected_tones:
            tone_file = f"{tone}.mp3"
            tone_path = tone_dir / tone_file
            if not tone_path.exists():
                missing_files.append(tone_file)
            else:
                existing_files.append(tone_file)
        
        if missing_files:
            self.stdout.write(self.style.ERROR(f'Missing {len(missing_files)} tone files: {", ".join(missing_files)}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'All {len(existing_files)} expected tone files exist'))
        
        # 4. Check for extra tone files
        all_tone_files = [f.name for f in tone_dir.glob('*.mp3')]
        extra_files = [f for f in all_tone_files if f.split('.')[0] not in all_expected_tones]
        
        if extra_files:
            self.stdout.write(self.style.WARNING(f'Found {len(extra_files)} extra tone files: {", ".join(extra_files)}'))
        
        # 5. Check enharmonic equivalents
        self.stdout.write('Checking enharmonic equivalents...')
        # Define all possible enharmonic pairs in both orders for flexibility
        enharmonic_pairs = [
            ('cs', 'db'), ('db', 'cs'),
            ('ds', 'eb'), ('eb', 'ds'),
            ('fs', 'gb'), ('gb', 'fs'),
            ('gs', 'ab'), ('ab', 'gs'),
            ('as', 'bb'), ('bb', 'as')
        ]
        
        enharmonic_errors = []
        for string_name, frets in expected_notes.items():
            for fret_index, fret in enumerate(frets):
                # Skip frets with only one note
                if len(fret) < 2:
                    continue
                
                # Check that the two notes in the fret are enharmonic equivalents
                note1 = fret[0].rstrip('0123456789')
                note2 = fret[1].rstrip('0123456789')
                octave1 = fret[0][-1]
                octave2 = fret[1][-1]
                
                # Octaves should match
                if octave1 != octave2:
                    enharmonic_errors.append(f'Octave mismatch in {string_name} fret {fret_index}: {fret[0]} and {fret[1]}')
                
                # Create a tuple with the two notes (without octave)
                fret_pair = (note1, note2)
                
                # Check if the pair is a valid enharmonic equivalent
                if fret_pair not in enharmonic_pairs:
                    enharmonic_errors.append(f'Invalid enharmonic pair in {string_name} fret {fret_index}: {fret_pair}')
        
        if enharmonic_errors:
            self.stdout.write(self.style.ERROR(f'Found {len(enharmonic_errors)} enharmonic errors:'))
            for error in enharmonic_errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
        else:
            self.stdout.write(self.style.SUCCESS('All enharmonic equivalents are correct'))
        
        # 6. Check for octave consistency
        self.stdout.write('Checking octave consistency...')
        octave_errors = []
        
        for string_name, frets in expected_notes.items():
            prev_octave = None
            
            for fret_index, fret in enumerate(frets):
                # Get octave from the first note in each fret
                current_octave = int(fret[0][-1])
                
                if prev_octave is not None:
                    # Octave should either stay the same or increment by 1
                    octave_diff = current_octave - prev_octave
                    if octave_diff not in [0, 1]:
                        octave_errors.append(f'Unexpected octave jump on {string_name} from fret {fret_index-1} ({prev_octave}) to {fret_index} ({current_octave})')
                
                prev_octave = current_octave
        
        if octave_errors:
            self.stdout.write(self.style.ERROR(f'Found {len(octave_errors)} octave consistency errors:'))
            for error in octave_errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
        else:
            self.stdout.write(self.style.SUCCESS('All octave progressions are consistent'))
        
        # Summary
        self.stdout.write('\nTone validation summary:')
        self.stdout.write(f'- Strings in array: {len(string_array)}')
        self.stdout.write(f'- Strings in NOTES: {len(expected_notes)}')
        self.stdout.write(f'- Expected unique tones: {len(all_expected_tones)}')
        self.stdout.write(f'- Existing tone files: {len(existing_files)}')
        self.stdout.write(f'- Missing tone files: {len(missing_files)}')
        self.stdout.write(f'- Extra tone files: {len(extra_files)}')
        self.stdout.write(f'- Enharmonic issues: {len(enharmonic_errors)}')
        self.stdout.write(f'- Octave consistency issues: {len(octave_errors)}')
        
        # Overall result
        if missing_files or enharmonic_errors or octave_errors:
            self.stdout.write(self.style.ERROR('\nTone validation FAILED. Please fix the issues listed above.'))
        else:
            self.stdout.write(self.style.SUCCESS('\nTone validation PASSED. All tones appear to be correctly defined and stored.'))
