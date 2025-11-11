"""
Main application entry point
Starts the Flask app with scheduler
"""
from app.app import app
from app.scheduler import init_scheduler, run_initial_scrape
import threading


def start_scheduler():
    """Start the background scheduler"""
    init_scheduler()


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Job Hunter Application")
    print("="*60 + "\n")
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Run initial scrape on startup (optional - comment out if you don't want this)
    # Uncomment the line below to run scrapers immediately on startup
    # run_initial_scrape()
    
    print("\n" + "="*60)
    print("🚀 Application is starting...")
    print("📱 Access the web interface at: http://localhost:5000")
    print("="*60 + "\n")
    
    # Start Flask app
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
