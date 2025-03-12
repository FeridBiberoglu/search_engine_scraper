/**
 * AutoScraper - Main JavaScript
 * 
 * This file contains common JavaScript functionality used across the application.
 */

// Initialize tooltips and popovers when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Initialize date formatting for elements with data-format-date attribute
    const dateElements = document.querySelectorAll('[data-format-date]');
    dateElements.forEach(element => {
        const dateStr = element.textContent.trim();
        if (dateStr) {
            try {
                const date = new Date(dateStr);
                element.textContent = date.toLocaleDateString();
            } catch (e) {
                console.error('Invalid date format:', dateStr);
            }
        }
    });
});

/**
 * Format a number with commas as thousands separators
 * @param {number} num - The number to format
 * @returns {string} The formatted number
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Truncate a string to a specified length and add ellipsis
 * @param {string} str - The string to truncate
 * @param {number} length - The maximum length
 * @returns {string} The truncated string
 */
function truncateString(str, length = 50) {
    if (!str) return '';
    return str.length > length ? str.substring(0, length) + '...' : str;
}

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    // Check if notification container exists, create if not
    let container = document.querySelector('.toast-container');
    
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type}`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    // Create toast content
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add toast to container
    container.appendChild(toast);
    
    // Initialize and show the toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    bsToast.show();
    
    // Remove toast from DOM after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Copy text to clipboard
 * @param {string} text - The text to copy
 * @returns {Promise<boolean>} Whether the operation was successful
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        return navigator.clipboard.writeText(text)
            .then(() => {
                showNotification('Copied to clipboard!', 'success');
                return true;
            })
            .catch(err => {
                console.error('Failed to copy text: ', err);
                showNotification('Failed to copy to clipboard', 'error');
                return false;
            });
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        
        try {
            const successful = document.execCommand('copy');
            document.body.removeChild(textarea);
            
            if (successful) {
                showNotification('Copied to clipboard!', 'success');
                return Promise.resolve(true);
            } else {
                showNotification('Failed to copy to clipboard', 'error');
                return Promise.resolve(false);
            }
        } catch (err) {
            console.error('Failed to copy text: ', err);
            document.body.removeChild(textarea);
            showNotification('Failed to copy to clipboard', 'error');
            return Promise.resolve(false);
        }
    }
} 