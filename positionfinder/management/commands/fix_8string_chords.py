from django.core.management.base import BaseCommand
from django.db import transaction, connection
from positionfinder.models_chords import ChordPosition
from positionfinder.eight_string_setup import create_base_position
from positionfinder.optimized_chords import add_eighth_string_voicings
import time

class Command(BaseCommand):
    help = 'Audit and fix 8-string chord configurations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--rebuild',
            action='store_true',
            help='Rebuild all 8-string chord positions',
        )
        parser.add_argument(
            '--audit',
            action='store_true',
            help='Audit 8-string chord positions without fixing',
        )
        parser.add_argument(
            '--fix-missing',
            action='store_true',
            help='Fix only missing 8-string chord positions',
        )

    def handle(self, *args, **options):
        rebuild = options.get('rebuild', False)
        audit = options.get('audit', False)
        fix_missing = options.get('fix_missing', False)

        if not any([rebuild, audit, fix_missing]):
            # Default to audit mode if no options specified
            audit = True
            self.stdout.write(self.style.WARNING('No options specified. Running in audit mode.'))

        # Start timer
        start_time = time.time()
        
        # Get all chords with 8-string ranges using a raw SQL query to avoid migration issues
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, type_name, chord_name, range 
                FROM positionfinder_chordnotes 
                WHERE range LIKE 'highA%' OR range LIKE '%lowB'
            """)
            chord_data = cursor.fetchall()
            
        eight_string_chord_ids = [row[0] for row in chord_data]
        self.stdout.write(f"Found {len(eight_string_chord_ids)} 8-string chords to process")
        
        # Track statistics
        stats = {
            'audited': 0,
            'missing_positions': 0,
            'fixed': 0,
            'failures': 0,
            'rebuilt': 0
        }

        # For rebuild, delete all 8-string chord positions first
        if rebuild:
            self.stdout.write(self.style.WARNING("Rebuilding all 8-string chord positions..."))
            with connection.cursor() as cursor:
                # Need to handle empty list case
                if eight_string_chord_ids:
                    if len(eight_string_chord_ids) == 1:
                        cursor.execute("""
                            DELETE FROM positionfinder_chordposition 
                            WHERE notes_name_id = %s
                        """, [eight_string_chord_ids[0]])
                    else:
                        cursor.execute("""
                            DELETE FROM positionfinder_chordposition 
                            WHERE notes_name_id IN %s
                        """, [tuple(eight_string_chord_ids)])
                    position_count = cursor.rowcount
                else:
                    position_count = 0
            
            self.stdout.write(f"Deleted {position_count} existing 8-string chord positions")
        
        # Process each chord
        with transaction.atomic():
            if rebuild:
                # Use optimized 8-string chord generator
                self.stdout.write("Creating optimized 8-string voicings...")
                add_eighth_string_voicings()
                stats['rebuilt'] = len(eight_string_chord_ids)
                
            else:
                # Audit and optionally fix chords
                for chord_id, chord_type, chord_name, chord_range in chord_data:
                    stats['audited'] += 1
                    
                    # Check if chord has positions
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT COUNT(*) FROM positionfinder_chordposition 
                            WHERE notes_name_id = %s
                        """, [chord_id])
                        position_count = cursor.fetchone()[0]
                    
                    has_positions = position_count > 0
                    
                    if not has_positions:
                        stats['missing_positions'] += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"Chord #{chord_id}: {chord_name} ({chord_range}) has no positions"
                            )
                        )
                        
                        # Fix missing positions if requested
                        if fix_missing:
                            try:
                                create_base_position(chord_id)
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"Created positions for chord #{chord_id}: {chord_name} ({chord_range})"
                                    )
                                )
                                stats['fixed'] += 1
                            except Exception as e:
                                self.stdout.write(
                                    self.style.ERROR(
                                        f"Failed to create positions for chord #{chord_id}: {e}"
                                    )
                                )
                                stats['failures'] += 1
                    
                    # Progress indicator every 10 chords
                    if stats['audited'] % 10 == 0:
                        self.stdout.write(f"Processed {stats['audited']} chords...")
        
        # Print summary
        elapsed_time = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f"\nCompleted in {elapsed_time:.2f} seconds"))
        self.stdout.write(f"Audited: {stats['audited']} 8-string chords")
        
        if audit or fix_missing:
            self.stdout.write(f"Missing positions: {stats['missing_positions']}")
            
        if fix_missing:
            self.stdout.write(f"Fixed: {stats['fixed']}")
            self.stdout.write(f"Failures: {stats['failures']}")
            
        if rebuild:
            self.stdout.write(f"Rebuilt: {stats['rebuilt']}")
