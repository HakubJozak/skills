# Typst Complete Cheat Sheet

## Three Modes

Typst has three syntactic modes:
- **Markup mode** — default; write prose, headings, lists
- **Code mode** — enter with `#`; write logic, variables, function calls
- **Math mode** — enter with `$...$`; write equations

Switch between modes:
- Markup → Code: `#expression`
- Code → Markup: `[markup content]`
- Markup/Code → Math: `$...$`

---

## Markup Syntax

### Text Formatting

| Syntax | Result | Function |
|--------|--------|----------|
| `*bold*` | **bold** | `strong` |
| `_italic_` | _italic_ | `emph` |
| `` `code` `` | `code` | `raw` |
| `"smart quotes"` | "smart quotes" | `smartquote` |
| `'single quotes'` | 'single quotes' | `smartquote` |

### Headings

```typst
= Level 1
== Level 2
=== Level 3
==== Level 4
```

### Lists

```typst
- Bullet item          // unordered list
  - Nested item        // indent with 2 spaces
- Another item

+ Numbered item        // ordered list
+ Another item
  + Nested numbered

/ Term: Definition     // term/description list
/ Another: Its def
```

### Links and References

```typst
https://example.com                    // auto-detected URL
#link("https://example.com")[label]    // labeled link
#link("mailto:a@b.com")               // mailto link

<my-label>                             // define label
@my-label                              // reference a label
```

### Special Characters

| Syntax | Output | Description |
|--------|--------|-------------|
| `\` | line break | |
| `~` | non-breaking space | |
| `---` | em dash (—) | |
| `--` | en dash (–) | |
| `...` | ellipsis (…) | |
| `\#` | literal # | escape special chars |
| `\*` | literal * | |
| `\\` | literal \ | |
| `\u{1f600}` | unicode char | |

### Comments

```typst
// Line comment
/* Block
   comment */
```

### Raw Text / Code Blocks

````typst
`inline raw`

```python
def hello():
    print("world")
```

```typ
#let x = 1   // syntax highlighted Typst
```
````

---

## Code Mode (Scripting)

### Variables

```typst
#let name = "value"
#let x = 42
#let colors = (red, green, blue)       // array
#let config = (width: 100, height: 50) // dictionary
#let (a, b) = (1, 2)                   // destructuring
#let (first, .., last) = array         // spread destructuring
```

### Data Types

| Type | Literal | Examples |
|------|---------|----------|
| None | `none` | |
| Boolean | `true`, `false` | |
| Integer | `10`, `0xff`, `0o77`, `0b1010` | |
| Float | `3.14`, `1e5`, `float.inf` | |
| String | `"hello"` | |
| Length | `1pt`, `2mm`, `3cm`, `4in`, `5em` | |
| Angle | `90deg`, `1rad` | |
| Ratio | `50%` | |
| Fraction | `1fr`, `2fr` | layout fractions |
| Color | `red`, `rgb("#abc")`, `luma(200)` | |
| Array | `(1, 2, 3)` | single: `(1,)` |
| Dictionary | `(key: "val")` | |
| Content | `[*hello*]` | |

### Operators

| Precedence | Operators | Description |
|------------|-----------|-------------|
| 7 | `-x`, `+x` | Unary negation/plus |
| 6 | `*`, `/` | Multiply, divide |
| 5 | `+`, `-` | Add, subtract |
| 4 | `==`, `!=`, `<`, `<=`, `>`, `>=` | Comparison |
| 4 | `in`, `not in` | Membership |
| 3 | `not` | Logical NOT |
| 3 | `and` | Logical AND (short-circuit) |
| 2 | `or` | Logical OR (short-circuit) |
| 1 | `=`, `+=`, `-=`, `*=`, `/=` | Assignment |

### Functions

```typst
// Named function
#let double(x) = x * 2

// With default argument
#let greet(name, greeting: "Hello") = [#greeting, #name!]

// Lambda / closure
#let transform = (x) => x * 2

// Calling with content body
#greet[World]            // equivalent to greet([World])

// Variadic via array spreading
#let f(..args) = args.pos()
```

### Control Flow

```typst
// Conditional
#if x > 0 [positive] else if x < 0 [negative] else [zero]

// For loop
#for item in (1, 2, 3) [#item, ]
#for (key, val) in dict [#key: #val]
#for i in range(5) [#i ]

// While loop
#while x < 10 { x += 1 }

// Loop control
#for x in items {
  if x == none { continue }
  if x == "stop" { break }
  [#x]
}
```

### String Methods

```typst
"hello".len()           // 5
"hello".contains("ell") // true
"hello".starts-with("h")
"hello".ends-with("o")
"hello".upper()         // "HELLO"
"hello".lower()
"a,b,c".split(",")     // ("a", "b", "c")
"hello".slice(1, 3)     // "el"
"  hi  ".trim()         // "hi"
"hello".replace("l", "r") // "herro"
str(42)                 // "42"
```

