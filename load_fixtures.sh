#!/bin/bash
# Enhanced load_fixtures.sh - Loads all fixtures with better error handling and V2 chord validation

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set text colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}FRETBOARD POSITION FINDER - FIXTURE LOADER${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to check if a command succeeds
check_command() {
  if [ $? -ne 0 ]; then
    echo -e "${RED}Error: $1${NC}"
    if [ "$2" = "exit" ]; then
      exit 1
    fi
    return 1
  fi
  return 0
}

# Try to activate virtual environment
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source venv/bin/activate
    check_command "Failed to activate virtual environment" "continue"
elif command -v conda &> /dev/null; then
    echo -e "${BLUE}Activating conda environment 'fretboard'...${NC}"
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate fretboard || echo -e "${YELLOW}Could not activate conda environment, proceeding with system Python...${NC}"
else
    echo -e "${YELLOW}No virtual environment found, using system Python...${NC}"
fi

# Check which fixture files exist
CHORD_DATA=""
if [ -f "fixtures/chordData.json" ]; then
    CHORD_DATA="fixtures/chordData.json"
elif [ -f "fixtures/chord_data_clean.json" ]; then
    CHORD_DATA="fixtures/chord_data_clean.json"
fi

SCALE_DATA=""
if [ -f "fixtures/scaleData.json" ]; then
    SCALE_DATA="fixtures/scaleData.json"
elif [ -f "fixtures/notes_data_clean.json" ]; then
    SCALE_DATA="fixtures/notes_data_clean.json"
fi

FRETBOARD_DATA=""
if [ -f "fixtures/fretboardData.json" ]; then
    FRETBOARD_DATA="fixtures/fretboardData.json"
elif [ -f "fixtures/fretboard_data_clean.json" ]; then
    FRETBOARD_DATA="fixtures/fretboard_data_clean.json"
fi

COMMON_DATA=""
if [ -f "fixtures/commonData.json" ]; then
    COMMON_DATA="fixtures/commonData.json"
fi

# Check for V2 chords in chord data (if possible)
if [ -n "$CHORD_DATA" ] && command -v python &> /dev/null; then
    echo -e "${BLUE}Checking for V2 chords in $CHORD_DATA...${NC}"
    V2_COUNT=$(python -c "
import json
try:
    with open('$CHORD_DATA', 'r') as f:
        data = json.load(f)
    v2_count = sum(1 for item in data if item.get('model') == 'positionfinder.chordnotes' and item.get('fields', {}).get('type_name') == 'V2')
    print(v2_count)
except Exception as e:
    print('ERROR: ' + str(e))
")

    if [[ $V2_COUNT == ERROR* ]]; then
        echo -e "${YELLOW}Could not check for V2 chords: ${V2_COUNT#ERROR: }${NC}"
    elif [ "$V2_COUNT" -lt 400 ]; then
        echo -e "${YELLOW}Warning: Found only $V2_COUNT V2 chords. Expected at least 400.${NC}"
        echo -e "${YELLOW}Would you like to update the chord fixture to include all V2 chords?${NC}"
        read -p "Update chord fixture? (y/n): " update_fixture
        
        if [ "$update_fixture" = "y" ] || [ "$update_fixture" = "Y" ]; then
            echo -e "${BLUE}Updating chord fixture...${NC}"
            
            # Create backup first
            echo -e "${BLUE}Backing up existing chord fixture...${NC}"
            TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
            mkdir -p fixtures/backups
            cp "$CHORD_DATA" "fixtures/backups/$(basename "$CHORD_DATA")_backup_$TIMESTAMP"
            check_command "Failed to create backup" "continue"
            
            # Update chord fixture
            echo -e "${BLUE}Creating new chord fixture with all V2 chords...${NC}"
            python manage.py dumpdata positionfinder.chordnotes positionfinder.chordposition --indent 2 > "$CHORD_DATA"
            check_command "Failed to update chord fixture" "continue"
            
            # Verify the update
            echo -e "${BLUE}Verifying updated chord fixture...${NC}"
            NEW_V2_COUNT=$(python -c "
import json
try:
    with open('$CHORD_DATA', 'r') as f:
        data = json.load(f)
    v2_count = sum(1 for item in data if item.get('model') == 'positionfinder.chordnotes' and item.get('fields', {}).get('type_name') == 'V2')
    print(v2_count)
except Exception as e:
    print('ERROR: ' + str(e))
")
            if [[ $NEW_V2_COUNT == ERROR* ]]; then
                echo -e "${YELLOW}Could not verify updated fixture: ${NEW_V2_COUNT#ERROR: }${NC}"
            elif [ "$NEW_V2_COUNT" -ge 400 ]; then
                echo -e "${GREEN}Successfully updated chord fixture with $NEW_V2_COUNT V2 chords!${NC}"
            else
                echo -e "${YELLOW}Warning: Updated fixture has only $NEW_V2_COUNT V2 chords.${NC}"
            fi
        fi
    else
        echo -e "${GREEN}Chord fixture contains $V2_COUNT V2 chords. Looks good!${NC}"
    fi
fi

# Ask if user wants to clear existing data
echo -e "${BLUE}Do you want to clear existing data before loading fixtures?${NC}"
echo -e "${YELLOW}WARNING: This will delete ALL data in the selected models!${NC}"
read -p "Clear existing data? (y/n): " clear_data

# Options for what data to load
echo -e "${BLUE}Which data would you like to load?${NC}"
echo "1) All data"
echo "2) Only chord data"
echo "3) Only notes/scales data"
echo "4) Only fretboard data"
if [ -n "$COMMON_DATA" ]; then
    echo "5) Only common data (roots, etc.)"
fi
read -p "Enter your choice (1-5): " choice

# Function to load data with optional clearing
load_data() {
    local model=$1
    local fixture_file=$2
    
    if [ "$clear_data" = "y" ] || [ "$clear_data" = "Y" ]; then
        echo -e "${YELLOW}Clearing existing data for $model...${NC}"
        python manage.py shell -c "from $model import *; $(echo "$model" | cut -d. -f2).objects.all().delete()"
        check_command "Failed to clear data" "continue"
    fi
    
    if [ -n "$fixture_file" ]; then
        echo -e "${BLUE}Loading data from $fixture_file${NC}"
        python manage.py loaddata "$fixture_file"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Successfully loaded $fixture_file${NC}"
        else
            echo -e "${RED}Failed to load $fixture_file${NC}"
        fi
    else
        echo -e "${YELLOW}No fixture file found for $model.${NC}"
    fi
}

case $choice in
  1)
    echo -e "${BLUE}Loading all data...${NC}"
    
    if [ "$clear_data" = "y" ] || [ "$clear_data" = "Y" ]; then
        echo -e "${RED}WARNING: Clearing ALL data in the database!${NC}"
        read -p "Are you sure? This cannot be undone! (y/n): " confirm_clear
        
        if [ "$confirm_clear" = "y" ] || [ "$confirm_clear" = "Y" ]; then
            echo -e "${YELLOW}Clearing database...${NC}"
            python manage.py shell -c "from positionfinder.models import *; from positionfinder.models_chords import *; ChordPosition.objects.all().delete(); ChordNotes.objects.all().delete(); Notes.objects.all().delete(); NotesCategory.objects.all().delete(); Root.objects.all().delete()"
            check_command "Failed to clear database" "continue"
        else
            echo -e "${BLUE}Database clearing cancelled. Continuing with loading data...${NC}"
        fi
    fi
    
    # Load data in proper order (common data first)
    if [ -n "$COMMON_DATA" ]; then
        echo -e "${BLUE}Loading common data from $COMMON_DATA${NC}"
        python manage.py loaddata "$COMMON_DATA"
        check_command "Failed to load common data" "continue"
    fi
    
    if [ -n "$SCALE_DATA" ]; then
        echo -e "${BLUE}Loading scale data from $SCALE_DATA${NC}"
        python manage.py loaddata "$SCALE_DATA"
        check_command "Failed to load scale data" "continue"
    fi
    
    if [ -n "$CHORD_DATA" ]; then
        echo -e "${BLUE}Loading chord data from $CHORD_DATA${NC}"
        python manage.py loaddata "$CHORD_DATA"
        check_command "Failed to load chord data" "continue"
    fi
    
    if [ -n "$FRETBOARD_DATA" ]; then
        echo -e "${BLUE}Loading fretboard data from $FRETBOARD_DATA${NC}"
        python manage.py loaddata "$FRETBOARD_DATA"
        check_command "Failed to load fretboard data" "continue"
    fi
    ;;
    
  2)
    if [ -n "$CHORD_DATA" ]; then
        if [ "$clear_data" = "y" ] || [ "$clear_data" = "Y" ]; then
            echo -e "${YELLOW}Clearing existing chord data...${NC}"
            python manage.py shell -c "from positionfinder.models_chords import *; ChordPosition.objects.all().delete(); ChordNotes.objects.all().delete()"
            check_command "Failed to clear chord data" "continue"
        fi
        
        echo -e "${BLUE}Loading chord data from $CHORD_DATA${NC}"
        python manage.py loaddata "$CHORD_DATA"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Successfully loaded chord data${NC}"
        else
            echo -e "${RED}Failed to load chord data${NC}"
        fi
    else
        echo -e "${YELLOW}No chord data found.${NC}"
    fi
    ;;
    
  3)
    if [ -n "$SCALE_DATA" ]; then
        if [ "$clear_data" = "y" ] || [ "$clear_data" = "Y" ]; then
            echo -e "${YELLOW}Clearing existing scale/notes data...${NC}"
            python manage.py shell -c "from positionfinder.models import *; Notes.objects.all().delete(); NotesCategory.objects.all().delete()"
            check_command "Failed to clear scale data" "continue"
        fi
        
        echo -e "${BLUE}Loading scale data from $SCALE_DATA${NC}"
        python manage.py loaddata "$SCALE_DATA"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Successfully loaded scale data${NC}"
        else
            echo -e "${RED}Failed to load scale data${NC}"
        fi
    else
        echo -e "${YELLOW}No scale data found.${NC}"
    fi
    ;;
    
  4)
    if [ -n "$FRETBOARD_DATA" ]; then
        if [ "$clear_data" = "y" ] || [ "$clear_data" = "Y" ]; then
            echo -e "${YELLOW}Clearing existing fretboard data...${NC}"
            python manage.py shell -c "from positionfinder.models import *; NotesPosition.objects.all().delete()"
            check_command "Failed to clear fretboard data" "continue"
        fi
        
        echo -e "${BLUE}Loading fretboard data from $FRETBOARD_DATA${NC}"
        python manage.py loaddata "$FRETBOARD_DATA"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Successfully loaded fretboard data${NC}"
        else
            echo -e "${RED}Failed to load fretboard data${NC}"
        fi
    else
        echo -e "${YELLOW}No fretboard data found.${NC}"
    fi
    ;;
    
  5)
    if [ -n "$COMMON_DATA" ]; then
        if [ "$clear_data" = "y" ] || [ "$clear_data" = "Y" ]; then
            echo -e "${YELLOW}Clearing existing root data...${NC}"
            python manage.py shell -c "from positionfinder.models import *; Root.objects.all().delete(); NotesCategory.objects.all().delete()"
            check_command "Failed to clear root data" "continue"
        fi
        
        echo -e "${BLUE}Loading common data from $COMMON_DATA${NC}"
        python manage.py loaddata "$COMMON_DATA"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Successfully loaded common data${NC}"
        else
            echo -e "${RED}Failed to load common data${NC}"
        fi
    else
        echo -e "${YELLOW}No common data found.${NC}"
        exit 1
    fi
    ;;
    
  *)
    echo -e "${RED}Invalid choice. Exiting.${NC}"
    exit 1
    ;;
