#!/bin/bash

# Fix Zero Jobs Issue in Portainer Container
# This script updates the container with fixes for the zero jobs problem

set -e

CONTAINER_NAME="${1:-job_hunter}"

echo ""
echo "============================================================"
echo "  Job Hunter - Fix Zero Jobs Issue"
echo "============================================================"
echo ""
echo "Target container: $CONTAINER_NAME"
echo ""

# Function to print colored messages
print_success() {
    echo -e "\033[0;32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[0;31m❌ $1\033[0m"
}

print_info() {
    echo -e "\033[0;34mℹ️  $1\033[0m"
}

print_warning() {
    echo -e "\033[0;33m⚠️  $1\033[0m"
}

# Check if container is running
echo "Checking container status..."
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_error "Container '$CONTAINER_NAME' is not running!"
    echo ""
    echo "Available containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "Please either:"
    echo "  1. Start the container in Portainer"
    echo "  2. Provide correct container name: ./fix_zero_jobs.sh <container-name>"
    echo ""
    exit 1
fi

print_success "Container is running"
echo ""

# Step 1: Diagnose current state
echo "============================================================"
echo "  Step 1: Diagnosing Current State"
echo "============================================================"
echo ""

print_info "Checking database location..."
DB_FILES=$(docker exec "$CONTAINER_NAME" find /app -name "*.db" -type f 2>/dev/null || echo "")
if [ -z "$DB_FILES" ]; then
    print_warning "No database files found!"
else
    echo "Found database files:"
    echo "$DB_FILES"
fi
echo ""

print_info "Checking instance directory..."
docker exec "$CONTAINER_NAME" ls -la /app/instance/ 2>/dev/null || print_warning "Instance directory not found"
echo ""

print_info "Checking current job count..."
JOB_COUNT=$(docker exec "$CONTAINER_NAME" sqlite3 /app/instance/jobs.db "SELECT COUNT(*) FROM jobs;" 2>/dev/null || echo "0")
print_warning "Current jobs in database: $JOB_COUNT"
echo ""

SCRAPER_RUNS=$(docker exec "$CONTAINER_NAME" sqlite3 /app/instance/jobs.db "SELECT COUNT(*) FROM scraper_runs;" 2>/dev/null || echo "0")
print_info "Scraper runs recorded: $SCRAPER_RUNS"
echo ""

# Step 2: Backup existing files
echo "============================================================"
echo "  Step 2: Creating Backups"
echo "============================================================"
echo ""

print_info "Backing up current files..."
docker exec "$CONTAINER_NAME" cp /app/app/app.py /app/app/app.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || print_warning "Could not backup app.py"
docker exec "$CONTAINER_NAME" cp /app/run.py /app/run.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || print_warning "Could not backup run.py"
print_success "Backups created"
echo ""

# Step 3: Apply fixes
echo "============================================================"
echo "  Step 3: Applying Fixes"
echo "============================================================"
echo ""

print_info "Copying fixed app.py (database path fix)..."
if docker cp app/app.py "$CONTAINER_NAME":/app/app/app.py; then
    print_success "app.py updated"
else
    print_error "Failed to copy app.py"
    exit 1
fi

print_info "Copying fixed run.py (enable initial scraping)..."
if docker cp run.py "$CONTAINER_NAME":/app/run.py; then
    print_success "run.py updated"
else
    print_error "Failed to copy run.py"
    exit 1
fi

echo ""

# Step 4: Create data directory
echo "============================================================"
echo "  Step 4: Setting Up Data Directory"
echo "============================================================"
echo ""

print_info "Creating /app/data directory..."
docker exec "$CONTAINER_NAME" mkdir -p /app/data
docker exec "$CONTAINER_NAME" chmod 777 /app/data
print_success "Data directory created"
echo ""

# Step 5: Restart container
echo "============================================================"
echo "  Step 5: Restarting Container"
echo "============================================================"
echo ""

print_info "Restarting container..."
if docker restart "$CONTAINER_NAME"; then
    print_success "Container restarted"
else
    print_error "Failed to restart container"
    exit 1
fi

echo ""
print_info "Waiting 10 seconds for container to start..."
sleep 10

# Step 6: Verify fix
echo ""
echo "============================================================"
echo "  Step 6: Verifying Fix"
echo "============================================================"
echo ""

print_info "Checking if container is running..."
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_success "Container is running"
else
    print_error "Container failed to start!"
    echo ""
    echo "Check logs:"
    echo "  docker logs $CONTAINER_NAME"
    exit 1
fi

echo ""
print_info "Checking for database file in new location..."
sleep 5
NEW_DB=$(docker exec "$CONTAINER_NAME" ls -la /app/data/jobs.db 2>/dev/null || echo "")
if [ -n "$NEW_DB" ]; then
    print_success "Database file found at /app/data/jobs.db"
    echo "$NEW_DB"
else
    print_warning "Database file not yet created (will be created on first scrape)"
fi

echo ""
print_info "Checking container logs for scraper activity..."
SCRAPER_LOGS=$(docker logs "$CONTAINER_NAME" 2>&1 | grep -i "scraper" | tail -5)
if [ -n "$SCRAPER_LOGS" ]; then
    echo "$SCRAPER_LOGS"
else
    print_warning "No scraper activity in logs yet"
fi

echo ""
echo "============================================================"
echo "  ✅ Fix Applied Successfully!"
echo "============================================================"
echo ""

print_success "The container has been updated with fixes:"
echo "  1. ✅ Database path fixed (now uses /app/data/jobs.db)"
echo "  2. ✅ Initial scraping enabled (runs on startup)"
echo "  3. ✅ Data directory created"
echo ""

echo "What happens next:"
echo "  1. ⏳ Initial scraping is running in background (2-5 minutes)"
echo "  2. 🔄 Scrapers will collect jobs from all sources"
echo "  3. 📊 Jobs will appear in web interface when complete"
echo ""

echo "How to verify:"
echo "  1. Wait 2-5 minutes for initial scraping to complete"
echo "  2. Check web interface: http://your-server-ip:5000"
echo "  3. View logs: docker logs -f $CONTAINER_NAME"
echo "  4. Check API: curl http://your-server-ip:5000/api/stats"
echo ""

echo "Monitoring commands:"
echo "  # Watch logs in real-time"
echo "  docker logs -f $CONTAINER_NAME"
echo ""
echo "  # Check database"
echo "  docker exec $CONTAINER_NAME sqlite3 /app/data/jobs.db \"SELECT COUNT(*) FROM jobs;\""
echo ""
echo "  # Check via API (replace localhost with your server IP)"
echo "  curl http://localhost:5000/api/stats | jq"
echo ""

print_info "Checking logs now (last 20 lines)..."
echo ""
echo "----------------------------------------"
docker logs "$CONTAINER_NAME" 2>&1 | tail -20
echo "----------------------------------------"
echo ""

print_success "Setup complete! Check the logs above for scraper progress."
echo ""
