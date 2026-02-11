#!/bin/bash
# Stop Playwright MCP Docker container

set -e

CONTAINER_NAME="${1:-playwright-mcp}"

echo "Stopping Playwright MCP container..."

if docker ps -q -f name="^${CONTAINER_NAME}$" | grep -q .; then
    docker stop "${CONTAINER_NAME}"
    echo "Container stopped successfully."
else
    echo "Container '${CONTAINER_NAME}' is not running."
fi
