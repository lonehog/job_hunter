"""
Database models for Job Hunter application
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Job(db.Model):
    """Model for storing job listings"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False)  # 'linkedin', 'stepstone', 'glassdoor'
    job_title = db.Column(db.String(500))
    company = db.Column(db.String(500))
    location = db.Column(db.String(500))
    job_url = db.Column(db.String(1000), unique=True)
    description = db.Column(db.Text)
    salary = db.Column(db.String(200))
    job_type = db.Column(db.String(200))
    
    # Timestamps
    posted_date = db.Column(db.String(200))  # Original posted date from scraper
    first_seen = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # When we first scraped it
    last_seen = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Last time we saw it
    
    # Track if this job was new in the last hourly run
    is_new_in_last_hour = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Job {self.job_title} at {self.company} - {self.source}>'
    
    def to_dict(self):
        """Convert job to dictionary"""
        return {
            'id': self.id,
            'source': self.source,
            'job_title': self.job_title,
            'company': self.company,
            'location': self.location,
            'job_url': self.job_url,
            'description': self.description,
            'salary': self.salary,
            'job_type': self.job_type,
            'posted_date': self.posted_date,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_new_in_last_hour': self.is_new_in_last_hour
        }


class ScraperRun(db.Model):
    """Model for tracking scraper execution history"""
    __tablename__ = 'scraper_runs'
    
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(50))  # 'running', 'completed', 'failed'
    jobs_found = db.Column(db.Integer, default=0)
    new_jobs = db.Column(db.Integer, default=0)  # New jobs in this run
    error_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<ScraperRun {self.source} at {self.start_time}>'
    
    def to_dict(self):
        """Convert scraper run to dictionary"""
        return {
            'id': self.id,
            'source': self.source,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'jobs_found': self.jobs_found,
            'new_jobs': self.new_jobs,
            'error_message': self.error_message
        }
