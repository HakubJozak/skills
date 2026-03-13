---
name: cloudflare-access
description: Manage Cloudflare Zero Trust Access applications and policies via API. Use when creating, updating, or debugging CF Access apps, bypass/allow/block policies, IP-based rules, path-scoped applications, or webhook bypass configurations.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - WebFetch
  - WebSearch
---

# Cloudflare Zero Trust Access Management

Create and manage Cloudflare Access applications and policies via the API.

## When to Use

- Creating or updating Access applications (self-hosted, SaaS, etc.)
- Setting up bypass policies for webhooks, health checks, or automated services
- Configuring IP-based access rules
- Path-scoped access control (protecting specific endpoints differently from the rest of the app)
- Debugging why requests are blocked by CF Access

## Core Concepts

### Applications

An Access Application defines **what** is protected. For self-hosted apps:

- `domain` field includes both hostname and optional path: `"app.example.com/api/webhooks"`
- `type` is `"self_hosted"` for apps behind CF tunnel or proxy
- `session_duration` controls token expiry (e.g. `"24h"`, `"30m"`)
- Applications are **deny-by-default** -- a user must match an Allow or Bypass policy

### Policies

A Policy defines **who** can access an application. Four action types:

| Action | Behavior | Logging | Identity Required |
|--------|----------|---------|-------------------|
| **Bypass** | Skip all Access controls | No | No |
| **Allow** | Grant access after identity check | Yes | Yes |
| **Block** | Deny access | Yes | Yes |
| **Service Auth** | Authenticate via service token or mTLS | Yes | No (machine) |

**Evaluation order:** Bypass and Service Auth first (top to bottom), then Block and Allow by order.

### Rule Logic

Policies use three rule types:

- **Include** (OR): user needs to match ANY one criterion
- **Exclude** (NOT): matching ANY exclusion denies access
- **Require** (AND): user must satisfy ALL conditions

### Available Selectors

Non-identity (for Bypass policies):
- **IP ranges**: IPv4/IPv6, CIDR notation
- Country, valid certificates, service tokens, device posture

Identity-based (NOT available for Bypass):
- Emails, email domains, IdP groups, SAML/OIDC claims, login methods

## Path-Scoped Bypass (Webhook Pattern)

To bypass Access for a specific path (e.g. webhook endpoint) while keeping the rest protected:

**You MUST create a separate Access Application for the subpath.** You cannot assign paths to policies within a single application.

1. Main app protects `app.example.com` with Allow policy
2. Second app protects `app.example.com/webhooks/endpoint` with Bypass policy
3. CF Access matches the **most specific path first**, so the subpath app takes precedence

This is the standard pattern for webhook callbacks from services like Postmark, Stripe, GitHub, etc.

## API Reference

Base URL: `https://api.cloudflare.com/client/v4`

### Authentication

```
Authorization: Bearer $CF_API_TOKEN
```

Required token permission: **Account > Access: Apps and Policies > Edit**

### Applications

```bash
# List all applications
GET /accounts/{account_id}/access/apps

# Create application
POST /accounts/{account_id}/access/apps
{
  "name": "My App",
  "domain": "app.example.com/optional/path",
  "type": "self_hosted",
  "session_duration": "24h"
}

# Update application
PUT /accounts/{account_id}/access/apps/{app_id}

# Delete application
DELETE /accounts/{account_id}/access/apps/{app_id}
```

### Policies

```bash
# List policies for an application
GET /accounts/{account_id}/access/apps/{app_id}/policies

# Create policy
POST /accounts/{account_id}/access/apps/{app_id}/policies
{
  "name": "Policy Name",
  "decision": "bypass",
  "include": [
    {"ip": {"ip": "1.2.3.4/32"}},
    {"ip": {"ip": "5.6.7.0/24"}}
  ]
}

# Update policy
PUT /accounts/{account_id}/access/apps/{app_id}/policies/{policy_id}

# Delete policy
DELETE /accounts/{account_id}/access/apps/{app_id}/policies/{policy_id}
```

### Reusable Policies (Recommended)

Modern CF Access supports reusable policies that can be shared across applications:

```bash
# Create reusable policy
POST /accounts/{account_id}/access/policies
{
  "name": "Postmark Bypass",
  "decision": "bypass",
  "include": [
    {"ip": {"ip": "3.134.147.250/32"}}
  ]
}

# Reference in application's policies array
PUT /accounts/{account_id}/access/apps/{app_id}
{
  "policies": ["{policy_id}"]
}
```

### IP Include Rule Format

Each IP in `include` is a separate object (OR'd together):

```json
{
  "include": [
    {"ip": {"ip": "1.2.3.4/32"}},
    {"ip": {"ip": "10.0.0.0/8"}},
    {"ip": {"ip": "2001:db8::/32"}}
  ]
}
```

### Bypass Policy for "Everyone"

To bypass for all traffic on a path (no IP restriction):

```json
{
  "name": "Public Bypass",
  "decision": "bypass",
  "include": [
    {"everyone": {}}
  ]
}
```

## API Response Format

All responses follow:

```json
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": { ... }
}
```

Check `success` field; on failure, `errors` array has details.

## Terraform Equivalent

```hcl
resource "cloudflare_access_application" "webhook" {
  account_id       = var.account_id
  name             = "Webhook Bypass"
  domain           = "app.example.com/webhooks"
  type             = "self_hosted"
  session_duration = "24h"
}

resource "cloudflare_access_policy" "webhook_bypass" {
  application_id = cloudflare_access_application.webhook.id
  account_id     = var.account_id
  name           = "Bypass for Webhook IPs"
  decision       = "bypass"
  precedence     = 1

  include {
    ip = ["1.2.3.4/32", "5.6.7.8/32"]
  }
}
```

## Common Gotchas

1. **Bypass != Allow with IP**: `Allow` still requires identity authentication even with IP rules. Only `Bypass` skips auth entirely.
2. **Path scoping requires separate apps**: You cannot scope a policy to a path within an application. Create a new application with the path in the `domain` field.
3. **Bypass disables logging**: Bypassed requests are NOT logged in Access audit logs.
4. **Wrangler can't manage Access**: The Wrangler CLI has no scopes for Zero Trust. Use the API directly or Terraform.
5. **IPs can change**: Third-party webhook IPs (Postmark, Stripe, etc.) can change. Check provider docs periodically.
6. **Most specific path wins**: When multiple applications match a request, the one with the most specific path takes precedence.
7. **Token permissions**: The default DNS/zone tokens don't include Access scopes. Create a dedicated token with Account > Access: Apps and Policies > Edit.

## Script Template

```bash
#!/usr/bin/env bash
set -euo pipefail

CF_API="https://api.cloudflare.com/client/v4"
# Requires: CF_API_TOKEN, CF_ACCOUNT_ID

cf_api() {
  local method=$1 path=$2; shift 2
  curl -sf -X "$method" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    -H "Content-Type: application/json" \
    "$CF_API/accounts/$CF_ACCOUNT_ID/$path" "$@"
}

# List apps
cf_api GET "access/apps" | jq '.result[] | {id, name, domain}'

# Create app
cf_api POST "access/apps" -d '{
  "name": "...",
  "domain": "...",
  "type": "self_hosted",
  "session_duration": "24h"
}'

# Create bypass policy
cf_api POST "access/apps/APP_ID/policies" -d '{
  "name": "...",
  "decision": "bypass",
  "include": [{"ip": {"ip": "1.2.3.4/32"}}]
}'
```
