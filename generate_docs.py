#!/usr/bin/env python3
"""
Script to generate documentation for the mst package using lazydocs.
"""

import os
import subprocess
import sys

def generate_docs():
    """Generate markdown documentation for the mst package."""
    # Define the output directory
    output_dir = "./documentation"
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Run lazydocs to generate documentation
    cmd = [
        "lazydocs",
        "--output-path", output_dir,
        "--overview-file", "overview.md",
        "--remove-package-prefix",  # Remove package prefixes from functions
        "mst"
    ]
    
    try:
        print("Generating documentation for mst package...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Documentation generation completed successfully!")
        print(f"Output directory: {output_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during documentation generation: {e}")
        print(f"Stderr: {e.stderr}")
        return False

if __name__ == "__main__":
    success = generate_docs()
    sys.exit(0 if success else 1)