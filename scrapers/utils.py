import logging
import json
import os
import random
import time
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

def setup_logging(level=logging.INFO):
    """Setup logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_config(config_file='config.json'):
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file {config_file} not found")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing configuration file: {e}")
        return {}

def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()

def get_random_user_agent():
    """Get a random user agent string."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    return random.choice(user_agents)

def get_headers():
    """Get headers for requests."""
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def random_delay(min_delay=1, max_delay=5):
    """Add random delay to avoid detection."""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

def sanitize_filename(filename):
    """Sanitize filename for safe file creation."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def extract_linkedin_username(url):
    """Extract username from LinkedIn profile URL."""
    if '/in/' in url:
        return url.split('/in/')[-1].split('/')[0]
    return None

def validate_linkedin_url(url):
    """Validate if URL is a proper LinkedIn profile URL."""
    linkedin_patterns = [
        'linkedin.com/in/',
        'www.linkedin.com/in/',
        'https://linkedin.com/in/',
        'https://www.linkedin.com/in/'
    ]
    return any(pattern in url.lower() for pattern in linkedin_patterns)

def save_progress(data, filename='progress.json'):
    """Save scraping progress to file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_progress(filename='progress.json'):
    """Load scraping progress from file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class RateLimiter:
    """Simple rate limiter to control request frequency."""
    
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            # Calculate how long to wait
            oldest_request = min(self.requests)
            wait_time = self.time_window - (now - oldest_request) + 1
            if wait_time > 0:
                logging.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
        
        self.requests.append(now)

def create_sample_urls_file():
    """Create a sample profile URLs file with random LinkedIn profiles."""
    sample_urls = [
        "https://www.linkedin.com/in/satyanadella/",
        "https://www.linkedin.com/in/jeffweiner08/",
        "https://www.linkedin.com/in/reidhoffman/",
        "https://www.linkedin.com/in/danielek/",
        "https://www.linkedin.com/in/williamhgates/",
        "https://www.linkedin.com/in/elonmusk/",
        "https://www.linkedin.com/in/sundarpichai/",
        "https://www.linkedin.com/in/tim-cook-1b51b/",
        "https://www.linkedin.com/in/sherrylsandberg/",
        "https://www.linkedin.com/in/melindagates/",
        "https://www.linkedin.com/in/oprahwinfrey/",
        "https://www.linkedin.com/in/richardbranson/",
        "https://www.linkedin.com/in/arianaahuffington/",
        "https://www.linkedin.com/in/garyvee/",
        "https://www.linkedin.com/in/simonsinekofficial/",
        "https://www.linkedin.com/in/neilpatel/",
        "https://www.linkedin.com/in/guykawaski/",
        "https://www.linkedin.com/in/adammosseri/",
        "https://www.linkedin.com/in/jeremywaite/",
        "https://www.linkedin.com/in/bernardmarr/"
    ]
    
    urls_file = Path('data/profile_urls.txt')
    urls_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(urls_file, 'w') as f:
        f.write("# LinkedIn Profile URLs to Scrape\n")
        f.write("# Add one URL per line\n")
        f.write("# Lines starting with # are comments\n\n")
        for url in sample_urls:
            f.write(f"{url}\n")
    
    logging.info(f"Created sample URLs file: {urls_file}")

if __name__ == "__main__":
    # Create sample URLs file if it doesn't exist
    if not Path('data/profile_urls.txt').exists():
        create_sample_urls_file()