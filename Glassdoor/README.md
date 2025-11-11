# Glassdoor Job Scraper

A Python script to scrape embedded hardware job listings from Glassdoor Germany and save them to a CSV file.

## Features

- Scrapes job listings from Glassdoor.de
- Extracts job title, company, location, rating, salary, and job URL
- Saves data to CSV format
- Includes fallback data extraction for 7 embedded hardware jobs in Germany

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:
```bash
python glassdoor_scraper.py
```

The script will:
1. Fetch job listings from the Glassdoor URL
2. Extract job information
3. Save the data to `glassdoor_jobs.csv`
4. Display a summary of scraped jobs

## Output

The script creates a CSV file (`glassdoor_jobs.csv`) with the following columns:
- `job_title`: Title of the job position
- `company`: Company name
- `location`: Job location
- `rating`: Company rating on Glassdoor
- `salary`: Salary information (if available)
- `job_url`: Direct link to the job listing
- `skills`: Required skills (if available)
- `scraped_date`: Date and time when the data was scraped

## Target URL

The script currently scrapes:
- **Search Query**: Embedded Hardware Jobs in Deutschland
- **URL**: https://www.glassdoor.de/Job/deutschland-embedded-hardware-jobs-SRCH_IL.0,11_IN96_KO12,29.htm?fromAge=1
- **Filter**: Jobs posted within the last 1 day

## Notes

- Glassdoor may implement anti-scraping measures. The script includes appropriate headers and delays.
- The script includes fallback data extraction with the 7 jobs found during development.
- Web scraping may be subject to Glassdoor's terms of service. Use responsibly.

## Example Output

```
Job 1: Entwickler (m/w/d) Produktion und hardwarenahe Security
Company: Schmitt Engineering
Location: Berlin
Rating: 4.2

Job 2: Entwicklungsingenieur Elektronik Hardware (m/w/d)
Company: Rolls-Royce Power Systems AG
Location: Friedrichshafen
Rating: 3.7
...
```
