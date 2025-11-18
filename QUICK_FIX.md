# Quick Fix Guide - Zero Jobs Problem

## Problem
Your deployed container shows **zero jobs** even though it's running.

## Quick Diagnosis

Run the diagnostic script to identify the issue:
```bash
./diagnose_container.sh job_hunter
```

Replace `job_hunter` with your actual container name if different.

## Quick Fixes (Choose One)

### Fix 1: Run the Automated Fix Script (RECOMMENDED)
This applies all code fixes and restarts the container:

```bash
./fix_zero_jobs.sh job_hunter
```

**What it does:**
- ✅ Updates database path to use absolute location
- ✅ Enables initial scraping on startup
- ✅ Creates data directory
- ✅ Restarts container
- ✅ Starts scraping immediately

**Wait time:** 2-5 minutes for scrapers to complete

---

### Fix 2: Manual Trigger (NO CODE CHANGES)
Just trigger the scrapers without changing any code:

**Via Web UI:**
1. Open http://your-server-ip:5000
2. Click "🔍 Search for jobs now" button
3. Wait 2-5 minutes
4. Refresh page

**Via API:**
```bash
# Replace localhost with your server IP
curl http://localhost:5000/api/scraper/trigger/all
```

**Wait time:** 2-5 minutes for scrapers to complete

---

### Fix 3: Manual File Update
If you prefer to update files manually:

1. **Update app.py** - Change database path:
```bash
docker cp app/app.py job_hunter:/app/app/app.py
```

2. **Update run.py** - Enable initial scraping:
```bash
docker cp run.py job_hunter:/app/run.py
```

3. **Restart container:**
```bash
docker restart job_hunter
```

**Wait time:** 2-5 minutes for scrapers to complete

---

## Verification

After applying fix, verify it worked:

### Check via API:
```bash
# Get job statistics
curl http://localhost:5000/api/stats

# Expected output (after 2-5 minutes):
# {
#   "total_jobs": 50+,
#   "linkedin_jobs": 20+,
#   "stepstone_jobs": 20+,
#   "glassdoor_jobs": 10+
# }
```

### Check via Web UI:
```bash
# Open in browser
http://localhost:5000/

# Should show:
# - Total Jobs: 50+ (not zero!)
# - LinkedIn Jobs: 20+
# - Stepstone Jobs: 20+
# - Glassdoor Jobs: 10+
```

### Check via Container Logs:
```bash
docker logs job_hunter | tail -50

# Should see:
# "LinkedIn Scraper completed: X jobs found, X new jobs"
# "Stepstone Scraper completed: X jobs found, X new jobs"
# "Glassdoor Scraper completed: X jobs found, X new jobs"
```

### Check Database:
```bash
# Check job count
docker exec job_hunter sqlite3 /app/data/jobs.db "SELECT COUNT(*) FROM jobs;"

# Should show a number > 0
```

---

## Common Issues

### Issue: "Please wait X minutes before running scrapers"
**Cause:** Timing protection (1-hour minimum between runs)

**Solution:** 
- Wait the specified time, OR
- Delete database to reset: `docker exec job_hunter rm -f /app/data/jobs.db && docker restart job_hunter`

---

### Issue: Scrapers run but still show zero jobs
**Cause:** Database path issue or scraper errors

**Solution:**
1. Check logs: `docker logs job_hunter | grep -i error`
2. Run fix script: `./fix_zero_jobs.sh job_hunter`
3. Check database location: `docker exec job_hunter find /app -name "*.db"`

---

### Issue: Container won't start after fix
**Cause:** Syntax error or file corruption

**Solution:**
1. Check logs: `docker logs job_hunter`
2. Restore backups:
```bash
docker exec job_hunter cp /app/app/app.py.backup* /app/app/app.py
docker exec job_hunter cp /app/run.py.backup* /app/run.py
docker restart job_hunter
```

---

### Issue: Cannot find container
**Cause:** Wrong container name

**Solution:**
```bash
# List all running containers
docker ps

# Use correct container name
./diagnose_container.sh <actual-container-name>
```

---

## What Changed in the Fix

### Before (Broken):
- ❌ Database path: `sqlite:///jobs.db` (relative, creates in Flask instance folder)
- ❌ Initial scraping: Disabled (commented out)
- ❌ Data directory: Not created
- ❌ Result: Container starts but has zero jobs forever

### After (Fixed):
- ✅ Database path: `sqlite:////app/data/jobs.db` (absolute, predictable location)
- ✅ Initial scraping: Enabled (runs on startup)
- ✅ Data directory: Created with proper permissions
- ✅ Result: Container starts and immediately begins scraping jobs

---

## Files Modified

| File | Change | Purpose |
|------|--------|---------|
| `app/app.py` | Database path | Use absolute path instead of relative |
| `run.py` | Uncommented line | Enable initial scraping on startup |

---

## Timeline After Fix

```
0:00  - Container starts
0:01  - Database created at /app/data/jobs.db
0:02  - Initial scraping begins
0:02  - LinkedIn scraper starts
0:03  - LinkedIn: 20+ jobs found
0:04  - Stepstone scraper starts
0:05  - Stepstone: 30+ jobs found
0:06  - Glassdoor scraper starts
0:07  - Glassdoor: 15+ jobs found
0:08  - All scrapers complete
0:09  - Web UI shows 65+ total jobs ✅
```

---

## Support Commands

```bash
# View live logs
docker logs -f job_hunter

# Check container status
docker ps | grep job_hunter

# Restart container
docker restart job_hunter

# Access container shell
docker exec -it job_hunter /bin/bash

# Check database
docker exec job_hunter sqlite3 /app/data/jobs.db "SELECT COUNT(*) FROM jobs;"

# Trigger scrapers
curl http://localhost:5000/api/scraper/trigger/all

# View all database tables
docker exec job_hunter sqlite3 /app/data/jobs.db ".tables"

# View recent jobs
docker exec job_hunter sqlite3 /app/data/jobs.db "SELECT job_title, company, source FROM jobs LIMIT 10;"
```

---

## Need More Help?

1. **Run diagnostic script:**
   ```bash
   ./diagnose_container.sh job_hunter
   ```

2. **Check detailed documentation:**
   - `ZERO_JOBS_DIAGNOSIS.md` - Complete diagnosis
   - `CONTAINER_FIX.md` - Original fix documentation
   - `TIMING_PROTECTION.md` - Info about 1-hour protection

3. **View logs:**
   ```bash
   docker logs job_hunter > container.log
   # Then examine container.log
   ```

---

**Last Updated:** November 18, 2025
