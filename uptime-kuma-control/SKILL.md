---
name: uptime-kuma-control
description: Manage and configure Uptime Kuma monitoring service via Python API. Use to add/edit/delete monitors, manage notifications, check service status, and automate monitoring setup for services in your homelab.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Uptime Kuma Control

Manage Uptime Kuma monitoring service programmatically using the uptime-kuma-api Python library.

## When to Use This Skill

- Add monitors for new services (HTTP, TCP, ping, Docker containers)
- Check status of existing monitors
- Manage notifications and alerts
- Automate monitoring setup
- List and manage monitor configurations

## Prerequisites

```bash
# Install the Python API wrapper
pip install uptime-kuma-api

# Or with pip3
pip3 install uptime-kuma-api
```

## Quick Start

### Using the Helper Script

The `scripts/kuma_manager.py` script provides convenient access to monitor management:

```bash
# Add a monitor
scripts/kuma_manager.py add-monitor \
  --name "My Service" \
  --type http \
  --url "https://example.com" \
  --interval 60

# List all monitors
scripts/kuma_manager.py list-monitors

# Get monitor details
scripts/kuma_manager.py get-monitor --id 1

# Delete a monitor
scripts/kuma_manager.py delete-monitor --id 1

# Pause/Resume a monitor
scripts/kuma_manager.py pause-monitor --id 1
scripts/kuma_manager.py resume-monitor --id 1
```

The script uses these environment variables:
```bash
export UPTIME_KUMA_URL="http://maple.tailbe6a3.ts.net:3001"
export UPTIME_KUMA_USERNAME="admin"
export UPTIME_KUMA_PASSWORD="your-password"
```

### Using Python API Directly

```python
from uptime_kuma_api import UptimeKumaApi, MonitorType

# Connect and authenticate
with UptimeKumaApi('http://maple.tailbe6a3.ts.net:3001') as api:
    api.login('username', 'password')

    # Add HTTP monitor
    result = api.add_monitor(
        type=MonitorType.HTTP,
        name="Immich",
        url="http://maple.tailbe6a3.ts.net:2283",
        interval=60  # seconds
    )
    print(f"Monitor added with ID: {result['monitorID']}")

    # List all monitors
    monitors = api.get_monitors()
    for monitor in monitors:
        print(f"{monitor['name']}: {monitor['url']}")
```

## Common Tasks

### Add HTTP/HTTPS Monitors

```python
from uptime_kuma_api import UptimeKumaApi, MonitorType

with UptimeKumaApi(KUMA_URL) as api:
    api.login(USERNAME, PASSWORD)

    # Basic HTTP monitor
    api.add_monitor(
        type=MonitorType.HTTP,
        name="My Website",
        url="https://example.com",
        interval=60,  # Check every 60 seconds
        maxretries=3,
        retryInterval=60
    )

    # With authentication
    api.add_monitor(
        type=MonitorType.HTTP,
        name="Protected API",
        url="https://api.example.com/health",
        authMethod="basic",  # or "ntlm", "mtls"
        basicAuthUser="user",
        basicAuthPass="pass"
    )

    # With custom headers
    api.add_monitor(
        type=MonitorType.HTTP,
        name="API with Headers",
        url="https://api.example.com",
        headers={"Authorization": "Bearer token123"}
    )
```

### Monitor Types Available

- `MonitorType.HTTP` / `MonitorType.HTTPS` - HTTP/HTTPS endpoints
- `MonitorType.TCP` - TCP port checks
- `MonitorType.PING` - ICMP ping
- `MonitorType.DOCKER` - Docker container status
- `MonitorType.DNS` - DNS resolution checks
- `MonitorType.PUSH` - Push-based monitoring
- `MonitorType.STEAM` - Steam game server
- `MonitorType.MQTT` - MQTT broker
- `MonitorType.SQLSERVER` - SQL Server database
- `MonitorType.POSTGRES` - PostgreSQL database
- `MonitorType.MYSQL` - MySQL/MariaDB database
- `MonitorType.MONGODB` - MongoDB database
- `MonitorType.REDIS` - Redis database

### List and Search Monitors

```python
with UptimeKumaApi(KUMA_URL) as api:
    api.login(USERNAME, PASSWORD)

    # Get all monitors
    monitors = api.get_monitors()

    # Search by name
    for monitor in monitors:
        if "Immich" in monitor['name']:
            print(f"ID: {monitor['id']}")
            print(f"Name: {monitor['name']}")
            print(f"URL: {monitor['url']}")
            print(f"Active: {monitor['active']}")
```

### Update/Edit Monitors

```python
with UptimeKumaApi(KUMA_URL) as api:
    api.login(USERNAME, PASSWORD)

    # Get existing monitor
    monitor = api.get_monitor(1)

    # Update interval
    api.edit_monitor(
        1,
        interval=120  # Change to 2 minutes
    )

    # Update URL
    api.edit_monitor(
        1,
        url="https://new-url.example.com"
    )
```

