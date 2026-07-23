---
name: tailscale
description: Manage Tailscale networks, devices, and services via CLI and API. This skill should be used when working with Tailscale networking - installing or configuring Tailscale, managing devices and tailnets, setting up subnet routers, exit nodes, DNS (MagicDNS), Tailscale SSH, Serve/Funnel, auth keys, Tailnet Lock, Docker containers, key expiry, or troubleshooting connectivity. For ACL/policy file authoring, use the tailscale-acl skill instead.
---

# Tailscale Network Management

Manage Tailscale mesh VPN networks: install, configure devices, set up routing, DNS, SSH, services, and troubleshoot connectivity. For ACL policy file authoring and examples, defer to the `tailscale-acl` skill.

## When to Use

- Installing Tailscale on servers or containers
- Configuring subnet routers, exit nodes, or DNS
- Setting up Tailscale SSH, Serve, or Funnel
- Managing auth keys, node keys, or Tailnet Lock
- Running Tailscale in Docker/Kubernetes
- Diagnosing connectivity or NAT traversal issues
- Querying device status, IPs, or tailnet state
- Using the Tailscale API for automation

## Core Concepts

**Tailnet**: Private mesh network of devices authenticated to the same Tailscale account. Each device gets a stable `100.x.y.z` IP address. Devices communicate peer-to-peer via WireGuard encryption.

**DERP relays**: Fallback relays when direct peer-to-peer NAT traversal fails. Tailscale cannot decrypt traffic passing through DERP.

**Coordination server**: Control plane that distributes node keys and configuration. Never handles user traffic.

**MagicDNS**: Automatic DNS resolution for tailnet devices by hostname (e.g., `my-server.tail12345.ts.net`).

**Tags vs Users**: Mutually exclusive on a device. Tagging removes user identity. Tags are for servers/infrastructure; users are for personal devices.

## Installation

Universal Linux installer:
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

Start and authenticate:
```bash
sudo tailscale up
```

Authenticate headlessly (servers, CI):
```bash
sudo tailscale up --auth-key=tskey-auth-XXXXX
```

## CLI Quick Reference

See `references/cli.md` for the complete CLI reference with all flags.

### Connection

| Command | Purpose |
|---------|---------|
| `tailscale up [flags]` | Connect and authenticate |
| `tailscale down` | Disconnect |
| `tailscale login --auth-key=KEY` | Auth with pre-generated key |
| `tailscale logout` | Disconnect and expire session |
| `tailscale set [flags]` | Change preferences without restart |
| `tailscale switch ACCOUNT` | Switch between accounts |

### Status & Diagnostics

| Command | Purpose |
|---------|---------|
| `tailscale status` | List devices and connection state |
| `tailscale status --json` | Machine-readable status |
| `tailscale ping HOST` | Test connectivity to peer |
| `tailscale netcheck` | Check NAT, UDP, DERP latency |
| `tailscale ip [-4\|-6]` | Show Tailscale IP |
| `tailscale whois IP` | Identify device/user by IP |
| `tailscale dns status` | Show DNS forwarder config |
| `tailscale version --daemon` | Show client and daemon version |

### Routing

| Command | Purpose |
|---------|---------|
| `tailscale set --advertise-routes=CIDR` | Advertise subnet routes |
| `tailscale set --advertise-exit-node` | Offer as exit node |
| `tailscale set --exit-node=HOST` | Use exit node |
| `tailscale set --exit-node-allow-lan-access` | Keep LAN access via exit node |
| `tailscale set --accept-routes` | Accept advertised subnets (Linux) |
| `tailscale exit-node list` | List available exit nodes |
| `tailscale exit-node suggest` | Get recommended exit node |

### Services

