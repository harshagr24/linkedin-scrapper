import logging
import time
import csv
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False
    print("Warning: undetected_chromedriver not available, using regular selenium")
from bs4 import BeautifulSoup
import pandas as pd

from .utils import RateLimiter, random_delay, get_headers, sanitize_filename, load_environment

class LinkedInScraper:
    """Main LinkedIn profile scraper using Selenium."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.rate_limiter = RateLimiter(
            max_requests=config.get('rate_limiting', {}).get('requests_per_minute', 10),
            time_window=60
        )
        load_environment()
        
    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures and server compatibility."""
        try:
            # Try undetected Chrome first (if available)
            if UC_AVAILABLE:
                try:
                    chrome_options = uc.ChromeOptions()
                    
                    # Basic options
                    if self.config.get('browser', {}).get('headless', False):
                        chrome_options.add_argument('--headless=new')
                    
                    # Server compatibility options
                    chrome_options.add_argument('--no-sandbox')
                    chrome_options.add_argument('--disable-dev-shm-usage')
                    chrome_options.add_argument('--disable-gpu')
                    chrome_options.add_argument('--disable-extensions')
                    chrome_options.add_argument('--disable-plugins')
                    chrome_options.add_argument('--disable-images')
                    chrome_options.add_argument('--remote-debugging-port=9222')
                    chrome_options.add_argument('--single-process')
                    
                    # Anti-detection options
                    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                    
                    # Window size
                    window_size = self.config.get('browser', {}).get('window_size', [1920, 1080])
                    chrome_options.add_argument(f'--window-size={window_size[0]},{window_size[1]}')
                    
                    # User data directory for persistence
                    user_data_dir = self.config.get('browser', {}).get('user_data_dir')
                    if user_data_dir:
                        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
                    
                    # Proxy configuration
                    proxy_config = self.config.get('proxies', {})
                    if proxy_config.get('enabled') and proxy_config.get('proxy_list'):
                        proxy = proxy_config['proxy_list'][0]  # Use first proxy for now
                        chrome_options.add_argument(f'--proxy-server={proxy}')
                    
                    self.driver = uc.Chrome(options=chrome_options, version_main=None)
                    
                    # Execute script to hide webdriver property
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    
                    self.logger.info("Undetected Chrome driver initialized successfully")
                    
                except Exception as uc_error:
                    self.logger.warning(f"Undetected Chrome failed: {uc_error}")
                    self.logger.info("Falling back to regular Selenium Chrome driver...")
                    UC_AVAILABLE = False  # Disable for this session
            
            # Use regular Selenium if undetected chrome not available or failed
            if not UC_AVAILABLE:
                
                # Fallback to regular Selenium
                chrome_options = Options()
                
                if self.config.get('browser', {}).get('headless', False):
                    chrome_options.add_argument('--headless=new')
                
                # Server compatibility options
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-plugins')
                chrome_options.add_argument('--disable-images')
                chrome_options.add_argument('--remote-debugging-port=9222')
                chrome_options.add_argument('--single-process')
                
                # Anti-detection options
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # Window size
                window_size = self.config.get('browser', {}).get('window_size', [1920, 1080])
                chrome_options.add_argument(f'--window-size={window_size[0]},{window_size[1]}')
                
                # Use ChromeDriverManager for automatic driver management
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Execute script to hide webdriver property
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                self.logger.info("Regular Chrome driver initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome driver: {str(e)}")
            self.logger.error("Please ensure Chrome browser is installed and up to date")
            raise
    
    def login_to_linkedin(self):
        """Login to LinkedIn if credentials are provided."""
        linkedin_config = self.config.get('linkedin', {})
        if not linkedin_config.get('auto_login', False):
            return True
        
        email = linkedin_config.get('email') or os.getenv('LINKEDIN_EMAIL')
        password = linkedin_config.get('password') or os.getenv('LINKEDIN_PASSWORD')
        
        if not email or not password:
            self.logger.warning("LinkedIn credentials not provided. Proceeding without login.")
            return False
        
        try:
            self.logger.info("Attempting to login to LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for login form
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Enter credentials
            email_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            
            email_field.send_keys(email)
            random_delay(1, 2)
            password_field.send_keys(password)
            random_delay(1, 2)
            login_button.click()
            
            # Wait for successful login or handle challenges
            time.sleep(5)
            
            # Check if we're logged in
            if "feed" in self.driver.current_url or "in/" in self.driver.current_url:
                self.logger.info("Successfully logged into LinkedIn")
                return True
            else:
                self.logger.warning("Login may have failed or requires additional verification")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to login to LinkedIn: {str(e)}")
            return False
    
    def scrape_profile(self, profile_url: str) -> Optional[Dict]:
        """Scrape a single LinkedIn profile."""
        try:
            self.rate_limiter.wait_if_needed()
            
            self.logger.info(f"Scraping profile: {profile_url}")
            self.driver.get(profile_url)
            
            # Wait for page to load
            random_delay(3, 7)
            
            # Check for various blocking scenarios
            current_url = self.driver.current_url.lower()
            page_source = self.driver.page_source.lower()
            
            if any(keyword in current_url for keyword in ["authwall", "login", "signup", "checkpoint"]):
                self.logger.warning(f"Hit login wall for {profile_url}")
                # Try to extract limited data anyway
                profile_data = self._extract_limited_data_from_title()
                if profile_data and profile_data.get('name'):
                    profile_data['profile_url'] = profile_url
                    profile_data['extraction_method'] = 'limited'
                    return profile_data
                return None
            
            # Check for access restrictions in page content
            if any(keyword in page_source for keyword in ["sign in", "join linkedin", "this profile", "unavailable"]):
                self.logger.warning(f"Profile may be restricted: {profile_url}")
                # Still try to extract what we can
            
            # Extract profile data
            profile_data = self._extract_profile_data()
            profile_data['profile_url'] = profile_url
            
            # Check if we got meaningful data
            meaningful_fields = ['name', 'headline', 'about']
            has_data = any(profile_data.get(field) for field in meaningful_fields)
            
            if has_data:
                self.logger.info(f"Successfully scraped profile: {profile_data.get('name', 'Unknown')}")
                return profile_data
            else:
                self.logger.warning(f"No meaningful data extracted for: {profile_url}")
                # Return basic profile data anyway
                profile_data['extraction_status'] = 'limited_data'
                return profile_data
            
        except TimeoutException:
            self.logger.error(f"Timeout while loading profile: {profile_url}")
        except Exception as e:
            self.logger.error(f"Error scraping profile {profile_url}: {str(e)}")
        
        return None
    
    def _extract_profile_data(self) -> Dict:
        """Extract comprehensive profile data from the current page."""
        data = {}
        
        try:
            # Wait a bit for page to load completely
            time.sleep(3)
            
            # Scroll down to load more content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Check if we're on an actual profile page
            page_source = self.driver.page_source.lower()
            if 'sign in' in page_source or 'join now' in page_source:
                self.logger.warning("Page requires authentication")
                return self._extract_limited_data_from_title()
            
            # === Basic Profile Information ===
            data.update(self._extract_basic_info(soup))
            
            # === Contact Information ===
            data.update(self._extract_contact_info(soup))
            
            # === Experience Details ===
            data.update(self._extract_experience_details(soup))
            
            # === Education Details ===
            data.update(self._extract_education_details(soup))
            
            # === Skills and Endorsements ===
            data.update(self._extract_skills_details(soup))
            
            # === Certifications and Licenses ===
            data.update(self._extract_certifications(soup))
            
            # === Languages ===
            data.update(self._extract_languages(soup))
            
            # === Volunteer Experience ===
            data.update(self._extract_volunteer_experience(soup))
            
            # === Publications and Projects ===
            data.update(self._extract_publications_projects(soup))
            
            # === Additional Profile Metrics ===
            data.update(self._extract_profile_metrics(soup))
            
            # Try alternative extraction if main fields are empty
            if not any([data.get('name'), data.get('headline')]):
                self.logger.info("Trying alternative extraction methods...")
                alt_data = self._extract_from_page_title_and_meta()
                data.update(alt_data)
            
        except Exception as e:
            self.logger.error(f"Error extracting profile data: {str(e)}")
        
        return data
    
    def _extract_basic_info(self, soup) -> Dict:
        """Extract basic profile information."""
        data = {}
        
        # Name
        name_selectors = [
            'h1.text-heading-xlarge.inline.t-24.v-align-middle.break-words',
            'h1[class*="text-heading-xlarge"]',
            'h1.break-words',
            '.pv-text-details__left-panel h1',
            '.ph5 h1',
            'h1'
        ]
        data['name'] = self._find_text_by_selectors(soup, name_selectors)
        
        # Headline
        headline_selectors = [
            '.text-body-medium.break-words',
            'div[class*="text-body-medium"][class*="break-words"]',
            '.pv-text-details__left-panel .text-body-medium',
            '.ph5 .text-body-medium',
            '[data-generated-suggestion-target]'
        ]
        data['headline'] = self._find_text_by_selectors(soup, headline_selectors)
        
        # Location
        location_selectors = [
            '.text-body-small.inline.t-black--light.break-words',
            'span[class*="text-body-small"][class*="t-black--light"]',
            '.pv-text-details__left-panel .text-body-small',
            '.ph5 .text-body-small',
            '.pv-top-card-profile-picture + div span.text-body-small'
        ]
        data['location'] = self._find_text_by_selectors(soup, location_selectors)
        
        # About section
        about_selectors = [
            '.pv-shared-text-with-see-more .full-width',
            '.pv-about__summary-text .full-width',
            '#about .full-width',
            '[class*="pv-about"] [class*="full-width"]',
            '.core-section-container__content .pv-shared-text-with-see-more',
            '.about-section .pv-shared-text-with-see-more'
        ]
        data['about'] = self._find_text_by_selectors(soup, about_selectors)
        
        # Connections count
        connections_selectors = [
            '.t-black--light .t-normal',
            '.pv-top-card--list-bullet li span',
            '.pv-top-card-v2-ctas .t-black--light',
            '.pv-top-card-profile-picture + div span.t-black--light',
            '[class*="t-black--light"] span'
        ]
        connections_text = self._find_text_by_selectors(soup, connections_selectors)
        data['connections'] = self._extract_connections_count(connections_text)
        
        # Profile picture URL
        img_selectors = [
            '.pv-top-card-profile-picture img',
            '.profile-photo-edit img',
            '.pv-top-card__photo img'
        ]
        for selector in img_selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                data['profile_picture_url'] = img.get('src')
                break
        else:
            data['profile_picture_url'] = ''
        
        return data
    
    def _extract_contact_info(self, soup) -> Dict:
        """Extract contact information."""
        data = {}
        
        # Try to find contact info in various places
        contact_selectors = [
            '.pv-contact-info__contact-type',
            '.ci-vanity-url',
            '.ci-email',
            '.ci-phone',
            '.ci-websites'
        ]
        
        # Email (sometimes visible)
        email_text = soup.get_text()
        import re
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_text)
        data['email'] = email_match.group() if email_match else ''
        
        # Phone (sometimes visible)
        phone_match = re.search(r'[\+]?[1-9]?[\d\s\-\(\)]{7,15}', email_text)
        data['phone'] = phone_match.group().strip() if phone_match else ''
        
        # Website/Portfolio
        website_selectors = [
            '.pv-contact-info__contact-type a[href*="http"]',
            '.ci-websites a'
        ]
        data['website'] = ''
        for selector in website_selectors:
            link = soup.select_one(selector)
            if link and link.get('href'):
                data['website'] = link.get('href')
                break
        
        return data
    
    def _extract_experience_details(self, soup) -> Dict:
        """Extract detailed experience information."""
        data = {}
        
        # Current position
        current_job_selectors = [
            '.experience-section .pv-entity__summary-info h3',
            '.pvs-list__paged-list-item .mr1.t-bold span[aria-hidden="true"]',
            '[data-field="experience"] .pvs-entity__summary-title a span[aria-hidden="true"]'
        ]
        data['current_position'] = self._find_text_by_selectors(soup, current_job_selectors)
        
        # Current company
        company_selectors = [
            '.experience-section .pv-entity__secondary-title',
            '.pvs-list__paged-list-item .t-14 span[aria-hidden="true"]',
            '[data-field="experience"] .t-14.t-normal span[aria-hidden="true"]'
        ]
        data['current_company'] = self._find_text_by_selectors(soup, company_selectors)
        
        # Employment duration
        duration_selectors = [
            '.experience-section .pv-entity__bullet-item-v2',
            '.pvs-list__paged-list-item .t-black--light span[aria-hidden="true"]',
            '[data-field="experience"] .pvs-entity__caption-wrapper'
        ]
        data['employment_duration'] = self._find_text_by_selectors(soup, duration_selectors)
        
        # All experience entries (up to 5)
        experience_entries = []
        exp_items = soup.select('.pvs-list__paged-list-item, .pv-entity__position-group-pager li')
        
        for i, item in enumerate(exp_items[:5]):
            entry = {}
            
            # Job title
            title_elem = item.select_one('.mr1.t-bold span[aria-hidden="true"], h3')
            entry['job_title'] = title_elem.get_text(strip=True) if title_elem else ''
            
            # Company
            company_elem = item.select_one('.t-14.t-normal span[aria-hidden="true"], .pv-entity__secondary-title')
            entry['company'] = company_elem.get_text(strip=True) if company_elem else ''
            
            # Duration
            duration_elem = item.select_one('.t-black--light span[aria-hidden="true"], .pv-entity__bullet-item')
            entry['duration'] = duration_elem.get_text(strip=True) if duration_elem else ''
            
            # Location
            location_elem = item.select_one('.t-black--light.t-normal span[aria-hidden="true"]')
            entry['job_location'] = location_elem.get_text(strip=True) if location_elem else ''
            
            if entry['job_title']:
                experience_entries.append(entry)
        
        # Convert experience to structured format
        for i, entry in enumerate(experience_entries):
            data[f'experience_{i+1}_title'] = entry.get('job_title', '')
            data[f'experience_{i+1}_company'] = entry.get('company', '')
            data[f'experience_{i+1}_duration'] = entry.get('duration', '')
            data[f'experience_{i+1}_location'] = entry.get('job_location', '')
        
        data['total_experience_count'] = len(experience_entries)
        
        return data
    
    def _extract_education_details(self, soup) -> Dict:
        """Extract detailed education information."""
        data = {}
        
        # Education entries (up to 3)
        education_entries = []
        edu_items = soup.select('[data-field="education"] .pvs-list__paged-list-item, .education-section .pv-entity__summary-info')
        
        for i, item in enumerate(edu_items[:3]):
            entry = {}
            
            # School name
            school_elem = item.select_one('.mr1.t-bold span[aria-hidden="true"], h3')
            entry['school'] = school_elem.get_text(strip=True) if school_elem else ''
            
            # Degree
            degree_elem = item.select_one('.t-14.t-normal span[aria-hidden="true"], .pv-entity__degree-name')
            entry['degree'] = degree_elem.get_text(strip=True) if degree_elem else ''
            
            # Field of study
            field_elem = item.select_one('.t-14 span[aria-hidden="true"]:nth-child(2)')
            entry['field'] = field_elem.get_text(strip=True) if field_elem else ''
            
            # Years
            years_elem = item.select_one('.t-black--light span[aria-hidden="true"], .pv-entity__dates')
            entry['years'] = years_elem.get_text(strip=True) if years_elem else ''
            
            if entry['school']:
                education_entries.append(entry)
        
        # Convert education to structured format
        for i, entry in enumerate(education_entries):
            data[f'education_{i+1}_school'] = entry.get('school', '')
            data[f'education_{i+1}_degree'] = entry.get('degree', '')
            data[f'education_{i+1}_field'] = entry.get('field', '')
            data[f'education_{i+1}_years'] = entry.get('years', '')
        
        data['total_education_count'] = len(education_entries)
        
        return data
    
    def _extract_skills_details(self, soup) -> Dict:
        """Extract skills and endorsements."""
        data = {}
        
        skills = []
        skill_selectors = [
            '.pv-skill-category-entity__name span[aria-hidden="true"]',
            '.skill-name',
            '.pvs-skill .mr1 span[aria-hidden="true"]',
            '[data-field="skill"] .mr1 span[aria-hidden="true"]'
        ]
        
        for selector in skill_selectors:
            skill_elements = soup.select(selector)
            for skill in skill_elements[:10]:  # Get up to 10 skills
                skill_text = skill.get_text(strip=True)
                if skill_text and skill_text not in skills and len(skill_text) > 2:
                    skills.append(skill_text)
            if len(skills) >= 10:
                break
        
        data['skills_list'] = ' | '.join(skills) if skills else ''
        data['skills_count'] = len(skills)
        
        # Top 5 skills as separate columns
        for i in range(5):
            data[f'skill_{i+1}'] = skills[i] if i < len(skills) else ''
        
        return data
    
    def _extract_certifications(self, soup) -> Dict:
        """Extract certifications and licenses."""
        data = {}
        
        certifications = []
        cert_selectors = [
            '[data-field="certification"] .mr1 span[aria-hidden="true"]',
            '.pv-accomplishments-block .pv-accomplishment-entity h4',
            '.certifications .pv-entity__summary-title'
        ]
        
        for selector in cert_selectors:
            cert_elements = soup.select(selector)
            for cert in cert_elements[:5]:  # Get up to 5 certifications
                cert_text = cert.get_text(strip=True)
                if cert_text and cert_text not in certifications and len(cert_text) > 3:
                    certifications.append(cert_text)
            if certifications:
                break
        
        data['certifications'] = ' | '.join(certifications) if certifications else ''
        data['certifications_count'] = len(certifications)
        
        return data
    
    def _extract_languages(self, soup) -> Dict:
        """Extract languages."""
        data = {}
        
        languages = []
        lang_selectors = [
            '[data-field="language"] .mr1 span[aria-hidden="true"]',
            '.languages .pv-accomplishment-entity h4'
        ]
        
        for selector in lang_selectors:
            lang_elements = soup.select(selector)
            for lang in lang_elements[:5]:
                lang_text = lang.get_text(strip=True)
                if lang_text and lang_text not in languages:
                    languages.append(lang_text)
        
        data['languages'] = ' | '.join(languages) if languages else ''
        data['languages_count'] = len(languages)
        
        return data
    
    def _extract_volunteer_experience(self, soup) -> Dict:
        """Extract volunteer experience."""
        data = {}
        
        volunteer_items = soup.select('[data-field="volunteer"] .pvs-list__paged-list-item')
        volunteer_entries = []
        
        for item in volunteer_items[:3]:  # Up to 3 volunteer experiences
            vol_title = item.select_one('.mr1.t-bold span[aria-hidden="true"]')
            vol_org = item.select_one('.t-14.t-normal span[aria-hidden="true"]')
            
            if vol_title:
                entry = {
                    'title': vol_title.get_text(strip=True),
                    'organization': vol_org.get_text(strip=True) if vol_org else ''
                }
                volunteer_entries.append(entry)
        
        data['volunteer_experience'] = ' | '.join([f"{v['title']} at {v['organization']}" for v in volunteer_entries]) if volunteer_entries else ''
        data['volunteer_count'] = len(volunteer_entries)
        
        return data
    
    def _extract_publications_projects(self, soup) -> Dict:
        """Extract publications and projects."""
        data = {}
        
        # Publications
        publications = []
        pub_selectors = [
            '[data-field="publication"] .mr1 span[aria-hidden="true"]',
            '.publications .pv-accomplishment-entity h4'
        ]
        
        for selector in pub_selectors:
            pub_elements = soup.select(selector)
            for pub in pub_elements[:3]:
                pub_text = pub.get_text(strip=True)
                if pub_text and len(pub_text) > 5:
                    publications.append(pub_text)
        
        data['publications'] = ' | '.join(publications) if publications else ''
        data['publications_count'] = len(publications)
        
        # Projects
        projects = []
        proj_selectors = [
            '[data-field="project"] .mr1 span[aria-hidden="true"]',
            '.projects .pv-accomplishment-entity h4'
        ]
        
        for selector in proj_selectors:
            proj_elements = soup.select(selector)
            for proj in proj_elements[:3]:
                proj_text = proj.get_text(strip=True)
                if proj_text and len(proj_text) > 5:
                    projects.append(proj_text)
        
        data['projects'] = ' | '.join(projects) if projects else ''
        data['projects_count'] = len(projects)
        
        return data
    
    def _extract_profile_metrics(self, soup) -> Dict:
        """Extract additional profile metrics."""
        data = {}
        
        # Follower count (if visible)
        follower_selectors = [
            '.pv-recent-activity-section__follower-count',
            '.follower-count',
            '[data-field="follower"]'
        ]
        data['followers'] = self._find_text_by_selectors(soup, follower_selectors)
        
        # Activity/Posts count
        activity_selectors = [
            '.pv-recent-activity-section__posts-count',
            '.activity-count'
        ]
        data['activity_posts'] = self._find_text_by_selectors(soup, activity_selectors)
        
        # Profile completeness indicators
        page_text = soup.get_text().lower()
        data['profile_completeness_indicators'] = {
            'has_about': 'about' in page_text and len(data.get('about', '')) > 50,
            'has_experience': 'experience' in page_text,
            'has_education': 'education' in page_text,
            'has_skills': 'skills' in page_text,
            'has_profile_picture': bool(data.get('profile_picture_url'))
        }
        
        return data
    
    def _extract_limited_data_from_title(self) -> Dict:
        """Extract limited data from page title when full page isn't accessible."""
        data = {}
        try:
            title = self.driver.title
            if title and '|' in title:
                # LinkedIn titles are usually "Name | Headline | LinkedIn"
                parts = [part.strip() for part in title.split('|')]
                if len(parts) >= 2:
                    data['name'] = parts[0]
                    data['headline'] = parts[1]
            elif title and title != 'LinkedIn':
                data['name'] = title.replace(' | LinkedIn', '').strip()
        except Exception as e:
            self.logger.debug(f"Error extracting from title: {str(e)}")
        return data
    
    def _extract_from_page_title_and_meta(self) -> Dict:
        """Extract data from page title and meta tags."""
        data = {}
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Try meta tags
            og_title = soup.find('meta', property='og:title')
            og_description = soup.find('meta', property='og:description')
            
            if og_title:
                title_content = og_title.get('content', '')
                if '|' in title_content:
                    parts = [part.strip() for part in title_content.split('|')]
                    if len(parts) >= 2:
                        data['name'] = parts[0]
                        data['headline'] = parts[1]
            
            if og_description:
                data['about'] = og_description.get('content', '')[:200]  # Limit length
                
        except Exception as e:
            self.logger.debug(f"Error extracting from meta: {str(e)}")
        
        return data
    
    def _find_text_by_selectors(self, soup, selectors: List[str]) -> str:
        """Try multiple CSS selectors to find text content."""
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element and element.get_text(strip=True):
                    return element.get_text(strip=True)
            except Exception:
                continue
        return ''
    
    def _extract_connections_count(self, text: str) -> str:
        """Extract connection count from text."""
        if not text:
            return ''
        
        import re
        # Look for patterns like "500+ connections"
        match = re.search(r'(\d+\+?)\s+connections?', text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return text
    
    def scrape_profiles(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple LinkedIn profiles."""
        if not self.driver:
            self.setup_driver()
        
        # Attempt login if configured
        if self.config.get('linkedin', {}).get('auto_login', False):
            self.login_to_linkedin()
        
        profiles = []
        total_urls = len(urls)
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Processing {i}/{total_urls}: {url}")
            
            profile_data = self.scrape_profile(url)
            if profile_data:
                profiles.append(profile_data)
            
            # Add delay between profiles
            delay = self.config.get('scraping', {}).get('delay_between_requests', 3)
            random_delay(delay, delay * 2)
        
        return profiles
    
    def save_to_csv(self, profiles: List[Dict], filename: str):
        """Save scraped profiles to CSV file with structured columns."""
        if not profiles:
            self.logger.warning("No profiles to save")
            return
        
        # Ensure output directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Define preferred column order for better CSV structure
        preferred_columns = [
            'name', 'headline', 'location', 'about', 'connections', 
            'profile_picture_url', 'email', 'phone', 'website',
            'current_position', 'current_company', 'employment_duration',
            'experience_1_title', 'experience_1_company', 'experience_1_duration', 'experience_1_location',
            'experience_2_title', 'experience_2_company', 'experience_2_duration', 'experience_2_location',
            'experience_3_title', 'experience_3_company', 'experience_3_duration', 'experience_3_location',
            'total_experience_count',
            'education_1_school', 'education_1_degree', 'education_1_field', 'education_1_years',
            'education_2_school', 'education_2_degree', 'education_2_field', 'education_2_years',
            'education_3_school', 'education_3_degree', 'education_3_field', 'education_3_years',
            'total_education_count',
            'skills_list', 'skills_count', 'skill_1', 'skill_2', 'skill_3', 'skill_4', 'skill_5',
            'certifications', 'certifications_count',
            'languages', 'languages_count',
            'volunteer_experience', 'volunteer_count',
            'publications', 'publications_count',
            'projects', 'projects_count',
            'followers', 'activity_posts',
            'profile_url'
        ]
        
        # Get all field names from profiles
        all_fields = set()
        for profile in profiles:
            all_fields.update(profile.keys())
        
        # Create ordered fieldnames: preferred columns first, then any additional ones
        fieldnames = []
        for col in preferred_columns:
            if col in all_fields:
                fieldnames.append(col)
        
        # Add any additional fields not in preferred list
        for field in sorted(all_fields):
            if field not in fieldnames:
                fieldnames.append(field)
        
        # Clean and prepare data
        cleaned_profiles = []
        for profile in profiles:
            cleaned_profile = {}
            for field in fieldnames:
                value = profile.get(field, '')
                # Clean the value
                if isinstance(value, str):
                    value = value.strip()
                    # Remove excessive whitespace
                    value = ' '.join(value.split())
                    # Limit very long text fields
                    if field == 'about' and len(value) > 1000:
                        value = value[:1000] + '...'
                elif isinstance(value, dict):
                    # Convert dict to string representation
                    value = str(value)
                
                cleaned_profile[field] = value
            cleaned_profiles.append(cleaned_profile)
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(cleaned_profiles)
            
            self.logger.info(f"Saved {len(profiles)} profiles to {filename}")
            
            # Also create an Excel file for better viewing
            try:
                import pandas as pd
                excel_filename = filename.replace('.csv', '.xlsx')
                df = pd.DataFrame(cleaned_profiles)
                df.to_excel(excel_filename, index=False, engine='openpyxl')
                self.logger.info(f"Also saved as Excel: {excel_filename}")
            except Exception as e:
                self.logger.debug(f"Could not create Excel file: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {str(e)}")
    
    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Driver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing driver: {str(e)}")