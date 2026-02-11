#!/usr/bin/env python3
"""
Uptime Kuma Manager - CLI tool for managing Uptime Kuma monitors

Usage:
    ./kuma_manager.py add-monitor --name "Service" --type http --url "https://example.com"
    ./kuma_manager.py list-monitors
    ./kuma_manager.py get-monitor --id 1
    ./kuma_manager.py delete-monitor --id 1
    ./kuma_manager.py pause-monitor --id 1
    ./kuma_manager.py resume-monitor --id 1

Environment Variables:
    UPTIME_KUMA_URL      - Uptime Kuma URL (default: http://localhost:3001)
    UPTIME_KUMA_USERNAME - Username for authentication
    UPTIME_KUMA_PASSWORD - Password for authentication
"""

import os
import sys
import argparse
import json
from typing import Optional

try:
    from uptime_kuma_api import UptimeKumaApi, MonitorType
except ImportError:
    print("ERROR: uptime-kuma-api is not installed", file=sys.stderr)
    print("Install with: pip install uptime-kuma-api", file=sys.stderr)
    sys.exit(1)


class KumaManager:
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password

    def add_monitor(self, name: str, monitor_type: str, url: str,
                   interval: int = 60, **kwargs) -> dict:
        """Add a new monitor"""
        # Convert string type to MonitorType enum
        type_map = {
            'http': MonitorType.HTTP,
            'https': MonitorType.HTTPS,
            'tcp': MonitorType.TCP,
            'ping': MonitorType.PING,
            'docker': MonitorType.DOCKER,
            'dns': MonitorType.DNS,
            'push': MonitorType.PUSH,
            'postgres': MonitorType.POSTGRES,
            'mysql': MonitorType.MYSQL,
            'redis': MonitorType.REDIS,
        }

        if monitor_type.lower() not in type_map:
            raise ValueError(f"Unknown monitor type: {monitor_type}")

        with UptimeKumaApi(self.url) as api:
            api.login(self.username, self.password)

            result = api.add_monitor(
                type=type_map[monitor_type.lower()],
                name=name,
                url=url,
                interval=interval,
                **kwargs
            )

            return result

    def list_monitors(self) -> list:
        """List all monitors"""
        with UptimeKumaApi(self.url) as api:
            api.login(self.username, self.password)
            return api.get_monitors()

    def get_monitor(self, monitor_id: int) -> dict:
        """Get monitor details by ID"""
        with UptimeKumaApi(self.url) as api:
            api.login(self.username, self.password)
            return api.get_monitor(monitor_id)

    def edit_monitor(self, monitor_id: int, **kwargs) -> dict:
        """Edit an existing monitor"""
        with UptimeKumaApi(self.url) as api:
            api.login(self.username, self.password)
            return api.edit_monitor(monitor_id, **kwargs)

    def delete_monitor(self, monitor_id: int) -> dict:
        """Delete a monitor"""
        with UptimeKumaApi(self.url) as api:
            api.login(self.username, self.password)
            return api.delete_monitor(monitor_id)

    def pause_monitor(self, monitor_id: int) -> dict:
        """Pause a monitor"""
        with UptimeKumaApi(self.url) as api:
            api.login(self.username, self.password)
            return api.pause_monitor(monitor_id)

    def resume_monitor(self, monitor_id: int) -> dict:
        """Resume a monitor"""
        with UptimeKumaApi(self.url) as api:
            api.login(self.username, self.password)
            return api.resume_monitor(monitor_id)


