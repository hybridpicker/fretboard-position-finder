# tests/support/mocks.py
"""
Mock objects and utilities for testing.
"""
from unittest.mock import MagicMock
from positionfinder.models import Notes

# Create a mock Scale model based on Notes
Scale = MagicMock()
Scale.objects = MagicMock()
Scale.objects.filter = Notes.objects.filter
Scale.objects.get = Notes.objects.get
Scale.objects.create = Notes.objects.create
Scale.objects.all = Notes.objects.all
