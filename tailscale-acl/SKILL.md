---
name: tailscale-acl
description: Write, explain, and apply Tailscale ACL (access control list) JSON policy files. Use when working with Tailscale network permissions, tailnet policy files, ACL rules, tags, groups, SSH ACLs, exit nodes, subnet routes, autoApprovers, postures, or device access control. Also use when asked to review, debug, or generate Tailscale ACL configurations.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - WebFetch
---

# Tailscale ACL Management

Write, explain, and apply Tailscale tailnet policy files (ACLs) in huJSON format.

## When to Use

- Writing or generating Tailscale ACL JSON files from scratch
- Explaining existing ACL configurations
- Adding rules, groups, tags, SSH access, exit nodes, or subnet routes
- Debugging why a device can't reach another device
- Setting up tests to validate ACL correctness
- Applying ACL changes via API or admin console

## Core Concepts

**Deny-by-default**: No traffic allowed unless explicitly permitted. An empty `"acls": []` denies everything. Absence of the `acls` key uses the default allow-all policy.

**Directional**: `src -> dst` does not imply `dst -> src`. Each direction needs its own rule.

**Locally enforced**: Each device enforces its own incoming rules. No central firewall.

**Tags vs Users**: Mutually exclusive on a device. Tagging a device removes user identity. Tags are for servers/infrastructure; users are for personal devices.

## File Format

Tailscale ACLs use **huJSON** (human JSON) - JSON with comments and trailing commas allowed. The file is called the "tailnet policy file."

## Policy File Structure

```jsonc
{
  // Optional: Named user collections (Premium plans)
  "groups": {
    "group:engineering": ["alice@example.com", "bob@example.com"]
  },

  // Optional: Friendly names for IPs/CIDRs
  "hosts": {
    "oak": "100.109.100.104",
    "dev-subnet": "192.168.1.0/24"
  },

  // Optional: Who can assign each tag
  "tagOwners": {
    "tag:server":  ["autogroup:admin"],
    "tag:monitor": ["group:engineering"]
  },

  // Required: Access rules (empty array = deny all)
  "acls": [
    {
      "action": "accept",
      "src": ["group:engineering"],
      "dst": ["tag:server:*"]
    }
  ],

  // Optional: SSH access rules
  "ssh": [
    {
      "action": "check",
      "src": ["autogroup:member"],
      "dst": ["autogroup:self"],
      "users": ["autogroup:nonroot"],
      "checkPeriod": "12h"
    }
  ],

  // Optional: Auto-approve subnet routes and exit nodes
  "autoApprovers": {
    "routes": {
      "192.168.1.0/24": ["tag:subnet-router"]
    },
    "exitNode": ["tag:exit-node"]
  },

  // Optional: Device posture requirements
  "postures": {
    "posture:latestMac": [
      "node:os IN ['macos']",
      "node:tsVersion >= '1.40'"
    ]
  },

  // Optional: Node configuration attributes
  "nodeAttrs": [
    {
      "target": ["autogroup:member"],
      "attr": ["funnel"]
    }
  ],

  // Recommended: Validate your rules
  "tests": [
    {
      "src": "alice@example.com",
      "accept": ["tag:server:22"],
      "deny":   ["tag:prod:443"]
    }
  ]
}
```

## Quick Reference

### Source/Destination Selectors

| Selector | Example | Notes |
|----------|---------|-------|
| Wildcard | `*` | All tailnet devices |
| User | `alice@example.com` | Premium plans |
| Group | `group:engineering` | Premium plans |
| Tag | `tag:server` | All plans |
| Tailscale IP | `100.64.0.1` | All plans |
| CIDR | `192.168.1.0/24` | Subnet range |
| Host alias | `my-host` | Defined in `hosts` |
| Autogroup | `autogroup:member` | Built-in groups |

### Autogroups

| Autogroup | Meaning |
|-----------|---------|
| `autogroup:member` | All tailnet members |
| `autogroup:admin` | Admin users |
| `autogroup:owner` | Tailnet owner |
| `autogroup:self` | User's own devices |
| `autogroup:tagged` | All tagged devices |
| `autogroup:internet` | Internet via exit nodes |
| `autogroup:shared` | Shared device users |
| `autogroup:nonroot` | Any non-root SSH user |

### Port Formats (in `dst`)

| Format | Example |
|--------|---------|
| All ports | `tag:server:*` |
| Single | `tag:server:22` |
| Multiple | `tag:server:80,443` |
| Range | `tag:server:1000-2000` |

