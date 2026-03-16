# acts_as_tenant — Full API Reference

## Model Macro: `acts_as_tenant`

```ruby
acts_as_tenant(tenant_name, options = {})
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `foreign_key` | String/Symbol | `"#{tenant_name}_id"` | FK column name |
| `primary_key` | String/Symbol | `"id"` | PK on the tenant model |
| `class_name` | String | — | Tenant model class if different from name |
| `optional` | Boolean | `false` | Allow null FK (record not owned by any tenant) |
| `has_global_records` | Boolean | `false` | Include rows with NULL FK in tenant queries |
| `polymorphic` | Boolean | `false` | FK is a polymorphic association |
| `through` | Symbol | — | Scope via a join table (HABTM pattern) |
| `inverse_of` | Symbol | — | Passed to `belongs_to` |
| `counter_cache` | Boolean/Symbol | — | Passed to `belongs_to` |
| `touch` | Boolean/Symbol | — | Passed to `belongs_to` |

### Examples

```ruby
# Basic
acts_as_tenant :account

# Custom FK/PK
acts_as_tenant :account, foreign_key: "accountID", primary_key: "account_code"

# Optional (record can be unowned)
acts_as_tenant :account, optional: true

# Global records included in tenant scope
acts_as_tenant :account, has_global_records: true

# Polymorphic tenant
acts_as_tenant :owner, polymorphic: true

# Join-table (HABTM)
class User < ApplicationRecord
  has_many :user_accounts
  has_many :accounts, through: :user_accounts
  acts_as_tenant :account, through: :user_accounts
end
```

---

## `validates_uniqueness_to_tenant`

```ruby
validates_uniqueness_to_tenant :attribute
validates_uniqueness_to_tenant :attribute, scope: [:other_column]
```

Wraps `validates_uniqueness_of` adding the tenant FK to scope. If `has_global_records: true`, global records (nil FK) validate globally.

---

## Global Configuration

```ruby
ActsAsTenant.configure do |config|
  # Raise NoTenantSet when accessing scoped model without tenant
  # Boolean or callable: -> { !request_path.start_with?("/admin") }
  config.require_tenant = false

  # PK used on tenant model (default :id)
  config.pkey = :id

  # Scope used when looking up tenant for background jobs
  # Useful for soft-deleted tenants
  config.job_scope = -> { with_deleted }

  # Hook called whenever current_tenant changes (including to nil)
  config.tenant_change_hook = lambda do |tenant|
    # e.g. set Postgres RLS variable
  end
end
```

---

## Setting/Getting the Tenant

```ruby
# Set globally for current thread
ActsAsTenant.current_tenant = account

# Get current tenant
ActsAsTenant.current_tenant  # => account or nil

# Block-scoped tenant (restores previous tenant after block)
ActsAsTenant.with_tenant(account) { ... }

# Disable all tenant scoping for a block
ActsAsTenant.without_tenant { ... }

# Allow tenant FK mutation within a block
ActsAsTenant.with_mutable_tenant { record.update!(account: other) }

# Check if scoping is disabled
ActsAsTenant.unscoped?

# Require tenant check (evaluates lambda if configured)
ActsAsTenant.should_require_tenant?
```

---

## Controller Helpers

Include `ActsAsTenant::ControllerExtensions` (auto-included in ActionController::Base).

```ruby
# Resolve tenant from first subdomain
set_current_tenant_by_subdomain(tenant_class, column = :subdomain)
set_current_tenant_by_subdomain(:account, :subdomain)
# Options: subdomain_lookup: :first (default) or :last

# Subdomain with domain fallback
set_current_tenant_by_subdomain_or_domain(tenant_class, subdomain_col, domain_col)

# Manual: call set_current_tenant(obj) in a before_action
set_current_tenant_through_filter
# then in a before_action:
set_current_tenant(account_object)
```

---

## Test Helpers

```ruby
# Set test tenant (used for request specs via middleware)
ActsAsTenant.test_tenant = account

# Middleware: wraps each request, resets test_tenant around request
# so test_tenant survives between requests but doesn't leak into request
require "acts_as_tenant/test_tenant_middleware"
Rails.application.configure do
  config.middleware.use ActsAsTenant::TestTenantMiddleware
end
```

---

## Model Class Methods

```ruby
# Check if a model is tenant-scoped
Project.scoped_by_tenant?  # => true

# Access without default_scope (removes all scopes including tenant)
Project.unscoped  # WARNING: strips tenant scope, prefer without_tenant block
```

---

## Errors

```ruby
ActsAsTenant::Errors::NoTenantSet        # Raised when require_tenant and no tenant set
ActsAsTenant::Errors::TenantIsImmutable  # Raised when FK changed after creation
```

---

## ActiveJob Extension

```ruby
class MyJob < ApplicationJob
  include ActsAsTenant::ActiveJobExtensions
end
```

Adds `serialize`/`deserialize` hooks that pack/unpack tenant via `GlobalID`.

---

## Sidekiq Middleware

```ruby
ActsAsTenant::Sidekiq::Client  # Writes {"acts_as_tenant": {"class":"Account","id":1}} to job
ActsAsTenant::Sidekiq::Server  # Reads it and calls ActsAsTenant.with_tenant { yield }
```

Job without tenant key → server middleware skips (no tenant set).
