# Uptime Kuma API Reference

## Monitor Types

The following monitor types are available in `uptime_kuma_api.MonitorType`:

- `HTTP` / `HTTPS` - HTTP/HTTPS endpoint monitoring
- `TCP` - TCP port checks
- `PING` - ICMP ping
- `DOCKER` - Docker container status
- `DNS` - DNS resolution checks
- `PUSH` - Push-based monitoring (service pushes status)
- `STEAM` - Steam game server
- `MQTT` - MQTT broker
- `SQLSERVER` - SQL Server database
- `POSTGRES` - PostgreSQL database
- `MYSQL` - MySQL/MariaDB database
- `MONGODB` - MongoDB database
- `REDIS` - Redis database
- `RADIUS` - RADIUS server
- `GRPC_KEYWORD` - gRPC with keyword check

## Monitor Parameters

### Common Parameters

Used by most monitor types:

- `type` (MonitorType) - Monitor type (required)
- `name` (str) - Display name (required)
- `url` (str) - URL to monitor (required for HTTP/HTTPS)
- `interval` (int) - Check interval in seconds (default: 60)
- `maxretries` (int) - Max retries before marking as down (default: 0)
- `retryInterval` (int) - Interval between retries in seconds (default: 60)
- `description` (str) - Monitor description
- `active` (bool) - Whether monitor is active (default: True)

### HTTP/HTTPS Specific

- `method` (str) - HTTP method: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS (default: GET)
- `body` (str) - Request body for POST/PUT
- `headers` (str) - Custom headers as JSON string
- `authMethod` (str) - Authentication: "", "basic", "ntlm", "mtls"
- `basicAuthUser` (str) - Basic auth username
- `basicAuthPass` (str) - Basic auth password
- `tlsCert` (str) - TLS client certificate
- `tlsKey` (str) - TLS client key
- `tlsCa` (str) - TLS CA certificate
- `ignoreTls` (bool) - Ignore TLS/SSL errors
- `maxredirects` (int) - Maximum redirects to follow (default: 10)
- `accepted_statuscodes` (list) - Acceptable HTTP status codes (default: ["200-299"])
- `keyword` (str) - Keyword to search for in response
- `invertKeyword` (bool) - Alert if keyword is found (instead of not found)
- `expiryNotification` (bool) - Enable certificate expiry notifications

### TCP Port Monitoring

- `hostname` (str) - Hostname or IP address
- `port` (int) - Port number
- `dns_resolve_server` (str) - DNS server to use for resolution

### Ping Monitoring

- `hostname` (str) - Hostname or IP address to ping
- `packetSize` (int) - Packet size in bytes

### DNS Monitoring

- `hostname` (str) - Domain to resolve
- `dns_resolve_server` (str) - DNS server to query
- `dns_resolve_type` (str) - DNS record type: A, AAAA, CNAME, MX, TXT, etc.
- `port` (int) - DNS server port (default: 53)

### Docker Monitoring

- `docker_container` (str) - Container name or ID
- `docker_host` (int) - Docker host ID (configured in Uptime Kuma)

### Database Monitoring (PostgreSQL, MySQL, etc.)

- `hostname` (str) - Database host
- `port` (int) - Database port
- `databaseConnectionString` (str) - Full connection string
- `databaseQuery` (str) - SQL query to execute

### Push Monitoring

- `pushToken` (str) - Push token (auto-generated if not provided)

## API Methods

### Monitor Management

```python
# Add monitor
api.add_monitor(type=MonitorType.HTTP, name="...", url="...", **kwargs)

# Get all monitors
api.get_monitors()

# Get single monitor
api.get_monitor(monitor_id)

# Edit monitor
api.edit_monitor(monitor_id, **kwargs)

# Delete monitor
api.delete_monitor(monitor_id)

# Pause monitor
api.pause_monitor(monitor_id)

# Resume monitor
api.resume_monitor(monitor_id)
```

### Notification Management

```python
# Add notification
api.add_notification(name="...", type="...", **kwargs)

# Get notifications
api.get_notifications()

# Delete notification
api.delete_notification(notification_id)
```

### Notification Types

- `smtp` - Email via SMTP
- `discord` - Discord webhook
- `telegram` - Telegram bot
- `slack` - Slack webhook
- `webhook` - Generic webhook
- `gotify` - Gotify
- `pushover` - Pushover
- `pushbullet` - Pushbullet
- `line` - LINE messenger
- `mattermost` - Mattermost
- `ntfy` - ntfy
- `signal` - Signal messenger

### Status Page Management

```python
# Get status pages
api.get_status_pages()

# Add status page
api.add_status_page(title="...", slug="...", **kwargs)

# Delete status page
api.delete_status_page(slug)
```

### Maintenance Windows

```python
# Get maintenance windows
api.get_maintenances()

# Add maintenance
api.add_maintenance(title="...", strategy="...", **kwargs)

# Pause maintenance
api.pause_maintenance(maintenance_id)

# Resume maintenance
api.resume_maintenance(maintenance_id)
```

### Tags

```python
# Get tags
api.get_tags()

# Add tag
api.add_tag(name="...", color="...")

# Delete tag
api.delete_tag(tag_id)
```

## Response Format

### Monitor Object

```json
{
  "id": 1,
  "name": "My Service",
  "url": "https://example.com",
  "type": "http",
  "interval": 60,
  "maxretries": 0,
  "retryInterval": 60,
  "active": true,
  "description": "Main service",
  "method": "GET",
  "ignoreTls": false,
  "accepted_statuscodes": ["200-299"]
}
```

### Add Monitor Response

```json
{
  "msg": "Added Successfully.",
  "monitorID": 1
}
```

## Common Patterns

### Bulk Import

```python
services = [
    {"name": "Service 1", "url": "https://example1.com"},
    {"name": "Service 2", "url": "https://example2.com"},
]

for service in services:
    api.add_monitor(
        type=MonitorType.HTTP,
        name=service["name"],
        url=service["url"]
    )
```

### Find Monitor by Name

```python
monitors = api.get_monitors()
for monitor in monitors:
    if monitor['name'] == "My Service":
        print(f"Found monitor ID: {monitor['id']}")
        break
```

### Update All Monitors

```python
monitors = api.get_monitors()
for monitor in monitors:
    api.edit_monitor(monitor['id'], interval=120)  # Change to 2 minutes
```

## Error Handling

```python
from uptime_kuma_api import UptimeKumaException

try:
    with UptimeKumaApi(url) as api:
        api.login(username, password)
        api.add_monitor(...)
except UptimeKumaException as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Authentication

Uptime Kuma uses username/password authentication. You must first complete the initial setup via the web UI to create an admin account.

```python
# Option 1: Context manager (recommended)
with UptimeKumaApi(url) as api:
    api.login(username, password)
    # Do work...
# Auto-disconnect

# Option 2: Manual connection
api = UptimeKumaApi(url)
api.login(username, password)
# Do work...
api.disconnect()
```

## External Links

- [Official Documentation](https://uptime-kuma-api.readthedocs.io/)
- [GitHub Repository](https://github.com/lucasheld/uptime-kuma-api)
- [PyPI Package](https://pypi.org/project/uptime-kuma-api/)
