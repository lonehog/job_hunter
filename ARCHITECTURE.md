# Job Hunter - Application Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         JOB HUNTER WEB APPLICATION                       │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │   Home   │  │ LinkedIn │  │Stepstone │  │Glassdoor │               │
│  │   Page   │  │   Jobs   │  │   Jobs   │  │   Jobs   │               │
│  │  (Stats) │  │(Last Hr) │  │(Last Hr) │  │(Last Hr) │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       │             │              │              │                      │
│       └─────────────┴──────────────┴──────────────┘                     │
│                             │                                            │
│                    Auto-Refresh (60s)                                    │
│                             │                                            │
└─────────────────────────────┼────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          REST API (Flask)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  GET /api/stats              →  Overall statistics                      │
│  GET /api/jobs/linkedin      →  LinkedIn jobs (last hour)               │
│  GET /api/jobs/stepstone     →  Stepstone jobs (last hour)              │
│  GET /api/jobs/glassdoor     →  Glassdoor jobs (last hour)              │
│  GET /api/scraper/status     →  Scraper run history                     │
│  GET /api/scraper/trigger/X  →  Manually trigger scraper                │
│                                                                           │
└─────────────────────────────┼────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      DATABASE (SQLite)                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │                         JOBS TABLE                           │        │
│  ├──────────────────────────────────────────────────────────────┤        │
│  │  id  │  source  │  job_title  │  company  │  location  │...│        │
│  │  job_url  │  first_seen  │  last_seen  │is_new_in_last_hour│        │
│  └─────────────────────────────────────────────────────────────┘        │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │                    SCRAPER_RUNS TABLE                        │        │
│  ├──────────────────────────────────────────────────────────────┤        │
│  │  id  │  source  │  start_time  │  end_time  │  status  │... │        │
│  │  jobs_found  │  new_jobs  │  error_message                   │        │
│  └─────────────────────────────────────────────────────────────┘        │
│                                                                           │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │
                                │ Read/Write
                                │
┌───────────────────────────────┴───────────────────────────────────────────┐
│                    SCRAPER INTEGRATION LAYER                              │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  run_linkedin_scraper()                                            │  │
│  │  ├─ Create ScraperRun entry                                        │  │
│  │  ├─ Import linkedin_job_scraper                                    │  │
│  │  ├─ Fetch jobs (last 1 hour)                                       │  │
│  │  ├─ Mark existing jobs as is_new_in_last_hour=False                │  │
│  │  ├─ For each job:                                                  │  │
│  │  │  ├─ Check if exists (by URL)                                    │  │
│  │  │  ├─ If NEW: Add to DB with is_new_in_last_hour=True            │  │
│  │  │  └─ If EXISTS: Update last_seen timestamp                       │  │
│  │  └─ Update ScraperRun with results                                 │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  run_stepstone_scraper()                                           │  │
│  │  ├─ Create ScraperRun entry                                        │  │
│  │  ├─ Import stepstone_scraper                                       │  │
│  │  ├─ Fetch jobs (last 24 hours)                                     │  │
│  │  ├─ Mark existing jobs as is_new_in_last_hour=False                │  │
│  │  ├─ For each job:                                                  │  │
│  │  │  ├─ Check if exists (by URL)                                    │  │
│  │  │  ├─ If NEW: is_new_in_last_hour=True (NEW in last hour!)       │  │
│  │  │  └─ If EXISTS: Update last_seen (NOT new)                       │  │
│  │  └─ Update ScraperRun with results                                 │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  run_glassdoor_scraper()                                           │  │
│  │  ├─ Create ScraperRun entry                                        │  │
│  │  ├─ Import glassdoor_scraper                                       │  │
│  │  ├─ Fetch jobs (last 24 hours)                                     │  │
│  │  ├─ Mark existing jobs as is_new_in_last_hour=False                │  │
│  │  ├─ For each job:                                                  │  │
│  │  │  ├─ Check if exists (by URL)                                    │  │
│  │  │  ├─ If NEW: is_new_in_last_hour=True (NEW in last hour!)       │  │
│  │  │  └─ If EXISTS: Update last_seen (NOT new)                       │  │
│  │  └─ Update ScraperRun with results                                 │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
└────────────────────────────────┬──────────────────────────────────────────┘
                                 │
                                 │ Calls
                                 │
