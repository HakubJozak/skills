# Premailer-Rails Troubleshooting Guide

## Common Issues and Solutions

### Stylesheets Not Being Found

**Symptom:** CSS styles are not being inlined in emails.

**Causes and Solutions:**

1. **Incorrect Path in Link Tag**

   ```html
   <!-- Wrong: relative to view -->
   <link rel="stylesheet" href="../stylesheets/email.css">

   <!-- Correct: absolute path from public/ -->
   <link rel="stylesheet" href="/stylesheets/email.css">

   <!-- Or use asset pipeline -->
   <link rel="stylesheet" href="<%= asset_path('email.css') %>">
   ```

2. **Asset Pipeline Fingerprinting**

   Premailer-rails automatically strips fingerprints, but ensure your asset is compiled:

   ```bash
   # Precompile assets
   rails assets:precompile
   ```

3. **Missing Stylesheet in Public Directory**

   If using filesystem strategy, ensure file exists:
   ```bash
   ls public/stylesheets/email.css
   ```

4. **Strategy Configuration**

   Verify correct strategies are enabled:
   ```ruby
   # Check current strategies
   Premailer::Rails.config[:strategies]
   # => [:filesystem, :asset_pipeline, :network]
   ```

### Skip Premailer Not Working

**Symptom:** Setting `skip_premailer: false` still skips processing.

**Cause:** Header values are converted to strings, making `'false'` truthy.

**Solution:** Only use `skip_premailer: true` or omit the header entirely:

```ruby
# To skip
mail(to: user.email, skip_premailer: true)

# To process (default)
mail(to: user.email)
```

### Styles Not Inlining in Development Mode

**Symptom:** Styles inline in production but not in development.

**Causes and Solutions:**

1. **Caching Disabled in Development**

   Stylesheets are cached only in production. Development fetches fresh on each request, which may fail if asset compilation is off.

   **Solution:** Precompile assets or enable caching temporarily:
   ```ruby
   # config/environments/development.rb
   config.cache_classes = true
   ```

2. **Asset Pipeline Not Serving Files**

   Ensure the Rails server is running and assets are accessible:
   ```bash
   curl http://localhost:3000/assets/email.css
   ```

### CSS Variables Not Working

**Symptom:** CSS variables like `var(--primary-color)` remain as-is in output.

**Cause:** Premailer does not automatically replace CSS variables with static values.

**Solutions:**

1. **Use Preprocessor Variables**

   Use Sass/SCSS variables instead:
   ```scss
   $primary-color: #007bff;

   .button {
     background-color: $primary-color;
   }
   ```

2. **Use PostCSS**

   Configure PostCSS to resolve CSS variables before premailer processes:
   ```ruby
   # Gemfile
   gem 'postcss-rails'
   ```

3. **Manually Replace Variables**

   Use helper methods to inject values:
   ```erb
   <style>
     .button {
       background-color: <%= brand_primary_color %>;
     }
   </style>
   ```

### Tailwind CSS Not Working

**Symptom:** Tailwind utility classes don't inline properly.

**Cause:** Tailwind generates utility classes on-demand. Premailer may not find the compiled CSS.

**Solutions:**

1. **Ensure Tailwind CSS is Compiled**

   ```bash
   rails assets:precompile
   ```

2. **Configure Tailwind for Email**

   Create email-specific Tailwind build:
   ```javascript
   // tailwind.email.config.js
   module.exports = {
     content: ['./app/views/mailers/**/*.html.erb'],
     // Disable features not supported in email
     corePlugins: {
       preflight: false,
     }
   }
   ```

3. **Link Compiled Tailwind CSS**

   ```erb
   <link rel="stylesheet" href="<%= asset_path('email-tailwind.css') %>">
   ```

4. **Alternative: Use Inline Styles Gem**

   Consider gems specifically designed for Tailwind emails:
   ```ruby
   gem 'tailwind_mailer'
   ```

### External Fonts Not Loading

**Symptom:** Google Fonts or other external fonts referenced in CSS don't appear in emails.

**Cause:** Most email clients don't support external font loading.

**Solutions:**

1. **Ignore Font Stylesheets**

   ```html
   <link rel="stylesheet"
         href="https://fonts.googleapis.com/css?family=Roboto"
         data-premailer="ignore">
   ```

   Some email clients (like Apple Mail) will load them; others will fall back to system fonts.

2. **Use Web-Safe Fonts**

   Stick to fonts available across all platforms:
   ```css
   body {
     font-family: Arial, Helvetica, sans-serif;
   }
   ```

3. **Font Stack Fallbacks**

   ```css
   body {
     font-family: 'Custom Font', Arial, sans-serif;
   }
   ```

### Images Not Displaying

**Symptom:** Images show broken in emails despite correct paths.

**Cause:** Relative image paths don't resolve correctly.

**Solution:** Use `base_url` configuration:

```ruby
Premailer::Rails.config.merge!(
  base_url: 'https://example.com'
)
```

