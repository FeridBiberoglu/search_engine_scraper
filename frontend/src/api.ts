import type { ScrapeResponse, EmailResponse, ScrapeProgress, EmailProgress } from './types';

const API_URL = 'http://localhost:8000';

export async function startScraping(query: string, numPages: number = 3): Promise<ScrapeResponse> {
  const response = await fetch(`${API_URL}/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, num_pages: numPages }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to start scraping');
  }
  
  return response.json();
}

export async function getScrapeProgress(): Promise<ScrapeProgress> {
  const response = await fetch(`${API_URL}/scrape-progress`);
  if (!response.ok) {
    throw new Error('Failed to fetch scrape progress');
  }
  return response.json();
}

export async function getEmailProgress(): Promise<EmailProgress> {
  const response = await fetch(`${API_URL}/email-progress`);
  if (!response.ok) {
    throw new Error('Failed to fetch email progress');
  }
  return response.json();
}

export async function sendEmailsForFile(filename: string): Promise<EmailResponse> {
  const response = await fetch(`${API_URL}/send-emails/${filename}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error('Failed to send emails');
  }
  
  return response.json();
}

export async function sendAllEmails(): Promise<EmailResponse> {
  const response = await fetch(`${API_URL}/send-all-emails`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error('Failed to send all emails');
  }
  
  return response.json();
}