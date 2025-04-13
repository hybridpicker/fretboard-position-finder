from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.management import call_command
import json

from positionfinder.models import Notes;
from positionfinder.positions import NotesPosition;
from positionfinder.models_chords import ChordNotes, ChordPosition;


class Command(BaseCommand):
    args = ''
    help = 'Loads the initial data in to database'

    def handle(self, *args, **options):
        # Your Code
        # Flush the database to remove all data, including content types
        self.stdout.write("Flushing the database...")
        call_command('flush', '--noinput')
        self.stdout.write("Database flushed.")
        #Load Fixtures
        call_command('loaddata', 'positionfinder/fixtures/databasedump.json')
        result = {'message': "Successfully Loading initial data"}
        return json.dumps(result)
