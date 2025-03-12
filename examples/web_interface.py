#!/usr/bin/env python3
"""
Example of running the AutoScraper web interface.

This script demonstrates how to start the AutoScraper web interface
which provides a user-friendly way to use the scraper functionality.
"""

import os
import sys

# Add the parent directory to sys.path to import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from autoscraper.app import start

def main():
    """Run the web interface."""
    print("=" * 60)
    print("AutoScraper - Web Interface Example")
    print("=" * 60)
    
    print("\nStarting the AutoScraper web interface...")
    print("Once started, you can access it at: http://localhost:8000")
    print("\nPress Ctrl+C to stop the server.")
    
    # Create necessary directories
    os.makedirs('debug', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Start the web interface
    start()

if __name__ == "__main__":
    main() 