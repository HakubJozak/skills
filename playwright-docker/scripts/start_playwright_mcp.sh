#!/bin/bash
# Start Playwright MCP server in Docker container
# This script handles container lifecycle and provides helpful status messages

set -e

CONTAINER_NAME="playwright-mcp"
IMAGE="mcr.microsoft.com/playwright-mcp:latest"
PORT="${PLAYWRIGHT_PORT:-8931}"
BROWSER="${PLAYWRIGHT_BROWSER:-chromium}"
MODE="${PLAYWRIGHT_MODE:-headless}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Starting Playwright MCP Docker container..."

# Check if container is already running
if docker ps -q -f name="^${CONTAINER_NAME}$" | grep -q .; then
    echo -e "${YELLOW}Container '${CONTAINER_NAME}' is already running.${NC}"
    echo "To restart, first run: docker stop ${CONTAINER_NAME}"
    exit 0
fi

# Check if stopped container exists and remove it
if docker ps -aq -f name="^${CONTAINER_NAME}$" | grep -q .; then
    echo "Removing stopped container..."
    docker rm "${CONTAINER_NAME}"
fi

# Build command flags
CMD_FLAGS="--${MODE} --browser ${BROWSER} --no-sandbox --port ${PORT}"

# Pull latest image
echo "Pulling latest image..."
docker pull "${IMAGE}"

# Start container
echo "Starting container on port ${PORT}..."
docker run -d -i --rm --init \
    --name "${CONTAINER_NAME}" \
    --ipc=host \
    --add-host=hostmachine:host-gateway \
    -p "${PORT}:${PORT}" \
    "${IMAGE}" \
    node cli.js ${CMD_FLAGS}

# Wait a moment for container to start
sleep 2

# Check if container is running
if docker ps -q -f name="^${CONTAINER_NAME}$" | grep -q .; then
    echo -e "${GREEN}Playwright MCP container started successfully!${NC}"
    echo ""
    echo "Container name: ${CONTAINER_NAME}"
    echo "Port: ${PORT}"
    echo "Browser: ${BROWSER}"
    echo "Mode: ${MODE}"
    echo ""
    echo "Commands:"
    echo "  View logs:  docker logs -f ${CONTAINER_NAME}"
    echo "  Stop:       docker stop ${CONTAINER_NAME}"
    echo "  Status:     docker ps -f name=${CONTAINER_NAME}"
    echo ""
    echo "Use http://hostmachine:PORT to access local services from the container."
else
    echo -e "${RED}Failed to start container. Check logs:${NC}"
    docker logs "${CONTAINER_NAME}"
    exit 1
fi
