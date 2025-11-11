# Stepstone Job Scraper

This project contains Python scripts to scrape Embedded Hardware job listings from Stepstone.de and save them to CSV files.

## 📁 Files

1. **stepstone_scraper.py** - Simple scraper using requests and BeautifulSoup
2. **stepstone_scraper_selenium.py** - Advanced scraper using Selenium for dynamic content (RECOMMENDED)
3. **requirements.txt** - Python dependencies

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. For Selenium Version (Recommended)

Install Chrome browser and ChromeDriver:

**On Ubuntu/Debian:**
```bash
# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f

# Install ChromeDriver
sudo apt-get install chromium-chromedriver
```

**On macOS:**
```bash
brew install chromedriver
```

**On Windows:**
Download ChromeDriver from: https://chromedriver.chromium.org/

### 3. Run the Scraper

**Option A: Using Selenium (Recommended):**
```bash
python stepstone_scraper_selenium.py
```

**Option B: Using Simple Scraper:**
```bash
python stepstone_scraper.py
```

## 📊 Output

The script will create a CSV file with timestamp:
- `stepstone_embedded_hardware_jobs_YYYYMMDD_HHMMSS.csv`

### CSV Columns:
- **title**: Job title
- **company**: Company name
- **location**: Job location
- **posted_date**: When the job was posted
- **job_type**: Full-time, Part-time, Student, Freelance, etc.
- **remote_option**: Remote, Hybrid, On-site
- **salary_info**: Whether salary information is available
- **job_url**: Direct link to the job posting
- **scraped_date**: When the data was scraped

## ⚙️ Configuration

### Selenium Scraper Settings

In `stepstone_scraper_selenium.py`, you can modify:

```python
# Run in headless mode (no browser window)
scraper = StepstoneSeleniumScraper(headless=True)

# Change maximum pages to scrape
scraper.scrape_all_pages(max_pages=12)
```

## 🎯 Target URL

The scraper targets jobs posted in the last 24 hours:
```
https://www.stepstone.de/jobs/embedded-hardware?action=facet_selected%3Bage%3Bage_1&q=Embedded+Hardware+&ag=age_1&searchOrigin=Resultlist_top-search
```

## 📈 Features

- ✅ Scrapes multiple pages automatically
- ✅ Extracts job title, company, location, and more
- ✅ Handles cookie consent banners
- ✅ Rate limiting to be respectful to the server
- ✅ Exports to CSV with timestamp
- ✅ Provides detailed summary statistics
- ✅ Error handling and logging

## 🔧 Troubleshooting

### ChromeDriver Issues
If you get ChromeDriver errors:
1. Make sure Chrome browser is installed
2. Ensure ChromeDriver version matches your Chrome version
3. Try updating ChromeDriver: `pip install --upgrade selenium`

### No Jobs Found
If no jobs are scraped:
1. Check your internet connection
2. The website structure may have changed
3. Try running with `headless=False` to see what's happening

### Import Errors
If you get import errors:
```bash
pip install --upgrade -r requirements.txt
```

## 📝 Example Output

```
🔍 STEPSTONE JOB SCRAPER (SELENIUM)
Embedded Hardware Jobs (Last 24 hours)
============================================================

Starting scrape of up to 12 pages...
============================================================

📄 Page 1/12
Loading page 1...
✓ Cookie banner accepted
Found 24 job elements on page
✓ Found 24 jobs on page 1
📊 Total jobs scraped so far: 24

...

============================================================
✓ Scraping complete! Total jobs found: 289
============================================================

📊 SCRAPING SUMMARY
============================================================
Total jobs scraped: 289

🏢 Top 10 Companies:
   • SKD SE: 8 job(s)
   • FERCHAU: 6 job(s)
   • Navimatix GmbH: 5 job(s)
   ...

📍 Top 10 Locations:
   • Munich: 15 job(s)
   • Berlin: 12 job(s)
   • Stuttgart: 8 job(s)
   ...

🏠 Remote Options:
   • Vor Ort: 150 job(s)
   • Teilweise Home-Office: 120 job(s)
   • Remote: 19 job(s)

💼 Job Types:
   • Vollzeit: 250 job(s)
   • Teilzeit: 25 job(s)
   • Werkstudent: 10 job(s)
   • Freelance: 4 job(s)
```

## 📄 License

This project is for educational purposes only. Please respect Stepstone's Terms of Service and robots.txt when scraping.

## ⚠️ Legal Notice

Web scraping should be done responsibly:
- This scraper includes delays between requests
- It respects the website's structure
- Use scraped data ethically and legally
- Always check the website's Terms of Service before scraping

## 🤝 Contributing

Feel free to improve the scraper! Some ideas:
- Add more data fields
- Implement proxy support
- Add job detail page scraping
- Create visualization of results
- Add database storage option

## 📧 Contact

For questions or issues, please create an issue in the repository.
