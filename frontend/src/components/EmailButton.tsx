import React from 'react';
import { Mail } from 'lucide-react';

interface EmailButtonProps {
  onClick: () => void;
  disabled: boolean;
  isSending: boolean;
}

export function EmailButton({ onClick, disabled, isSending }: EmailButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`flex items-center px-3 py-1.5 rounded-lg text-sm transition-colors
        ${disabled
          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
          : 'bg-secondary-600 text-white hover:bg-secondary-700 focus:ring-2 focus:ring-secondary-500 focus:ring-offset-2'
        }`}
    >
      <Mail className="h-4 w-4 mr-1.5" />
      {isSending ? 'Sending...' : 'Send Emails'}
    </button>
  );
}