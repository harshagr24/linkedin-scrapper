#!/usr/bin/env python3
"""
LinkedIn Login Test
Test login functionality with 2FA support
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.utils import load_config, setup_logging, load_environment


def test_login():
    """Test LinkedIn login with 2FA support."""
    print("🔐 LinkedIn Login Test")
    print("=" * 30)
    
    # Load environment variables
    load_environment()
    
    # Check credentials
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ Please set up your LinkedIn credentials in the .env file")
        return
    
    print(f"📧 Using email: {email}")
    print("🌐 Opening browser for login...")
    
    # Setup
    logger = setup_logging()
    config = load_config()
    config['linkedin']['auto_login'] = True
    
    # Initialize scraper
    scraper = LinkedInScraper(config)
    
    try:
        # Setup browser
        scraper.setup_driver()
        print("✅ Browser started successfully")
        
        # Attempt login
        print("\n🔑 Attempting LinkedIn login...")
        login_success = scraper.login_to_linkedin()
        
        if login_success:
            print("\n🎉 Login successful!")
            print("🏠 Navigating to LinkedIn home...")
            scraper.driver.get("https://www.linkedin.com/feed/")
            print("✅ Ready to start scraping!")
            
            input("\n⏸️ Press Enter to close browser and exit...")
        else:
            print("\n❌ Login failed!")
            input("\n⏸️ Press Enter to close browser and exit...")
    
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        scraper.cleanup()


if __name__ == "__main__":
    test_login()