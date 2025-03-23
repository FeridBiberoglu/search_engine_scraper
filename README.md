# Search Engine Scraper & Email Extractor

A powerful tool for extracting URLs from search engine results and finding email addresses from websites, designed for lead generation and research purposes.

## Features

- **Multi-Page Search Results Scraping**: Extract up to 1000 URLs (10 pages with 100 results each)
- **Asynchronous Email Extraction**: Efficiently extract emails from multiple websites concurrently
- **Advanced Email Categorization**: Automatically categorizes emails by type (contact, sales, support, etc.)
- **Domain Matching**: Identifies emails that match the website's domain
- **Multiple Export Formats**:
  - Comprehensive CSV with detailed metadata
  - Excel workbooks with multiple sheets for different email categories
  - Simplified email-only CSV for easy importing
  - JSON export for programmatic use
  - Summary reports with key statistics
- **Robust HTML Parsing**: Multiple strategies to handle changes in search engine HTML structure

## Installation

1. Clone the repository:
```bash
git clone https://github.com/FeridBiberoglu/search_engine_scraper.git
cd search_engine_scraper
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the asynchronous scraper:

```bash
python async_google_scraper.py
```

The script will prompt you for:
1. A search term
2. Number of results per page (10-100)
3. Number of pages to scrape (1-10)
4. Whether to extract emails from the found URLs

### Output Files

The scraper generates several output files:

- `google_results_with_emails.csv`: Main CSV file with all data
- `google_results_with_emails.xlsx`: Excel workbook with multiple sheets (requires pandas)
- `emails_only.csv`: Simplified CSV with just domains and emails
- `search_results.json`: Raw data in JSON format
- `email_scraping_summary.txt`: Text summary with statistics
- `google_urls.txt`: Plain text list of all URLs found

### Data Structure

The Excel workbook contains the following sheets:

1. **Full Results**: Complete dataset with all metadata
2. **Summary**: Key statistics about the scraping results
3. **Contact Emails**: Emails categorized as contact/info addresses
4. **Sales Emails**: Emails categorized as sales-related
5. **Support Emails**: Emails categorized as support/help
6. **Admin Emails**: Administrative emails
7. **Personal Emails**: Emails that appear to be personal
8. **Other Emails**: Uncategorized emails
9. **All Emails**: Simple list of all emails found

## Integration with Email Systems

The data structure is designed to be easily integrated with email marketing systems:

- Use the categorized CSVs for targeted campaigns
- Import the Excel sheets into CRM systems
- Use the JSON output for API-based integration

## Advanced Configuration

For advanced users, the script can be modified to:

- Adjust the number of concurrent requests
- Change the email categorization rules
- Modify the export formats
- Add custom email validation

## Dependencies

- `selenium`: For browser automation
- `beautifulsoup4`: For HTML parsing
- `aiohttp`: For asynchronous HTTP requests
- `pandas` and `openpyxl`: For Excel export (optional)

## License

MIT

## Disclaimer

This tool is for educational purposes only. Be sure to respect websites' terms of service and robots.txt files. Use responsibly and ethically. 