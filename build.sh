#!/bin/bash
# Railway build script - install Chrome and dependencies

echo "🚀 Installing Chrome and dependencies for LinkedIn Scraper..."

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

# Install Python dependencies
pip install -r requirements.txt

echo "✅ Build complete!"