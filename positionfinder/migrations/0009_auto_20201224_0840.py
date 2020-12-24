# Generated by Django 3.1.3 on 2020-12-24 08:40

from django.db import migrations
import positionfinder.notes_choices


class Migration(migrations.Migration):

    dependencies = [
        ('positionfinder', '0008_notes_chords'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notes',
            name='chords',
            field=positionfinder.notes_choices.ChordChoicesField(choices=[('Augmented', 'Augmented'), ('Diminished', 'Diminished'), ('Dominant 7', 'Dominant 7'), ('Major', 'Major'), ('Major 7', 'Major 7'), ('Major7(#5)', 'Major7(#5)'), ('Minor', 'Minor'), ('Minor 7', 'Minor 7'), ('Minor7b5', 'Minor 7b5')], default='Major 7', max_length=20, verbose_name='Chord Name'),
        ),
    ]