### Protocol Field (optional)

`"proto"`: `"tcp"`, `"udp"`, `"igmp"` (2), `"gre"` (47), `"sctp"` (132), or IANA number 1-255. Only TCP/UDP/SCTP support port specification.

## SSH Section

```jsonc
{
  "ssh": [
    {
      "action": "accept",     // or "check" (requires re-auth)
      "src": ["group:sre"],   // Cannot be bare "*"
      "dst": ["tag:prod"],    // Cannot be bare "*", port always 22
      "users": ["ubuntu", "root"],  // or "autogroup:nonroot"
      "checkPeriod": "12h"    // Only with "check" action, 1m-168h
    }
  ]
}
```

`"check"` action requires periodic re-authentication. Default `checkPeriod` is 12h.

## Tests Section

Tests validate your policy on every change. If a test fails, Tailscale **rejects the policy update**.

```jsonc
"tests": [
  {
    "src": "alice@example.com",
    "accept": ["tag:server:22", "tag:server:443"],
    "deny":   ["tag:prod:22"]
  },
  {
    "src": "tag:monitoring",
    "proto": "tcp",
    "accept": ["tag:server:9100"]
  },
  {
    // ICMP test: use proto "icmp" and port 0
    "src": "bob@example.com",
    "proto": "icmp",
    "accept": ["tag:server:0"]
  },
  {
    // Posture test
    "src": "alice@example.com",
    "srcPostureAttrs": { "node:os": "macos" },
    "accept": ["tag:secure:443"]
  }
]
```

**Limitations**: Cannot use CIDR notation in tests. Use specific IPs or host aliases instead.

## Common Patterns

See `references/patterns.md` for complete examples including:
- Homelab with tagged servers and personal devices
- Production/staging environment separation
- Monitoring with restricted scrape access
- CI/CD pipeline access
- Exit node and subnet router setup
- Contractor/shared access

## Applying ACL Changes

### Admin Console
Edit directly at: Tailscale Admin > Access Controls

### Tailscale API

```bash
# Get current policy
curl -s "https://api.tailscale.com/api/v2/tailnet/-/acl" \
  -u "${TS_API_KEY}:" | jq .

# Update policy (provide full file)
curl -X POST "https://api.tailscale.com/api/v2/tailnet/-/acl" \
  -u "${TS_API_KEY}:" \
  -H "Content-Type: application/json" \
  -d @policy.json

# Validate without applying (dry run)
curl -X POST "https://api.tailscale.com/api/v2/tailnet/-/acl/validate" \
  -u "${TS_API_KEY}:" \
  -H "Content-Type: application/json" \
  -d @policy.json
```

API key: Generate at Tailscale Admin > Settings > Keys > API keys. Use `-` for your own tailnet or the tailnet name for others.

### GitOps

Store the policy file in a Git repo. On PRs, Tailscale validates and tests without applying. On merge to main, changes are applied automatically. Available for all plans. Supports **GitHub Actions**, **GitLab CI**, and **Bitbucket Pipelines**.

See `references/gitops.md` for complete setup guides per platform.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| No `acls` key at all | Add `"acls": [...]` - without it the default allow-all applies |
| Forgot reverse direction | Add a second rule for `dst -> src` if bidirectional needed |
| Tagged device can't be addressed by user | Tags replace user identity; use the tag in rules |
| Exit node not working | Add `"dst": ["autogroup:internet:*"]` rule for users |
| Subnet unreachable | Both approve the route (autoApprovers) AND add ACL rule |
| SSH rule with port | SSH section always uses port 22, don't specify ports in `dst` |
| `*` in SSH src/dst | SSH section doesn't allow bare `*`, use `autogroup:member` etc. |
| Test uses CIDR | Tests don't support CIDR; use specific IPs or host aliases |
| Groups on free plan | `groups` requires Premium plan; use tags or autogroups instead |

## Debugging Access Issues

1. Check `tailscale status` to confirm both devices are online
2. Verify the source device's identity (user or tag) with `tailscale whois <ip>`
3. Check if ACL rules exist for that src->dst+port combination
4. For tagged devices, confirm tag is applied: `tailscale status --json | jq '.Self.Tags'`
5. For subnet routes, verify route is approved AND ACL rule exists
6. Run `tailscale ping <target>` to test connectivity
7. Add a `tests` entry matching your expected access to validate the policy
