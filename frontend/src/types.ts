export interface Company {
  name: string;
  website: string;
  email: string;
  scrapedDate: string;
}

export interface SearchResult {
  query: string;
  companies_found: number;
  filename: string;
  timestamp: string;
  isSendingEmails: boolean;
}

export interface ScrapeProgress {
  current: number;
  total: number;
  status: string;
  phase: string;
  percentage: number;
}

export interface EmailProgress {
  current: number;
  total: number;
  status: string;
  percentage: number;
}

export interface ScrapeResponse {
  message: string;
  companies_found: number;
  filename: string;
  query: string;
}

export interface EmailResponse {
  message: string;
  emails_sent: number;
}