# Generated by Django 3.1.3 on 2020-11-30 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('positionfinder', '0007_auto_20201122_0406'),
    ]

    operations = [
        migrations.AddField(
            model_name='notes',
            name='chords',
            field=models.CharField(blank=True, max_length=24),
        ),
    ]
