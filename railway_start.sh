#!/bin/bash

# Railway startup script - installs Chrome and starts the app

echo "🚀 Starting LinkedIn Scraper on Railway..."

# Update package list
apt-get update

# Install Chrome dependencies
apt-get install -y wget gnupg software-properties-common

# Add Google Chrome repository
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

# Install Chrome and virtual display
apt-get update
apt-get install -y google-chrome-stable xvfb

# Create data directories
mkdir -p data/output

# Create default profile URLs if not exists
if [ ! -f "data/profile_urls.txt" ]; then
    echo "https://www.linkedin.com/in/sample-profile/" > data/profile_urls.txt
fi

echo "✅ Setup complete! Starting web app..."

# Start the Flask app with virtual display
exec xvfb-run -a python web_app.py