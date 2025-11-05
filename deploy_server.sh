#!/bin/bash
# LinkedIn Scraper Server Setup Script
# Run this on a fresh Ubuntu 22.04 server

set -e

echo "🚀 Setting up LinkedIn Scraper on server..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Chrome dependencies
sudo apt install -y wget gnupg software-properties-common

# Add Google Chrome repository
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list

# Install Chrome
sudo apt update
sudo apt install -y google-chrome-stable

# Install virtual display for headless operation
sudo apt install -y xvfb

# Install git
sudo apt install -y git

# Create application directory
mkdir -p ~/linkedin-scraper
cd ~/linkedin-scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install selenium beautifulsoup4 pandas undetected-chromedriver python-dotenv openpyxl webdriver-manager

echo "✅ Server setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Upload your scraper files to ~/linkedin-scraper/"
echo "2. Create .env file with your LinkedIn credentials"
echo "3. Run: cd ~/linkedin-scraper && source venv/bin/activate"
echo "4. Run: xvfb-run -a python3 main.py"
echo ""
echo "💡 To run in background: nohup xvfb-run -a python3 main.py > scraper.log 2>&1 &"