### Array Methods

```typst
let a = (1, 2, 3)
a.len()                 // 3
a.at(0)                 // 1
a.push(4)               // modifies in place
a.pop()                 // removes and returns last
a.first()               // 1
a.last()                // 3
a.contains(2)           // true
a.filter(x => x > 1)   // (2, 3)
a.map(x => x * 2)      // (2, 4, 6)
a.join(", ")            // "1, 2, 3"
a.sorted()
a.rev()
a.flatten()
a.zip((4, 5, 6))       // ((1,4), (2,5), (3,6))
a.enumerate()           // ((0,1), (1,2), (2,3))
a.fold(0, (acc, x) => acc + x) // 6
range(5)                // (0, 1, 2, 3, 4)
range(1, 10, step: 2)  // (1, 3, 5, 7, 9)
```

### Dictionary Methods

```typst
let d = (name: "Alice", age: 30)
d.name                  // "Alice"  (field access)
d.at("name")            // "Alice"  (method access)
d.keys()                // ("name", "age")
d.values()              // ("Alice", 30)
d.pairs()               // (("name","Alice"), ("age",30))
d.len()                 // 2
d.insert("key", "val")
d.remove("key")
```

### Modules and Imports

```typst
#include "chapter.typ"                    // insert content from file
#import "utils.typ"                       // import as module
#import "utils.typ": helper, format-price // import specific items
#import "utils.typ": *                    // import everything
#import "utils.typ" as u                  // import with alias
#import "@preview/tablex:0.0.8": tablex   // community package
```

---

## Set and Show Rules

### Set Rules (configure elements)

```typst
// Global — affects all subsequent content
#set text(font: "Liberation Serif", size: 11pt, lang: "cs")
#set page(paper: "a4", margin: 2.5cm)
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.")

// Scoped — only affects content inside block
#{
  set text(fill: red)
  [This is red.]
}
[This is not red.]
```

### Show Rules (transform elements)

```typst
// Simple replacement
#show "TODO": text(fill: red)[*TODO*]

// Transform by element type
#show heading: it => {
  set text(fill: blue)
  it
  line(length: 100%, stroke: 1pt + blue)
}

// Filter by level/field
#show heading.where(level: 1): it => {
  set text(size: 18pt, weight: "bold")
  v(1em)
  it
  v(0.5em)
}

// Transform raw blocks
#show raw.where(block: true): it => {
  rect(fill: luma(240), radius: 3pt, inset: 8pt, it)
}
```

---

## Page Layout

### Page Setup

```typst
#set page(
  paper: "a4",              // or "us-letter", "a5", etc.
  // width: 21cm,           // custom dimensions
  // height: 29.7cm,
  flipped: false,           // landscape if true
  margin: (
    left: 2.5cm,
    right: 2.5cm,
    top: 3cm,
    bottom: 3cm,
  ),
  columns: 1,               // multi-column layout
  fill: white,              // page background
  numbering: "1",           // page numbering pattern
  header: [...],
  footer: [...],
)
```

### Header and Footer

```typst
#set page(
  header: context {
    set text(size: 9pt, fill: gray)
    [Document Title]
    h(1fr)
    [Page #counter(page).display()]
  },
  footer: context {
    line(length: 100%, stroke: 0.5pt + gray)
    v(-0.3em)
    align(center, text(size: 8pt)[Footer text])
  },
)
```

### Layout Functions

```typst
#align(center)[centered content]
#align(left + top)[top-left]
#h(1fr)                 // flexible horizontal space
#v(2em)                 // vertical space
#pagebreak()            // force page break
#colbreak()             // force column break
#block(width: 100%)[…]  // block-level container
#box[…]                 // inline container
#pad(left: 1em)[…]     // padding

// Grid layout
#grid(
  columns: (1fr, 2fr),
  gutter: 10pt,
  [Left], [Right],
)

// Stack
#stack(dir: ltr, spacing: 5pt, [A], [B], [C])
```

---

## Tables

```typst
#table(
  columns: (auto, 1fr, 1fr),        // column widths
  rows: auto,                        // row heights
  align: (left, center, right),      // per-column alignment
  fill: (col, row) => {              // conditional fill
    if row == 0 { blue }
    else if calc.rem(row, 2) == 0 { luma(240) }
  },
  stroke: 0.5pt + gray,             // border style
  inset: 10pt,                       // cell padding

  // Header row (repeats on page breaks)
  table.header(
    [#text(fill: white, weight: "bold")[Header 1]],
    [#text(fill: white, weight: "bold")[Header 2]],
    [#text(fill: white, weight: "bold")[Header 3]],
  ),

  // Data rows
  [Cell 1], [Cell 2], [Cell 3],
  [Cell 4], [Cell 5], [Cell 6],

  // Horizontal line
  table.hline(stroke: 2pt + blue),

  // Footer/summary row
  [*Total*], [], [*100*],
)
```

