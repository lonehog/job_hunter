"""
Scraper Integration Module
Integrates existing scrapers with the database
"""
import sys
import os
from datetime import datetime
from app.app import app
from app.models import db, Job, ScraperRun

# Add parent directories to path to import scrapers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Linkedin'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Stepstone'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Glassdoor'))


def save_jobs_to_db(jobs_data, source):
    """
    Save jobs to database and track new jobs
    
    Args:
        jobs_data: List of job dictionaries
        source: Source name ('linkedin', 'stepstone', 'glassdoor')
    
    Returns:
        Tuple of (total_jobs, new_jobs)
    """
    with app.app_context():
        new_jobs_count = 0
        total_jobs = len(jobs_data)
        
        # First, mark all existing jobs from this source as not new
        Job.query.filter_by(source=source).update({'is_new_in_last_hour': False})
        
        for job_data in jobs_data:
            try:
                # Check if job already exists (by URL)
                existing_job = Job.query.filter_by(job_url=job_data.get('job_url')).first()
                
                if existing_job:
                    # Update last_seen timestamp
                    existing_job.last_seen = datetime.utcnow()
                    # Don't mark as new since it already existed
                    existing_job.is_new_in_last_hour = False
                else:
                    # Create new job entry
                    new_job = Job(
                        source=source,
                        job_title=job_data.get('job_title', '')[:500],
                        company=job_data.get('company', '')[:500],
                        location=job_data.get('location', '')[:500],
                        job_url=job_data.get('job_url', '')[:1000],
                        description=job_data.get('description', ''),
                        salary=job_data.get('salary', '')[:200],
                        job_type=job_data.get('job_type', '')[:200],
                        posted_date=job_data.get('posted_date', '')[:200],
                        first_seen=datetime.utcnow(),
                        last_seen=datetime.utcnow(),
                        is_new_in_last_hour=True  # Mark as new
                    )
                    db.session.add(new_job)
                    new_jobs_count += 1
                
            except Exception as e:
                print(f"Error saving job: {str(e)}")
                continue
        
        db.session.commit()
        return total_jobs, new_jobs_count


def run_linkedin_scraper():
    """Run LinkedIn scraper and save to database"""
    print(f"\n{'='*50}")
    print(f"Running LinkedIn Scraper - {datetime.now()}")
    print(f"{'='*50}\n")
    
    with app.app_context():
        # Create scraper run entry
        scraper_run = ScraperRun(
            source='linkedin',
            start_time=datetime.utcnow(),
            status='running'
        )
        db.session.add(scraper_run)
        db.session.commit()
        
        try:
            from linkedin_job_scraper import LinkedInJobScraper
            
            # LinkedIn URL for last 1 hour jobs
            url = "https://www.linkedin.com/jobs/search/?f_TPR=r3600&keywords=embedded%20hardware"
            
            scraper = LinkedInJobScraper(url)
            scraper.scrape_jobs()
            
            # Convert to standardized format
            jobs_data = []
            for job in scraper.jobs:
                jobs_data.append({
                    'job_title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'location': job.get('location', ''),
                    'job_url': job.get('link', ''),
                    'description': job.get('description', ''),
                    'salary': job.get('salary', ''),
                    'job_type': job.get('job_type', ''),
                    'posted_date': job.get('posted_date', '')
                })
            
            # Save to database
            total, new = save_jobs_to_db(jobs_data, 'linkedin')
            
            # Update scraper run
            scraper_run.end_time = datetime.utcnow()
            scraper_run.status = 'completed'
            scraper_run.jobs_found = total
            scraper_run.new_jobs = new
            db.session.commit()
            
            print(f"\nLinkedIn Scraper completed: {total} jobs found, {new} new jobs")
            return True
            
        except Exception as e:
            print(f"Error running LinkedIn scraper: {str(e)}")
            scraper_run.end_time = datetime.utcnow()
            scraper_run.status = 'failed'
            scraper_run.error_message = str(e)
            db.session.commit()
            return False


