"""
Validate chord ranges to ensure all chord types have complete range coverage.
This command checks that all chord types (especially V1/V2) have data for all standard ranges.
"""
from django.core.management.base import BaseCommand
from positionfinder.models_chords import ChordNotes
from django.db.models import Q
import json
from collections import defaultdict
import os
from django.utils.termcolors import colorize

class Command(BaseCommand):
    help = 'Validate chord ranges to ensure complete coverage across chord types'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            default='V2',
            help='Chord type to validate (default: V2)',
        )
        parser.add_argument(
            '--report',
            action='store_true',
            help='Generate detailed report',
        )
        parser.add_argument(
            '--output',
            help='Output file for JSON report',
        )

    def handle(self, *args, **options):
        chord_type = options['type']
        detailed_report = options['report']
        output_file = options['output']
        
        # Standard ranges for 6-string and 8-string guitars
        standard_ranges_6string = [
            'a - g', 'e - d', 'b - A', 'g - E', 'd - B'
        ]
        
        standard_ranges_8string = [
            'highA - g', 'd - lowB'
        ]
        
        all_standard_ranges = standard_ranges_6string + standard_ranges_8string
        
        # Get all unique chord names for the specified type
        chord_names = ChordNotes.objects.filter(
            type_name=chord_type
        ).values_list('chord_name', flat=True).distinct().order_by('chord_name')
        
        self.stdout.write(f"Validating ranges for chord type: {chord_type}")
        self.stdout.write(f"Found {len(chord_names)} chord names: {', '.join(chord_names)}")
        
        # Check coverage for each chord name
        missing_ranges = {}
        extra_ranges = {}
        counts = defaultdict(int)
        coverage_summary = {}
        chord_range_details = defaultdict(dict)
        
        for chord_name in chord_names:
            # Get all ranges for this chord
            ranges_for_chord = ChordNotes.objects.filter(
                type_name=chord_type,
                chord_name=chord_name
            ).values_list('range', flat=True).distinct()
            
            # Convert to set for easier comparison
            ranges_set = set(ranges_for_chord)
            standard_set = set(all_standard_ranges)
            
            # Check for missing standard ranges
            missing = standard_set - ranges_set
            if missing:
                missing_ranges[chord_name] = list(missing)
                
            # Check for extra non-standard ranges
            extra = ranges_set - standard_set
            if extra:
                extra_ranges[chord_name] = list(extra)
            
            # Count occurrences of each range for this chord
            for range_value in ranges_for_chord:
                counts[(chord_name, range_value)] += 1
            
            # Build coverage data
            chord_coverage = {
                'name': chord_name,
                'total_ranges': len(ranges_set),
                'standard_ranges': list(ranges_set & standard_set),
                'missing_ranges': list(missing),
                'extra_ranges': list(extra),
                'coverage_percentage': round(len(ranges_set & standard_set) / len(standard_set) * 100, 1),
                'duplicates': [r for r in ranges_for_chord if list(ranges_for_chord).count(r) > 1]
            }
            coverage_summary[chord_name] = chord_coverage
            
            # Get detail for each range
            for range_name in all_standard_ranges:
                chords_with_range = ChordNotes.objects.filter(
                    type_name=chord_type,
                    chord_name=chord_name,
                    range=range_name
                )
                
                chord_range_details[chord_name][range_name] = {
                    'exists': chords_with_range.exists(),
                    'count': chords_with_range.count(),
                    'ids': list(chords_with_range.values_list('id', flat=True)),
                }
        
        # Look for duplicate chord-range combinations
        duplicates = {k: v for k, v in counts.items() if v > 1}
        
        # Summary of findings
        self.stdout.write("\n===== SUMMARY =====")
        
        # Missing ranges
        if missing_ranges:
            self.stdout.write(colorize(f"⚠️  {len(missing_ranges)} chord names missing standard ranges", fg="yellow"))
            if detailed_report:
                for chord_name, ranges in missing_ranges.items():
                    self.stdout.write(f"  - {chord_name}: Missing {', '.join(ranges)}")
        else:
            self.stdout.write(colorize("✅ All chord names have all standard ranges", fg="green"))
            
        # Extra ranges
        if extra_ranges:
            self.stdout.write(colorize(f"ℹ️  {len(extra_ranges)} chord names have non-standard ranges", fg="red"))
            if detailed_report:
                for chord_name, ranges in extra_ranges.items():
                    self.stdout.write(f"  - {chord_name}: Has extra ranges {', '.join(ranges)}")
        else:
            self.stdout.write(colorize("✅ No chord names have non-standard ranges", fg="green"))
            
        # Duplicate ranges
        if duplicates:
            self.stdout.write(colorize(f"⚠️  Found {len(duplicates)} duplicate chord-range combinations", fg="yellow"))
            if detailed_report:
                for (chord_name, range_name), count in duplicates.items():
                    self.stdout.write(f"  - {chord_name}, {range_name}: {count} duplicates")
        else:
            self.stdout.write(colorize("✅ No duplicate chord-range combinations found", fg="green"))
            
        # Range coverage statistics
        self.stdout.write("\n===== RANGE COVERAGE =====")
        coverage_stats = {}
        for range_name in all_standard_ranges:
            chords_with_range = sum(1 for chord_name in chord_names 
                                  if chord_range_details[chord_name][range_name]['exists'])
            coverage_percent = round(chords_with_range / len(chord_names) * 100, 1)
            coverage_stats[range_name] = {
                'chords_with_range': chords_with_range,
                'total_chords': len(chord_names),
                'coverage_percent': coverage_percent
            }
            
            color = "green" if coverage_percent == 100 else "yellow" if coverage_percent >= 80 else "red"
            status = "✅" if coverage_percent == 100 else "⚠️" if coverage_percent >= 80 else "❌"
            self.stdout.write(colorize(f"{status} {range_name}: {coverage_percent}% ({chords_with_range}/{len(chord_names)} chords)", fg=color))
        
        # Range distribution table
        if detailed_report:
            self.stdout.write("\n===== RANGE DISTRIBUTION =====")
            header = "Chord Name".ljust(20) + " | " + " | ".join(r.ljust(10) for r in all_standard_ranges)
            separator = "-" * len(header)
            self.stdout.write(separator)
            self.stdout.write(header)
            self.stdout.write(separator)
            
            for chord_name in chord_names:
                row = chord_name.ljust(20) + " | "
                for range_name in all_standard_ranges:
                    if chord_range_details[chord_name][range_name]['exists']:
                        row += "✅".ljust(10) + " | "
                    else:
                        row += "❌".ljust(10) + " | "
                self.stdout.write(row.rstrip(" | "))
            
            self.stdout.write(separator)
            
        # Save JSON report if requested
        if output_file:
            report_data = {
                'chord_type': chord_type,
                'chord_names': list(chord_names),
                'coverage_summary': coverage_summary,
                'range_stats': coverage_stats,
                'chord_range_details': chord_range_details
            }
            
            # Create fixtures directory if it doesn't exist
            fixtures_dir = 'fixtures'
            if not os.path.exists(fixtures_dir):
                os.makedirs(fixtures_dir)
                
            # Full path to output file
            output_path = os.path.join(fixtures_dir, output_file)
            
            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2)
                
            self.stdout.write(self.style.SUCCESS(f"Detailed report saved to {output_path}"))
