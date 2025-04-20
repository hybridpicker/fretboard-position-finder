"""
Create a full database dump of all positionfinder models in JSON format.
This management command creates a comprehensive database dump for backup or migration.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Create a full database dump for all positionfinder models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default='full_database_dump.json',
            help='Output file name (default: full_database_dump.json)',
        )
        parser.add_argument(
            '--indent',
            type=int,
            default=4,
            help='JSON indentation level (default: 4)',
        )
        parser.add_argument(
            '--app',
            default='positionfinder',
            help='App to dump (default: positionfinder)',
        )
        parser.add_argument(
            '--exclude',
            nargs='+',
            help='Models to exclude from the dump',
        )

    def handle(self, *args, **options):
        output_file = options['output']
        indent = options['indent']
        app_name = options['app']
        exclude_models = options['exclude'] or []
        
        # Create fixtures directory if it doesn't exist
        fixtures_dir = 'fixtures'
        if not os.path.exists(fixtures_dir):
            os.makedirs(fixtures_dir)
            self.stdout.write(f"Created directory: {fixtures_dir}")
            
        # Full path to output file
        output_path = os.path.join(fixtures_dir, output_file)
        
        # Create a timestamped backup if file exists
        if os.path.exists(output_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{os.path.splitext(output_path)[0]}_{timestamp}.json"
            os.rename(output_path, backup_file)
            self.stdout.write(f"Created backup: {backup_file}")
        
        # Get all model names from the app
        app_models = []
        for model in apps.get_app_config(app_name).get_models():
            model_name = model.__name__
            if model_name not in exclude_models:
                app_models.append(f"{app_name}.{model_name}")
        
        self.stdout.write(f"Creating dump for the following models: {', '.join(app_models)}")
        
        # Create the dump using Django's dumpdata command
        call_command(
            'dumpdata',
            *app_models,
            indent=indent,
            output=output_path
        )
        
        # Verify file was created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / 1024  # Size in KB
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created database dump at {output_path} ({file_size:.2f} KB)"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR("Failed to create database dump")
            )
