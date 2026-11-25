#!/bin/bash
# Run all tests to verify our fixes

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

# Run specific tests first
echo "===== Running Unused Files Test ====="
python3 -m pytest tests/unit/test_unused_files.py -v

echo
echo "===== Running Triad Tests ====="
python3 -m pytest tests/unit/test_triads.py -v

echo
echo "===== Running V-System Tests ====="
python3 -m pytest tests/unit/test_v_system.py -v

echo
echo "All tests completed!"
