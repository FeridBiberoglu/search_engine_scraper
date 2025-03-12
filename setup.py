#!/usr/bin/env python3
"""
AutoScraper - Google Scraper and Contact Finder

Setup script for installing the AutoScraper package.
"""

from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read long description from README.md
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

# Package data to include
package_data = {
    'autoscraper': [
        'static/css/*.css',
        'static/js/*.js',
        'templates/*.html',
    ],
}

setup(
    name="autoscraper",
    version="1.0.0",
    description="Advanced Google scraper and business contact finder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/autoscraper",
    packages=find_packages(),
    include_package_data=True,
    package_data=package_data,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'autoscraper=autoscraper.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    keywords="scraper, google, contact finder, email, web scraping",
) 