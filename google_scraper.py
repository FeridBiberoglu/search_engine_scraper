import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

class GoogleScraper:
    def __init__(self, headless=True):
        """Initialize the Google Scraper with required configurations."""
        # Configure Chrome options
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("--disable-notifications")
        self.chrome_options.add_argument("--disable-popup-blocking")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
        # Initialize the Chrome driver
        self.driver = webdriver.Chrome(options=self.chrome_options)
        
    def search(self, query, num_results=10):
        """Perform a Google search and extract URLs.
        
        Args:
            query (str): The search term to use in Google
            num_results (int): Maximum number of results to extract
            
        Returns:
            list: A list of dictionaries containing extracted URLs and titles
        """
        # Format the search query for URL
        formatted_query = query.replace(' ', '+')
        search_url = f"https://www.google.com/search?q={formatted_query}"
        
        # Open the search URL
        self.driver.get(search_url)
        print("Navigating to Google search page...")
        
        # Wait for the page to load
        time.sleep(3)
        
        # Get the page source and parse with BeautifulSoup
        page_html = self.driver.page_source
        soup = BeautifulSoup(page_html, 'html.parser')
        
        # Extract search results
        results = []
        
        # Save HTML for debugging (optional)
        with open("google_source.html", "w", encoding="utf-8") as f:
            f.write(page_html)
        print("Saved HTML source to google_source.html for debugging")
        
        # Try multiple selector strategies to find search results
        print("Extracting information from search results...")
        
        # Method 1: Try the original selectors from info.txt
        try:
            organic_results = soup.find("div", {"class": "dURPMd"}).find_all("div", {"class": "Ww4FFb"})
            print(f"Method 1: Found {len(organic_results)} results")
            
            for result in organic_results[:num_results]:
                data = {}
                
                # Extract title
                try:
                    data["title"] = result.find("h3").text
                except:
                    data["title"] = None
                
                # Extract URL
                try:
                    url = result.find("a").get('href')
                    # Clean URL if necessary
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]
                    data["url"] = url
                except:
                    data["url"] = None
                
                # Add result if URL exists
                if data["url"]:
                    results.append(data)
                
        except Exception as e:
            print(f"Method 1 failed: {e}")
            
        # Method 2: Try finding all search result blocks with class "g"
        if not results:
            try:
                search_divs = soup.find_all("div", class_="g")
                print(f"Method 2: Found {len(search_divs)} results")
                
                for div in search_divs[:num_results]:
                    data = {}
                    
                    # Extract title
                    try:
                        h3 = div.find("h3")
                        if h3:
                            data["title"] = h3.text
                        else:
                            # Try alternative title patterns
                            a_tag = div.find("a")
                            if a_tag:
                                h3_like = a_tag.find(["h3", "h4", "div", "span"])
                                if h3_like:
                                    data["title"] = h3_like.text
                    except:
                        data["title"] = None
                    
                    # Extract URL
                    try:
                        a_tag = div.find("a")
                        if a_tag and a_tag.get('href'):
                            url = a_tag.get('href')
                            if url.startswith('http'):
                                data["url"] = url
                    except:
                        data["url"] = None
                    
                    # Add result if URL exists
                    if data.get("url"):
                        results.append(data)
            except Exception as e:
                print(f"Method 2 failed: {e}")
        
        # Method 3: Try another common pattern with "yuRUbf" class
        if not results:
            try:
                search_results = soup.find_all("div", {"class": "yuRUbf"})
                print(f"Method 3: Found {len(search_results)} results")
                
                for result in search_results[:num_results]:
                    data = {}
                    
                    # Extract title
                    try:
                        h3 = result.find("h3")
                        if h3:
                            data["title"] = h3.text
                    except:
                        data["title"] = None
                    
                    # Extract URL
                    try:
                        url = result.find("a").get('href')
                        if url.startswith('http'):
                            data["url"] = url
                    except:
                        data["url"] = None
                    
                    # Add result if URL exists
                    if data.get("url"):
                        results.append(data)
            except Exception as e:
                print(f"Method 3 failed: {e}")
        
        # Method 4: Most generic approach
        if not results:
            try:
                all_links = soup.find_all("a")
                print(f"Method 4: Found {len(all_links)} links")
                
                result_count = 0
                for link in all_links:
                    if result_count >= num_results:
                        break
                        
                    href = link.get('href')
                    if href and href.startswith('http') and 'google' not in href:
                        data = {}
                        data["url"] = href
                        
                        # Try to find title near the link
                        try:
                            # Check nearby h3 tags
                            parent = link.parent
                            h3 = parent.find("h3")
                            if h3:
                                data["title"] = h3.text
                            else:
                                # Use link text as fallback title
                                data["title"] = link.text.strip()
                                if not data["title"]:
                                    data["title"] = href
                        except:
                            data["title"] = href
                        
                        # Add result if not already in results
                        if data["url"] and not any(r.get("url") == data["url"] for r in results):
                            results.append(data)
                            result_count += 1
            except Exception as e:
                print(f"Method 4 failed: {e}")
        
        # Remove any remaining Google-related URLs
        results = [result for result in results if 'google.com' not in result.get("url", "")]
        
        return results
    
    def save_to_csv(self, results, filename="google_results.csv"):
        """Save the extracted results to a CSV file.
        
        Args:
            results (list): List of dictionaries containing the extracted data
            filename (str): Name of the CSV file to save results to
        """
        df = pd.DataFrame(results)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Results saved to {filename}")
    
    def close(self):
        """Close the browser and release resources."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Note: Could not terminate browser process cleanly, but this is normal. Error: {type(e).__name__}")
            
    def __del__(self):
        """Destructor to ensure browser is closed."""
        self.close()


def main():
    # Example usage
    query = input("Enter search term: ")
    num_results = int(input("Enter number of results to extract (default 10): ") or "10")
    
    # Initialize the scraper
    scraper = GoogleScraper(headless=True)  # Set to True for headless mode
    
    try:
        # Perform the search and get results
        print(f"Searching for: {query}")
        results = scraper.search(query, num_results)
        
        # Print the results
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.get('title', 'No title')}")
            print(f"   URL: {result.get('url', 'No URL')}")
            print()
        
        # Save results to CSV
        scraper.save_to_csv(results)
        
    finally:
        # Close the browser
        scraper.close()


if __name__ == "__main__":
    main() 