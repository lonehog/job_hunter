# Zero Jobs Problem - Diagnosis and Solutions

## Problems Identified

Your deployed container shows zero jobs because:

### 1. **Database Location Issue** ⚠️
The SQLite database uses a **relative path** `sqlite:///jobs.db` which creates the database in Flask's "instance" folder. In a container, this location may not be persistent or accessible.

**Location:** `app/app.py` line 16:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
```

This creates database at: `/app/instance/jobs.db` (Flask's default instance folder)

### 2. **No Initial Scraping** ⚠️
The application doesn't run scrapers on startup. It only waits for:
- Scheduled hourly runs (at minute 0, 10, 20)
- Manual trigger via "Search for jobs now" button

**Location:** `run.py` line 16:
```python
# run_initial_scrape()  # COMMENTED OUT!
```

### 3. **Potential Volume Mounting Issue** ⚠️
If you deployed with Portainer, the database might be created inside the container but:
- Not mapped to a persistent volume
- Created in a different location than expected
- Gets reset when container restarts

## Solutions

### Solution 1: Use Absolute Database Path (RECOMMENDED)

Change the database path to be explicit and predictable:

**File:** `app/app.py` (line 16)

**Change from:**
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
```

**Change to:**
```python
import os
# Use absolute path for database
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
```

This will create the database at `/app/jobs.db` (predictable location).

### Solution 2: Enable Initial Scraping

Uncomment initial scraping to populate database on startup:

**File:** `run.py` (line 16)

**Change from:**
```python
# run_initial_scrape()
```

**Change to:**
```python
run_initial_scrape()
```

### Solution 3: Add Environment Variable Support

Make database location configurable via environment variable:

**File:** `app/app.py` (add after imports)

```python
import os

# Allow database path to be configured via environment variable
DB_PATH = os.environ.get('DATABASE_PATH', '/app/data/jobs.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
```

Then in Portainer:
- Add environment variable: `DATABASE_PATH=/app/data/jobs.db`
- Mount volume: `/path/on/host:/app/data`

## Diagnostic Commands

### Check if database exists in container:

```bash
# Find database file
docker exec job_hunter find /app -name "*.db" -type f

# Check instance folder
docker exec job_hunter ls -la /app/instance/

# Check root folder
docker exec job_hunter ls -la /app/

# Check database location
docker exec job_hunter python -c "from app.app import app; print(app.config['SQLALCHEMY_DATABASE_URI'])"
```

### Check if scrapers have run:

```bash
# Check container logs
docker logs job_hunter | grep -i "scraper"

# Check if scrapers are scheduled
docker logs job_hunter | grep -i "scheduler"

# Query database directly
docker exec job_hunter sqlite3 /app/instance/jobs.db "SELECT COUNT(*) FROM jobs;"
docker exec job_hunter sqlite3 /app/instance/jobs.db "SELECT COUNT(*) FROM scraper_runs;"
```

### Check scraper status via API:

```bash
# Get stats
curl http://your-container-ip:5000/api/stats

# Check scraper status
curl http://your-container-ip:5000/api/scraper/status

# Check if can run
curl http://your-container-ip:5000/api/scraper/can-run
```

## Quick Fix Scripts

### Script 1: Fix Database Path + Enable Initial Scraping

Create `fix_zero_jobs.sh`:

```bash
#!/bin/bash

CONTAINER_NAME="${1:-job_hunter}"

echo "Fixing zero jobs issue in container: $CONTAINER_NAME"

# Backup current files
docker exec "$CONTAINER_NAME" cp /app/app/app.py /app/app/app.py.backup
docker exec "$CONTAINER_NAME" cp /app/run.py /app/run.py.backup

# Copy fixed files
docker cp app/app.py "$CONTAINER_NAME":/app/app/app.py
docker cp run.py "$CONTAINER_NAME":/app/run.py

# Restart container
docker restart "$CONTAINER_NAME"

echo "Container restarted. Check logs:"
echo "  docker logs -f $CONTAINER_NAME"
```

### Script 2: Manually Trigger Scrapers

```bash
#!/bin/bash

CONTAINER_IP="${1:-localhost}"
PORT="${2:-5000}"

echo "Triggering scrapers on $CONTAINER_IP:$PORT"

# Trigger all scrapers
curl -X GET "http://$CONTAINER_IP:$PORT/api/scraper/trigger/all"

echo ""
echo "Scrapers triggered. Wait 2-5 minutes then check:"
echo "  curl http://$CONTAINER_IP:$PORT/api/stats"
```

## Step-by-Step Fix Process

### Step 1: Diagnose Current State

```bash
# 1. Find database location
docker exec job_hunter find /app -name "*.db"

# 2. Check if database has data
docker exec job_hunter sqlite3 /app/instance/jobs.db "SELECT COUNT(*) FROM jobs;"

# 3. Check scraper run history
docker exec job_hunter sqlite3 /app/instance/jobs.db "SELECT * FROM scraper_runs ORDER BY start_time DESC LIMIT 5;"
```

### Step 2: Apply Fix (Choose One)

