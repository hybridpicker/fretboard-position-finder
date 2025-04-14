"""
Standardize chord ranges for V1 and V2 chords to a consistent set of options.
This management command ensures that all V1 and V2 chords only use standardized ranges.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from positionfinder.models_chords import ChordNotes
from django.db.models import Q

class Command(BaseCommand):
    help = 'Standardize ranges for V1 and V2 chords to a consistent set of options'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate changes without actually modifying the database',
        )
        parser.add_argument(
            '--type',
            help='Target specific chord type to standardize (e.g., "V1", "V2", "Triads")',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Standard ranges we want to keep for V1 and V2 chords
        STANDARD_RANGES = [
            'a-g', 'e-d', 'b-A', 'g-E', 'd-B'
        ]
        
        # 8-string specific ranges we want to preserve
        EIGHT_STRING_RANGES = [
            'highA - g', 'd - lowB'
        ]
        
        # Normalized format with spaces we'll convert to
        NORMALIZED_RANGES = [
            'a - g', 'e - d', 'b - A', 'g - E', 'd - B'
        ] + EIGHT_STRING_RANGES
        
        # Map of non-standard ranges to their standard replacements
        # This defines which non-standard range gets replaced with which standard range
        RANGE_MAPPING = {
            # Map similar high register ranges to 'e - d'
            'a - b': 'a - g',
            'e - g': 'e - d',
            'b - d': 'b - A',
            'g - A': 'g - E',
            'd - E': 'd - B',
            
            # Map any other ranges to appropriate replacements
            'A - B': 'd - B',
            'a - D': 'a - g',
            'e - A': 'e - d',
            'b - E': 'b - A',
            'g - B': 'g - E',
            'a - A': 'a - g',
            'e - E': 'e - d',
            'b - B': 'b - A',
            'a - E': 'a - g',
            'e - B': 'e - d',
            
            # Normalize any ranges that might be missing spaces
            'a-g': 'a - g',
            'e-d': 'e - d',
            'b-A': 'b - A',
            'g-E': 'g - E',
            'd-B': 'd - B',
            
            # Preserve 8-string specific ranges but normalize format if needed
            'highA-g': 'highA - g',
            'd-lowB': 'd - lowB',
            
            # Map other 8-string specific ranges to our two standard 8-string ranges
            'e - lowB': 'd - lowB',
            'b - lowB': 'd - lowB',
            'g - lowB': 'd - lowB',
            'A - lowB': 'd - lowB',
            'E - lowB': 'd - lowB',
            'highA - e': 'highA - g',
            'highA - b': 'highA - g',
            'highA - d': 'highA - g',
            'highA - A': 'highA - g', 
            'highA - E': 'highA - g',
            'highA - lowB': 'highA - g', # Full range maps to high register for simplicity
            'highA - AString': 'highA - g',
            'highA - ELowString': 'highA - g',
            'bString - lowB': 'd - lowB',
            'dString - lowB': 'd - lowB',
        }
        
        # Get chords to process
        chord_type = options.get('type')
        if chord_type:
            v_system_chords = ChordNotes.objects.filter(type_name=chord_type)
        else:
            # Default to V1 and V2 chords
            v_system_chords = ChordNotes.objects.filter(
                Q(type_name='V1') | Q(type_name='V2')
            )
        
        # Count chords before changes
        total_chords = v_system_chords.count()
        self.stdout.write(f"Found {total_chords} V1/V2 chords to process")
        
        # Analyze current ranges
        current_ranges = v_system_chords.values_list('range', flat=True).distinct()
        self.stdout.write(f"Current ranges in use: {sorted(list(current_ranges))}")
        
        # Counts for reporting
        updated_count = 0
        skipped_count = 0
        
        # Process chords
        if dry_run:
            # For dry run, no transaction needed
            self._process_chords(v_system_chords, NORMALIZED_RANGES, RANGE_MAPPING, dry_run)
            
            # Final report for dry run
            self.stdout.write(self.style.SUCCESS(f"Would process {total_chords} chords:"))
            self.stdout.write(f"- {self.updated_count} chords would be updated")
            self.stdout.write(f"- {self.skipped_count} chords already have standard ranges")
            self.stdout.write(self.style.WARNING("DRY RUN: No changes were made to the database"))
        else:
            # For actual changes, use atomic transaction
            try:
                with transaction.atomic():
                    self._process_chords(v_system_chords, NORMALIZED_RANGES, RANGE_MAPPING, dry_run)
                    
                    # Final report
                    self.stdout.write(self.style.SUCCESS(f"Processed {total_chords} chords:"))
                    self.stdout.write(f"- {self.updated_count} chords updated")
                    self.stdout.write(f"- {self.skipped_count} chords already had standard ranges")
                    self.stdout.write(self.style.SUCCESS("Changes committed to database"))
                    
                # Show final ranges outside transaction
                final_ranges = ChordNotes.objects.filter(
                    Q(type_name='V1') | Q(type_name='V2')
                ).values_list('range', flat=True).distinct()
                self.stdout.write(f"Final ranges in use: {sorted(list(final_ranges))}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
                raise
                
    def _process_chords(self, chords, normalized_ranges, range_mapping, dry_run):
        """Process each chord, updating ranges as needed"""
        self.updated_count = 0
        self.skipped_count = 0
        
        for chord in chords:
            current_range = chord.range
            
            # Check if range needs updating
            if current_range in normalized_ranges:
                # Range is already one of our standards in correct format
                self.skipped_count += 1
                continue
            
            # If range needs normalization or replacement
            if current_range in range_mapping:
                new_range = range_mapping[current_range]
                self.stdout.write(f"Changing chord {chord.id} ({chord.type_name}, {chord.chord_name}) range from '{current_range}' to '{new_range}'")
                
                if not dry_run:
                    chord.range = new_range
                    chord.save(update_fields=['range'])
                
                self.updated_count += 1
            else:
                # Range not in our mapping, set to default
                if 'a' in current_range.lower():
                    new_range = 'a - g'
                elif 'e' in current_range.lower():
                    new_range = 'e - d'
                elif 'b' in current_range.lower():
                    new_range = 'b - A'
                elif 'g' in current_range.lower():
                    new_range = 'g - E'
                else:
                    new_range = 'd - B'
                
                self.stdout.write(f"Unmapped range: Changing chord {chord.id} ({chord.type_name}, {chord.chord_name}) range from '{current_range}' to '{new_range}'")
                
                if not dry_run:
                    chord.range = new_range
                    chord.save(update_fields=['range'])
                
                self.updated_count += 1
