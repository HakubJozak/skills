#!/bin/bash
# Check status of Playwright MCP Docker container

CONTAINER_NAME="${1:-playwright-mcp}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Playwright MCP Container Status"
echo "================================"
echo ""

# Check if container exists and is running
if docker ps -q -f name="^${CONTAINER_NAME}$" | grep -q .; then
    echo -e "${GREEN}Status: RUNNING${NC}"

    # Get container details
    echo ""
    echo "Container Details:"
    docker ps -f name="^${CONTAINER_NAME}$" --format "  Name: {{.Names}}\n  Image: {{.Image}}\n  Status: {{.Status}}\n  Ports: {{.Ports}}"

    # Get resource usage
    echo ""
    echo "Resource Usage:"
    docker stats "${CONTAINER_NAME}" --no-stream --format "  CPU: {{.CPUPerc}}\n  Memory: {{.MemUsage}} ({{.MemPerc}})"

    # Check logs for errors
    echo ""
    echo "Recent Logs (last 5 lines):"
    docker logs --tail 5 "${CONTAINER_NAME}" 2>&1 | sed 's/^/  /'

    # Test connectivity
    echo ""
    echo "Connectivity:"
    PORT=$(docker port "${CONTAINER_NAME}" | grep -o "0.0.0.0:[0-9]*" | cut -d: -f2 | head -1)
    if [ -n "$PORT" ]; then
        if curl -s -o /dev/null -w "%{http_code}" "http://localhost:${PORT}" >/dev/null 2>&1; then
            echo -e "  ${GREEN}Port ${PORT}: Accessible${NC}"
        else
            echo -e "  ${YELLOW}Port ${PORT}: Exposed but not responding${NC}"
        fi
    fi

elif docker ps -aq -f name="^${CONTAINER_NAME}$" | grep -q .; then
    echo -e "${YELLOW}Status: STOPPED${NC}"
    echo ""
    echo "Container exists but is not running."
    echo "Start with: ./scripts/start_playwright_mcp.sh"

else
    echo -e "${RED}Status: NOT FOUND${NC}"
    echo ""
    echo "Container does not exist."
    echo "Create with: ./scripts/start_playwright_mcp.sh"
fi

echo ""
echo "Commands:"
echo "  Start:  ./scripts/start_playwright_mcp.sh"
echo "  Stop:   ./scripts/stop_playwright_mcp.sh"
echo "  Logs:   docker logs -f ${CONTAINER_NAME}"
echo "  Shell:  docker exec -it ${CONTAINER_NAME} /bin/bash"
