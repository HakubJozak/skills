---
name: commit
version: 1.0.0
description: "Commit changes using the Conventional Commits specification (v1.0.0). Use for: committing code, writing commit messages, staging and committing files, splitting changes into logical commits. Ensures commit messages follow the format: type(scope): description, with support for breaking changes, multi-paragraph bodies, and git-trailer footers."
author: Jakub Hozak
allowed-tools: Bash(git *)
---

# Conventional Commits Skill

Write commit messages following the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) specification.

## Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Types

| Type | When to use |
|------|-------------|
| `feat` | A new feature (correlates with SemVer MINOR) |
| `fix` | A bug fix (correlates with SemVer PATCH) |
| `docs` | Documentation-only changes |
| `style` | Formatting, whitespace, semicolons — no code logic change |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `build` | Changes to build system or external dependencies |
| `ci` | CI configuration and scripts |
| `chore` | Other changes that don't modify src or test files |

## Rules

1. **Type is mandatory.** Pick the most specific type from the table above.
2. **Scope is optional.** A noun in parentheses describing the section of the codebase: `feat(parser):`, `fix(api):`.
3. **Description is mandatory.** Lowercase, imperative mood, no trailing period. Follows the colon and a single space.
4. **Body is optional.** Separated from description by a blank line. Free-form, may contain multiple paragraphs.
5. **Footers are optional.** Separated from body by a blank line. Use git-trailer format: `Token: value` or `Token #value`. Tokens use hyphens for spaces (`Reviewed-by`, not `Reviewed by`).
6. **Breaking changes:**
   - Append `!` after type/scope: `feat(api)!: remove endpoint`
   - And/or add a footer: `BREAKING CHANGE: description of what broke`
   - `BREAKING CHANGE` must be uppercase. `BREAKING-CHANGE` is synonymous.
   - Correlates with SemVer MAJOR.
7. Breaking changes can accompany any type.

## Workflow

1. Run `git status` and `git diff --stat` to understand what changed.
2. Group related changes into logical commits — each commit should represent one coherent change.
3. If you encounter changes you did not author, warn the user but do not discard them.
4. Stage files for each logical group and commit with a well-formed message.
5. Use a HEREDOC to pass the commit message for correct formatting.
6. After committing, run `git status` to verify.

## Examples

```
feat(lang): add Polish language support
```

```
fix(api): handle null response from upstream

The upstream service occasionally returns null instead of an empty
array. Guard against this to prevent TypeError in the mapper.

Reviewed-by: Alice
Refs: #123
```

```
refactor!: drop support for Node 14

BREAKING CHANGE: Node 14 reached EOL and is no longer tested in CI.
Minimum supported version is now Node 18.
```
