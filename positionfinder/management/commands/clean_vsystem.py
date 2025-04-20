from django.core.management.base import BaseCommand
from django.db import connection
from positionfinder.models_chords import ChordNotes, ChordPosition

class Command(BaseCommand):
    help = 'Cleans up any v-system related data from the database'

    def handle(self, *args, **kwargs):
        # Delete positions related to v-system chords
        with connection.cursor() as cursor:
            # Remove v-system related data from ChordPosition
            cursor.execute('''
                DELETE FROM positionfinder_chordposition
                WHERE notes_name_id IN (
                    SELECT id FROM positionfinder_chordnotes
                    WHERE type_name LIKE 'V%' OR type_name LIKE 'v%'
                );
            ''')
            position_count = cursor.rowcount
            
            # Delete v-system related chord notes
            cursor.execute('''
                DELETE FROM positionfinder_chordnotes
                WHERE type_name LIKE 'V%' OR type_name LIKE 'v%';
            ''')
            chord_count = cursor.rowcount
            
            # Ensure v-system columns are dropped
            try:
                cursor.execute('''
                    ALTER TABLE positionfinder_chordposition
                    DROP COLUMN IF EXISTS position_type,
                    DROP COLUMN IF EXISTS first_note_voicing,
                    DROP COLUMN IF EXISTS second_note_voicing,
                    DROP COLUMN IF EXISTS third_note_voicing,
                    DROP COLUMN IF EXISTS fourth_note_voicing,
                    DROP COLUMN IF EXISTS fifth_note_voicing,
                    DROP COLUMN IF EXISTS sixth_note_voicing;
                ''')
                column_dropped = True
            except Exception as e:
                column_dropped = False
                self.stdout.write(self.style.ERROR(f'Error dropping columns: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Removed {position_count} positions and {chord_count} chords related to v-system'))
        if column_dropped:
            self.stdout.write(self.style.SUCCESS('Successfully dropped v-system related columns'))
