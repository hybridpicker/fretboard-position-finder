#!/usr/bin/env python
"""
Simple script to check if the Guitar Positions Logo files exist in the expected locations.
This can be run directly without needing Django's test runner.
"""
import os
import sys


def check_logo_files():
    """Check if logo files exist in the expected static directory."""
    # Base directory path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the static/media/logo directory
    logo_dir = os.path.join(base_dir, 'static', 'media', 'logo')
    
    # List of logo files to check
    logo_files = [
        'Guitar_Positions_Logo.svg',
        'Guitar_Positions_Logo_themed.svg',
        'Guitar_Positions_Logo.png'  # Check for PNG version if it exists
    ]
    
    missing_files = []
    existing_files = []
    
    # Check each logo file
    for logo_file in logo_files:
        file_path = os.path.join(logo_dir, logo_file)
        if os.path.exists(file_path):
            existing_files.append(logo_file)
        else:
            missing_files.append(logo_file)
    
    # Print results
    print("\n=== Guitar Positions Logo Check ===")
    
    if existing_files:
        print("\n✅ Found logo files:")
        for file in existing_files:
            file_path = os.path.join(logo_dir, file)
            file_size = os.path.getsize(file_path) / 1024  # Convert to KB
            print(f"  - {file} ({file_size:.1f} KB)")
    
    if missing_files:
        print("\n❌ Missing logo files:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nLogo files should be placed in:")
        print(f"  {logo_dir}")
    
    print("\nSummary:")
    print(f"  - {len(existing_files)} logo files found")
    print(f"  - {len(missing_files)} logo files missing")
    
    # Return success if at least one logo file exists
    return len(existing_files) > 0


if __name__ == "__main__":
    success = check_logo_files()
    # Exit with status code 0 if successful, 1 if no logo files found
    sys.exit(0 if success else 1)
