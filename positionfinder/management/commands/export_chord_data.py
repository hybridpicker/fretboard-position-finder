"""
Export chord data to a JSON fixture file.
This management command exports ChordNotes and ChordPosition data to JSON format.
"""
from django.core.management.base import BaseCommand
from django.core import serializers
from positionfinder.models_chords import ChordNotes, ChordPosition
from django.db.models import Q
import json
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Export chord data to a JSON fixture file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default='chord_data_dump.json',
            help='Output file name (default: chord_data_dump.json)',
        )
        parser.add_argument(
            '--type',
            help='Filter by chord type (e.g., V1, V2, Triads)',
        )
        parser.add_argument(
            '--pretty',
            action='store_true',
            help='Format JSON with indentation for readability',
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Create a timestamped backup if file exists',
        )

    def handle(self, *args, **options):
        output_file = options['output']
        chord_type = options['type']
        pretty = options['pretty']
        backup = options['backup']
        
        # Create fixtures directory if it doesn't exist
        fixtures_dir = 'fixtures'
        if not os.path.exists(fixtures_dir):
            os.makedirs(fixtures_dir)
            self.stdout.write(f"Created directory: {fixtures_dir}")
            
        # Full path to output file
        output_path = os.path.join(fixtures_dir, output_file)
        
        # Check if file exists and backup if requested
        if os.path.exists(output_path) and backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{os.path.splitext(output_path)[0]}_{timestamp}.json"
            with open(output_path, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
            self.stdout.write(f"Created backup: {backup_file}")
            
        # Build query for chord notes
        query = ChordNotes.objects.all()
        if chord_type:
            query = query.filter(type_name=chord_type)
            self.stdout.write(f"Filtering chords by type: {chord_type}")
        
        # Get chord notes and their IDs
        chord_notes = list(query)
        chord_note_ids = [chord.id for chord in chord_notes]
        self.stdout.write(f"Found {len(chord_notes)} chord notes")
        
        # Get related chord positions
        chord_positions = ChordPosition.objects.filter(notes_name_id__in=chord_note_ids)
        self.stdout.write(f"Found {chord_positions.count()} chord positions")
        
        # Combine the querysets and serialize
        all_objects = list(chord_notes) + list(chord_positions)
        
        # Serialize to JSON
        indent = 4 if pretty else None
        serialized_data = serializers.serialize('json', all_objects, indent=indent)
        
        # Save to file
        with open(output_path, 'w') as f:
            f.write(serialized_data)
            
        self.stdout.write(self.style.SUCCESS(f"Successfully exported data to {output_path}"))
        self.stdout.write(f"- {len(chord_notes)} chord notes")
        self.stdout.write(f"- {chord_positions.count()} chord positions")
        
        # Summarize chord types
        if not chord_type:
            chord_types = ChordNotes.objects.values_list('type_name', flat=True).distinct()
            self.stdout.write("Chord types included:")
            for t in sorted(chord_types):
                count = ChordNotes.objects.filter(type_name=t).count()
                self.stdout.write(f"- {t}: {count} chords")
