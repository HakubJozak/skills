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
uc deploy --no-build              # Skip building (use pre-built images)
uc deploy --no-cache              # Bypass build cache (if building)
uc deploy --build-pull            # Pull newer base images before building
uc deploy -p prod                 # Enable compose profile(s)
uc deploy --build-arg KEY=value   # Pass build arg to image builds
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
uc ps --sort machine              # Sort by machine (also: service, health)
uc ls                             # List all services (alias: uc service ls)
uc inspect <service>              # Detailed info for one service (alias: uc service inspect)
uc inspect caddy                  # Check Caddy reverse proxy
```

### Logs

```bash
uc logs -f <service>              # Follow logs
uc logs -n 200 <service>          # Last 200 lines per replica (default 100)
uc logs -n all <service>          # All logs, no line limit
uc logs --since 1h <service>      # Last hour
uc logs --since 2h --until 1h <service>
uc logs web sidekiq               # Multiple services
uc logs -m machine-name <service> # Filter by machine
uc logs --utc <service>           # UTC timestamps
uc logs                           # Logs from every service in compose.yaml
```

### Exec into Containers

```bash
uc exec <service>                     # Interactive shell (tries bash then sh)
uc exec <service> /bin/bash           # Interactive shell with explicit command
uc exec <service> bin/rails console   # Rails console
uc exec <service> bin/rails db:migrate
uc exec -d <service> /scripts/task.sh # Background command
uc exec -T <service> command          # No TTY (for pipes)
uc exec --container <id> <service> ls # Target a specific replica (ID or prefix)

# Pipe data in:
cat dump.sql | uc exec -T db psql -U myuser mydb
```

> **No `--` separator.** Unlike `docker exec`, `uc exec` does not accept
> `--` between the service name and the command — everything after the
> service is treated as the command, so `uc exec db -- pg_isready` tries
> to run a binary literally named `--`. Write `uc exec db pg_isready …`.

### Scale

```bash
uc scale <service> 3
```

### Start / Stop

```bash
uc stop <service>                 # Graceful stop (SIGTERM, 10s timeout)
uc stop --signal SIGINT <service>
uc stop --timeout 30 <service>    # Wait 30s before SIGKILL (-1 = forever)
uc start <service>                # Restart a previously-stopped service
uc stop web sidekiq               # Multiple services
```

### Remove Services

```bash
uc rm <service>              # Remove service (named volumes preserved)
uc rm web sidekiq            # Remove multiple services
# Anonymous Docker volumes (from VOLUME in Dockerfile) are removed with the container.
# Named volumes must be cleaned up separately via `uc volume rm`.
```

### Run (ad-hoc service, no compose file)

```bash
uc run --name app -p app.example.com:3000/https myimage:latest
uc run --name db -v pgdata:/var/lib/postgresql/data postgres:16
uc run --mode global --name agent myagent:latest
uc run -e KEY=value --cpu 0.5 --memory 512m myimage:latest
uc run -m machine1 myimage:latest   # Machine placement
```

## Machine Management

```bash
uc machine ls
uc machine init root@server.example.com          # Initialize new cluster
uc machine init root@server -c prod -n vps1      # Custom context + name
uc machine init root@server --no-caddy --no-dns  # Skip Caddy + DNS reservation
uc machine add root@server2.example.com          # Add machine to cluster
uc machine add -n worker root@server2            # Name it
uc machine rm machine-name                       # Remove + reset (use --no-reset to keep data)
uc machine rename old-name new-name
uc machine update --name new-name                # Update name or --public-ip
uc machine token                                 # Print local machine token (run on the machine itself)
```

Connection prefixes: `ssh://user@host` (default, built-in SSH) or `ssh+cli://user@host`
(system SSH, supports ProxyJump / SSH config).

## Context Management

```bash
uc ctx ls
uc ctx use production
uc ctx connection              # Change default connection
```

## Volume Management

```bash
uc volume ls                              # All volumes (filter with -m / -q)
uc volume inspect volume-name
uc volume create volume-name -m machine1  # Create on a specific machine
uc volume create data -d local -o type=nfs -o device=...
uc volume rm volume-name                  # Destructive! Fails if in use
uc volume rm -f vol1 vol2 -y              # Force + auto-confirm
```

## Image Management

```bash
uc images                                 # List images on all machines
uc image ls                               # Same thing
uc images -m machine1                     # Only images on one machine
uc images "myapp:1.*"                     # Filter by pattern
uc image push myapp:latest                # Upload local image to every machine
uc image push myapp:latest -m m1,m2       # To specific machines
uc image push myapp:latest --platform linux/amd64
```

## Caddy (Reverse Proxy)

```bash
uc caddy config                # Show generated Caddyfile
uc caddy config -m machine1    # From a specific machine
uc caddy deploy                # Redeploy latest Caddy (rolling update)
uc caddy deploy --image caddybuilds/caddy-cloudflare:2.10.2
uc caddy deploy --caddyfile ./global.caddyfile   # Prepended to auto-generated config
uc caddy deploy -m machine1                      # Only certain machines
```

## Cluster DNS (Uncloud DNS)

Reserves a `xxxxxx.uncld.dev` domain for the cluster. When set, Caddy can
publish services at `service-name.<cluster-domain>` automatically.

```bash
uc dns show        # Current reserved cluster domain
uc dns reserve     # Reserve a new cluster domain
uc dns release     # Release the reserved domain
```

## WireGuard Network

```bash
uc wg show                     # Inspect mesh network state (connected machine)
uc wg show -m machine1         # For a specific machine
```

Network ranges:
- `10.210.0.0/16` — full mesh
- `10.210.X.0/24` — subnet for machine X
- `<service>.internal` — DNS for all service containers
- `<machine>.machine.internal` — DNS for machine mesh IP

## Troubleshooting

- **Service not starting**: `uc logs <service>` → `uc inspect <service>`
- **Image not found on cluster**: `uc build --push` then `uc deploy --no-build`, or `uc image push <image>` to upload a locally-built image
- **List images present on each machine**: `uc images` (or `uc image ls`)
- **HTTPS not working**: `uc caddy config` to inspect Caddyfile; `uc caddy deploy` to refresh
- **Stale containers**: `uc deploy --recreate` to force recreation
- **WireGuard issues**: `uc wg show` to inspect peer state
