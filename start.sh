#!/bin/bash
# Quick start script for LinkedIn Scraper

echo "🔗 LinkedIn Scraper - Quick Start"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password_here
EOF
    echo "⚠️  Please edit .env file with your LinkedIn credentials!"
    echo "   nano .env"
    echo ""
fi

# Make data directories
mkdir -p data/output

# Check if profile URLs exist
if [ ! -f "data/profile_urls.txt" ]; then
    echo "Creating sample profile_urls.txt..."
    cat > data/profile_urls.txt << EOF
https://www.linkedin.com/in/sample-profile/
EOF
    echo "📝 Please edit data/profile_urls.txt with LinkedIn profile URLs to scrape"
    echo "   nano data/profile_urls.txt"
    echo ""
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 Choose how to run:"
echo "1. Command line: xvfb-run -a python3 main.py"
echo "2. Web interface: xvfb-run -a python3 web_app.py"
echo "3. Background: nohup xvfb-run -a python3 main.py > scraper.log 2>&1 &"