esac

# Verify data was loaded correctly
echo -e "${BLUE}\nVerifying loaded data...${NC}"
python manage.py shell -c "
from positionfinder.models import *
from positionfinder.models_chords import *
import sys

root_count = Root.objects.count()
print(f'Roots: {root_count}')

category_count = NotesCategory.objects.count()
print(f'Note categories: {category_count}')

chord_count = ChordNotes.objects.count()
print(f'Chords: {chord_count}')

v2_chord_count = ChordNotes.objects.filter(type_name='V2').count()
print(f'V2 chords: {v2_chord_count}')

chord_position_count = ChordPosition.objects.count()
print(f'Chord positions: {chord_position_count}')

# Check if we have the right chord types for V2
v2_chord_types = list(ChordNotes.objects.filter(type_name='V2').values_list('chord_name', flat=True).distinct())
print(f'V2 chord types: {sorted(v2_chord_types)}')

# Make sure we have the required chord types
required_types = ['Dominant 7', 'Major 7', 'Minor 7', 'Minor 7b5']
missing = [t for t in required_types if t not in v2_chord_types]
if missing:
    print(f'MISSING REQUIRED CHORD TYPES: {missing}', file=sys.stderr)
else:
    print('All required V2 chord types are present.')
"

echo -e "${GREEN}\nData loading complete!${NC}"
echo -e "${BLUE}========================================${NC}"
