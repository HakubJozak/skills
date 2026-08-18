# Skills Setup on New Machine

Quick reference for setting up hakub-skills on a new machine.

## Prerequisites

- Syncthing should have synced the `~/skills` directory
- Claude Code installed

## Steps

### 1. Add Local Marketplace

```bash
/plugin marketplace add /home/dev/skills
```

This registers your local skills repository as a plugin marketplace.

### 2. Install Skills

**Option A: Install All Skills (Recommended)**
```bash
/plugin install all@hakub-skills
```

**Option B: Install Specific Bundles**
```bash
# Development and infrastructure tools
/plugin install development-tools@hakub-skills

# Ruby on Rails helpers
/plugin install rails-tools@hakub-skills

# Productivity automation
/plugin install productivity-tools@hakub-skills
```

### 3. Install Anthropic Skills

Official Anthropic skills for document processing and examples:

```bash
# Add Anthropic marketplace
/plugin marketplace add anthropics/skills

# Install document processing skills (Excel, Word, PowerPoint, PDF)
/plugin install document-skills@anthropic-agent-skills

# Optional: Install example skills
/plugin install example-skills@anthropic-agent-skills
```

## Verification

After installation:
- Skills should appear in Claude Code
- Test by asking about tmux or calendar
- Skills will respond when their functionality is needed

## Skills Included

Your custom skills:
- **Google Calendar** - Calendar integration and scheduling
- **Browser testing** - Playwright automation for local testing
- **Premailer Rails** - Email CSS inlining guide
- **RubyGem docs** - Fetch Ruby gem documentation
- **Slash commands** - Create custom Claude Code commands
- **Syncthing** - Monitor and control file synchronization
- **tmux** - Manage background processes and sessions

## Troubleshooting

**Skills directory not synced yet?**
- Check Syncthing status
- Verify folder sharing is configured
- Wait for initial sync to complete

**Marketplace not found?**
- Ensure path is correct: `/home/dev/skills`
- Check that directory contains `.claude-plugin/marketplace.json`

**Skills not loading?**
- Restart Claude Code
- Verify plugin installation: check available plugins
- Review Claude Code logs for errors
