"""
Job Scheduler Module
Schedules scrapers to run at regular intervals
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import threading
from app.scraper_integration import run_linkedin_scraper, run_stepstone_scraper, run_glassdoor_scraper
from app.app import app
from app.models import db, ScraperRun

# Lock to prevent concurrent scraper runs
scraper_lock = threading.Lock()

# Track last successful run times for each source
last_run_times = {
    'linkedin': None,
    'stepstone': None,
    'glassdoor': None
}

def check_last_run_time(source):
    """
    Check if at least 1 hour has passed since the last successful run
    
    Args:
        source: 'linkedin', 'stepstone', or 'glassdoor'
    
    Returns:
        bool: True if enough time has passed, False otherwise
    """
    with app.app_context():
        # Get the last completed run from database
        last_run = ScraperRun.query.filter_by(
            source=source,
            status='completed'
        ).order_by(ScraperRun.end_time.desc()).first()
        
        if not last_run or not last_run.end_time:
            # No previous run or no end time, allow to run
            print(f"  ℹ️  No previous completed run found for {source}, allowing scraper to run")
            return True
        
        time_since_last_run = datetime.utcnow() - last_run.end_time
        time_since_seconds = time_since_last_run.total_seconds()
        time_since_minutes = time_since_seconds / 60
        
        # Check if at least 1 hour (3600 seconds) has passed
        if time_since_seconds < 3600:
            remaining_minutes = (3600 - time_since_seconds) / 60
            print(f"  ⏰ Last {source} run completed {time_since_minutes:.1f} minutes ago")
            print(f"  ⛔ Less than 1 hour since last run. Skipping. (Wait {remaining_minutes:.1f} more minutes)")
            return False
        
        print(f"  ✅ Last {source} run completed {time_since_minutes:.1f} minutes ago. Proceeding with new run.")
        return True


def run_scraper_task(source):
    """
    Run a specific scraper task
    
    Args:
        source: 'linkedin', 'stepstone', or 'glassdoor'
    """
    # Prevent concurrent runs
    if not scraper_lock.acquire(blocking=False):
        print(f"⏳ Scraper for {source} is already running, skipping...")
        return
    
    try:
        print(f"\n{'#'*60}")
        print(f"Scheduled scraper run for {source} at {datetime.now()}")
        print(f"{'#'*60}\n")
        
        # Check if enough time has passed since last run
        if not check_last_run_time(source):
            print(f"{'#'*60}\n")
            return
        
        # Run the scraper
        if source == 'linkedin':
            run_linkedin_scraper()
        elif source == 'stepstone':
            run_stepstone_scraper()
        elif source == 'glassdoor':
            run_glassdoor_scraper()
        else:
            print(f"Unknown source: {source}")
        
        # Update last run time in memory
        last_run_times[source] = datetime.utcnow()
            
    except Exception as e:
        print(f"Error in scheduled task for {source}: {str(e)}")
    finally:
        scraper_lock.release()


def run_all_scrapers():
    """
    Run all scrapers in sequence with time checks
    Only runs if at least 1 hour has passed since last completed run
    """
    print(f"\n{'#'*60}")
    print(f"Running all scrapers at {datetime.now()}")
    print(f"{'#'*60}\n")
    
    with app.app_context():
        # Check the last run time for all scrapers
        sources = ['linkedin', 'stepstone', 'glassdoor']
        
        # Find the most recent completion time among all scrapers
        latest_completion = None
        for source in sources:
            last_run = ScraperRun.query.filter_by(
                source=source,
                status='completed'
            ).order_by(ScraperRun.end_time.desc()).first()
            
            if last_run and last_run.end_time:
                if latest_completion is None or last_run.end_time > latest_completion:
                    latest_completion = last_run.end_time
        
        # Check if at least 1 hour has passed since the last completed run
        if latest_completion:
            time_since_last = datetime.utcnow() - latest_completion
            time_since_minutes = time_since_last.total_seconds() / 60
            
            if time_since_last.total_seconds() < 3600:
                remaining_minutes = (3600 - time_since_last.total_seconds()) / 60
                print(f"⏰ Last scraper batch completed {time_since_minutes:.1f} minutes ago")
                print(f"⛔ Less than 1 hour since last batch completion.")
                print(f"   Skipping all scrapers. (Wait {remaining_minutes:.1f} more minutes)")
                print(f"{'#'*60}\n")
                return
            
            print(f"✅ Last scraper batch completed {time_since_minutes:.1f} minutes ago.")
            print(f"   Proceeding with new scraper batch.\n")
    
    # Run LinkedIn first (gets last 1 hour jobs)
    run_scraper_task('linkedin')
    
    # Run Stepstone (gets last 24 hours, we track new ones)
    run_scraper_task('stepstone')
    
    # Run Glassdoor (gets last 24 hours, we track new ones)
    run_scraper_task('glassdoor')
    
    print(f"\n{'#'*60}")
    print(f"All scrapers batch completed at {datetime.now()}")
    print(f"{'#'*60}\n")


def init_scheduler():
    """Initialize and start the scheduler"""
    scheduler = BackgroundScheduler()
    
    # Run all scrapers every hour at the top of the hour
    # This ensures we capture:
    # - LinkedIn: jobs from last 1 hour
    # - Stepstone: new jobs since last run (by comparing with previous 24h data)
    # - Glassdoor: new jobs since last run (by comparing with previous 24h data)
    
    scheduler.add_job(
        func=run_all_scrapers,
        trigger=CronTrigger(minute=0),  # Run at the start of every hour
        id='hourly_scraper',
        name='Hourly job scraper',
        replace_existing=True
    )
    
    # Optional: Run individual scrapers at different intervals if needed
    # Uncomment these if you want more frequent updates for specific sources
    
    # LinkedIn every hour (at minute 0)
    scheduler.add_job(
        func=lambda: run_scraper_task('linkedin'),
        trigger=CronTrigger(minute=0),
        id='linkedin_scraper',
        name='LinkedIn hourly scraper',
        replace_existing=True
    )
    
    # Stepstone every hour (at minute 10)
    scheduler.add_job(
        func=lambda: run_scraper_task('stepstone'),
        trigger=CronTrigger(minute=10),
        id='stepstone_scraper',
        name='Stepstone hourly scraper',
        replace_existing=True
    )
    
    # Glassdoor every hour (at minute 20)
    scheduler.add_job(
        func=lambda: run_scraper_task('glassdoor'),
        trigger=CronTrigger(minute=20),
        id='glassdoor_scraper',
        name='Glassdoor hourly scraper',
        replace_existing=True
    )
    
    scheduler.start()
    
    print("\n" + "="*60)
    print("Scheduler initialized successfully!")
    print("="*60)
    print("\nScheduled jobs:")
    for job in scheduler.get_jobs():
        print(f"  - {job.name} (ID: {job.id})")
        print(f"    Next run: {job.next_run_time}")
    print("="*60 + "\n")
    
    return scheduler


def run_initial_scrape():
    """Run all scrapers immediately on startup"""
    print("\n" + "="*60)
    print("Running initial scrape on startup...")
    print("="*60 + "\n")
    
    run_all_scrapers()
    
    print("\n" + "="*60)
    print("Initial scrape completed!")
    print("="*60 + "\n")


if __name__ == '__main__':
    # For testing
    scheduler = init_scheduler()
    
    # Keep the script running
    try:
        import time
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
