#!/usr/bin/env python3
"""
LinkedIn Job Scraper
Scrapes job listings from LinkedIn and saves them to a CSV file.
"""

import csv
import time
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup


class LinkedInJobScraper:
    def __init__(self, url):
        """Initialize the scraper with the LinkedIn search URL."""
        self.url = url
        self.jobs = []
        self.session = requests.Session()
        
        # Set up headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def fetch_page(self, url):
        """Fetch a page and return the BeautifulSoup object."""
        try:
            print(f"Fetching URL: {url}")
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {str(e)}")
            return None
    
    def extract_job_cards(self, soup):
        """Extract all job card elements from the page."""
        try:
            # Find all job cards
            job_cards = soup.find_all('div', class_='base-card')
            
            if not job_cards:
                # Try alternative selectors
                job_cards = soup.find_all('li', class_='jobs-search-results__list-item')
            
            if not job_cards:
                job_cards = soup.find_all('div', class_='job-search-card')
            
            print(f"Found {len(job_cards)} job listings")
            return job_cards
            
        except Exception as e:
            print(f"Error extracting job cards: {str(e)}")
            return []
    
    def clean_text(self, text):
        """Clean and normalize text."""
        if not text:
            return ""
        # Remove extra whitespace and newlines
        text = ' '.join(text.split())
        return text.strip()
    
    def extract_job_details(self, job_card, index):
        """Extract details from a single job card."""
        job_data = {
            'job_id': '',
            'title': '',
            'company': '',
            'location': '',
            'posted_date': '',
            'job_url': '',
            'description': '',
            'seniority_level': '',
            'employment_type': '',
            'job_function': '',
            'industries': ''
        }
        
        try:
            # Extract job title
            title_elem = job_card.find('h3', class_='base-search-card__title')
            if not title_elem:
                title_elem = job_card.find('a', class_='job-card-list__title')
            if not title_elem:
                title_elem = job_card.find('h3', class_='job-card-list__title')
            if title_elem:
                job_data['title'] = self.clean_text(title_elem.get_text())
            
            # Extract company name
            company_elem = job_card.find('h4', class_='base-search-card__subtitle')
            if not company_elem:
                company_elem = job_card.find('a', class_='job-card-container__company-name')
            if not company_elem:
                company_elem = job_card.find('h4', class_='job-card-container__company-name')
            if company_elem:
                job_data['company'] = self.clean_text(company_elem.get_text())
            
            # Extract location
            location_elem = job_card.find('span', class_='job-search-card__location')
            if not location_elem:
                location_elem = job_card.find('span', class_='job-card-container__metadata-item')
            if location_elem:
                job_data['location'] = self.clean_text(location_elem.get_text())
            
            # Extract posted date
            time_elem = job_card.find('time')
            if time_elem:
                job_data['posted_date'] = time_elem.get('datetime', '') or self.clean_text(time_elem.get_text())
            
            # Extract job URL and ID
            link_elem = job_card.find('a', class_='base-card__full-link')
            if not link_elem:
                link_elem = job_card.find('a', href=re.compile(r'/jobs/view/'))
            if link_elem:
                job_url = link_elem.get('href', '')
                if job_url:
                    # Make sure URL is absolute
                    if job_url.startswith('/'):
                        job_url = 'https://www.linkedin.com' + job_url
                    job_data['job_url'] = job_url
                    
                    # Extract job ID from URL
                    job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
                    if not job_id_match:
                        job_id_match = re.search(r'currentJobId=(\d+)', job_url)
                    if job_id_match:
                        job_data['job_id'] = job_id_match.group(1)
            
            # Try to extract description snippet if available
            desc_elem = job_card.find('div', class_='base-search-card__snippet')
            if desc_elem:
                job_data['description'] = self.clean_text(desc_elem.get_text())
            
            if job_data['title']:
                print(f"Scraped job {index + 1}: {job_data['title']} at {job_data['company']}")
            
        except Exception as e:
            print(f"Error extracting job details for job {index + 1}: {str(e)}")
        
        return job_data
    
    def fetch_job_details(self, job_url, job_data):
        """Fetch full job details from individual job page."""
        try:
            soup = self.fetch_page(job_url)
            if not soup:
                return job_data
            
            # Extract full description
            desc_elem = soup.find('div', class_='show-more-less-html__markup')
            if not desc_elem:
                desc_elem = soup.find('div', class_='description__text')
            if desc_elem:
                job_data['description'] = self.clean_text(desc_elem.get_text())
            
            # Extract job criteria
            criteria_list = soup.find('ul', class_='description__job-criteria-list')
            if criteria_list:
                criteria_items = criteria_list.find_all('li')
                for item in criteria_items:
                    label_elem = item.find('h3')
                    value_elem = item.find('span')
                    
                    if label_elem and value_elem:
                        label = self.clean_text(label_elem.get_text())
                        value = self.clean_text(value_elem.get_text())
                        
                        if 'seniority' in label.lower():
                            job_data['seniority_level'] = value
                        elif 'employment type' in label.lower():
                            job_data['employment_type'] = value
                        elif 'job function' in label.lower():
                            job_data['job_function'] = value
                        elif 'industries' in label.lower():
                            job_data['industries'] = value
            
            time.sleep(1)  # Be respectful with requests
            
        except Exception as e:
            print(f"Error fetching job details: {str(e)}")
        
        return job_data
    
    def scrape_jobs(self, fetch_full_details=False):
        """Main method to scrape all jobs from the URL."""
        try:
            # Fetch the main search page
            soup = self.fetch_page(self.url)
            
            if not soup:
                print("Failed to load the search page!")
                return []
            
            # Extract job cards
            job_cards = self.extract_job_cards(soup)
            
            if not job_cards:
                print("No job listings found!")
                print("\nNote: LinkedIn may require authentication or may be blocking automated access.")
                print("Try accessing the URL in a browser to verify it works.")
                return []
            
            # Extract details from each job card
            print("\nExtracting job details...")
            for idx, job_card in enumerate(job_cards):
                job_data = self.extract_job_details(job_card, idx)
                
                # Optionally fetch full details from individual job pages
                if fetch_full_details and job_data['job_url']:
                    print(f"  Fetching full details for job {idx + 1}...")
                    job_data = self.fetch_job_details(job_data['job_url'], job_data)
                
                if job_data['title']:  # Only add if we got at least a title
                    self.jobs.append(job_data)
                
                # Add small delay to avoid rate limiting
                time.sleep(0.5)
            
            print(f"\nSuccessfully scraped {len(self.jobs)} jobs!")
            return self.jobs
            
        except Exception as e:
            print(f"Error during scraping: {str(e)}")
            return []
    
    def save_to_csv(self, filename=None):
        """Save scraped jobs to a CSV file."""
        if not self.jobs:
            print("No jobs to save!")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_jobs_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['job_id', 'title', 'company', 'location', 'posted_date', 
                             'job_url', 'description', 'seniority_level', 'employment_type',
                             'job_function', 'industries']
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for job in self.jobs:
                    writer.writerow(job)
            
            print(f"\nSuccessfully saved {len(self.jobs)} jobs to '{filename}'")
            return filename
            
        except Exception as e:
            print(f"Error saving to CSV: {str(e)}")
            return None


def main():
    """Main function to run the scraper."""
    # LinkedIn job search URL
    url = "https://www.linkedin.com/jobs/search/?currentJobId=4335475416&f_TPR=r3600&keywords=embedded%20hardware&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
    
    print("=" * 60)
    print("LinkedIn Job Scraper")
    print("=" * 60)
    
    # Create scraper instance
    scraper = LinkedInJobScraper(url)
    
    # Scrape jobs
    # Set fetch_full_details=True to get complete job descriptions (slower)
    jobs = scraper.scrape_jobs(fetch_full_details=False)
    
    # Save to CSV
    if jobs:
        scraper.save_to_csv()
    else:
        print("\nNo jobs were scraped. Please check the URL and try again.")
        print("\nNote: LinkedIn often requires authentication for full access.")
        print("The scraper works best with publicly accessible job listings.")


if __name__ == "__main__":
    main()
