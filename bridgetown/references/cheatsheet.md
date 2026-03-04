# Bridgetown Cheat Sheet

Bridgetown v2.x — Ruby static site generator. ERB is the default template engine.
Docs: https://www.bridgetownrb.com/docs/

---

## New Site Setup

```bash
gem install bridgetown -N
bridgetown new mysite --template erb    # ERB (recommended)
cd mysite
bin/bridgetown start                    # → http://localhost:4000
```

---

## Front Matter (Required for Processing)

Every file in `src/` must have front matter to be transformed:

```markdown
---
layout: default
title: My Page Title
description: SEO description
date: 2024-01-15        # posts only
tags: [ruby, web]       # optional taxonomy
permalink: /custom-url/ # override generated URL
---
Content here.
```

Minimum (empty front matter still triggers processing):
```
---
---
```

**Ruby front matter** (dynamic values):
```ruby
###ruby
layout :post
title "Post ##{rand(100)}"
date Time.now
###
```

---

## ERB Templates

```erb
<!-- Output expression -->
<%= data.title %>

<!-- Code block (no output) -->
<% if data.show_nav %>
  <%= render "nav" %>
<% end %>

<!-- Loop -->
<% collections.posts.resources.each do |post| %>
  <h2><%= post.data.title %></h2>
  <p><%= post.date.strftime("%B %d, %Y") %></p>
<% end %>

<!-- Unescaped HTML (use with caution) -->
<%== raw_html_string %>
```

---

## Layouts

Store in `src/_layouts/`. Layouts wrap resource content.

**ERB layout** (`src/_layouts/default.erb`):
```erb
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title><%= data.title %></title>
  <link rel="stylesheet" href="<%= asset_path :css %>" />
</head>
<body>
  <%= yield %>
  <script src="<%= asset_path :js %>" defer></script>
</body>
</html>
```

**Layout inheritance** — a layout can extend another:
```erb
---
layout: default
---
<article>
  <h1><%= data.title %></h1>
  <time><%= resource.date.strftime("%B %d, %Y") %></time>
  <%= yield %>
</article>
```

**Front matter defaults** (apply layout automatically in `bridgetown.config.yml`):
```yaml
defaults:
  - scope:
      path: "_posts"
      type: posts
    values:
      layout: post
```

---

## Partials

Store in `src/_partials/` with underscore-prefixed filenames.

```
src/_partials/_nav.erb
src/_partials/_footer.erb
src/_partials/_card.erb
```

**Render a partial:**
```erb
<%= render "nav" %>
<%= render "card", title: "Hello", url: "/about/" %>
```

**Inside `_card.erb`:**
```erb
<div class="card">
  <h2><%= title %></h2>
  <a href="<%= url %>">Read more</a>
</div>
```

---

## Components

Store in `src/_components/`. Can have an optional Ruby class for logic.

**Simple ERB component** (`src/_components/button.erb`):
```erb
<button class="btn btn-<%= variant || "primary" %>">
  <%= label %>
</button>
```

**Usage:**
```erb
<%= render "button", label: "Submit", variant: "danger" %>
```

**Ruby component class** (`src/_components/card_component.rb`):
```ruby
class CardComponent < Bridgetown::Component
  def initialize(title:, url:, excerpt: nil)
    @title = title
    @url = url
    @excerpt = excerpt
  end

  def truncated_excerpt
    @excerpt&.truncate(120)
  end
end
```

**Component template** (`src/_components/card_component.erb`):
```erb
<div class="card">
  <h2><a href="<%= @url %>"><%= @title %></a></h2>
  <p><%= truncated_excerpt %></p>
</div>
```

---

## Content Access in Templates

```erb
data.title           # Front matter value
data.my_custom_field # Any front matter key

resource             # Current resource object
resource.content     # Raw content
resource.date        # Date object (posts)
resource.url         # Generated URL
resource.relative_url # URL relative to baseurl

site.metadata.title  # From src/_data/site_metadata.yml
site.config          # bridgetown.config.yml values
site.data.nav        # From src/_data/nav.yml

collections.posts.resources          # All posts
collections.my_collection.resources  # Custom collection
```

