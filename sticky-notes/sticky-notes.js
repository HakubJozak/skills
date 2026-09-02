/* sticky-notes — in-place review layer (skill ~/.claude/skills/sticky-notes).
   Loads anywhere: inlined in an HTML file, pasted in a console, bookmarklet,
   Stimulus controller. Defines
     window.KZStickyNotes = { mount({ key, root }), unmount(), refresh() }
   ✎ Notes → click an element → yellow note pinned to it (drag by header,
   resize from corner, dotted leader). Export = CSS path · element text ·
   comment. Notes persist in localStorage under "kz-notes:<key>";
   key defaults to location.pathname — pass a fixed one where paths change
   between versions (artifact viewer). */
(() => {
  const STYLE = `
#kz-notes-bar{position:fixed;right:16px;bottom:16px;z-index:2147482930;display:flex;gap:6px;align-items:center;background:var(--card,#fff);color:var(--ink,#1e2430);border:1px solid var(--line,#c8ccd4);padding:6px 8px;box-shadow:0 4px 16px rgba(0,0,0,.15);font:12px "IBM Plex Mono",ui-monospace,Menlo,monospace}
#kz-notes-bar button{all:unset;cursor:pointer;padding:6px 10px;border:1px solid var(--line,#c8ccd4);font:inherit;line-height:1;white-space:nowrap}
#kz-notes-bar button:hover{background:rgba(0,0,0,.06)}
#kz-notes-bar button[aria-pressed=true]{background:#e0b400;color:#1e2430;border-color:#e0b400}
#kz-notes-bar .count{opacity:.6;min-width:3ch;text-align:center}
body.kz-noting, body.kz-noting *{cursor:crosshair !important}
.kz-hover{outline:2px dashed #e0b400 !important;outline-offset:2px}
.kz-noted{outline:2px solid #e0b400 !important;outline-offset:2px}
#kz-leader{position:absolute;left:0;top:0;z-index:2147482900;pointer-events:none;overflow:visible}
.kz-note{position:absolute;z-index:2147482920;width:240px;height:110px;min-width:160px;min-height:72px;display:flex;flex-direction:column;box-sizing:border-box;resize:both;overflow:hidden;margin:0;
  background:#fff3b0;color:#1e2430;border:1px solid #d9b93c;border-radius:0;box-shadow:2px 3px 0 rgba(0,0,0,.18);padding:6px 8px 8px;font:12px/1.4 "IBM Plex Sans",system-ui,sans-serif;text-align:left}
.kz-note[hidden],#kz-notes-out[hidden]{display:none !important}
.kz-note.kz-dragging{box-shadow:6px 8px 0 rgba(0,0,0,.22);opacity:.95}
.kz-note header{display:flex;align-items:center;gap:6px;margin:0 0 4px;padding:0;font:600 11px "IBM Plex Mono",ui-monospace,Menlo,monospace;color:#6b5a12;cursor:grab;user-select:none;touch-action:none}
.kz-note.kz-dragging header{cursor:grabbing}
.kz-note header b{background:#1e2430;color:#fff3b0;border-radius:9px;padding:0 6px;font:inherit}
.kz-note header code{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font:inherit;font-size:10px;background:none;color:inherit;padding:0}
.kz-note header button{all:unset;color:#6b5a12;padding:0 4px;cursor:pointer;font-size:14px;line-height:18px}
.kz-note header button[data-a=del]{font-weight:700;border:1px solid transparent}
.kz-note header button[data-a=del]:hover{color:#fff;background:#b3261e;border-color:#b3261e}
.kz-note textarea{all:unset;display:block;flex:1;width:100%;box-sizing:border-box;min-height:0;color:inherit;font:inherit;white-space:pre-wrap;overflow:auto}
.kz-badge{position:absolute;z-index:2147482910;background:#1e2430;color:#fff3b0;font:700 10px "IBM Plex Mono",ui-monospace,Menlo,monospace;border-radius:9px;padding:0 5px;line-height:16px;cursor:pointer}
#kz-notes-out{position:fixed;left:16px;right:16px;bottom:64px;max-height:40vh;overflow:auto;z-index:2147482930;margin:0;background:var(--card,#fff);color:var(--ink,#1e2430);border:1px solid var(--line,#c8ccd4);padding:12px;font:12px "IBM Plex Mono",ui-monospace,Menlo,monospace;white-space:pre-wrap;text-align:left}
`;
  const T = { mode: "✎ Notes", md: "Copy Markdown", json: "Copy JSON", clear: "Clear", copied: "copied", remove: "remove note", orphan: "(element not found on this version of the page)", unanchored: "(unanchored — give the container an id)" };
  const DEFAULT = { dx: -264, dy: -8, w: 240, h: 110 };  // offset from the element's top-left corner: note sits to the left
  const OURS = "#kz-notes-bar, #kz-notes-out, .kz-note, .kz-badge, #kz-leader";

  let S = null;   // mounted state; null when unmounted

  // ── css path: climbs to the nearest strong anchor the page already has
  //   testid/hq selector > id > field name / form action, then tag:nth-of-type below it.
  //   Weak segments (data-controller, landmarks) only make the path readable.
  //   `anchored` = false → pure nth-of-type chain → give the container an id.
  const GENERATED_ID = /^(?:[0-9a-f-]{20,}|radix-|headlessui-|mui-|react-|:)/i;
  const LANDMARK = /^(nav|main|form|table|section|article|header|footer|aside|dialog|fieldset)$/;
  const attr = (name, v) => `[${name}="${v.replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"]`;
  function segment(el) {
    const tag = el.tagName.toLowerCase();
    const siblings = [...el.parentNode.children].filter((c) => c.tagName === el.tagName);
    const unique = (q) => siblings.filter((c) => c.matches(q)).length === 1;
    const weak = [["name", el.name], ["action", el.getAttribute("action")], ["data-controller", el.dataset.controller]].find(([n, v]) => v && unique(tag + attr(n, v)));
    if (weak) return tag + attr(...weak);
    return siblings.length > 1 ? `${tag}:nth-of-type(${siblings.indexOf(el) + 1})` : tag;
  }
  function cssPath(el) {
    const parts = [];
    let anchored = false;
    while (el && el.nodeType === 1 && el !== document.body) {
      const test = ["data-testid", "data-hq"].find((a) => el.getAttribute(a));
      const id = el.id && !GENERATED_ID.test(el.id) && document.querySelectorAll("#" + CSS.escape(el.id)).length === 1 && el.id;
      if (test || id) { parts.unshift(test ? attr(test, el.getAttribute(test)) : "#" + CSS.escape(id)); anchored = true; break; }
      const seg = segment(el);
      anchored ||= /\[(name|action)=/.test(seg);
      parts.unshift(seg);
      el = el.parentNode;
    }
    return { path: parts.join(" > "), anchored };
  }
  // nearest preceding heading/caption/legend = where the reviewer was looking
  function contextOf(el) {
    let ctx = "";
    for (const h of document.querySelectorAll("h1,h2,h3,h4,caption,legend")) {
      if (h.closest(OURS)) continue;
      if (h.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING) ctx = (h.innerText || "").trim().replace(/\s+/g, " ").slice(0, 80);
    }
    return ctx;
  }
  // form controls have no text — fall back to what the reviewer sees
  const labelOf = (el) => (el.id && document.querySelector(`label[for="${CSS.escape(el.id)}"]`)?.innerText) || el.closest("label")?.innerText || "";
  const excerpt = (el) => (el.innerText || el.value || labelOf(el) || el.getAttribute("aria-label") || el.getAttribute("placeholder") || el.alt || el.textContent || "")
    .trim().replace(/\s+/g, " ").slice(0, 120);
  // element's top-left corner in document coordinates = the anchor
  function anchorOf(el) {
    const r = el.getBoundingClientRect();
    return { x: window.scrollX + r.left, y: window.scrollY + r.top };
  }
  // note sits left of the element; near the left edge it would clamp over the
  // element itself, so flip it to the right, or below when that overflows too
  function initialOffset(el) {
    const a = anchorOf(el), r = el.getBoundingClientRect(), gap = 24;
    if (a.x + DEFAULT.dx >= 0) return {};
    if (a.x + r.width + gap + DEFAULT.w <= document.documentElement.clientWidth) return { dx: r.width + gap };
    return { dx: 0, dy: r.height + gap / 2 };
  }
  const save = () => { try { localStorage.setItem(S.key, JSON.stringify(S.notes)); } catch (e) {} };

  function mount(opts = {}) {
    if (S) unmount();
    const key = "kz-notes:" + (opts.key || location.pathname);
    let notes = [];
    try { notes = JSON.parse(localStorage.getItem(key) || "[]"); } catch (e) {}
    const root = opts.root || document.body;
    const ac = new AbortController();
    S = { key, root, ac, notes, live: new Map(), noting: false, hovered: null };

    if (!document.getElementById("kz-notes-style")) {
      const st = document.createElement("style"); st.id = "kz-notes-style"; st.textContent = STYLE;
      document.head.appendChild(st);
    }

    // ── bar, export pane, leader overlay ──
    const bar = S.bar = document.createElement("div");
    bar.id = "kz-notes-bar";
    bar.innerHTML = `<button type="button" data-k="mode" aria-pressed="false">${T.mode}</button><span class="count">0</span>
      <button type="button" data-k="md">${T.md}</button><button type="button" data-k="json">${T.json}</button>
      <button type="button" data-k="clear">${T.clear}</button><span class="msg"></span>`;
    const out = S.out = document.createElement("pre"); out.id = "kz-notes-out"; out.hidden = true;
    const leader = S.leader = document.createElementNS("http://www.w3.org/2000/svg", "svg"); leader.id = "kz-leader";
    // data-turbo-temporary: keep our DOM out of Turbo's snapshot cache
    [bar, out, leader].forEach((n) => { n.setAttribute("data-turbo-temporary", ""); root.appendChild(n); });

    bar.addEventListener("click", (e) => {
      const k = e.target.dataset.k; if (!k) return;
      if (k === "mode") setMode(!S.noting);
      if (k === "md" || k === "json") exportNotes(k);
      if (k === "clear" && S.notes.length && confirm(`Delete ${S.notes.length} notes?`)) { S.notes = []; save(); renderAll(); }
    });

    // ── capture clicks in note mode (capture phase: beats Turbo / SPA routers) ──
    const opt = { signal: ac.signal }, cap = { signal: ac.signal, capture: true };
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMode(false); }, opt);
    document.addEventListener("mouseover", (e) => {
      if (!S.noting || e.target.closest(OURS)) return;
      S.hovered?.classList.remove("kz-hover");
      S.hovered = e.target; S.hovered.classList.add("kz-hover");
    }, opt);
    document.addEventListener("mouseout", () => S.hovered?.classList.remove("kz-hover"), opt);
    document.addEventListener("click", (e) => {
      if (!S.noting || e.target.closest(OURS)) return;
      e.preventDefault(); e.stopPropagation();
      const el = e.target;
      const note = { id: Date.now().toString(36), ...cssPath(el), text: excerpt(el), ctx: contextOf(el), note: "", created: new Date().toISOString(), ...DEFAULT, ...initialOffset(el) };
      S.notes.push(note); save(); renderAll();
      root.querySelector(`.kz-note[data-id="${note.id}"] textarea`)?.focus();
      setMode(false);
    }, cap);
    window.addEventListener("resize", renderAll, opt);

    renderAll();
  }

  function unmount() {
    if (!S) return;
    setMode(false);
    S.ac.abort();
    S.live.forEach(({ ro }) => ro.disconnect());
    S.root.querySelectorAll(".kz-note, .kz-badge").forEach((n) => n.remove());
    [S.bar, S.out, S.leader].forEach((n) => n.remove());
    document.querySelectorAll(".kz-noted, .kz-hover").forEach((n) => n.classList.remove("kz-noted", "kz-hover"));
    document.getElementById("kz-notes-style")?.remove();
    S = null;
  }

  // re-anchor after the host swapped DOM (Turbo frames, morphs, SPA re-render)
  const refresh = () => { if (S) renderAll(); };

  function setMode(on) {
    S.noting = on;
    document.body.classList.toggle("kz-noting", on);
    S.bar.querySelector('[data-k="mode"]').setAttribute("aria-pressed", String(on));
    S.out.hidden = true;
    if (!on) S.hovered?.classList.remove("kz-hover");
  }
  const msg = (t) => { const m = S.bar.querySelector(".msg"); m.textContent = t; setTimeout(() => (m.textContent = ""), 1500); };

  // ── geometry ──
  function placeNote(n, el, box) {
    const a = anchorOf(el);
    const maxLeft = Math.max(0, document.documentElement.scrollWidth - (n.w || DEFAULT.w) - 4);
    box.style.left = `${Math.min(Math.max(0, a.x + n.dx), maxLeft)}px`;
    box.style.top = `${Math.max(0, a.y + n.dy)}px`;
    box.style.width = `${n.w}px`; box.style.height = `${n.h}px`;
  }
  function placeBadge(el, badge) {
    const a = anchorOf(el);
    badge.style.left = `${a.x - 8}px`; badge.style.top = `${a.y - 8}px`;
  }
  // nearest point on the note's border to the anchor → dotted leader
  function drawLeaders() {
    const leader = S.leader;
    leader.setAttribute("width", document.documentElement.scrollWidth);
    leader.setAttribute("height", document.documentElement.scrollHeight);
    leader.innerHTML = "";
    for (const [, { el, box }] of S.live) {
      if (box.hidden) continue;
      const a = anchorOf(el);
      const x = box.offsetLeft, y = box.offsetTop, w = box.offsetWidth, h = box.offsetHeight;
      const px = Math.min(Math.max(a.x, x), x + w), py = Math.min(Math.max(a.y, y), y + h);
      if (px === a.x && py === a.y) continue;          // anchor inside the note
      leader.insertAdjacentHTML("beforeend",
        `<line x1="${a.x}" y1="${a.y}" x2="${px}" y2="${py}" stroke="#c9a227" stroke-width="1.5" stroke-dasharray="2 4" stroke-linecap="round"/>` +
        `<circle cx="${a.x}" cy="${a.y}" r="2.5" fill="#c9a227"/>`);
    }
  }

  // ── drag (header) + resize (css resize:both, observed) ──
  function makeDraggable(n, el, box) {
    const header = box.querySelector("header");
    header.addEventListener("pointerdown", (e) => {
      if (e.target.closest("button")) return;
      e.preventDefault();
      const start = { x: e.clientX, y: e.clientY, dx: n.dx, dy: n.dy };
      box.classList.add("kz-dragging");
      try { header.setPointerCapture(e.pointerId); } catch (err) {}   // synthetic events have no live pointer
      const move = (ev) => { n.dx = start.dx + (ev.clientX - start.x); n.dy = start.dy + (ev.clientY - start.y); placeNote(n, el, box); drawLeaders(); };
      const up = () => { header.removeEventListener("pointermove", move); box.classList.remove("kz-dragging"); save(); };
      header.addEventListener("pointermove", move);
      header.addEventListener("pointerup", up, { once: true });
      header.addEventListener("pointercancel", up, { once: true });
    });
    const ro = new ResizeObserver(() => {
      if (box.hidden || box.classList.contains("kz-dragging")) return;
      const w = box.offsetWidth, h = box.offsetHeight;
      if (w === n.w && h === n.h) return;
      n.w = w; n.h = h; save(); drawLeaders();
    });
    ro.observe(box);
    return ro;
  }

  // ── render ──
  function renderAll() {
    const { root, notes, live } = S;
    live.forEach(({ ro }) => ro.disconnect());
    root.querySelectorAll(".kz-note, .kz-badge").forEach((n) => n.remove());
    document.querySelectorAll(".kz-noted").forEach((n) => n.classList.remove("kz-noted"));
    live.clear();
    notes.forEach((n, i) => {
      let el = null; try { el = document.querySelector(n.path); } catch (e) {}
      n.orphan = !el;
      if (!el) return;
      Object.keys(DEFAULT).forEach((k) => { if (typeof n[k] !== "number") n[k] = DEFAULT[k]; });   // notes saved by the first prototype
      el.classList.add("kz-noted");
      const box = document.createElement("div");
      box.className = "kz-note"; box.dataset.id = n.id; box.hidden = !!n.collapsed;
      box.setAttribute("data-turbo-temporary", "");
      box.innerHTML = `<header title="drag to move"><b>${i + 1}</b><code title="${n.path}">${n.path}</code><button type="button" title="collapse" data-a="fold">–</button><button type="button" title="${T.remove}" aria-label="${T.remove}" data-a="del">✕</button></header><textarea placeholder="note…"></textarea>`;
      box.querySelector("textarea").value = n.note;
      box.querySelector("textarea").addEventListener("input", (e) => { n.note = e.target.value; save(); });
      box.querySelector('[data-a="del"]').addEventListener("click", () => { S.notes = S.notes.filter((x) => x !== n); save(); renderAll(); });
      box.querySelector('[data-a="fold"]').addEventListener("click", () => { n.collapsed = true; save(); renderAll(); });
      const badge = document.createElement("span");
      badge.className = "kz-badge"; badge.textContent = i + 1; badge.title = n.note || n.path;
      badge.setAttribute("data-turbo-temporary", "");
      badge.addEventListener("click", () => { n.collapsed = !n.collapsed; save(); renderAll(); });
      root.append(box, badge);
      placeNote(n, el, box); placeBadge(el, badge);
      live.set(n.id, { el, box, badge, ro: makeDraggable(n, el, box) });
    });
    S.bar.querySelector(".count").textContent = notes.length;
    drawLeaders();
  }

  // ── export ──
  function exportNotes(fmt) {
    const rows = S.notes.map((n, i) => ({ n: i + 1, path: n.path, anchored: n.anchored !== false, text: n.text, ctx: n.ctx || "", note: n.note, orphan: !!n.orphan }));
    let text;
    if (fmt === "json") text = JSON.stringify({ page: location.href, title: document.title, key: S.key, notes: rows }, null, 2);
    else text = [`# Notes on ${document.title}`, location.href, "", ...rows.flatMap((r) => {
      const pad = " ".repeat(`${r.n}. `.length);   // continuation lines align under the bullet text
      return [
        `${r.n}. \`${r.path}\`${r.orphan ? " " + T.orphan : ""}${r.anchored ? "" : " " + T.unanchored}`,
        `${pad}> ${r.text || "—"}`,
        ...(r.ctx ? [`${pad}under: ${r.ctx}`] : []),
        ...(r.note || "(no comment)").split("\n").map((l) => pad + l), ""
      ];
    })].join("\n");
    S.out.textContent = text; S.out.hidden = false;
    navigator.clipboard?.writeText(text).then(() => msg(T.copied), () => msg("select & copy"));
  }

  window.KZStickyNotes = { mount, unmount, refresh };
})();
