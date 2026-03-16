---
name: acts-as-tenant
description: Architecture guide for building multitenant Rails applications using the acts_as_tenant gem. This skill should be used when designing or implementing multitenancy in a Rails app, scoping models to a tenant, setting up tenant resolution (subdomain, session, JWT), handling background jobs across tenants, writing tenant-aware tests, or debugging cross-tenant data leaks.
---

# acts_as_tenant — Multitenant Rails Architecture Guide

`acts_as_tenant` enforces tenant scoping at the ActiveRecord level via `default_scope`. Every query on a scoped model is automatically filtered to the current tenant stored in thread-local storage (`ActiveSupport::CurrentAttributes`).

Detailed option reference → `references/api.md`
Cheatsheet → `references/cheatsheet.md`
Traps & gotchas → `references/gotchas.md`

---

## How It Works

1. A tenant object (e.g. `Account`) is stored in `ActsAsTenant.current_tenant` at the start of each request or job.
2. Every model declared with `acts_as_tenant :account` gains a `default_scope` that appends `WHERE account_id = <current>`.
3. Belongs-to associations are automatically validated to stay within the tenant boundary.
4. The tenant FK is immutable after record creation to prevent cross-tenant data movement.

---

## Setup Checklist

### 1. Gemfile
```ruby
gem "acts_as_tenant"
```

### 2. Tenant column on every scoped table
```ruby
add_reference :projects, :account, null: false, index: true
```

### 3. Scope the model
```ruby
class Project < ApplicationRecord
  acts_as_tenant :account
end
```
This auto-adds `belongs_to :account`, a `default_scope`, and before-validation to auto-assign the FK.

### 4. Set the tenant per request — choose one strategy:

**A — Subdomain (most common SaaS pattern)**
```ruby
class ApplicationController < ActionController::Base
  set_current_tenant_by_subdomain(:account, :subdomain)
end
```

**B — Subdomain with domain fallback**
```ruby
set_current_tenant_by_subdomain_or_domain(:account, :subdomain, :domain)
```

**C — Manual (JWT, session, API key, etc.)**
```ruby
class ApplicationController < ActionController::Base
  set_current_tenant_through_filter
  before_action :set_tenant

  private

  def set_tenant
    set_current_tenant(Current.user.account)
  end
end
```

### 5. Validate uniqueness within tenant
```ruby
validates_uniqueness_to_tenant :name
validates_uniqueness_to_tenant :name, scope: [:owner_id]
```

---

## Background Jobs

### ActiveJob
```ruby
class MyJob < ApplicationJob
  include ActsAsTenant::ActiveJobExtensions
end
```
Serializes tenant via GlobalID into job payload; restored on execution.

### Sidekiq
```ruby
# config/initializers/sidekiq.rb
Sidekiq.configure_client do |config|
  config.client_middleware { |c| c.add ActsAsTenant::Sidekiq::Client }
end
Sidekiq.configure_server do |config|
  config.client_middleware { |c| c.add ActsAsTenant::Sidekiq::Client }
  config.server_middleware { |c| c.add ActsAsTenant::Sidekiq::Server }
end
```
Tenant stored as `{"class":"Account","id":42}` in job hash; restored via `job_scope`.

**Soft-deleted tenants in jobs:**
```ruby
ActsAsTenant.configure do |config|
  config.job_scope = -> { with_deleted }
end
```

---

## Escaping Tenant Scope

```ruby
ActsAsTenant.without_tenant { Account.all }           # admin cross-tenant query
ActsAsTenant.with_tenant(other_account) { ... }       # switch tenant for a block
ActsAsTenant.with_mutable_tenant { record.update!(..) } # allow FK mutation
```

---

## Global Records (shared across tenants)

```ruby
class Plan < ApplicationRecord
  acts_as_tenant :account, has_global_records: true
end
# Returns WHERE account_id IN (current_id, NULL)
```

---

## Testing Setup

```ruby
# spec/support/tenant_helpers.rb
RSpec.configure do |config|
  config.before(:suite) { $default_account = Account.create!(name: "test") }

  config.before(:each) do |example|
    if example.metadata[:type] == :request
      ActsAsTenant.test_tenant = $default_account
    else
      ActsAsTenant.current_tenant = $default_account
    end
  end

  config.after(:each) do
    ActsAsTenant.current_tenant = nil
    ActsAsTenant.test_tenant = nil
  end
end
```

```ruby
# config/environments/test.rb
require "acts_as_tenant/test_tenant_middleware"
Rails.application.configure do
  config.middleware.use ActsAsTenant::TestTenantMiddleware
end
```

---

## PostgreSQL Row-Level Security Integration

```ruby
ActsAsTenant.configure do |config|
  config.tenant_change_hook = lambda do |tenant|
    sql = tenant ? ["SET rls.account_id = ?;", tenant.id] : ["RESET rls.account_id;"]
    ActiveRecord::Base.connection.execute(ActiveRecord::Base.sanitize_sql_array(sql))
  end
end
```

---

## Key Architecture Decisions

| Decision | Rationale |
|---|---|
| `default_scope` for filtering | Transparent — works with all Rails query methods including associations |
| `CurrentAttributes` for storage | Thread-safe; no RequestStore dependency |
| Tenant FK immutable after create | Prevents silent cross-tenant record migration |
| Belongs-to validated within scope | Closes FK-reassignment loophole |
| Unsaved tenant → empty result | Fail-safe: unpersisted tenant never exposes data |
| GlobalID for job serialization | Portable; works with any AR model |

---

## Top 5 Pitfalls

1. **Forgot `acts_as_tenant` on a model** → returns all rows. Audit with `Model.scoped_by_tenant?`.
2. **Used `.unscoped` in app code** → strips tenant scope. Use `ActsAsTenant.without_tenant { }` instead.
3. **Cross-tenant association attempt** → raises `ActiveRecord::RecordInvalid`, not silent corruption.
4. **Sidekiq job enqueued without tenant** → no `acts_as_tenant` key, server middleware skips setup.
5. **`require_tenant = true` surprises** → raises `ActsAsTenant::Errors::NoTenantSet` on any unscoped model access.

Full gotchas with fixes → `references/gotchas.md`
