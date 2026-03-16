# acts_as_tenant — Cheatsheet

## Model Scoping

```ruby
acts_as_tenant :account                                  # basic
acts_as_tenant :account, foreign_key: "accountID"        # custom FK
acts_as_tenant :account, primary_key: "account_code"     # custom PK
acts_as_tenant :account, optional: true                  # nullable FK
acts_as_tenant :account, has_global_records: true        # include nil FK rows
acts_as_tenant :account, polymorphic: true               # polymorphic owner
acts_as_tenant :account, through: :user_accounts         # join table

validates_uniqueness_to_tenant :name                     # unique within tenant
validates_uniqueness_to_tenant :name, scope: [:status]   # with extra scope
```

## Controller

```ruby
# Subdomain
set_current_tenant_by_subdomain(:account, :subdomain)
set_current_tenant_by_subdomain(:account, :subdomain, subdomain_lookup: :last)

# Subdomain + domain fallback
set_current_tenant_by_subdomain_or_domain(:account, :subdomain, :domain)

# Manual
set_current_tenant_through_filter
before_action { set_current_tenant(Current.user.account) }
```

## Setting Tenant

```ruby
ActsAsTenant.current_tenant = account          # set for thread
ActsAsTenant.current_tenant                    # read
ActsAsTenant.with_tenant(account) { ... }      # scoped to block
ActsAsTenant.without_tenant { ... }            # no scope in block
ActsAsTenant.with_mutable_tenant { ... }       # allow FK changes
```

## Config

```ruby
ActsAsTenant.configure do |config|
  config.require_tenant = false                # or true or lambda
  config.pkey = :id                            # tenant PK
  config.job_scope = -> { with_deleted }       # for soft-delete
  config.tenant_change_hook = ->(t) { ... }    # on tenant change
end
```

## Background Jobs

```ruby
# ActiveJob
class MyJob < ApplicationJob
  include ActsAsTenant::ActiveJobExtensions
end

# Sidekiq (initializer)
Sidekiq.configure_client { |c| c.client_middleware { |m| m.add ActsAsTenant::Sidekiq::Client } }
Sidekiq.configure_server do |c|
  c.client_middleware { |m| m.add ActsAsTenant::Sidekiq::Client }
  c.server_middleware { |m| m.add ActsAsTenant::Sidekiq::Server }
end
```

## Testing

```ruby
# Model/unit specs
ActsAsTenant.current_tenant = account
ActsAsTenant.current_tenant = nil              # teardown

# Request/integration specs
ActsAsTenant.test_tenant = account

# Middleware (test.rb env)
require "acts_as_tenant/test_tenant_middleware"
config.middleware.use ActsAsTenant::TestTenantMiddleware
```

## Checks

```ruby
Project.scoped_by_tenant?                      # => true/false
ActsAsTenant.should_require_tenant?            # => true/false
ActsAsTenant.unscoped?                         # => true/false
```

## Errors

```ruby
ActsAsTenant::Errors::NoTenantSet              # no tenant + require_tenant
ActsAsTenant::Errors::TenantIsImmutable        # FK changed after create
```

## Postgres RLS Hook

```ruby
config.tenant_change_hook = lambda do |tenant|
  sql = tenant ? ["SET rls.account_id = ?;", tenant.id] : ["RESET rls.account_id;"]
  ActiveRecord::Base.connection.execute(ActiveRecord::Base.sanitize_sql_array(sql))
end
```

## Danger Zones

| Pattern | Problem | Fix |
|---|---|---|
| `Model.unscoped` | Removes tenant scope | `without_tenant { }` |
| `Account.new` as tenant | Silent empty results | Always persist first |
| No tenant when enqueuing | Job runs unscoped | Guard or raise before enqueue |
| `require_tenant = true` | Breaks admin/auth paths | Use a lambda with path check |
