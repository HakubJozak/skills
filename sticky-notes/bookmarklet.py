#!/usr/bin/env python3
"""Print the sticky-notes layer as a bookmarklet for any running web app.

    bookmarklet.py [PAGE_KEY] | wl-copy     # no key → notes keyed by location.pathname

Paste the javascript: URL into a bookmark; click it on the page to review.
"""
import pathlib, sys
from urllib.parse import quote

key = sys.argv[1] if len(sys.argv) > 1 else None
core = (pathlib.Path(__file__).parent / "sticky-notes.js").read_text()
opts = f"{{ key: {key!r} }}" if key else "{}"
print("javascript:" + quote(f"(()=>{{{core}\nKZStickyNotes.mount({opts});}})()", safe=""))
