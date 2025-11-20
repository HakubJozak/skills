---
name: premailer-rails
description: Guide for integrating and configuring premailer-rails gem in Rails applications to automatically convert CSS to inline styles for HTML emails. Use when working with Rails ActionMailer and email styling, setting up email CSS inlining, configuring premailer options, troubleshooting email rendering issues across email clients (Gmail, Outlook, Apple Mail), or when users mention premailer-rails, CSS inline styles, or email compatibility problems.
---

# Premailer-Rails

Integrate and configure premailer-rails to automatically convert CSS to inline styles for HTML emails in Rails applications.

## Overview

Premailer-rails solves the fundamental email styling problem: most email clients ignore linked stylesheets and `<style>` tags. The gem automatically converts CSS rules into inline `style` attributes while maintaining clean separation of HTML and CSS during development.

## Quick Start

### Installation

Add to Gemfile:
```ruby
gem 'premailer-rails'
gem 'nokogiri'  # Required HTML parser
```

Run `bundle install`.

### Basic Usage

No configuration required. The gem automatically processes all ActionMailer emails on delivery:

```ruby
class UserMailer < ActionMailer::Base
  def welcome_email(user)
    mail(to: user.email, subject: 'Welcome!')
  end
end
```

Link stylesheets in email templates:
```erb
<link rel="stylesheet" href="/stylesheets/email.css">
```

## Configuration

Configure in an initializer (optional):

```ruby
# config/initializers/premailer_rails.rb
Premailer::Rails.config.merge!(
  preserve_styles: true,        # Keep style tags for clients that support them
  remove_ids: false,            # Keep ID attributes
  generate_text_part: true,     # Auto-generate plain text version
  base_url: 'https://example.com'  # Convert relative URLs to absolute
)
```

**For complete configuration options**, see [configuration-options.md](references/configuration-options.md).

## Common Tasks

### Skip Processing for Specific Emails

```ruby
mail(to: user.email, skip_premailer: true)
```

### Exclude Stylesheets from Processing

Add `data-premailer="ignore"` to link tags (useful for external fonts):
```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css"
      data-premailer="ignore">
```

### Manual Processing

```ruby
mail = SomeMailer.some_message(args)
Premailer::Rails::Hook.perform(mail)
```

### Configure CSS Retrieval Strategies

Control how stylesheets are located:
```ruby
Premailer::Rails.config.merge!(
  strategies: [:asset_pipeline, :network]  # Skip filesystem
)
```

## CSS Retrieval Flow

The gem locates stylesheets using three strategies in order:

1. **Filesystem** - Checks `public/` directory
2. **Asset Pipeline** - Requests through Rails asset pipeline (strips fingerprints)
3. **Network** - HTTP requests for CDN-hosted assets

Stylesheets are cached in production.

## Framework Integration

### Rails (Automatic)

Works automatically with ActionMailer. Supports Rails 5-7, Sprockets, and Propshaft.

### Non-Rails Frameworks

Manually register interceptors:
```ruby
Premailer::Rails.register_interceptors
```

## Special CSS Properties

Use custom properties for table attributes:

```css
table {
  -premailer-width: 600;
  -premailer-cellspacing: 0;
  -premailer-align: center;
}
```

Generates:
```html
<table width="600" cellspacing="0" align="center">
```

## Troubleshooting

### Stylesheets Not Inlining

1. Verify stylesheet path is absolute from `public/`: `/stylesheets/email.css`
2. Check assets are compiled: `rails assets:precompile`
3. Ensure Nokogiri gem is installed

### CSS Variables Not Working

Premailer doesn't resolve CSS variables. Use Sass variables or PostCSS instead:
```scss
$primary-color: #007bff;
.button { background-color: $primary-color; }
```

### Tailwind CSS Issues

1. Compile Tailwind: `rails assets:precompile`
2. Create email-specific Tailwind build
3. Link compiled CSS in email template

### Performance Issues

Use faster parser adapter:
```ruby
Premailer::Adapter.use = :nokogiri_fast
```

**For comprehensive troubleshooting**, see [troubleshooting.md](references/troubleshooting.md).

## Documentation

- **[premailer-rails.md](references/premailer-rails.md)** - Complete setup guide, usage patterns, and how it works
- **[configuration-options.md](references/configuration-options.md)** - Full reference of all configuration options
- **[troubleshooting.md](references/troubleshooting.md)** - Common issues and solutions

## Testing Emails

Use Rails mailer previews to test CSS inlining:

```ruby
# test/mailers/previews/user_mailer_preview.rb
class UserMailerPreview < ActionMailer::Preview
  def welcome_email
    UserMailer.welcome_email(User.first)
  end
end
```

Visit: `http://localhost:3000/rails/mailers`

## Best Practices

1. **Create email-specific CSS files** - Don't link entire application stylesheet
2. **Use table layouts** - Better email client support than modern CSS
3. **Set base_url in production** - Convert relative URLs to absolute
4. **Test across email clients** - Use Litmus or Email on Acid
5. **Keep styles simple** - Stick to well-supported CSS properties
6. **Preserve style tags** - Set `preserve_styles: true` for responsive emails