def main():
    parser = argparse.ArgumentParser(
        description='Uptime Kuma Manager - Manage monitors via CLI'
    )

    # Global options
    parser.add_argument(
        '--url',
        default=os.environ.get('UPTIME_KUMA_URL', 'http://localhost:3001'),
        help='Uptime Kuma URL (default: from UPTIME_KUMA_URL env or http://localhost:3001)'
    )
    parser.add_argument(
        '--username',
        default=os.environ.get('UPTIME_KUMA_USERNAME'),
        help='Username (default: from UPTIME_KUMA_USERNAME env)'
    )
    parser.add_argument(
        '--password',
        default=os.environ.get('UPTIME_KUMA_PASSWORD'),
        help='Password (default: from UPTIME_KUMA_PASSWORD env)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # add-monitor command
    add_parser = subparsers.add_parser('add-monitor', help='Add a new monitor')
    add_parser.add_argument('--name', required=True, help='Monitor name')
    add_parser.add_argument('--type', required=True, choices=['http', 'https', 'tcp', 'ping', 'docker', 'dns', 'push', 'postgres', 'mysql', 'redis'], help='Monitor type')
    add_parser.add_argument('--url', required=True, help='URL to monitor')
    add_parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds (default: 60)')
    add_parser.add_argument('--max-retries', type=int, default=0, help='Max retries before marking as down')
    add_parser.add_argument('--retry-interval', type=int, default=60, help='Retry interval in seconds')

    # list-monitors command
    subparsers.add_parser('list-monitors', help='List all monitors')

    # get-monitor command
    get_parser = subparsers.add_parser('get-monitor', help='Get monitor details')
    get_parser.add_argument('--id', type=int, required=True, help='Monitor ID')

    # delete-monitor command
    delete_parser = subparsers.add_parser('delete-monitor', help='Delete a monitor')
    delete_parser.add_argument('--id', type=int, required=True, help='Monitor ID')

    # pause-monitor command
    pause_parser = subparsers.add_parser('pause-monitor', help='Pause a monitor')
    pause_parser.add_argument('--id', type=int, required=True, help='Monitor ID')

    # resume-monitor command
    resume_parser = subparsers.add_parser('resume-monitor', help='Resume a monitor')
    resume_parser.add_argument('--id', type=int, required=True, help='Monitor ID')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Validate credentials
    if not args.username or not args.password:
        print("ERROR: Username and password are required", file=sys.stderr)
        print("Set UPTIME_KUMA_USERNAME and UPTIME_KUMA_PASSWORD environment variables", file=sys.stderr)
        print("or use --username and --password flags", file=sys.stderr)
        sys.exit(1)

    manager = KumaManager(args.url, args.username, args.password)

    try:
        if args.command == 'add-monitor':
            kwargs = {}
            if args.max_retries:
                kwargs['maxretries'] = args.max_retries
            if args.retry_interval:
                kwargs['retryInterval'] = args.retry_interval

            result = manager.add_monitor(
                args.name,
                args.type,
                args.url,
                args.interval,
                **kwargs
            )
            print(f"✅ Monitor created successfully")
            print(f"   ID: {result['monitorID']}")
            print(f"   Name: {args.name}")
            print(f"   URL: {args.url}")

        elif args.command == 'list-monitors':
            monitors = manager.list_monitors()
            if not monitors:
                print("No monitors found")
            else:
                print(f"Found {len(monitors)} monitor(s):\n")
                for monitor in monitors:
                    status = "🟢 UP" if monitor.get('active') else "🔴 DOWN"
                    print(f"  [{monitor['id']}] {monitor['name']}")
                    print(f"      URL: {monitor.get('url', 'N/A')}")
                    print(f"      Type: {monitor.get('type', 'N/A')}")
                    print(f"      Status: {status}")
                    print(f"      Interval: {monitor.get('interval', 'N/A')}s")
                    print()

        elif args.command == 'get-monitor':
            monitor = manager.get_monitor(args.id)
            print(json.dumps(monitor, indent=2))

        elif args.command == 'delete-monitor':
            manager.delete_monitor(args.id)
            print(f"✅ Monitor {args.id} deleted successfully")

        elif args.command == 'pause-monitor':
            manager.pause_monitor(args.id)
            print(f"⏸️  Monitor {args.id} paused")

        elif args.command == 'resume-monitor':
            manager.resume_monitor(args.id)
            print(f"▶️  Monitor {args.id} resumed")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
