# Uncloud - Deployment Platform

Uncloud is a decentralized container orchestration platform for deploying applications across heterogeneous infrastructure. It provides a simpler alternative to Kubernetes while supporting multi-machine deployments.

**Project Status**: Currently in active development, not yet production-ready. APIs may change between releases.

- Website: https://uncloud.run
- GitHub: https://github.com/psviderski/uncloud
- Discord: https://discord.gg/eR35KQJhPu

## Key Features

### Infrastructure & Networking
- **Deploy anywhere**: Combine cloud VMs, dedicated servers, and bare metal into unified environment
- **WireGuard mesh network**: Automatic peer discovery with NAT traversal
- **Decentralized architecture**: No central control plane - each machine maintains synchronized cluster state
- **DNS-based service discovery**: Built-in DNS for container communication

### Application Management
- **Docker Compose compatibility**: Familiar service definitions
- **Zero-downtime deployments**: Rolling updates without service interruption
- **Automatic HTTPS**: Caddy reverse proxy with Let's Encrypt
- **Persistent storage**: Docker volumes across machines

### Network Architecture
The system uses a flat WireGuard mesh network:
- `10.210.0.0/16`: Complete mesh network space
- `10.210.X.0/24`: Subnet for machine X
- `10.210.X.1/32`: Machine gateway address
- `10.210.X.Y/32`: Container Y on machine X

### DNS Patterns
- `<machine>.machine.internal` → Machine mesh IP
- `<container>.<machine>.machine.internal` → Container IP
- `<service>.internal` → All service container IPs

## Installation

### macOS via Homebrew
```bash
brew install psviderski/tap/uncloud
```

### macOS/Linux via curl
```bash
curl -fsS https://get.uncloud.run/install.sh | sh
```

## Configuration

### Environment Variables
- `UNCLOUD_CONNECT`: Remote cluster connection string
- `UNCLOUD_CONFIG`: Config file path (default: `~/.config/uncloud/config.yaml`)
- `UNCLOUD_CONTEXT`: Cluster context name
- `UNCLOUD_AUTO_CONFIRM`: Auto-confirm deployment plans

### Connection Methods
- `ssh://user@host` - Built-in SSH library (default)
- `ssh+cli://user@host` - System SSH command (supports ProxyJump, SSH config)
- `tcp://host:port` - Direct TCP connection
- `unix:///path/to/socket` - Unix socket

## Cluster Setup

### Initialize First Machine
```bash
uc machine init root@your-server-ip
```

This creates a new cluster and context in the Uncloud config.

**Flags:**
| Flag | Default | Description |
|------|---------|-------------|
| `--name, -n` | auto | Machine name |
| `--network` | 10.210.0.0/16 | IPv4 network CIDR |
| `--public-ip` | auto | Public IP for ingress |
| `--no-caddy` | false | Skip Caddy deployment |
| `--no-dns` | false | Skip Uncloud DNS reservation |
| `--no-install` | false | Skip Docker/daemon install |
| `--ssh-key, -i` | | Path to SSH private key |
| `--version` | latest | Uncloud daemon version |
| `--context, -c` | default | Context name in config |

### Add More Machines
```bash
uc machine add root@another-server-ip
```

**Flags:**
| Flag | Default | Description |
|------|---------|-------------|
| `--name, -n` | auto | Machine name |
| `--public-ip` | auto | Public IP for ingress |
| `--no-caddy` | false | Skip Caddy deployment |
| `--no-install` | false | Skip Docker/daemon install |
| `--ssh-key, -i` | | Path to SSH private key |
| `--version` | latest | Uncloud daemon version |

## Deploying Services

### Using Docker Compose
```bash
uc deploy
uc deploy -f compose.yaml
uc deploy -f compose.yaml web api
```

**Flags:**
| Flag | Default | Description |
|------|---------|-------------|
| `--file, -f` | compose.yaml | Compose file(s) |
| `--profile, -p` | | Compose profiles to enable |
| `--build-arg` | | Build-time variables |
| `--no-build` | false | Skip building images |
| `--no-cache` | false | Don't use cache when building |
| `--recreate` | false | Force container recreation |
| `--yes, -y` | false | Auto-confirm deployment |

