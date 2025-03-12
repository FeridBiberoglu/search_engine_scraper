# AutoScraper

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen)
![FastAPI](https://img.shields.io/badge/FastAPI-0.70.0-green)
![Docker](https://img.shields.io/badge/Docker-Compatible-blue)

An advanced Google scraper for finding and gathering business contact information with built-in email functionality. This tool uses sophisticated techniques to bypass Google's security measures and scrape search results.

![AutoScraper Screenshot](https://via.placeholder.com/800x400?text=AutoScraper+Screenshot)

## 🌟 Features

- **Advanced Google Scraping**: Bypasses Google's security checks and CAPTCHAs
- **Business Contact Extraction**: Finds email addresses and contact information from websites
- **Email Automation**: Sends templated emails to gathered contacts
- **Modern Web Interface**: Beautiful and responsive UI for easy operation
- **API Access**: Fully documented REST API for integration
- **Command-Line Interface**: Use from the terminal for automation
- **Docker Support**: Easy deployment with Docker and docker-compose
- **Asynchronous Processing**: Handles multiple requests concurrently for improved performance

## 📋 Requirements

- Python 3.8+
- Docker (optional, for containerized deployment)

## 🚀 Installation

### Option 1: Using Python

1. Clone the repository:
```bash
git clone https://github.com/yourusername/autoscraper.git
cd autoscraper
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

### Option 2: Using Docker

1. Clone the repository:
```bash
git clone https://github.com/yourusername/autoscraper.git
cd autoscraper
```

2. Build and start the container:
```bash
docker-compose up -d
```

## 📊 Usage

### Web Interface

Start the web server:
```bash
python run.py web
```

Then open http://localhost:8000 in your browser.

### Command-Line Interface

Run a search from the command line:
```bash
python run.py cli "dentist amsterdam" --pages 3
```

For more options:
```bash
python run.py cli --help
```

### Quick Test

Run a test scrape:
```bash
python run.py test
```

### Docker

If using Docker:
```bash
docker-compose up -d
```

Then access the web interface at http://localhost:8000.

## 🔌 API Reference

AutoScraper provides a REST API for integration with other systems:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/scrape` | POST | Start a scraping job |
| `/send-email` | POST | Send an email to a contact |
| `/send-test-emails` | POST | Send test emails to all contacts |
| `/download/{filename}` | GET | Download results as CSV |
| `/email-templates` | GET | List available email templates |
| `/email-template/{name}` | GET | Get a specific email template |

API documentation is available at http://localhost:8000/docs when the server is running.

## 📝 Email Templates

The system includes several email templates located in the `templates` directory:

- `introduction_email.txt`: For introducing your company/service
- `partnership_email.txt`: For proposing business partnerships
- `service_offer_email.txt`: For offering specific services

You can customize these templates or add new ones as needed.

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_SERVER` | SMTP server address | smtp.gmail.com |
| `EMAIL_PORT` | SMTP server port | 587 |
| `EMAIL_USERNAME` | SMTP username | - |
| `EMAIL_PASSWORD` | SMTP password | - |
| `EMAIL_FROM` | Default sender email | - |
| `MAX_CONCURRENT_SCRAPES` | Maximum concurrent scraping tasks | 5 |
| `DEFAULT_DELAY` | Default delay between requests in seconds | 10 |

### Docker Configuration

You can modify the `docker-compose.yml` file to change port mappings, volumes, and environment variables.

## 🔧 Troubleshooting

### Common Issues

1. **Getting blocked by Google**:
   - Try increasing the delay between requests
   - Use a VPN or proxy service
   - Rotate user agents more frequently

2. **No results found**:
   - Check if the search query is specific enough
   - View the debug HTML files in `debug/` directory
   - Ensure your IP isn't temporarily blocked by Google

3. **Email sending failures**:
   - Verify SMTP settings
   - Check if recipient email addresses are valid
   - Ensure email templates are properly formatted

## 📁 Project Structure

```
autoscraper/
├── autoscraper/            # Python package
│   ├── __init__.py         # Package initialization
│   ├── app.py              # FastAPI web application
│   ├── cli.py              # Command-line interface
│   ├── scraper.py          # Core scraper functionality
│   ├── test_scraper.py     # Test script
│   ├── static/             # Static assets for web UI
│   └── templates/          # HTML templates for web UI
├── templates/              # Email templates
├── debug/                  # Debug output directory
├── results/                # Results output directory
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── setup.py                # Package installation
├── run.py                  # Entry point script
├── LICENSE                 # License file
└── README.md               # This file
```

## 📈 Future Improvements

- Implement proxy rotation
- Add support for other search engines
- Create more sophisticated email templates
- Improve CAPTCHA detection and handling
- Add better error reporting and logging

## ⚠️ Legal Disclaimer

This tool is provided for educational and research purposes only. Always respect website terms of service and robots.txt files. Web scraping may be against the terms of service of some websites, and using this tool improperly could result in your IP being blocked or other consequences.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 