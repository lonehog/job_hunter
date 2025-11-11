# Job Hunter Web Application

A comprehensive job tracking web application that aggregates job postings from LinkedIn, Stepstone, and Glassdoor, with a focus on tracking jobs posted in the last hour.

## 🎯 Features

- **Automated Scraping**: Runs scrapers hourly for all three platforms
- **Smart Tracking**: Identifies NEW jobs posted in the last hour for each platform
- **Real-time Dashboard**: View statistics and job listings through a modern web interface
- **Four Pages**:
  - 🏠 **Home**: Overview with statistics and last scraper runs
  - 💼 **LinkedIn**: Jobs posted in last 1 hour
  - 🔧 **Stepstone**: New jobs detected in last hour
  - 🚪 **Glassdoor**: New jobs detected in last hour

## 📊 How It Works

### LinkedIn
- Scrapes jobs posted in the **last 1 hour** directly from LinkedIn
- Runs every hour at the top of the hour

### Stepstone & Glassdoor
- These platforms return jobs from the **last 24 hours**
- The application runs scrapers **every hour**
- Compares new results with previous runs to identify jobs posted in the **last hour**
- Only displays newly discovered jobs on the respective pages

## 🏗️ Project Structure

```
job_hunter/
├── app/
│   ├── models.py              # Database models (Job, ScraperRun)
│   ├── app.py                 # Flask application with API endpoints
│   ├── scraper_integration.py # Integration with existing scrapers
│   └── scheduler.py           # APScheduler for automated runs
├── templates/
│   ├── base.html             # Base template
│   ├── home.html             # Home page
│   ├── linkedin.html         # LinkedIn jobs page
│   ├── stepstone.html        # Stepstone jobs page
│   └── glassdoor.html        # Glassdoor jobs page
├── static/                    # Static files (auto-created)
├── Linkedin/                  # Existing LinkedIn scraper
├── Stepstone/                 # Existing Stepstone scraper
├── Glassdoor/                 # Existing Glassdoor scraper
├── run.py                     # Main application entry point
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Existing Scrapers

Make sure your existing scrapers in `Linkedin/`, `Stepstone/`, and `Glassdoor/` folders are working properly.

### 3. Run the Application

```bash
python run.py
```

The application will:
- Start the Flask web server on `http://localhost:5000`
- Initialize the scheduler to run scrapers every hour
- Create a SQLite database (`app/jobs.db`) to store job data

### 4. Access the Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

## 📅 Scheduler Configuration

The scheduler runs:
- **LinkedIn**: Every hour at minute 0 (e.g., 1:00, 2:00, 3:00)
- **Stepstone**: Every hour at minute 10 (e.g., 1:10, 2:10, 3:10)
- **Glassdoor**: Every hour at minute 20 (e.g., 1:20, 2:20, 3:20)

This staggered approach prevents overloading and allows time for each scraper to complete.

## 🔧 API Endpoints

### Statistics
```
GET /api/stats
```
Returns overall statistics including total jobs, new jobs in last hour, and last scraper runs.

### Jobs by Source
```
GET /api/jobs/<source>
```
Returns jobs from a specific source (linkedin, stepstone, glassdoor) that were posted in the last hour.

**Parameters:**
- `source`: One of `linkedin`, `stepstone`, or `glassdoor`

### All Jobs
```
GET /api/jobs/all
```
Returns all jobs (up to 1000 most recent).

### Scraper Status
```
GET /api/scraper/status
```
Returns status and history of scraper runs.

### Trigger Scraper
```
GET /api/scraper/trigger/<source>
```
Manually trigger a scraper run.

**Parameters:**
- `source`: One of `linkedin`, `stepstone`, `glassdoor`, or `all`

## 💾 Database

The application uses SQLite with two tables:

### Jobs Table
- `id`: Primary key
- `source`: linkedin, stepstone, or glassdoor
- `job_title`, `company`, `location`, `job_url`, etc.
- `first_seen`: When we first discovered the job
- `last_seen`: Last time we saw the job
- `is_new_in_last_hour`: Boolean flag for new jobs

### ScraperRuns Table
- `id`: Primary key
- `source`: Which scraper ran
- `start_time`, `end_time`, `status`
- `jobs_found`, `new_jobs`: Statistics
- `error_message`: Any errors that occurred

## 🎨 Customization

### Modify Scraper Frequency

Edit `app/scheduler.py` and adjust the `CronTrigger` settings:

```python
# Run every 30 minutes
scheduler.add_job(
    func=run_scraper_task,
    trigger=CronTrigger(minute='0,30'),
    ...
)
```

### Change Database Location

Edit `app/app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///path/to/your/database.db'
```

### Run Initial Scrape on Startup

In `run.py`, uncomment this line:

```python
# run_initial_scrape()
```

## 🐛 Troubleshooting

### Scrapers Not Running

1. Check if the original scrapers work independently
2. Verify the URLs in `app/scraper_integration.py`
3. Check the `ScraperRuns` table for error messages

### No Jobs Appearing

1. Wait for the first scraper run (check scheduler logs)
2. Manually trigger scrapers: `http://localhost:5000/api/scraper/trigger/all`
3. Check database: `sqlite3 app/jobs.db` then `SELECT * FROM jobs;`

### Import Errors

Make sure all scraper files are in their respective folders and have correct function/class names.

## 📝 Notes

- The application tracks jobs by their URL to avoid duplicates
- Jobs are marked as "new in last hour" based on when they first appear
- For Stepstone and Glassdoor, the app compares hourly runs to find truly new jobs
- The web interface auto-refreshes every 60 seconds

## 🔒 Security Considerations

For production deployment:
1. Change the Flask `SECRET_KEY` in `app/app.py`
2. Use a production WSGI server (gunicorn, uWSGI)
3. Set up proper authentication if needed
4. Use environment variables for configuration
5. Consider using PostgreSQL instead of SQLite

## 📄 License

This project builds upon existing job scrapers and is provided as-is for educational purposes.

## 🤝 Contributing

Feel free to enhance the scrapers, improve the UI, or add new features!

---

**Happy Job Hunting! 🎯**
