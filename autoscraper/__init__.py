"""
AutoScraper - Advanced Google scraper and business contact finder.

This package provides tools for scraping Google search results, extracting
business contact information from websites, and sending automated emails.
"""

__version__ = '1.0.0'
__author__ = 'AutoScraper Contributors'

from .scraper import GoogleScraper, EmailSender

# Export main classes at package level
__all__ = ['GoogleScraper', 'EmailSender'] 