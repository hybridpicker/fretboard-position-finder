"""
Management command to check V-System chord positions.
"""
from django.core.management.base import BaseCommand
from positionfinder.models_chords import ChordNotes, ChordPosition

class Command(BaseCommand):
    help = 'Check V-System chord positions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='all',
            help='V-System type to check (v1, v2, or all)',
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information about each chord',
        )

    def handle(self, *args, **options):
        v_system_type = options['type'].lower()
        verbose = options['verbose']
        
        # Set the types to check
        types_to_check = []
        if v_system_type == 'all':
            types_to_check = ['V1', 'V2']
        elif v_system_type == 'v1':
            types_to_check = ['V1']
        elif v_system_type == 'v2':
            types_to_check = ['V2']
        else:
            self.stdout.write(self.style.ERROR(f"Invalid type: {v_system_type}. Use 'v1', 'v2', or 'all'."))
            return
            
        # Check V-System chord positions
        self.stdout.write(f"Checking positions for {', '.join(types_to_check)} chords...")
        
        # Count chords
        chord_count = ChordNotes.objects.filter(type_name__in=types_to_check).count()
        self.stdout.write(f"Found {chord_count} chords to check.")
        
        # Track statistics
        chords_with_positions = 0
        chords_missing_positions = 0
        chords_with_issues = 0
        
        position_types = {
            'Basic Position': 0,
            'First Inversion': 0,
            'Second Inversion': 0,
            'Third Inversion': 0
        }
        
        # Process each chord
        for chord in ChordNotes.objects.filter(type_name__in=types_to_check):
            # Get positions for this chord
            positions = ChordPosition.objects.filter(notes_name_id=chord.id)
            position_count = positions.count()
            
            if verbose:
                self.stdout.write(f"\nChord: {chord.type_name} {chord.chord_name} (Root: {chord.tonal_root}, Range: {chord.range})")
                self.stdout.write(f"  Notes: {chord.first_note}, {chord.second_note}, {chord.third_note}, {chord.fourth_note}")
                self.stdout.write(f"  Strings: {chord.first_note_string}, {chord.second_note_string}, {chord.third_note_string}, {chord.fourth_note_string}")
                self.stdout.write(f"  Positions: {position_count}")
            
            if position_count == 0:
                chords_missing_positions += 1
                if verbose:
                    self.stdout.write(self.style.WARNING(f"  No positions found for chord {chord.id}"))
                continue
                
            chords_with_positions += 1
            
            # Check if all positions are present
            expected_positions = ['Basic Position', 'First Inversion', 'Second Inversion', 'Third Inversion']
            found_positions = set(positions.values_list('inversion_order', flat=True))
            missing_positions = set(expected_positions) - found_positions
            
            # Update position statistics
            for pos in found_positions:
                if pos in position_types:
                    position_types[pos] += 1
            
            if missing_positions:
                chords_with_issues += 1
                if verbose:
                    self.stdout.write(self.style.WARNING(f"  Missing positions: {', '.join(missing_positions)}"))
                
            # Check if positions have valid intervals
            for position in positions:
                has_issue = False
                
                # Check if any position has None values
                if None in (position.first_note, position.second_note, position.third_note, position.fourth_note):
                    has_issue = True
                    if verbose:
                        self.stdout.write(self.style.ERROR(f"  Position {position.inversion_order} has None values: {position.first_note}, {position.second_note}, {position.third_note}, {position.fourth_note}"))
                
                # Check if Basic Position has all zeros
                if position.inversion_order == 'Basic Position':
                    if not (position.first_note == 0 and position.second_note == 0 and 
                            position.third_note == 0 and position.fourth_note == 0):
                        has_issue = True
                        if verbose:
                            self.stdout.write(self.style.ERROR(f"  Basic Position does not have all zeros: {position.first_note}, {position.second_note}, {position.third_note}, {position.fourth_note}"))
                
                if has_issue:
                    chords_with_issues += 1
                    
                # Show position details if verbose
                if verbose:
                    self.stdout.write(f"  {position.inversion_order}: {position.first_note}, {position.second_note}, {position.third_note}, {position.fourth_note}")
        
        # Summary
        self.stdout.write("\nSummary:")
        self.stdout.write(f"Total chords: {chord_count}")
        self.stdout.write(f"Chords with positions: {chords_with_positions}")
        self.stdout.write(f"Chords missing positions: {chords_missing_positions}")
        self.stdout.write(f"Chords with issues: {chords_with_issues}")
        self.stdout.write("\nPosition types found:")
        for pos_type, count in position_types.items():
            self.stdout.write(f"  {pos_type}: {count}")
