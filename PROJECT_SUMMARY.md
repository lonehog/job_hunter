# Job Hunter Web Application - Project Summary

## 🎯 Project Overview

A full-stack web application that aggregates job postings from LinkedIn, Stepstone, and Glassdoor, with intelligent tracking of jobs posted in the last hour.

## 🏗️ Architecture

### Backend (Flask + SQLAlchemy)
- **Flask** web framework with REST API
- **SQLite** database for job storage
- **APScheduler** for automated scraping
- Integration with existing Python scrapers

### Frontend (HTML/CSS/JavaScript)
- Responsive web interface
- Real-time updates (auto-refresh)
- Modern gradient design
- 4 pages: Home, LinkedIn, Stepstone, Glassdoor

### Scrapers (Existing + Integration)
- **LinkedIn**: Scrapes jobs from last 1 hour
- **Stepstone**: Scrapes jobs from last 24 hours
- **Glassdoor**: Scrapes jobs from last 24 hours
- **Smart tracking**: Compares runs to find new jobs in last hour

## 📁 Complete File Structure

```
job_hunter/
│
├── app/                                    # Main application package
│   ├── __init__.py                        # Package initializer
│   ├── models.py                          # SQLAlchemy models (Job, ScraperRun)
│   ├── app.py                             # Flask app with API endpoints
│   ├── scraper_integration.py             # Integration with existing scrapers
│   └── scheduler.py                       # APScheduler configuration
│
├── templates/                              # HTML templates (Jinja2)
│   ├── base.html                          # Base template with navigation
│   ├── home.html                          # Home page with statistics
│   ├── linkedin.html                      # LinkedIn jobs page
│   ├── stepstone.html                     # Stepstone jobs page
│   └── glassdoor.html                     # Glassdoor jobs page
│
├── static/                                 # Static files (auto-created)
│   └── (CSS/JS/images if needed)
│
├── Linkedin/                               # Existing LinkedIn scraper
│   ├── linkedin_job_scraper.py
│   ├── linkedin_jobs_20251111_170126.csv
│   ├── QUICKSTART.md
│   ├── README.md
│   └── requirements.txt
│
├── Stepstone/                              # Existing Stepstone scraper
│   ├── stepstone_scraper.py
│   ├── stepstone_scraper_selenium.py
│   ├── stepstone_embedded_hardware_jobs_20251111_164204.csv
│   ├── README.md
│   └── requirements.txt
│
├── Glassdoor/                              # Existing Glassdoor scraper
│   ├── glassdoor_scraper.py
│   ├── glassdoor_jobs.csv
│   ├── view_jobs.py
│   ├── run_scraper.sh
│   ├── README.md
│   ├── SUMMARY.md
│   └── requirements.txt
│
├── run.py                                  # Main application entry point
├── start.sh                                # Bash startup script
├── requirements.txt                        # Python dependencies
├── README.md                               # Full documentation
├── QUICKSTART.md                           # Quick start guide
└── .gitignore                              # Git ignore file
```

## 🔧 Key Components

### 1. Database Models (`app/models.py`)

#### Job Model
- Stores job listings from all platforms
- Tracks first_seen and last_seen timestamps
- Boolean flag `is_new_in_last_hour` for filtering
- Unique constraint on job_url to prevent duplicates

#### ScraperRun Model
- Tracks each scraper execution
- Records start_time, end_time, status
- Counts jobs_found and new_jobs
- Stores error_message if scraper fails

### 2. Flask Application (`app/app.py`)

#### Routes
- `/` - Home page
- `/linkedin` - LinkedIn jobs page
- `/stepstone` - Stepstone jobs page
- `/glassdoor` - Glassdoor jobs page

#### API Endpoints
- `GET /api/stats` - Overall statistics
- `GET /api/jobs/<source>` - Jobs from specific source (last hour only)
- `GET /api/jobs/all` - All jobs
- `GET /api/scraper/status` - Scraper run history
- `GET /api/scraper/trigger/<source>` - Manually trigger scraper

### 3. Scraper Integration (`app/scraper_integration.py`)

#### Functions
- `save_jobs_to_db()` - Saves jobs and marks new ones
- `run_linkedin_scraper()` - LinkedIn integration
- `run_stepstone_scraper()` - Stepstone integration
- `run_glassdoor_scraper()` - Glassdoor integration

#### Logic
1. Mark all existing jobs as not new
2. Fetch jobs from scraper
3. Check if job exists (by URL)
4. If new: Add to DB with `is_new_in_last_hour=True`
5. If exists: Update `last_seen` timestamp
6. Track statistics in ScraperRun table

### 4. Scheduler (`app/scheduler.py`)

#### Schedule
- **LinkedIn**: Every hour at :00 (e.g., 1:00, 2:00, 3:00)
- **Stepstone**: Every hour at :10 (e.g., 1:10, 2:10, 3:10)
- **Glassdoor**: Every hour at :20 (e.g., 1:20, 2:20, 3:20)

#### Features
- Background scheduler using APScheduler
- Thread-safe with locking mechanism
- Error handling and logging
- Optional initial scrape on startup

