
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.utils import load_config, setup_logging, load_environment


def main():
    """Main scraper application."""
    print(" LinkedIn Profile Scraper")
    print("=" * 40)
    
    # Load environment variables
    load_environment()
    
    # Check credentials
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password or email == 'your_email@gmail.com':
        print("❌ Please set up your LinkedIn credentials in the .env file")
        print("\nEdit .env file:")
        print("LINKEDIN_EMAIL=your_email@gmail.com")
        print("LINKEDIN_PASSWORD=your_password")
        return
    
    print(f"✅ Authenticated as: {email}")
    
    # Setup
    logger = setup_logging()
    config = load_config()
    config['linkedin']['auto_login'] = True
    
    # Load URLs
    urls_file = Path('data/profile_urls.txt')
    if not urls_file.exists():
        print("❌ No profile URLs found. Please add URLs to data/profile_urls.txt")
        return
    
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not urls:
        print("❌ No valid URLs found in profile_urls.txt")
        return
    
    print(f"📋 Found {len(urls)} profiles to scrape")
    
    # Initialize scraper
    scraper = LinkedInScraper(config)
    
    try:
        print("\n🚀 Starting extraction...")
        profiles = scraper.scrape_profiles(urls)
        
        if profiles:
            # Generate output filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"data/output/linkedin_data_{timestamp}.csv"
            
            # Save results
            scraper.save_to_csv(profiles, output_file)
            
            print(f"\n✅ Extraction complete!")
            print(f"📊 Scraped {len(profiles)} profiles")
            print(f"💾 Saved to: {output_file}")
            
            # Show sample data
            successful = [p for p in profiles if p.get('name')]
            if successful:
                print(f"\n📋 Sample results:")
                for i, profile in enumerate(successful[:3], 1):
                    name = profile.get('name', 'Unknown')
                    headline = profile.get('headline', 'No headline')
                    print(f"   {i}. {name}")
                    if headline:
                        print(f"      {headline[:60]}...")
        else:
            print("❌ No profiles were successfully scraped")
    
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"Scraping failed: {str(e)}")
    finally:
        scraper.cleanup()


if __name__ == "__main__":
    main()