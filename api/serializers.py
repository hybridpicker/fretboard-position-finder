from rest_framework import serializers
from positionfinder.models_chords import ChordNotes, ChordPosition

class ChordPositionSerializer(serializers.ModelSerializer):
    """Serializer for chord positions."""
    class Meta:
        model = ChordPosition
        fields = ['inversion_order', 'first_note', 'second_note', 'third_note', 'fourth_note']

class ChordNotesSerializer(serializers.ModelSerializer):
    """Serializer for chord notes."""
    positions = ChordPositionSerializer(source='chordposition_set', many=True, read_only=True)
    
    class Meta:
        model = ChordNotes
        fields = ['id', 'type_name', 'chord_name', 'range', 'positions']

class VoicingSerializer(serializers.Serializer):
    """Serializer for chord voicings."""
    frets = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=24)
    )
    intervals = serializers.ListField(
        child=serializers.CharField(max_length=10)
    )
    score = serializers.FloatField(min_value=0, max_value=1.0)
    playable = serializers.BooleanField()

class ChordVoicingResponseSerializer(serializers.Serializer):
    """Serializer for chord voicing API responses."""
    voicing_group = serializers.CharField(max_length=10)
    instrument = serializers.CharField(max_length=10)
    string_set = serializers.CharField(max_length=10)
    chord = serializers.CharField(max_length=30)
    voicings = VoicingSerializer(many=True)
