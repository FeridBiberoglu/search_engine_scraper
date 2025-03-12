#!/bin/bash
# Frontend installation and build script for AutoScraper

# Function to display messages
print_message() {
    echo "====================================================="
    echo "$1"
    echo "====================================================="
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Node.js is installed
if ! command_exists node; then
    print_message "ERROR: Node.js is not installed"
    echo "Please install Node.js v16 or higher before proceeding."
    echo "Visit https://nodejs.org/ for installation instructions."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d 'v' -f2)
NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d. -f1)

if [ "$NODE_MAJOR" -lt 16 ]; then
    print_message "ERROR: Node.js v16 or higher is required"
    echo "Current version: v$NODE_VERSION"
    echo "Please upgrade your Node.js installation."
    exit 1
fi

print_message "Installing AutoScraper Frontend"
echo "Node.js version: v$NODE_VERSION"

# Create logs directory
mkdir -p logs

# Install dependencies
print_message "Installing dependencies"
npm install > logs/npm_install.log 2>&1
if [ $? -ne 0 ]; then
    print_message "ERROR: Failed to install dependencies"
    echo "Check logs/npm_install.log for details."
    exit 1
fi
echo "Dependencies installed successfully."

# Build the frontend
print_message "Building the frontend"
npm run build > logs/npm_build.log 2>&1
if [ $? -ne 0 ]; then
    print_message "ERROR: Failed to build the frontend"
    echo "Check logs/npm_build.log for details."
    exit 1
fi
echo "Frontend built successfully."

# Copy to backend
print_message "Integrating with backend"
node copy-to-backend.js > logs/copy_to_backend.log 2>&1
if [ $? -ne 0 ]; then
    print_message "ERROR: Failed to copy files to backend"
    echo "Check logs/copy_to_backend.log for details."
    exit 1
fi
echo "Frontend integrated with backend successfully."

print_message "Installation completed successfully!"
echo ""
echo "The frontend has been built and integrated with the backend."
echo "You can now access it by running the AutoScraper web interface:"
echo "  python -m autoscraper.app"
echo ""
echo "The modern React frontend will be available at:"
echo "  http://localhost:8000/"
echo "" 