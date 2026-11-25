import os

from django.core.management import call_command
from django.core.management.base import BaseCommand

# The dump is committed to a public repository, so it must never contain
# accounts, sessions or admin history.
EXCLUDED_MODELS = ("auth.user", "sessions.session", "admin.logentry")


class Command(BaseCommand):
    """Management command; see ``help`` for details."""

    help = "Creates a database dump in the Django fixture format at positionfinder/fixtures/databasedump.json."

    def handle(self, *args, **options) -> None:
        """Dump the database to the default fixture file."""
        output_path = os.path.join("positionfinder", "fixtures", "databasedump.json")
        self.stdout.write(f"Backing up database to {output_path}...")
        call_command(
            "dumpdata",
            "--natural-foreign",
            "--natural-primary",
            *(f"--exclude={model}" for model in EXCLUDED_MODELS),
            "--indent",
            "2",
            "--output",
            output_path,
        )
        self.stdout.write(self.style.SUCCESS(f"Database backup complete: {output_path}"))
