#!/usr/bin/env python3
"""
AutoScraper - Core Scraper Module

This module contains the core functionality for scraping Google search results
and extracting contact information from websites.
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import csv
import time
import json
import os
import random
from urllib.parse import urlparse, quote
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional, Callable, Any, Union

class EmailSender:
    """
    Email sender class for sending emails to contacts.
    
    This class provides methods to connect to an SMTP server, send emails,
    and manage email delivery.
    """
    
    def __init__(self, 
                 smtp_server: str = "smtp.gmail.com", 
                 port: int = 587,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 from_email: Optional[str] = None):
        """
        Initialize the EmailSender.
        
        Args:
            smtp_server: SMTP server address
            port: SMTP server port
            username: SMTP username (optional, falls back to environment variable)
            password: SMTP password (optional, falls back to environment variable)
            from_email: Sender email address (optional, falls back to username)
        """
        self.smtp_server = smtp_server
        self.port = port
        
        # Use environment variables as fallback
        self.sender_email = from_email or username or os.environ.get("EMAIL_USERNAME", "example@gmail.com")
        self.username = username or os.environ.get("EMAIL_USERNAME", "example@gmail.com")
        self.password = password or os.environ.get("EMAIL_PASSWORD", "")
        
        # Test mode for development (doesn't send to real recipients)
        self.test_mode = True
        self.test_email = self.sender_email
        
        # SMTP connection
        self.server = None

    def connect(self) -> None:
        """Establish SMTP connection."""
        if not self.server:
            print("Connecting to SMTP server...")
            self.server = smtplib.SMTP(self.smtp_server, self.port)
            print("Starting TLS...")
            self.server.starttls()
            print("Logging in...")
            self.server.login(self.username, self.password)

    def disconnect(self) -> None:
        """Close SMTP connection."""
        if self.server:
            self.server.quit()
            self.server = None

    def send_email(self, recipient_email: str, subject: str, body: str) -> bool:
        """
        Send an email to a recipient.
        
        Args:
            recipient_email: Email address of the recipient
            subject: Email subject
            body: Email body content
            
        Returns:
            bool: Whether the email was sent successfully
        """
        try:
            if self.test_mode:
                recipient_email = self.test_email
                subject = f"[TEST] {subject}"
            
            print(f"\nSending email to: {recipient_email}")
            
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            if not self.server:
                self.connect()
                
            self.server.sendmail(self.sender_email, recipient_email, msg.as_string())
            print("Email sent successfully")
            return True
                
        except Exception as e:
            print(f"Error sending email: {type(e).__name__}: {str(e)}")
            # Try to reconnect on failure
            self.disconnect()
            return False


class GoogleScraper:
    """
    Google scraper for finding businesses and extracting contact information.
    
    This class provides methods to search Google, extract search results,
    scrape websites for contact information, and send emails to discovered
    contacts.
    """
    
    def __init__(self):
        """Initialize the GoogleScraper."""
        # Common referrers to rotate through
        self.referrers = [
            'https://www.google.com/',
            'https://www.google.nl/',
            'https://www.bing.com/',
            'https://search.yahoo.com/',
            'https://duckduckgo.com/',
        ]
        
        # Enhanced headers to better mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': random.choice(self.referrers),
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Sec-CH-UA': '"Google Chrome";v="120", "Chromium";v="120", "Not=A?Brand";v="24"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
        }
        
        # State tracking
        self.companies = []
        self.urls_to_scrape = set()
        
        # Progress tracking
        self.email_progress = {
            'current': 0,
            'total': 0,
            'status': ''
        }
        
        # Progress callbacks
        self.progress_callback = None
        self.email_progress_callback = None
        
        # Configuration from environment
        self.max_concurrent_scrapes = int(os.environ.get("MAX_CONCURRENT_SCRAPES", "5"))
        self.default_delay = int(os.environ.get("DEFAULT_DELAY", "10"))
    
    def set_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        """
        Set a callback function for progress updates during processing.
        
        Args:
            callback: Function that takes current and total counts
        """
        self.progress_callback = callback
    
    def set_email_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        """
        Set a callback function for progress updates during email sending.
        
        Args:
            callback: Function that takes current and total counts
        """
        self.email_progress_callback = callback

    async def search_google(self, query: str, num_pages: int = 3) -> Set[Tuple[str, str]]:
        """
        Get URLs from Google search concurrently.
        
        Args:
            query: Search query to use
            num_pages: Number of search result pages to process
            
        Returns:
            Set of tuples containing (company_name, url)
        """
        print(f"\nGathering URLs from Google search results...")
        
        # Create a debug directory if it doesn't exist
        os.makedirs('debug', exist_ok=True)
        
        # Wait for a longer initial delay to avoid immediate detection
        initial_delay = random.uniform(3, 7)
        print(f"Waiting {initial_delay:.1f} seconds before starting...")
        await asyncio.sleep(initial_delay)
        
        async def fetch_page(page: int):
            # Security phrases that indicate we've been blocked
            security_phrases = [
                'unusual traffic', 
                'captcha', 
                'robot', 
                'automated', 
                'suspicious activity',
                'security check',
                'human',
                'blocked ip'
            ]
            
            # Construct URL with parameters
            url = (
                f'https://www.google.nl/search'
                f'?q={quote(query)}'
                f'&start={page * 10}'
                f'&num=100'
                f'&hl=nl'
                f'&gl=NL'
            )
            
            # Add random delay between requests (2-5 seconds)
            page_delay = random.uniform(2, 5)
            print(f"Waiting {page_delay:.1f} seconds before fetching page {page + 1}...")
            await asyncio.sleep(page_delay)
            
            try:
                # Rotate headers with random referrer
                current_headers = self.headers.copy()
                current_headers['Referer'] = random.choice(self.referrers)
                
                # Create session with cookies and custom headers
                async with aiohttp.ClientSession() as session:
                    print(f"Fetching page {page + 1}...")
                    async with session.get(url, headers=current_headers) as response:
                        # Check response status
                        print(f"Response status: {response.status}")
                        
                        if response.status == 200:
                            html = await response.text()
                            
                            # Save the HTML for debugging
                            with open(f'debug/google_page_{page + 1}.html', 'w', encoding='utf-8') as f:
                                f.write(html)
                            
                            # Check if we're being blocked
                            html_lower = html.lower()
                            if any(phrase in html_lower for phrase in security_phrases):
                                print(f"Security check detected on page {page + 1}!")
                                print("Google may be blocking automated access.")
                                return []
                            
                            # Parse the HTML
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            results = []
                            
                            # Try multiple selectors as Google's HTML structure may change
                            selectors = [
                                'div.g', 
                                'div.srg div.g', 
                                'div[class="g"]',
                                'div.yuRUbf',
                                'div.tF2Cxc'
                            ]
                            
                            for selector in selectors:
                                elements = soup.select(selector)
                                if elements:
                                    print(f"Found {len(elements)} results with selector: {selector}")
                                    break
                            
                            # Process all the search results
                            for result in elements:
                                try:
                                    link = result.find('a')
                                    if not link:
                                        continue
                                        
                                    href = link.get('href', '')
                                    
                                    # Only process actual links
                                    if not href.startswith('http'):
                                        continue
                                        
                                    # Filter out unwanted domains
                                    if any(x in href.lower() for x in [
                                        'google', 'youtube', 'facebook',
                                        'linkedin', 'twitter', 'instagram',
                                        'zorgkaart', 'independer', 'zoekdokter',
                                        'amazon', 'yelp', 'tripadvisor'
                                    ]):
                                        continue
                                    
                                    # Extract the title/company name
                                    title = result.find('h3')
                                    if not title:
                                        continue
                                        
                                    results.append((title.text.strip(), href))
                                    
                                except Exception as e:
                                    print(f"Error processing result: {str(e)}")
                            
                            return results
                            
                        elif response.status == 429:
                            print("Rate limit exceeded (429). Google is blocking access.")
                            return []
                        elif response.status == 403:
                            print("Access forbidden (403). Google is blocking access.")
                            return []
                        elif response.status == 503:
                            print("Service unavailable (503). Google might be suspecting automated access.")
                            return []
                        else:
                            print(f"Unexpected status code: {response.status}")
                            return []
                            
            except Exception as e:
                print(f"Error on page {page + 1}: {str(e)}")
                return []
        
        # Fetch all pages concurrently
        tasks = [fetch_page(page) for page in range(num_pages)]
        results = await asyncio.gather(*tasks)
        
        # Add all results to urls_to_scrape
        for page_results in results:
            for company_name, href in page_results:
                self.urls_to_scrape.add((company_name, href))
                print(f"Added: {company_name} - {href}")
        
        # Return the set of URLs (company_name, href)
        return self.urls_to_scrape

    async def scrape_website(self, session: aiohttp.ClientSession, company_name: str, url: str) -> Dict[str, Any]:
        """
        Scrape individual website for contact info.
        
        Args:
            session: aiohttp ClientSession to use for requests
            company_name: Name of the company
            url: URL of the company website
            
        Returns:
            Dictionary with company information
        """
        print(f"\nScraping {company_name}: {url}")
        
        # Paths to check for contact info
        contact_paths = [
            '',             # Main page
            '/contact',
            '/contact-us',
            '/contactgegevens',
            '/over-ons',
            '/about',
            '/praktijkinformatie',
            '/locatie',
            '/team'
        ]
        
        try:
            # Process paths concurrently with rate limiting
            path_sem = asyncio.Semaphore(2)  # Check 2 paths at a time per website
            
            async def check_path(path: str) -> Optional[str]:
                async with path_sem:
                    full_url = url.rstrip('/') + '/' + path.lstrip('/')
                    if path == '':
                        full_url = url
                        
                    try:
                        # Add a small delay to avoid overwhelming the server
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                        
                        # Update headers with appropriate referer
                        current_headers = self.headers.copy()
                        current_headers['Referer'] = url if path != '' else random.choice(self.referrers)
                        
                        # Set a timeout to avoid waiting too long
                        timeout = aiohttp.ClientTimeout(total=10)
                        
                        async with session.get(full_url, headers=current_headers, timeout=timeout) as response:
                            if response.status == 200:
                                try:
                                    text = await response.text(encoding='utf-8')
                                except UnicodeDecodeError:
                                    try:
                                        text = await response.text(encoding='latin-1')
                                    except:
                                        return None
                                
                                # Extract emails from the page content
                                emails = self.extract_emails(text)
                                if emails:
                                    return next(iter(emails))
                    except:
                        pass
                    return None
            
            # Create tasks for all paths
            path_tasks = [check_path(path) for path in contact_paths]
            
            # Process all paths and get first email found
            emails = await asyncio.gather(*path_tasks)
            email = next((e for e in emails if e), None)
            
            if email:
                # Create the company data
                company_data = {
                    'name': company_name,
                    'website': url,
                    'email': email
                }
                
                # Add to our list of companies
                self.companies.append(company_data)
                print(f"Found email for {company_name}: {email}")
                return company_data
            else:
                print(f"No email found for {company_name}")
                return None
        
        except Exception as e:
            print(f"Error processing {company_name}: {str(e)}")
            return None

    async def process_urls(self) -> List[Dict[str, Any]]:
        """
        Process the collected URLs concurrently with rate limiting.
        
        Returns:
            List of dictionaries with company information
        """
        if not self.urls_to_scrape:
            print("No URLs to process")
            return []
            
        print(f"\nProcessing {len(self.urls_to_scrape)} websites...")
        
        # Create a semaphore to limit concurrent connections
        sem = asyncio.Semaphore(self.max_concurrent_scrapes)  # Process N websites at a time
        
        # Track progress
        total = len(self.urls_to_scrape)
        current = 0
        
        async with aiohttp.ClientSession() as session:
            async def scrape_with_semaphore(company_name: str, url: str):
                nonlocal current
                
                async with sem:  # Limit concurrent requests
                    result = await self.scrape_website(session, company_name, url)
                    
                    # Update progress
                    current += 1
                    if self.progress_callback:
                        await self.progress_callback(current, total)
                    
                    return result
            
            # Create tasks for all URLs
            tasks = [
                scrape_with_semaphore(company_name, url)
                for company_name, url in self.urls_to_scrape
            ]
            
            # Process all tasks concurrently
            results = await asyncio.gather(*tasks)
            
            # Filter out None results
            return [r for r in results if r]

    def extract_emails(self, text: str) -> Set[str]:
        """
        Extract email addresses from text.
        
        Args:
            text: Text to extract emails from
            
        Returns:
            Set of discovered email addresses
        """
        email_patterns = [
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'(?i)(?:email|e-mail|mail|contact|info):\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'(?i)(?:praktijk|zorg|assistente|info)@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        ]
        
        emails = set()
        for pattern in email_patterns:
            found = re.findall(pattern, text)
            emails.update([e[0] if isinstance(e, tuple) else e for e in found])
        
        # Filter out test/example emails
        return {email for email in emails if not any(x in email.lower() for x in ['example', 'test@', '@example', '@test'])}

    def save_results(self, query: str) -> str:
        """
        Save scraping results to a CSV file.
        
        Args:
            query: The search query used
            
        Returns:
            Filename of the saved results
        """
        # Create results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
        
        # Clean the query to make it filename-safe
        safe_query = re.sub(r'[^a-zA-Z0-9]', '_', query)
        
        # Generate a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create the filename
        filename = f'results/search_results_{safe_query}_{timestamp}.csv'
        
        # Sort companies alphabetically
        self.companies.sort(key=lambda x: x['name'])
        
        # Define CSV fields
        fieldnames = ['Company Name', 'Website', 'Email', 'Scraped Date']
        
        # Write to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(fieldnames)
            
            for company in self.companies:
                writer.writerow([
                    company['name'],
                    company['website'],
                    company['email'],
                    datetime.now().strftime('%Y-%m-%d')
                ])
        
        print("\nSummary:")
        print(f"Total companies with emails found: {len(self.companies)}")
        print(f"Results saved to {filename}")
        
        return filename  # Return filename for use in other functions

    def clean_company_name(self, name: str) -> str:
        """
        Clean company name for professional email use.
        
        Args:
            name: The company name to clean
            
        Returns:
            Cleaned company name
        """
        # Remove common suffixes and location indicators
        removals = [
            '- Jouw tandarts in',
            '- Tandarts in Amsterdam',
            '| Tandarts Amsterdam',
            'Tandarts Amsterdam |',
            '| De tandarts van',
            ': Home - Amsterdam',
            '... - Amsterdam',
            '...',
            'Home -',
            ': Welkom op onze website'
        ]
        
        # First split on common separators and take first part
        for sep in ['|', '-', ':', '•']:
            name = name.split(sep)[0]
        
        # Remove specific phrases
        for text in removals:
            name = name.replace(text, '')
        
        # Clean up whitespace
        name = ' '.join(name.split())
        name = name.strip()
        
        return name

    def send_emails_to_companies(self, template_name: str) -> int:
        """
        Send emails to all companies found.
        
        Args:
            template_name: Name of the email template to use
            
        Returns:
            Number of emails sent successfully
        """
        email_sender = EmailSender()
        emails_sent = 0
        
        # Template variables
        variables = {
            'sender_name': 'John Doe',
            'sender_company': 'Digital Solutions BV',
            'sender_position': 'Business Development Manager',
            'sender_phone': '06-12345678',
            'service_type': 'digitale marketing voor zorginstellingen',
            'industry_type': 'zorgprofessionals',
            'event_name': 'Digital Health Summit 2024',
            'event_date': '15 februari 2024',
            'special_offer': '3 maanden gratis service bij jaarcontract',
            'benefit_metric': '35%',
            'target_metric': 'online vindbaarheid',
            'topic_1': 'Digitale Transformatie in de Zorg',
            'topic_2': 'Patient Journey Optimalisatie',
            'topic_3': 'Online Marketing Strategieën',
            'improvement_area': 'online zichtbaarheid',
            'industry_topic': 'digitale zorginnovatie'
        }
        
        try:
            # Load the template
            template_path = os.path.join('templates', f'{template_name}.txt')
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
                
            # Connect to the email server
            email_sender.connect()
            
            # Setup progress tracking
            total = len(self.companies)
            self.email_progress['total'] = total
                
            # Send emails to all companies
            print("\nSending emails to companies...")
            for i, company in enumerate(self.companies, 1):
                try:
                    # Update progress
                    self.email_progress['current'] = i
                    self.email_progress['status'] = f"Sending email to {company['name']}"
                    
                    if self.email_progress_callback:
                        self.email_progress_callback(i, total)
                    
                    # Clean the company name
                    clean_name = self.clean_company_name(company['name'])
                    
                    # Add company-specific variables
                    company_vars = {
                        **variables,
                        'company_name': clean_name,
                        'location': 'Amsterdam',  # Default location
                        'company_strength': 'uitstekende tandheelkundige zorg',
                        'company_specialty': 'tandheelkunde',
                        'pain_point': 'online vindbaarheid en patiëntwerving'
                    }
                    
                    # Replace all variables in template
                    email_content = template
                    for key, value in company_vars.items():
                        email_content = email_content.replace(f'{{{key}}}', str(value))
                    
                    # Split into subject and body
                    subject, body = email_content.split('\n', 1)
                    subject = subject.replace('Subject: ', '')
                    
                    # Send email
                    success = email_sender.send_email(
                        recipient_email=company['email'],
                        subject=subject.strip(),
                        body=body.strip()
                    )
                    
                    if success:
                        emails_sent += 1
                    
                    # Add a small delay between emails
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Error sending email to {company['name']}: {str(e)}")
                    self.email_progress['status'] = f"Error: {str(e)}"
                    
        except Exception as e:
            print(f"Error sending emails: {str(e)}")
            
        finally:
            # Always disconnect from the email server
            email_sender.disconnect()
            
        return emails_sent 