---

## Data Files

Place in `src/_data/`. Supports YAML, JSON, CSV, TSV.

```yaml
# src/_data/nav.yml
- title: Home
  url: /
- title: Blog
  url: /blog/
```

```erb
<% site.data.nav.each do |item| %>
  <a href="<%= item["url"] %>"><%= item["title"] %></a>
<% end %>
```

---

## Collections

**Define in `bridgetown.config.yml`:**
```yaml
collections:
  projects:
    output: true
    permalink: /projects/:slug/
  team:
    output: false   # Only usable as data, no pages generated
```

**Content files go in `src/_projects/`:**
```markdown
---
title: My Project
year: 2024
---
Project description here.
```

**Access:**
```erb
<% collections.projects.resources.sort_by { |p| p.data.year }.reverse.each do |project| %>
  <h2><%= project.data.title %></h2>
<% end %>
```

---

## Asset Pipeline (esbuild + PostCSS)

**Entry points:**
- JS: `frontend/javascript/index.js`
- CSS: `frontend/styles/index.css`

**Import CSS in JS:**
```js
// frontend/javascript/index.js
import "../styles/index.css"
```

**Reference compiled assets in templates:**
```erb
<link rel="stylesheet" href="<%= asset_path :css %>" />
<script src="<%= asset_path :js %>" defer></script>
```

**Path aliases in frontend files:**
```js
import "$styles/components/card.css"   // → frontend/styles/
import "$javascript/utils.js"          // → frontend/javascript/
import "$components/button.js"         // → src/_components/
```

**Static files** (in `src/`, served at root, no hashing):
```
src/images/logo.svg → https://example.com/images/logo.svg
src/favicon.ico     → https://example.com/favicon.ico
```

---

## Helpers Quick Reference

```erb
<%= link_to "About", "/about/" %>
<%= link_to "Post", resource, class: "link" %>

<%= asset_path :css %>          # /assets/styles.abc123.css
<%= asset_path :js %>           # /assets/index.def456.js

<%= markdownify "**bold** text" %>

<%= truncate text, length: 150 %>
<%= slugify "My Title" %>       # "my-title"

<%= date_to_string resource.date %>    # "15 Jan 2024"
<%= date_to_xmlschema resource.date %> # ISO 8601
```

---

## Slots (Named Content Blocks)

Pass content from pages up to layouts:

**In page template:**
```erb
<% slot :head_meta do %>
  <meta name="description" content="<%= data.description %>" />
  <meta property="og:image" content="<%= data.image %>" />
<% end %>

<% slot :sidebar do %>
  <p>Page-specific sidebar content</p>
<% end %>
```

**In layout:**
```erb
<head>
  <%= slotted :head_meta %>
</head>
<body>
  <main><%= yield %></main>
  <aside><%= slotted :sidebar %></aside>
</body>
```

---

## Taxonomies (Tags & Categories)

Built-in: `tags` and `categories` front matter keys.

```markdown
---
tags: [ruby, web, tutorial]
categories: [programming]
---
```

```erb
<!-- List all tags -->
<% site.taxonomy_types.tags.values.each do |tag| %>
  <a href="<%= tag.url %>"><%= tag.label %> (<%= tag.resources.count %>)</a>
<% end %>
```

**Custom taxonomy** in config:
```yaml
taxonomies:
  genre:
    key: genre
    title: Genres
```

---

## Pagination

```yaml
# In collection config
collections:
  posts:
    output: true
    permalink: /blog/:slug/

# In bridgetown.config.yml
pagination:
  enabled: true
  per_page: 10
```

**Index page front matter:**
```markdown
---
layout: default
paginate:
  collection: posts
  per_page: 10
---
```