**Option A: Fix with initial scraping (FASTEST)**
1. Edit `run.py` - uncomment `run_initial_scrape()`
2. Edit `app/app.py` - fix database path (see Solution 1)
3. Deploy changes to container
4. Restart container
5. Wait 2-5 minutes for initial scraping

**Option B: Fix without initial scraping**
1. Edit `app/app.py` - fix database path (see Solution 1)
2. Deploy changes to container
3. Restart container
4. Click "Search for jobs now" button in web UI
5. Wait 2-5 minutes

**Option C: Quick manual trigger (NO CODE CHANGES)**
1. Access web UI: http://your-container-ip:5000
2. Click "🔍 Search for jobs now" button
3. Wait for confirmation
4. Refresh page after 2-5 minutes
5. Jobs should appear

### Step 3: Verify Fix

```bash
# 1. Check logs for scraper activity
docker logs job_hunter | tail -50

# 2. Check database
docker exec job_hunter sqlite3 /app/instance/jobs.db "SELECT COUNT(*) FROM jobs;"

# 3. Check via API
curl http://your-container-ip:5000/api/stats | jq

# 4. Check web UI
# Open http://your-container-ip:5000 in browser
```

## Expected Output After Fix

### Successful Scraping Logs:
```
############################
Running all scrapers at 2025-11-18 ...
############################

✅ Last scraper batch completed X minutes ago.
   Proceeding with new scraper batch.

==================================================
Running LinkedIn Scraper - 2025-11-18 ...
==================================================

LinkedIn Scraper completed: 25 jobs found, 25 new jobs

==================================================
Running Stepstone Scraper - 2025-11-18 ...
==================================================

Stepstone Scraper completed: 42 jobs found, 42 new jobs

==================================================
Running Glassdoor Scraper - 2025-11-18 ...
==================================================

Glassdoor Scraper completed: 18 jobs found, 18 new jobs
```

### API Response with Jobs:
```json
{
  "total_jobs": 85,
  "linkedin_jobs": 25,
  "stepstone_jobs": 42,
  "glassdoor_jobs": 18,
  "new_jobs_last_hour": 85
}
```

## Common Issues

### Issue: "Less than 1 hour since last run"
**Cause:** Timing protection is active
**Solution:** Wait until 1 hour has passed, OR delete database and restart

```bash
# Delete database to reset timing
docker exec job_hunter rm -f /app/instance/jobs.db
docker restart job_hunter
```

### Issue: "ModuleNotFoundError: No module named 'linkedin_job_scraper'"
**Cause:** Scrapers not available in container
**Solution:** Check if scraper files are in container

```bash
docker exec job_hunter ls -la /app/Linkedin/
docker exec job_hunter ls -la /app/Stepstone/
docker exec job_hunter ls -la /app/Glassdoor/
```

### Issue: Database file not found
**Cause:** Database path is wrong or directory doesn't exist
**Solution:** Create directory and check permissions

```bash
docker exec job_hunter mkdir -p /app/instance
docker exec job_hunter chmod 777 /app/instance
docker restart job_hunter
```

### Issue: Container logs show errors
**Cause:** Various - check specific error
**Solution:** 

```bash
# View full logs
docker logs job_hunter

# View recent errors
docker logs job_hunter 2>&1 | grep -i "error"

# View scraper activity
docker logs job_hunter 2>&1 | grep -i "scraper"
```

## Persistent Volume Setup for Portainer

To preserve database across container restarts:

### Method 1: Named Volume
In Portainer container creation:
1. Go to Volumes tab
2. Add volume mapping:
   - Container: `/app/data`
   - Volume: `job_hunter_data` (create new named volume)
3. Update `app/app.py` to use `/app/data/jobs.db`

### Method 2: Bind Mount
In Portainer container creation:
1. Go to Volumes tab
2. Add bind mount:
   - Container: `/app/data`
   - Host: `/path/on/your/host/job_hunter_data`
3. Update `app/app.py` to use `/app/data/jobs.db`

### Method 3: Environment Variable
In Portainer container creation:
1. Go to Environment Variables tab
2. Add: `DATABASE_PATH=/app/data/jobs.db`
3. Add volume mapping for `/app/data`
4. Update `app/app.py` to read from environment variable

## Recommended Solution

**For immediate fix (no rebuild):**
1. Access container web UI
2. Click "🔍 Search for jobs now"
3. Wait 2-5 minutes
4. Refresh page

**For permanent fix (requires rebuild):**
1. Apply Solution 1 (absolute database path)
2. Apply Solution 2 (enable initial scraping)
3. Apply Solution 3 (environment variable support)
4. Add persistent volume in Portainer
5. Rebuild and redeploy container

## Testing After Fix

```bash
# Test script
curl http://localhost:5000/api/stats
# Should show: total_jobs > 0

curl http://localhost:5000/api/scraper/status
# Should show: recent scraper runs

# Manual test
python3 /home/surya/job_hunter/test_trigger.py
```

---

**Created:** November 18, 2025  
**Priority:** HIGH  
**Status:** Ready to apply
