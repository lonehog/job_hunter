# Job Hunter Container Fix - "Search for jobs now" Button

## Problem Identified

Your job-hunter container wasn't scraping jobs because:

1. **No initial scrape on startup** - The `run_initial_scrape()` was commented out in `run.py`
2. **Import error in trigger endpoint** - Wrong import path (`scheduler` instead of `app.scheduler`)
3. **Missing UI button** - No "Search for jobs now" button in the interface

## Fixes Applied

### 1. Fixed Import Error in `app/app.py`
**Line 253 changed from:**
```python
from scheduler import run_scraper_task, run_all_scrapers, check_last_run_time
```

**To:**
```python
from app.scheduler import run_scraper_task, run_all_scrapers, check_last_run_time
```

This fixes the module import error that was preventing manual scraper triggers from working.

### 2. Added "Search for jobs now" Button in `templates/home.html`

Added a new button alongside the "Refresh Stats" button:
```html
<button class="refresh-btn" onclick="triggerScrapers()" id="search-now-btn">🔍 Search for jobs now</button>
```

Added JavaScript function to handle the button click:
```javascript
async function triggerScrapers() {
    // 1. Check if enough time has passed (1 hour)
    // 2. Show user-friendly messages about timing
    // 3. Trigger all scrapers via API
    // 4. Refresh stats automatically after trigger
}
```

## How It Works Now

### When You Click "Search for jobs now":

1. **Checks timing** - Calls `/api/scraper/can-run` to verify 1 hour has passed
2. **Shows alert** - If too soon, tells you exactly how many minutes to wait
3. **Triggers scrapers** - If ready, calls `/api/scraper/trigger/all`
4. **Respects 1-hour limit** - Each scraper must wait 1 hour between runs
5. **Runs in background** - Doesn't block the interface
6. **Auto-refreshes** - Stats update automatically after trigger

### Timing Protection

The system enforces **1-hour minimum** between scraper runs:

- ✅ **First click**: Scrapers run immediately
- ⏰ **Second click (< 1 hour)**: Shows message: "Please wait X minutes"
- ✅ **After 1 hour**: Can run again

## Testing the Fix

### Option 1: Web Interface
1. Open http://localhost:5000 (or your container's URL)
2. Click "🔍 Search for jobs now" button
3. Wait for alert confirmation
4. Refresh page to see new jobs

### Option 2: API Testing
Run the test script:
```bash
cd /home/surya/job_hunter
python3 test_trigger.py
```

This will:
- Check if scrapers can run
- Attempt to trigger them
- Show current job stats

### Option 3: Direct API Call
```bash
# Check if scrapers can run
curl http://localhost:5000/api/scraper/can-run

# Trigger all scrapers
curl http://localhost:5000/api/scraper/trigger/all

# Check stats
curl http://localhost:5000/api/stats
```

## Deploying to Portainer

### If you need to rebuild your container:

1. **Stop the current container** in Portainer
2. **Pull the latest code**:
   ```bash
   cd /home/surya/job_hunter
   git add .
   git commit -m "Fix scraper trigger and add search button"
   git push
   ```
3. **Recreate container** in Portainer (it will pull latest code)
4. **Or update files directly** in running container:
   - Copy `app/app.py` to container
   - Copy `templates/home.html` to container
   - Restart container

### Quick Fix Without Rebuilding:

If your container is already running, you can update files directly:

```bash
# Copy fixed files to container
docker cp app/app.py job-hunter:/app/app/app.py
docker cp templates/home.html job-hunter:/app/templates/home.html

# Restart container
docker restart job-hunter
```

## Verification

After deploying, verify it works:

1. ✅ **Web interface loads** - No errors in browser console
2. ✅ **Button appears** - "Search for jobs now" is visible
3. ✅ **Button responds** - Clicking shows messages
4. ✅ **Scrapers run** - Jobs appear after waiting a few minutes
5. ✅ **Timing works** - Second click too soon shows wait message

## Expected Behavior

### First Run (No previous scrapes):
```
Click "Search for jobs now"
  → ✅ Scrapers start immediately
  → Wait 2-5 minutes
  → Refresh page
  → See new jobs
```

### Subsequent Runs (< 1 hour since last):
```
Click "Search for jobs now"
  → ⏰ Alert: "Please wait X minutes"
  → Wait until 1 hour has passed
  → Try again
```

### After 1 Hour:
```
Click "Search for jobs now"
  → ✅ Scrapers start again
  → New jobs added to database
```

## Troubleshooting

### Button does nothing when clicked
**Check browser console** (F12) for JavaScript errors:
```bash
# If you see errors, verify the files were updated in container
docker exec job-hunter ls -la /app/templates/home.html
docker exec job-hunter ls -la /app/app/app.py
```

### Import error in logs
```bash
# Check container logs
docker logs job-hunter

# If you see "ModuleNotFoundError: No module named 'scheduler'"
# The fix wasn't applied - update app/app.py line 253
```

### Scrapers still won't run
```bash
# Check if timing protection is active
curl http://your-container-url:5000/api/scraper/can-run

# Check scraper status
curl http://your-container-url:5000/api/scraper/status
```

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scraper/can-run` | GET | Check if scrapers are ready (1 hour passed) |
| `/api/scraper/trigger/all` | GET | Trigger all scrapers (with timing check) |
| `/api/scraper/trigger/linkedin` | GET | Trigger only LinkedIn scraper |
| `/api/scraper/trigger/stepstone` | GET | Trigger only Stepstone scraper |
| `/api/scraper/trigger/glassdoor` | GET | Trigger only Glassdoor scraper |
| `/api/stats` | GET | Get job statistics |
| `/api/scraper/status` | GET | Get detailed scraper run history |

## Files Modified

1. ✅ `app/app.py` - Fixed import statement
2. ✅ `templates/home.html` - Added button and JavaScript function
3. ✅ `test_trigger.py` - Created test script (optional)

## Next Steps

1. **Deploy the fixes** to your Portainer container
2. **Test the button** - Click "Search for jobs now"
3. **Wait for results** - Scrapers take 2-5 minutes to complete
4. **Monitor logs** - Check container logs for scraper activity
5. **Verify jobs** - Refresh page to see new jobs

---

**Created:** November 18, 2025  
**Status:** Ready to deploy
