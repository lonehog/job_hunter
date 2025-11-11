#!/usr/bin/env python3
"""
Installation checker for Job Hunter
Verifies all dependencies and configurations
"""

import sys
import os

def check_python_version():
    """Check if Python version is 3.7+"""
    print("Checking Python version...", end=" ")
    if sys.version_info >= (3, 7):
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
        return True
    else:
        print(f"✗ Python {sys.version_info.major}.{sys.version_info.minor} (Need 3.7+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_cors',
        'apscheduler',
        'requests',
        'bs4',
        'selenium'
    ]
    
    print("\nChecking dependencies:")
    all_installed = True
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (not installed)")
            all_installed = False
    
    return all_installed

def check_file_structure():
    """Check if all required files exist"""
    print("\nChecking file structure:")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        'app/models.py',
        'app/app.py',
        'app/scheduler.py',
        'app/scraper_integration.py',
        'templates/base.html',
        'templates/home.html',
        'templates/linkedin.html',
        'templates/stepstone.html',
        'templates/glassdoor.html',
        'run.py',
        'requirements.txt',
        'start.sh'
    ]
    
    all_exist = True
    
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (missing)")
            all_exist = False
    
    return all_exist

def check_scraper_folders():
    """Check if scraper folders exist"""
    print("\nChecking scraper folders:")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    scrapers = ['Linkedin', 'Stepstone', 'Glassdoor']
    all_exist = True
    
    for scraper in scrapers:
        scraper_path = os.path.join(base_dir, scraper)
        if os.path.exists(scraper_path) and os.path.isdir(scraper_path):
            print(f"  ✓ {scraper}/")
        else:
            print(f"  ✗ {scraper}/ (missing)")
            all_exist = False
    
    return all_exist

def main():
    """Run all checks"""
    print("=" * 60)
    print("Job Hunter - Installation Checker")
    print("=" * 60)
    print()
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_file_structure(),
        check_scraper_folders()
    ]
    
    print()
    print("=" * 60)
    
    if all(checks):
        print("✓ All checks passed! You're ready to run Job Hunter.")
        print()
        print("To start the application:")
        print("  ./start.sh")
        print("  or")
        print("  python run.py")
        print()
        print("Then open: http://localhost:5000")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print()
        print("To install dependencies:")
        print("  pip install -r requirements.txt")
    
    print("=" * 60)
    
    return all(checks)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
