from django.core.management.base import BaseCommand
from positionfinder.models_chords import ChordNotes, ChordPosition

class Command(BaseCommand):
    help = 'Deletes duplicate entries in ChordNotes and ChordPosition'

    def handle(self, *args, **kwargs):
        # Deleting duplicates in ChordNotes (using only type_name, chord_name, and range)
        unique_chords = set()
        duplicates_chords = []

        for chord in ChordNotes.objects.all():
            identifier = (
                chord.type_name, chord.chord_name, chord.range
            )
            if identifier in unique_chords:
                duplicates_chords.append(chord.id)
            else:
                unique_chords.add(identifier)

        ChordNotes.objects.filter(id__in=duplicates_chords).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {len(duplicates_chords)} duplicate chord(s) (by type_name, chord_name, range)."))

        # Delete every V2 chord that is not Maj7
        v2_nonmaj7 = ChordNotes.objects.filter(type_name="V2").exclude(chord_name__iexact="Major 7")
        count_v2_nonmaj7 = v2_nonmaj7.count()
        v2_nonmaj7.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count_v2_nonmaj7} V2 chords that are not Major 7."))

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