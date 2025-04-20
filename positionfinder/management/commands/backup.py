from django.core.management.base import BaseCommand
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Creates a database dump in the Django fixture format at positionfinder/fixtures/databasedump.json.'

    def handle(self, *args, **options):
        output_path = os.path.join('positionfinder', 'fixtures', 'databasedump.json')
        self.stdout.write(f'Backing up database to {output_path}...')
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--indent', '2',
            '--output', output_path
        )
        self.stdout.write(self.style.SUCCESS(f'Database backup complete: {output_path}'))
