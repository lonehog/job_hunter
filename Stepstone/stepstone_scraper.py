"""
Stepstone Job Scraper
Scrapes Embedded Hardware jobs from Stepstone.de and saves to CSV
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
import re
from urllib.parse import urljoin

class StepstoneScraper:
    def __init__(self):
        self.base_url = "https://www.stepstone.de/jobs/embedded-hardware"
        self.params = {
            'action': 'facet_selected:age:age_1',
            'q': 'Embedded Hardware ',
            'ag': 'age_1',
            'searchOrigin': 'Resultlist_top-search'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.jobs = []
        
    def get_page(self, page_number=1):
        """Fetch a single page of job listings"""
        params = self.params.copy()
        if page_number > 1:
            params['page'] = page_number
            
        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page {page_number}: {e}")
            return None
    
    def parse_jobs(self, html):
        """Parse job listings from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        jobs_found = []
        
        # Find all job listing containers
        # Looking for article tags or job cards
        job_articles = soup.find_all(['article', 'div'], class_=re.compile(r'job|listing|result', re.I))
        
        if not job_articles:
            # Try alternative selectors
            job_articles = soup.find_all('a', href=re.compile(r'/stellenangebote--'))
        
        for article in job_articles:
            try:
                job_data = self.extract_job_data(article)
                if job_data and job_data['title']:  # Only add if we have at least a title
                    jobs_found.append(job_data)
            except Exception as e:
                print(f"Error parsing job: {e}")
                continue
        
        return jobs_found
    
    def extract_job_data(self, element):
        """Extract job information from a job element"""
        job = {
            'title': '',
            'company': '',
            'location': '',
            'posted_date': '',
            'job_url': '',
            'job_type': '',
            'remote_option': '',
            'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Extract job URL and title
        link = element.find('a', href=re.compile(r'/stellenangebote--'))
        if link:
            job['job_url'] = urljoin('https://www.stepstone.de', link.get('href', ''))
            # Title might be in the link text or in a heading
            title_elem = link.find(['h2', 'h3', 'span']) or link
            job['title'] = title_elem.get_text(strip=True)
        else:
            # If element itself is a link
            if element.name == 'a':
                job['job_url'] = urljoin('https://www.stepstone.de', element.get('href', ''))
                title_elem = element.find(['h2', 'h3', 'span']) or element
                job['title'] = title_elem.get_text(strip=True)
        
        # Extract company name
        # Look for company link or specific class patterns
        company_elem = element.find('a', href=re.compile(r'/cmp/')) or \
                       element.find(class_=re.compile(r'company', re.I))
        if company_elem:
            job['company'] = company_elem.get_text(strip=True)
        
        # Extract location
        # Locations often come before "Gehalt" or standalone
        text_content = element.get_text()
        location_patterns = [
            r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[a-zäöüß]+)*(?:\s+\([A-ZÄÖÜ][a-zäöüß\-]+\))?)',
            r'(\w+(?:,\s*\w+)*)\s+(?:Teilweise\s+Home-Office|Gehalt|vor)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text_content)
            if match:
                potential_location = match.group(1)
                # Filter out common non-location words
                if potential_location not in ['Gehalt', 'NEU', 'Teilweise', 'Home', 'Office']:
                    job['location'] = potential_location
                    break
        
        # Extract posted date
        if 'vor' in text_content:
            date_match = re.search(r'vor\s+(\d+\s+\w+|\d+\s+\w+)', text_content)
            if date_match:
                job['posted_date'] = date_match.group(0)
        
        # Check for remote/home office options
        if 'Home-Office' in text_content or 'Teilweise Home-Office' in text_content:
            job['remote_option'] = 'Teilweise Home-Office'
        elif 'Remote' in text_content:
            job['remote_option'] = 'Remote'
        else:
            job['remote_option'] = 'Vor Ort'
        
        # Check for job type indicators
        if 'Teilzeit' in text_content:
            job['job_type'] = 'Teilzeit'
        elif 'Werkstudent' in text_content or 'Working Student' in text_content:
            job['job_type'] = 'Werkstudent'
        elif 'Freelance' in text_content or 'Freier' in text_content:
            job['job_type'] = 'Freelance'
        else:
            job['job_type'] = 'Vollzeit'
        
        return job
    
    def scrape_all_pages(self, max_pages=12):
        """Scrape all available pages"""
        print(f"Starting scrape of up to {max_pages} pages...")
        
        for page_num in range(1, max_pages + 1):
            print(f"\nScraping page {page_num}/{max_pages}...")
            
            html = self.get_page(page_num)
            if not html:
                print(f"Failed to fetch page {page_num}")
                continue
            
            jobs_on_page = self.parse_jobs(html)
            
            if not jobs_on_page:
                print(f"No jobs found on page {page_num}. Stopping.")
                break
            
            self.jobs.extend(jobs_on_page)
            print(f"Found {len(jobs_on_page)} jobs on page {page_num}. Total: {len(self.jobs)}")
            
            # Be polite - wait between requests
            if page_num < max_pages:
                time.sleep(2)
        
        print(f"\n✓ Scraping complete! Total jobs found: {len(self.jobs)}")
        return self.jobs
    
    def save_to_csv(self, filename='stepstone_jobs.csv'):
        """Save scraped jobs to CSV file"""
        if not self.jobs:
            print("No jobs to save!")
            return
        
        fieldnames = ['title', 'company', 'location', 'posted_date', 'job_type', 
                     'remote_option', 'job_url', 'scraped_date']
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.jobs)
            
            print(f"\n✓ Successfully saved {len(self.jobs)} jobs to {filename}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def print_summary(self):
        """Print a summary of scraped jobs"""
        if not self.jobs:
            print("No jobs scraped yet!")
            return
        
        print("\n" + "="*60)
        print("SCRAPING SUMMARY")
        print("="*60)
        print(f"Total jobs scraped: {len(self.jobs)}")
        
        # Count by company
        companies = {}
        for job in self.jobs:
            company = job['company'] or 'Unknown'
            companies[company] = companies.get(company, 0) + 1
        
        print(f"\nTop 5 companies:")
        for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {company}: {count} jobs")
        
        # Count by location
        locations = {}
        for job in self.jobs:
            location = job['location'] or 'Unknown'
            locations[location] = locations.get(location, 0) + 1
        
        print(f"\nTop 5 locations:")
        for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {location}: {count} jobs")
        
        # Count by remote option
        remote = {}
        for job in self.jobs:
            remote_opt = job['remote_option']
            remote[remote_opt] = remote.get(remote_opt, 0) + 1
        
        print(f"\nRemote options:")
        for opt, count in remote.items():
            print(f"  - {opt}: {count} jobs")
        
        print("="*60 + "\n")


def main():
    """Main execution function"""
    print("="*60)
    print("STEPSTONE JOB SCRAPER")
    print("Embedded Hardware Jobs (Last 24 hours)")
    print("="*60 + "\n")
    
    scraper = StepstoneScraper()
    
    # Scrape all pages (up to 12 pages based on the website)
    scraper.scrape_all_pages(max_pages=12)
    
    # Print summary
    scraper.print_summary()
    
    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'stepstone_embedded_hardware_jobs_{timestamp}.csv'
    scraper.save_to_csv(filename)
    
    print("\n✓ Done! Check the CSV file for all job listings.")


if __name__ == "__main__":
    main()
