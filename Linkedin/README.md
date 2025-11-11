# LinkedIn Job Scraper

A lightweight Python script to scrape job listings from LinkedIn and save them to a CSV file using `requests` and `BeautifulSoup`.

## Features

- Scrapes job listings from LinkedIn search results
- Extracts comprehensive job details including:
  - Job title
  - Company name
  - Location
  - Posted date
  - Job description
  - Job URL and ID
  - Seniority level
  - Employment type
  - Job functions
  - Industries
- Option to fetch full job details from individual job pages
- Saves results to CSV with timestamp
- No browser required - uses HTTP requests directly

## Prerequisites

- Python 3.7 or higher
- Internet connection

## Installation

1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

Alternatively, install manually:

```bash
pip install requests beautifulsoup4 lxml
```

## Usage

### Basic Usage

Simply run the script:

```bash
python linkedin_job_scraper.py
```

The script will:
1. Fetch the LinkedIn job search URL
2. Extract job details from the search results page
3. Save the results to a CSV file named `linkedin_jobs_YYYYMMDD_HHMMSS.csv`

### Fetch Full Job Details

To fetch complete job descriptions and additional details from individual job pages (slower but more complete):

Edit the script and change:
```python
jobs = scraper.scrape_jobs(fetch_full_details=True)
```

### Custom URL

To scrape a different search, edit the `url` variable in the `main()` function:

```python
url = "YOUR_LINKEDIN_SEARCH_URL_HERE"
```

### Custom Output Filename

To specify a custom output filename, modify the `save_to_csv()` call:

```python
scraper.save_to_csv("my_custom_filename.csv")
```

## Output

The script generates a CSV file with the following columns:

- `job_id`: LinkedIn job ID
- `title`: Job title
- `company`: Company name
- `location`: Job location
- `posted_date`: When the job was posted
- `job_url`: Direct link to the job posting
- `description`: Full job description
- `seniority_level`: Required seniority level
- `employment_type`: Full-time, Part-time, Contract, etc.
- `job_function`: Job function category
- `industries`: Related industries

## Notes

- **LinkedIn Rate Limiting**: LinkedIn may block excessive requests. The script includes delays to minimize this risk, but use responsibly.
- **Authentication**: Some job details require LinkedIn authentication. This script works with publicly available data only.
- **Dynamic Content**: LinkedIn's HTML structure may change over time, which could require updates to the CSS selectors.
- **Legal Considerations**: Make sure to comply with LinkedIn's Terms of Service and robots.txt when scraping.
- **Success Rate**: LinkedIn actively works to prevent scraping. Results may vary and the script may need adjustments over time.

## Troubleshooting

### No Jobs Found

If the script doesn't find any jobs:
- Check that the URL is correct and accessible in a browser
- LinkedIn may be blocking automated access
- Try adding cookies from an authenticated session
- The HTML structure may have changed - inspect the page source

### Connection Errors

If you get connection errors:
- Check your internet connection
- LinkedIn may be rate-limiting your requests
- Try adding longer delays between requests
- Consider using a proxy or VPN

### Empty Descriptions

If job descriptions are empty:
- Set `fetch_full_details=True` to fetch from individual job pages
- Note that this will be slower as it makes one request per job
- Some jobs may require authentication to view full details

## Customization

You can customize the script by:

1. **Modifying CSS Selectors**: Update the selectors in `extract_job_details()` if LinkedIn's HTML changes
2. **Adding More Fields**: Extract additional data points by finding their CSS selectors
3. **Adding Request Delays**: Adjust `time.sleep()` values to change request frequency
4. **Adding Authentication**: Add cookies or session tokens to access authenticated content
5. **Using Proxies**: Configure the requests session to use proxies for better reliability

## Example Output

```
==============================================================
LinkedIn Job Scraper
==============================================================
Fetching URL: https://www.linkedin.com/jobs/search/...
Found 25 job listings

Extracting job details...
Scraped job 1: Embedded Hardware Engineer at TechCorp
Scraped job 2: Senior Hardware Engineer at InnovateTech
...

Successfully scraped 25 jobs!
Successfully saved 25 jobs to 'linkedin_jobs_20251111_143022.csv'
```

## License

This script is for educational purposes only. Make sure to comply with LinkedIn's Terms of Service.
