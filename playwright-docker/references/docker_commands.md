# Playwright Docker Commands Reference

Complete reference for running Playwright in Docker containers.

## Container Images

### Official Images

```bash
# Microsoft Playwright MCP (recommended for MCP integration)
mcr.microsoft.com/playwright-mcp:latest

# Microsoft Playwright (for server mode)
mcr.microsoft.com/playwright:v1.58.0-noble    # Ubuntu 24.04
mcr.microsoft.com/playwright:v1.58.0-jammy    # Ubuntu 22.04
mcr.microsoft.com/playwright:v1.58.0          # Default
mcr.microsoft.com/playwright:latest           # Latest release
```

### Pull Images

```bash
# Pull specific version
docker pull mcr.microsoft.com/playwright:v1.58.0-noble

# Pull MCP image
docker pull mcr.microsoft.com/playwright-mcp:latest
```

## Running Containers

### MCP Server Mode

```bash
# Basic MCP server (headless)
docker run -d -i --rm --init \
  --name playwright-mcp \
  --ipc=host \
  -p 8931:8931 \
  mcr.microsoft.com/playwright-mcp:latest \
  node cli.js --headless --browser chromium --no-sandbox --port 8931

# With access to local services
docker run -d -i --rm --init \
  --name playwright-mcp \
  --ipc=host \
  --add-host=hostmachine:host-gateway \
  -p 8931:8931 \
  mcr.microsoft.com/playwright-mcp:latest \
  node cli.js --headless --browser chromium --no-sandbox --port 8931

# With different browser
docker run -d -i --rm --init \
  --name playwright-mcp \
  --ipc=host \
  -p 8931:8931 \
  mcr.microsoft.com/playwright-mcp:latest \
  node cli.js --headless --browser firefox --port 8931

# With headed mode (requires X11)
docker run -d -i --rm --init \
  --name playwright-mcp \
  --ipc=host \
  -p 8931:8931 \
  -e DISPLAY=:0 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  mcr.microsoft.com/playwright-mcp:latest \
  node cli.js --headed --browser chromium --no-sandbox --port 8931
```

### Playwright Server Mode

```bash
# Basic server
docker run -d --rm --init \
  --name playwright-server \
  --ipc=host \
  -p 3000:3000 \
  --user pwuser \
  --workdir /home/pwuser \
  mcr.microsoft.com/playwright:v1.58.0-noble \
  /bin/sh -c "npx -y playwright@1.58.0 run-server --port 3000 --host 0.0.0.0"

# With local service access
docker run -d --rm --init \
  --name playwright-server \
  --ipc=host \
  --add-host=hostmachine:host-gateway \
  -p 3000:3000 \
  --user pwuser \
  --workdir /home/pwuser \
  mcr.microsoft.com/playwright:v1.58.0-noble \
  /bin/sh -c "npx -y playwright@1.58.0 run-server --port 3000 --host 0.0.0.0"
```

### Run Tests Directly in Container

```bash
# Mount project and run tests
docker run --rm --init \
  --ipc=host \
  -v $(pwd):/work \
  -w /work \
  mcr.microsoft.com/playwright:v1.58.0-noble \
  npx playwright test

# With environment variables
docker run --rm --init \
  --ipc=host \
  -e CI=true \
  -v $(pwd):/work \
  -w /work \
  mcr.microsoft.com/playwright:v1.58.0-noble \
  npx playwright test

# Interactive bash session
docker run -it --rm --init \
  --ipc=host \
  -v $(pwd):/work \
  -w /work \
  mcr.microsoft.com/playwright:v1.58.0-noble \
  /bin/bash
```

## Container Management

### Lifecycle Commands

```bash
# Start container
docker start playwright-mcp

# Stop container
docker stop playwright-mcp

# Restart container
docker restart playwright-mcp

# Remove container
docker rm playwright-mcp
docker rm -f playwright-mcp  # Force remove running container

# List running containers
docker ps -f name=playwright

# List all containers (including stopped)
docker ps -a -f name=playwright
```

### Logs and Monitoring

```bash
# View logs
docker logs playwright-mcp

# Follow logs in real-time
docker logs -f playwright-mcp

# Last 100 lines
docker logs --tail 100 playwright-mcp

# With timestamps
docker logs -t playwright-mcp

# Container stats (CPU, memory usage)
docker stats playwright-mcp

# Inspect container
docker inspect playwright-mcp
```

### Execute Commands in Container

```bash
# Run command in running container
docker exec playwright-mcp ps aux

# Interactive shell
docker exec -it playwright-mcp /bin/bash

# Check Playwright version
docker exec playwright-mcp npx playwright --version

# List installed browsers
docker exec playwright-mcp npx playwright install --dry-run
```

## Networking Options

### Port Mapping

```bash
# Map single port
-p 8931:8931

# Map different host port
-p 9000:8931

# Map all exposed ports
-P

# Bind to specific interface
-p 127.0.0.1:8931:8931
```

### Network Modes

```bash
# Bridge mode (default)
docker run --network bridge ...

# Host mode (Linux only - shares host network)
docker run --network host ...

# None (no networking)
docker run --network none ...

# Custom network
docker network create playwright-net
docker run --network playwright-net ...
```

### Access Host Services

```bash
# Using host.docker.internal (Mac/Windows)
# Access host via http://host.docker.internal:3001

# Using extra hosts (Linux)
--add-host=hostmachine:host-gateway
# Access host via http://hostmachine:3001

# Using host networking (Linux only)
--network=host
# Access host via http://localhost:3001
```

