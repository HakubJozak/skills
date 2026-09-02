---
name: sticky-notes
description: Use when Jakub wants to review a page in place — an HTML artifact, a running web app, or a Rails view — by pinning comments to specific elements (diagram labels, table rows, form fields) instead of describing them, or when he pastes back "# Notes on …" Markdown with CSS paths to act on.
---

# Sticky notes

In-place review layer for any web page: a "✎ Notes" mode where clicking an
element pins a draggable, resizable yellow note to it; export gives every note
as **CSS path · quoted element text · nearest heading · comment**. Notes live in
the reviewer's localStorage under `kz-notes:<key>` and re-attach by path on reload.

**Addressing.** Paths climb to the nearest anchor the page already has —
`data-testid`/`data-hq` › `id` (Rails `dom_id`, field ids) › field `name` / form
`action` — then `tag:nth-of-type` below it. No extra markup scheme: a note that
finds no anchor exports as "(unanchored — give the container an id)". Fix those
on demand, on the container only (form, table, card, section); rows and fields
are already covered by `dom_id` and `name`.

Core: `sticky-notes.js` — one IIFE, no dependencies, injects its own CSS,
defines `window.KZStickyNotes = { mount({ key, root }), unmount(), refresh() }`.
`key` defaults to `location.pathname`.

## Three ways in

| target | do |
|---|---|
| HTML file / artifact | `inject.py PAGE.html <page-key>` → publish. Idempotent; handles body-less fragments. |
| any running app, ad hoc | Playwright: `page.addScriptTag({ path: "~/.claude/skills/sticky-notes/sticky-notes.js" })` then `page.evaluate(() => KZStickyNotes.mount())`. Chrome MCP: paste the file into `javascript_tool`, then mount. For Jakub's own clicks: `bookmarklet.py [key] \| wl-copy` → bookmark. |
| Rails app, permanent | `rails/install.sh APP_ROOT` writes a self-contained `sticky_notes_controller.js` (core inlined, works with importmap/vite/esbuild) + `app/views/application/_sticky_notes.html.erb`; add `<%= render "sticky_notes" %>` before `</body>`. Renders in development or with `STICKY_NOTES=1`. |

**Page key.** Artifacts: fixed slug `<project>-<page>` (`krouzitko-domain-model`) —
the artifact viewer changes paths per version, so never key by path. Existing
page → reuse its key (`grep -o 'kz-notes:[a-z0-9-]*' PAGE.html`). Apps: default
pathname is right (notes per record page); pass
`render "sticky_notes", key: "#{controller_path}##{action_name}"` for per-template
notes that follow the reviewer across records.

**Turbo.** The controller mounts into its own element on every visit, unmounts on
`turbo:before-cache` so outlines never land in the snapshot, and re-anchors on
`turbo:frame-render` / `turbo:morph`. Note mode swallows clicks in the capture
phase, so links and submit buttons do not fire while picking an element.

## Reading the export

Jakub pastes:

```
# Notes on Kroužítko
https://krouzitko.oak.hozak.dev/joga/events/12

1. `#event_12 > td:nth-of-type(3)`
   > 14:00–15:30
   under: Events
   show duration, not end time
```

The URL line says which page. Resolve each path against the *current* source
(for Rails: find the view/partial that renders the quoted text — the quote is
the reliable part; nth-of-type paths shift when markup changes). Apply, then
redeploy/republish; notes re-attach where the path still resolves and export as
"(element not found …)" where it does not — mention those.

## What the layer does (so you don't re-implement it)

| action | behaviour |
|---|---|
| ✎ Notes → click element | note anchored at the element's top-left; opens to its left, flips right/below near the viewport edge; mode turns off |
| header drag / corner drag | move / resize; offset and size persisted |
| dotted leader | from note border to the element's top-left dot + numbered badge |
| badge click · – | collapse / expand |
| ✕ | remove (one click); **Clear** removes all (confirm) |
| Copy Markdown / JSON | clipboard + preview pane; URL + title in header; orphaned notes flagged |
| Esc | leave note mode |

Namespace `#kz-*` / `.kz-*`, z-index near max, `all:unset` on controls so host
CSS (Tailwind, Bootstrap) does not leak in. Edit the core, never the generated
controller — re-run `install.sh`.

## Common mistakes

- Injecting an artifact with a key that differs from the previous publish → reviewer's notes "vanish". Look up the key first.
- Marking the Rails controller element `data-turbo-temporary` → Turbo drops it from the restoration snapshot and the bar is gone after Back. Only the layer's own nodes carry that attribute.
- Rebuilding a page so IDs/order change → notes orphaned. Prefer stable `id`s (Rails `dom_id`) on things that get reviewed.
- Sprinkling `data-sticky-notes`/ids everywhere up front → drift and noise. Add an `id` only where an export said "unanchored".
- Answering the export in prose only → apply the changes and redeploy; the export is a change request, not a discussion.
