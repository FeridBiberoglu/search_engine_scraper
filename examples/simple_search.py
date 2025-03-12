#!/usr/bin/env python3
"""
Simple example of using the AutoScraper package.

This script demonstrates how to use the GoogleScraper class to search
for businesses, extract contact information, and save the results.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the parent directory to sys.path to import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from autoscraper.scraper import GoogleScraper

async def main():
    """Run a simple search and extraction process."""
    print("=" * 60)
    print("AutoScraper - Simple Search Example")
    print("=" * 60)
    
    # Create a GoogleScraper instance
    scraper = GoogleScraper()
    
    # Define the search query and number of pages
    query = "restaurants amsterdam"
    num_pages = 1
    
    print(f"\nSearching for: {query}")
    print(f"Number of pages: {num_pages}")
    
    # Create debug directory
    os.makedirs('debug', exist_ok=True)
    
    try:
        # Perform the search
        print("\nStep 1: Searching Google...")
        await scraper.search_google(query, num_pages)
        
        print(f"Found {len(scraper.urls_to_scrape)} unique URLs")
        
        # Process the URLs
        print("\nStep 2: Extracting contact information...")
        await scraper.process_urls()
        
        print(f"Found {len(scraper.companies)} companies with contact information")
        
        # Display results
        if scraper.companies:
            print("\nContact Information:")
            for i, company in enumerate(scraper.companies[:5], 1):
                print(f"  {i}. {company['name']}")
                print(f"     Website: {company['website']}")
                print(f"     Email: {company['email']}")
                print()
                
            if len(scraper.companies) > 5:
                print(f"  ... and {len(scraper.companies) - 5} more")
        
            # Save results
            print("\nStep 3: Saving results...")
            filename = scraper.save_results(query)
            print(f"Results saved to: {filename}")
        else:
            print("\nNo contact information found.")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        
    print("\nExample completed.")

if __name__ == "__main__":
    # Run the asyncio event loop
    asyncio.run(main()) 