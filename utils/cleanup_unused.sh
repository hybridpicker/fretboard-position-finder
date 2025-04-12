#!/bin/bash
# Cleanup script for removing unused JavaScript and CSS files
# Generated on: $(date)

# Change to the project directory
cd "$(dirname "$0")/.."

# Check for conda environment first
if command -v conda &> /dev/null; then
    echo "Activating conda environment 'fretboard'..."
    # Use eval to work around potential conda initialization issues
    eval "$(conda shell.bash hook)"
    conda activate fretboard
# Fall back to venv if conda is not available
elif [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the test first to see what needs to be cleaned up
echo "Running the unused files test to check what needs to be cleaned..."
python3 manage.py test positionfinder.test_unused_files.UnusedFilesTestCase.test_high_confidence_files_removed -v 2

# Create backup directory
BACKUP_DIR="$HOME/Coding/Django/fretboard-position-finder/static/backup_$(date +%Y%m%d)"
mkdir -p "${BACKUP_DIR}/js"
mkdir -p "${BACKUP_DIR}/css"

# Files to delete (high confidence)
JS_FILES=(
  "base_fixed.js"
  "c_major_final_fix.js"
  "c_major_fix.js"
  "c_major_fix_v2.js"
  "chord_note_autofix.js"
  "chord_ui_enhancements_fixed.js"
  "debug-helpers.js"
  "direct_keyboard_fix.js"
  "fixed-chord-inversions.js"
  "installHook.js"
  "keyboard_navigation_fix.js"
  "root_note_fix.js"
)

CSS_FILES=(
  "minimal-chord-ui.css"
)

echo "=== Starting cleanup of unused files ==="
echo "Backing up files to ${BACKUP_DIR}"

# Backup and delete JS files
for file in "${JS_FILES[@]}"; do
  src="$HOME/Coding/Django/fretboard-position-finder/static/js/${file}"
  if [ -f "$src" ]; then
    echo "Processing: ${file}"
    cp "$src" "${BACKUP_DIR}/js/"
    rm "$src"
    echo "  ✓ Backed up and removed"
  else
    echo "  ! File not found: ${file}"
  fi
done

# Backup and delete CSS files
for file in "${CSS_FILES[@]}"; do
  src="$HOME/Coding/Django/fretboard-position-finder/static/css/${file}"
  if [ -f "$src" ]; then
    echo "Processing: ${file}"
    cp "$src" "${BACKUP_DIR}/css/"
    rm "$src"
    echo "  ✓ Backed up and removed"
  else
    echo "  ! File not found: ${file}"
  fi
done

echo "=== Cleanup complete ==="
echo "Files have been backed up to ${BACKUP_DIR}"
echo "If you need to restore any files, you can find them in the backup directory."

# Run the test again to verify cleanup
echo -e "\nVerifying cleanup was successful..."
python3 manage.py test positionfinder.test_unused_files.UnusedFilesTestCase.test_high_confidence_files_removed -v 2

if [ $? -eq 0 ]; then
    echo -e "\n✅ Success! All high-confidence unused files have been removed."
else
    echo -e "\n❌ Verification failed. Some files may not have been removed correctly."
    echo "Please check the output above for details."
fi
