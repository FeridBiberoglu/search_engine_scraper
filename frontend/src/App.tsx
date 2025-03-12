import React, { useState, useEffect } from 'react';
import { Bot, AlertCircle, Download, Mail, Mails, Search, ExternalLink } from 'lucide-react';
import { SearchForm } from './components/SearchForm';
import { startScraping, sendEmailsForFile, sendAllEmails, getScrapeProgress, getEmailProgress } from './api';
import type { ScrapeResponse, EmailResponse, SearchResult, ScrapeProgress, EmailProgress } from './types';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [isSendingAll, setIsSendingAll] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [scrapeProgress, setScrapeProgress] = useState<ScrapeProgress | null>(null);
  const [emailProgress, setEmailProgress] = useState<EmailProgress | null>(null);

  // Progress polling
  useEffect(() => {
    let interval: number;

    if (isLoading) {
      interval = window.setInterval(async () => {
        try {
          const progress = await getScrapeProgress();
          setScrapeProgress(progress);
        } catch (err) {
          console.error('Failed to fetch scrape progress:', err);
        }
      }, 1000);
    } else {
      setScrapeProgress(null);
    }

    return () => {
      if (interval) window.clearInterval(interval);
    };
  }, [isLoading]);

  useEffect(() => {
    let interval: number;

    if (searchResults.some(r => r.isSendingEmails) || isSendingAll) {
      interval = window.setInterval(async () => {
        try {
          const progress = await getEmailProgress();
          setEmailProgress(progress);
        } catch (err) {
          console.error('Failed to fetch email progress:', err);
        }
      }, 1000);
    } else {
      setEmailProgress(null);
    }

    return () => {
      if (interval) window.clearInterval(interval);
    };
  }, [searchResults, isSendingAll]);

  const handleSearch = async (query: string, numPages: number) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await startScraping(query, numPages);
      setSearchResults(prev => [{
        query: response.query,
        companies_found: response.companies_found,
        filename: response.filename,
        timestamp: new Date().toISOString(),
        isSendingEmails: false
      }, ...prev]);
    } catch (err) {
      console.error('Error during scraping:', err);
      setError('Failed to complete scraping. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendEmails = async (filename: string, index: number) => {
    setError(null);
    const updatedResults = [...searchResults];
    updatedResults[index].isSendingEmails = true;
    setSearchResults(updatedResults);

    try {
      const response = await sendEmailsForFile(filename);
      
      // Update the results after sending
      const newResults = [...searchResults];
      newResults[index].isSendingEmails = false;
      setSearchResults(newResults);
      
      // Show success message
      alert(`Successfully sent ${response.emails_sent} emails!`);
    } catch (err) {
      console.error('Error sending emails:', err);
      setError('Failed to send emails. Please try again.');
      
      // Update state to reflect error
      const newResults = [...searchResults];
      newResults[index].isSendingEmails = false;
      setSearchResults(newResults);
    }
  };

  const handleSendAllEmails = async () => {
    setError(null);
    setIsSendingAll(true);

    try {
      const response = await sendAllEmails();
      alert(`Successfully sent ${response.emails_sent} emails!`);
    } catch (err) {
      console.error('Error sending all emails:', err);
      setError('Failed to send all emails. Please try again.');
    } finally {
      setIsSendingAll(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-primary-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div className="flex items-center mb-4 md:mb-0">
              <Search className="h-8 w-8 mr-3" />
              <div>
                <h1 className="text-2xl font-bold">AutoScraper</h1>
                <p className="text-primary-200 text-sm">Advanced Google Scraper & Contact Finder</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4 mt-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-xl shadow-soft">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 flex items-center">
              <Bot className="h-5 w-5 mr-2 text-primary-500" />
              Start New Search
            </h2>
            
            {/* Search form */}
            <SearchForm onSubmit={handleSearch} isLoading={isLoading} />
            
            {/* Progress indicator */}
            {scrapeProgress && (
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  {scrapeProgress.phase}: {scrapeProgress.status}
                </h3>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-primary-600 h-2.5 rounded-full transition-all duration-300"
                    style={{ width: `${scrapeProgress.percentage}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {scrapeProgress.current} of {scrapeProgress.total} ({scrapeProgress.percentage}%)
                </p>
              </div>
            )}
            
            {/* Email progress indicator */}
            {emailProgress && (
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  Sending Emails: {emailProgress.status}
                </h3>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-secondary-500 h-2.5 rounded-full transition-all duration-300"
                    style={{ width: `${emailProgress.percentage}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {emailProgress.current} of {emailProgress.total} ({emailProgress.percentage}%)
                </p>
              </div>
            )}
            
            {/* Error message */}
            {error && (
              <div className="mt-4 p-3 bg-red-100 border border-red-200 text-red-700 rounded-lg flex items-start">
                <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-soft">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-800 flex items-center">
                <Download className="h-5 w-5 mr-2 text-primary-500" />
                Search Results
              </h2>
              
              {searchResults.length > 0 && (
                <button
                  onClick={handleSendAllEmails}
                  disabled={isSendingAll || isLoading || searchResults.some(r => r.isSendingEmails)}
                  className={`px-3 py-1.5 text-sm rounded-lg flex items-center
                    ${isSendingAll || isLoading || searchResults.some(r => r.isSendingEmails)
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-secondary-600 text-white hover:bg-secondary-700'
                    }`}
                >
                  <Mails className="h-4 w-4 mr-1.5" />
                  Send All Emails
                </button>
              )}
            </div>
            
            {searchResults.length === 0 ? (
              <p className="text-gray-500 italic">No search results yet. Start a search to see results here.</p>
            ) : (
              <div className="space-y-4 max-h-[400px] overflow-y-auto">
                {searchResults.map((result, index) => (
                  <div key={result.timestamp} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium text-gray-800">{result.query}</h3>
                        <p className="text-sm text-gray-500">
                          {new Date(result.timestamp).toLocaleString()}
                        </p>
                      </div>
                      <span className="bg-primary-100 text-primary-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                        {result.companies_found} companies
                      </span>
                    </div>
                    
                    <div className="mt-3 flex space-x-2">
                      <a
                        href={`/download/${result.filename}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm flex items-center transition-colors"
                      >
                        <Download className="h-4 w-4 mr-1.5" />
                        Download CSV
                      </a>
                      
                      <button
                        onClick={() => handleSendEmails(result.filename, index)}
                        disabled={result.isSendingEmails || isLoading || isSendingAll}
                        className={`px-3 py-1.5 rounded-lg text-sm flex items-center transition-colors
                          ${result.isSendingEmails || isLoading || isSendingAll
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-secondary-600 text-white hover:bg-secondary-700'
                          }`}
                      >
                        <Mail className="h-4 w-4 mr-1.5" />
                        {result.isSendingEmails ? 'Sending...' : 'Send Emails'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
      
      <footer className="mt-12 py-6 bg-gray-100">
        <div className="container mx-auto px-4 text-center text-gray-600 text-sm">
          <p>&copy; {new Date().getFullYear()} AutoScraper | <a href="https://github.com/FeridBiberoglu/search_engine_scraper" className="text-primary-600 hover:underline">GitHub</a></p>
          <p className="mt-1 text-xs">Use responsibly and in accordance with websites' terms of service.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;