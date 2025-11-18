#!/bin/bash

# Diagnostic script for Job Hunter container
# Checks current state and identifies problems

CONTAINER_NAME="${1:-job_hunter}"

echo ""
echo "============================================================"
echo "  Job Hunter Container Diagnostic"
echo "============================================================"
echo ""
echo "Checking container: $CONTAINER_NAME"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_section() {
    echo ""
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

print_check() {
    echo -e "${BLUE}🔍 Checking: $1${NC}"
}

print_pass() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
}

print_fail() {
    echo -e "${RED}❌ FAIL: $1${NC}"
}

print_warn() {
    echo -e "${YELLOW}⚠️  WARN: $1${NC}"
}

# Check 1: Container Status
print_section "1. Container Status"
print_check "Is container running?"
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_pass "Container is running"
    CONTAINER_STATUS=$(docker ps --filter "name=^${CONTAINER_NAME}$" --format "{{.Status}}")
    echo "   Status: $CONTAINER_STATUS"
else
    print_fail "Container is not running!"
    echo ""
    echo "Available containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    exit 1
fi

# Check 2: Database Files
print_section "2. Database Files"
print_check "Looking for database files..."
DB_FILES=$(docker exec "$CONTAINER_NAME" find /app -name "*.db" -type f 2>/dev/null)
if [ -n "$DB_FILES" ]; then
    print_pass "Found database file(s)"
    echo "$DB_FILES" | while read -r file; do
        SIZE=$(docker exec "$CONTAINER_NAME" stat -f %z "$file" 2>/dev/null || docker exec "$CONTAINER_NAME" stat -c %s "$file" 2>/dev/null)
        echo "   📄 $file (${SIZE} bytes)"
    done
else
    print_fail "No database files found!"
    echo "   This means the database hasn't been created yet."
fi

# Check 3: Database Content
print_section "3. Database Content"

