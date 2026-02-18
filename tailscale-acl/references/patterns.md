# Tailscale ACL Patterns & Examples

Complete, copy-paste-ready ACL configurations for common scenarios.

## Homelab Setup

Personal tailnet with tagged servers and personal device access.

```jsonc
{
  "hosts": {
    "oak":     "100.109.100.104",
    "juniper": "100.x.x.x"
  },

  "tagOwners": {
    "tag:server":     [],  // empty = only admins can assign
    "tag:exit-node":  [],
    "tag:monitoring": []
  },

  "acls": [
    // Personal devices can reach all servers
    {
      "action": "accept",
      "src": ["autogroup:member"],
      "dst": ["tag:server:*"]
    },
    // Servers can talk to each other
    {
      "action": "accept",
      "src": ["tag:server"],
      "dst": ["tag:server:*"]
    },
    // Monitoring can scrape all devices
    {
      "action": "accept",
      "src": ["tag:monitoring"],
      "dst": ["*:9090,9100,3001"]
    },
    // Allow exit node internet access
    {
      "action": "accept",
      "src": ["autogroup:member"],
      "dst": ["autogroup:internet:*"]
    },
    // Users can reach their own devices
    {
      "action": "accept",
      "src": ["autogroup:member"],
      "dst": ["autogroup:self:*"]
    }
  ],

  "ssh": [
    {
      "action": "check",
      "src": ["autogroup:member"],
      "dst": ["autogroup:self"],
      "users": ["autogroup:nonroot", "root"],
      "checkPeriod": "24h"
    },
    {
      "action": "check",
      "src": ["autogroup:member"],
      "dst": ["tag:server"],
      "users": ["dev", "root"],
      "checkPeriod": "12h"
    }
  ],

  "autoApprovers": {
    "exitNode": ["tag:exit-node"]
  },

  "tests": [
    {
      "src": "owner@example.com",
      "accept": ["tag:server:22", "tag:server:80", "tag:server:443"]
    },
    {
      "src": "tag:monitoring",
      "accept": ["tag:server:9100"],
      "deny":   ["tag:server:22"]
    }
  ]
}
```

## Production/Staging Separation

Dev team accesses staging; only DevOps accesses production.

```jsonc
{
  "groups": {
    "group:dev":    ["alice@example.com", "bob@example.com"],
    "group:devops": ["carl@example.com"]
  },

  "tagOwners": {
    "tag:staging":    ["group:devops"],
    "tag:prod":       ["group:devops"],
    "tag:monitoring": ["group:devops"]
  },

  "acls": [
    // Everyone accesses own devices
    {
      "action": "accept",
      "src": ["autogroup:member"],
      "dst": ["autogroup:self:*"]
    },
    // Developers access staging
    {
      "action": "accept",
      "src": ["group:dev"],
      "dst": ["tag:staging:*"]
    },
    // DevOps accesses everything
    {
      "action": "accept",
      "src": ["group:devops"],
      "dst": ["tag:staging:*", "tag:prod:*", "tag:monitoring:*"]
    },
    // Everyone can view monitoring dashboards
    {
      "action": "accept",
      "src": ["autogroup:member"],
      "dst": ["tag:monitoring:80,443,3000"]
    },
    // Monitoring scrapes all servers
    {
      "action": "accept",
      "src": ["tag:monitoring"],
      "dst": ["tag:staging:9100", "tag:prod:9100"]
    }
  ],

  "ssh": [
    {
      "action": "check",
      "src": ["group:devops"],
      "dst": ["tag:prod"],
      "users": ["ubuntu", "root"],
      "checkPeriod": "1h"
    },
    {
      "action": "accept",
      "src": ["group:dev", "group:devops"],
      "dst": ["tag:staging"],
      "users": ["ubuntu"]
    }
  ],

  "tests": [
    {
      "src": "carl@example.com",
      "accept": ["tag:prod:80", "tag:staging:80"]
    },
    {
      "src": "alice@example.com",
      "accept": ["tag:staging:80"],
      "deny":   ["tag:prod:80"]
    },
    {
      "src": "tag:monitoring",
      "accept": ["tag:prod:9100"],
      "deny":   ["tag:prod:22"]
    }
  ]
}
```

## Subnet Router with Restricted Access

Expose a local network to specific users.

```jsonc
{
  "tagOwners": {
    "tag:subnet-router": ["autogroup:admin"]
  },

  "acls": [
    // Admin accesses entire subnet
    {
      "action": "accept",
      "src": ["autogroup:admin"],
      "dst": ["192.168.1.0/24:*"]
    },
    // Members only access specific services on the subnet
    {
      "action": "accept",
      "src": ["autogroup:member"],
      "dst": ["192.168.1.0/24:80,443,8080"]
    }
  ],

  "autoApprovers": {
    "routes": {
      "192.168.1.0/24": ["tag:subnet-router"]
    }
  },

  "tests": [
    {
      "src": "admin@example.com",
      "accept": ["192.168.1.50:22"]
    }
  ]
}
```