### Pause/Resume Monitors

```python
with UptimeKumaApi(KUMA_URL) as api:
    api.login(USERNAME, PASSWORD)

    # Pause a monitor (stop checking)
    api.pause_monitor(1)

    # Resume monitoring
    api.resume_monitor(1)
```

### Delete Monitors

```python
with UptimeKumaApi(KUMA_URL) as api:
    api.login(USERNAME, PASSWORD)

    # Delete by ID
    api.delete_monitor(1)

    # Delete by name (find first)
    monitors = api.get_monitors()
    for monitor in monitors:
        if monitor['name'] == "Old Service":
            api.delete_monitor(monitor['id'])
            break
```

### Manage Notifications

```python
with UptimeKumaApi(KUMA_URL) as api:
    api.login(USERNAME, PASSWORD)

    # Add email notification
    notification = api.add_notification(
        name="Email Alert",
        type="smtp",
        smtpHost="smtp.gmail.com",
        smtpPort=587,
        smtpSecure=True,
        smtpUsername="user@gmail.com",
        smtpPassword="password",
        smtpFrom="alert@example.com",
        smtpTo="admin@example.com"
    )

    # Add notification to monitor
    api.edit_monitor(
        1,
        notificationIDList=[notification['id']]
    )
```

## Monitor Configuration Options

Common options for `add_monitor()` and `edit_monitor()`:

- `type`: Monitor type (see MonitorType enum)
- `name`: Display name
- `url`: URL to monitor (HTTP/HTTPS)
- `interval`: Check interval in seconds (default: 60)
- `maxretries`: Max retries before marking as down (default: 0)
- `retryInterval`: Interval between retries in seconds
- `upsideDown`: Invert status (true = expect failure)
- `keyword`: Keyword to search for in response
- `ignoreTls`: Ignore TLS/SSL errors
- `maxredirects`: Maximum redirects to follow
- `accepted_statuscodes`: List of acceptable HTTP status codes
- `proxyId`: Proxy server to use
- `method`: HTTP method (GET, POST, etc.)
- `body`: Request body (for POST/PUT)
- `headers`: Custom HTTP headers (JSON string)
- `authMethod`: Authentication method (basic, ntlm, mtls)
- `basicAuthUser`: Basic auth username
- `basicAuthPass`: Basic auth password

## Advanced Usage

### Bulk Import Monitors

```python
import json

services = [
    {"name": "Immich", "url": "http://maple.tailbe6a3.ts.net:2283"},
    {"name": "Mailcatcher", "url": "http://100.109.100.104:1080"},
    {"name": "Uptime Kuma", "url": "http://100.109.100.104:3001"}
]

with UptimeKumaApi(KUMA_URL) as api:
    api.login(USERNAME, PASSWORD)

    for service in services:
        print(f"Adding monitor for {service['name']}...")
        result = api.add_monitor(
            type=MonitorType.HTTP,
            name=service['name'],
            url=service['url'],
            interval=60
        )
        print(f"  -> Created with ID: {result['monitorID']}")
```

### Export/Backup Configuration

```python
import json

with UptimeKumaApi(KUMA_URL) as api:
    api.login(USERNAME, PASSWORD)

    # Export all monitors
    monitors = api.get_monitors()

    # Save to file
    with open('monitors_backup.json', 'w') as f:
        json.dump(monitors, f, indent=2)
```

### Health Check Script

```python
with UptimeKumaApi(KUMA_URL) as api:
    api.login(USERNAME, PASSWORD)

    monitors = api.get_monitors()
    down_count = 0

    for monitor in monitors:
        if not monitor.get('active'):
            print(f"⚠️  {monitor['name']} is DOWN")
            down_count += 1

    if down_count == 0:
        print("✅ All monitors are UP")
    else:
        print(f"❌ {down_count} monitors are DOWN")
```

## Resources

### scripts/kuma_manager.py

Python CLI script for managing Uptime Kuma monitors. Provides commands for add, list, get, edit, delete, pause, and resume operations.

### references/api_reference.md

Complete API documentation including:
- All MonitorType options
- Full parameter reference
- Notification types and configuration
- API endpoint details
- Example code snippets

## Troubleshooting

### Connection Issues

```python
# Test connection
try:
    api = UptimeKumaApi('http://maple.tailbe6a3.ts.net:3001')
    api.login('username', 'password')
    print("✅ Connected successfully")
    api.disconnect()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Authentication Errors

- Ensure you've completed initial Uptime Kuma setup via web UI
- Create admin account first before using API
- Check username/password are correct
- Verify UPTIME_KUMA_URL is accessible

## External Resources

- [uptime-kuma-api Documentation](https://uptime-kuma-api.readthedocs.io/)
- [GitHub Repository](https://github.com/lucasheld/uptime-kuma-api)
- [Uptime Kuma Official Docs](https://github.com/louislam/uptime-kuma/wiki)