### Using Service Run
```bash
uc run --name my-app -p app.example.com:8000/https image:latest
```

**Flags:**
| Flag | Default | Description |
|------|---------|-------------|
| `--name, -n` | auto | Service name |
| `--publish, -p` | | Port publishing (TCP, UDP, HTTP, HTTPS) |
| `--env, -e` | | Environment variables |
| `--volume, -v` | | Mount volumes or bind mounts |
| `--replicas` | 1 | Number of containers |
| `--mode` | replicated | Replication mode (replicated/global) |
| `--machine, -m` | | Placement constraints |
| `--cpu` | | Max CPU cores |
| `--memory` | | Max memory (b, k, m, g units) |
| `--entrypoint` | | Override image ENTRYPOINT |
| `--user, -u` | | User/UID for container |
| `--privileged` | false | Extended privileges |
| `--pull` | missing | Pull policy (always/missing/never) |
| `--caddyfile` | | Custom Caddy config |

### Port Publishing Format
```bash
# HTTP with automatic HTTPS
-p app.example.com:8000/https

# TCP port
-p 3000:3000/tcp

# UDP port
-p 53:53/udp
```

## Building Images

```bash
uc build
uc build web api
uc build --push
uc build --push-registry
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--file, -f` | Compose file(s) |
| `--profile, -p` | Compose profiles |
| `--build-arg` | Build-time variables |
| `--no-cache` | Skip cache |
| `--pull` | Pull newer base images |
| `--push` | Push to cluster machines |
| `--push-registry` | Push to external registry |
| `--machine, -m` | Target machines for push |
| `--check` | Validate without building |
| `--deps` | Include dependent services |

## Managing Services

### List Containers
```bash
uc ps
uc ps --sort machine
uc ps --sort health
```

### View Logs
```bash
uc logs web
uc logs -f web          # Follow
uc logs -n 50 web       # Last 50 lines
uc logs --since 1h web  # Last hour
uc logs web api db      # Multiple services
```

**Flags:**
| Flag | Default | Description |
|------|---------|-------------|
| `--follow, -f` | false | Stream new logs |
| `--tail, -n` | 100 | Lines per replica |
| `--since` | | After timestamp |
| `--until` | | Before timestamp |
| `--machine, -m` | | Filter by machine |
| `--utc` | false | UTC timestamps |

### Scale Services
```bash
uc scale my-app 3
```

### Execute Commands
```bash
uc exec web                      # Interactive shell
uc exec web /bin/bash            # Specific shell
uc exec -d web /scripts/job.sh   # Background
uc exec --container abc123 web ls
cat dump.sql | uc exec -T db psql -U postgres mydb
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--detach, -d` | Run in background |
| `--no-tty, -T` | Disable pseudo-terminal |
| `--container` | Target specific container |

### Remove Services
```bash
uc rm my-app
uc rm web api db
```

Volumes are preserved - remove separately with `uc volume rm`.

## Workflow Examples

### Deploy Rails App with HTTPS
```bash
# Initialize cluster
uc machine init root@server.example.com

# Deploy from compose.yaml
uc deploy

# Or run directly
uc run --name tender -p tender.example.com:3000/https tender-app:latest
```

### Scale and Monitor
```bash
# Check status
uc ps

# View logs
uc logs -f tender

# Scale up
uc scale tender 2

# Run migrations
uc exec tender bin/rails db:migrate
```

### Multi-Machine Deployment
```bash
# Add second machine
uc machine add root@server2.example.com

# Services automatically distribute across machines
uc deploy
```

## Comparison with Other Tools

| Feature | Uncloud | Kamal | Kubernetes |
|---------|---------|-------|------------|
| Control plane | None | None | Required |
| Multi-machine | Native | Limited | Native |
| Learning curve | Low | Low | High |
| Resource usage | ~150MB | Low | High |
| Docker Compose | Compatible | Not native | Via Kompose |
| Auto HTTPS | Built-in | Via Traefik | Manual setup |

## Resources

- [Design Document](https://github.com/psviderski/uncloud/blob/main/misc/design.md)
- [GitHub Repository](https://github.com/psviderski/uncloud)
- [Official Website](https://uncloud.run)
