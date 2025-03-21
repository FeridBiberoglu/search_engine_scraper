# AutoScraper

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.70.0-green.svg)
![Docker](https://img.shields.io/badge/docker-compatible-blue.svg)

Advanced Google scraper and business contact finder with built-in email functionality.

## 🚀 Features

- **Google Search Scraping**: Automatically search Google for businesses and extract URLs
- **Security Bypass**: Advanced techniques to avoid Google's security checks
- **Business Contact Extraction**: Find email addresses and contact information from websites
- **Email Automation**: Send personalized emails using customizable templates
- **Web Interface**: User-friendly interface for configuring and monitoring scraping jobs
- **Command-Line Interface**: Powerful CLI for automation and scripting
- **Docker Support**: Easy deployment with Docker and docker-compose
- **Asynchronous Processing**: Fast, concurrent processing of multiple websites
## 🛠️ Installation

### Using Python and Virtual Environment (Recommended)

```bash
# Navigate to the project directory
cd autoscraper_pkg

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install the required packages
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Running the Application

```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # On Linux/Mac

# Start the web server directly with uvicorn
uvicorn autoscraper.app:app --reload

# Or use the run.py script (if available in your directory)
# python run.py web
```

Then open your browser and navigate to `http://localhost:8000`.

### Troubleshooting Installation

If you encounter a "No module named 'aiohttp'" error or similar:

```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Install the specific missing package
pip install aiohttp

# Or reinstall all requirements
pip install -r requirements.txt
```

### Using Docker (Alternative)

```bash
# Navigate to the project directory
cd autoscraper_pkg

# Build and run with Docker Compose
docker-compose up -d
```

## 📝 Usage

### Web Interface

```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # On Linux/Mac

# Start the web server directly with uvicorn
uvicorn autoscraper.app:app --reload
```

Then open your browser and navigate to `http://localhost:8000`.

### Command-Line Interface

```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # On Linux/Mac

# Basic search
python -m autoscraper.cli search "dentists amsterdam" --pages 3

# Search and send emails
python -m autoscraper.cli search "lawyers new york" --pages 5 --send-emails --email-template introduction_email

# List available email templates
python -m autoscraper.cli templates
```

## 🔌 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/scrape` | POST | Start a new scraping job |
| `/scrape-progress` | GET | Get the current progress of a scraping job |
| `/send-emails/{filename}` | POST | Send emails to contacts in a specific file |
| `/send-all-emails` | POST | Send emails to all contacts |
| `/download/{filename}` | GET | Download results as CSV |
| `/email-templates` | GET | List available email templates |

## 📧 Email Templates

AutoScraper comes with several pre-defined email templates:

- `introduction_email.txt`: A general introduction to your services
- `partnership_email.txt`: Proposal for potential business partnerships
- `service_offer_email.txt`: Special offer for your services
- `event_invitation_email.txt`: Invitation to an event or webinar

## ⚙️ Configuration

AutoScraper can be configured through environment variables:

- `EMAIL_SERVER`: SMTP server for sending emails (default: smtp.gmail.com)
- `EMAIL_PORT`: SMTP server port (default: 587)
- `EMAIL_USERNAME`: Email account username
- `EMAIL_PASSWORD`: Email account password or app password
- `EMAIL_FROM`: Sender email address (default: same as EMAIL_USERNAME)
- `MAX_CONCURRENT_SCRAPES`: Maximum number of concurrent website scrapes (default: 5)
- `DEFAULT_DELAY`: Default delay between requests in seconds (default: 10)

## 🔍 Troubleshooting

- **No results found**: Google might be blocking your requests. Try increasing the delay between requests or using a proxy.
- **Email sending fails**: Check your SMTP settings and ensure you're using an app password if using Gmail.
- **Rate limiting**: If you're getting 429 errors, you're being rate limited. Increase the delay between requests.

## 🔮 Future Improvements

- Proxy support for avoiding IP-based blocking
- More advanced parsing for different types of websites
- Machine learning for better contact information extraction
- Integration with CRM systems
- Support for more search engines

## ⚠️ Legal Disclaimer

This tool is provided for educational purposes only. Web scraping may violate the terms of service of some websites. Always respect robots.txt files and website terms of use. Ensure compliance with email marketing laws like CAN-SPAM, GDPR, etc.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Frontend Interface

AutoScraper includes a modern React-based frontend built with:

- React 18
- TypeScript
- Tailwind CSS
- Vite

The frontend provides an intuitive interface for:
- Running scraping jobs
- Monitoring progress in real-time
- Viewing and downloading results
- Sending emails to discovered contacts

### Building the Frontend

If you want to modify the frontend, you can rebuild it with:

```bash
cd frontend
npm install
npm run build:backend
```

This will build the frontend and automatically integrate it with the backend. 