# Uncloud CLI Cheat Sheet

Quick reference for the `uc` command.

## Installation

```bash
# macOS
brew install psviderski/tap/uncloud

# Linux/macOS
curl -fsS https://get.uncloud.run/install.sh | sh

# Verify
uc --version
```

## Cluster Management

```bash
# Initialize new cluster
uc machine init root@server.example.com
uc machine init -n vps1 -c prod root@server.example.com   # -n machine name, -c new context name
uc machine init root@server --no-caddy --no-dns           # Skip Caddy + cluster domain reservation
uc machine init root@server --network 10.42.0.0/16        # Custom mesh CIDR

# Add machine to cluster
uc machine add root@server2.example.com
uc machine add -n worker root@server2.example.com
uc machine add root@server --public-ip none               # Disable ingress on this machine
uc machine add root@server --no-install                   # Daemon already installed
uc machine add root@server --version v0.16.0              # Pin daemon version

# Use system SSH (for ProxyJump, SSH config)
uc machine init ssh+cli://root@server.example.com

# List / rename / remove / update / token
uc machine ls
uc machine rename old new
uc machine rm machine-name          # --no-reset keeps data, -y skips confirm
uc machine update --name new        # --public-ip to change
uc machine token                    # Run on the machine itself to get its join token
```

## Deployment

```bash
# Deploy from compose file
uc deploy
uc deploy -y                            # Auto-confirm (or set UNCLOUD_AUTO_CONFIRM=true)
uc deploy -f production.yaml            # Specific file (can pass multiple)
uc deploy web api                       # Specific services
uc deploy --recreate                    # Force container recreation
uc deploy --no-build                    # Skip building
uc deploy --no-cache                    # Disable cache when building
uc deploy --build-pull                  # Pull newer base images before building
uc deploy --build-arg VAR=value         # Build-time variable (repeatable)
uc deploy -p dev                        # Enable compose profile(s)

# Run single service imperatively (no compose file)
uc run --name app -p app.example.com:3000/https image:latest
uc run --name db -v pgdata:/var/lib/postgresql/data postgres:16
uc run --mode global myimage            # One replica per machine
uc run --replicas 3 myimage             # N replicas
uc run --cpu 0.5 --memory 512m myimage  # Resource limits
uc run --entrypoint "" myimage bash     # Clear ENTRYPOINT, run bash
uc run -e KEY=value -e SECRET myimage   # -e KEY uses value from local env
uc run -m machine1,machine2 myimage     # Restrict to machines
uc run --pull always myimage            # always | missing (default) | never
```

## Service Management

```bash
# List
uc ps                        # All containers (default sort: service)
uc ps --sort machine         # Sort by machine (service | machine | health)
uc ps --sort health          # Sort by health
uc ls                        # List services (alias: uc service ls, uc list)
uc inspect web               # Detailed service info (alias: uc service inspect)

# Scale (scaling down requires confirmation)
uc scale app 3

# Start / stop
uc start web
uc start web sidekiq                 # Multiple services
uc stop web
uc stop --signal SIGINT web          # Custom signal (name or number)
uc stop --timeout 30 web             # Wait 30s before SIGKILL; -1 = forever

# Remove (named volumes are NOT removed; clean up with `uc volume rm`)
uc rm app                    # Remove one service
uc rm app sidekiq web        # Multiple services (aliases: remove, delete)
```

## Logs

```bash
uc logs app                          # Last 100 lines per replica
uc logs -f app                       # Follow/stream
uc logs -n 50 app                    # Last 50 lines per replica
uc logs -n all app                   # All logs, no line limit
uc logs --since 1h app               # Relative duration
uc logs --since 2h --until 1h app    # Time range
uc logs --since 2024-05-14T22:50:00  # RFC 3339 (local timezone)
uc logs --since 1763953966 app       # Unix timestamp
uc logs web api db                   # Multiple services
uc logs -m machine1,machine2 app     # Filter by machine(s)
uc logs --utc app                    # UTC timestamps
uc logs                              # All services from compose.yaml
uc logs --file compose.prod.yaml     # Override compose file used for discovery
# alias: uc log
```

## Execute Commands

```bash
uc exec app                       # Interactive shell (tries bash, falls back to sh)
uc exec app /bin/bash             # Explicit shell
uc exec app bin/rails console     # Rails console
uc exec app bin/rails db:migrate  # Run migrations
uc exec -d app /scripts/task.sh   # Background (detached)
uc exec -T app command            # No TTY (for pipes)
uc exec --container abc123 app ls # Target specific replica (full ID or unique prefix)

# Pipe input
cat backup.sql | uc exec -T db psql -U postgres mydb
```

> **No `--` separator.** `uc exec SERVICE -- cmd` does NOT work; the `--`
> is treated as the command. Put the command directly after the service:
> `uc exec db pg_isready -U postgres`.

## Building Images

