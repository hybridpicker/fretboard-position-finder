"""
Fill in missing chord ranges by cloning and adapting existing chord data.
"""
from django.core.management.base import BaseCommand
from positionfinder.models_chords import ChordNotes, ChordPosition
from django.db import transaction
from django.db.models import Q
import logging

class Command(BaseCommand):
    help = 'Fill in missing chord ranges for V1/V2/Triads chord types'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--type',
            help='Target specific chord type to fill (V1, V2, or Triads)',
        )
        parser.add_argument(
            '--range',
            help='Target specific range to fill',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        target_type = options['type']
        target_range = options['range']
        
        # Standard ranges for 6-string and 8-string guitars
        standard_ranges_6string = [
            'a - g', 'e - d', 'b - A', 'g - E', 'd - B'
        ]
        
        standard_ranges_8string = [
            'highA - g', 'd - lowB'
        ]
        
        all_standard_ranges = standard_ranges_6string + standard_ranges_8string
        
        # Map to define which source range to use for each target range
        range_source_map = {
            # For 6-string ranges
            'a - g': 'e - d',   # Use e-d voicings as template for a-g
            'd - B': 'g - E',   # Use g-E voicings as template for d-B
            
            # For 8-string specific ranges - only if needed
            'highA - g': 'e - d',  # Use e-d voicings for highA-g
            'd - lowB': 'b - A',   # Use b-A voicings for d-lowB
        }
        
        # Set up a filter for chord types
        if target_type:
            type_filter = Q(type_name=target_type)
        else:
            # Focus on V1 and V2 for now
            type_filter = Q(type_name='V1') | Q(type_name='V2')
        
        # Get all chord types and names that need checking
        chord_data = ChordNotes.objects.filter(type_filter).values_list(
            'type_name', 'chord_name'
        ).distinct()
        
        self.stdout.write(f"Found {len(chord_data)} unique type-name combinations")
        
        # Track statistics
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        # Process in transaction
        with transaction.atomic():
            for chord_type, chord_name in chord_data:
                self.stdout.write(f"Processing {chord_type} {chord_name}:")
                
                # Get ranges that already exist for this chord
                existing_ranges = ChordNotes.objects.filter(
                    type_name=chord_type,
                    chord_name=chord_name
                ).values_list('range', flat=True).distinct()
                
                # Determine missing ranges
                missing_ranges = set(all_standard_ranges) - set(existing_ranges)
                
                # Filter to specific range if requested
                if target_range:
                    if target_range in missing_ranges:
                        missing_ranges = {target_range}
                    else:
                        missing_ranges = set()
                
                if not missing_ranges:
                    self.stdout.write(f"  No missing ranges for {chord_type} {chord_name}")
                    continue
                
                # Process each missing range
                for missing_range in missing_ranges:
                    # Determine source range
                    source_range = range_source_map.get(missing_range) 
                    if not source_range:
                        self.stdout.write(f"  ❌ No source range defined for {missing_range}, skipping")
                        skipped_count += 1
                        continue
                        
                    # Check if source range exists
                    source_chords = ChordNotes.objects.filter(
                        type_name=chord_type,
                        chord_name=chord_name,
                        range=source_range
                    )
                    
                    if not source_chords.exists():
                        self.stdout.write(f"  ❌ Source range {source_range} not found for {chord_type} {chord_name}, skipping")
                        skipped_count += 1
                        continue
                    
                    # Get the source chord to clone from
                    # Handle the case where there might be multiple source chords
                    if source_chords.count() > 1:
                        self.stdout.write(f"  ⚠️ Multiple source chords found for {source_range}, using first one")
                        
                    source_chord = source_chords.first()
                    
                    # Note what we're doing
                    self.stdout.write(f"  Creating {missing_range} from {source_range}")
                    
                    # Adapt string assignments for the new range
                    if missing_range == 'd - B':
                        # For d-B, use one string lower than g-E
                        first_string = self._lower_string(source_chord.first_note_string)
                        second_string = self._lower_string(source_chord.second_note_string)
                        third_string = self._lower_string(source_chord.third_note_string)
                        fourth_string = self._lower_string(source_chord.fourth_note_string) if source_chord.fourth_note_string else None
                    elif missing_range == 'a - g':
                        # For a-g, use default or slightly higher strings
                        first_string = self._higher_string(source_chord.first_note_string)
                        second_string = self._higher_string(source_chord.second_note_string)
                        third_string = self._higher_string(source_chord.third_note_string)
                        fourth_string = self._higher_string(source_chord.fourth_note_string) if source_chord.fourth_note_string else None
                    elif missing_range == 'highA - g':
                        # For highA-g, adapt for high A string
                        first_string = 'highAString' if source_chord.first_note_string == 'eString' else source_chord.first_note_string
                        second_string = source_chord.second_note_string
                        third_string = source_chord.third_note_string
                        fourth_string = source_chord.fourth_note_string
                    elif missing_range == 'd - lowB':
                        # For d-lowB, adapt for low B string
                        first_string = source_chord.first_note_string
                        second_string = source_chord.second_note_string
                        third_string = source_chord.third_note_string
                        fourth_string = 'lowBString' if source_chord.fourth_note_string == 'ELowString' else source_chord.fourth_note_string
                    else:
                        # Direct clone for other ranges
                        first_string = source_chord.first_note_string
                        second_string = source_chord.second_note_string
                        third_string = source_chord.third_note_string
                        fourth_string = source_chord.fourth_note_string
                    
                    if not dry_run:
                        try:
                            # Create new chord with adapted values
                            new_chord = ChordNotes.objects.create(
                                category_id=source_chord.category_id,
                                ordering=source_chord.ordering,
                                type_name=source_chord.type_name,
                                chord_name=source_chord.chord_name,
                                chord_ordering=source_chord.chord_ordering,
                                range=missing_range,
                                range_ordering=source_chord.range_ordering,
                                tonal_root=source_chord.tonal_root,
                                first_note=source_chord.first_note,
                                first_note_string=first_string,
                                second_note=source_chord.second_note,
                                second_note_string=second_string,
                                third_note=source_chord.third_note,
                                third_note_string=third_string,
                                fourth_note=source_chord.fourth_note,
                                fourth_note_string=fourth_string,
                                fifth_note=source_chord.fifth_note,
                                fifth_note_string=source_chord.fifth_note_string,
                                sixth_note=source_chord.sixth_note,
                                sixth_note_string=source_chord.sixth_note_string
                            )
                            
                            # Clone positions
                            source_positions = ChordPosition.objects.filter(notes_name_id=source_chord.id)
                            for pos in source_positions:
                                ChordPosition.objects.create(
                                    notes_name_id=new_chord.id,
                                    inversion_order=pos.inversion_order,
                                    first_note=pos.first_note,
                                    second_note=pos.second_note,
                                    third_note=pos.third_note,
                                    fourth_note=pos.fourth_note,
                                    fifth_note=pos.fifth_note,
                                    sixth_note=pos.sixth_note
                                )
                            
                            created_count += 1
                            self.stdout.write(f"    ✅ Created {chord_type} {chord_name} for range {missing_range}")
                        except Exception as e:
                            error_count += 1
                            self.stdout.write(f"    ❌ Error creating {chord_type} {chord_name} for range {missing_range}: {str(e)}")
                    else:
                        self.stdout.write(f"    (dry run) Would create {chord_type} {chord_name} for range {missing_range}")
                        created_count += 1
        
        # Summary
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Dry run complete. Would create {created_count} chords, skipped {skipped_count}, with {error_count} errors"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Created {created_count} chords, skipped {skipped_count}, with {error_count} errors"))
    
    def _lower_string(self, string_name):
        """Move one string lower (thicker)"""
        string_map = {
            'eString': 'bString',
            'bString': 'gString',
            'gString': 'dString',
            'dString': 'AString',
            'AString': 'ELowString',
            'ELowString': 'lowBString',
        }
        return string_map.get(string_name, string_name)
    
    def _higher_string(self, string_name):
        """Move one string higher (thinner)"""
        string_map = {
            'lowBString': 'ELowString',
            'ELowString': 'AString',
            'AString': 'dString',
            'dString': 'gString',
            'gString': 'bString',
            'bString': 'eString',
            'eString': 'highAString',
        }
        return string_map.get(string_name, string_name)