## Volume Mounting

```bash
# Mount current directory
-v $(pwd):/work

# Mount specific directory
-v /path/to/project:/work

# Mount as read-only
-v $(pwd):/work:ro

# Mount with specific user permissions
-v $(pwd):/work:rw,z

# Mount temporary directory
-v /tmp:/tmp

# Anonymous volume
-v /app/node_modules
```

## Environment Variables

```bash
# Set single variable
-e DISPLAY=:0

# Set multiple variables
-e VAR1=value1 -e VAR2=value2

# Load from file
--env-file .env

# Common Playwright variables
-e CI=true
-e DEBUG=pw:api
-e PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
```

## Resource Limits

```bash
# Limit memory
--memory=2g
--memory-reservation=1g

# Limit CPU
--cpus=2
--cpu-shares=1024

# Set IPC mode (critical for Chromium!)
--ipc=host

# Set shared memory size
--shm-size=2g
```

## Docker Compose

### Basic Configuration

```yaml
services:
  playwright:
    image: mcr.microsoft.com/playwright-mcp:latest
    container_name: playwright-mcp
    restart: unless-stopped
    ipc: host
    ports:
      - "8931:8931"
    extra_hosts:
      - "hostmachine:host-gateway"
    command: node cli.js --headless --browser chromium --no-sandbox --port 8931
    stdin_open: true
    init: true
```

### Advanced Configuration

```yaml
services:
  playwright:
    image: mcr.microsoft.com/playwright-mcp:latest
    container_name: playwright-mcp
    restart: unless-stopped
    ipc: host
    ports:
      - "8931:8931"
    extra_hosts:
      - "hostmachine:host-gateway"
    environment:
      - DEBUG=pw:api
    volumes:
      - ./screenshots:/screenshots
      - ./videos:/videos
    command: node cli.js --headless --browser chromium --no-sandbox --port 8931
    stdin_open: true
    init: true
    mem_limit: 2g
    cpus: 2
```

### Compose Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart playwright

# Pull latest images
docker-compose pull

# Build and start
docker-compose up -d --build

# Remove all stopped containers
docker-compose down -v
```

## Troubleshooting Commands

### Debugging

```bash
# Check container status
docker ps -a -f name=playwright

# Check port bindings
docker port playwright-mcp

# Test network connectivity from container
docker exec playwright-mcp ping -c 3 google.com
docker exec playwright-mcp curl http://hostmachine:3001

# Check browser processes
docker exec playwright-mcp ps aux | grep -E "(chromium|firefox|webkit)"

# Check available disk space
docker exec playwright-mcp df -h

# Check memory usage
docker stats playwright-mcp --no-stream
```

### Clean Up

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove all playwright images
docker images | grep playwright | awk '{print $3}' | xargs docker rmi

# Remove all (be careful!)
docker system prune -a
```

### Performance Tuning

```bash
# Increase shared memory
--shm-size=2g

# Use host IPC namespace (recommended for Chromium)
--ipc=host

# Allocate more memory
--memory=4g

# Use more CPU cores
--cpus=4

# Disable security features (testing only!)
--security-opt seccomp=unconfined
--cap-add=SYS_ADMIN
```

## Security Considerations

### Running as Non-Root

```bash
# Use pwuser (when available)
--user pwuser

# Create custom user
docker run --rm -it \
  mcr.microsoft.com/playwright:v1.58.0-noble \
  /bin/bash -c "useradd -m testuser && su - testuser"
```

### Sandboxing

```bash
# Disable sandbox (required when running as root)
--no-sandbox

# Use seccomp profile
--security-opt seccomp=/path/to/profile.json

# Drop capabilities
--cap-drop=ALL --cap-add=SYS_ADMIN
```

## Examples

### Complete Production Setup

```bash
docker run -d --rm --init \
  --name playwright-mcp-prod \
  --restart=unless-stopped \
  --ipc=host \
  --add-host=hostmachine:host-gateway \
  -p 8931:8931 \
  --memory=4g \
  --cpus=2 \
  --health-cmd="curl -f http://localhost:8931 || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  -v $(pwd)/screenshots:/screenshots \
  -v $(pwd)/videos:/videos \
  -e DEBUG=pw:api \
  mcr.microsoft.com/playwright-mcp:latest \
  node cli.js --headless --browser chromium --no-sandbox --port 8931
```

### Development Setup with VNC

```bash
docker run -d --rm --init \
  --name playwright-dev \
  --ipc=host \
  -p 3000:3000 \
  -p 5900:5900 \
  -v $(pwd):/work \
  -w /work \
  mcr.microsoft.com/playwright:v1.58.0-noble \
  /bin/sh -c "x11vnc -create -forever -shared -rfbport 5900 & \
              npx playwright@1.58.0 run-server --port 3000 --host 0.0.0.0"
```

## Version Information

Check versions in containers:

```bash
# Playwright version
docker run --rm mcr.microsoft.com/playwright:v1.58.0-noble \
  npx playwright --version

# Node version
docker run --rm mcr.microsoft.com/playwright:v1.58.0-noble \
  node --version

# OS version
docker run --rm mcr.microsoft.com/playwright:v1.58.0-noble \
  cat /etc/os-release

# Installed browsers
docker run --rm mcr.microsoft.com/playwright:v1.58.0-noble \
  npx playwright install --dry-run
```
