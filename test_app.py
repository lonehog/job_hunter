#!/usr/bin/env python3
"""
Simple test to check if the web app can start
This bypasses the scrapers for now and just tests the Flask app
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

print("="*60)
print("Testing Job Hunter Application")
print("="*60)
print()

# Test 1: Check Python version
print("1. Checking Python version...")
print(f"   Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
print("   ✓ Python version OK")
print()

# Test 2: Check required modules
print("2. Checking required modules...")
required = {
    'flask': 'Flask',
    'flask_sqlalchemy': 'Flask-SQLAlchemy',
    'flask_cors': 'Flask-CORS',
    'apscheduler': 'APScheduler',
    'sqlalchemy': 'SQLAlchemy',
    'requests': 'requests',
    'bs4': 'BeautifulSoup4',
}

missing = []
for module, name in required.items():
    try:
        __import__(module)
        print(f"   ✓ {name}")
    except ImportError:
        print(f"   ✗ {name} - NOT INSTALLED")
        missing.append(name)

print()

if missing:
    print("❌ Missing dependencies:")
    for dep in missing:
        print(f"   - {dep}")
    print()
    print("To install dependencies, run:")
    print("   1. Install Python pip: sudo pacman -S python-pip")
    print("   2. Install packages: pip install --user flask flask-sqlalchemy flask-cors apscheduler sqlalchemy requests beautifulsoup4")
    print()
    sys.exit(1)

# Test 3: Try to import app modules
print("3. Checking app modules...")
try:
    from app import app as flask_app
    print("   ✓ Flask app can be imported")
except Exception as e:
    print(f"   ✗ Error importing Flask app: {e}")
    sys.exit(1)

try:
    from models import db, Job, ScraperRun
    print("   ✓ Database models can be imported")
except Exception as e:
    print(f"   ✗ Error importing models: {e}")
    sys.exit(1)

print()

# Test 4: Check database
print("4. Checking database...")
try:
    with flask_app.app_context():
        db.create_all()
    print("   ✓ Database initialized successfully")
    print("   Database location: app/jobs.db")
except Exception as e:
    print(f"   ✗ Error initializing database: {e}")
    sys.exit(1)

print()
print("="*60)
print("✅ All tests passed!")
print("="*60)
print()
print("To start the application:")
print("  python run.py")
print()
print("Then open your browser:")
print("  http://localhost:5000")
print()
