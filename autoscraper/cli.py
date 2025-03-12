#!/usr/bin/env python3
"""
AutoScraper - Command Line Interface

This module provides a command-line interface to the AutoScraper functionality.
"""

import asyncio
import argparse
import sys
import os
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
import typer
from typing import Optional

from autoscraper.scraper import GoogleScraper, EmailSender

# Initialize Rich console for better output
console = Console()

# Initialize Typer app
app = typer.Typer(help="AutoScraper - Find business contact information from Google searches")

def print_banner():
    """Print the program banner."""
    banner = r"""
    ___         __       _____                                
   /   | __  __/ /_____/ ___/______________ _____  ___  _____
  / /| |/ / / / __/ __ \__ \/ ___/ ___/ __ `/ __ \/ _ \/ ___/
 / ___ / /_/ / /_/ /_/ /__/ / /__/ /  / /_/ / /_/ /  __/ /    
/_/  |_\__,_/\__/\____/____/\___/_/   \__,_/ .___/\___/_/     
                                          /_/                 
                                          
  The Advanced Google Scraper & Contact Finder
  v1.0.0
  """
    console.print(banner, style="bold blue")

async def run_scraper(query: str, num_pages: int, output: Optional[str] = None, 
                      send_emails: bool = False, email_template: str = "introduction_email"):
    """Run the scraper with command line arguments."""
    scraper = GoogleScraper()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        # Create a progress bar for the search
        search_task = progress.add_task(f"Searching Google for: {query}", total=num_pages)
        
        # Perform the search
        start_time = time.time()
        await scraper.search_google(query, num_pages)
        progress.update(search_task, completed=num_pages)
        
        # Display search results
        if scraper.urls_to_scrape:
            console.print(f"\n[bold green]Found {len(scraper.urls_to_scrape)} unique URLs[/bold green]")
            
            # Process the URLs
            process_task = progress.add_task("Processing websites to extract contact information", 
                                            total=len(scraper.urls_to_scrape))
            
            # Set up progress callback
            async def progress_callback(current, total):
                progress.update(process_task, completed=current)
            
            # Process URLs
            scraper.set_progress_callback(progress_callback)
            await scraper.process_urls()
            
            # Display the results
            console.print(f"\n[bold green]Found {len(scraper.companies)} companies with contact information[/bold green]")
            
            # Save results
            if output:
                output_file = output
            else:
                output_file = scraper.save_results(query)
            
            console.print(f"\n[bold]Results saved to:[/bold] {output_file}")
            
            # Send emails if requested
            if send_emails:
                if len(scraper.companies) == 0:
                    console.print("\n[bold red]No companies found, cannot send emails[/bold red]")
                    return
                
                email_task = progress.add_task(f"Sending {email_template} emails", total=len(scraper.companies))
                
                # Set up email progress callback
                def email_progress_callback(current, total):
                    progress.update(email_task, completed=current)
                
                scraper.set_email_progress_callback(email_progress_callback)
                scraper.send_emails_to_companies(email_template)
                
                console.print("[bold green]Email sending completed[/bold green]")
        else:
            console.print("\n[bold yellow]No URLs found. Possible reasons:[/bold yellow]")
            console.print("  - Google may be blocking automated access")
            console.print("  - The search query returned no results")
            console.print("  - There was an error parsing the search results")
            console.print("\nCheck the debug file debug/google_page_1.html for the actual response from Google.")
    
    total_time = time.time() - start_time
    console.print(f"\n[bold]Total processing time:[/bold] {total_time:.2f} seconds")
    
    return scraper

@app.command()
def search(
    query: str = typer.Argument(..., help="The search query to use for finding businesses"),
    pages: int = typer.Option(3, "--pages", "-p", help="Number of Google search pages to process"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output CSV file path"),
    send_emails: bool = typer.Option(False, "--send-emails", "-e", help="Send emails to discovered contacts"),
    email_template: str = typer.Option(
        "introduction_email", "--email-template", "-t", 
        help="Email template to use"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Search Google and extract business contact information."""
    # Print banner
    print_banner()
    
    # Create debug directory if it doesn't exist
    os.makedirs('debug', exist_ok=True)
    
    # Run the scraper
    try:
        asyncio.run(run_scraper(query, pages, output, send_emails, email_template))
    except KeyboardInterrupt:
        console.print("\n[bold red]Operation cancelled by user[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc(), style="red")
        sys.exit(1)

@app.command()
def templates():
    """List available email templates."""
    print_banner()
    
    templates_dir = os.path.join(os.getcwd(), "templates")
    
    if not os.path.exists(templates_dir):
        console.print("[bold yellow]No templates directory found.[/bold yellow]")
        console.print("Create a 'templates' directory and add your email templates.")
        return
    
    templates = []
    for filename in os.listdir(templates_dir):
        if filename.endswith(".txt"):
            templates.append(filename.replace(".txt", ""))
    
    if templates:
        console.print("\n[bold]Available email templates:[/bold]")
        for template in templates:
            console.print(f"  - {template}")
    else:
        console.print("[bold yellow]No email templates found.[/bold yellow]")
        console.print("Add .txt files to the 'templates' directory.")

def main():
    """Main entry point for the CLI."""
    app()

if __name__ == "__main__":
    main() 