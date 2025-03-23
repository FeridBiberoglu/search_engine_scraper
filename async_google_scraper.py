import time
import re
import csv
import json
import asyncio
import aiohttp
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Note: pandas not installed. Excel export will be skipped.")
    print("To enable Excel export, install pandas: pip install pandas openpyxl")

async def scrape_google_urls(query, num_results=100, num_pages=1):
    """
    Scrape URLs from Google search results.
    
    Args:
        query (str): The search term to use
        num_results (int): Number of results to request from Google per page (default: 100)
        num_pages (int): Number of pages to scrape (default: 1)
        
    Returns:
        list: A list of URLs from the search results
    """
    # Format the search query for URL
    formatted_query = query.replace(' ', '+')
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    # Initialize the Chrome driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        all_urls = []
        
        for page in range(num_pages):
            # Calculate the start parameter for pagination (0, 100, 200, etc.)
            start = page * min(num_results, 100)
            
            # Add num and start parameters
            search_url = f"https://www.google.com/search?q={formatted_query}&num={min(num_results, 100)}&start={start}"
            
            # Open the search URL
            driver.get(search_url)
            print(f"Navigating to Google search results page {page+1} (starting at result {start+1})...")
            
            # Wait for the page to load
            await asyncio.sleep(5)  # Slightly longer wait for Google to load
            
            # Get the page source and parse with BeautifulSoup
            page_html = driver.page_source
            soup = BeautifulSoup(page_html, 'html.parser')
            
            # Extract URLs for this page
            page_urls = []
            
            # Save HTML for debugging (optional, only save the first page)
            if page == 0:
                with open("google_source.html", "w", encoding="utf-8") as f:
                    f.write(page_html)
                print("Saved HTML source to google_source.html for debugging")
            
            # Try multiple selector strategies to find search results
            print(f"Extracting URLs from page {page+1}...")
            
            # Method 1: Try the original selectors from info.txt
            try:
                organic_results = soup.find("div", {"class": "dURPMd"}).find_all("div", {"class": "Ww4FFb"})
                print(f"Method 1: Found {len(organic_results)} results")
                
                for result in organic_results:
                    try:
                        url = result.find("a").get('href')
                        # Clean URL if necessary
                        if url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]
                        page_urls.append(url)
                    except:
                        continue
            except Exception as e:
                print(f"Method 1 failed: {e}")
            
            # Method 2: Try finding all search result blocks with common classes
            if not page_urls:
                try:
                    # Look for any divs that might contain search results (most common pattern)
                    search_divs = soup.find_all("div", class_="g")
                    print(f"Method 2: Found {len(search_divs)} results")
                    
                    for div in search_divs:
                        try:
                            a_tag = div.find("a")
                            if a_tag and a_tag.get('href'):
                                url = a_tag.get('href')
                                if url.startswith('http'):
                                    page_urls.append(url)
                        except Exception as e:
                            continue
                except Exception as e:
                    print(f"Method 2 failed: {e}")
            
            # Method 3: Try another common pattern
            if not page_urls:
                try:
                    # Try to find all 'a' tags within search results
                    search_results = soup.find_all("div", {"class": "yuRUbf"})
                    print(f"Method 3: Found {len(search_results)} results")
                    
                    for result in search_results:
                        try:
                            url = result.find("a").get('href')
                            if url.startswith('http'):
                                page_urls.append(url)
                        except:
                            continue
                except Exception as e:
                    print(f"Method 3 failed: {e}")
            
            # Method 4: Most generic approach - find all links on the page and filter
            if not page_urls:
                try:
                    all_links = soup.find_all("a")
                    print(f"Method 4: Found {len(all_links)} links")
                    
                    for link in all_links:
                        href = link.get('href')
                        if href and href.startswith('http') and 'google' not in href and '?' in href:
                            # This is likely a search result link
                            if href not in page_urls:
                                page_urls.append(href)
                except Exception as e:
                    print(f"Method 4 failed: {e}")
            
            # Remove Google-related URLs
            page_urls = [url for url in page_urls if 'google.com' not in url]
            
            # Add to the global list
            all_urls.extend(page_urls)
            print(f"Found {len(page_urls)} URLs on page {page+1}")
            
            # Check if we have enough results or if there are no results on this page
            if len(page_urls) == 0:
                print(f"No more results found on page {page+1}, stopping pagination")
                break
                
            # Delay between pages to avoid being detected as a bot (if scraping multiple pages)
            if page < num_pages - 1:
                delay = 3 + (page * 0.5)  # Progressive delay to further reduce detection risk
                print(f"Waiting {delay:.1f} seconds before loading the next page...")
                await asyncio.sleep(delay)
        
        # Remove duplicates
        all_urls = list(dict.fromkeys(all_urls))  # Remove duplicates while preserving order
        
        print(f"Successfully extracted {len(all_urls)} unique URLs from Google search results")
        
        return all_urls
        
    finally:
        # Close the browser safely
        try:
            driver.quit()
        except Exception as e:
            print(f"Note: Could not terminate browser process cleanly, but this is normal. Error: {type(e).__name__}")