**In template:**
```erb
<% paginator.resources.each do |post| %>
  <!-- post card -->
<% end %>

<% if paginator.previous_page %>
  <%= link_to "← Newer", paginator.previous_page_path %>
<% end %>
<% if paginator.next_page %>
  <%= link_to "Older →", paginator.next_page_path %>
<% end %>
```

---

## bridgetown.config.yml Reference

```yaml
# Core
url: "https://example.com"
baseurl: ""                    # "" for root, "/subdir" for subfolder
title: My Site
description: Site description

# Build
template_engine: erb           # Default. Options: erb, serbea, liquid
timezone: Europe/Prague        # IANA timezone
permalink: pretty              # URL style: pretty = /slug/, date = /YYYY/MM/DD/slug/

# Exclude from build
exclude:
  - Gemfile
  - README.md
  - "*.sh"

# Content
markdown: kramdown
highlighter: rouge

# Collections
collections:
  projects:
    output: true
    permalink: /projects/:slug/

# Front matter defaults
defaults:
  - scope:
      path: "_posts"
      type: posts
    values:
      layout: post
      author: Default Author
```

---

## Plugins

**Official plugins worth knowing:**
- `bridgetown-seo-tag` — SEO meta tags
- `bridgetown-feed` — RSS/Atom feeds
- `bridgetown-sitemap` — XML sitemap
- `bridgetown-cloudinary` — Image optimization

**Install:**
```bash
# Automation (recommended — installs + configures):
bin/bridgetown apply https://github.com/bridgetownrb/bridgetown-seo-tag

# Manual:
bundle add bridgetown-seo-tag
# Add to config/initializers.rb:
init :"bridgetown-seo-tag"
```

**Local plugins** — place `.rb` files in `plugins/`, they auto-load:
```ruby
# plugins/custom_filter.rb
module CustomFilter
  def upcase_title(input)
    input.upcase
  end
end
Liquid::Template.register_filter(CustomFilter)  # if using Liquid
```

---

## Build & Deploy Reference

| Command | Purpose |
|---------|---------|
| `bin/bridgetown start` | Dev server, live reload, builds frontend |
| `bin/bridgetown build` | Static build only, NO frontend compilation |
| `bin/bridgetown deploy` | Frontend + static build (use for CI/CD) |
| `bin/bridgetown clean` | Wipe output/ and .bridgetown-cache/ |
| `BRIDGETOWN_ENV=production bin/bridgetown deploy` | Production build |

**Output directory:** `output/` — deploy this directory to any static host.

### Cloudflare Pages Setup

| Setting | Value |
|---------|-------|
| Build command | `bin/bridgetown deploy` |
| Output directory | `output` |
| `BRIDGETOWN_ENV` env var | `production` |
| `NODE_VERSION` env var | `22` |
| Ruby version | Via `.ruby-version` file in repo root |

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloudflare Pages
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with:
          bundler-cache: true
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm ci
      - run: BRIDGETOWN_ENV=production bin/bridgetown deploy
      - uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CF_API_TOKEN }}
          accountId: ${{ secrets.CF_ACCOUNT_ID }}
          projectName: my-site
          directory: output
```

---

## Common Gotchas

1. **No front matter = no processing.** Files without `---` are copied as-is.
2. **Tabs in YAML = parse error.** Always use spaces in `bridgetown.config.yml`.
3. **`site.posts` is Jekyll syntax** — use `collections.posts.resources` in Bridgetown v2.
4. **Partials need underscore prefix** — `_nav.erb` not `nav.erb`.
5. **`bin/bridgetown build` skips esbuild** — `asset_path` will return nil. Always use `deploy` for final builds.
6. **`baseurl` must match hosting path** — use `""` for Cloudflare Pages root domain.
7. **ERB files without `.html` extension** — use `.html.erb` for explicit HTML or just `.erb`.
8. **Ruby front matter requires `###ruby` fences**, not YAML dashes.
9. **Collections need `output: true`** to generate individual pages.
10. **Component CSS is auto-bundled** from `src/_components/` — no manual import needed.