Then images will convert from relative to absolute:
```html
<!-- Before -->
<img src="/images/logo.png">

<!-- After -->
<img src="https://example.com/images/logo.png">
```

### Plain Text Part Has Formatting Issues

**Symptom:** Generated plain text version has poor formatting.

**Solutions:**

1. **Adjust Line Length**

   ```ruby
   Premailer::Rails.config.merge!(line_length: 80)
   ```

2. **Disable Auto-generation and Create Manual Version**

   ```ruby
   Premailer::Rails.config.merge!(generate_text_part: false)
   ```

   Then create text template manually:
   ```ruby
   class UserMailer < ActionMailer::Base
     def welcome_email(user)
       mail(to: user.email) do |format|
         format.html
         format.text { render plain: "Custom plain text" }
       end
     end
   end
   ```

### Performance Issues with Large CSS Files

**Symptom:** Email generation is slow.

**Solutions:**

1. **Use Faster Parser**

   ```ruby
   Premailer::Adapter.use = :nokogiri_fast
   ```

   Note: Uses more memory but 20x faster.

2. **Split Email-Specific CSS**

   Create a smaller CSS file just for emails instead of linking entire application stylesheet:
   ```html
   <!-- Instead of application.css -->
   <link rel="stylesheet" href="/stylesheets/email.css">
   ```

3. **Remove Unused CSS**

   Only include styles actually used in email templates.

4. **Cache Stylesheets**

   Ensure caching is enabled in production (default behavior).

### Media Queries Being Removed

**Symptom:** Responsive email styles disappear.

**Cause:** By default, Premailer may strip media queries.

**Solution:** Preserve style tags containing media queries:

```ruby
Premailer::Rails.config.merge!(preserve_styles: true)
```

Email clients that support media queries will use them; others will use inline styles.

### Nokogiri Gem Not Found

**Symptom:** Error about missing Nokogiri when sending emails.

**Cause:** Premailer-rails doesn't declare hard dependency on HTML parser.

**Solution:** Explicitly add to Gemfile:

```ruby
gem 'nokogiri'
```

Then run:
```bash
bundle install
```

### Rails 7 + Propshaft Issues

**Symptom:** Assets not found with Propshaft asset pipeline.

**Solution:** Premailer-rails supports Propshaft. Ensure assets are in correct location:

```
app/assets/stylesheets/email.css
```

And properly referenced:
```erb
<link rel="stylesheet" href="<%= asset_path('email.css') %>">
```

### Testing Emails Locally

**Issue:** How to test premailer processing during development.

**Solutions:**

1. **Use Letter Opener**

   ```ruby
   # Gemfile
   gem 'letter_opener', group: :development

   # config/environments/development.rb
   config.action_mailer.delivery_method = :letter_opener
   ```

2. **Use Mailer Previews**

   ```ruby
   # test/mailers/previews/user_mailer_preview.rb
   class UserMailerPreview < ActionMailer::Preview
     def welcome_email
       UserMailer.welcome_email(User.first)
     end
   end
   ```

   Visit: `http://localhost:3000/rails/mailers/user_mailer/welcome_email`

3. **Send Test Email to Yourself**

   ```ruby
   # Rails console
   UserMailer.welcome_email(user).deliver_now
   ```

### Debugging CSS Inlining

**How to debug what CSS is being applied:**

1. **Enable Verbose Mode**

   ```ruby
   Premailer::Rails.config.merge!(verbose: true)
   ```

2. **Check Warnings**

   ```ruby
   Premailer::Rails.config.merge!(
     warn_level: Premailer::Warnings::RISKY
   )
   ```

3. **Manually Inspect Processing**

   ```ruby
   mail = UserMailer.welcome_email(user)
   Premailer::Rails::Hook.perform(mail)
   puts mail.html_part.body
   ```

### Email Rendering Differently Across Clients

**Issue:** Email looks different in Gmail vs Outlook vs Apple Mail.

**Reality:** This is expected due to varying CSS support in email clients.

**Best Practices:**

1. **Test in Multiple Clients**

   Use services like:
   - Litmus
   - Email on Acid
   - Mail Tester

2. **Follow Email CSS Best Practices**

   - Use table layouts for structure
   - Inline all critical styles
   - Avoid flexbox/grid
   - Use web-safe colors
   - Test thoroughly

3. **Keep Styles Simple**

   Stick to well-supported CSS properties:
   ```css
   /* Good */
   .button {
     background-color: #007bff;
     color: white;
     padding: 10px 20px;
     text-decoration: none;
   }

   /* Avoid */
   .button {
     display: flex; /* Not supported */
     transform: rotate(45deg); /* Not supported */
   }
   ```

## Getting Help

If issues persist:

1. Check GitHub issues: https://github.com/fphilipe/premailer-rails/issues
2. Review premailer gem docs: https://github.com/premailer/premailer
3. Test email rendering: https://www.caniemail.com/
