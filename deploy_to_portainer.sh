#!/bin/bash

# Deployment script for Portainer container
# This script copies the fixed files to your running container

echo "========================================"
echo "Job Hunter - Portainer Deployment Fix"
echo "========================================"
echo ""

# Check if container name is provided
CONTAINER_NAME="${1:-job-hunter}"

echo "Target container: $CONTAINER_NAME"
echo ""

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Container '$CONTAINER_NAME' is not running!"
    echo ""
    echo "Please either:"
    echo "  1. Start the container in Portainer"
    echo "  2. Provide correct container name: ./deploy_to_portainer.sh <container-name>"
    echo ""
    exit 1
fi

echo "✅ Container is running"
echo ""

# Backup existing files (optional)
echo "📦 Creating backup of existing files..."
docker exec "$CONTAINER_NAME" cp /app/app/app.py /app/app/app.py.backup 2>/dev/null
docker exec "$CONTAINER_NAME" cp /app/templates/home.html /app/templates/home.html.backup 2>/dev/null
echo "✅ Backup created"
echo ""

# Copy fixed files to container
echo "📤 Copying fixed files to container..."

if docker cp app/app.py "$CONTAINER_NAME":/app/app/app.py; then
    echo "✅ app/app.py copied successfully"
else
    echo "❌ Failed to copy app/app.py"
    exit 1
fi

if docker cp templates/home.html "$CONTAINER_NAME":/app/templates/home.html; then
    echo "✅ templates/home.html copied successfully"
else
    echo "❌ Failed to copy templates/home.html"
    exit 1
fi

echo ""
echo "🔄 Restarting container..."
if docker restart "$CONTAINER_NAME"; then
    echo "✅ Container restarted successfully"
else
    echo "❌ Failed to restart container"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ Deployment completed!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Wait 10-15 seconds for container to start"
echo "  2. Open your web interface"
echo "  3. Click '🔍 Search for jobs now' button"
echo "  4. Wait 2-5 minutes for scrapers to complete"
echo "  5. Refresh page to see new jobs"
echo ""
echo "To check container logs:"
echo "  docker logs -f $CONTAINER_NAME"
echo ""
echo "To verify files were updated:"
echo "  docker exec $CONTAINER_NAME cat /app/app/app.py | grep 'app.scheduler'"
echo ""
