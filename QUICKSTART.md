# 🎯 Job Hunter - Quick Start Guide

## Overview

Job Hunter is a web application that automatically scrapes job postings from LinkedIn, Stepstone, and Glassdoor, tracking jobs posted in the **last hour** across all platforms.

## Key Features

✅ **Hourly automated scraping** from 3 job platforms
✅ **Smart tracking** of jobs posted in the last hour
✅ **Modern web dashboard** with real-time updates
✅ **4 pages**: Home, LinkedIn Jobs, Stepstone Jobs, Glassdoor Jobs

## How It Works

### LinkedIn 🔵
- Directly fetches jobs posted in **last 1 hour**
- Uses LinkedIn's time filter parameter

### Stepstone 🔴 & Glassdoor 🟢
- These platforms only show jobs from **last 24 hours**
- Our app runs scrapers **every hour**
- Compares results to find **NEW jobs** since last run
- Only shows truly new jobs (posted in last hour)

## Installation

### Step 1: Install Dependencies

```bash
cd /home/surya/Projects/job_hunter
pip install -r requirements.txt
```

### Step 2: Start the Application

**Option A: Using the startup script (Recommended)**
```bash
./start.sh
```

**Option B: Direct Python**
```bash
python run.py
```

### Step 3: Access the Web Interface

Open your browser and go to:
```
http://localhost:5000
```

## Web Interface Pages

### 1. 🏠 Home Page (`/`)
- **Total jobs** across all platforms
- **New jobs in last hour** counter
- **Per-platform statistics**
- **Last scraper run** information
- **Auto-refreshes** every 60 seconds

### 2. 💼 LinkedIn Page (`/linkedin`)
- Shows jobs posted in **last 1 hour** on LinkedIn
- Direct from LinkedIn's time filter
- Real-time job listings with full details

### 3. 🔧 Stepstone Page (`/stepstone`)
- Shows **NEW** jobs detected in last hour
- Filtered from 24-hour Stepstone results
- Identified by comparing hourly scraper runs

### 4. 🚪 Glassdoor Page (`/glassdoor`)
- Shows **NEW** jobs detected in last hour
- Filtered from 24-hour Glassdoor results
- Identified by comparing hourly scraper runs

## Scheduler Schedule

The application runs scrapers automatically:

| Scraper | Time | Frequency |
|---------|------|-----------|
| LinkedIn | Every hour at :00 | Hourly |
| Stepstone | Every hour at :10 | Hourly |
| Glassdoor | Every hour at :20 | Hourly |

Example: 1:00, 1:10, 1:20, then 2:00, 2:10, 2:20...

## Manual Scraper Trigger

You can manually trigger scrapers via API:

```bash
# Trigger all scrapers
curl http://localhost:5000/api/scraper/trigger/all

# Trigger specific scraper
curl http://localhost:5000/api/scraper/trigger/linkedin
curl http://localhost:5000/api/scraper/trigger/stepstone
curl http://localhost:5000/api/scraper/trigger/glassdoor
```

## Database

Jobs are stored in SQLite database: `app/jobs.db`

### View Database

```bash
sqlite3 app/jobs.db
```

```sql
-- View all jobs
SELECT * FROM jobs;

-- View jobs from last hour
SELECT * FROM jobs WHERE is_new_in_last_hour = 1;

-- View scraper runs
SELECT * FROM scraper_runs;
```

## Troubleshooting

### Problem: No jobs appearing

**Solution:**
1. Wait for first scraper run (check scheduler logs)
2. Manually trigger: `http://localhost:5000/api/scraper/trigger/all`
3. Check if original scrapers work independently

### Problem: Scrapers failing

**Solution:**
1. Check individual scraper folders (Linkedin/, Stepstone/, Glassdoor/)
2. Test scrapers independently
3. Check error messages in web interface (Home page → Last Scraper Runs)
4. Verify URLs in `app/scraper_integration.py`

### Problem: Import errors

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Problem: Port 5000 already in use

**Solution:**
Edit `run.py` and change the port:
```python
app.run(debug=False, host='0.0.0.0', port=8000)  # Change to 8000 or any free port
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Overall statistics |
| `/api/jobs/<source>` | GET | Jobs from specific source (last hour) |
| `/api/jobs/all` | GET | All jobs (limit 1000) |
| `/api/scraper/status` | GET | Scraper run history |
| `/api/scraper/trigger/<source>` | GET | Manually trigger scraper |

## Configuration

### Change Scraper Frequency

Edit `app/scheduler.py`:

```python
# Run every 30 minutes instead of hourly
scheduler.add_job(
    func=run_all_scrapers,
    trigger=CronTrigger(minute='0,30'),  # At :00 and :30
    ...
)
```

### Enable Initial Scrape on Startup

Edit `run.py` and uncomment:

```python
# Run scrapers immediately when app starts
run_initial_scrape()
```

### Change Search Keywords

Edit `app/scraper_integration.py` and modify the URLs for each scraper.

## File Structure

```
job_hunter/
├── app/
│   ├── __init__.py
│   ├── models.py              # Database models
│   ├── app.py                 # Flask app + API
│   ├── scraper_integration.py # Scraper integration
│   └── scheduler.py           # Automated scheduling
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── linkedin.html
│   ├── stepstone.html
│   └── glassdoor.html
├── Linkedin/                  # Original LinkedIn scraper
├── Stepstone/                 # Original Stepstone scraper
├── Glassdoor/                 # Original Glassdoor scraper
├── run.py                     # Main entry point
├── start.sh                   # Startup script
├── requirements.txt           # Python dependencies
└── README.md                  # Full documentation
```

## Tips & Best Practices

1. **Let it run for 2-3 hours** to accumulate data
2. **Check Home page** to see scraper status
3. **Database grows over time** - consider cleanup script for old jobs
4. **Scrapers may fail** due to website changes - check error messages
5. **Rate limiting** - staggered schedule prevents overloading sites

## Next Steps

1. ✅ Start the application: `./start.sh`
2. ✅ Open browser: `http://localhost:5000`
3. ✅ Wait for first scraper runs (will happen automatically)
4. ✅ Check job listings on individual pages
5. ✅ Monitor statistics on home page

## Support

For issues:
1. Check `README.md` for detailed documentation
2. Review scraper logs in terminal
3. Check database for data: `sqlite3 app/jobs.db`
4. Test individual scrapers in their folders

---

**Happy Job Hunting! 🎯**
