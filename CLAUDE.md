# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of Claude Skills - folders containing instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. The repository is organized into:

### Custom Skills (Root Directory)
Personal and project-specific skills for development and productivity:
- **YouTrack automation** - Issue management and agile board operations
- **Google Calendar** - Calendar integration and scheduling
- **Browser testing** - Local web application testing
- **Rails tools** - Premailer-rails and RubyGem documentation
- **Infrastructure** - Syncthing, tmux, and slash command management

### Anthropic Skills (_anthropic Directory)
Official Anthropic skills and development utilities:
- **Example skills** (open source, Apache 2.0): Demonstration skills in various categories (creative, development, enterprise)
- **Document skills** (source-available): Production skills for document manipulation (docx, pdf, pptx, xlsx)
- **Skill development utilities**: Scripts for creating, validating, and packaging skills

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

The repository provides two Claude Code plugin marketplaces:

### Custom Skills Marketplace (Root)
Configuration in `.claude-plugin/marketplace.json` with three plugin bundles:
- **development-tools**: YouTrack automation, browser testing, tmux control, slash commands
- **rails-tools**: Premailer-rails configuration, RubyGem documentation
- **productivity-tools**: Google Calendar integration, Syncthing control

Install via:
```
/plugin marketplace add HakubJozak/skills
/plugin install development-tools@hakub-skills
/plugin install rails-tools@hakub-skills
/plugin install productivity-tools@hakub-skills
```

### Anthropic Skills Marketplace (_anthropic)
Configuration in `_anthropic/.claude-plugin/marketplace.json` with two plugin bundles:
- **document-skills**: Excel, Word, PowerPoint, PDF capabilities
- **example-skills**: Collection of demonstration skills

Install via:
```
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

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

### Root Level (Custom Skills)
- `.claude-plugin/marketplace.json` - Custom skills marketplace configuration
- `claude-skill-youtrack/` - YouTrack API automation skill
- `google-calendar-skill/` - Google Calendar integration
- `local-browser-testing/` - Browser automation for local testing
- `premailer-rails/` - Rails email CSS inlining guide
- `rubygem-docs/` - RubyGem documentation fetcher
- `slash-commands/` - Claude Code slash command builder
- `syncthing-control/` - Syncthing REST API controller
- `tmux-control/` - Tmux session management

### _anthropic Directory (Anthropic Skills)
- `_anthropic/.claude-plugin/marketplace.json` - Anthropic marketplace configuration
- `_anthropic/agent_skills_spec.md` - Official specification for skill format
- `_anthropic/skill-creator/` - Meta-skill with comprehensive skill development guidance
- `_anthropic/template-skill/` - Minimal skill template for starting new skills
- `_anthropic/document-skills/` - Production-grade document manipulation skills (source-available)
- `_anthropic/README.md`, `_anthropic/THIRD_PARTY_NOTICES.md` - Anthropic documentation

## Git Configuration

- Main branch: `main`
- Remote: origin (HakubJozak/skills), upstream (anthropics/skills)
- `.gitignore` excludes: `.DS_Store`
