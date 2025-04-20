#!/bin/bash
# This script creates a database dump for the Django project

# Activate the correct conda environment
source ~/anaconda3/etc/profile.d/conda.sh
conda activate fretboard

# Navigate to the project root (if needed, adjust path)
PROJECT_ROOT="$(dirname "$0")/.."
cd "$PROJECT_ROOT"

# Run the Django backup command
python manage.py backup
