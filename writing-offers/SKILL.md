---
name: writing-offers
description: Use when drafting, pricing, or revising a consulting/implementation offer (nabídka, cenová nabídka, proposal) for a client such as Enerfis, Šárynka/Ekodomov, or AgroPlan — a Czech PDF with phased scope, MD-based pricing, support and guarantee terms.
---

# Writing Offers

Czech consulting offers as Typst → PDF. The template carries the layout, supplier
identity and business terms; you supply the client-specific scope and numbers.

**REQUIRED SUB-SKILL:** typst-editor (compile, syntax, visual validation).

## Workflow

1. Read the prospect's prep notes (`~/Sync/Documents/<client>/CLAUDE.md`, `research/`, and any `demo/` artifacts — a prior demo `.typ` is load-bearing for scoping). Scope must name their real workflow, tools and pains, not generic AI pitches.
2. `cp ~/skills/writing-offers/assets/offer-template.typ <client-dir>/offer/offer.typ`
3. Fill the `CONFIG` block only: `meta`, `items` (MD per activity), `monthly` (or `()`), keep `supplier` and `md-rate` unless told otherwise.
4. Replace placeholder prose in `CONTENT`; delete sections that don't apply (Phase B, monthly costs, comparison table). Keep the section order.
   Re-derive per client: the *Proč X a ne Y* axis and the `monthly` lines follow *this* client's architecture (a local POC has no VPS line). Never copy AgroPlan's cloud-vs-local table unless that is the actual decision.
   Numbers not backed by prep notes (API usage, doba realizace, client legal form) → mark `TODO` in the .typ and list them in your reply; don't silently estimate.
5. `typst compile offer.typ <client>-<topic>-v<version>.pdf`, then PNG-render and inspect every page (typst-editor → Visual Validation).
6. Bump `meta.version` on every revision sent to the client; keep the PDF filename versioned.

## Offer anatomy (section order)

| # | Section | Purpose |
|---|---------|---------|
| 1 | Úvod + info-box | goal in 2 sentences; 3 design principles (bezpečnost, praktičnost, škálovatelnost) |
| 2 | FÁZE A: Co dodáme | numbered deliverables: system, nasazení, školení + předání zdrojového kódu |
| 2.x | Proč X a ne Y | 3-row comparison table + one-line *Závěr* recommendation |
| 2.x | Měsíční náklady | 3rd-party running costs as min–max ranges (API, VPS) |
| 2.x | Cena Fáze A | MD table, bold total, rate note |
| 3 | Podpora a garance | 3-month support model, guarantee bullets, 2 options after support |
| 4 | FÁZE B | extension table, "cena po vyhodnocení Fáze A" |
| 5 | Shrnutí | green summary table + "Pro <klient>" / "Pro <uživatele>" benefit bullets |
| 6 | Další kroky | 4 steps ending in "zahájení realizace" |

## Standard terms (baked into template — change only on purpose)

- Rate 16 000 Kč/MD, all prices bez DPH, supplier is plátce DPH.
- Small first phase, extension priced after evaluation — never quote Phase B.
- 3 months intensive support included as a priced line (~4 MD); 1-year bug-fix
  guarantee; 24h reaction on critical issues, working days only, no 24/7.
- Cloud AI over local hardware for pilots; local model listed as future option.
- Full source code handover; after support either IT handoff or paid retainer.

## Template mechanics

- Every Kč value derives from `items`/`monthly` — never type a total by hand.
- `ztable(header: (...), highlight: (row,), header-fill: ...)` — zebra table; pass
  rows as `..list.map(...).flatten()` for data-driven rows.
- `info-box(title: ...)[...]` for principles and options.
- Email is a plain string in `supplier` — rendering via `#supplier.email` needs no `\@` escape.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Generic scope ("AI helps you work faster") | cite their tools/formats/roles from prep notes |
| Hardcoded "200 000 Kč" | add/adjust an `items` entry |
| Missing supplier legal line | comes from footer — don't remove `supplier` |
| Forced `#pagebreak()` everywhere | only before Shrnutí if the table would split |
| Sending PDF without visual check | render PNG, read every page |

Reference implementation: `~/projects/agroplan/offer/offer.typ` (AgroPlan AI knowledge base, 02/2026).
