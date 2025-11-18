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
    
    # Run initial scrape on startup to populate database immediately
    # This ensures the container has jobs right away instead of waiting for hourly schedule
    print("\n" + "="*60)
    print("🚀 Running initial scrape to populate database...")
    print("="*60 + "\n")
    
    # Run initial scrape in background thread so it doesn't block app startup
    initial_scrape_thread = threading.Thread(target=run_initial_scrape, daemon=True)
    initial_scrape_thread.start()
    
    print("\n" + "="*60)
    print("🚀 Application is starting...")
    print("📱 Access the web interface at: http://localhost:5000")
    print("="*60 + "\n")
    
    # Start Flask app
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
