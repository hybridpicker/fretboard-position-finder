from django.core.management.base import BaseCommand
from positionfinder.models_chords import ChordNotes

class Command(BaseCommand):
    help = 'Generate Dominant 7, Minor 7, and Minor 7b5 variants from Major 7 chords of a given type.'

    def handle(self, *args, **options):
        chord_type = input('Enter the chord type (e.g., V2, V4, V5): ').strip()
        if not chord_type:
            self.stdout.write(self.style.ERROR('No chord type entered. Exiting.'))
            return

        maj7_chords = ChordNotes.objects.filter(chord_name='Major 7', type_name=chord_type)
        count = maj7_chords.count()
        if count == 0:
            self.stdout.write(self.style.WARNING(f'No Major 7 chords found for type {chord_type}. Please add them to your database.'))
            return

        # Check if all variants already exist for all Maj7 chords
        all_variants_exist = True
        for chord in maj7_chords:
            dom7_exists = ChordNotes.objects.filter(
                category_id=chord.category.id,
                type_name=chord.type_name,
                chord_name='Dominant 7',
                range=chord.range,
                tonal_root=chord.tonal_root
            ).exists()
            min7_exists = ChordNotes.objects.filter(
                category_id=chord.category.id,
                type_name=chord.type_name,
                chord_name='Minor 7',
                range=chord.range,
                tonal_root=chord.tonal_root
            ).exists()
            min7b5_exists = ChordNotes.objects.filter(
                category_id=chord.category.id,
                type_name=chord.type_name,
                chord_name='Minor 7b5',
                range=chord.range,
                tonal_root=chord.tonal_root
            ).exists()
            if not (dom7_exists and min7_exists and min7b5_exists):
                all_variants_exist = False
                break

        if all_variants_exist:
            self.stdout.write(self.style.SUCCESS(f'All variants already exist for Major 7 chords of type {chord_type}. Nothing to do.'))
            return

        # Otherwise, generate missing variants
        for chord in maj7_chords:
            dom7_exists = ChordNotes.objects.filter(
                category_id=chord.category.id,
                type_name=chord.type_name,
                chord_name='Dominant 7',
                range=chord.range,
                tonal_root=chord.tonal_root
            ).exists()
            min7_exists = ChordNotes.objects.filter(
                category_id=chord.category.id,
                type_name=chord.type_name,
                chord_name='Minor 7',
                range=chord.range,
                tonal_root=chord.tonal_root
            ).exists()
            min7b5_exists = ChordNotes.objects.filter(
                category_id=chord.category.id,
                type_name=chord.type_name,
                chord_name='Minor 7b5',
                range=chord.range,
                tonal_root=chord.tonal_root
            ).exists()
            if not (dom7_exists and min7_exists and min7b5_exists):
                chord._generate_chord_variants()
                self.stdout.write(self.style.SUCCESS(f'Generated missing variants for Major 7 chord ID {chord.id} (type {chord_type}).'))
            else:
                self.stdout.write(self.style.WARNING(f'All variants already exist for Major 7 chord ID {chord.id} (type {chord_type}).'))

        self.stdout.write(self.style.SUCCESS(f'Finished generating variants for Major 7 chords of type {chord_type}.'))
