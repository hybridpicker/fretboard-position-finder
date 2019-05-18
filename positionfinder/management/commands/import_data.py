from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.management import call_command
import json

class Command(BaseCommand):
    args = ''
    help = 'Loads the initial data in to database'

    def handle(self, *args, **options):
        # Your Code
        call_command('loaddata', 'positionfinder/fixtures/databasedump.json')
        result = {'message': "Successfully Loading initial data"}
        return json.dumps(result)
