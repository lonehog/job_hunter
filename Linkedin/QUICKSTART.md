# LinkedIn Job Scraper - Quick Start

## What Was Created

A lightweight Python web scraper that extracts job listings from LinkedIn and saves them to CSV files.

### Files Created:
1. **linkedin_job_scraper.py** - Main scraper script
2. **requirements.txt** - Python dependencies
3. **README.md** - Comprehensive documentation
4. **example_usage.py** - Example usage patterns

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Scraper
```bash
python linkedin_job_scraper.py
```

This will scrape the embedded hardware jobs from your URL and save them to a CSV file.

## What It Does

The script:
- ✅ Fetches job listings from LinkedIn search results
- ✅ Extracts job title, company, location, posted date, and URLs
- ✅ Optionally fetches full job descriptions (set `fetch_full_details=True`)
- ✅ Saves everything to a timestamped CSV file
- ✅ Works without a browser (uses HTTP requests directly)

## Recent Test Results

Successfully scraped **60 jobs** from your embedded hardware search!

Output file: `linkedin_jobs_20251111_170126.csv` (17KB)

Sample jobs found:
- Senior Embedded Engineer at Andiamo
- Hardware Electrical Engineer at Motorola Solutions
- Mechatronics Engineer at Lila Sciences
- Embedded System Engineer at Saxon Global
- And 56 more...

## CSV Output Columns

- job_id
- title
- company
- location
- posted_date
- job_url
- description
- seniority_level
- employment_type
- job_function
- industries

## Customization

### Change the Search URL
Edit line 235 in `linkedin_job_scraper.py`:
```python
url = "YOUR_LINKEDIN_SEARCH_URL"
```

### Get Full Job Details
Edit line 242 in `linkedin_job_scraper.py`:
```python
jobs = scraper.scrape_jobs(fetch_full_details=True)
```
Note: This is slower as it fetches each job's individual page.

### Custom Output Filename
```python
scraper.save_to_csv("my_jobs.csv")
```

## Important Notes

⚠️ **LinkedIn Limitations**
- LinkedIn actively works to prevent scraping
- Some jobs may require authentication to view
- Results may vary depending on LinkedIn's current HTML structure
- Use responsibly and respect rate limits

🔧 **No Selenium Required**
- Uses `requests` and `BeautifulSoup` instead
- Lighter weight and faster
- No browser or ChromeDriver needed

## Examples

See `example_usage.py` for advanced usage including:
- Custom search URLs
- Data analysis of scraped jobs
- Fetching full job details
- Multiple search queries

Run it with:
```bash
python example_usage.py
```

## Troubleshooting

**No jobs found?**
- LinkedIn may be blocking access
- Try the URL in a browser first to verify it works
- The HTML structure may have changed

**Want more jobs?**
- LinkedIn typically shows 25-100 jobs per search page
- Try different search URLs or pagination

**Need authentication?**
- Consider adding session cookies to the requests
- See README.md for more advanced options

## Next Steps

1. ✅ The script is ready to use
2. ✅ Test CSV file has been created
3. Customize the URL for your specific job searches
4. Run it periodically to track new job postings
5. Consider adding authentication for better results
