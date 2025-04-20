#!/usr/bin/env python3
"""
Script to create a database dump using the Django management command 'backup'.
This will output to positionfinder/fixtures/databasedump.json.
"""
import subprocess
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Activate conda environment (if running from shell, otherwise assume active)
# If you want to ensure the environment is active, run this script from an activated shell.

os.chdir(PROJECT_ROOT)

try:
    result = subprocess.run([
        sys.executable, 'manage.py', 'backup'
    ], check=True)
    print("Database backup completed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error during backup: {e}")
    sys.exit(1)
