#!/bin/bash
# Fretboard Project Activation Script

cd "$(dirname "$0")"
source venv/bin/activate
echo "🎸 Fretboard environment activated!"
echo "Python: $(which python)"
echo "Django version: $(python -c 'import django; print(django.get_version())')"
echo ""
echo "To start server: python manage.py runserver 0.0.0.0:8080"
echo "To deactivate: deactivate"
