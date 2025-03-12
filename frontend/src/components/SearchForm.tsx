import React, { useState } from 'react';
import { Search } from 'lucide-react';

interface SearchFormProps {
  onSubmit: (query: string, pages: number) => void;
  isLoading: boolean;
}

export function SearchForm({ onSubmit, isLoading }: SearchFormProps) {
  const [query, setQuery] = useState('');
  const [pages, setPages] = useState(3);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query.trim(), pages);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 w-full">
      <div className="space-y-2">
        <label htmlFor="query" className="block text-sm font-medium text-gray-700">
          Search Query
        </label>
        <div className="relative">
          <input
            id="query"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your search query..."
            className="block w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            disabled={isLoading}
          />
          <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
        </div>
        <p className="text-xs text-gray-500">
          Example: "dentists amsterdam" or "marketing agencies london"
        </p>
      </div>

      <div className="space-y-2">
        <label htmlFor="pages" className="block text-sm font-medium text-gray-700">
          Number of Pages
        </label>
        <input
          id="pages"
          type="number"
          min="1"
          max="10"
          value={pages}
          onChange={(e) => setPages(parseInt(e.target.value) || 1)}
          className="block w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          disabled={isLoading}
        />
        <p className="text-xs text-gray-500">
          More pages will find more results but take longer to process
        </p>
      </div>

      <button
        type="submit"
        disabled={isLoading || !query.trim()}
        className={`w-full py-2.5 px-4 rounded-lg text-white font-medium transition-colors
          ${isLoading 
            ? 'bg-gray-400 cursor-not-allowed' 
            : 'bg-primary-600 hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
          }`}
      >
        {isLoading ? 'Scraping...' : 'Start Scraping'}
      </button>
    </form>
  );
}