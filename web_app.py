#!/usr/bin/env python3
"""
Simple Flask web interface for LinkedIn Scraper
Access via browser to trigger scraping and download results
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
import subprocess
import threading
from pathlib import Path

app = Flask(__name__)

# Global status
scraper_status = {
    'running': False,
    'last_run': None,
    'profiles_scraped': 0,
    'errors': []
}

@app.route('/')
def index():
    return render_template('index.html', status=scraper_status)

@app.route('/api/status')
def get_status():
    return jsonify(scraper_status)

@app.route('/api/start', methods=['POST'])
def start_scraping():
    if scraper_status['running']:
        return jsonify({'error': 'Scraper is already running'}), 400
    
    # Get URLs from form
    urls = request.json.get('urls', [])
    if not urls:
        return jsonify({'error': 'No URLs provided'}), 400
    
    # Write URLs to file
    with open('data/profile_urls.txt', 'w') as f:
        for url in urls:
            f.write(url.strip() + '\n')
    
    # Start scraping in background
    thread = threading.Thread(target=run_scraper)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Scraping started successfully'})

@app.route('/api/download/<file_type>')
def download_results(file_type):
    if file_type == 'csv':
        file_path = 'data/output/linkedin_profiles_authenticated.csv'
    elif file_type == 'json':
        file_path = 'data/output/linkedin_profiles_authenticated.json'
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=True)

def run_scraper():
    global scraper_status
    
    scraper_status['running'] = True
    scraper_status['last_run'] = datetime.now().isoformat()
    scraper_status['profiles_scraped'] = 0
    scraper_status['errors'] = []
    
    try:
        # Run the main scraper
        result = subprocess.run(['python3', 'main.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # Count scraped profiles
            csv_path = 'data/output/linkedin_profiles_authenticated.csv'
            if os.path.exists(csv_path):
                import pandas as pd
                df = pd.read_csv(csv_path)
                scraper_status['profiles_scraped'] = len(df)
        else:
            scraper_status['errors'].append(result.stderr)
            
    except Exception as e:
        scraper_status['errors'].append(str(e))
    
    finally:
        scraper_status['running'] = False

# Initialize directories and templates on module load
os.makedirs('data/output', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Create default profile URLs if not exists
if not os.path.exists('data/profile_urls.txt'):
    with open('data/profile_urls.txt', 'w') as f:
        f.write('https://www.linkedin.com/in/sample-profile/\n')

# Create HTML template
html_template = '''<!DOCTYPE html>
<html>
<head>
    <title>LinkedIn Scraper Control Panel</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .status { padding: 20px; background: #f5f5f5; border-radius: 5px; margin: 20px 0; }
        .running { background: #d4edda; }
        .error { background: #f8d7da; }
        textarea { width: 100%; height: 200px; margin: 10px 0; }
        button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background: #0056b3; }
        button:disabled { background: #6c757d; cursor: not-allowed; }
        .download-section { margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 LinkedIn Scraper Control Panel</h1>
        
        <div class="status" id="status">
            <h3>Status</h3>
            <p><strong>Running:</strong> <span id="running">{{ status.running }}</span></p>
            <p><strong>Last Run:</strong> <span id="last_run">{{ status.last_run or 'Never' }}</span></p>
            <p><strong>Profiles Scraped:</strong> <span id="profiles_scraped">{{ status.profiles_scraped }}</span></p>
        </div>
        
        <div class="scraping-section">
            <h3>Start Scraping</h3>
            <textarea id="urls" placeholder="Enter LinkedIn profile URLs, one per line:
https://www.linkedin.com/in/profile1/
https://www.linkedin.com/in/profile2/"></textarea>
            <br>
            <button onclick="startScraping()" id="startBtn">Start Scraping</button>
        </div>
        
        <div class="download-section">
            <h3>Download Results</h3>
            <button onclick="downloadFile('csv')">Download CSV</button>
            <button onclick="downloadFile('json')">Download JSON</button>
        </div>
        
        <div id="errors" style="color: red; margin-top: 20px;"></div>
    </div>

    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('running').textContent = data.running;
                    document.getElementById('last_run').textContent = data.last_run || 'Never';
                    document.getElementById('profiles_scraped').textContent = data.profiles_scraped;
                    
                    const statusDiv = document.getElementById('status');
                    const startBtn = document.getElementById('startBtn');
                    
                    if (data.running) {
                        statusDiv.className = 'status running';
                        startBtn.disabled = true;
                        startBtn.textContent = 'Scraping in Progress...';
                    } else {
                        statusDiv.className = 'status';
                        startBtn.disabled = false;
                        startBtn.textContent = 'Start Scraping';
                    }
                    
                    if (data.errors && data.errors.length > 0) {
                        document.getElementById('errors').innerHTML = 
                            '<h4>Errors:</h4>' + data.errors.map(e => '<p>' + e + '</p>').join('');
                    }
                });
        }
        
        function startScraping() {
            const urls = document.getElementById('urls').value.split('\\n').filter(url => url.trim());
            
            if (urls.length === 0) {
                alert('Please enter at least one LinkedIn profile URL');
                return;
            }
            
            fetch('/api/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({urls: urls})
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    alert('Scraping started! Check status for updates.');
                }
            });
        }
        
        function downloadFile(type) {
            window.location.href = '/api/download/' + type;
        }
        
        // Update status every 2 seconds
        setInterval(updateStatus, 2000);
        updateStatus();
    </script>
</body>
</html>'''
    
# Write HTML template to file
with open('templates/index.html', 'w') as f:
    f.write(html_template)

if __name__ == '__main__':
    print("🚀 LinkedIn Scraper Web Interface starting...")
    
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 5000))
    print(f"📱 Access at: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)