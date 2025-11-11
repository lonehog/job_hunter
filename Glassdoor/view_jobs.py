#!/usr/bin/env python3
"""
Glassdoor Jobs CSV Viewer and Analyzer
View and analyze the scraped job data
"""

import csv
from collections import Counter


def read_jobs_from_csv(filename='glassdoor_jobs.csv'):
    """Read jobs from CSV file"""
    jobs = []
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            jobs = list(reader)
        return jobs
    except FileNotFoundError:
        print(f"Error: {filename} not found. Please run glassdoor_scraper.py first.")
        return []
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []


def analyze_jobs(jobs):
    """Analyze job data and print statistics"""
    if not jobs:
        print("No jobs to analyze.")
        return
    
    print("\n" + "=" * 70)
    print("JOB DATA ANALYSIS")
    print("=" * 70)
    
    # Total jobs
    print(f"\nTotal Jobs Scraped: {len(jobs)}")
    
    # Companies
    companies = [job.get('company', 'N/A') for job in jobs]
    company_counts = Counter(companies)
    print(f"\nCompanies ({len(company_counts)}):")
    for company, count in company_counts.most_common():
        print(f"  - {company}: {count} job(s)")
    
    # Locations
    locations = [job.get('location', 'N/A') for job in jobs]
    location_counts = Counter(locations)
    print(f"\nLocations ({len(location_counts)}):")
    for location, count in location_counts.most_common():
        print(f"  - {location}: {count} job(s)")
    
    # Ratings
    ratings = []
    for job in jobs:
        rating = job.get('rating', 'N/A')
        if rating != 'N/A':
            try:
                ratings.append(float(rating.replace(',', '.')))
            except:
                pass
    
    if ratings:
        avg_rating = sum(ratings) / len(ratings)
        print(f"\nCompany Ratings:")
        print(f"  - Average Rating: {avg_rating:.2f}")
        print(f"  - Highest Rating: {max(ratings):.1f}")
        print(f"  - Lowest Rating: {min(ratings):.1f}")
    
    # Skills analysis
    all_skills = []
    for job in jobs:
        skills = job.get('skills', '')
        if skills and skills != 'N/A':
            skills_list = [s.strip() for s in skills.split(',')]
            all_skills.extend(skills_list)
    
    if all_skills:
        skill_counts = Counter(all_skills)
        print(f"\nTop Skills (appearing in job listings):")
        for skill, count in skill_counts.most_common(10):
            print(f"  - {skill}: {count} time(s)")
    
    print("\n" + "=" * 70)


def display_jobs(jobs):
    """Display all jobs in a readable format"""
    if not jobs:
        print("No jobs to display.")
        return
    
    print("\n" + "=" * 70)
    print("ALL JOB LISTINGS")
    print("=" * 70)
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job.get('job_title', 'N/A')}")
        print(f"   Company: {job.get('company', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Rating: {job.get('rating', 'N/A')}")
        
        if job.get('salary', 'N/A') != 'N/A':
            print(f"   Salary: {job.get('salary')}")
        
        if job.get('skills', 'N/A') != 'N/A':
            print(f"   Skills: {job.get('skills')}")
        
        print(f"   URL: {job.get('job_url', 'N/A')}")
        print(f"   Scraped: {job.get('scraped_date', 'N/A')}")
    
    print("\n" + "=" * 70)


def search_jobs(jobs, keyword):
    """Search jobs by keyword"""
    keyword_lower = keyword.lower()
    matching_jobs = []
    
    for job in jobs:
        # Search in all fields
        if any(keyword_lower in str(value).lower() for value in job.values()):
            matching_jobs.append(job)
    
    return matching_jobs


def main():
    """Main function"""
    import sys
    
    # Read jobs
    jobs = read_jobs_from_csv()
    
    if not jobs:
        return
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--analyze' or sys.argv[1] == '-a':
            analyze_jobs(jobs)
        elif sys.argv[1] == '--search' or sys.argv[1] == '-s':
            if len(sys.argv) > 2:
                keyword = sys.argv[2]
                matching = search_jobs(jobs, keyword)
                print(f"\nFound {len(matching)} jobs matching '{keyword}':")
                display_jobs(matching)
            else:
                print("Please provide a search keyword. Usage: python view_jobs.py --search <keyword>")
        else:
            print("Usage:")
            print("  python view_jobs.py              - Display all jobs")
            print("  python view_jobs.py --analyze    - Analyze job data")
            print("  python view_jobs.py --search <keyword> - Search jobs")
    else:
        # Default: display all jobs and analysis
        display_jobs(jobs)
        analyze_jobs(jobs)


if __name__ == "__main__":
    main()
