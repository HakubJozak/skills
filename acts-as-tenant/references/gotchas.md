# acts_as_tenant — Gotchas & Traps

## 1. Tenant FK Is Immutable After Creation

Once a record is saved, the tenant FK cannot be changed. Attempting to assign a different value raises `ActsAsTenant::Errors::TenantIsImmutable`.

```ruby
project = account.projects.create!(name: "foo")
project.account_id = other_account.id  # => raises TenantIsImmutable
project.account_id = account.id        # same value is fine
```

**Fix:** Use `ActsAsTenant.with_mutable_tenant { }` for admin/migration scenarios.

---

## 2. `.unscoped` Strips Tenant Scope Silently

`.unscoped` removes ALL default scopes including the tenant filter. This is a data leak.

```ruby
# DANGEROUS — returns all records regardless of tenant
Project.unscoped.where(name: "foo")

# SAFE — disables scoping explicitly
ActsAsTenant.without_tenant { Project.where(name: "foo") }
```

---

## 3. Unsaved Tenant Returns Empty Set (Not an Error)

If you set an unsaved (not-yet-persisted) AR object as the tenant, queries return empty results silently.

```ruby
ActsAsTenant.current_tenant = Account.new  # not saved
Project.all  # => []  (no error!)
```

**Fix:** Always persist the tenant before setting it. In tests, use `create` not `build`.

---

## 4. Jobs Enqueued Without a Tenant

If a Sidekiq job is enqueued when `ActsAsTenant.current_tenant` is nil, no `acts_as_tenant` key is written to the job payload. The server middleware skips tenant setup → job runs without tenant scope → possible cross-tenant queries or `NoTenantSet` error.

```ruby
# Guard in the caller:
raise "tenant required" unless ActsAsTenant.current_tenant
MyWorker.perform_async(id)
```

---

## 5. `require_tenant = true` Breaks Devise/Admin Paths

Setting `require_tenant = true` raises `ActsAsTenant::Errors::NoTenantSet` on any access to a scoped model without a tenant — including Devise sign-in, admin routes, health checks, etc.

**Fix:** Use a callable:
```ruby
ActsAsTenant.configure do |config|
  config.require_tenant = -> {
    # Skip for paths that don't need a tenant
    path = Thread.current[:request_path]
    path.present? && !path.start_with?("/admin", "/health", "/auth")
  }
end
```

Or store request path in a thread-local from ApplicationController.

---

## 6. Cross-Tenant Association Is Silently Rejected (Not Crashed)

Assigning a belongs-to association from another tenant fails validation but may not raise:

```ruby
task.update(project: other_tenant_project)
# => false (validation failed), not an exception
task.errors.full_messages  # => ["Project is not in the current tenant's scope"]
```

**Fix:** Always check return value of `update`, or use `update!` to raise on failure.

---

## 7. `has_global_records` Includes NULL FK Records for ALL Tenants

When `has_global_records: true`, every tenant sees the global (nil FK) records. This is intended but surprising:

```ruby
# All three accounts will see the global Plan record
Plan.all  # => [<Plan account_id: nil, name: "Free">]
```

**Trap:** If you accidentally leave a record with nil FK, it's visible to everyone.

---

## 8. `through:` Association Requires the Join Table to Be Scoped Too

```ruby
class User < ApplicationRecord
  acts_as_tenant :account, through: :user_accounts
end
class UserAccount < ApplicationRecord
  acts_as_tenant :account  # MUST also scope the join table
end
```

If you forget to scope the join table, a user can be joined to another tenant's records via the unscoped join.

---

## 9. `validates_uniqueness_to_tenant` Does Not Use a DB Unique Index

It's an application-level validation with a race condition under concurrent creates. Always pair with a DB unique index:

```ruby
add_index :projects, [:account_id, :name], unique: true
```

---

## 10. Polymorphic Tenants Require the Type Column in Scope

```ruby
acts_as_tenant :owner, polymorphic: true
```

The generated scope includes both the FK and the type column:
```sql
WHERE owner_id = 1 AND owner_type = 'Account'
```

If you switch a record's polymorphic type, tenant scoping may exclude it from the new tenant's queries even with the right ID.

---

## 11. Subdomain Lookup Is Case-Insensitive But Downcased

The lookup calls `.downcase` on the subdomain before querying. Ensure your `subdomain` column stores values in lowercase.

---

## 12. `test_tenant` vs `current_tenant` in Request Specs

- `current_tenant` is reset per request by `TestTenantMiddleware`.
- `test_tenant` persists across requests within the test.

For unit/model specs: use `current_tenant`.
For request/integration specs: use `test_tenant` + `TestTenantMiddleware`.

Mixing them up causes intermittent test failures where the tenant appears set but is cleared mid-request.

---

## 13. GlobalID Serialization Fails for Non-Persisted Tenant in Jobs

If you enqueue a job with an unsaved tenant:
```ruby
ActsAsTenant.current_tenant = Account.new  # unsaved
MyJob.perform_later
# => raises GlobalID::InvalidGlobalIDError or records nil GID
```

Always persist before enqueuing.