### 5. Frontend Templates

#### Base Template (`base.html`)
- Modern gradient design
- Responsive navigation
- Common styling
- Auto-refresh JavaScript

#### Page-Specific Templates
- Display job cards with details
- Real-time loading states
- Error handling
- Auto-refresh every 60 seconds

## 🔄 Data Flow

### Initial Startup
1. User runs `./start.sh` or `python run.py`
2. Flask app initializes
3. Database tables created (if not exist)
4. Scheduler starts in background thread
5. Web server starts on port 5000

### Hourly Scraper Run
1. Scheduler triggers scraper (e.g., LinkedIn at :00)
2. Create ScraperRun entry (status='running')
3. Import and run scraper module
4. Mark all existing jobs as `is_new_in_last_hour=False`
5. Fetch jobs from scraper
6. For each job:
   - Check if exists (by URL)
   - If new: Add with `is_new_in_last_hour=True`
   - If exists: Update `last_seen` timestamp
7. Update ScraperRun (status='completed', counts)
8. Commit to database

### User Views Jobs
1. User opens browser to `/linkedin` (or other page)
2. Page loads, JavaScript fetches `/api/jobs/linkedin`
3. Backend queries: `Job.query.filter_by(source='linkedin', is_new_in_last_hour=True)`
4. Returns JSON with job list
5. Frontend renders job cards
6. Auto-refresh every 60 seconds

## 🎨 Design Choices

### Why SQLite?
- Simple setup, no external database needed
- Perfect for single-user application
- Easy to backup (single file)

### Why Hourly Scraping?
- LinkedIn provides 1-hour filter natively
- Stepstone/Glassdoor: Compare runs to find new jobs
- Balance between freshness and rate limiting

### Why Mark Jobs as "New"?
- Stepstone and Glassdoor return 24-hour data
- By comparing runs, we identify truly new jobs
- Avoids showing same jobs repeatedly

### Why Staggered Schedule?
- Prevents overloading job sites
- Allows time for each scraper to complete
- Reduces chance of getting blocked

## 📊 Database Schema

### jobs Table
```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    job_title VARCHAR(500),
    company VARCHAR(500),
    location VARCHAR(500),
    job_url VARCHAR(1000) UNIQUE,
    description TEXT,
    salary VARCHAR(200),
    job_type VARCHAR(200),
    posted_date VARCHAR(200),
    first_seen DATETIME NOT NULL,
    last_seen DATETIME NOT NULL,
    is_new_in_last_hour BOOLEAN
);
```

### scraper_runs Table
```sql
CREATE TABLE scraper_runs (
    id INTEGER PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    status VARCHAR(50),
    jobs_found INTEGER,
    new_jobs INTEGER,
    error_message TEXT
);
```

## 🚀 Deployment Instructions

### Local Development
```bash
cd /home/surya/Projects/job_hunter
./start.sh
```

### Production Deployment (Example)
```bash
# Install dependencies
pip install -r requirements.txt gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

## 🔐 Security Notes

### For Production
1. Change `SECRET_KEY` in `app/app.py`
2. Use environment variables for configuration
3. Add authentication/authorization
4. Use HTTPS
5. Rate limiting on API endpoints
6. Input validation and sanitization

## 🐛 Known Limitations

1. **Scraper reliability**: Depends on website structure
2. **Rate limiting**: May get blocked if scrapers run too frequently
3. **Time zones**: Uses UTC timestamps
4. **Database size**: Will grow over time (add cleanup job)
5. **Single-threaded scrapers**: Only one scraper runs at a time

## 🔮 Future Enhancements

- [ ] Add job filtering by keywords, location, company
- [ ] Email notifications for new jobs
- [ ] Export jobs to CSV/PDF
- [ ] Job application tracking
- [ ] Favorite/bookmark jobs
- [ ] User authentication and profiles
- [ ] Multiple search queries
- [ ] Mobile app
- [ ] PostgreSQL support
- [ ] Docker containerization

## 📚 Dependencies

### Core
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-CORS 4.0.0
- SQLAlchemy 2.0.23
- APScheduler 3.10.4

### Scraping
- requests 2.31.0
- beautifulsoup4 4.12.2
- lxml 4.9.3
- selenium 4.15.2

### Utilities
- python-dateutil 2.8.2
- pytz 2023.3

## 📖 Documentation

- `README.md` - Full documentation
- `QUICKSTART.md` - Quick start guide
- `PROJECT_SUMMARY.md` - This file (architecture overview)
- Individual scraper READMEs in respective folders

## ✅ Completed Features

✅ Database models with job tracking
✅ Flask REST API with all endpoints
✅ Integration with existing scrapers
✅ Automated hourly scheduling
✅ 4-page responsive web interface
✅ Real-time statistics dashboard
✅ Smart "last hour" job detection
✅ Error handling and logging
✅ Auto-refresh functionality
✅ Manual scraper triggering
✅ Startup script
✅ Comprehensive documentation

---

**Project Status: ✅ Complete and Ready to Run**

Run `./start.sh` to get started!
