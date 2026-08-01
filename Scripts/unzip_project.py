#!/usr/bin/env python3
"""
Unzip the Unity project archive into the repository root.
Assumes there is exactly one .zip file in the current directory.
"""

import os
import sys
import zipfile
import glob
from pathlib import Path

def unzip_project():
    cwd = Path.cwd()
    zip_files = list(cwd.glob("*.zip"))
    
    if not zip_files:
        print("No .zip file found in current directory.")
        sys.exit(1)
    
    # Use the first zip file (you can be more specific if needed)
    zip_path = zip_files[0]
    print(f"Found archive: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Extract all contents into the current directory, overwriting existing
        zf.extractall(cwd)
    
    print(f"Extracted {zip_path} successfully.")
    # Optionally, remove the zip after extraction to avoid confusion
    # os.remove(zip_path)  # uncomment if you want to clean up

if __name__ == "__main__":
    unzip_project()