```bash
uc build                         # Build all services with build:
uc build web api                 # Specific services
uc build --push                  # Build + push to cluster machines (or x-machines)
uc build --push -m m1,m2         # Push to specific machines
uc build --push-registry         # Push to Docker Hub/registry
uc build --no-cache              # Fresh build
uc build --pull                  # Update base images before building
uc build --check                 # Validate build configuration without building
uc build --deps                  # Also build services listed as dependencies
uc build --build-arg KEY=value   # Build-time variable (repeatable)
uc build -p dev                  # Enable compose profile(s)
uc build -f compose.prod.yaml    # Specific compose file(s)
```

## Image Management

```bash
uc images                                   # List images on all machines (top-level)
uc image ls                                 # Same thing
uc images -m machine1,machine2              # Filter by machine
uc images myapp                             # Filter by name (any tag)
uc images "myapp:1.*"                       # Glob pattern
uc image push myapp:latest                  # Upload local image to cluster
uc image push myapp:latest -m m1,m2         # Push to specific machines
uc image push myapp:latest --platform linux/amd64  # Specific platform from multi-arch
```

## Context Management

```bash
uc ctx ls                    # List contexts (alias: uc ctx list, uc context ls)
uc ctx use production        # Switch context (no arg = interactive picker)
uc ctx connection            # Change default connection for current context (alias: conn)
```

## Volume Management

```bash
uc volume ls                            # List volumes (filter with -m; -q for names only)
uc volume inspect vol-name              # Volume details (-m to pick a machine)
uc volume create vol-name -m machine1   # Create on specific machine
uc volume create data -d local \        # Custom driver + opts
  -o type=nfs -o device=...
uc volume create vol -l key=value       # With labels
uc volume rm vol-name                   # Remove (fails if in use)
uc volume rm -f -y vol1 vol2            # Force + skip confirm
uc volume rm vol -m machine1            # Only remove from specific machine(s)
```

## Caddy & WireGuard

```bash
uc caddy config                      # Show current Caddyfile (connected machine)
uc caddy config -m machine1          # From a specific machine
uc caddy config --no-color           # Disable syntax highlighting
uc caddy deploy                      # Deploy/upgrade Caddy (rolling update)
uc caddy deploy --caddyfile my.conf  # Global Caddyfile prepended to auto-generated config
uc caddy deploy --image caddy:2.10   # Pin Caddy image
uc caddy deploy -m machine1,machine2 # Only certain machines
uc wg show                           # WireGuard state (connected machine)
uc wg show -m machine1               # WireGuard state for specific machine
```

## DNS (Cluster domain)

```bash
uc dns show                             # Show reserved cluster domain
uc dns reserve                          # Reserve xxxxxx.uncld.dev for this cluster
uc dns reserve --endpoint https://...   # Custom DNS API endpoint
uc dns release                          # Release reserved domain
```

## Global Flags

Apply to every command:

```bash
--connect <URL>       # Ad-hoc connection bypassing uncloud config [$UNCLOUD_CONNECT]
-c, --context <name>  # Select cluster context [$UNCLOUD_CONTEXT]
--uncloud-config <f>  # Override config file path [$UNCLOUD_CONFIG]
                      # default: ~/.config/uncloud/config.yaml
-v, --version         # Print uc version
```

Per-command flags (NOT global, but common):

```bash
-f, --file       # Compose file(s) for build/deploy/logs
-y, --yes        # Auto-confirm (deploy, rm, machine rm, volume rm, machine init/add)
-m, --machine    # Filter / target machines (many commands)
-n, --name       # Name a machine or service
```

## Environment Variables

```bash
export UNCLOUD_CONNECT=ssh://root@server
export UNCLOUD_CONTEXT=production
export UNCLOUD_CONFIG=~/.config/uncloud/config.yaml
export UNCLOUD_AUTO_CONFIRM=true
```

## Connection Methods

- `ssh://user@host` — built-in SSH (default)
- `ssh+cli://user@host` — system SSH (supports ProxyJump, SSH config)
- `tcp://host:port` — direct TCP
- `unix:///path/to/socket` — Unix socket

## Port Publishing Format (`-p` / `x-ports`)

```bash
# HTTPS with automatic Let's Encrypt cert
domain.example.com:3000/https

# HTTP only
domain.example.com:3000/http

# TCP on all interfaces
3000:3000/tcp

# TCP on specific IP (loopback or Tailscale)
127.0.0.1:9000:9000/tcp@host
100.x.x.x:9000:9000/tcp@host

# UDP
53:53/udp
```

## Common Patterns

### Deploy Rails App

```bash
uc machine init root@server.example.com
uc deploy
uc exec web bin/rails db:migrate
uc logs -f web
```

### CI/CD Pipeline

```bash
# Step 1 (build stage):
uc build --push

# Step 2 (deploy stage):
uc deploy --no-build -y
```

### Scale and Monitor

```bash
uc ps
uc logs -f web
uc scale web 2
uc exec web bin/rails db:migrate
```
