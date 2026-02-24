# Anthropic Admin API

Endpoints that require an **Admin API key** (`sk-ant-admin...`) and are **not** covered by the `anthropic` gem.
Admin keys are provisioned in the Claude Console by org admins.

Uses `http.rb` gem (`gem "http"`).

## Client Helper

```ruby
require "http"
require "json"

module AnthropicAdmin
  BASE = "https://api.anthropic.com/v1/organizations"
  VERSION = "2023-06-01"

  def self.client
    HTTP
      .headers(
        "x-api-key"         => ENV.fetch("ANTHROPIC_ADMIN_KEY"),
        "anthropic-version" => VERSION,
        "content-type"      => "application/json"
      )
  end

  def self.get(path, params = {})
    client.get("#{BASE}#{path}", params: params).parse(:json)
  end

  def self.post(path, body = {})
    client.post("#{BASE}#{path}", json: body).parse(:json)
  end

  def self.delete(path)
    client.delete("#{BASE}#{path}").parse(:json)
  end
end
```

---

## Organization

```ruby
# Get org info
AnthropicAdmin.get("/me")
# => { "id" => "org_...", "name" => "Acme", "type" => "organization" }
```

---

## Cost & Usage Reports

### Credit / Cost Report

Amounts are in **cents** as decimal strings (`"123.45"` = $1.23).

```ruby
report = AnthropicAdmin.get("/cost_report", {
  starting_at: "2026-02-01T00:00:00Z",
  ending_at:   "2026-02-23T23:59:59Z",
  bucket_width: "1d"
})

report["data"].each do |bucket|
  puts bucket["starting_at"]
  bucket["results"].each do |r|
    dollars = r["amount"].to_f / 100
    puts "  #{r["cost_type"]} #{r["model"]}: $#{"%.4f" % dollars}"
  end
end
```

Key response fields per result: `amount` (cents string), `currency`, `cost_type` (`"tokens"`, `"web_search"`, `"code_execution"`), `model`, `service_tier`, `workspace_id`.

Optional `group_by[]`: `"workspace_id"`, `"description"`.

### Messages Usage Report

Detailed token-level breakdown. Supports grouping and filtering by model, workspace, API key, etc.

```ruby
usage = AnthropicAdmin.get("/usage_report/messages", {
  starting_at:  "2026-02-01T00:00:00Z",
  bucket_width: "1d",
  "group_by[]" => "model"
})

usage["data"].each do |bucket|
  bucket["results"].each do |r|
    puts "#{r["model"]}: #{r["output_tokens"]} output tokens"
  end
end
```

Key response fields: `uncached_input_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, `output_tokens`, `model`, `service_tier`, `workspace_id`, `api_key_id`.

Filter params: `api_key_ids[]`, `workspace_ids[]`, `models[]`, `service_tiers[]`.

### Claude Code Usage Report

Per-user productivity metrics (commits, PRs, lines of code). `starting_at` is a date string, not a timestamp.

```ruby
cc = AnthropicAdmin.get("/usage_report/claude_code", { starting_at: "2026-02-22" })

cc["data"].each do |record|
  m = record["core_metrics"]
  puts "#{record.dig("actor", "email")}: #{m["commits"]} commits, #{m["lines_of_code"]} lines"
end
```

---

## API Keys

```ruby
# List all active keys
AnthropicAdmin.get("/api_keys", { status: "active", limit: 100 })

# Get one key
AnthropicAdmin.get("/api_keys/apikey_01...")

# Deactivate a key
AnthropicAdmin.post("/api_keys/apikey_01...", { status: "inactive" })

# Archive a key
AnthropicAdmin.post("/api_keys/apikey_01...", { status: "archived" })

# Rename
AnthropicAdmin.post("/api_keys/apikey_01...", { name: "Production Key v2" })
```

Filter list by: `status` (`"active"` / `"inactive"` / `"archived"`), `workspace_id`, `created_by_user_id`.

Response fields: `id`, `name`, `status`, `partial_key_hint`, `workspace_id`, `created_at`, `created_by`.
Full key value is never returned.

---

## Users

```ruby
# List users (optionally filter by email)
AnthropicAdmin.get("/users", { email: "alice@example.com" })

# Get one user
AnthropicAdmin.get("/users/user_01...")

# Update role (cannot set "admin" via API)
# Valid roles: "user", "developer", "billing", "claude_code_user", "managed"
AnthropicAdmin.post("/users/user_01...", { role: "developer" })

# Remove user (admins cannot be removed via API)
AnthropicAdmin.delete("/users/user_01...")
```

---

## Invites

```ruby
# Create invite (expires after 21 days)
AnthropicAdmin.post("/invites", { email: "new@example.com", role: "developer" })

# List invites
AnthropicAdmin.get("/invites", { limit: 100 })

# Get one
AnthropicAdmin.get("/invites/invite_01...")

# Cancel
AnthropicAdmin.delete("/invites/invite_01...")
```

---

## Workspaces

```ruby
# List (optionally include archived)
AnthropicAdmin.get("/workspaces", { include_archived: false })

# Get one
AnthropicAdmin.get("/workspaces/wrkspc_01...")

# Create
AnthropicAdmin.post("/workspaces", { name: "ML Team" })

# Rename
AnthropicAdmin.post("/workspaces/wrkspc_01...", { name: "ML Team (archived)" })

# Archive (soft delete; workspace_geo is immutable after creation)
AnthropicAdmin.post("/workspaces/wrkspc_01.../archive", {})
```

---

## Workspace Members

```ruby
# Add user to workspace
# workspace_role: "workspace_user" | "workspace_developer" | "workspace_admin"
AnthropicAdmin.post("/workspaces/wrkspc_01.../members", {
  user_id:        "user_01...",
  workspace_role: "workspace_developer"
})

# List members
AnthropicAdmin.get("/workspaces/wrkspc_01.../members")

# Get one
AnthropicAdmin.get("/workspaces/wrkspc_01.../members/user_01...")

# Change role (adds "workspace_billing" as additional option)
AnthropicAdmin.post("/workspaces/wrkspc_01.../members/user_01...", {
  workspace_role: "workspace_admin"
})

# Remove from workspace
AnthropicAdmin.delete("/workspaces/wrkspc_01.../members/user_01...")
```

---

## Pagination

All list endpoints use cursor-based pagination:

```ruby
def paginate(path, params = {})
  results = []
  loop do
    page = AnthropicAdmin.get(path, params)
    results.concat(page["data"])
    break unless page["has_more"]
    params = params.merge(after_id: page["last_id"])
  end
  results
end

all_keys = paginate("/api_keys", { status: "active" })
```

---

## Notes

- Usage data appears within ~5 minutes of request completion
- Cost report excludes Priority Tier (different billing model)
- Admin API key format: `sk-ant-admin...` — distinct from regular `sk-ant-...` keys
- `anthropic-version: 2023-06-01` header is required on all requests
