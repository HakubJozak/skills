---
name: bridgetown
description: This skill should be used when working with the Bridgetown static site generator (bridgetownrb.com) — creating new sites, writing content, building components/layouts, configuring the project, and deploying to Cloudflare Pages or other static hosts. Triggers on phrases like "bridgetown site", "bridgetown build", "deploy to Cloudflare Pages", or when editing files in a Bridgetown project (src/, _layouts/, _components/, bridgetown.config.yml).
---

# Bridgetown Skill

Bridgetown (v2.x) is a Ruby-based progressive static site generator. It builds sites from Markdown/ERB content and outputs to the `output/` directory. The **default and recommended template engine is ERB** — avoid Liquid unless maintaining legacy content.

For a comprehensive quick reference, read `references/cheatsheet.md`.

## Project Structure

```
mysite/
├── src/                    # All content and templates
│   ├── _layouts/           # Layout templates (default.erb, post.erb…)
│   ├── _components/        # Reusable components (.erb + optional .rb class)
│   ├── _partials/          # Partial snippets (_name.erb — underscore prefix required)
│   ├── _data/              # YAML/JSON/CSV data files
│   ├── _posts/             # Blog posts: YYYY-MM-DD-title.md
│   └── index.html / *.md  # Pages
├── frontend/
│   ├── javascript/index.js # JS entry point (esbuild)
│   └── styles/index.css    # CSS entry point (PostCSS)
├── config/
│   └── initializers.rb     # Plugin initialization
├── plugins/                # Local Ruby plugins (.rb files, auto-loaded)
├── bridgetown.config.yml
└── Gemfile
```

## Essential Commands

```bash
bin/bridgetown start          # Dev server at localhost:4000 with live reload
bin/bridgetown build          # One-time build → output/ (no frontend compile)
bin/bridgetown deploy         # Build frontend assets + static site (use for production)
bin/bridgetown console        # Interactive Ruby console with site access
bin/bridgetown clean          # Remove output/ and caches
bin/bridgetown plugins list   # List installed plugins
```

**Always use `bin/bridgetown`** (not global `bridgetown`) to ensure the correct gem version is used.

## Deploy to Cloudflare Pages

**Cloudflare Pages dashboard settings:**
- Build command: `bin/bridgetown deploy`
- Build output directory: `output`
- Environment variables:
  - `BRIDGETOWN_ENV` = `production`
  - `NODE_VERSION` = `22`

**`.ruby-version` file** (required in repo root — Cloudflare reads this):
```
3.3.0
```

**Optional `wrangler.toml`:**
```toml
name = "my-site"
pages_build_output_dir = "output"

[vars]
BRIDGETOWN_ENV = "production"
```

**Critical pitfalls for Cloudflare:**
- Use `bin/bridgetown deploy`, NOT `build` — `build` skips esbuild frontend compilation, causing `asset_path` to return nil
- Pin Ruby via `.ruby-version` and Node via `NODE_VERSION` env var; Cloudflare's default image is old
- `baseurl` in config must be `""` for Cloudflare Pages root deployments

## Adding Plugins

```bash
# Manual method
bundle add bridgetown-seo-tag
# Add to config/initializers.rb:
init :"bridgetown-seo-tag"

# Automation method (installs + configures automatically)
bin/bridgetown apply https://github.com/bridgetownrb/bridgetown-seo-tag
```

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `asset_path` returns nil | Frontend not built | Use `bin/bridgetown deploy` not `build` |
| Layout not applied | Missing `layout:` front matter | Add `layout: default` |
| YAML parse error in config | Tabs used | Use spaces only in `bridgetown.config.yml` |
| Collection pages not generated | Missing `output: true` | Add to collection config |
| Partial not found | Missing underscore prefix | Rename `nav.erb` → `_nav.erb` |
| ERB not processed | No front matter | Add `---\n---` triple-dash block |
| Jekyll syntax fails | Bridgetown v2 API differs | Use `collections.posts.resources` not `site.posts` |
| Cloudflare build fails | Wrong Ruby/Node version | Set `.ruby-version` file and `NODE_VERSION` env var |
| baseurl wrong on CF Pages | Non-empty baseurl | Set `baseurl: ""` in config |
