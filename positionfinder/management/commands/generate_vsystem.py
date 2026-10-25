"""
Management command to generate Ted Greene's V-System voicings.
"""

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from positionfinder.models_chords import ChordNotes
from positionfinder.v_system_generator import VoicingSystem


class Command(BaseCommand):
    """Management command; see ``help`` for details."""

    help = "Generate V-System voicings for the database"

    def add_arguments(self, parser: CommandParser) -> None:
        """Register the command-line options."""
        parser.add_argument(
            "--v-system",
            type=str,
            default="v1",
            help="V-System to generate (v1, v2, or all)",
        )

        parser.add_argument(
            "--root",
            type=int,
            default=None,
            help="Root note (0-11, where 0=C, 1=C#, etc.). If not specified, generates for all roots.",
        )

        parser.add_argument(
            "--chord-type",
            type=str,
            default=None,
            help="Chord type to generate. If not specified, generates for all chord types.",
        )

        parser.add_argument(
            "--string-set",
            type=str,
            default="e-b",
            help="String set to use (e-b, d-E, g-A, e-E, highA-E, e-lowB, highA-lowB)",
        )

        parser.add_argument(
            "--clean",
            action="store_true",
            help="Clean existing V-System chords before generating new ones",
        )

    def handle(self, *args, **options) -> None:
        """Generate (and optionally clean) V-System voicings according to the options."""
        v_system = options["v_system"].lower()
        root = options["root"]
        chord_type = options["chord_type"]
        string_set = options["string_set"]
        clean = options["clean"]

        # Clean existing V-System chords if requested
        if clean:
            self.stdout.write("Cleaning existing V-System chords...")
            with transaction.atomic():
                # Delete positions first (due to foreign key)
                deleted, _ = ChordNotes.objects.filter(type_name__in=["V1", "V2"]).delete()
                self.stdout.write(f"Deleted {deleted} existing V-System chords")

        # Initialize the voicing system
        voicing_system = VoicingSystem()

        # Generate chords based on options
        if v_system == "v1" or v_system == "all":
            chord_type = self._generate_version(voicing_system, "V1", root, chord_type, string_set)

        if v_system == "v2" or v_system == "all":
            chord_type = self._generate_version(voicing_system, "V2", root, chord_type, string_set)

        self.stdout.write(self.style.SUCCESS("Done!"))

    def _generate_version(self, voicing_system, version, root, chord_type, string_set):
        """Generate voicings of one V-System version; returns the (possibly rebound) chord_type."""
        if root is not None and chord_type is not None:
            self._generate_single(voicing_system, version, root, chord_type, string_set)
        elif root is not None and chord_type is None:
            self._generate_all_types(voicing_system, version, root, string_set)
        elif root is None and chord_type is not None:
            self._generate_all_roots(voicing_system, version, chord_type, string_set)
        else:
            chord_type = self._generate_everything(voicing_system, version, chord_type, string_set)
        return chord_type

    def _generate_single(self, voicing_system, version, root, chord_type, string_set):
        """Generate a specific chord."""
        self.stdout.write(
            f"Generating {version} voicing for root={root}, chord_type={chord_type}, string_set={string_set}"
        )
        try:
            generate = getattr(voicing_system, f"generate_{version.lower()}_voicing")
            chord = generate(root, chord_type, string_set)
            if chord:
                self.stdout.write(f"Created chord: {chord}")
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Failed to create chord for {string_set}. Try a different string set."
                    )
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating chord: {e}"))

    def _generate_all_types(self, voicing_system, version, root, string_set):
        """Generate all chord types for a specific root."""
        self.stdout.write(
            f"Generating {version} voicings for all chord types with root={root}, string_set={string_set}"
        )
        try:
            generate = getattr(voicing_system, f"generate_all_types_{version.lower()}")
            chords = generate(root, string_set)
            # Filter None values (failed creations)
            chords = [c for c in chords if c is not None]
            self.stdout.write(f"Created {len(chords)} {version} chords")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error generating {version} voicings: {e}"))

    def _generate_all_roots(self, voicing_system, version, chord_type, string_set):
        """Generate all roots for a specific chord type."""
        self.stdout.write(
            f"Generating {version} voicings for all roots with chord_type={chord_type}, string_set={string_set}"
        )
        try:
            generate = getattr(voicing_system, f"generate_all_roots_{version.lower()}")
            chords = generate(chord_type, string_set)
            # Filter None values (failed creations)
            chords = [c for c in chords if c is not None]
            self.stdout.write(f"Created {len(chords)} {version} chords")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error generating {version} voicings: {e}"))

    def _generate_everything(self, voicing_system, version, chord_type, string_set):
        """Generate all chords for all roots and chord types; returns the last chord_type used."""
        self.stdout.write(
            f"Generating {version} voicings for all roots and chord types with string_set={string_set}"
        )
        try:
            generate = getattr(voicing_system, f"generate_all_roots_{version.lower()}")
            chords = []
            for chord_type in voicing_system.chord_types:
                generated = generate(chord_type, string_set)
                # Filter None values (failed creations)
                generated = [c for c in generated if c is not None]
                chords.extend(generated)
            self.stdout.write(f"Created {len(chords)} {version} chords")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error generating {version} voicings: {e}"))
        return chord_type