def run_stepstone_scraper():
    """Run Stepstone scraper and save to database"""
    print(f"\n{'='*50}")
    print(f"Running Stepstone Scraper - {datetime.now()}")
    print(f"{'='*50}\n")
    
    with app.app_context():
        # Create scraper run entry
        scraper_run = ScraperRun(
            source='stepstone',
            start_time=datetime.utcnow(),
            status='running'
        )
        db.session.add(scraper_run)
        db.session.commit()
        
        try:
            from stepstone_scraper import StepstoneScraper
            
            scraper = StepstoneScraper()
            scraper.scrape_all_pages(max_pages=5)  # Scrape first 5 pages
            
            # Convert to standardized format
            jobs_data = []
            for job in scraper.jobs:
                jobs_data.append({
                    'job_title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'location': job.get('location', ''),
                    'job_url': job.get('url', ''),
                    'description': job.get('description', ''),
                    'salary': job.get('salary', ''),
                    'job_type': job.get('employment_type', ''),
                    'posted_date': job.get('posted_date', '')
                })
            
            # Save to database
            total, new = save_jobs_to_db(jobs_data, 'stepstone')
            
            # Update scraper run
            scraper_run.end_time = datetime.utcnow()
            scraper_run.status = 'completed'
            scraper_run.jobs_found = total
            scraper_run.new_jobs = new
            db.session.commit()
            
            print(f"\nStepstone Scraper completed: {total} jobs found, {new} new jobs")
            return True
            
        except Exception as e:
            print(f"Error running Stepstone scraper: {str(e)}")
            scraper_run.end_time = datetime.utcnow()
            scraper_run.status = 'failed'
            scraper_run.error_message = str(e)
            db.session.commit()
            return False


def run_glassdoor_scraper():
    """Run Glassdoor scraper and save to database"""
    print(f"\n{'='*50}")
    print(f"Running Glassdoor Scraper - {datetime.now()}")
    print(f"{'='*50}\n")
    
    with app.app_context():
        # Create scraper run entry
        scraper_run = ScraperRun(
            source='glassdoor',
            start_time=datetime.utcnow(),
            status='running'
        )
        db.session.add(scraper_run)
        db.session.commit()
        
        try:
            from glassdoor_scraper import scrape_glassdoor_jobs
            
            # Glassdoor URL for embedded hardware jobs in last 24 hours
            url = "https://www.glassdoor.de/Job/embedded-hardware-jobs-SRCH_KO0,17.htm?fromAge=1"
            
            jobs = scrape_glassdoor_jobs(url)
            
            # Jobs are already in correct format
            jobs_data = []
            for job in jobs:
                jobs_data.append({
                    'job_title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'location': job.get('location', ''),
                    'job_url': job.get('url', ''),
                    'description': job.get('description', ''),
                    'salary': job.get('salary', ''),
                    'job_type': job.get('job_type', ''),
                    'posted_date': job.get('posted_date', '')
                })
            
            # Save to database
            total, new = save_jobs_to_db(jobs_data, 'glassdoor')
            
            # Update scraper run
            scraper_run.end_time = datetime.utcnow()
            scraper_run.status = 'completed'
            scraper_run.jobs_found = total
            scraper_run.new_jobs = new
            db.session.commit()
            
            print(f"\nGlassdoor Scraper completed: {total} jobs found, {new} new jobs")
            return True
            
        except Exception as e:
            print(f"Error running Glassdoor scraper: {str(e)}")
            scraper_run.end_time = datetime.utcnow()
            scraper_run.status = 'failed'
            scraper_run.error_message = str(e)
            db.session.commit()
            return False


if __name__ == '__main__':
    # Test the scrapers
    print("Testing LinkedIn scraper...")
    run_linkedin_scraper()
    
    print("\nTesting Stepstone scraper...")
    run_stepstone_scraper()
    
    print("\nTesting Glassdoor scraper...")
    run_glassdoor_scraper()
