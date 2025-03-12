#!/usr/bin/env python3
"""
Example of sending emails with the AutoScraper package.

This script demonstrates how to use the EmailSender class to send
emails to contacts discovered by the GoogleScraper.
"""

import asyncio
import os
import sys
import time
from datetime import datetime

# Add the parent directory to sys.path to import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from autoscraper.scraper import GoogleScraper, EmailSender

async def main():
    """Run a search and send test emails to discovered contacts."""
    print("=" * 60)
    print("AutoScraper - Email Sending Example")
    print("=" * 60)
    
    # Create a GoogleScraper instance
    scraper = GoogleScraper()
    
    # Define the search query and number of pages
    query = "restaurants amsterdam"
    num_pages = 1
    
    print(f"\nSearching for: {query}")
    print(f"Number of pages: {num_pages}")
    
    # Create necessary directories
    os.makedirs('debug', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Check if email templates exist
    template_name = "introduction_email"
    template_path = os.path.join('templates', f'{template_name}.txt')
    
    if not os.path.exists(template_path):
        print(f"\nCreating example template: {template_path}")
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write("""Subject: Introducing Our Services to {company_name}

Dear Team at {company_name},

I hope this email finds you well. My name is {sender_name} from {sender_company}, and I came across your business while researching leading companies in the {industry_type} sector in {location}.

We specialize in {service_type} and have worked with several businesses similar to yours in the {location} area. Our clients have seen an average {benefit_metric} improvement in {target_metric} after working with us.

I would love to schedule a brief 15-minute call to discuss how we might be able to support your business goals. Would you be available sometime next week for a quick conversation?

Thank you for your time, and I look forward to hearing from you.

Best regards,
{sender_name}
{sender_position}
{sender_company}
{sender_phone}
""")
    
    try:
        # Perform the search
        print("\nStep 1: Searching Google...")
        await scraper.search_google(query, num_pages)
        
        print(f"Found {len(scraper.urls_to_scrape)} unique URLs")
        
        # Process the URLs
        print("\nStep 2: Extracting contact information...")
        await scraper.process_urls()
        
        print(f"Found {len(scraper.companies)} companies with contact information")
        
        # Send emails if contact information was found
        if scraper.companies:
            print("\nStep 3: Sending test emails...")
            
            # Configure EmailSender (in test mode)
            email_sender = EmailSender()
            email_sender.test_mode = True  # Ensure test mode is on
            
            # Connect to SMTP server
            try:
                email_sender.connect()
                print("Connected to SMTP server")
                
                # Send emails to each company
                for i, company in enumerate(scraper.companies, 1):
                    print(f"\nSending email {i}/{len(scraper.companies)} to {company['name']}...")
                    
                    # Template variables
                    variables = {
                        'company_name': company['name'],
                        'sender_name': "John Smith",
                        'sender_company': "Example Company",
                        'sender_position': "Business Development Manager",
                        'sender_phone': "123-456-7890",
                        'service_type': "digital marketing services",
                        'industry_type': "restaurant",
                        'location': "Amsterdam",
                        'benefit_metric': "35%",
                        'target_metric': "online visibility"
                    }
                    
                    # Load template
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template = f.read()
                    
                    # Replace template variables
                    email_content = template
                    for key, value in variables.items():
                        email_content = email_content.replace(f'{{{key}}}', str(value))
                    
                    # Split into subject and body
                    subject, body = email_content.split('\n', 1)
                    subject = subject.replace('Subject: ', '')
                    
                    # Send email
                    email_sender.send_email(
                        recipient_email=company['email'],
                        subject=subject.strip(),
                        body=body.strip()
                    )
                    
                    # Add delay between emails
                    if i < len(scraper.companies):
                        time.sleep(1)
                
                print("\nAll test emails sent successfully")
                
            finally:
                # Always disconnect from SMTP server
                email_sender.disconnect()
                print("Disconnected from SMTP server")
        else:
            print("\nNo contact information found, skipping email sending.")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        
    print("\nExample completed.")

if __name__ == "__main__":
    # Run the asyncio event loop
    asyncio.run(main()) 