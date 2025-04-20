"""
Management command to generate Ted Greene's V-System voicings.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from positionfinder.v_system_generator import VoicingSystem
from positionfinder.models_chords import ChordNotes

class Command(BaseCommand):
    help = 'Generate V-System voicings for the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--v-system',
            type=str,
            default='v1',
            help='V-System to generate (v1, v2, or all)',
        )
        
        parser.add_argument(
            '--root',
            type=int,
            default=None,
            help='Root note (0-11, where 0=C, 1=C#, etc.). If not specified, generates for all roots.',
        )
        
        parser.add_argument(
            '--chord-type',
            type=str,
            default=None,
            help='Chord type to generate. If not specified, generates for all chord types.',
        )
        
        parser.add_argument(
            '--string-set',
            type=str,
            default='e-b',
            help='String set to use (e-b, d-E, g-A, e-E, highA-E, e-lowB, highA-lowB)',
        )
        
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing V-System chords before generating new ones',
        )

    def handle(self, *args, **options):
        v_system = options['v_system'].lower()
        root = options['root']
        chord_type = options['chord_type']
        string_set = options['string_set']
        clean = options['clean']
        
        # Clean existing V-System chords if requested
        if clean:
            self.stdout.write('Cleaning existing V-System chords...')
            with transaction.atomic():
                # Delete positions first (due to foreign key)
                deleted, _ = ChordNotes.objects.filter(type_name__in=['V1', 'V2']).delete()
                self.stdout.write(f'Deleted {deleted} existing V-System chords')
        
        # Initialize the voicing system
        voicing_system = VoicingSystem()
        
        # Generate chords based on options
        if v_system == 'v1' or v_system == 'all':
            if root is not None and chord_type is not None:
                # Generate a specific V1 chord
                self.stdout.write(f'Generating V1 voicing for root={root}, chord_type={chord_type}, string_set={string_set}')
                try:
                    chord = voicing_system.generate_v1_voicing(root, chord_type, string_set)
                    if chord:
                        self.stdout.write(f'Created chord: {chord}')
                    else:
                        self.stdout.write(self.style.WARNING(f'Failed to create chord for {string_set}. Try a different string set.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating chord: {e}'))
                
            elif root is not None and chord_type is None:
                # Generate all chord types for a specific root
                self.stdout.write(f'Generating V1 voicings for all chord types with root={root}, string_set={string_set}')
                try:
                    chords = voicing_system.generate_all_types_v1(root, string_set)
                    # Filter None values (failed creations)
                    chords = [c for c in chords if c is not None]
                    self.stdout.write(f'Created {len(chords)} V1 chords')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error generating V1 voicings: {e}'))
                
            elif root is None and chord_type is not None:
                # Generate all roots for a specific chord type
                self.stdout.write(f'Generating V1 voicings for all roots with chord_type={chord_type}, string_set={string_set}')
                try:
                    chords = voicing_system.generate_all_roots_v1(chord_type, string_set)
                    # Filter None values (failed creations)
                    chords = [c for c in chords if c is not None]
                    self.stdout.write(f'Created {len(chords)} V1 chords')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error generating V1 voicings: {e}'))
                
            else:
                # Generate all V1 chords for all roots and chord types
                self.stdout.write(f'Generating V1 voicings for all roots and chord types with string_set={string_set}')
                try:
                    chords = []
                    for chord_type in voicing_system.chord_types:
                        generated = voicing_system.generate_all_roots_v1(chord_type, string_set)
                        # Filter None values (failed creations)
                        generated = [c for c in generated if c is not None]
                        chords.extend(generated)
                    self.stdout.write(f'Created {len(chords)} V1 chords')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error generating V1 voicings: {e}'))
                
        if v_system == 'v2' or v_system == 'all':
            if root is not None and chord_type is not None:
                # Generate a specific V2 chord
                self.stdout.write(f'Generating V2 voicing for root={root}, chord_type={chord_type}, string_set={string_set}')
                try:
                    chord = voicing_system.generate_v2_voicing(root, chord_type, string_set)
                    if chord:
                        self.stdout.write(f'Created chord: {chord}')
                    else:
                        self.stdout.write(self.style.WARNING(f'Failed to create chord for {string_set}. Try a different string set.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating chord: {e}'))
                
            elif root is not None and chord_type is None:
                # Generate all chord types for a specific root
                self.stdout.write(f'Generating V2 voicings for all chord types with root={root}, string_set={string_set}')
                try:
                    chords = voicing_system.generate_all_types_v2(root, string_set)
                    # Filter None values (failed creations)
                    chords = [c for c in chords if c is not None]
                    self.stdout.write(f'Created {len(chords)} V2 chords')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error generating V2 voicings: {e}'))
                
            elif root is None and chord_type is not None:
                # Generate all roots for a specific chord type
                self.stdout.write(f'Generating V2 voicings for all roots with chord_type={chord_type}, string_set={string_set}')
                try:
                    chords = voicing_system.generate_all_roots_v2(chord_type, string_set)
                    # Filter None values (failed creations)
                    chords = [c for c in chords if c is not None]
                    self.stdout.write(f'Created {len(chords)} V2 chords')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error generating V2 voicings: {e}'))
                
            else:
                # Generate all V2 chords for all roots and chord types
                self.stdout.write(f'Generating V2 voicings for all roots and chord types with string_set={string_set}')
                try:
                    chords = []
                    for chord_type in voicing_system.chord_types:
                        generated = voicing_system.generate_all_roots_v2(chord_type, string_set)
                        # Filter None values (failed creations)
                        generated = [c for c in generated if c is not None]
                        chords.extend(generated)
                    self.stdout.write(f'Created {len(chords)} V2 chords')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error generating V2 voicings: {e}'))
                
        self.stdout.write(self.style.SUCCESS('Done!'))
