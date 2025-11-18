"""
Flask application for Job Hunter
"""
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
from app.models import db, Job, ScraperRun
import os

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
CORS(app)

# Configuration
# Use absolute path for database to ensure it's in a predictable location
DB_PATH = os.environ.get('DATABASE_PATH')
if not DB_PATH:
    # Default to /app/data/jobs.db in container, or local path if running locally
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(data_dir, exist_ok=True)
    DB_PATH = os.path.join(data_dir, 'jobs.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

print(f"\n{'='*60}")
print(f"📁 Database location: {DB_PATH}")
print(f"{'='*60}\n")

# Initialize database
db.init_app(app)


# Create tables
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    """Home page"""
    return render_template('home.html')


@app.route('/linkedin')
def linkedin_page():
    """LinkedIn jobs page"""
    return render_template('linkedin.html')


@app.route('/stepstone')
def stepstone_page():
    """Stepstone jobs page"""
    return render_template('stepstone.html')


@app.route('/glassdoor')
def glassdoor_page():
    """Glassdoor jobs page"""
    return render_template('glassdoor.html')


# API Endpoints

@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    try:
        total_jobs = Job.query.count()
        linkedin_jobs = Job.query.filter_by(source='linkedin').count()
        stepstone_jobs = Job.query.filter_by(source='stepstone').count()
        glassdoor_jobs = Job.query.filter_by(source='glassdoor').count()
        
        # Jobs in last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        new_jobs_last_hour = Job.query.filter(Job.first_seen >= one_hour_ago).count()
        
        linkedin_last_hour = Job.query.filter(
            Job.source == 'linkedin',
            Job.is_new_in_last_hour == True
        ).count()
        
        stepstone_last_hour = Job.query.filter(
            Job.source == 'stepstone',
            Job.is_new_in_last_hour == True
        ).count()
        
        glassdoor_last_hour = Job.query.filter(
            Job.source == 'glassdoor',
            Job.is_new_in_last_hour == True
        ).count()
        
        # Last scraper runs
        last_runs = {}
        for source in ['linkedin', 'stepstone', 'glassdoor']:
            last_run = ScraperRun.query.filter_by(source=source).order_by(
                ScraperRun.start_time.desc()
            ).first()
            if last_run:
                last_runs[source] = last_run.to_dict()
            else:
                last_runs[source] = None
        
        return jsonify({
            'total_jobs': total_jobs,
            'linkedin_jobs': linkedin_jobs,
            'stepstone_jobs': stepstone_jobs,
            'glassdoor_jobs': glassdoor_jobs,
            'new_jobs_last_hour': new_jobs_last_hour,
            'linkedin_last_hour': linkedin_last_hour,
            'stepstone_last_hour': stepstone_last_hour,
            'glassdoor_last_hour': glassdoor_last_hour,
            'last_runs': last_runs,
            'last_updated': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs/<source>')
def get_jobs_by_source(source):
    """Get jobs from specific source (only those posted in last hour)"""
    try:
        if source not in ['linkedin', 'stepstone', 'glassdoor']:
            return jsonify({'error': 'Invalid source'}), 400
        
        # Get jobs marked as new in last hour
        jobs = Job.query.filter_by(
            source=source,
            is_new_in_last_hour=True
        ).order_by(Job.first_seen.desc()).all()
        
        return jsonify({
            'source': source,
            'count': len(jobs),
            'jobs': [job.to_dict() for job in jobs]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs/all')
def get_all_jobs():
    """Get all jobs"""
    try:
        jobs = Job.query.order_by(Job.first_seen.desc()).limit(1000).all()
        return jsonify({
            'count': len(jobs),
            'jobs': [job.to_dict() for job in jobs]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scraper/status')
def get_scraper_status():
    """Get status of all scrapers"""
    try:
        status = {}
        for source in ['linkedin', 'stepstone', 'glassdoor']:
            # Get last 5 runs
            runs = ScraperRun.query.filter_by(source=source).order_by(
                ScraperRun.start_time.desc()
            ).limit(5).all()
            
            # Get last completed run
            last_completed = ScraperRun.query.filter_by(
                source=source,
                status='completed'
            ).order_by(ScraperRun.end_time.desc()).first()
            
            can_run = True
            time_until_next_run = None
            time_since_last_run = None
            
            if last_completed and last_completed.end_time:
                time_diff = datetime.utcnow() - last_completed.end_time
                time_since_last_run = time_diff.total_seconds() / 60  # in minutes
                
                if time_diff.total_seconds() < 3600:
                    can_run = False
                    time_until_next_run = (3600 - time_diff.total_seconds()) / 60  # in minutes
            
            status[source] = {
                'recent_runs': [run.to_dict() for run in runs],
                'can_run': can_run,
                'time_since_last_run_minutes': round(time_since_last_run, 1) if time_since_last_run else None,
                'time_until_next_run_minutes': round(time_until_next_run, 1) if time_until_next_run else 0
            }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scraper/can-run')
def can_run_scrapers():
    """Check if scrapers can be run (1 hour has passed)"""
    try:
        result = {}
        
        # Check each individual scraper
        for source in ['linkedin', 'stepstone', 'glassdoor']:
            last_run = ScraperRun.query.filter_by(
                source=source,
                status='completed'
            ).order_by(ScraperRun.end_time.desc()).first()
            
            can_run = True
            time_until_next = 0
            
            if last_run and last_run.end_time:
                time_diff = datetime.utcnow() - last_run.end_time
                if time_diff.total_seconds() < 3600:
                    can_run = False
                    time_until_next = (3600 - time_diff.total_seconds()) / 60
            
            result[source] = {
                'can_run': can_run,
                'time_until_next_run_minutes': round(time_until_next, 1)
            }
        
        # Check if batch can run
        sources = ['linkedin', 'stepstone', 'glassdoor']
        latest_completion = None
        
        for src in sources:
            last_run = ScraperRun.query.filter_by(
                source=src,
                status='completed'
            ).order_by(ScraperRun.end_time.desc()).first()
            
            if last_run and last_run.end_time:
                if latest_completion is None or last_run.end_time > latest_completion:
                    latest_completion = last_run.end_time
        
        batch_can_run = True
        batch_time_until_next = 0
        
        if latest_completion:
            time_diff = datetime.utcnow() - latest_completion
            if time_diff.total_seconds() < 3600:
                batch_can_run = False
                batch_time_until_next = (3600 - time_diff.total_seconds()) / 60
        
        result['all'] = {
            'can_run': batch_can_run,
            'time_until_next_run_minutes': round(batch_time_until_next, 1)
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scraper/trigger/<source>')
def trigger_scraper(source):
    """Manually trigger a scraper (will check if 1 hour has passed)"""
    try:
        if source not in ['linkedin', 'stepstone', 'glassdoor', 'all']:
            return jsonify({'error': 'Invalid source'}), 400
        
        from app.scheduler import run_scraper_task, run_all_scrapers, check_last_run_time
        
        # Check timing before running
        if source == 'all':
            # Check if enough time has passed for batch run
            with app.app_context():
                sources = ['linkedin', 'stepstone', 'glassdoor']
                latest_completion = None
                
                for src in sources:
                    last_run = ScraperRun.query.filter_by(
                        source=src,
                        status='completed'
                    ).order_by(ScraperRun.end_time.desc()).first()
                    
                    if last_run and last_run.end_time:
                        if latest_completion is None or last_run.end_time > latest_completion:
                            latest_completion = last_run.end_time
                
                if latest_completion:
                    time_since_last = datetime.utcnow() - latest_completion
                    if time_since_last.total_seconds() < 3600:
                        remaining_minutes = (3600 - time_since_last.total_seconds()) / 60
                        return jsonify({
                            'message': 'Cannot run scrapers yet',
                            'status': 'skipped',
                            'reason': f'Less than 1 hour since last batch completion. Wait {remaining_minutes:.1f} more minutes.',
                            'time_since_last_minutes': time_since_last.total_seconds() / 60
                        }), 429
            
            # Run all scrapers
            import threading
            thread = threading.Thread(target=run_all_scrapers, daemon=True)
            thread.start()
        else:
            # Check timing for individual scraper
            if not check_last_run_time(source):
                with app.app_context():
                    last_run = ScraperRun.query.filter_by(
                        source=source,
                        status='completed'
                    ).order_by(ScraperRun.end_time.desc()).first()
                    
                    if last_run and last_run.end_time:
                        time_since_last = datetime.utcnow() - last_run.end_time
                        remaining_minutes = (3600 - time_since_last.total_seconds()) / 60
                        return jsonify({
                            'message': f'Cannot run {source} scraper yet',
                            'status': 'skipped',
                            'reason': f'Less than 1 hour since last run. Wait {remaining_minutes:.1f} more minutes.',
                            'time_since_last_minutes': time_since_last.total_seconds() / 60
                        }), 429
            
            # Run individual scraper
            import threading
            thread = threading.Thread(target=lambda: run_scraper_task(source), daemon=True)
            thread.start()
        
        return jsonify({
            'message': f'Scraper triggered for {source}',
            'status': 'running'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
