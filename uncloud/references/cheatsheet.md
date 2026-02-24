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
uc machine init -n production root@server.example.com

# Add machine to cluster
uc machine add root@server2.example.com
uc machine add -n worker root@server2.example.com

# Use system SSH (for ProxyJump, SSH config)
uc machine init ssh+cli://root@server.example.com

# List / rename / remove
uc machine ls
uc machine rename old new
uc machine rm machine-name
```

## Deployment

```bash
# Deploy from compose file
uc deploy
uc deploy -y                     # Auto-confirm
uc deploy -f production.yaml     # Specific file
uc deploy web api                # Specific services
uc deploy --recreate             # Force container recreation
uc deploy --no-build             # Skip building

# Run single service imperatively
uc run --name app -p app.example.com:3000/https image:latest
uc run --name db -v pgdata:/var/lib/postgresql/data postgres:16
```

## Service Management

```bash
# List
uc ps                        # All containers
uc ps --sort machine         # Sort by machine
uc ps --sort health          # Sort by health
uc service ls                # List services
uc service inspect web       # Detailed service info

# Scale
uc scale app 3

# Start / stop
uc start web
uc stop web

# Remove
uc rm app                    # Preserve volumes
uc rm app --volumes          # Also remove volumes (destructive!)
```

## Logs

```bash
uc logs app                  # Last 100 lines
uc logs -f app               # Follow/stream
uc logs -n 50 app            # Last 50 lines
uc logs --since 1h app       # Last hour
uc logs --since 2h --until 1h app
uc logs web api db           # Multiple services
uc logs -m machine1 app      # Filter by machine
uc logs --utc app            # UTC timestamps
```

## Execute Commands

```bash
uc exec app                       # Interactive shell
uc exec app /bin/bash             # Specific shell
uc exec app bin/rails console     # Rails console
uc exec app bin/rails db:migrate  # Run migrations
uc exec -d app /scripts/task.sh   # Background
uc exec -T app command            # No TTY (for pipes)
uc exec --container abc123 app ls # Target specific container

# Pipe input
cat backup.sql | uc exec -T db psql -U postgres mydb
```

## Building Images

```bash
uc build                     # Build all services with build:
uc build web api             # Specific services
uc build --push              # Build + push to cluster machines
uc build --push-registry     # Push to Docker Hub/registry
uc build --no-cache          # Fresh build
uc build --pull              # Update base images
uc build --check             # Validate without building
```

## Image Management

```bash
uc image ls                          # List images on cluster
uc image push myapp:latest           # Upload local image to cluster
uc image push myapp:latest -m m1,m2  # Push to specific machines
uc images                            # Alias for image ls
```

## Context Management

```bash
uc ctx ls                    # List contexts
uc ctx use production        # Switch context
uc ctx rename old new        # Rename context
uc ctx connection            # Change default connection
```

## Volume Management

```bash
uc volume ls                 # List all volumes
uc volume inspect vol-name   # Volume details
uc volume create vol-name    # Create volume
uc volume rm vol-name        # Remove volume
```

## Caddy & WireGuard

```bash
uc caddy config                      # Show current Caddyfile
uc caddy deploy                      # Deploy/upgrade Caddy
uc caddy deploy --caddyfile my.conf  # Custom Caddyfile
uc wg show                           # WireGuard network state
```

## DNS

```bash
uc dns show       # Show cluster domain
uc dns reserve    # Reserve domain in Uncloud DNS
uc dns release    # Release reserved domain
```

## Global Flags

```bash
--connect    # Remote cluster connection string
--context    # Select cluster context
-c           # Short for --context
-f           # Compose file path
-y / --yes   # Auto-confirm
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
