#!/bin/bash
# Run the unused files test to check if high-confidence unused files 
# have been removed from the project.

echo "Running unused files test..."
echo "This test checks if high-confidence unused files have been removed."

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

# Run the specific test
python3 manage.py test tests.test_unused_files_testcase

# Check if the test passed
if [ $? -eq 0 ]; then
    echo -e "\n✅ Success! All high-confidence unused files have been removed."
else
    echo -e "\n❌ Test failed. Some high-confidence unused files still exist."
    echo "Please run the cleanup script: ./utils/cleanup_unused.sh"
fi
