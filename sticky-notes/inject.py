#!/usr/bin/env python3
"""Inject (or refresh) the sticky-notes layer into an HTML file.

    inject.py PAGE.html PAGE_KEY

PAGE_KEY names the localStorage bucket (e.g. krouzitko-domain-model); keep it
stable across republishes so notes survive. Re-running replaces an existing block.
"""
import re, sys, pathlib

if len(sys.argv) != 3:
    sys.exit(__doc__)

page, key = pathlib.Path(sys.argv[1]), sys.argv[2]
if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", key):
    sys.exit("PAGE_KEY: lowercase letters, digits, dashes")

core = (pathlib.Path(__file__).parent / "sticky-notes.js").read_text()
snippet = (f"<!-- ── sticky-notes (skill ~/.claude/skills/sticky-notes): comment on any element in place, export CSS path + text ── -->\n"
           f"<script>\n{core}\nKZStickyNotes.mount({{ key: {key!r} }});\n</script>")
html = page.read_text()

# replace an existing block (marker comment … first </script> after it)
html = re.sub(r"<!-- ── sticky-notes \(skill.*?</script>\n?", "", html, count=1, flags=re.S)

if "</body>" in html:
    html = html.replace("</body>", snippet + "\n</body>", 1)
else:                       # artifact-style fragment without a body tag
    html = html.rstrip("\n") + "\n" + snippet + "\n"

page.write_text(html)
print(f"{page}: sticky-notes injected, key kz-notes:{key}")
