---
name: rubygem-docs
description: Fetch and store Ruby gem documentation in AI-friendly markdown. Use when you need gem documentation, API reference, or usage examples for any RubyGem.
---

# RubyGem Documentation for AI

Fetches, extracts, and stores Ruby gem documentation in AI-friendly markdown format. Use this skill when:
- You need documentation for a Ruby gem that isn't in your training data
- The user asks to fetch/update gem docs
- You need API reference or usage examples for a gem

## Quick Usage

```bash
# Fetch docs for a gem (stores in doc/gems/<gemname>.md)
~/.claude/skills/rubygem-docs/fetch-gem-docs.rb <gemname>

# Examples:
~/.claude/skills/rubygem-docs/fetch-gem-docs.rb sidekiq
~/.claude/skills/rubygem-docs/fetch-gem-docs.rb http
~/.claude/skills/rubygem-docs/fetch-gem-docs.rb ruby_llm
```

## What the Script Fetches

The `fetch-gem-docs.rb` script automatically discovers and fetches documentation from multiple sources:

### 1. GitHub Wiki (Primary - Most Comprehensive)

Many gems have extensive documentation in their GitHub wiki. The script:
- Detects wiki presence via raw.githubusercontent.com
- Parses the Home page to discover all wiki pages
- Fetches each page and combines into single markdown

Example: http.rb wiki has 17+ pages covering Making Requests, Timeouts, Cookies, HTTPS, etc.

### 2. agent-context Files

Some gems ship with dedicated AI context files in a `context/` directory. The script checks for these and includes them.

Gems with agent-context: async, decode, falcon, sus (growing list).

### 3. GitHub README

Falls back to README if no wiki exists. Handles both .md and .rdoc formats.

### 4. Local Gem Documentation

From the installed gem directory:
- `examples/` - Ruby example files
- `doc/` or `docs/` - Additional markdown docs
- `CHANGELOG.md` - Recent changes (first 80 lines)

### 5. YARD API Docs

If `yardoc` is available, generates API documentation from source.

## Output Format

Generated docs are saved to `doc/gems/<gemname>.md`:

```markdown
# <GemName> Documentation

> **Version:** x.y.z | **License:** MIT
> **Homepage:** https://github.com/...

[Summary from gemspec]

## Documentation
[All wiki pages combined]

### Page Title
[Page content...]

## Examples
[From examples/ directory]

## Changelog (Recent)
[First 80 lines of CHANGELOG]
```

## Manual Documentation Sources

### llm-docs-builder

Transform web documentation to AI-friendly format:

```bash
gem install llm-docs-builder

# Transform a single URL
llm-docs-builder transform -u https://docs.example.com/guide -o doc/gems/guide.md
```

### ri (Ruby Documentation)

For quick method lookups:

```bash
ri HTTP::Client#get
ri Sidekiq::Worker
```

### Local Gem Files

```bash
# Find gem location
bundle info <gemname> --path

# Browse docs
ls $(bundle info <gemname> --path)
```

## Tips

1. **Check doc/gems/ first** - docs may already be fetched
2. **Refresh when upgrading** - run script after `bundle update <gem>`
3. **Wiki is gold** - most popular gems have extensive wiki docs
4. **Combine sources** - use ri for method signatures, wiki for examples
