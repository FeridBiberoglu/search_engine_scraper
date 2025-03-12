#!/bin/bash
# Installation script for AutoScraper

# Function to display messages
print_message() {
    echo "====================================================="
    echo "$1"
    echo "====================================================="
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_message "ERROR: Python 3 is not installed."
    echo "Please install Python 3.8 or higher before proceeding."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
python_major=$(echo "$python_version" | cut -d. -f1)
python_minor=$(echo "$python_version" | cut -d. -f2)

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]); then
    print_message "ERROR: Python 3.8 or higher is required."
    echo "Current version: Python $python_version"
    echo "Please upgrade your Python installation."
    exit 1
fi

print_message "Installing AutoScraper"
echo "Python version: $python_version"

# Create directory for logs
mkdir -p logs

# Create virtual environment
print_message "Creating virtual environment"
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_message "ERROR: Failed to create virtual environment."
        exit 1
    fi
    echo "Virtual environment created successfully."
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_message "ERROR: Failed to activate virtual environment."
    exit 1
fi
echo "Virtual environment activated."

# Upgrade pip
print_message "Upgrading pip"
pip install --upgrade pip > logs/pip_upgrade.log 2>&1
if [ $? -ne 0 ]; then
    print_message "WARNING: Failed to upgrade pip. Continuing anyway."
fi

# Install dependencies
print_message "Installing dependencies"
pip install -r requirements.txt > logs/dependencies_install.log 2>&1
if [ $? -ne 0 ]; then
    print_message "ERROR: Failed to install dependencies."
    echo "Check logs/dependencies_install.log for details."
    exit 1
fi
echo "Dependencies installed successfully."

# Install the package in development mode
print_message "Installing AutoScraper package"
pip install -e . > logs/package_install.log 2>&1
if [ $? -ne 0 ]; then
    print_message "ERROR: Failed to install AutoScraper package."
    echo "Check logs/package_install.log for details."
    exit 1
fi
echo "AutoScraper package installed successfully."

# Create necessary directories
print_message "Creating necessary directories"
mkdir -p debug results templates
echo "Directories created."

print_message "Installation completed successfully!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To test the installation, run one of the example scripts:"
echo "  python examples/simple_search.py"
echo ""
echo "Or use the command-line interface:"
echo "  autoscraper search \"restaurants amsterdam\" --pages 1"
echo ""
echo "Or start the web interface:"
echo "  python -m autoscraper.app"
echo "" 