# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of Claude Skills - folders containing instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks.

### Custom Skills
Personal skills for development, Rails, and productivity automation:
- **AI Model Intel** (`ai-model-intel/`) - Report on AI model capabilities, costs, and privacy policies
- **Car Picker** (`car-picker/`) - Research Czech car market for family vehicles
- **YouTrack automation** (`claude-skill-youtrack/`) - Issue management and agile board operations
- **Google Calendar** (`google-calendar-skill/`) - Calendar integration and scheduling
- **Browser testing** (`local-browser-testing/`) - Local web application testing with Playwright
- **Playwright Docker** (`playwright-docker/`) - Run Playwright in Docker to avoid browser conflicts
- **Premailer Rails** (`premailer-rails/`) - Rails email CSS inlining configuration guide
- **RubyGem docs** (`rubygem-docs/`) - Fetch and store Ruby gem documentation
- **Slash commands** (`slash-commands/`) - Create and manage Claude Code slash commands
- **Syncthing control** (`syncthing-control/`) - Control and monitor Syncthing file synchronization
- **tmux control** (`tmux-control/`) - Manage tmux sessions for background processes
- **Uptime Kuma** (`uptime-kuma-control/`) - Manage Uptime Kuma monitoring service

### Installing Anthropic Skills

Official Anthropic skills (document processing, skill creation tools, etc.) are maintained separately. Install them directly from the official marketplace:

```bash
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

## Skill Architecture

### Core Structure

Every skill follows the Agent Skills Spec (agent_skills_spec.md):

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required fields: name, description)
│   └── Markdown instructions
└── Optional bundled resources:
    ├── scripts/      - Executable code (Python/Bash/etc.)
    ├── references/   - Documentation loaded as needed
    └── assets/       - Files used in output (templates, icons, etc.)
```

### Progressive Disclosure Pattern

Skills use a three-level loading system to manage context efficiently:

1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words, ideally <500 lines)
3. **Bundled resources** - Loaded as needed by Claude

Keep SKILL.md concise. When approaching 500 lines, split content into reference files and link them from SKILL.md with clear guidance on when to read them.

### YAML Frontmatter Requirements

Required fields:
- `name` - Skill name in hyphen-case (must match directory name)
- `description` - Complete description of what the skill does AND when to use it (this is the primary trigger mechanism)

Optional fields:
- `license` - License information
- `allowed-tools` - Pre-approved tools (Claude Code only)
- `metadata` - Additional key-value pairs

## Skill Development Workflow

### Creating a New Skill

1. **Initialize the skill**:
   ```bash
   /home/dev/skills/_anthropic/skill-creator/scripts/init_skill.py <skill-name> --path /home/dev/skills
   ```
   This creates the skill directory with SKILL.md template and example resource directories.

2. **Implement bundled resources**:
   - Add scripts to `scripts/` (must be tested by running them)
   - Add documentation to `references/`
   - Add templates/assets to `assets/`
   - Delete unused example files

3. **Write SKILL.md**:
   - Use imperative/infinitive form
   - Include "when to use" information in the description field (not in the body)
   - Reference bundled resources clearly
   - Keep under 500 lines; split longer content into references

4. **Package the skill**:
   ```bash
   /home/dev/skills/_anthropic/skill-creator/scripts/package_skill.py /home/dev/skills/<skill-name> [output-dir]
   ```
   This validates and packages the skill into a distributable .skill file (zip with .skill extension).

### Validating a Skill

```bash
/home/dev/skills/_anthropic/skill-creator/scripts/quick_validate.py /home/dev/skills/<skill-name>
```

Validation checks:
- YAML frontmatter format and required fields
- Skill naming conventions and directory structure
- Description completeness
- File organization and resource references

## Plugin Marketplace

This repository provides a personal Claude Code plugin marketplace with four plugin bundles:

Configuration in `.claude-plugin/marketplace.json`:
- **all**: Complete collection (all 8 skills in one command)
- **development-tools**: YouTrack automation, browser testing, tmux control, slash commands
- **rails-tools**: Premailer-rails configuration, RubyGem documentation
- **productivity-tools**: Google Calendar integration, Syncthing control

### Installation

#### On Your Machines (Local Marketplace)
```bash
# Add local marketplace
/plugin marketplace add /home/dev/skills

# Install all skills at once
/plugin install all@hakub-skills

# Or install specific bundles
/plugin install development-tools@hakub-skills
/plugin install rails-tools@hakub-skills
/plugin install productivity-tools@hakub-skills
```

#### Installing Anthropic Skills
```bash
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

## Multi-Machine Setup

This repository uses a hybrid distribution strategy:

### Your Setup
- **Primary Machine**: Edit skills, commit to private GitHub repository
- **Syncthing**: Automatically syncs changes to all your machines
- **Git**: Version control and private backup on GitHub

### On New Machines
1. Wait for Syncthing to sync `/home/dev/skills` directory
2. In Claude Code: `/plugin marketplace add /home/dev/skills`
3. Install skills: `/plugin install all@hakub-skills`
4. (Optional) Install Anthropic skills as shown above

See `SETUP.md` for detailed new machine setup instructions.

## Key Design Principles

### Concise is Key

Context window is a public good. Only add context Claude doesn't already have. Challenge each piece of information: "Does Claude really need this explanation?"

### Avoid Duplication

Information should live in either SKILL.md or reference files, not both. Prefer reference files for detailed information to keep SKILL.md lean.

### Set Appropriate Degrees of Freedom

- **High freedom** (text instructions): Multiple valid approaches, context-dependent decisions
- **Medium freedom** (pseudocode with parameters): Preferred pattern exists, some variation acceptable
- **Low freedom** (specific scripts): Operations are fragile, consistency is critical

### No Extraneous Documentation

Skills should only contain files that directly support functionality. Do NOT create:
- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md

Skills are for AI agents, not human documentation.

## Important Files and Directories

### Repository Files
- `.claude-plugin/marketplace.json` - Marketplace configuration (4 plugin bundles)
- `CLAUDE.md` - This file (AI-readable documentation)
- `SETUP.md` - Quick reference for new machine setup
- `.gitignore` - Git exclusions

### Custom Skills (12 Skills)
- `ai-model-intel/` - AI model capabilities, costs, and privacy intelligence
- `car-picker/` - Czech car market research for family vehicles
- `claude-skill-youtrack/` - YouTrack API automation skill
- `google-calendar-skill/` - Google Calendar integration
- `local-browser-testing/` - Browser automation for local testing
- `playwright-docker/` - Playwright in Docker containers
- `premailer-rails/` - Rails email CSS inlining guide
- `rubygem-docs/` - RubyGem documentation fetcher
- `slash-commands/` - Claude Code slash command builder
- `syncthing-control/` - Syncthing REST API controller
- `tmux-control/` - Tmux session management
- `uptime-kuma-control/` - Uptime Kuma monitoring management

### Anthropic Skills (External)
Install separately from official marketplace: `/plugin marketplace add anthropics/skills`

## Git Configuration

- Main branch: `main`
- Remote: origin (HakubJozak/skills), upstream (anthropics/skills)
- `.gitignore` excludes: `.DS_Store`
