---
name: typst-editor
description: Edit, create, and compile Typst (.typ) documents. This skill should be used when working with Typst source files, generating PDFs from Typst, needing Typst syntax guidance. Covers markup, scripting, page layout, tables, math, CLI compilation, Emacs setup and visual PDF validation.
---

# Typst Editor

## Overview

This skill provides guidance for editing and creating Typst documents (.typ files), compiling them to PDF/PNG/SVG, and validating the visual output. Typst is a modern typesetting system — a practical alternative to LaTeX with a cleaner syntax.

## Workflow

### Editing a Typst Document

1. Read the existing .typ file to understand its structure, variables, and styling
2. Make edits preserving the document's existing conventions (color scheme, custom functions, formatting patterns)
3. Compile to verify no errors: `typst compile <file>.typ`
4. Validate the visual output (see Visual Validation below)

### Creating a New Typst Document

1. Start with page setup (`#set page(...)`) and text defaults (`#set text(...)`)
2. Define reusable variables and functions at the top of the file
3. Structure content with headings, lists, tables as needed
4. Compile and validate

### Compiling

```bash
# Compile to PDF (default)
typst compile input.typ

# Compile to specific output
typst compile input.typ output.pdf

# Compile specific pages
typst compile --pages 1-3 input.typ

# Compile to PNG (per-page output)
typst compile -f png input.typ "page-{0p}.png"

# Watch for changes and recompile
typst watch input.typ

# Pass input variables
typst compile --input version=2.0 input.typ

# List available fonts
typst fonts
```

Key CLI flags:
- `--root <DIR>` — project root for absolute paths
- `--font-path <DIR>` — additional font directories
- `--ppi <N>` — PPI for PNG export (default: 144)
- `--open` — open output after compilation
- `--pages <PAGES>` — export specific pages (e.g., `1,3-5,8-`)
- `--pdf-standard <STD>` — enforce PDF standard (e.g., `a-2b`, `ua-1`)

## Syntax Quick Reference

For the full syntax and scripting reference, load `references/typst-cheatsheet.md`.

### Markup Essentials

```typst
= Heading 1
== Heading 2
=== Heading 3

*bold*          _italic_          `raw/code`
- bullet item   + numbered item   / Term: description
@label          <label>           #link("url")[text]
\               // line break in markup
~               // non-breaking space
---             // em dash
--              // en dash
...             // ellipsis
```

### Code Mode (prefix with `#`)

```typst
#let x = 42
#let greet(name) = [Hello, #name!]
#if condition [yes] else [no]
#for item in items [#item, ]
#set text(size: 12pt, font: "Liberation Serif")
#show heading.where(level: 1): it => { ... }
#import "other.typ": func
```

### Common Patterns

```typst
// Page setup
#set page(paper: "a4", margin: (left: 2.5cm, right: 2.5cm, top: 3cm, bottom: 3cm))
#set text(font: "Liberation Serif", lang: "cs", size: 11pt)
#set par(justify: true)
#set heading(numbering: "1.")

// Table
#table(
  columns: (auto, 1fr),
  align: (left, right),
  fill: (col, row) => if row == 0 { blue },
  stroke: 0.5pt + gray,
  inset: 10pt,
  table.header([*Col A*], [*Col B*]),
  [Cell 1], [Cell 2],
)

// Colors and boxes
#let my-color = rgb("#2c5f8d")
#rect(width: 100%, fill: luma(240), stroke: 1pt + blue, radius: 4pt, inset: 12pt)[content]

// Images
#image("path/to/image.png", width: 50%)

// Math
$integral_0^infinity f(x) dif x$    // display math
$x^2 + y^2 = r^2$                   // inline math

// Page break
#pagebreak()

// Vertical/horizontal spacing
#v(1em)    #h(1fr)

// Context-dependent content (e.g., page counter)
#context counter(page).display("1 / 1", both: true)
```

## Visual Validation

After compiling a Typst document, always validate the PDF output visually. This is critical because Typst compilation succeeding does NOT guarantee the document looks correct — layout issues, overflow, misaligned tables, and broken styling are only visible in the rendered output.

### Validation Procedure

1. **Compile to PNG** for visual inspection:
   ```bash
   typst compile -f png <file>.typ "/tmp/typst-preview-{0p}.png" --ppi 200
   ```

2. **Read the PNG files** using the Read tool to visually inspect each page. Check for:
   - **Layout** — margins, alignment, spacing between elements
   - **Tables** — column widths, text overflow, header styling, alternating row colors
   - **Typography** — font rendering, sizes, bold/italic applied correctly
   - **Page breaks** — content not cut off, logical page divisions
   - **Headers/footers** — present on every page, correct content
   - **Colors** — fills, strokes, and text colors render as intended
   - **Special characters** — Czech diacritics, currency symbols, math symbols

3. **Report issues** found and fix them in the .typ source, then recompile and re-validate.

### Common Visual Issues

| Issue | Typical Cause | Fix |
|-------|--------------|-----|
| Table text overflow | Column too narrow | Use `1fr` fractional widths |
| Missing diacritics | Font lacks glyphs | Switch font or add `--font-path` |
| Cramped layout | Insufficient spacing | Add `#v()` / adjust `inset` |
| Page number wrong | Counter misconfigured | Check `context counter(page)` usage |
| Header on page 1 | No conditional guard | Use `context` to check page number |
| Broken alignment | Mixed `align` values | Ensure consistent `align` in tables |

### Validation for Specific Changes

- **Price/number changes** — verify the computed values display correctly (Typst evaluates expressions, so check the math)
- **Text content changes** — check for text overflow in fixed-width containers
- **Style changes** — inspect all pages, as style rules cascade globally
- **Table modifications** — verify all rows render, especially after adding/removing rows

## Tips

- Typst uses `kebab-case` for identifiers (e.g., `my-variable`, `format-price`)
- Escape `@` in email addresses with backslash: `jakub.hozak\@gmail.com`
- Use `#h(1fr)` for flexible horizontal space (pushes content apart)
- Use `context` when accessing stateful values like page counters
- `#set` rules are scoped — wrap in `{ }` to limit scope
- `#show` rules transform content globally — place them early in the document
- Arrays use parentheses: `(1, 2, 3)`, single-element needs trailing comma: `(1,)`
- String concatenation uses `+`: `"hello" + " " + "world"`
- Czech language support: `#set text(lang: "cs")` for proper hyphenation
