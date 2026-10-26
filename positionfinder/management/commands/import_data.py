import json

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Management command; see ``help`` for details."""

    args = ""
    help = "Loads the initial data in to database"

    def handle(self, *args, **options) -> str:
        """Flush the database and load the merged fixture."""
        # Your Code
        # Flush the database to remove all data, including content types
        self.stdout.write("Flushing the database...")
        call_command("flush", "--noinput")
        self.stdout.write("Database flushed.")
        # Load the merged fixture containing all data (scales, chords, positions, V-System voicings)
        merged = "positionfinder/fixtures/databasedump.json"
        self.stdout.write(f"Loading fixture: {merged}")
        call_command("loaddata", merged)
        result = {"message": "Successfully Loading initial data"}
        return json.dumps(result)
