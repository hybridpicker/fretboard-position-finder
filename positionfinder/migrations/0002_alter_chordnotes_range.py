from django.db import migrations, models
import positionfinder.string_range_choices

class Migration(migrations.Migration):

    dependencies = [
        ('positionfinder', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chordnotes',
            name='range',
            field=positionfinder.string_range_choices.StringRangeChoicesField(choices=[('A - B', 'A - B'), ('A - lowB', 'A - lowB'), ('E - lowB', 'E - lowB'), ('ELowString - lowB', 'ELowString - lowB'), ('a - A', 'a - A'), ('a - D', 'a - D'), ('a - E', 'a - E'), ('a - b', 'a - b'), ('a - g', 'a - g'), ('b - A', 'b - A'), ('b - B', 'b - B'), ('b - E', 'b - E'), ('b - d', 'b - d'), ('b - lowB', 'b - lowB'), ('bString - lowB', 'bString - lowB'), ('d - B', 'd - B'), ('d - E', 'd - E'), ('d - lowB', 'd - lowB'), ('dString - lowB', 'dString - lowB'), ('e - A', 'e - A'), ('e - B', 'e - B'), ('e - E', 'e - E'), ('e - d', 'e - d'), ('e - g', 'e - g'), ('e - lowB', 'e - lowB'), ('g - A', 'g - A'), ('g - B', 'g - B'), ('g - E', 'g - E'), ('g - lowB', 'g - lowB'), ('highA - A', 'highA - A'), ('highA - AString', 'highA - AString'), ('highA - E', 'highA - E'), ('highA - ELowString', 'highA - ELowString'), ('highA - b', 'highA - b'), ('highA - d', 'highA - d'), ('highA - e', 'highA - e'), ('highA - g', 'highA - g'), ('highA - lowB', 'highA - lowB')], default='e - g', max_length=20, verbose_name='String Range'),
        ),
    ]
