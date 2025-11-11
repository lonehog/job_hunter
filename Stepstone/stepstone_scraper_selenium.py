"""
Stepstone Job Scraper with Selenium
Scrapes Embedded Hardware jobs from Stepstone.de using browser automation
Handles dynamic content loading
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import time
from datetime import datetime
import re


class StepstoneSeleniumScraper:
    def __init__(self, headless=True):
        """Initialize the scraper with Selenium WebDriver"""
        self.jobs = []
        self.headless = headless
        self.driver = None
        self.base_url = "https://www.stepstone.de/jobs/embedded-hardware"
        
    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✓ Chrome WebDriver initialized successfully")
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            print("Make sure you have Chrome and ChromeDriver installed!")
            raise
    
    def close_cookie_banner(self):
        """Try to close cookie consent banner if present"""
        try:
            # Wait for cookie banner and try to accept
            cookie_buttons = [
                "//button[contains(text(), 'Alle akzeptieren')]",
                "//button[contains(text(), 'Accept')]",
                "//button[@id='ccmgt_explicit_accept']",
                "//button[contains(@class, 'accept')]"
            ]
            
            for xpath in cookie_buttons:
                try:
                    button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    button.click()
                    print("✓ Cookie banner accepted")
                    time.sleep(1)
                    return
                except:
                    continue
        except Exception as e:
            print("No cookie banner found or already dismissed")
    
    def get_page(self, page_number=1):
        """Navigate to a specific page"""
        url = self.base_url
        params = f"?action=facet_selected%3Bage%3Bage_1&q=Embedded+Hardware+&ag=age_1&searchOrigin=Resultlist_top-search"
        
        if page_number > 1:
            params += f"&page={page_number}"
        
        full_url = url + params
        
        try:
            print(f"Loading page {page_number}...")
            self.driver.get(full_url)
            
            # Wait for job listings to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Close cookie banner on first page
            if page_number == 1:
                self.close_cookie_banner()
            
            # Scroll to load all content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            
            return True
        except TimeoutException:
            print(f"Timeout loading page {page_number}")
            return False
        except Exception as e:
            print(f"Error loading page {page_number}: {e}")
            return False
    
    def extract_job_data(self, job_element):
        """Extract job information from a job element"""
        job = {
            'title': '',
            'company': '',
            'location': '',
            'posted_date': '',
            'job_url': '',
            'job_type': '',
            'remote_option': '',
            'salary_info': '',
            'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Extract job title and URL
            try:
                title_element = job_element.find_element(By.CSS_SELECTOR, 'h2 a, h3 a, a[href*="stellenangebote"]')
                job['title'] = title_element.text.strip()
                job['job_url'] = title_element.get_attribute('href')
            except NoSuchElementException:
                pass
            
            # Extract company name
            try:
                company_element = job_element.find_element(By.CSS_SELECTOR, 'a[href*="/cmp/"]')
                job['company'] = company_element.text.strip()
            except NoSuchElementException:
                pass
            
            # Get all text from the job element for parsing
            full_text = job_element.text
            
            # Extract location (usually before certain keywords)
            location_match = re.search(r'([A-ZÄÖÜ][a-zäöüß\-]+(?:\s+[a-zäöüß\-]+)*(?:\s+\([^)]+\))?)\s*(?:Teilweise|Gehalt|vor|$)', full_text)
            if location_match:
                job['location'] = location_match.group(1).strip()
            
            # Extract posting date
            date_match = re.search(r'vor\s+(\d+\s+\w+|gestern|heute)', full_text, re.IGNORECASE)
            if date_match:
                job['posted_date'] = date_match.group(0)
            elif 'NEU' in full_text:
                job['posted_date'] = 'NEU'
            
            # Check for remote/home office
            if 'Teilweise Home-Office' in full_text:
                job['remote_option'] = 'Teilweise Home-Office'
            elif 'Remote' in full_text:
                job['remote_option'] = 'Remote'
            else:
                job['remote_option'] = 'Vor Ort'
            
            # Check for salary info
            if 'Gehalt anzeigen' in full_text:
                job['salary_info'] = 'Gehalt verfügbar'
            
            # Determine job type
            if 'Teilzeit' in full_text:
                job['job_type'] = 'Teilzeit'
            elif 'Werkstudent' in full_text or 'Working Student' in full_text:
                job['job_type'] = 'Werkstudent'
            elif 'Freelance' in full_text or 'Freier' in full_text:
                job['job_type'] = 'Freelance'
            elif 'Duales Studium' in full_text:
                job['job_type'] = 'Duales Studium'
            else:
                job['job_type'] = 'Vollzeit'
            
        except Exception as e:
            print(f"Error extracting job data: {e}")
        
        return job
    
    def scrape_page(self):
        """Scrape all jobs from current page"""
        jobs_on_page = []
        
        try:
            # Find all job article elements
            job_elements = self.driver.find_elements(By.TAG_NAME, 'article')
            
            print(f"Found {len(job_elements)} job elements on page")
            
            for job_element in job_elements:
                job_data = self.extract_job_data(job_element)
                
                # Only add if we have at least a title
                if job_data['title']:
                    jobs_on_page.append(job_data)
            
        except Exception as e:
            print(f"Error scraping page: {e}")
        
        return jobs_on_page
    
    def scrape_all_pages(self, max_pages=12):
        """Scrape all available pages"""
        print(f"\nStarting scrape of up to {max_pages} pages...")
        print("="*60)
        
        if not self.driver:
            self.setup_driver()
        
        for page_num in range(1, max_pages + 1):
            print(f"\n📄 Page {page_num}/{max_pages}")
            
            if not self.get_page(page_num):
                print(f"Failed to load page {page_num}. Stopping.")
                break
            
            jobs_on_page = self.scrape_page()
            
            if not jobs_on_page:
                print(f"No jobs found on page {page_num}. Stopping.")
                break
            
            self.jobs.extend(jobs_on_page)
            print(f"✓ Found {len(jobs_on_page)} jobs on page {page_num}")
            print(f"📊 Total jobs scraped so far: {len(self.jobs)}")
            
            # Wait between pages
            if page_num < max_pages:
                time.sleep(2)
        
        print("\n" + "="*60)
        print(f"✓ Scraping complete! Total jobs found: {len(self.jobs)}")
        print("="*60)
        
        return self.jobs
    
    def save_to_csv(self, filename='stepstone_jobs.csv'):
        """Save scraped jobs to CSV file"""
        if not self.jobs:
            print("No jobs to save!")
            return
        
        fieldnames = ['title', 'company', 'location', 'posted_date', 'job_type', 
                     'remote_option', 'salary_info', 'job_url', 'scraped_date']
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.jobs)
            
            print(f"\n✓ Successfully saved {len(self.jobs)} jobs to {filename}")
            print(f"📁 File location: {filename}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def print_summary(self):
        """Print a summary of scraped jobs"""
        if not self.jobs:
            print("No jobs scraped yet!")
            return
        
        print("\n" + "="*60)
        print("📊 SCRAPING SUMMARY")
        print("="*60)
        print(f"Total jobs scraped: {len(self.jobs)}")
        
        # Count by company
        companies = {}
        for job in self.jobs:
            company = job['company'] or 'Unknown'
            companies[company] = companies.get(company, 0) + 1
        
        print(f"\n🏢 Top 10 Companies:")
        for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {company}: {count} job(s)")
        
        # Count by location
        locations = {}
        for job in self.jobs:
            location = job['location'] or 'Unknown'
            locations[location] = locations.get(location, 0) + 1
        
        print(f"\n📍 Top 10 Locations:")
        for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {location}: {count} job(s)")
        
        # Count by remote option
        remote = {}
        for job in self.jobs:
            remote_opt = job['remote_option']
            remote[remote_opt] = remote.get(remote_opt, 0) + 1
        
        print(f"\n🏠 Remote Options:")
        for opt, count in sorted(remote.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {opt}: {count} job(s)")
        
        # Count by job type
        job_types = {}
        for job in self.jobs:
            jtype = job['job_type']
            job_types[jtype] = job_types.get(jtype, 0) + 1
        
        print(f"\n💼 Job Types:")
        for jtype, count in sorted(job_types.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {jtype}: {count} job(s)")
        
        print("="*60 + "\n")
    
    def cleanup(self):
        """Close the browser and cleanup"""
        if self.driver:
            self.driver.quit()
            print("✓ Browser closed")


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("🔍 STEPSTONE JOB SCRAPER (SELENIUM)")
    print("Embedded Hardware Jobs (Last 24 hours)")
    print("="*60)
    
    scraper = StepstoneSeleniumScraper(headless=False)  # Set to True for headless mode
    
    try:
        # Setup WebDriver
        scraper.setup_driver()
        
        # Scrape all pages
        scraper.scrape_all_pages(max_pages=12)
        
        # Print summary
        scraper.print_summary()
        
        # Save to CSV with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'stepstone_embedded_hardware_jobs_{timestamp}.csv'
        scraper.save_to_csv(filename)
        
        print("\n✓ Done! Check the CSV file for all job listings.")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        # Always cleanup
        scraper.cleanup()


if __name__ == "__main__":
    main()