| Command | Purpose |
|---------|---------|
| `tailscale serve PORT` | Share local service on tailnet |
| `tailscale serve --bg PORT` | Share in background (persists) |
| `tailscale funnel PORT` | Expose to public internet |
| `tailscale serve status` | Show serve configuration |
| `tailscale serve reset` | Clear all serve config |
| `tailscale ssh user@host` | SSH via Tailscale identity |
| `tailscale cert HOSTNAME` | Generate Let's Encrypt cert |
| `tailscale file cp FILE HOST:` | Send file via Taildrop |
| `tailscale file get DIR` | Receive files |

### Security

| Command | Purpose |
|---------|---------|
| `tailscale lock init` | Initialize Tailnet Lock |
| `tailscale lock status` | Show lock state and TLK |
| `tailscale lock sign NODEKEY TLPUB` | Sign a node into locked tailnet |
| `tailscale lock add TLPUB` | Add trusted signing key |
| `tailscale lock remove TLPUB` | Remove signing key |
| `tailscale set --shields-up` | Block all incoming connections |

### Maintenance

| Command | Purpose |
|---------|---------|
| `tailscale update` | Update to latest version |
| `tailscale update --dry-run` | Preview update |
| `tailscale up --force-reauth` | Rotate keys and re-authenticate |
| `tailscale bugreport` | Generate diagnostic report |
| `tailscale metrics print` | Show Prometheus metrics |

## Subnet Routers

Subnet routers expose physical network segments to the tailnet without installing Tailscale on every device. Traffic goes through the router, which performs SNAT by default.

### Setup (Linux)

1. Enable IP forwarding:
```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
```

2. Advertise routes:
```bash
sudo tailscale set --advertise-routes=192.168.1.0/24,10.0.0.0/16
```

3. Approve routes in admin console (Machines > device > Subnets > Edit) or via `autoApprovers` in ACL policy.

4. On Linux clients, accept routes:
```bash
sudo tailscale set --accept-routes
```

### High Availability

Deploy multiple subnet routers advertising the same routes. Tailscale uses longest-prefix matching for overlapping routes. Avoid `--accept-routes` on standby routers advertising identical routes.

### Disable SNAT

Preserve original source IPs (Linux only):
```bash
tailscale up --snat-subnet-routes=false
```

Requires return routes to `100.64.0.0/10` via router's LAN IP on downstream devices.

## Exit Nodes

Exit nodes route all internet traffic through a tailnet device (like a traditional VPN).

### Setup

On the exit node:
```bash
sudo tailscale set --advertise-exit-node
```

Approve in admin console (Machines > device > Edit route settings > Use as exit node) or via `autoApprovers`.

On clients:
```bash
tailscale set --exit-node=EXIT_NODE_NAME
tailscale set --exit-node-allow-lan-access   # optional: keep local LAN
```

Disable:
```bash
tailscale set --exit-node=
```

## DNS (MagicDNS)

MagicDNS is enabled by default. Devices are reachable by hostname within the tailnet.

### Split DNS

Configure restricted nameservers in admin console (DNS page) to resolve specific domains via internal DNS servers (e.g., `*.corp.example.com` via `10.0.0.53`).

### Override Local DNS

Force all devices to use tailnet global nameservers. Enable in admin console DNS settings. Verify all devices can reach the configured nameservers first.

### Test DNS

```bash
tailscale dns status          # show config
tailscale dns query HOSTNAME  # query via forwarder (v1.76+)
```

On macOS, use `dscacheutil -q host -a name DOMAIN` instead of `nslookup` for accurate split DNS results.

## Tailscale SSH

Centralized SSH authentication using Tailscale identity instead of SSH keys.

### Enable on server

```bash
tailscale set --ssh
```

### Connect

```bash
tailscale ssh user@hostname
ssh user@hostname          # also works via MagicDNS
```

### ACL Configuration

SSH rules go in the `ssh` section of the tailnet policy file (see `tailscale-acl` skill for full syntax):

