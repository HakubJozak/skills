# Premailer-Rails Complete Guide

## Overview

Premailer-Rails is a Ruby gem that automates CSS inlining for HTML emails. It solves the fundamental problem that most email clients ignore linked stylesheets and `<style>` tags by converting CSS rules into inline `style` attributes on HTML elements.

**Key Benefit:** Maintain clean, separated HTML and CSS files during development while generating properly styled emails that work across all email clients.

## Installation

Add to your Gemfile:

```ruby
gem 'premailer-rails'
gem 'nokogiri'  # Required HTML parser
```

Run:
```bash
bundle install
```

**Important:** You must add an HTML parser gem (Nokogiri is recommended) since neither Premailer nor Premailer-Rails declares hard dependencies. Other options include `hpricot`.

## Basic Setup

### Rails Application

No configuration required for basic functionality. The gem automatically:
- Registers a delivery hook with ActionMailer
- Processes all outgoing emails on delivery
- Inlines CSS from linked stylesheets and style tags

### Non-Rails Environments

For frameworks like Sinatra, manually register interceptors:

```ruby
Premailer::Rails.register_interceptors
```

## How It Works

### CSS Retrieval Strategies

The gem locates and retrieves stylesheets using three strategies in priority order:

1. **In-memory cache** (disabled in Rails development mode)
2. **Filesystem Strategy**
   - Checks the `public/` directory for matching file paths
   - Looks for files like `public/stylesheets/email.css`

3. **Asset Pipeline Strategy** (Rails only)
   - Requests files through Rails' asset pipeline
   - Automatically strips asset fingerprints (e.g., `email-abc123.css` → `email.css`)
   - Supports both Sprockets and Propshaft

4. **Network Strategy**
   - Falls back to direct HTTP requests
   - Useful for CDN-hosted assets

### Stylesheet Caching

Retrieved stylesheets are cached in production Rails environments to improve performance.

## Usage with ActionMailer

### Automatic Processing

All emails are processed automatically when delivered:

```ruby
class UserMailer < ActionMailer::Base
  def welcome_email(user)
    mail(to: user.email, subject: 'Welcome!')
  end
end

# Premailer automatically processes on delivery
UserMailer.welcome_email(user).deliver
```

### Skipping Processing for Specific Emails

Use the `:skip_premailer` header to bypass processing:

```ruby
class UserMailer < ActionMailer::Base
  def plain_email(user)
    mail(
      to: user.email,
      subject: 'Plain Email',
      skip_premailer: true
    )
  end
end
```

**Important Caveat:** Even setting `skip_premailer: false` will cause premailer to be skipped because the header value is transformed into a string, making `'false'` truthy.

### Manual Processing

Trigger CSS inlining manually outside normal delivery:

```ruby
mail = SomeMailer.some_message(args)
Premailer::Rails::Hook.perform(mail)
```

This modifies the email object in place.

## Stylesheet Handling

### Link Tags

The gem processes `<link rel="stylesheet">` tags:

```html
<link rel="stylesheet" href="/stylesheets/email.css">
<link rel="stylesheet" href="https://cdn.example.com/styles.css">
```

### Excluding Stylesheets

Add `data-premailer="ignore"` to exclude specific stylesheets from processing (useful for external fonts):

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto"
      data-premailer="ignore">
```

### Style Tags

Inline `<style>` tags are also processed:

```html
<style>
  .button {
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
  }
</style>
```

## Rails Version Support

Tested and compatible with:
- Rails 5.x
- Rails 6.x
- Rails 7.x

Supports both asset pipeline implementations:
- Sprockets
- Propshaft

## Framework Independence

While built for Rails ActionMailer, premailer-rails functions independently and can be used with:
- Sinatra
- Other Ruby web frameworks
- Standalone Ruby scripts

## Plain Text Generation

By default, the gem generates a plain-text version of HTML emails with:
- Inlined links
- Image alt text
- Proper text formatting

Disable this feature in configuration:

```ruby
Premailer::Rails.config.merge!(generate_text_part: false)
```

## License

Released under the MIT License.
