#!/usr/bin/env python3
"""
AutoScraper - Web Application Module

This module provides a FastAPI web application for the AutoScraper tool.
"""

import os
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .scraper import GoogleScraper

# Initialize FastAPI app
app = FastAPI(
    title="AutoScraper API",
    description="API for scraping Google search results and extracting business contact information",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Setup templates and static files
current_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

# Create global scraper instance
scraper = GoogleScraper()

# Debug directory
os.makedirs('debug', exist_ok=True)

# Request/response models
class ScrapeRequest(BaseModel):
    query: str
    num_pages: int = 3  # Default value

class EmailRequest(BaseModel):
    recipient: str
    subject: str
    body: str
    template_name: Optional[str] = None

# Store the latest search results
latest_results = {
    "query": "",
    "companies": [],
    "timestamp": "",
    "filename": ""
}

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/results", response_class=HTMLResponse)
async def get_results(request: Request):
    """Render the results page."""
    return templates.TemplateResponse(
        "results.html", 
        {
            "request": request,
            "companies": latest_results["companies"],
            "query": latest_results["query"],
            "timestamp": latest_results["timestamp"],
            "filename": latest_results["filename"]
        }
    )

@app.post("/scrape")
async def scrape_data(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Start a scraping job to search Google and extract contact information.
    
    Args:
        request: The scrape request containing the query and number of pages
        background_tasks: FastAPI background tasks
        
    Returns:
        JSON response with job status
    """
    global scraper, latest_results
    
    # Reset scraper state
    scraper = GoogleScraper()
    
    try:
        # Perform the search
        await scraper.search_google(request.query, request.num_pages)
        
        # Process the URLs
        if scraper.urls:
            await scraper.process_urls()
            
        # Save results
        filename = scraper.save_results(request.query)
        
        # Update latest results
        latest_results = {
            "query": request.query,
            "companies": scraper.companies,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": filename
        }
        
        return JSONResponse(content={
            "message": "Scraping completed",
            "companies_found": len(scraper.companies),
            "filename": filename
        })
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

@app.post("/send-email")
async def send_email(request: EmailRequest):
    """
    Send an email to a contact.
    
    Args:
        request: The email request containing recipient, subject, and body
        
    Returns:
        JSON response with send status
    """
    try:
        sender = scraper.email_sender
        sender.connect()
        sender.send_email(request.recipient, request.subject, request.body)
        sender.disconnect()
        
        return JSONResponse(content={
            "message": "Email sent successfully"
        })
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

@app.post("/send-test-emails")
async def send_test_emails():
    """
    Send test emails to all scraped contacts.
    
    Returns:
        JSON response with send status
    """
    global scraper
    
    if not scraper.companies:
        return JSONResponse(
            content={"error": "No companies found. Please run scraping first."}, 
            status_code=404
        )
    
    try:
        emails_sent = scraper.send_test_emails()
        return JSONResponse(content={
            "message": "Test emails sent",
            "emails_sent": emails_sent
        })
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

@app.get("/download/{filename}")
async def download_csv(filename: str):
    """
    Download a CSV file with scraping results.
    
    Args:
        filename: The name of the file to download
        
    Returns:
        The CSV file
    """
    file_path = os.path.join(os.getcwd(), filename)
    
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type='text/csv',
            filename=filename
        )
    return JSONResponse(
        content={"error": "File not found"},
        status_code=404
    )

@app.get("/email-templates")
async def get_email_templates():
    """
    Get a list of available email templates.
    
    Returns:
        JSON response with template names
    """
    templates_dir = os.path.join(os.getcwd(), "templates")
    
    templates = []
    if os.path.exists(templates_dir):
        for filename in os.listdir(templates_dir):
            if filename.endswith(".txt"):
                template_name = filename.replace(".txt", "")
                templates.append(template_name)
    
    return JSONResponse(content={
        "templates": templates
    })

@app.get("/email-template/{template_name}")
async def get_email_template(template_name: str):
    """
    Get the content of an email template.
    
    Args:
        template_name: The name of the template
        
    Returns:
        JSON response with template content
    """
    template_path = os.path.join(os.getcwd(), "templates", f"{template_name}.txt")
    
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        return JSONResponse(content={
            "name": template_name,
            "content": content
        })
    
    return JSONResponse(
        content={"error": "Template not found"},
        status_code=404
    )

def start():
    """Start the FastAPI app with uvicorn."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start() 