┌────────────────────────────────┴──────────────────────────────────────────┐
│                         SCHEDULER (APScheduler)                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │  Hourly Schedule (Cron Triggers)                                 │     │
│  ├──────────────────────────────────────────────────────────────────┤     │
│  │                                                                   │     │
│  │  Every hour at :00  →  run_linkedin_scraper()                    │     │
│  │  Every hour at :10  →  run_stepstone_scraper()                   │     │
│  │  Every hour at :20  →  run_glassdoor_scraper()                   │     │
│  │                                                                   │     │
│  │  Example Timeline:                                                │     │
│  │  1:00 → LinkedIn runs                                             │     │
│  │  1:10 → Stepstone runs                                            │     │
│  │  1:20 → Glassdoor runs                                            │     │
│  │  2:00 → LinkedIn runs                                             │     │
│  │  2:10 → Stepstone runs                                            │     │
│  │  2:20 → Glassdoor runs                                            │     │
│  │  ...                                                              │     │
│  └──────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Uses
                                 │
┌────────────────────────────────┴──────────────────────────────────────────┐
│                        EXISTING SCRAPERS                                   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────┐  │
│  │   Linkedin/         │  │   Stepstone/        │  │   Glassdoor/     │  │
│  │ linkedin_job_       │  │ stepstone_          │  │ glassdoor_       │  │
│  │   scraper.py        │  │   scraper.py        │  │   scraper.py     │  │
│  │                     │  │                     │  │                  │  │
│  │ Returns: Jobs from  │  │ Returns: Jobs from  │  │ Returns: Jobs    │  │
│  │ LAST 1 HOUR         │  │ LAST 24 HOURS       │  │ from LAST 24 HRS │  │
│  └──────┬──────────────┘  └──────┬──────────────┘  └────┬─────────────┘  │
│         │                        │                       │                 │
│         └────────────────────────┴───────────────────────┘                 │
│                                  │                                         │
│                         Scrapes from Web                                   │
│                                  │                                         │
└──────────────────────────────────┼─────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         JOB WEBSITES                                      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐          │
│  │   LinkedIn   │      │  Stepstone   │      │  Glassdoor   │          │
│  │              │      │              │      │              │          │
│  │  Filter:     │      │  Filter:     │      │  Filter:     │          │
│  │  Last 1 hour │      │  Last 24 hrs │      │  Last 24 hrs │          │
│  └──────────────┘      └──────────────┘      └──────────────┘          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘


KEY INSIGHT: HOW "LAST HOUR" TRACKING WORKS
═══════════════════════════════════════════

LinkedIn:
─────────
✓ Directly provides "last 1 hour" filter
✓ No comparison needed
✓ All jobs returned are genuinely from last hour

Stepstone & Glassdoor:
──────────────────────
✓ Only provide "last 24 hours" filter
✓ We run scraper EVERY HOUR
✓ Compare with previous run to find NEW jobs
✓ NEW jobs = Posted in the last hour!

Example:
1:00 AM - Scraper finds 100 jobs (all from last 24h)
2:00 AM - Scraper finds 103 jobs (all from last 24h)
         → 3 NEW jobs appeared since 1:00 AM
         → These 3 are marked as "posted in last hour"
         → These 3 appear on the Stepstone/Glassdoor pages


DATA FLOW SUMMARY
═════════════════

1. USER opens http://localhost:5000
2. Frontend loads and calls /api/stats
3. Backend queries database for statistics
4. Returns: Total jobs, new jobs in last hour, etc.
5. User clicks "LinkedIn Jobs"
6. Frontend calls /api/jobs/linkedin
7. Backend queries: WHERE source='linkedin' AND is_new_in_last_hour=True
8. Returns only NEW jobs from last hour
9. Frontend displays jobs in cards
10. Auto-refreshes every 60 seconds

Meanwhile, in the background:
- Scheduler triggers scrapers every hour
- Scrapers fetch latest jobs
- Compare with existing jobs in DB
- Mark NEW jobs with is_new_in_last_hour=True
- Mark old jobs with is_new_in_last_hour=False
- Update statistics in scraper_runs table
```
