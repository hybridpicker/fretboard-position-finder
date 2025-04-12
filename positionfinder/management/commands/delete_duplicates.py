from django.core.management.base import BaseCommand
from positionfinder.models_chords import ChordNotes, ChordPosition

class Command(BaseCommand):
    help = 'Deletes duplicate entries in ChordNotes and ChordPosition'

    def handle(self, *args, **kwargs):
        # Deleting duplicates in ChordNotes
        unique_chords = set()
        duplicates_chords = []

        for chord in ChordNotes.objects.all():
            identifier = (
                chord.category_id, chord.type_name, chord.chord_name, chord.range,
                chord.tonal_root, chord.first_note, chord.second_note, chord.third_note,
                chord.fourth_note, chord.fifth_note, chord.sixth_note
            )
            if identifier in unique_chords:
                duplicates_chords.append(chord.id)
            else:
                unique_chords.add(identifier)

        ChordNotes.objects.filter(id__in=duplicates_chords).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {len(duplicates_chords)} duplicate chord(s)."))

        # Deleting duplicates in ChordPosition
        unique_positions = set()
        duplicates_positions = []

        for position in ChordPosition.objects.all():
            identifier = (
                position.notes_name_id, position.inversion_order, position.first_note,
                position.second_note, position.third_note, position.fourth_note,
                position.fifth_note, position.sixth_note
            )
            if identifier in unique_positions:
                duplicates_positions.append(position.id)
            else:
                unique_positions.add(identifier)

        ChordPosition.objects.filter(id__in=duplicates_positions).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {len(duplicates_positions)} duplicate position(s)."))