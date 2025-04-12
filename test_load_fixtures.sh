#!/bin/bash

# Exit on error
set -e

# Display what's happening
echo "Testing fixture loading..."

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate conda environment if available
if command -v conda &> /dev/null; then
    echo "Activating conda environment 'fretboard'..."
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate fretboard || echo "Could not activate conda environment, proceeding with system Python..."
fi

# First check if the fixture files exist
if [ ! -f "fixtures/scaleData.json" ] || [ ! -f "fixtures/chordData.json" ]; then
    echo "Fixture files not found. Please run the pre-push-dump.sh script first."
    exit 1
fi

# Test loading the fixtures (with --dry-run to not actually modify the database)
echo "Testing scale data loading..."
python manage.py loaddata fixtures/scaleData.json --dry-run

echo "Testing chord data loading..."
python manage.py loaddata fixtures/chordData.json --dry-run

if [ -f "fixtures/commonData.json" ]; then
    echo "Testing common data loading..."
    python manage.py loaddata fixtures/commonData.json --dry-run
fi

echo "All fixture files appear to be valid JSON and compatible with loaddata!"
echo "To actually load the data (which will replace existing data), run:"
echo "python manage.py loaddata fixtures/scaleData.json fixtures/chordData.json fixtures/commonData.json"
