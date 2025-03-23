import time
import re
import csv
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def scrape_google_urls(query):
    """
    Scrape URLs from the first page of Google search results.
    
    Args:
        query (str): The search term to use
        
    Returns:
        list: A list of URLs from the search results
    """
    # Format the search query for URL
    formatted_query = query.replace(' ', '+')
    search_url = f"https://www.google.com/search?q={formatted_query}"
    
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
        # Open the search URL
        driver.get(search_url)
        print("Navigating to Google search page...")
        
        # Wait for the page to load
        time.sleep(3)
        
        # Get the page source and parse with BeautifulSoup
        page_html = driver.page_source
        soup = BeautifulSoup(page_html, 'html.parser')
        
        # Extract URLs
        urls = []
        
        # Save HTML for debugging (optional)
        with open("google_source.html", "w", encoding="utf-8") as f:
            f.write(page_html)
        print("Saved HTML source to google_source.html for debugging")
        
        # Try multiple selector strategies to find search results
        print("Extracting URLs from search results...")
        
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
                    urls.append(url)
                except:
                    continue
        except Exception as e:
            print(f"Method 1 failed: {e}")
        
        # Method 2: Try finding all search result blocks with common classes
        if not urls:
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
                                urls.append(url)
                    except Exception as e:
                        continue
            except Exception as e:
                print(f"Method 2 failed: {e}")
        
        # Method 3: Try another common pattern
        if not urls:
            try:
                # Try to find all 'a' tags within search results
                search_results = soup.find_all("div", {"class": "yuRUbf"})
                print(f"Method 3: Found {len(search_results)} results")
                
                for result in search_results:
                    try:
                        url = result.find("a").get('href')
                        if url.startswith('http'):
                            urls.append(url)
                    except:
                        continue
            except Exception as e:
                print(f"Method 3 failed: {e}")
        
        # Method 4: Most generic approach - find all links on the page and filter
        if not urls:
            try:
                all_links = soup.find_all("a")
                print(f"Method 4: Found {len(all_links)} links")
                
                for link in all_links:
                    href = link.get('href')
                    if href and href.startswith('http') and 'google' not in href and '?' in href:
                        # This is likely a search result link
                        if href not in urls:
                            urls.append(href)
            except Exception as e:
                print(f"Method 4 failed: {e}")
        
        # Remove duplicates and Google-related URLs
        urls = [url for url in urls if 'google.com' not in url]
        urls = list(dict.fromkeys(urls))  # Remove duplicates while preserving order
        
        return urls
        
    finally:
        # Close the browser safely
        try:
            driver.quit()
        except Exception as e:
            print(f"Note: Could not terminate browser process cleanly, but this is normal. Error: {type(e).__name__}")

def extract_emails_from_url(url, timeout=10):
    """
    Extract email addresses from a given URL.
    
    Args:
        url (str): The URL to scrape for emails
        timeout (int): Request timeout in seconds
        
    Returns:
        list: A list of found email addresses
    """
    emails = []
    
    try:
        # Get the domain name for potential contact page check
        domain = urlparse(url).netloc
        
        # Common user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        
        # Pages to check for emails
        pages_to_check = [url]  # Start with the main URL
        
        # Also check for common contact pages
        contact_paths = ['contact', 'contact-us', 'contact-ons', 'contact-page', 'contactpage', 'about', 'about-us', 'over-ons']
        for path in contact_paths:
            # Add both http and https versions with www and without
            if domain.startswith('www.'):
                pages_to_check.append(f"https://{domain}/{path}")
            else:
                pages_to_check.append(f"https://www.{domain}/{path}")
                pages_to_check.append(f"https://{domain}/{path}")
        
        # Regular expression for email extraction
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Check all pages for emails
        for page_url in pages_to_check[:3]:  # Limit to first 3 to avoid too many requests
            try:
                print(f"Checking for emails on: {page_url}")
                response = requests.get(page_url, headers=headers, timeout=timeout)
                
                if response.status_code == 200:
                    # Try to find emails in the HTML content
                    page_emails = re.findall(email_regex, response.text)
                    
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
                            len(email) < 100
                        ):
                            # Normalize email to lowercase
                            email = email.lower()
                            if email not in emails:
                                emails.append(email)
                
                # Only continue if we haven't found any emails yet
                if emails:
                    break
                    
            except Exception as e:
                print(f"Error checking {page_url}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error extracting emails from {url}: {str(e)}")
    
    return emails

def scrape_websites_for_emails(urls, max_sites=None):
    """
    Scrape a list of websites for email addresses.
    
    Args:
        urls (list): List of URLs to check for emails
        max_sites (int): Maximum number of sites to check (None for all)
        
    Returns:
        list: A list of dictionaries containing URLs and their emails
    """
    results = []
    
    # Limit the number of sites to check if specified
    if max_sites:
        urls = urls[:max_sites]
    
    print(f"\nSearching for email addresses on {len(urls)} websites...")
    
    for i, url in enumerate(urls, 1):
        data = {"url": url, "emails": []}
        
        print(f"\n[{i}/{len(urls)}] Checking {url}")
        emails = extract_emails_from_url(url)
        
        if emails:
            data["emails"] = emails
            print(f"  Found {len(emails)} email(s): {', '.join(emails)}")
        else:
            print(f"  No emails found")
        
        results.append(data)
    
    return results

def save_results_to_csv(results, filename="google_results_with_emails.csv"):
    """
    Save the URLs and emails to a CSV file.
    
    Args:
        results (list): List of dictionaries containing URLs and their emails
        filename (str): Name of the CSV file to save results to
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['url', 'emails']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow({
                'url': result['url'],
                'emails': ', '.join(result['emails'])
            })
    
    print(f"\nResults saved to {filename}")

if __name__ == "__main__":
    search_term = input("Enter search term: ")
    print(f"Searching for: {search_term}")
    
    # Get URLs from Google search results
    urls = scrape_google_urls(search_term)
    
    print(f"\nFound {len(urls)} URLs:")
    for i, url in enumerate(urls, 1):
        print(f"{i}. {url}")
    
    # Ask user if they want to proceed with email extraction
    proceed = input("\nDo you want to extract emails from these websites? (y/n): ").lower()
    
    if proceed == 'y':
        # Ask for the maximum number of sites to check
        try:
            max_sites = int(input("\nEnter maximum number of sites to check (or press Enter for all): ") or 0)
            if max_sites <= 0:
                max_sites = None
        except ValueError:
            max_sites = None
        
        # Scrape websites for emails
        results = scrape_websites_for_emails(urls, max_sites)
        
        # Count total emails found
        total_emails = sum(len(result['emails']) for result in results)
        print(f"\nTotal emails found: {total_emails}")
        
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