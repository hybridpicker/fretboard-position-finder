#!/bin/bash

# Exit on error
set -e

# Display what's happening
echo "Running pre-push data dump script..."

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create fixtures directory if it doesn't exist
mkdir -p fixtures

# Activate conda environment if available
if command -v conda &> /dev/null; then
    echo "Activating conda environment 'fretboard'..."
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate fretboard || echo "Could not activate conda environment, proceeding with system Python..."
fi

# Try to dump data from PostgreSQL
echo "Attempting to dump data from database..."
if python manage.py dumpdata positionfinder.Notes positionfinder.NotesCategory positionfinder.NotesPosition --indent 4 > fixtures/scaleData.json 2>/dev/null &&
   python manage.py dumpdata positionfinder.ChordPosition positionfinder.ChordNotes --indent 4 > fixtures/chordData.json 2>/dev/null &&
   python manage.py dumpdata positionfinder.Root --indent 4 > fixtures/commonData.json 2>/dev/null; then
    
    echo "Successfully dumped data from database!"
else
    echo "Database dump failed, using existing fixture files instead..."
    
    # Copy existing fixtures to the expected locations
    if [ -f "fixtures/chord_data_clean.json" ]; then
        echo "Copying existing chord data..."
        cp fixtures/chord_data_clean.json fixtures/chordData.json
    fi

    if [ -f "fixtures/fretboard_data_clean.json" ]; then
        echo "Copying existing fretboard data..."
        cp fixtures/fretboard_data_clean.json fixtures/fretboardData.json
    fi

    if [ -f "fixtures/notes_data_clean.json" ]; then
        echo "Copying existing notes data..."
        cp fixtures/notes_data_clean.json fixtures/scaleData.json
    fi
fi

echo "Data backup complete!"

# Add the fixtures to git staging
git add fixtures/*.json

echo "Fixture files have been added to git staging."
echo "You can now continue with your git push or commit the changes first."

# Print a helpful message about psycopg2 if the database dump failed
if [ $? -ne 0 ]; then
    echo ""
    echo "NOTE: If you're having issues with PostgreSQL connections, you might need to reinstall psycopg2:"
    echo "pip uninstall -y psycopg2-binary"
    echo "pip install psycopg2-binary"
    echo ""
    echo "Or try installing psycopg2 from source:"
    echo "pip uninstall -y psycopg2-binary"
    echo "pip install psycopg2"
    echo ""
fi
