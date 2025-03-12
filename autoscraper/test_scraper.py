#!/usr/bin/env python3
"""
AutoScraper - Test Script

This module provides a simple way to test the AutoScraper functionality.
It performs a Google search, extracts information, and displays the results.
"""

import asyncio
import sys
import os
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from autoscraper.scraper import GoogleScraper

# Initialize Rich console for better output
console = Console()

async def test_scraper():
    """Test the scraper with a predefined search query."""
    # Set the search query and number of pages
    query = "tandarts amsterdam"  # Dutch for "dentist amsterdam"
    num_pages = 1
    
    console.print("Initializing scraper...", style="bold blue")
    scraper = GoogleScraper()
    
    # Create debug directory
    os.makedirs('debug', exist_ok=True)
    
    console.print(f"Searching Google for: [bold]{query}[/bold]")
    console.print(f"Number of pages: [bold]{num_pages}[/bold]")
    
    # Add some delay to simulate human behavior
    console.print("Waiting 5 seconds before starting...", style="yellow")
    await asyncio.sleep(5)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        # Create a progress task
        search_task = progress.add_task("Searching Google...", total=1)
        
        # Perform the search
        start_time = time.time()
        await scraper.search_google(query, num_pages)
        progress.update(search_task, completed=1)
        
        # Display search results
        if scraper.urls_to_scrape:
            console.print(f"\n[bold green]Found {len(scraper.urls_to_scrape)} unique URLs:[/bold green]")
            for i, (company_name, url) in enumerate(list(scraper.urls_to_scrape)[:5], 1):
                console.print(f"  {i}. [cyan]{company_name}[/cyan] - {url}")
            
            if len(scraper.urls_to_scrape) > 5:
                console.print(f"  ... and {len(scraper.urls_to_scrape) - 5} more")
                
            # Process the URLs
            process_task = progress.add_task("Processing websites...", total=len(scraper.urls_to_scrape))
            
            # Set up progress callback
            async def progress_callback(current, total):
                progress.update(process_task, completed=current)
            
            # Process URLs with progress
            scraper.set_progress_callback(progress_callback)
            await scraper.process_urls()
            
            # Display the results
            console.print(f"\n[bold green]Found {len(scraper.companies)} companies with contact info:[/bold green]")
            for i, company in enumerate(scraper.companies[:5], 1):
                console.print(f"  {i}. [cyan]{company['name']}[/cyan]")
                if 'email' in company:
                    console.print(f"     Email: [yellow]{company['email']}[/yellow]")
                console.print(f"     URL: {company['website']}")
                
            if len(scraper.companies) > 5:
                console.print(f"  ... and {len(scraper.companies) - 5} more")
            
            # Save results
            if scraper.companies:
                filename = scraper.save_results(query)
                console.print(f"\n[bold]Results saved to:[/bold] {filename}")
        else:
            console.print("\n[bold yellow]No URLs found. Possible reasons:[/bold yellow]")
            console.print("  - Google may be blocking automated access")
            console.print("  - The search query returned no results")
            console.print("  - There was an error parsing the search results")
            console.print("\nCheck the debug file debug/google_page_1.html for the actual response from Google.")
    
    total_time = time.time() - start_time
    console.print(f"\n[bold]Total processing time:[/bold] {total_time:.2f} seconds")

def main():
    """Main entry point for the test script."""
    console.rule("[bold blue]AutoScraper - Test Script[/bold blue]")
    
    try:
        asyncio.run(test_scraper())
    except KeyboardInterrupt:
        console.print("\n[bold red]Operation cancelled by user[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc(), style="red")
        sys.exit(1)

if __name__ == "__main__":
    main() 