```jsonc
"ssh": [{
  "action": "check",
  "src": ["autogroup:member"],
  "dst": ["tag:server"],
  "users": ["ubuntu", "root"],
  "checkPeriod": "12h"
}]
```

- `accept`: immediate access
- `check`: requires periodic re-authentication via SSO (1m-168h period)
- Port is always 22; do not specify in `dst`
- Cannot use bare `*` in `src` or `dst`

## Serve & Funnel

### Serve (tailnet-only)

```bash
tailscale serve 3000                           # HTTPS proxy to localhost:3000
tailscale serve --http=80 localhost:3000        # HTTP
tailscale serve --tcp=5432 tcp://localhost:5432 # raw TCP
tailscale serve /path/to/file.html             # static file
tailscale serve --bg 3000                      # background (persists reboots)
tailscale serve 3000 off                       # disable
```

### Funnel (public internet)

Exposes service to the internet through Tailscale relay. Ports limited to **443, 8443, 10000**.

```bash
tailscale funnel 3000
tailscale funnel 3000 off
```

Requires MagicDNS enabled and `funnel` node attribute in ACL policy:
```jsonc
"nodeAttrs": [{"target": ["autogroup:member"], "attr": ["funnel"]}]
```

## Auth Keys

Pre-authentication keys for headless/automated device registration.

| Type | Use case |
|------|----------|
| One-off | Single server, cloud VM |
| Reusable | Fleet provisioning (store securely!) |
| Ephemeral | Containers, Lambda - auto-removes on disconnect |
| Tagged | Applies tags automatically |
| Pre-approved | Skips device approval |

```bash
sudo tailscale up --auth-key=tskey-auth-XXXXX
```

Keys expire in 1-90 days (configurable). Revoking a key does NOT deauthorize existing devices.

## Key Expiry & Rotation

- Default node key expiry: 180 days (configurable 1-180 days)
- Tagged devices: key expiry disabled by default
- Renew expired key: `tailscale up --force-reauth`
- Admin can temporarily extend expired keys for 30 minutes via admin console
- Disable key expiry: admin console > Machines > device > Disable Key Expiry

## Tailnet Lock

Cryptographic verification preventing unauthorized nodes, even if coordination server is compromised.

### Enable

Requires 2+ signing nodes, Tailscale v1.46.1+:
1. Admin console > Device management > Enable Tailnet Lock
2. Select signing nodes, execute generated `tailscale lock init` command
3. Store disablement secrets securely (needed to disable lock)

### Sign nodes

```bash
tailscale lock sign nodekey:XXXX tlpub:YYYY
```

### Manage signing keys

```bash
tailscale lock add tlpub:KEY1 tlpub:KEY2      # add signers
tailscale lock remove tlpub:KEY               # remove signer
tailscale lock status                         # show state
tailscale lock log                            # audit log
```

### Emergency disable

```bash
tailscale lock local-disable   # per-node emergency bypass
```

## Docker Integration

See `references/docker.md` for complete Docker/container configuration.

### Quick start

```yaml
services:
  tailscale:
    image: tailscale/tailscale:latest
    hostname: my-container
    environment:
      - TS_AUTHKEY=tskey-auth-XXXXX
      - TS_STATE_DIR=/var/lib/tailscale
      - TS_HOSTNAME=my-container
    volumes:
      - tailscale-state:/var/lib/tailscale
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    devices:
      - /dev/net/tun:/dev/net/tun

  app:
    image: myapp:latest
    network_mode: service:tailscale

volumes:
  tailscale-state:
```

### Key environment variables

| Variable | Purpose |
|----------|---------|
| `TS_AUTHKEY` | Auth key for automated login |
| `TS_STATE_DIR` | Persistent state directory |
| `TS_HOSTNAME` | Custom tailnet hostname |
| `TS_ROUTES` | Advertise subnet routes |
| `TS_SERVE_CONFIG` | JSON config for Serve/Funnel |
| `TS_EXTRA_ARGS` | Additional `tailscale up` flags |
| `TS_USERSPACE` | Userspace networking (default: true) |
| `TS_ACCEPT_DNS` | Accept MagicDNS config |
| `TS_ENABLE_HEALTH_CHECK` | Enable `/healthz` endpoint |
| `TS_ENABLE_METRICS` | Enable `/metrics` endpoint |

