from django.core.management.base import BaseCommand
from positionfinder.optimized_positions import create_optimized_positions, update_specific_scale_positions
from positionfinder.models import Notes, NotesCategory
from positionfinder.positions import NotesPosition

class Command(BaseCommand):
    help = 'Creates or updates optimized scale positions for better playability'

    def add_arguments(self, parser):
        parser.add_argument(
            '--scale',
            help='Specific scale to optimize (e.g., "Major")',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all available scales',
        )
        parser.add_argument(
            '--count',
            action='store_true',
            help='Count positions for each scale',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information',
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_scales()
            return

        if options['count']:
            self.count_positions()
            return

        if options['scale']:
            scale_name = options['scale']
            self.stdout.write(self.style.SUCCESS(f'Optimizing positions for {scale_name} scale'))
            
            # Get scale from database
            try:
                scale = Notes.objects.get(note_name=scale_name, category__category_name='Scales')
                # Call the update function for this specific scale
                from positionfinder.optimized_positions import SCALE_POSITIONS
                if scale_name in SCALE_POSITIONS:
                    success = update_specific_scale_positions(scale_name, SCALE_POSITIONS[scale_name])
                    if success:
                        self.stdout.write(self.style.SUCCESS(f'Successfully updated positions for {scale_name}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'Failed to update positions for {scale_name}'))
                else:
                    self.stdout.write(self.style.ERROR(f'No optimized positions found for {scale_name}'))
            except Notes.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Scale {scale_name} not found'))
        else:
            # Optimize all scales
            self.stdout.write(self.style.SUCCESS('Creating optimized positions for all scales'))
            create_optimized_positions()
            self.stdout.write(self.style.SUCCESS('Successfully created optimized positions'))
            
            # Count positions
            self.count_positions()

    def list_scales(self):
        """List all available scales in the database"""
        scales_category = NotesCategory.objects.get(category_name='Scales')
        scales = Notes.objects.filter(category=scales_category).order_by('note_name')
        
        self.stdout.write(self.style.SUCCESS(f'Found {scales.count()} scales:'))
        for scale in scales:
            self.stdout.write(f'- {scale.note_name}')

    def count_positions(self):
        """Count positions for each scale"""
        scales_category = NotesCategory.objects.get(category_name='Scales')
        scales = Notes.objects.filter(category=scales_category).order_by('note_name')
        
        self.stdout.write(self.style.SUCCESS('Position counts for each scale:'))
        for scale in scales:
            position_count = NotesPosition.objects.filter(notes_name=scale).count()
            self.stdout.write(f'{scale.note_name}: {position_count} positions')
