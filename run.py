#!/usr/bin/env python3
"""
AutoScraper - Run Script

This script is the entry point for running the AutoScraper application.
It detects if it's run directly or imported and acts accordingly.
"""

import os
import sys

def run_web_app():
    """Run the web application."""
    from autoscraper.app import start
    print("Starting AutoScraper web application...")
    start()

def run_cli():
    """Run the command-line interface."""
    print("""
    ___         __       _____                                
   /   | __  __/ /_____/ ___/______________ _____  ___  _____
  / /| |/ / / / __/ __ \__ \/ ___/ ___/ __ `/ __ \/ _ \/ ___/
 / ___ / /_/ / /_/ /_/ /__/ / /__/ /  / /_/ / /_/ /  __/ /    
/_/  |_\__,_/\__/\____/____/\___/_/   \__,_/ .___/\___/_/     
                                          /_/                 
                                          
  The Advanced Google Scraper & Contact Finder
  v1.0.0
    """)
    if len(sys.argv) < 2:
        print("Usage: python run.py [command]")
        print("\nCommands:")
        print("  web        Run the web application")
        print("  cli        Run the command-line interface")
        print("  test       Run the test scraper")
        return

    command = sys.argv[1]
    if command == "web":
        run_web_app()
    elif command == "cli":
        # Remove the command argument
        sys.argv.pop(1)
        from autoscraper.cli import main
        main()
    elif command == "test":
        from autoscraper.test_scraper import main
        main()
    else:
        print(f"Unknown command: {command}")
        print("Use 'web', 'cli', or 'test'")

if __name__ == "__main__":
    # Ensure the necessary directories exist
    os.makedirs('debug', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    
    run_cli()
else:
    # When imported, expose the start function
    from autoscraper.app import start 