async def extract_emails_from_url(session, url, semaphore, timeout=10):
    """
    Extract email addresses from a given URL asynchronously.
    
    Args:
        session: aiohttp ClientSession
        url (str): The URL to scrape for emails
        semaphore: asyncio Semaphore to limit concurrent requests
        timeout (int): Request timeout in seconds
        
    Returns:
        tuple: (url, list of found email addresses, metadata)
    """
    emails = []
    metadata = {
        'pages_checked': 0,
        'status': 'failure',
        'error': None,
        'categorized_emails': {},
        'domain_matches': 0
    }
    
    try:
        # Parse the URL to get domain info
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        base_domain = '.'.join(domain.split('.')[-2:]) if len(domain.split('.')) > 1 else domain
        
        # Common user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        
        # Pages to check for emails
        pages_to_check = [url]  # Start with the main URL
        
        # Also check for common contact pages
        contact_paths = ['contact', 'contact-us', 'contacts', 'contact-ons', 'contact-page', 'contactpage', 'about', 'about-us', 'over-ons']
        for path in contact_paths:
            # Add both http and https versions with www and without
            if domain.startswith('www.'):
                pages_to_check.append(f"https://{domain}/{path}")
            else:
                pages_to_check.append(f"https://www.{domain}/{path}")
                pages_to_check.append(f"https://{domain}/{path}")
        
        # Regular expression for email extraction - more comprehensive
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Email categorization patterns
        email_categories = {
            'contact': ['contact', 'info', 'inquiries', 'enquiries', 'general'],
            'support': ['support', 'help', 'service', 'services', 'customer'],
            'sales': ['sales', 'order', 'orders', 'business', 'marketing'],
            'admin': ['admin', 'administrator', 'webmaster', 'hostmaster', 'postmaster'],
            'personal': ['john', 'jane', 'david', 'mike', 'sarah', 'jennifer'],
            'other': []  # Default category
        }
        
        # Initialize categorized emails dictionary
        categorized_emails = {category: [] for category in email_categories}
        
        # Check all pages for emails (limit to 3 to avoid too many requests)
        for page_index, page_url in enumerate(pages_to_check[:3]):
            try:
                # Use semaphore to limit concurrent requests
                async with semaphore:
                    print(f"Checking for emails on: {page_url}")
                    metadata['pages_checked'] += 1
                    
                    async with session.get(page_url, headers=headers, timeout=timeout) as response:
                        if response.status == 200:
                            # Get the HTML content
                            content = await response.text()
                            
                            # Try to find emails in the HTML content
                            page_emails = re.findall(email_regex, content)
                            
                            # Clean and filter the emails
                            for email in page_emails:
                                # Basic validation to ignore common false positives
                                if (
                                    '.' in email and 
                                    '@' in email and
                                    not email.endswith('.png') and
                                    not email.endswith('.jpg') and
                                    not email.endswith('.gif') and
                                    not email.endswith('.svg') and
                                    not email.endswith('.js') and
                                    not email.endswith('.css') and
                                    len(email) < 100 and
                                    len(email) > 5  # Minimum length for valid email
                                ):
                                    # Enhanced validation
                                    parts = email.split('@')
                                    if len(parts) == 2:
                                        username, domain_part = parts
                                        
                                        # Check for valid username and domain structure
                                        if (
                                            len(username) > 1 and
                                            '.' in domain_part and
                                            domain_part.split('.')[-1] in ['com', 'org', 'net', 'edu', 'io', 'gov', 'co', 'info', 'biz', 'de', 'uk', 'fr', 'es', 'it', 'nl']
                                        ):
                                            # Normalize email to lowercase
                                            email = email.lower()
                                            
                                            # Check if this is a new email
                                            if email not in emails:
                                                emails.append(email)
                                                
                                                # Check if email domain matches website domain
                                                email_domain = email.split('@')[1]
                                                if base_domain in email_domain:
                                                    metadata['domain_matches'] += 1
                                                
                                                # Categorize the email
                                                categorized = False
                                                for category, keywords in email_categories.items():
                                                    for keyword in keywords:
                                                        if keyword in username.lower():
                                                            categorized_emails[category].append(email)
                                                            categorized = True
                                                            break
                                                    if categorized:
                                                        break
                                                
                                                # If not categorized, add to 'other'
                                                if not categorized:
                                                    categorized_emails['other'].append(email)
                
                # Only continue if we haven't found any emails yet
                if emails and page_index > 0:  # Only stop early if we've checked more than the main page
                    break
                    
            except Exception as e:
                print(f"Error checking {page_url}: {str(e)}")
                continue
        
        # Update metadata with categorized emails
        metadata['categorized_emails'] = {k: v for k, v in categorized_emails.items() if v}  # Only include non-empty categories
        metadata['status'] = 'success'
                
    except Exception as e:
        metadata['error'] = str(e)
        print(f"Error extracting emails from {url}: {str(e)}")
    
    # Return the URL, found emails, and metadata
    return url, emails, metadata