## API

Base URL: `https://api.tailscale.com/api/v2`

Authentication: API key (basic auth, key as username) or OAuth client token.

```bash
# List devices
curl -s "https://api.tailscale.com/api/v2/tailnet/-/devices" \
  -u "${TS_API_KEY}:"

# Get device info
curl -s "https://api.tailscale.com/api/v2/device/{deviceId}" \
  -u "${TS_API_KEY}:"

# Get current ACL policy
curl -s "https://api.tailscale.com/api/v2/tailnet/-/acl" \
  -u "${TS_API_KEY}:"

# Create auth key
curl -X POST "https://api.tailscale.com/api/v2/tailnet/-/keys" \
  -u "${TS_API_KEY}:" \
  -H "Content-Type: application/json" \
  -d '{"capabilities":{"devices":{"create":{"reusable":false,"ephemeral":true,"tags":["tag:server"]}}}}'

# Set DNS nameservers
curl -X POST "https://api.tailscale.com/api/v2/tailnet/-/dns/nameservers" \
  -u "${TS_API_KEY}:" \
  -H "Content-Type: application/json" \
  -d '{"dns":["1.1.1.1","8.8.8.8"]}'
```

Use `-` for your own tailnet or the org name for others. Generate API keys at admin console > Settings > Keys.

## Troubleshooting

### Connectivity

1. `tailscale status` - confirm both devices online
2. `tailscale ping TARGET` - test peer reachability
3. `tailscale netcheck` - check NAT type, UDP, DERP latency
4. `tailscale whois IP` - verify device identity/tags
5. Check ACL rules allow src -> dst + port

### Subnet routes unreachable

1. Verify routes advertised: `tailscale status --json | jq '.Self.AllowedIPs'`
2. Verify routes approved in admin console
3. Verify ACL rules permit traffic to the subnet CIDR
4. On Linux clients: `tailscale set --accept-routes`
5. Check IP forwarding on router: `sysctl net.ipv4.ip_forward`

### Exit node not working

1. Verify exit node advertised and approved
2. ACL must include `"dst": ["autogroup:internet:*"]` rule
3. Client: `tailscale set --exit-node=NODE`
4. Verify: check public IP at whatismyip.com

### DNS issues

1. `tailscale dns status` - check resolver config
2. On macOS use `dscacheutil` not `nslookup` for split DNS
3. Verify nameservers reachable from all devices before enabling override

### Key expired

1. `tailscale up --force-reauth` (need console/local access, not SSH)
2. Admin can extend key 30min via admin console for remote re-auth

## Docs Reference

- Overview: https://tailscale.com/kb/1151/what-is-tailscale
- CLI: https://tailscale.com/kb/1080/cli
- Subnet routers: https://tailscale.com/kb/1019/subnets
- Exit nodes: https://tailscale.com/kb/1103/exit-nodes
- DNS/MagicDNS: https://tailscale.com/kb/1054/dns
- SSH: https://tailscale.com/kb/1193/tailscale-ssh
- Serve: https://tailscale.com/kb/1242/tailscale-serve
- Funnel: https://tailscale.com/kb/1223/funnel
- Auth keys: https://tailscale.com/kb/1085/auth-keys
- Key expiry: https://tailscale.com/kb/1028/key-expiry
- Tailnet Lock: https://tailscale.com/docs/features/tailnet-lock
- Docker: https://tailscale.com/kb/1282/docker
- ACLs: https://tailscale.com/kb/1018/acls (see tailscale-acl skill)
- API: https://tailscale.com/api
