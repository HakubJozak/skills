# Syncthing API and CLI Reference

## Authentication

All REST API requests require authentication via `X-API-Key` header. The API key is found in Syncthing's config.xml file.

```bash
# Set environment variable
export SYNCTHING_API_KEY="your-api-key-here"
export SYNCTHING_URL="http://127.0.0.1:8384"  # optional, defaults to this
```

## Common REST API Endpoints

Base URL: `http://127.0.0.1:8384` (default)

### System Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rest/system/status` | GET | Current system state and statistics |
| `/rest/system/version` | GET | Software version information |
| `/rest/system/connections` | GET | Device connection status |
| `/rest/system/config` | GET | Full system configuration |
| `/rest/system/pause` | POST | Pause all devices (add `?device=ID` for specific device) |
| `/rest/system/resume` | POST | Resume all devices (add `?device=ID` for specific device) |
| `/rest/system/restart` | POST | Restart Syncthing |
| `/rest/system/shutdown` | POST | Shutdown Syncthing |

### Folder Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rest/db/status?folder=ID` | GET | Folder sync status and progress |
| `/rest/db/browse?folder=ID&prefix=PATH` | GET | Browse folder contents |
| `/rest/db/scan?folder=ID` | POST | Trigger folder rescan (add `&sub=PATH` for subdirectory) |
| `/rest/folder/errors?folder=ID` | GET | List sync errors for folder |
| `/rest/db/need?folder=ID` | GET | Files needing sync |
| `/rest/db/override?folder=ID` | POST | Force local version as authoritative |

### Cluster & Devices

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rest/cluster/pending/devices` | GET | View unaccepted device requests |
| `/rest/cluster/pending/folders` | GET | View folder sharing invitations |
| `/rest/stats/device` | GET | Device performance metrics |

### Configuration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rest/config` | GET | Get full configuration |
| `/rest/config` | PUT | Update configuration (requires full config object) |
| `/rest/system/paths` | GET | Application directory paths |

## CLI Commands

Syncthing provides a `cli` subcommand for easier REST API access:

```bash
# Show system status
syncthing cli show system

# Show device status
syncthing cli show devices

# Show folder status
syncthing cli show folders

# Get configuration
syncthing cli config dump

# Operations
syncthing cli operations restart
syncthing cli operations shutdown

# Errors
syncthing cli errors show
syncthing cli errors push  # Clear error
```

## Example API Requests

### Using curl

```bash
# Get system status
curl -X GET -H "X-API-Key: $SYNCTHING_API_KEY" \
  http://127.0.0.1:8384/rest/system/status

# Get folder status
curl -X GET -H "X-API-Key: $SYNCTHING_API_KEY" \
  "http://127.0.0.1:8384/rest/db/status?folder=default"

# Trigger folder scan
curl -X POST -H "X-API-Key: $SYNCTHING_API_KEY" \
  "http://127.0.0.1:8384/rest/db/scan?folder=default"

# Pause a device
curl -X POST -H "X-API-Key: $SYNCTHING_API_KEY" \
  "http://127.0.0.1:8384/rest/system/pause?device=DEVICE-ID"
```

### Using the helper script

```bash
# Get system status
scripts/syncthing_api.py status

# Get connections
scripts/syncthing_api.py connections

# Get folder status
scripts/syncthing_api.py folder-status default

# Scan folder
scripts/syncthing_api.py scan default

# Pause device
scripts/syncthing_api.py pause-device DEVICE-ID
```

## Response Examples

### System Status

```json
{
  "alloc": 123456789,
  "connectionServiceStatus": {
    "tcp://0.0.0.0:22000": {"error": null, "lanAddresses": [...], ...}
  },
  "cpuPercent": 0.5,
  "discoveryEnabled": true,
  "goroutines": 100,
  "myID": "DEVICE-ID-HERE",
  "pathSeparator": "/",
  "startTime": "2025-12-17T10:00:00Z",
  "sys": 987654321,
  "uptime": 3600
}
```

### Folder Status

```json
{
  "globalBytes": 1000000,
  "globalDeleted": 0,
  "globalDirectories": 10,
  "globalFiles": 50,
  "inSyncBytes": 950000,
  "inSyncFiles": 48,
  "needBytes": 50000,
  "needDeletes": 0,
  "needDirectories": 0,
  "needFiles": 2,
  "state": "syncing",
  "stateChanged": "2025-12-17T10:30:00Z",
  "version": 123
}
```

States: `idle`, `syncing`, `scanning`, `error`

### Connections

```json
{
  "connections": {
    "DEVICE-ID-1": {
      "address": "192.168.1.100:22000",
      "at": "2025-12-17T10:00:00Z",
      "connected": true,
      "inBytesTotal": 1000000,
      "outBytesTotal": 500000,
      "paused": false,
      "type": "tcp-client"
    }
  },
  "total": {
    "inBytesTotal": 1000000,
    "outBytesTotal": 500000
  }
}
```
