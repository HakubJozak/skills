---
name: slash-commands
description: "Create, edit, and organize Claude Code slash commands. Use when the user requests: (1) Creating a new slash command, (2) Editing existing slash commands, (3) Help with command structure or best practices, (4) Organizing commands by scope (project/user/global), or (5) Automating workflows with custom commands."
---

# Slash Commands Builder

Create and manage custom slash commands for Claude Code to automate workflows and standardize team processes.

## Quick Start

**Project commands** (shared with team via git):
```
.claude/commands/command-name.md
```

**Personal commands** (available across all your projects):
```
~/.claude/commands/command-name.md
```

## Creating Commands

### 1. Choose Command Pattern

**Simple Command** - Single-purpose prompt with no arguments:
- Use for: Code reviews, explanations, formatting tasks
- Example: `/review` - Review code for security and performance
- Template: `assets/simple-command.md`

**Parameterized Command** - Accepts arguments for flexibility:
- Use for: Issue-specific tasks, dynamic workflows
- Arguments: `$1`, `$2`, etc. for individual args, or `$ARGUMENTS` for all args
- Example: `/fix-issue 123 high alice` - Fix issue with priority and assignee
- Template: `assets/parameterized-command.md`

**Bash-Executing Command** - Gathers context via bash before task:
- Use for: Git workflows, status-dependent tasks, context gathering
- Requires: `allowed-tools` frontmatter with explicit bash permissions
- Example: `/commit` - Create commit based on current git status
- Template: `assets/bash-command.md`

### 2. Write Command File

Create `.md` file with optional YAML frontmatter:

```markdown
---
description: Brief description (required for SlashCommand tool)
argument-hint: [optional] [args]
allowed-tools: Bash(command:*), Bash(other:*)
model: claude-3-5-haiku-20241022
---

# Command Instructions

Clear instructions for Claude on what to execute.
```

### 3. Choose Command Scope

**Project scope** - `.claude/commands/`
- Shared with team via version control
- Shows as "(project)" in `/help`
- Overrides personal commands with same name

**Personal scope** - `~/.claude/commands/`
- Personal to your account across all projects
- Shows as "(user)" in `/help`

**Namespacing** - Use subdirectories to organize:
```
.claude/commands/
├── frontend/component.md  → /component (project:frontend)
└── backend/test.md        → /test (project:backend)
```

## Frontmatter Reference

All fields are optional:

| Field | Purpose | Example |
|-------|---------|---------|
| `description` | Brief description (enables SlashCommand tool) | `"Review code for security"` |
| `argument-hint` | Arguments hint for autocomplete | `"[issue-number] [priority]"` |
| `allowed-tools` | Restrict to specific bash commands | `"Bash(git add:*), Bash(git status:*)"` |
| `model` | Use specific model for this command | `"claude-3-5-haiku-20241022"` |
| `disable-model-invocation` | Prevent auto-execution via SlashCommand tool | `true` |

## Advanced Features

### File References

Include file contents with `@` prefix:

```markdown
Review the implementation in @src/utils/helpers.js

Compare @src/old-version.js with @src/new-version.js
```

### Bash Command Execution

Use `!` prefix to execute bash before running command:

```markdown
---
allowed-tools: Bash(git status:*), Bash(git diff:*)
---

## Current Status
!`git status`

## Changes
!`git diff HEAD`

Create a commit based on the above changes.
```

**Security**: Must explicitly list allowed bash commands in `allowed-tools`.

### Extended Thinking

Include extended thinking keywords to trigger deeper reasoning for complex tasks.

## Best Practices

1. **Descriptive names** - Match command name to purpose (`/review`, `/fix-issue`)
2. **Required descriptions** - Include `description` frontmatter for SlashCommand tool discoverability
3. **Document arguments** - Use `argument-hint` to show expected parameters
4. **Restrict tools** - Only allow necessary bash commands via `allowed-tools`
5. **Organize with directories** - Group related commands in subdirectories
6. **Keep simple** - Single file, focused purpose (complex workflows → use Skills instead)
7. **Version control** - Store project commands in `.claude/commands/` for team sharing

## Slash Commands vs Skills

**Use Slash Commands for:**
- Quick, frequently used prompts
- Simple prompt snippets in one file
- Examples: `/review`, `/explain`, `/commit`

**Use Skills for:**
- Complex workflows with multiple steps
- Knowledge organized across multiple files
- Team workflows requiring structure and resources
- Examples: PDF processing, data analysis workflows

## Template Files

Copy and customize from `assets/`:
- `simple-command.md` - Basic single-purpose command
- `parameterized-command.md` - Command with arguments
- `bash-command.md` - Command that executes bash for context
