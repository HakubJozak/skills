---
name: syncthing-control
description: Control and monitor Syncthing file synchronization locally via REST API and CLI. Use when working with Syncthing to check sync status, view folder/device information, troubleshoot sync errors, pause/resume syncing, trigger folder scans, or perform any Syncthing management tasks.
---

# Syncthing Control

Control and monitor your local Syncthing instance using the REST API or CLI commands.

## Quick Start

### Using the Helper Script

The `scripts/syncthing_api.py` script provides convenient access to common operations:

```bash
# Check system status
scripts/syncthing_api.py status

# View device connections
scripts/syncthing_api.py connections

# Get folder status
scripts/syncthing_api.py folder-status <folder-id>

# Scan a folder
scripts/syncthing_api.py scan <folder-id>
```

The script automatically discovers your API key from `~/.config/syncthing/config.xml`, `~/.local/state/syncthing/config.xml`, or `~/.local/share/syncthing/config.xml`. Override with environment variables:

```bash
export SYNCTHING_API_KEY="your-key"
export SYNCTHING_URL="http://127.0.0.1:8384"
```

### Using Syncthing CLI

```bash
# Show system status
syncthing cli show system

# Show all folders
syncthing cli show folders

# Show all devices
syncthing cli show devices

# View errors
syncthing cli errors show
```

### Using curl directly

```bash
curl -H "X-API-Key: $SYNCTHING_API_KEY" \
  http://127.0.0.1:8384/rest/system/status
```

## Common Tasks

### Check Sync Status

Get overview of all folders and their sync state:

```python
import json
from scripts.syncthing_api import get_config_full, get_folder_status

# Get all configured folders
config = get_config_full()
folders = config.get("folders", [])

for folder in folders:
    folder_id = folder["id"]
    status = get_folder_status(folder_id)
    print(f"{folder_id}: {status['state']} - {status['inSyncFiles']}/{status['globalFiles']} files synced")
```

Or via CLI:

```bash
syncthing cli show folders
```

### View Device Connections

```python
from scripts.syncthing_api import get_connections

connections = get_connections()
for device_id, conn in connections["connections"].items():
    if conn["connected"]:
        print(f"{device_id[:7]}...: connected via {conn['address']}")
    else:
        print(f"{device_id[:7]}...: disconnected")
```

### Troubleshoot Sync Errors

Check for errors in a specific folder:

```python
from scripts.syncthing_api import get_folder_errors

errors = get_folder_errors("default")
if errors.get("errors"):
    for error in errors["errors"]:
        print(f"Error in {error['path']}: {error['error']}")
```

Trigger a rescan if files aren't syncing:

```bash
scripts/syncthing_api.py scan <folder-id>
```

### Pause/Resume Syncing

Pause a specific device:

```python
from scripts.syncthing_api import pause_device, resume_device

pause_device("DEVICE-ID-HERE")
# Later...
resume_device("DEVICE-ID-HERE")
```

Or use the API directly:

```bash
curl -X POST -H "X-API-Key: $SYNCTHING_API_KEY" \
  "http://127.0.0.1:8384/rest/system/pause?device=DEVICE-ID"
```

### Get Folder IDs and Device IDs

List configured folders and devices:

```python
from scripts.syncthing_api import get_config_full

config = get_config_full()

# Folders
for folder in config["folders"]:
    print(f"Folder: {folder['label']} (ID: {folder['id']})")

# Devices
for device in config["devices"]:
    print(f"Device: {device.get('name', 'Unnamed')} (ID: {device['deviceID']})")
```

Or get your own device ID:

```bash
syncthing cli show system | grep "Device ID"
```

### Monitor Sync Progress

For a specific folder, track sync progress:

```python
from scripts.syncthing_api import get_folder_status

status = get_folder_status("default")
need_bytes = status["needBytes"]
global_bytes = status["globalBytes"]

if need_bytes > 0:
    progress = ((global_bytes - need_bytes) / global_bytes) * 100
    print(f"Sync progress: {progress:.1f}%")
    print(f"Need to sync: {need_bytes / 1024 / 1024:.1f} MB")
else:
    print(f"Folder state: {status['state']}")
```

States: `idle` (fully synced), `syncing` (actively syncing), `scanning` (scanning for changes), `error` (sync errors)

### Browse Folder Contents

List files in a synced folder via API:

```bash
curl -H "X-API-Key: $SYNCTHING_API_KEY" \
  "http://127.0.0.1:8384/rest/db/browse?folder=default&prefix=subdir"
```

## Reference Documentation

For complete API endpoint documentation, response formats, and additional examples, see [references/api_reference.md](references/api_reference.md).

## Resources

### scripts/syncthing_api.py

Python helper script providing functions for all common Syncthing operations. Can be imported as a module or run standalone:

```bash
scripts/syncthing_api.py <command> [args]
```

Available commands: `status`, `version`, `connections`, `config`, `folder-status`, `folder-errors`, `scan`, `pause-device`, `resume-device`, `restart`, `shutdown`

### references/api_reference.md

Comprehensive REST API documentation including:
- Authentication setup
- All available endpoints with descriptions
- CLI command reference
- Example requests and responses
- Response format documentation
