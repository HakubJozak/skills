# Tailscale Docker & Container Reference

Docs: https://tailscale.com/kb/1282/docker
Code examples: https://github.com/tailscale-dev/docker-guide-code-examples

## Docker Compose Sidecar Pattern

The standard pattern runs Tailscale as a sidecar container. The application container shares its network namespace.

```yaml
services:
  tailscale:
    image: tailscale/tailscale:latest
    hostname: my-service
    environment:
      - TS_AUTHKEY=tskey-auth-XXXXX
      - TS_STATE_DIR=/var/lib/tailscale
      - TS_HOSTNAME=my-service
    volumes:
      - tailscale-state:/var/lib/tailscale
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    devices:
      - /dev/net/tun:/dev/net/tun
    restart: unless-stopped

  app:
    image: myapp:latest
    network_mode: service:tailscale
    depends_on:
      - tailscale

volumes:
  tailscale-state:
```

## Standalone Docker

```bash
docker run -d \
  --name=tailscale \
  --hostname=my-container \
  -e TS_AUTHKEY=tskey-auth-XXXXX \
  -e TS_STATE_DIR=/var/lib/tailscale \
  -e TS_HOSTNAME=my-container \
  -v tailscale-state:/var/lib/tailscale \
  --cap-add=NET_ADMIN \
  --cap-add=SYS_MODULE \
  --device=/dev/net/tun:/dev/net/tun \
  tailscale/tailscale:latest
```

## Subnet Router in Docker

```yaml
services:
  tailscale:
    image: tailscale/tailscale:latest
    environment:
      - TS_AUTHKEY=tskey-auth-XXXXX
      - TS_STATE_DIR=/var/lib/tailscale
      - TS_HOSTNAME=docker-router
      - TS_ROUTES=172.16.0.0/24
      - TS_USERSPACE=false
    volumes:
      - tailscale-state:/var/lib/tailscale
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    devices:
      - /dev/net/tun:/dev/net/tun
    sysctls:
      - net.ipv4.ip_forward=1
      - net.ipv6.conf.all.forwarding=1
```

## Serve/Funnel in Docker

Mount a JSON serve config:

```yaml
services:
  tailscale:
    image: tailscale/tailscale:latest
    environment:
      - TS_AUTHKEY=tskey-auth-XXXXX
      - TS_STATE_DIR=/var/lib/tailscale
      - TS_HOSTNAME=my-service
      - TS_SERVE_CONFIG=/config/serve.json
    volumes:
      - tailscale-state:/var/lib/tailscale
      - ./serve-config:/config
```

Example `serve.json`:
```json
{
  "TCP": {
    "443": {
      "HTTPS": true
    }
  },
  "Web": {
    "my-service.tail12345.ts.net:443": {
      "Handlers": {
        "/": {
          "Proxy": "http://127.0.0.1:3000"
        }
      }
    }
  }
}
```

## Userspace vs Kernel Networking

**Userspace mode** (default, `TS_USERSPACE=true`):
- No `NET_ADMIN` or `/dev/net/tun` needed
- Less performant
- Cannot act as subnet router or exit node

**Kernel mode** (`TS_USERSPACE=false`):
- Requires `NET_ADMIN`, `SYS_MODULE`, `/dev/net/tun`
- Full performance
- Required for subnet routing, exit nodes

## All Environment Variables

### Authentication

| Variable | Description |
|----------|-------------|
| `TS_AUTHKEY` | Auth key for automated login. Append `?ephemeral=true` for ephemeral nodes |
| `TS_CLIENT_ID` | OAuth client ID |
| `TS_CLIENT_SECRET` | OAuth client secret |
| `TS_ID_TOKEN` | Identity provider token for workload identity federation |
| `TS_AUDIENCE` | Target audience for ID token requests |
| `TS_AUTH_ONCE` | Only authenticate when unauthenticated (default: false) |

### Networking & Routing

| Variable | Description |
|----------|-------------|
| `TS_HOSTNAME` | Custom tailnet hostname |
| `TS_ROUTES` | Advertise subnet routes |
| `TS_ACCEPT_DNS` | Accept MagicDNS config from admin console |
| `TS_USERSPACE` | Userspace networking mode (default: true) |
| `TS_DEST_IP` | Proxy incoming traffic to destination IP |
| `TS_TAILNET_TARGET_IP` | Route non-Tailscale traffic to tailnet IP |
| `TS_TAILNET_TARGET_FQDN` | Route via MagicDNS resolution |

### Services

| Variable | Description |
|----------|-------------|
| `TS_SERVE_CONFIG` | JSON config path for Serve/Funnel (mount as directory volume) |
| `TS_SOCKS5_SERVER` | SOCKS5 proxy address:port |
| `TS_OUTBOUND_HTTP_PROXY_LISTEN` | HTTP proxy address:port |

### State & Storage

| Variable | Description |
|----------|-------------|
| `TS_STATE_DIR` | Persistent state directory (must survive restarts) |
| `TS_KUBE_SECRET` | Kubernetes secret name for state (default: `tailscale`) |

### Monitoring

| Variable | Description |
|----------|-------------|
| `TS_ENABLE_HEALTH_CHECK` | Enable `/healthz` endpoint (200 when node has IP) |
| `TS_ENABLE_METRICS` | Enable `/metrics` Prometheus endpoint |
| `TS_LOCAL_ADDR_PORT` | Listen address for metrics/health (default: `[::]:9002`) |

### Advanced

| Variable | Description |
|----------|-------------|
| `TS_SOCKET` | Unix socket path for LocalAPI |
| `TS_EXTRA_ARGS` | Additional `tailscale up` flags |
| `TS_TAILSCALED_EXTRA_ARGS` | Additional `tailscaled` daemon flags |
| `TS_EXPERIMENTAL_SERVICE_AUTO_ADVERTISEMENT` | Auto service advertisement (default: true, v1.96+) |

## Kubernetes

For Kubernetes, Tailscale provides:
- Official Helm chart
- Kubernetes operator for automated sidecar injection
- State storage via Kubernetes secrets (`TS_KUBE_SECRET`)

Docs: https://tailscale.com/kb/1185/kubernetes

## Tips

- Always use `TS_STATE_DIR` with a persistent volume to survive container restarts
- Use ephemeral auth keys for short-lived containers
- Use tagged auth keys to auto-apply ACL tags
- Disable key expiry on infrastructure containers
- For health checks in orchestrators, enable `TS_ENABLE_HEALTH_CHECK`
- The `/metrics` endpoint is unauthenticated; bind to localhost or restrict access
