from django.core.management.base import BaseCommand
from django.db import transaction, connection
from positionfinder.models_chords import ChordNotes
from positionfinder.chord_validation import validate_chord_notes, fix_chord_validation_issues
import time
import json

class Command(BaseCommand):
    help = 'Validate and fix chord note configuration issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--chord-id',
            type=int,
            help='Validate a specific chord by ID',
        )
        parser.add_argument(
            '--chord-name',
            type=str,
            help='Validate chords by name (e.g., "Major", "Minor 7")',
        )
        parser.add_argument(
            '--range',
            type=str,
            help='Validate chords by range (e.g., "highA - e", "e - lowB")',
        )
        parser.add_argument(
            '--audit',
            action='store_true',
            help='Audit chords without fixing',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix validation issues in chords',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed validation reports',
        )

    def handle(self, *args, **options):
        chord_id = options.get('chord_id', None)
        chord_name = options.get('chord_name', None)
        range_filter = options.get('range', None)
        audit_only = options.get('audit', False)
        fix_issues = options.get('fix', False)
        verbose = options.get('verbose', False)

        if not any([audit_only, fix_issues]):
            # Default to audit mode if no options specified
            audit_only = True
            self.stdout.write(self.style.WARNING('No action specified. Running in audit mode.'))

        # Start timer
        start_time = time.time()
        
        # Get chords to validate
        if chord_id:
            # Validate a specific chord
            chords = ChordNotes.objects.filter(id=chord_id)
        elif chord_name:
            # Validate chords by name
            chords = ChordNotes.objects.filter(chord_name=chord_name)
        elif range_filter:
            # Validate chords by range
            chords = ChordNotes.objects.filter(range=range_filter)
        else:
            # Validate all chords
            chords = ChordNotes.objects.all()
        
        chord_count = chords.count()
        self.stdout.write(f"Found {chord_count} chords to validate")
        
        # Track statistics
        stats = {
            'total': chord_count,
            'valid': 0,
            'invalid': 0,
            'fixed': 0,
            'fix_failed': 0,
        }

        # Process each chord
        for chord in chords:
            # Validate the chord
            validation = validate_chord_notes(chord.id)
            
            if validation['valid']:
                stats['valid'] += 1
                if verbose:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Chord #{chord.id}: {chord.chord_name} ({chord.range}) is valid"
                        )
                    )
            else:
                stats['invalid'] += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Chord #{chord.id}: {chord.chord_name} ({chord.range}) has validation issues:"
                    )
                )
                for issue in validation['issues']:
                    self.stdout.write(f"  - {issue}")
                
                if verbose:
                    self.stdout.write("  Validation details:")
                    self.stdout.write(f"    Note count: {validation['note_count']}")
                    self.stdout.write(f"    String assignments: {json.dumps(validation['string_assignments'])}")
                    self.stdout.write(f"    Positions: {len(validation['positions'])}")
                
                # Fix issues if requested
                if fix_issues:
                    self.stdout.write(f"  Attempting to fix chord #{chord.id}...")
                    
                    try:
                        with transaction.atomic():
                            fix_result = fix_chord_validation_issues(chord.id)
                            
                            if fix_result['fixed']:
                                stats['fixed'] += 1
                                self.stdout.write(
                                    self.style.SUCCESS(f"  Fixed chord #{chord.id}")
                                )
                                if verbose:
                                    for action in fix_result['actions']:
                                        self.stdout.write(f"    - {action}")
                            else:
                                stats['fix_failed'] += 1
                                self.stdout.write(
                                    self.style.ERROR(f"  Failed to fix chord #{chord.id}")
                                )
                                for issue in fix_result['remaining_issues']:
                                    self.stdout.write(f"    - {issue}")
                    except Exception as e:
                        stats['fix_failed'] += 1
                        self.stdout.write(
                            self.style.ERROR(f"  Error fixing chord #{chord.id}: {str(e)}")
                        )
            
            # Progress indicator every 10 chords
            if (stats['valid'] + stats['invalid']) % 10 == 0:
                self.stdout.write(f"Processed {stats['valid'] + stats['invalid']} of {chord_count} chords...")
        
        # Print summary
        elapsed_time = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f"\nCompleted in {elapsed_time:.2f} seconds"))
        self.stdout.write(f"Total chords: {stats['total']}")
        self.stdout.write(f"Valid chords: {stats['valid']}")
        self.stdout.write(f"Invalid chords: {stats['invalid']}")
        
        if fix_issues:
            self.stdout.write(f"Fixed chords: {stats['fixed']}")
            self.stdout.write(f"Failed fixes: {stats['fix_failed']}")
