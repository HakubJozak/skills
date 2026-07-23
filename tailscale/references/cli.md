# Tailscale CLI Complete Reference

All `tailscale` subcommands with flags and examples.

Docs: https://tailscale.com/kb/1080/cli

## Connection Management

### tailscale up

Connect to Tailscale and authenticate.

```
tailscale up [flags]
```

| Flag | Description |
|------|-------------|
| `--accept-routes` | Accept subnet routes from other nodes |
| `--advertise-exit-node` | Offer as exit node |
| `--advertise-routes=CIDR` | Expose physical subnet routes (comma-separated) |
| `--exit-node=IP\|NAME` | Use specified exit node |
| `--exit-node-allow-lan-access` | Allow LAN access while using exit node |
| `--shields-up` | Block incoming connections |
| `--ssh` | Run Tailscale SSH server |
| `--force-reauth` | Force re-authentication |
| `--auth-key=KEY` | Authenticate with pre-generated auth key |
| `--hostname=NAME` | Set custom device hostname |
| `--qr` | Generate QR code for login URL |
| `--snat-subnet-routes=false` | Disable SNAT on subnet router |

### tailscale down

Disconnect from Tailscale.

```
tailscale down [flags]
```

| Flag | Description |
|------|-------------|
| `--accept-risk=RISK` | Skip confirmation (`lose-ssh`, `all`) |
| `--reason=DESC` | Specify disconnection reason |

### tailscale login

Log into Tailscale and register device.

```
tailscale login [flags]
```

Same flags as `tailscale up`. Use `--auth-key` for headless authentication.

### tailscale logout

Disconnect and expire current session.

```
tailscale logout
```

### tailscale set

Change preferences without full reconnect.

```
tailscale set [flags]
```

| Flag | Description |
|------|-------------|
| `--accept-dns` | Accept admin console DNS config |
| `--accept-routes` | Accept subnet routes |
| `--advertise-exit-node` | Offer as exit node |
| `--advertise-routes=CIDR` | Expose subnet routes |
| `--exit-node=IP\|NAME` | Use exit node (`auto:any` for auto-switching) |
| `--exit-node-allow-lan-access` | Keep LAN access via exit node |
| `--hostname=NAME` | Change device hostname |
| `--ssh` | Enable/disable SSH server |
| `--shields-up` | Block incoming connections |
| `--auto-update` | Enable/disable auto-updates |
| `--webclient` | Enable web interface on port 5252 |

### tailscale switch

Switch between Tailscale accounts (fast user switching).

```
tailscale switch ACCOUNT [flags]
tailscale switch --list
tailscale switch remove ID
```

## Status & Diagnostics

### tailscale status

Show device connections.

```
tailscale status [flags]
```

Output columns: Tailscale IP, machine name, owner, OS, connection status.

| Flag | Description |
|------|-------------|
| `--json` | Machine-readable JSON |
| `--web` | Run web interface |
| `--active` | Only active peers |
| `--peers` | Show peers (default: true) |
| `--self` | Show local machine (default: true) |

### tailscale ping

Ping a device over Tailscale.

```
tailscale ping HOSTNAME-OR-IP [flags]
```

| Flag | Description |
|------|-------------|
| `--c=N` | Max pings (default: 10) |
| `--timeout=DUR` | Wait time (default: 5s) |
| `--icmp` | ICMP-level ping |
| `--tsmp` | TSMP-level ping |
| `--until-direct` | Stop once direct path established |

### tailscale netcheck

Check physical network conditions.

```
tailscale netcheck [flags]
```

Reports: UDP connectivity, IPv4/IPv6, NAT type, nearest DERP, relay latencies.

| Flag | Description |
|------|-------------|
| `--every=DUR` | Incremental reports at interval |
| `--format=FMT` | Output format (human, json, json-line) |
| `--verbose` | Verbose logging |

### tailscale ip

Get device Tailscale IP.

```
tailscale ip [flags] [HOSTNAME]
```

| Flag | Description |
|------|-------------|
| `-4` | IPv4 only |
| `-6` | IPv6 only |
| `-1` | One address (prefer IPv4) |
| `--assert=IP` | Verify node IP matches |

### tailscale whois

Identify device/user by IP.

```
tailscale whois IP[:PORT] [flags]
```

| Flag | Description |
|------|-------------|
| `--json` | JSON output |
| `--proto=PROTO` | Protocol filter (tcp/udp/both) |

### tailscale dns

DNS management (v1.74+).

```
tailscale dns status [flags]
tailscale dns query HOSTNAME [flags]   # v1.76+
```

| Flag | Description |
|------|-------------|
| `--all` | Advanced debugging info |
| `--json` | JSON output |

## Routing

### tailscale exit-node

Exit node information.

```
tailscale exit-node list [flags]
tailscale exit-node suggest
```

