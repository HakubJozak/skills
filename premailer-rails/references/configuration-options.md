# Premailer-Rails Configuration Options Reference

## Configuration Syntax

Configure premailer-rails by merging options into the config hash, typically in an initializer:

```ruby
# config/initializers/premailer_rails.rb
Premailer::Rails.config.merge!(
  preserve_styles: true,
  remove_ids: true,
  generate_text_part: true
)
```

## Premailer-Rails Specific Options

### `generate_text_part`
- **Type:** Boolean
- **Default:** `true`
- **Purpose:** Automatically generates plain-text version from HTML content
- **Usage:** Set to `false` to disable automatic plain-text generation

```ruby
Premailer::Rails.config.merge!(generate_text_part: false)
```

### `input_encoding`
- **Type:** String
- **Default:** `'UTF-8'`
- **Purpose:** Specifies the encoding of the input HTML
- **Usage:** Change if your emails use a different encoding

### `strategies`
- **Type:** Array of Symbols
- **Default:** `[:filesystem, :asset_pipeline, :network]`
- **Purpose:** Controls which CSS retrieval strategies are used and their priority order
- **Usage:** Customize to modify how stylesheets are located

```ruby
# Only use asset pipeline and network, skip filesystem
Premailer::Rails.config.merge!(strategies: [:asset_pipeline, :network])
```

## Core Premailer Options

All options from the Premailer gem can be passed through premailer-rails configuration.

### CSS Processing Options

#### `preserve_styles`
- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Retains link and style elements in the output HTML
- **Common Usage:** Keep style blocks for email clients that support them

```ruby
Premailer::Rails.config.merge!(preserve_styles: true)
```

#### `css_to_attributes`
- **Type:** Boolean
- **Default:** `true`
- **Purpose:** Copies related CSS properties into HTML attributes (e.g., `width`, `height`, `align`)
- **Example:** CSS `width: 600px` becomes HTML attribute `width="600"`

#### `include_link_tags`
- **Type:** Boolean
- **Default:** `true`
- **Purpose:** Process CSS from `<link rel="stylesheet">` tags

#### `include_style_tags`
- **Type:** Boolean
- **Default:** `true`
- **Purpose:** Process CSS from `<style>` tags

#### `css`
- **Type:** Array of Strings
- **Default:** `[]`
- **Purpose:** Manually specify CSS file paths to include

```ruby
Premailer::Rails.config.merge!(css: ['/path/to/extra.css'])
```

#### `css_string`
- **Type:** String
- **Default:** `nil`
- **Purpose:** Pass CSS directly as a string instead of from files

```ruby
Premailer::Rails.config.merge!(css_string: '.button { background: red; }')
```

#### `create_shorthands`
- **Type:** Boolean
- **Default:** `true`
- **Purpose:** Combines individual CSS properties into shorthand format
- **Example:** Combines `margin-top`, `margin-right`, etc. into `margin`

#### `preserve_style_attribute`
- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Maintains original inline style attributes instead of replacing them

### HTML Attribute Options

#### `remove_ids`
- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Eliminates ID attributes from elements
- **Note:** Also converts internal anchors to use name attributes

```ruby
Premailer::Rails.config.merge!(remove_ids: true)
```

#### `remove_classes`
- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Removes all class attributes from elements

#### `remove_comments`
- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Strips HTML comments from output

#### `remove_scripts`
- **Type:** Boolean
- **Default:** `true`
- **Purpose:** Removes `<script>` elements from HTML

#### `reset_contenteditable`
- **Type:** Boolean
- **Default:** `true`
- **Purpose:** Removes contenteditable attributes

### Color Options

#### `rgb_to_hex_attributes`
- **Type:** Boolean
- **Default:** `true`
- **Purpose:** Converts RGB color values to hexadecimal format
- **Example:** `rgb(255, 0, 0)` becomes `#ff0000`

### URL Handling Options

#### `base_url`
- **Type:** String
- **Default:** `nil`
- **Purpose:** Base URL for resolving relative paths to absolute URLs
- **Example:** `/images/logo.png` becomes `https://example.com/images/logo.png`

```ruby
Premailer::Rails.config.merge!(base_url: 'https://example.com')
```