### Table Column Widths

- `auto` — fit to content
- `1fr`, `2fr` — fractional (like CSS flex)
- `5cm`, `100pt` — fixed width
- Mix: `(auto, 1fr, 2fr, 100pt)`

---

## Math Mode

```typst
// Inline math (no spaces around $)
The equation $x^2 + y^2 = r^2$ is a circle.

// Display math (spaces around $)
$ integral_0^infinity e^(-x) dif x = 1 $

// Common symbols
$alpha, beta, gamma, delta, epsilon$
$sum, product, integral$
$arrow.r, arrow.l, arrow.r.long$
$<=, >=, !=, approx, equiv$
$times, dot, plus.minus$

// Fractions
$(a + b) / c$

// Alignment (for multi-line equations)
$ x &= 2 + 3 \
    &= 5 $

// Matrices
$ mat(1, 2; 3, 4) $

// Cases
$ f(x) = cases(
  0 &"if" x < 0,
  1 &"if" x >= 0,
) $

// Text in math
$ "if" x > 0 $
```

---

## Colors

```typst
// Named colors
red, green, blue, black, white, gray, orange, yellow, purple

// RGB
rgb("#2c5f8d")
rgb("#abc")                // shorthand
rgb(44, 95, 141)           // decimal

// Grayscale
luma(200)                  // 0 = black, 255 = white

// Modifiers
blue.lighten(50%)
blue.darken(20%)
white.transparentize(40%)
gray.darken(20%)

// Gradient
gradient.linear(red, blue)
```

---

## Images and Figures

```typst
#image("photo.png")
#image("diagram.svg", width: 80%)
#image("chart.png", height: 5cm)

#figure(
  image("chart.png", width: 70%),
  caption: [Monthly sales data],
) <fig-sales>

See @fig-sales for details.
```

---

## Calc Module

```typst
calc.abs(-5)       // 5
calc.round(3.7)    // 4
calc.floor(3.7)    // 3
calc.ceil(3.2)     // 4
calc.min(1, 2)     // 1
calc.max(1, 2)     // 2
calc.pow(2, 10)    // 1024
calc.sqrt(16)      // 4
calc.rem(7, 3)     // 1  (modulo)
calc.log(100)      // 2 (base 10)
calc.round(3.456, digits: 2) // 3.46
```

---

## CLI Reference (typst 0.14)

### Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `typst compile <input>` | `typst c` | Compile to PDF/PNG/SVG/HTML |
| `typst watch <input>` | `typst w` | Watch and recompile on changes |
| `typst init <template>` | | Initialize project from template |
| `typst query <input>` | | Extract metadata |
| `typst fonts` | | List available fonts |
| `typst info` | | Show debugging info |

### Compile Options

```bash
# Output formats
typst compile doc.typ                        # PDF (default)
typst compile -f png doc.typ "out-{0p}.png"  # PNG per page
typst compile -f svg doc.typ "out-{0p}.svg"  # SVG per page
typst compile -f html doc.typ out.html       # HTML (experimental)

# Specific pages
typst compile --pages 1,3-5 doc.typ

# Quality
typst compile --ppi 300 -f png doc.typ out.png  # high-res PNG

# Input variables (accessible via sys.inputs)
typst compile --input key=value doc.typ

# Font paths
typst compile --font-path /path/to/fonts doc.typ

# Open after compile
typst compile --open doc.typ

# PDF standards
typst compile --pdf-standard a-2b doc.typ
typst compile --pdf-standard ua-1 doc.typ    # accessibility

# Performance
typst compile -j 4 doc.typ                   # parallel jobs
```

### Watch Options

```bash
typst watch doc.typ                 # recompile on change
typst watch doc.typ --open          # open and keep updating
typst watch -f html doc.typ        # HTML with live reload
typst watch --port 3000 doc.typ    # custom port for HTML
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `TYPST_ROOT` | Project root directory |
| `TYPST_FONT_PATHS` | Additional font directories (colon-separated) |
| `TYPST_PACKAGE_PATH` | Custom local package path |
| `TYPST_PACKAGE_CACHE_PATH` | Custom package cache path |
| `TYPST_CERT` | Custom CA certificate for network requests |
| `SOURCE_DATE_EPOCH` | Document creation timestamp |
| `TYPST_FEATURES` | Enable experimental features (`html`, `a11y-extras`) |

### Page Number Templates (PNG/SVG)

| Placeholder | Description |
|-------------|-------------|
| `{p}` | Page number |
| `{0p}` | Zero-padded page number |
| `{t}` | Total page count |

Example: `typst compile -f png doc.typ "page-{0p}-of-{t}.png"`
