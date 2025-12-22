#!/usr/bin/env python3
"""
Syncthing REST API helper script.
Provides convenient functions for common Syncthing operations.
"""

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def get_config():
    """Load Syncthing configuration (API key and URL)."""
    config_paths = [
        Path.home() / ".config/syncthing/config.xml",
        Path.home() / ".local/state/syncthing/config.xml",
        Path.home() / ".local/share/syncthing/config.xml",
    ]

    api_key = None
    gui_address = "http://127.0.0.1:8384"

    # Try to read from config file
    for config_path in config_paths:
        if config_path.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(config_path)
                root = tree.getroot()

                # Get API key
                api_elem = root.find(".//apikey")
                if api_elem is not None and api_elem.text:
                    api_key = api_elem.text

                # Get GUI address
                gui_elem = root.find(".//gui/address")
                if gui_elem is not None and gui_elem.text:
                    addr = gui_elem.text
                    if not addr.startswith("http"):
                        addr = f"http://{addr}"
                    gui_address = addr

                if api_key:
                    break
            except Exception:
                pass

    # Environment variables override config file
    api_key = os.environ.get("SYNCTHING_API_KEY", api_key)
    gui_address = os.environ.get("SYNCTHING_URL", gui_address)

    if not api_key:
        print("Error: Could not find Syncthing API key.", file=sys.stderr)
        print("Set SYNCTHING_API_KEY environment variable or ensure config.xml exists.", file=sys.stderr)
        sys.exit(1)

    return api_key, gui_address


def api_request(endpoint, method="GET", data=None):
    """Make a request to the Syncthing REST API."""
    api_key, base_url = get_config()
    url = f"{base_url}{endpoint}"

    headers = {"X-API-Key": api_key}

    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()

    req = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(req) as response:
            content = response.read()
            if content:
                return json.loads(content)
            return None
    except HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        if e.code == 403:
            print("Authentication failed. Check your API key.", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        print("Is Syncthing running?", file=sys.stderr)
        sys.exit(1)


def get_system_status():
    """Get system status."""
    return api_request("/rest/system/status")


def get_system_version():
    """Get Syncthing version."""
    return api_request("/rest/system/version")


def get_connections():
    """Get device connection status."""
    return api_request("/rest/system/connections")


def get_config_full():
    """Get full configuration."""
    return api_request("/rest/config")


def get_folder_status(folder_id):
    """Get status for a specific folder."""
    return api_request(f"/rest/db/status?folder={folder_id}")


def get_folder_errors(folder_id):
    """Get errors for a specific folder."""
    return api_request(f"/rest/folder/errors?folder={folder_id}")


def scan_folder(folder_id, sub_path=None):
    """Trigger a scan of a folder."""
    endpoint = f"/rest/db/scan?folder={folder_id}"
    if sub_path:
        endpoint += f"&sub={sub_path}"
    return api_request(endpoint, method="POST")


def pause_device(device_id):
    """Pause a device."""
    return api_request(f"/rest/system/pause?device={device_id}", method="POST")


def resume_device(device_id):
    """Resume a device."""
    return api_request(f"/rest/system/resume?device={device_id}", method="POST")


def restart():
    """Restart Syncthing."""
    return api_request("/rest/system/restart", method="POST")


def shutdown():
    """Shutdown Syncthing."""
    return api_request("/rest/system/shutdown", method="POST")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: syncthing_api.py <command> [args]")
        print("\nCommands:")
        print("  status              - Get system status")
        print("  version             - Get Syncthing version")
        print("  connections         - Get device connections")
        print("  config              - Get full configuration")
        print("  folder-status <id>  - Get folder status")
        print("  folder-errors <id>  - Get folder errors")
        print("  scan <id> [path]    - Scan folder")
        print("  pause-device <id>   - Pause device")
        print("  resume-device <id>  - Resume device")
        print("  restart             - Restart Syncthing")
        print("  shutdown            - Shutdown Syncthing")
        sys.exit(1)

    command = sys.argv[1]

    result = None
    if command == "status":
        result = get_system_status()
    elif command == "version":
        result = get_system_version()
    elif command == "connections":
        result = get_connections()
    elif command == "config":
        result = get_config_full()
    elif command == "folder-status":
        if len(sys.argv) < 3:
            print("Error: folder-status requires folder ID", file=sys.stderr)
            sys.exit(1)
        result = get_folder_status(sys.argv[2])
    elif command == "folder-errors":
        if len(sys.argv) < 3:
            print("Error: folder-errors requires folder ID", file=sys.stderr)
            sys.exit(1)
        result = get_folder_errors(sys.argv[2])
    elif command == "scan":
        if len(sys.argv) < 3:
            print("Error: scan requires folder ID", file=sys.stderr)
            sys.exit(1)
        sub_path = sys.argv[3] if len(sys.argv) > 3 else None
        result = scan_folder(sys.argv[2], sub_path)
    elif command == "pause-device":
        if len(sys.argv) < 3:
            print("Error: pause-device requires device ID", file=sys.stderr)
            sys.exit(1)
        result = pause_device(sys.argv[2])
    elif command == "resume-device":
        if len(sys.argv) < 3:
            print("Error: resume-device requires device ID", file=sys.stderr)
            sys.exit(1)
        result = resume_device(sys.argv[2])
    elif command == "restart":
        result = restart()
    elif command == "shutdown":
        result = shutdown()
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)

    if result is not None:
        print(json.dumps(result, indent=2))
