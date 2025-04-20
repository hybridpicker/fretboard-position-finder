#!/bin/bash
# Script to create a database dump for the fretboard-position-finder project

# Set constants
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DUMP_PATH="$PROJECT_ROOT/positionfinder/fixtures/databasedump.json"
DUMP_DIR="$(dirname "$DUMP_PATH")"

# Ensure the fixtures directory exists
mkdir -p "$DUMP_DIR"

# Echo info
echo "Creating database dump at $DUMP_PATH..."

# Try to find Python from virtualenv first
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"

if [ -f "$VENV_PYTHON" ]; then
    echo "Using virtual environment Python"
    PYTHON="$VENV_PYTHON"
# Try conda as fallback
elif command -v conda &> /dev/null && conda info --envs | grep -q "fretboard"; then
    # Source conda to ensure it's available in this script
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate fretboard
    echo "Activated conda environment: fretboard"
    PYTHON="python"
else
    echo "Warning: Could not find Python in venv or conda environment"
    # Default to system Python
    PYTHON="python3"
    echo "Trying system Python: $PYTHON"
fi

# Create the database dump
cd "$PROJECT_ROOT" && $PYTHON manage.py dumpdata \
    --exclude auth.permission \
    --exclude contenttypes \
    --exclude admin.logentry \
    --exclude sessions.session \
    --indent 4 > "$DUMP_PATH"

# Check if dump was successful
if [ $? -eq 0 ] && [ -f "$DUMP_PATH" ]; then
    echo "✅ Database dump created successfully!"
    echo "  Location: $DUMP_PATH"
    echo "  Size: $(du -h "$DUMP_PATH" | cut -f1)"
    
    # Add the dump to git staging
    git add "$DUMP_PATH"
    
    exit 0
else
    echo "❌ Failed to create database dump!"
    exit 1
fi