#### `link_query_string`
- **Type:** String
- **Default:** `nil`
- **Purpose:** Query string appended to all anchor href attributes
- **Usage:** Add tracking parameters to all links

```ruby
Premailer::Rails.config.merge!(link_query_string: 'utm_source=email&utm_medium=email')
```

#### `escape_url_attributes`
- **Type:** Boolean
- **Default:** `true`
- **Purpose:** URL-escapes href, src, and background attributes

#### `unescaped_ampersand`
- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Uses unescaped ampersands (`&`) instead of encoded (`&amp;`) in URLs

### Text Generation Options

#### `line_length`
- **Type:** Integer
- **Default:** `65`
- **Purpose:** Maximum line length used by `to_plain_text` method

#### `replace_html_entities`
- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Converts HTML entities to actual characters

### Warning and Error Options

#### `warn_level`
- **Type:** Integer
- **Default:** `Premailer::Warnings::SAFE`
- **Purpose:** Determines CSS compatibility warning verbosity
- **Options:**
  - `Premailer::Warnings::SAFE` - Only safe warnings
  - `Premailer::Warnings::POOR` - Poor support warnings
  - `Premailer::Warnings::RISKY` - All warnings including risky

```ruby
Premailer::Rails.config.merge!(warn_level: Premailer::Warnings::RISKY)
```

#### `verbose`
- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Prints errors and warnings to `$stderr`

#### `io_exceptions`
- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Throws exceptions on I/O errors instead of silently failing

### Parser Options

#### `adapter`
- **Type:** Symbol
- **Default:** `:nokogiri`
- **Purpose:** Selects HTML parser implementation
- **Options:**
  - `:nokogiri` - Default, balanced performance
  - `:nokogiri_fast` - 20x speed improvement, higher memory usage
  - `:nokogumbo` - Alternative parser

```ruby
Premailer::Adapter.use = :nokogiri_fast
```

#### `with_html_string`
- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Treats HTML parameter as raw string instead of file path

#### `html_fragment`
- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Handles HTML fragment without wrapper elements

### Encoding Options

#### `input_encoding`
- **Type:** String
- **Default:** `'ASCII-8BIT'`
- **Purpose:** Source document character encoding

#### `output_encoding`
- **Type:** String
- **Default:** `nil`
- **Purpose:** Nokogiri adapter output character encoding

### MailChimp Compatibility

#### `preserve_reset`
- **Type:** Boolean
- **Default:** `true`
- **Purpose:** Maintains MailChimp reset code styles

## Complete Example Configuration

```ruby
# config/initializers/premailer_rails.rb
Premailer::Rails.config.merge!(
  # Premailer-Rails options
  generate_text_part: true,
  input_encoding: 'UTF-8',
  strategies: [:filesystem, :asset_pipeline, :network],

  # CSS processing
  preserve_styles: true,
  css_to_attributes: true,
  create_shorthands: true,

  # HTML cleanup
  remove_ids: false,
  remove_classes: false,
  remove_comments: false,
  remove_scripts: true,

  # URL handling
  base_url: 'https://example.com',
  link_query_string: 'utm_source=email',

  # Colors
  rgb_to_hex_attributes: true,

  # Debugging
  verbose: Rails.env.development?,
  warn_level: Premailer::Warnings::SAFE
)
```

## Special CSS Properties

Premailer supports custom CSS properties for table attributes:

| CSS Property | HTML Elements | HTML Attribute |
|--------------|---------------|----------------|
| `-premailer-width` | table, th, td | `width` |
| `-premailer-height` | table, tr, th, td | `height` |
| `-premailer-cellpadding` | table | `cellpadding` |
| `-premailer-cellspacing` | table | `cellspacing` |
| `-premailer-align` | table | `align` |

**Example:**

```css
table {
  -premailer-cellspacing: 5;
  -premailer-width: 500;
  -premailer-align: center;
}
```

Produces:

```html
<table cellspacing="5" width="500" align="center">
```

## Data Attributes

### Ignoring Elements

Add `data-premailer="ignore"` to exclude elements from processing:

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css"
      data-premailer="ignore">

<style data-premailer="ignore">
  /* This CSS will not be processed */
</style>
```