async def scrape_websites_for_emails(urls, max_sites=None, max_concurrent=10):
    """
    Scrape multiple websites for email addresses asynchronously.
    
    Args:
        urls (list): List of URLs to scrape
        max_sites (int, optional): Maximum number of sites to check. None means check all sites.
        max_concurrent (int, optional): Maximum number of concurrent requests
        
    Returns:
        list: List of dictionaries with URL and extracted emails
    """
    # Limit the number of sites to check if specified
    if max_sites is not None and max_sites > 0:
        urls = urls[:max_sites]
    
    # Create a semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # Create an aiohttp session for all requests
    async with aiohttp.ClientSession() as session:
        # Create tasks for each URL
        tasks = [extract_emails_from_url(session, url, semaphore) for url in urls]
        
        # Track progress
        total_tasks = len(tasks)
        completed_tasks = 0
        results = []
        
        print(f"\nStarting to check {total_tasks} websites for emails...")
        print(f"Progress: 0/{total_tasks} (0.0%)")
        
        # Wait for all tasks to complete
        for i, task_result in enumerate(asyncio.as_completed(tasks), 1):
            url, emails, metadata = await task_result
            
            data = {"url": url, "emails": emails, "metadata": metadata}
            
            # Print result
            if emails:
                email_count = len(emails)
                print(f"Found {email_count} email{'s' if email_count > 1 else ''} from {url}")
            
            results.append(data)
            
            # Update progress
            completed_tasks += 1
            progress_percent = (completed_tasks / total_tasks) * 100
            print(f"Progress: {completed_tasks}/{total_tasks} ({progress_percent:.1f}%)")
        
        return results