# Try different possible locations
for DB_PATH in "/app/data/jobs.db" "/app/instance/jobs.db" "/app/jobs.db"; do
    if docker exec "$CONTAINER_NAME" test -f "$DB_PATH" 2>/dev/null; then
        echo "Checking database: $DB_PATH"
        
        print_check "Job count in database..."
        JOB_COUNT=$(docker exec "$CONTAINER_NAME" sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM jobs;" 2>/dev/null || echo "ERROR")
        if [ "$JOB_COUNT" = "ERROR" ]; then
            print_fail "Cannot query database"
        elif [ "$JOB_COUNT" = "0" ]; then
            print_fail "Database has ZERO jobs"
        else
            print_pass "Database has $JOB_COUNT jobs"
        fi
        
        print_check "Scraper run history..."
        SCRAPER_RUNS=$(docker exec "$CONTAINER_NAME" sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM scraper_runs;" 2>/dev/null || echo "ERROR")
        if [ "$SCRAPER_RUNS" = "ERROR" ]; then
            print_warn "Cannot query scraper_runs table"
        elif [ "$SCRAPER_RUNS" = "0" ]; then
            print_fail "No scraper runs recorded (scrapers never ran)"
        else
            print_pass "Found $SCRAPER_RUNS scraper run(s)"
            
            # Show recent runs
            echo ""
            echo "Recent scraper runs:"
            docker exec "$CONTAINER_NAME" sqlite3 "$DB_PATH" \
                "SELECT source, status, jobs_found, new_jobs, datetime(start_time, 'localtime') 
                 FROM scraper_runs 
                 ORDER BY start_time DESC 
                 LIMIT 5;" 2>/dev/null | while read -r line; do
                echo "   • $line"
            done
        fi
        
        print_check "Jobs by source..."
        for SOURCE in linkedin stepstone glassdoor; do
            COUNT=$(docker exec "$CONTAINER_NAME" sqlite3 "$DB_PATH" \
                "SELECT COUNT(*) FROM jobs WHERE source='$SOURCE';" 2>/dev/null || echo "0")
            echo "   📊 $SOURCE: $COUNT jobs"
        done
        
        break
    fi
done

# Check 4: Application Configuration
print_section "4. Application Configuration"
print_check "Database configuration..."
DB_CONFIG=$(docker exec "$CONTAINER_NAME" grep -r "SQLALCHEMY_DATABASE_URI" /app/app/app.py 2>/dev/null || echo "NOT FOUND")
if [[ "$DB_CONFIG" == *"sqlite:///jobs.db"* ]]; then
    print_warn "Using relative database path (can cause issues)"
    echo "   Found: $DB_CONFIG"
    echo "   ⚠️  This should be changed to an absolute path"
elif [[ "$DB_CONFIG" == *"sqlite:///"* ]]; then
    print_pass "Using absolute database path"
    echo "   Found: $DB_CONFIG"
else
    print_fail "Cannot determine database configuration"
fi

# Check 5: Scheduler Status
print_section "5. Scheduler Status"
print_check "Looking for scheduler initialization in logs..."
SCHEDULER_INIT=$(docker logs "$CONTAINER_NAME" 2>&1 | grep -i "scheduler initialized" | tail -1)
if [ -n "$SCHEDULER_INIT" ]; then
    print_pass "Scheduler was initialized"
    echo "   $SCHEDULER_INIT"
else
    print_fail "No scheduler initialization found in logs"
fi

print_check "Looking for scheduled jobs in logs..."
SCHEDULED_JOBS=$(docker logs "$CONTAINER_NAME" 2>&1 | grep -i "scheduled jobs:" -A 5 | tail -6)
if [ -n "$SCHEDULED_JOBS" ]; then
    print_pass "Found scheduled jobs"
    echo "$SCHEDULED_JOBS"
else
    print_warn "No scheduled jobs information in logs"
fi

# Check 6: Scraper Activity
print_section "6. Scraper Activity"
print_check "Looking for scraper runs in logs..."
SCRAPER_LOGS=$(docker logs "$CONTAINER_NAME" 2>&1 | grep -E "(Running|Scraper completed|scraper)" | tail -10)
if [ -n "$SCRAPER_LOGS" ]; then
    print_pass "Found scraper activity"
    echo "$SCRAPER_LOGS"
else
    print_fail "No scraper activity found in logs"
    echo "   ⚠️  Scrapers have never run!"
fi

# Check 7: Recent Errors
print_section "7. Recent Errors"
print_check "Looking for errors in logs..."
ERRORS=$(docker logs "$CONTAINER_NAME" 2>&1 | grep -iE "(error|exception|failed|traceback)" | tail -10)
if [ -n "$ERRORS" ]; then
    print_warn "Found errors in logs"
    echo "$ERRORS"
else
    print_pass "No recent errors found"
fi

# Check 8: API Endpoints
print_section "8. API Endpoint Tests"

# Get container IP or use localhost
CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$CONTAINER_NAME" 2>/dev/null)
if [ -z "$CONTAINER_IP" ]; then
    CONTAINER_IP="localhost"
fi

# Get port
CONTAINER_PORT=$(docker port "$CONTAINER_NAME" 5000 2>/dev/null | cut -d: -f2)
if [ -z "$CONTAINER_PORT" ]; then
    CONTAINER_PORT="5000"
fi

API_URL="http://${CONTAINER_IP}:${CONTAINER_PORT}"

print_check "Testing API connection to $API_URL..."
if curl -s -o /dev/null -w "%{http_code}" "$API_URL/" --max-time 5 | grep -q "200"; then
    print_pass "API is responding"
    
    # Test stats endpoint
    print_check "Testing /api/stats endpoint..."
    STATS=$(curl -s "$API_URL/api/stats" --max-time 5 2>/dev/null)
    if [ -n "$STATS" ]; then
        print_pass "Stats endpoint is working"
        TOTAL_JOBS=$(echo "$STATS" | grep -o '"total_jobs":[0-9]*' | cut -d: -f2)
        echo "   Total jobs reported by API: ${TOTAL_JOBS:-0}"
    else
        print_warn "Stats endpoint returned no data"
    fi
else
    print_fail "Cannot connect to API"
    echo "   Tried: $API_URL"
fi

# Summary
print_section "Summary & Recommendations"

if [ "$JOB_COUNT" = "0" ] || [ -z "$JOB_COUNT" ]; then
    echo -e "${RED}🔴 PROBLEM IDENTIFIED: Zero jobs in database${NC}"
    echo ""
    echo "Possible causes:"
    echo "  1. Scrapers have never run (no scraper_runs recorded)"
    echo "  2. Database file doesn't exist yet"
    echo "  3. Initial scraping is disabled in run.py"
    echo "  4. Timing protection preventing scrapers from running"
    echo ""
    echo "Solutions:"
    echo "  1. Run the fix script:"
    echo "     ./fix_zero_jobs.sh $CONTAINER_NAME"
    echo ""
    echo "  2. Or manually trigger scrapers via web UI:"
    echo "     http://${CONTAINER_IP}:${CONTAINER_PORT}/"
    echo "     Click '🔍 Search for jobs now' button"
    echo ""
    echo "  3. Or trigger via API:"
    echo "     curl http://${CONTAINER_IP}:${CONTAINER_PORT}/api/scraper/trigger/all"
    echo ""
else
    echo -e "${GREEN}🟢 Container appears to be working correctly${NC}"
    echo "   Jobs in database: $JOB_COUNT"
    echo ""
    echo "Access web interface:"
    echo "   http://${CONTAINER_IP}:${CONTAINER_PORT}/"
    echo ""
fi

echo "Useful commands:"
echo "  # View live logs"
echo "  docker logs -f $CONTAINER_NAME"
echo ""
echo "  # Restart container"
echo "  docker restart $CONTAINER_NAME"
echo ""
echo "  # Check database directly"
echo "  docker exec $CONTAINER_NAME sqlite3 /app/data/jobs.db 'SELECT COUNT(*) FROM jobs;'"
echo ""
echo "  # Trigger scrapers"
echo "  curl http://${CONTAINER_IP}:${CONTAINER_PORT}/api/scraper/trigger/all"
echo ""

print_section "Diagnostic Complete"
