from django.core.management.base import BaseCommand
from positionfinder.optimized_chords import create_optimized_chord_voicings, add_eighth_string_voicings, add_8string_specific_ranges
from positionfinder.models import NotesCategory
from positionfinder.models_chords import ChordNotes, ChordPosition

class Command(BaseCommand):
    help = 'Creates or updates optimized chord voicings for better playability and 8-string support'

    def add_arguments(self, parser):
        parser.add_argument(
            '--eight-string',
            action='store_true',
            help='Add 8-string specific voicings',
        )
        parser.add_argument(
            '--standard',
            action='store_true',
            help='Add standard 6-string voicings',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all available chord types',
        )
        parser.add_argument(
            '--count',
            action='store_true',
            help='Count voicings for each chord type',
        )
        parser.add_argument(
            '--ranges',
            action='store_true',
            help='Show 8-string specific ranges to add',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all chord voicings before adding new ones',
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_chord_types()
            return

        if options['count']:
            self.count_voicings()
            return
            
        if options['ranges']:
            add_8string_specific_ranges()
            return

        if options['reset']:
            self.reset_chords()

        if options['standard'] or not (options['eight-string'] or options['standard']):
            self.stdout.write(self.style.SUCCESS('Creating optimized standard chord voicings'))
            create_optimized_chord_voicings()
            self.stdout.write(self.style.SUCCESS('Successfully created standard chord voicings'))

        if options['eight-string']:
            self.stdout.write(self.style.SUCCESS('Adding 8-string specific chord voicings'))
            add_eighth_string_voicings()
            self.stdout.write(self.style.SUCCESS('Successfully added 8-string chord voicings'))
            
        # Count voicings after adding
        self.count_voicings()

    def list_chord_types(self):
        """List all available chord types in the database"""
        chords_category = NotesCategory.objects.get(category_name='Chords')
        chord_types = ChordNotes.objects.filter(category=chords_category).values_list('chord_name', flat=True).distinct()
        
        self.stdout.write(self.style.SUCCESS(f'Found {len(chord_types)} chord types:'))
        for chord_type in sorted(chord_types):
            self.stdout.write(f'- {chord_type}')

    def count_voicings(self):
        """Count voicings for each chord type"""
        chords_category = NotesCategory.objects.get(category_name='Chords')
        chord_types = ChordNotes.objects.filter(category=chords_category).values_list('chord_name', flat=True).distinct()
        
        self.stdout.write(self.style.SUCCESS('Voicing counts for each chord type:'))
        
        for chord_type in sorted(chord_types):
            voicing_count = ChordNotes.objects.filter(chord_name=chord_type).count()
            # Count how many have 8-string specific ranges
            eight_string_count = ChordNotes.objects.filter(
                chord_name=chord_type, 
                first_note_string__in=['lowBString', 'highAString']
            ).count() + ChordNotes.objects.filter(
                chord_name=chord_type, 
                second_note_string__in=['lowBString', 'highAString']
            ).count() + ChordNotes.objects.filter(
                chord_name=chord_type, 
                third_note_string__in=['lowBString', 'highAString']
            ).count() + ChordNotes.objects.filter(
                chord_name=chord_type, 
                fourth_note_string__in=['lowBString', 'highAString']
            ).count()
            
            if eight_string_count > 0:
                self.stdout.write(f'{chord_type}: {voicing_count} voicings (including {eight_string_count} 8-string specific)')
            else:
                self.stdout.write(f'{chord_type}: {voicing_count} voicings')
                
    def reset_chords(self):
        """Reset all chord voicings"""
        chords_category = NotesCategory.objects.get(category_name='Chords')
        count = ChordNotes.objects.filter(category=chords_category).count()
        ChordNotes.objects.filter(category=chords_category).delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} chord voicings'))
