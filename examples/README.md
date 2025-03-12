# AutoScraper Examples

This directory contains example scripts that demonstrate how to use the AutoScraper package for various tasks.

## Available Examples

### 1. Simple Search

**File:** `simple_search.py`

This example demonstrates the basic functionality of AutoScraper: searching Google for businesses, extracting contact information, and saving the results to a CSV file.

**Usage:**
```bash
python simple_search.py
```

### 2. Send Emails

**File:** `send_emails.py`

This example shows how to send emails to contacts discovered by the scraper. It includes loading email templates, personalizing the content, and sending emails through an SMTP server.

**Usage:**
```bash
python send_emails.py
```

### 3. Web Interface

**File:** `web_interface.py`

This example starts the AutoScraper web interface, which provides a user-friendly way to use the scraper functionality through a browser.

**Usage:**
```bash
python web_interface.py
```
Then open http://localhost:8000 in your browser.

## Running the Examples

Before running the examples, make sure you have installed the AutoScraper package:

```bash
pip install -e ..
```

Or, if you haven't installed the package, you can run the examples directly:

```bash
python simple_search.py
```

The examples will automatically add the parent directory to the Python path, so you can run them without installing the package.

## Note on Email Sending

The email sending example is configured to run in test mode by default, which means it will not send emails to actual recipients. Instead, it will send all emails to the sender's email address with a "[TEST]" prefix in the subject line.

To send emails to real recipients, you can modify the script to set `email_sender.test_mode = False`. 