## CI/CD Pipeline

CI runners deploy to staging; only tagged CI can promote to prod.

```jsonc
{
  "groups": {
    "group:dev":    ["alice@example.com", "bob@example.com"],
    "group:devops": ["carl@example.com"]
  },

  "tagOwners": {
    "tag:ci":      ["group:devops"],
    "tag:staging": ["group:devops", "tag:ci"],
    "tag:prod":    ["group:devops", "tag:ci"]
  },

  "acls": [
    // Developers access staging directly
    {
      "action": "accept",
      "src": ["group:dev"],
      "dst": ["tag:staging:*"]
    },
    // CI can deploy to staging and prod
    {
      "action": "accept",
      "src": ["tag:ci"],
      "dst": ["tag:staging:*", "tag:prod:*"]
    },
    // DevOps full access
    {
      "action": "accept",
      "src": ["group:devops"],
      "dst": ["tag:ci:*", "tag:staging:*", "tag:prod:*"]
    }
  ],

  "tests": [
    {
      "src": "tag:ci",
      "accept": ["tag:prod:443", "tag:staging:443"]
    },
    {
      "src": "alice@example.com",
      "accept": ["tag:staging:443"],
      "deny":   ["tag:prod:443"]
    }
  ]
}
```

## Network Microsegmentation

Isolated segments that cannot communicate with each other.

```jsonc
{
  "tagOwners": {
    "tag:segment-a": ["autogroup:admin"],
    "tag:segment-b": ["autogroup:admin"],
    "tag:jumpbox":   ["autogroup:admin"]
  },

  "acls": [
    // Admins access all segments
    {
      "action": "accept",
      "src": ["autogroup:admin"],
      "dst": ["tag:segment-a:*", "tag:segment-b:*"]
    },
    // Jumpbox can reach all segments
    {
      "action": "accept",
      "src": ["tag:jumpbox"],
      "dst": ["tag:segment-a:*", "tag:segment-b:*"]
    },
    // Within-segment communication
    {
      "action": "accept",
      "src": ["tag:segment-a"],
      "dst": ["tag:segment-a:*"]
    },
    {
      "action": "accept",
      "src": ["tag:segment-b"],
      "dst": ["tag:segment-b:*"]
    }
    // Note: no rule allows segment-a <-> segment-b
  ],

  "tests": [
    {
      "src": "tag:segment-a",
      "accept": ["tag:segment-a:443"],
      "deny":   ["tag:segment-b:443"]
    },
    {
      "src": "tag:segment-b",
      "accept": ["tag:segment-b:443"],
      "deny":   ["tag:segment-a:443"]
    }
  ]
}
```

## Exit Node with Posture Check

Only allow exit node usage from up-to-date devices.

```jsonc
{
  "tagOwners": {
    "tag:exit-node": ["autogroup:admin"]
  },

  "postures": {
    "posture:upToDate": [
      "node:tsReleaseTrack == 'stable'",
      "node:tsVersion >= '1.60'"
    ]
  },

  "acls": [
    {
      "action": "accept",
      "src": ["autogroup:member"],
      "srcPosture": ["posture:upToDate"],
      "dst": ["autogroup:internet:*"]
    }
  ],

  "autoApprovers": {
    "exitNode": ["tag:exit-node"]
  }
}
```

## Contractor / Shared Access

Third-party contractors access only dev environment via shared devices.

```jsonc
{
  "groups": {
    "group:dev": ["alice@example.com", "bob@example.com"]
  },

  "tagOwners": {
    "tag:dev": ["group:dev"]
  },

  "acls": [
    // Members access own devices
    {
      "action": "accept",
      "src": ["autogroup:member"],
      "dst": ["autogroup:self:*"]
    },
    // Dev team and shared-device users access dev environment
    {
      "action": "accept",
      "src": ["group:dev", "autogroup:shared"],
      "dst": ["tag:dev:*"]
    }
  ],

  "tests": [
    {
      "src": "alice@example.com",
      "accept": ["tag:dev:443"]
    }
  ]
}
```

## Docs Reference

- ACL overview: https://tailscale.com/kb/1018/acls
- ACL syntax: https://tailscale.com/kb/1337/acl-syntax
- ACL examples: https://tailscale.com/docs/reference/examples/acls
- Tags: https://tailscale.com/kb/1068/acl-tags
- SSH ACLs: https://tailscale.com/kb/1193/tailscale-ssh
- Subnet routers: https://tailscale.com/kb/1019/subnets
- Exit nodes: https://tailscale.com/kb/1103/exit-nodes