def save_results_to_csv(results, filename="google_results_with_emails.csv"):
    """
    Save the URLs and emails to a CSV file in a clean, structured format.
    
    Args:
        results (list): List of dictionaries containing URLs and their emails
        filename (str): Name of the CSV file to save results to
    """
    # Get current date and time for the report
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare data for export
    export_data = []
    for i, result in enumerate(results, 1):
        # Extract domain from URL
        try:
            domain = urlparse(result['url']).netloc
        except:
            domain = ''
        
        # Prepare email data
        emails = result.get('emails', [])
        email_str = '; '.join(emails) if emails else ''
        has_email = 'Yes' if emails else 'No'
        
        # Get metadata
        metadata = result.get('metadata', {})
        status = metadata.get('status', 'unknown')
        pages_checked = metadata.get('pages_checked', 0)
        error = metadata.get('error', '')
        domain_matches = metadata.get('domain_matches', 0)
        
        # Get categorized emails
        categorized = metadata.get('categorized_emails', {})
        contact_emails = '; '.join(categorized.get('contact', []))
        support_emails = '; '.join(categorized.get('support', []))
        sales_emails = '; '.join(categorized.get('sales', []))
        admin_emails = '; '.join(categorized.get('admin', []))
        personal_emails = '; '.join(categorized.get('personal', []))
        other_emails = '; '.join(categorized.get('other', []))
        
        # Create a comprehensive row
        row = {
            'id': i,
            'url': result['url'],
            'domain': domain,
            'has_email': has_email,
            'email_count': len(emails),
            'domain_match_count': domain_matches,
            'pages_checked': pages_checked,
            'status': status,
            'error': error,
            'contact_emails': contact_emails,
            'support_emails': support_emails,
            'sales_emails': sales_emails,
            'admin_emails': admin_emails,
            'personal_emails': personal_emails,
            'other_emails': other_emails,
            'all_emails': email_str,
            'timestamp': timestamp
        }
        
        export_data.append(row)
    
    # Define field names for CSV
    fieldnames = [
        'id', 
        'url', 
        'domain',
        'has_email',
        'email_count',
        'domain_match_count',
        'pages_checked',
        'status',
        'error',
        'contact_emails',
        'support_emails',
        'sales_emails',
        'admin_emails',
        'personal_emails',
        'other_emails',
        'all_emails', 
        'timestamp'
    ]
    
    # Save as CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in export_data:
            writer.writerow(row)
    
    print(f"\nResults saved to {filename} in a clean, structured format")
    
    # Save as Excel if pandas is available
    if PANDAS_AVAILABLE:
        excel_filename = filename.replace('.csv', '.xlsx')
        try:
            # Convert to pandas DataFrame and save as Excel
            df = pd.DataFrame(export_data)
            
            # Create a Pandas Excel writer
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                # Write main data to a sheet
                df.to_excel(writer, sheet_name='Full Results', index=False)
                
                # Create a summary sheet
                total_sites = len(results)
                sites_with_emails = sum(1 for r in results if r.get('emails'))
                total_emails = sum(len(r.get('emails', [])) for r in results)
                
                # Count emails by category
                all_categorized_emails = {}
                for result in results:
                    metadata = result.get('metadata', {})
                    categorized = metadata.get('categorized_emails', {})
                    for category, emails in categorized.items():
                        if category not in all_categorized_emails:
                            all_categorized_emails[category] = 0
                        all_categorized_emails[category] += len(emails)
                
                # Create summary metrics
                summary_data = {
                    'Metric': [
                        'Date', 
                        'Total websites scraped', 
                        'Websites with emails', 
                        'Success rate', 
                        'Total emails found',
                        'Domain-matching emails',
                        'Average emails per website',
                        'Average emails per website with emails'
                    ],
                    'Value': [
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        total_sites,
                        sites_with_emails,
                        f"{sites_with_emails/total_sites*100:.1f}%" if total_sites > 0 else "0%",
                        total_emails,
                        sum(r.get('metadata', {}).get('domain_matches', 0) for r in results),
                        f"{total_emails/total_sites:.2f}" if total_sites > 0 else "0",
                        f"{total_emails/sites_with_emails:.2f}" if sites_with_emails > 0 else "0"
                    ]
                }
                
                # Add category breakdowns
                for category, count in sorted(all_categorized_emails.items(), key=lambda x: x[1], reverse=True):
                    summary_data['Metric'].append(f'{category.title()} emails')
                    summary_data['Value'].append(count)
                
                # Write summary to a separate sheet
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Create sheets for each category of emails
                for category in ['contact', 'support', 'sales', 'admin', 'personal', 'other']:
                    category_data = []
                    for result in results:
                        try:
                            domain = urlparse(result['url']).netloc
                            metadata = result.get('metadata', {})
                            categorized = metadata.get('categorized_emails', {})
                            emails = categorized.get(category, [])
                            
                            for email in emails:
                                category_data.append({
                                    'Domain': domain,
                                    'URL': result['url'],
                                    'Email': email
                                })
                        except Exception:
                            continue
                    
                    if category_data:
                        pd.DataFrame(category_data).to_excel(
                            writer, 
                            sheet_name=f'{category.title()} Emails', 
                            index=False
                        )
                
                # Create a simple emails-only sheet
                email_data = []
                for result in results:
                    if result.get('emails'):
                        domain = urlparse(result['url']).netloc
                        for email in result.get('emails', []):
                            is_domain_match = any(domain in email for domain in [domain, domain.replace('www.', '')])
                            email_data.append({
                                'Domain': domain,
                                'Email': email,
                                'Domain Match': 'Yes' if is_domain_match else 'No'
                            })
                
                if email_data:
                    pd.DataFrame(email_data).to_excel(writer, sheet_name='All Emails', index=False)
            
            print(f"Excel workbook with multiple sheets saved to {excel_filename}")
        except Exception as e:
            print(f"Warning: Could not save Excel file. Error: {str(e)}")
    
    # Also save a simplified version with just domains and emails for quick reference
    simple_filename = "emails_only.csv"
    with open(simple_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Domain', 'Email', 'Category', 'Domain Match'])
        
        for result in results:
            if result.get('emails'):
                try:
                    domain = urlparse(result['url']).netloc
                    metadata = result.get('metadata', {})
                    categorized = metadata.get('categorized_emails', {})
                    
                    # Flatten categorized emails
                    for category, emails in categorized.items():
                        for email in emails:
                            is_domain_match = email.split('@')[1] in [domain, domain.replace('www.', '')]
                            writer.writerow([
                                domain, 
                                email, 
                                category.title(),
                                'Yes' if is_domain_match else 'No'
                            ])
                except:
                    # Fallback if categorization failed
                    for email in result.get('emails', []):
                        writer.writerow([domain, email, 'Uncategorized', 'Unknown'])
    
    print(f"Simplified email list saved to {simple_filename}")
    
    # Save as JSON for programmatic use
    json_filename = "search_results.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"Raw data saved to {json_filename} for programmatic use")
    
    # Count and report statistics
    total_sites = len(results)
    sites_with_emails = sum(1 for r in results if r.get('emails'))
    total_emails = sum(len(r.get('emails', [])) for r in results)
    
    # Save a summary report
    summary_filename = "email_scraping_summary.txt"
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write(f"Email Scraping Summary\n")
        f.write(f"====================\n\n")
        f.write(f"Date: {timestamp}\n")
        f.write(f"Total websites scraped: {total_sites}\n")
        
        # Calculate percentage safely
        email_percentage = sites_with_emails/total_sites*100 if total_sites > 0 else 0
        f.write(f"Websites with emails: {sites_with_emails} ({email_percentage:.1f}%)\n")
        
        f.write(f"Total emails found: {total_emails}\n")
        
        # Count domain-matching emails
        domain_match_emails = sum(r.get('metadata', {}).get('domain_matches', 0) for r in results)
        domain_match_percentage = domain_match_emails/total_emails*100 if total_emails > 0 else 0
        f.write(f"Domain-matching emails: {domain_match_emails} ({domain_match_percentage:.1f}%)\n")
        
        # Calculate averages safely
        avg_per_site = total_emails/total_sites if total_sites > 0 else 0
        avg_per_site_with_emails = total_emails/sites_with_emails if sites_with_emails > 0 else 0
        
        f.write(f"Average emails per website: {avg_per_site:.2f}\n")
        f.write(f"Average emails per website with emails: {avg_per_site_with_emails:.2f}\n\n")
        
        # Write email breakdown by category
        f.write(f"Email breakdown by category:\n")
        all_categorized_emails = {}
        for result in results:
            metadata = result.get('metadata', {})
            categorized = metadata.get('categorized_emails', {})
            for category, emails in categorized.items():
                if category not in all_categorized_emails:
                    all_categorized_emails[category] = 0
                all_categorized_emails[category] += len(emails)
        
        for category, count in sorted(all_categorized_emails.items(), key=lambda x: x[1], reverse=True):
            percentage = count/total_emails*100 if total_emails > 0 else 0
            f.write(f"- {category.title()}: {count} ({percentage:.1f}%)\n")
        
        f.write(f"\nTop domains with most emails:\n")
        top_domains = sorted(results, key=lambda x: len(x.get('emails', [])), reverse=True)[:10]
        for i, result in enumerate(top_domains, 1):
            if result.get('emails'):
                domain = urlparse(result['url']).netloc
                f.write(f"{i}. {domain}: {len(result['emails'])} emails\n")
    
    print(f"Summary report saved to {summary_filename}")

async def main():
    search_term = input("Enter search term: ")
    print(f"Searching for: {search_term}")
    
    # Ask for the number of search results to request
    try:
        num_results = int(input("\nHow many search results do you want per page? (10-100, default 100): ") or 100)
        num_results = max(10, min(100, num_results))  # Limit between 10 and 100
    except ValueError:
        num_results = 100
        
    # Ask for the number of pages to scrape
    try:
        num_pages = int(input("\nHow many pages of Google search results do you want to scrape? (1-10, default 1): ") or 1)
        num_pages = max(1, min(10, num_pages))  # Limit between 1 and 10
    except ValueError:
        num_pages = 1
    
    # Get URLs from Google search results
    urls = await scrape_google_urls(search_term, num_results, num_pages)
    
    print(f"\nFound {len(urls)} URLs:")
    for i, url in enumerate(urls, 1):
        print(f"{i}. {url}")
    
    # Ask user if they want to proceed with email extraction
    proceed = input("\nDo you want to extract emails from these websites? (y/n): ").lower()
    
    if proceed == 'y':
        # Use default values instead of prompting
        max_sites = None  # Check all sites by default
        max_concurrent = 15  # Default to 15 concurrent requests for good performance
        
        print(f"\nUsing optimized default settings:")
        print(f"- Checking all {len(urls)} websites")
        print(f"- Using 15 concurrent requests for maximum speed")
        print(f"- Checking up to 3 pages per website (main page + contact pages)")
        print("\nStarting email extraction...")
        
        # Start time
        start_time = time.time()
        
        # Scrape websites for emails
        results = await scrape_websites_for_emails(urls, max_sites, max_concurrent)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Count total emails found
        total_emails = sum(len(result['emails']) for result in results)
        print(f"\nTotal emails found: {total_emails}")
        print(f"Time taken: {elapsed_time:.2f} seconds")
        
        # Save results to CSV
        save_results_to_csv(results)
        
        # Also write URLs to a text file (original functionality)
        with open("google_urls.txt", "w") as f:
            for url in urls:
                f.write(f"{url}\n")
        print(f"URLs saved to google_urls.txt")
    else:
        # Just write URLs to a text file without scraping for emails
        with open("google_urls.txt", "w") as f:
            for url in urls:
                f.write(f"{url}\n")
        print(f"\nURLs saved to google_urls.txt")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 