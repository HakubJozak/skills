---
name: uncloud
description: Manage uncloud container deployments using the `uc` CLI. This skill should be used when the user wants to deploy, inspect, scale, or manage services on an uncloud cluster; work with compose files using uncloud extensions (x-ports, x-machines); manage machines, volumes, Caddy, or contexts; troubleshoot running services; or run commands inside containers. Triggers on phrases like "deploy to uncloud", "uc deploy", "check uncloud logs", "exec into container", or "scale service".
---

# Uncloud Deployment Management

Uncloud is a decentralized container orchestration platform. Services are defined in Docker Compose
files with custom `x-*` extensions and managed via the `uc` CLI across a WireGuard mesh network.

For full CLI reference and compose extension details, see:
- `references/cheatsheet.md` — quick command reference
- `references/compose-extensions.md` — x-ports, x-machines, and all uncloud compose extensions
- `references/compose-build-spec.md` — full `build:` spec (context, dockerfile, args, cache, secrets, platforms, attestations, etc.)

## Key Workflows

### Deploy

```bash
uc deploy                         # Deploy all services (looks for compose.yaml)
uc deploy -f compose.yml -y       # Specific file, auto-confirm
uc deploy web                     # Deploy single service
uc deploy web sidekiq             # Deploy multiple services
uc deploy --recreate              # Force container recreation
```

### Build & Deploy (services with `build:` section)

```bash
# All-in-one (builds, pushes to cluster, deploys):
uc deploy

# CI/CD split:
uc build --push                   # Build + push images to cluster
uc deploy --no-build              # Deploy without rebuilding
```

### Check Status

```bash
uc ps                             # All running containers
uc ps --sort machine              # Grouped by machine
uc service ls                     # List all services
uc service inspect <service>      # Detailed info for one service
uc inspect caddy                  # Check Caddy reverse proxy
```

### Logs

```bash
uc logs -f <service>              # Follow logs
uc logs -n 200 <service>          # Last 200 lines
uc logs --since 1h <service>      # Last hour
uc logs --since 2h --until 1h <service>
uc logs web sidekiq               # Multiple services
uc logs -m machine-name <service> # Filter by machine
```

### Exec into Containers

```bash
uc exec <service> /bin/bash           # Interactive shell
uc exec <service> bin/rails console   # Rails console
uc exec <service> bin/rails db:migrate
uc exec -d <service> /scripts/task.sh # Background command
uc exec -T <service> command          # No TTY (for pipes)

# Pipe data in:
cat dump.sql | uc exec -T db psql -U myuser mydb
```

### Scale

```bash
uc scale <service> 3
```

### Remove Services

```bash
uc rm <service>              # Remove service (volumes preserved)
uc rm <service> --volumes    # Remove service + its volumes (destructive!)
```

## Machine Management

```bash
uc machine ls
uc machine init root@server.example.com         # Initialize new cluster
uc machine init -n myname root@server.example.com
uc machine add root@server2.example.com          # Add machine
uc machine rm machine-name
uc machine rename old-name new-name
```

## Context Management

```bash
uc ctx ls
uc ctx use production
uc ctx connection              # Change default connection
```

## Volume Management

```bash
uc volume ls
uc volume inspect volume-name
uc volume rm volume-name       # Destructive!
```

## Caddy (Reverse Proxy)

```bash
uc caddy config                # Show generated Caddyfile
uc caddy deploy                # Redeploy latest Caddy
uc caddy deploy --image caddybuilds/caddy-cloudflare:2.10.2
```

## WireGuard Network

```bash
uc wg show                     # Inspect mesh network state
```

Network ranges:
- `10.210.0.0/16` — full mesh
- `10.210.X.0/24` — subnet for machine X
- `<service>.internal` — DNS for all service containers
- `<machine>.machine.internal` — DNS for machine mesh IP

## Troubleshooting

- **Service not starting**: `uc logs <service>` → `uc service inspect <service>`
- **Image not found on cluster**: `uc build --push` then `uc deploy --no-build`
- **HTTPS not working**: `uc caddy config` to inspect Caddyfile; `uc caddy deploy` to refresh
- **Stale containers**: `uc deploy --recreate` to force recreation
- **WireGuard issues**: `uc wg show` to inspect peer state
