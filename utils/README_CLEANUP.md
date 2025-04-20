# Cleaning Up Unused Static Files

This directory contains tools to help you identify and safely remove unused JavaScript and CSS files from the project.

## Summary

Our analysis has identified several JavaScript and CSS files that appear to be unused in the project. These tools will help you:

1. Identify unused files
2. Test the application without these files
3. Safely remove the files if they're confirmed to be unnecessary

## The Files

The following files appear to be unused with high confidence:

### JavaScript Files
- base_fixed.js
- c_major_final_fix.js
- c_major_fix.js
- c_major_fix_v2.js
- chord_note_autofix.js
- chord_ui_enhancements_fixed.js
- debug-helpers.js
- direct_keyboard_fix.js
- fixed-chord-inversions.js
- installHook.js
- keyboard_navigation_fix.js
- root_note_fix.js

### CSS Files (Medium Confidence)
- chord-inversion-cycling.css
- cursor-images.css
- minimal-chord-ui.css

## Environment Setup

This project supports both conda and traditional virtual environments:

- **Using conda**: The scripts will automatically try to use the conda environment named `fretboard`
- **Using venv**: If conda is not available, the scripts will check for a `venv` directory

## How to Use These Tools

### Step 0: Run the Test

Run the test to see if your project already has the high-confidence unused files:

```bash
./utils/run_unused_files_test.sh
```

If the test passes, it means all high-confidence unused files have already been removed.
If it fails, it will tell you which files need to be deleted.

### Step 1: Analyze the Project

Run the analysis script to get an updated list of potentially unused files:

```bash
python utils/unused_file_detector.py
```

This will print out lists of files categorized by confidence level, along with a cleanup script.

### Step 2: Test Removing the Files

Use the Django management command to temporarily hide files and test if the application still works:

```bash
# Hide the high-confidence JavaScript files
python manage.py test_unused_files --hide js

# Test the application - make sure everything still works!

# Restore all files when done testing
python manage.py test_unused_files --restore
```

### Step 3: Clean Up

Once you've confirmed the files are safe to remove, use the cleanup script:

```bash
./utils/cleanup_unused.sh
```

This script will:
1. Create a backup of all files before deletion
2. Remove the high-confidence unused files
3. Print a summary of actions taken

## Safety Notes

- Always make sure you have a backup before deleting files
- Test thoroughly after each set of changes
- Consider using a version control system (like git) to track your changes
- Some files might be loaded dynamically or conditionally, so manual testing is critical

## Integration with Git

You can set up a pre-commit hook to automatically check for unused files before each commit:

```bash
# Install the pre-commit hook
cp utils/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

This will prevent commits if high-confidence unused files are detected in your project.

## Integration with CI/CD

You can include the unused files test in your CI/CD pipeline by adding this command to your test suite:

```bash
python manage.py test positionfinder.test_unused_files
```

This will ensure that your codebase stays clean of the identified unused files.

## Further Recommendations

1. Implement a bundling system like webpack to better manage your static assets
2. Add comments to your JavaScript and CSS files indicating their purpose
3. Consider consolidating similar files (especially those with "fix" in the name)
4. Add documentation about which template includes which static files
5. Run the unused files test regularly or include it in your pre-commit hooks
