#!/bin/bash

# Script to back up and remove old JavaScript files that are no longer needed
# after implementing the unified fretboard architecture
# Created by Cascade AI Assistant

# Create backup directory
BACKUP_DIR="./static/js/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "Created backup directory: $BACKUP_DIR"

# Files to be removed (primary files replaced by unified architecture)
PRIMARY_FILES=(
  "static/js/fretboard_chords.2.1.0.js"
  "static/js/fretboard_scales.2.1.0.js"
)

# Obsolete files that were used by or extended the primary files
OBSOLETE_FILES=(
  "static/js/chord-inversions.js"
  "static/js/chord_debug.js"
  "static/js/chord_debug_notes.js"
  "static/js/scale_arpeggio_debug.js"
  "static/js/fretboard_optimizer.js"
  "static/js/optimized/chord-view-controller-part3.js"
  "static/js/optimized/chord-view-utils.js"
)

# Back up and remove primary files
for file in "${PRIMARY_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "Backing up $file"
    cp "$file" "$BACKUP_DIR/$(basename "$file")"
    echo "Removing $file"
    rm "$file"
  else
    echo "File not found: $file"
  fi
done

# Back up and remove obsolete files
for file in "${OBSOLETE_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "Backing up $file"
    cp "$file" "$BACKUP_DIR/$(basename "$file")"
    echo "Removing $file"
    rm "$file"
  else
    echo "File not found: $file"
  fi
done

echo "Backup completed. All files have been copied to $BACKUP_DIR"
echo "Remove operations are now enabled."
echo "Files have been deleted as requested."
