# Scraper Timing Protection

## Overview

The Job Hunter application now includes **automatic timing protection** to prevent scrapers from running too frequently. This ensures:

1. ✅ **Rate limiting compliance** - Respects website rate limits
2. ✅ **Meaningful data collection** - New jobs have time to appear
3. ✅ **System resource optimization** - Prevents unnecessary scraping
4. ✅ **Reliable operation** - Reduces risk of getting blocked

## How It Works

### One-Hour Minimum Gap

**Every scraper (LinkedIn, Stepstone, Glassdoor) must wait at least 1 hour after its last successful completion before running again.**

### Timing Check Flow

```
Scraper Triggered
      ↓
Check Last Completed Run
      ↓
Was it more than 1 hour ago?
      ↓
    YES: Run scraper
    NO:  Skip and show wait time
```

## Implementation Details

### Individual Scraper Check

Each scraper (LinkedIn, Stepstone, Glassdoor) is checked independently:

- **Check**: Last completed run's `end_time`
- **Requirement**: Must be ≥ 1 hour (3600 seconds) ago
- **Action if too soon**: Skip and log remaining wait time
- **Action if ready**: Run scraper and collect jobs

### Batch Scraper Check (`run_all_scrapers`)

When running all scrapers together:

- **Check**: Latest `end_time` among ALL three scrapers
- **Requirement**: Must be ≥ 1 hour since any scraper completed
- **Action if too soon**: Skip entire batch
- **Action if ready**: Run all scrapers sequentially

### Example Scenario

```
2:00 PM - LinkedIn completes
2:05 PM - Stepstone completes  
2:10 PM - Glassdoor completes  ← Latest completion

3:00 PM - Scheduler tries to run batch
          ↓
          Check: Latest completion was 2:10 PM (50 minutes ago)
          Result: ⛔ SKIP (need to wait 10 more minutes)
          
3:15 PM - Scheduler tries again
          ↓
          Check: Latest completion was 2:10 PM (65 minutes ago)
          Result: ✅ RUN ALL SCRAPERS
```

## API Endpoints

### Check If Scrapers Can Run

```bash
GET /api/scraper/can-run
```

**Response:**
```json
{
  "linkedin": {
    "can_run": false,
    "time_until_next_run_minutes": 15.3
  },
  "stepstone": {
    "can_run": true,
    "time_until_next_run_minutes": 0
  },
  "glassdoor": {
    "can_run": true,
    "time_until_next_run_minutes": 0
  },
  "all": {
    "can_run": false,
    "time_until_next_run_minutes": 15.3
  }
}
```

### Trigger Scraper (with timing check)

```bash
GET /api/scraper/trigger/linkedin
GET /api/scraper/trigger/stepstone
GET /api/scraper/trigger/glassdoor
GET /api/scraper/trigger/all
```

**Success Response (ready to run):**
```json
{
  "message": "Scraper triggered for linkedin",
  "status": "running"
}
```

**Blocked Response (too soon):**
```json
{
  "message": "Cannot run linkedin scraper yet",
  "status": "skipped",
  "reason": "Less than 1 hour since last run. Wait 15.3 more minutes.",
  "time_since_last_minutes": 44.7
}
```

HTTP Status: `429 Too Many Requests`

## Visual Indicators

### Home Page Dashboard

The home page now shows:

1. **Time since last run** - How long ago each scraper completed
2. **Can run status** - Whether scraper can run now
3. **Wait time** - Minutes remaining until scraper can run again

**Example Display:**

```
LINKEDIN
Status: completed
Jobs Found: 45
New Jobs: 12

Started: 11/11/2025, 2:00:00 PM
Ended: 11/11/2025, 2:05:30 PM

⏰ Must wait 15.3 more minutes (44.7 minutes since last run)
```

or

```
STEPSTONE
Status: completed
Jobs Found: 23
New Jobs: 8

Started: 11/11/2025, 1:00:00 PM
Ended: 11/11/2025, 1:08:15 PM

✅ Can run again (1.2 hours since last run)
```

## Console Logs

When scrapers are blocked, you'll see detailed logs:

```
##############################################################
Scheduled scraper run for linkedin at 2025-11-11 15:00:00
##############################################################

  ⏰ Last linkedin run completed 44.7 minutes ago
  ⛔ Less than 1 hour since last run. Skipping. (Wait 15.3 more minutes)
##############################################################
```

When scrapers are allowed to run:

```
##############################################################
Scheduled scraper run for linkedin at 2025-11-11 15:15:00
##############################################################

  ✅ Last linkedin run completed 65.2 minutes ago. Proceeding with new run.

Running LinkedIn Scraper - 2025-11-11 15:15:00
...
```

## Configuration

### Change Minimum Wait Time

To change from 1 hour to a different interval, edit `app/scheduler.py`:

```python
# Change 3600 seconds (1 hour) to desired value
# Example: 30 minutes = 1800 seconds

if time_since_seconds < 1800:  # 30 minutes instead of 3600
    # Skip scraper
    ...
```

### Disable Timing Check (Not Recommended)

To disable timing checks completely (not recommended):

1. Edit `app/scheduler.py`
2. Comment out the timing check in `run_scraper_task()`:

```python
def run_scraper_task(source):
    # ...
    
    # Check if enough time has passed since last run
    # if not check_last_run_time(source):
    #     print(f"{'#'*60}\n")
    #     return
    
    # Run the scraper immediately
    ...
```

## Benefits

### 1. **Prevents Getting Blocked**
Websites may block IPs that scrape too frequently. The 1-hour gap helps avoid this.

### 2. **Data Quality**
Jobs need time to be posted. Running every few minutes won't find many new jobs.

### 3. **Resource Efficiency**
Reduces unnecessary CPU, network, and database usage.

### 4. **Compliance**
Shows good faith effort to respect website resources and terms of service.

## Troubleshooting

### Q: Scraper won't run even though I triggered it

**A:** Check the last run time:
```bash
# Check if scrapers can run
curl http://localhost:5000/api/scraper/can-run

# Or check the home page in browser
```

### Q: I need to run scrapers more frequently

**A:** Consider:
1. Is it really necessary? Jobs don't appear every minute
2. You might get blocked by the websites
3. If needed, reduce the wait time (see Configuration above)

### Q: First run won't start

**A:** If no previous runs exist, scrapers should start immediately. Check:
```bash
# View database
sqlite3 app/jobs.db
SELECT * FROM scraper_runs;
```

### Q: How to force a run immediately

**A:** Delete the last run from database:
```bash
sqlite3 app/jobs.db
DELETE FROM scraper_runs WHERE source='linkedin';
```

Then trigger manually:
```bash
curl http://localhost:5000/api/scraper/trigger/linkedin
```

## Best Practices

1. ✅ **Let the scheduler run automatically** - It's optimized for hourly runs
2. ✅ **Check home page before manual triggers** - See if scrapers are ready
3. ✅ **Monitor error logs** - Timing blocks are logged clearly
4. ✅ **Use the API** - Check `/api/scraper/can-run` before triggering
5. ✅ **Be patient** - Quality data takes time

---

**The 1-hour minimum gap ensures sustainable, reliable, and respectful job scraping.**
