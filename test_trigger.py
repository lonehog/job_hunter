#!/usr/bin/env python3
"""
Test script to verify the trigger endpoint works
"""
import requests
import time

BASE_URL = "http://localhost:5000"

def test_can_run():
    """Test the can-run endpoint"""
    print("\n" + "="*60)
    print("Testing /api/scraper/can-run endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/scraper/can-run")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_trigger_all():
    """Test triggering all scrapers"""
    print("\n" + "="*60)
    print("Testing /api/scraper/trigger/all endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/scraper/trigger/all")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 429:
            print("\n⏰ Scrapers need more time before running again")
        elif response.status_code == 200:
            print("\n✅ Scrapers triggered successfully!")
        
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_stats():
    """Test the stats endpoint"""
    print("\n" + "="*60)
    print("Testing /api/stats endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"\nTotal Jobs: {data.get('total_jobs', 0)}")
        print(f"New in Last Hour: {data.get('new_jobs_last_hour', 0)}")
        print(f"LinkedIn Jobs: {data.get('linkedin_jobs', 0)}")
        print(f"Stepstone Jobs: {data.get('stepstone_jobs', 0)}")
        print(f"Glassdoor Jobs: {data.get('glassdoor_jobs', 0)}")
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    print("\n🧪 Job Hunter - Testing Scraper Trigger Functionality")
    print("="*60)
    
    # Test 1: Check if scrapers can run
    can_run_data = test_can_run()
    
    # Test 2: Try to trigger scrapers
    if can_run_data and can_run_data.get('all', {}).get('can_run'):
        print("\n✅ Scrapers are ready to run!")
        trigger_data = test_trigger_all()
    else:
        print("\n⏰ Scrapers are not ready yet (need to wait 1 hour)")
        if can_run_data:
            wait_time = can_run_data.get('all', {}).get('time_until_next_run_minutes', 0)
            print(f"   Wait {wait_time:.1f} more minutes")
    
    # Test 3: Check current stats
    test_stats()
    
    print("\n" + "="*60)
    print("✅ Testing completed!")
    print("="*60 + "\n")