| Flag | Description |
|------|-------------|
| `--filter=COUNTRY` | Filter by country |

## File Sharing

### tailscale file

Taildrop file transfer.

```
tailscale file cp FILES... TARGET:
tailscale file get TARGET-DIR
```

`cp` flags: `--name=NAME`, `--targets` (list targets), `--verbose`
`get` flags: `--conflict=BEHAVIOR` (skip/overwrite/rename), `--loop`, `--wait`

### tailscale drive

Taildrive directory sharing.

```
tailscale drive share NAME PATH
tailscale drive rename OLD NEW
tailscale drive unshare NAME
tailscale drive list
```

## Services

### tailscale serve

Share local services within tailnet.

```
tailscale serve [flags] TARGET [off]
tailscale serve status [--json]
tailscale serve reset
```

Target types: port (`3000`), URL (`localhost:3000`, `https+insecure://localhost:8443`, `tcp://localhost:5432`), file path, `text:"Hello"`.

| Flag | Description |
|------|-------------|
| `--https=PORT` | HTTPS server (default) |
| `--http=PORT` | HTTP server |
| `--tcp=PORT` | Raw TCP forwarder |
| `--tls-terminated-tcp=PORT` | TLS-terminated TCP |
| `--set-path=PATH` | URL path mount point |
| `--proxy-protocol=VER` | PROXY protocol (1 or 2) |
| `--bg` | Background mode (persists reboots) |
| `--yes` | Skip prompts |

### tailscale funnel

Share local services to public internet. Ports: **443, 8443, 10000** only.

```
tailscale funnel [flags] TARGET [off]
tailscale funnel status
tailscale funnel reset
```

Same flags as `tailscale serve`. Requires MagicDNS and `funnel` ACL node attribute.

### tailscale ssh

SSH via Tailscale identity.

```
tailscale ssh [user@]HOST
```

Uses MagicDNS name or Tailscale IP.

## Security

### tailscale lock

Tailnet Lock management.

```
tailscale lock init
tailscale lock status
tailscale lock add TLPUB...
tailscale lock remove TLPUB...
tailscale lock sign NODEKEY TLPUB
tailscale lock revoke-keys TLPUB...
tailscale lock local-disable
tailscale lock log
```

### tailscale cert

Generate Let's Encrypt certificates for tailnet HTTPS.

```
tailscale cert [flags] HOSTNAME.ts.net
```

| Flag | Description |
|------|-------------|
| `--cert-file=PATH` | Certificate output path |
| `--key-file=PATH` | Private key output path |
| `--min-validity=DUR` | Min remaining validity |
| `--serve-demo` | Demo serve on port 443 |

Certificates expire in 90 days. Manual renewal needed when using `--cert-file`.

### tailscale syspolicy

System policy management.

```
tailscale syspolicy list [--json]
tailscale syspolicy reload
```

## System

### tailscale update

Update Tailscale client.

```
tailscale update [flags]
```

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview without updating |
| `--track=TRACK` | stable/release-candidate/unstable |
| `--version=VER` | Specific version |
| `--yes` | Update without prompts |

### tailscale version

```
tailscale version [flags]
```

| Flag | Description |
|------|-------------|
| `--daemon` | Also print daemon version |
| `--json` | JSON output |
| `--upstream` | Latest upstream release |
| `--track=TRACK` | Check specific track |

### tailscale configure

Configure tailnet resources.

```
tailscale configure kubeconfig HOSTNAME
tailscale configure mac-vpn
tailscale configure synology
tailscale configure sysext
tailscale configure systray
```

### tailscale bugreport

Generate diagnostic report ID for support.

```
tailscale bugreport [flags]
```

| Flag | Description |
|------|-------------|
| `--diagnose` | Print verbose info to logs |
| `--record` | Create before/after identifiers |

### tailscale metrics

Expose Prometheus metrics.

```
tailscale metrics print
tailscale metrics write FILE
```

### tailscale web

Web interface for tailscaled.

```
tailscale web [flags]
```

| Flag | Description |
|------|-------------|
| `--listen=ADDR` | Listen address (default: localhost:8088) |
| `--readonly` | Read-only mode |

### tailscale nc

Netcat-style connection.

```
tailscale nc HOSTNAME-OR-IP PORT
```

### tailscale wait

Wait for Tailscale resources.

```
tailscale wait [--timeout=DUR]
```

### tailscale completion

Shell tab-completion.

```
tailscale completion bash|zsh|fish|powershell [--flags] [--descs]
```

Load for current session:
```bash
source <(tailscale completion bash)
```

Persistent:
```bash
tailscale completion bash > /etc/bash_completion.d/tailscale
```

## Global Flags

| Flag | Description |
|------|-------------|
| `--socket=PATH` | Path to tailscaled socket |
