---
name: playwright-docker
description: Run Playwright browser automation in an isolated Docker container to avoid Chrome session conflicts. Use when Playwright MCP tools fail due to browser conflicts, when you need isolated browser instances, or when testing requires a clean browser environment.
---

# Playwright Docker

Run Playwright browser automation inside a Docker container to avoid Chrome session conflicts and provide isolated browser environments.

## Overview

This skill solves the common problem of Chrome session conflicts when using Playwright MCP directly on the host machine. By running Playwright in Docker, you get:

- Isolated browser instances that don't conflict with host Chrome
- Clean, reproducible browser environment
- No need to manage browser installations locally
- Support for headless and headed modes

## Quick Start

### Option 1: Playwright MCP Server (Recommended)

Run Playwright MCP server as a long-lived Docker container:

```bash
docker run -d -i --rm --init \
  --name playwright-mcp \
  --ipc=host \
  -p 8931:8931 \
  mcr.microsoft.com/playwright-mcp:latest \
  node cli.js --headless --browser chromium --no-sandbox --port 8931
```

This starts an MCP server on port 8931 that you can connect to from your host machine.

**Important flags:**
- `--ipc=host` - Recommended for Chromium to prevent memory issues
- `--no-sandbox` - Required when running as root in Docker
- `--headless` - Run without visible browser (change to `--headed` to see the browser)

### Option 2: Playwright Server Mode

Run Playwright server for connecting from host tests:

```bash
docker run -d --rm --init \
  --name playwright-server \
  --ipc=host \
  -p 3000:3000 \
  --user pwuser \
  --workdir /home/pwuser \
  mcr.microsoft.com/playwright:v1.58.0-noble \
  /bin/sh -c "npx -y playwright@1.58.0 run-server --port 3000 --host 0.0.0.0"
```

Connect from host with:

```javascript
const { chromium } = require('playwright');
const browser = await chromium.connect('ws://localhost:3000');
```

### Option 3: VNC Access (For Debugging)

Run with VNC to visually see the browser:

```bash
docker run -d --rm --init \
  --name playwright-vnc \
  --ipc=host \
  -p 3000:3000 \
  -p 5900:5900 \
  mcr.microsoft.com/playwright:v1.58.0-noble \
  /bin/sh -c "x11vnc -display :99 -forever -shared & npx -y playwright@1.58.0 run-server --port 3000 --host 0.0.0.0"
```

Connect with VNC client to `localhost:5900` to watch browser automation in real-time.

## Common Tasks

### Start the Container

```bash
# Start MCP server
./scripts/start_playwright_mcp.sh

# Or manually
docker run -d -i --rm --init \
  --name playwright-mcp \
  --ipc=host \
  -p 8931:8931 \
  mcr.microsoft.com/playwright-mcp:latest \
  node cli.js --headless --browser chromium --no-sandbox --port 8931
```

### Check Container Status

```bash
docker ps -f name=playwright

# Check logs
docker logs playwright-mcp

# Follow logs
docker logs -f playwright-mcp
```

### Stop the Container

```bash
docker stop playwright-mcp
```

### Access Local Services from Container

If you need to test a local development server (e.g., `http://localhost:3001`), use host networking or map the host:

```bash
docker run -d -i --rm --init \
  --name playwright-mcp \
  --ipc=host \
  --add-host=hostmachine:host-gateway \
  -p 8931:8931 \
  mcr.microsoft.com/playwright-mcp:latest \
  node cli.js --headless --browser chromium --no-sandbox --port 8931
```

Then in your tests, use `http://hostmachine:3001` instead of `http://localhost:3001`.

### Run with Headed Browser

For debugging, run with visible browser:

```bash
docker run -d -i --rm --init \
  --name playwright-mcp \
  --ipc=host \
  -p 8931:8931 \
  -e DISPLAY=:0 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  mcr.microsoft.com/playwright-mcp:latest \
  node cli.js --headed --browser chromium --no-sandbox --port 8931
```

Note: Requires X11 forwarding to be set up on your host.

## Using with Playwright MCP Tools

Once the container is running, you can use the standard Playwright MCP tools from Claude Code. The tools will connect to the containerized browser automatically if configured correctly.

Example workflow:

1. Start the container:
   ```bash
   ./scripts/start_playwright_mcp.sh
   ```

2. Use Playwright MCP tools as normal:
   - `mcp__playwright__browser_navigate` - Navigate to URL
   - `mcp__playwright__browser_snapshot` - Take page snapshot
   - `mcp__playwright__browser_click` - Click elements
   - `mcp__playwright__browser_type` - Type text
   - etc.

3. Stop when done:
   ```bash
   docker stop playwright-mcp
   ```

## Docker Compose Setup

For easier management, use docker-compose:

```yaml
# docker-compose.yml
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
```

Then use:

```bash
docker-compose up -d      # Start
docker-compose logs -f    # View logs
docker-compose down       # Stop
```

## Troubleshooting

**Container won't start:**
- Check if port 8931 is already in use: `lsof -i :8931`
- Try a different port: `-p 9000:9000` and update the command
- Check Docker logs: `docker logs playwright-mcp`

**Can't access local servers:**
- Use `--add-host=hostmachine:host-gateway`
- Access via `http://hostmachine:PORT` instead of `localhost:PORT`
- Or use host networking: `--network=host` (Linux only)

**Browser crashes or out of memory:**
- Add `--ipc=host` flag (critical for Chromium)
- Increase Docker memory limit in Docker Desktop settings
- Check logs for specific error messages

**MCP connection fails:**
- Verify container is running: `docker ps`
- Check port is exposed: `docker port playwright-mcp`
- Test connection: `curl http://localhost:8931`
- Review MCP server configuration in Claude Code

**Slow performance:**
- Use `--headless` mode instead of `--headed`
- Ensure `--ipc=host` is set for Chromium
- Check Docker resource allocation

## Version Compatibility

Always match your Playwright version with the Docker image version. Mismatched versions will cause browser executable errors.

Check current version:
```bash
docker run --rm mcr.microsoft.com/playwright:v1.58.0-noble npx playwright --version
```

Available tags:
- `:latest` - Latest stable release
- `:v1.58.0-noble` - Ubuntu 24.04 based
- `:v1.58.0-jammy` - Ubuntu 22.04 based
- `:v1.58.0` - Default Ubuntu version

## Security Considerations

The container runs browsers as root by default, which disables the Chromium sandbox. This is acceptable for testing but not recommended for untrusted content.

For production use:
- Create a dedicated user inside the container
- Use seccomp profiles for additional security
- Avoid exposing the container port to public networks
- Use `--user pwuser` flag when possible

## Reference

See [references/docker_commands.md](references/docker_commands.md) for complete command reference and advanced usage patterns.

## Resources

- [Playwright Docker Documentation](https://playwright.dev/docs/docker)
- [Microsoft Playwright Container Registry](https://mcr.microsoft.com/en-us/product/playwright/about)
- [Playwright MCP GitHub](https://github.com/microsoft/playwright-mcp)
- Helper script: `scripts/start_playwright_mcp.sh`
