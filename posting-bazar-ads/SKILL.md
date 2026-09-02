---
name: posting-bazar-ads
description: Use when posting, mirroring, or extracting classified ads (inzeráty) on the Czech marketplaces sbazar.cz and bazos.cz — e.g. "add my sbazar ads to bazos", "post this item for sale", "copy my listings over" — or when blocked by the Seznam consent wall or the bazos SMS phone verification.
---

# Posting Bazar Ads

## Overview

Post or mirror classified ads between sbazar.cz (Seznam) and bazos.cz. Reading sbazar needs no browser; posting on bazos is a browser flow gated by SMS phone verification. Battle-tested on bazos in 08/2026.

## Seller defaults (Jakub)

Jméno `Jakub Hozak` · Telefon `777855359` · E-mail `jakub.hozak@gmail.com` · PSČ `16000` (Praha 6). Confirm PSČ per ad if the item's location is unclear.

Bazos heslo (per-ad edit/delete password): `3234d8af` — reuse it for every new ad so all ads share one password.

## Hard checkpoints — ask via AskUserQuestion, never skip

1. Bazos terms checkbox + submitting the phone number (triggers the SMS) — needs explicit OK.
2. The SMS code ("mobilní klíč") — only the user can read it. Verification persists in session cookies: verify once, post many.
3. Final publish confirmation with a full ad summary — one question may cover a whole batch of ads.

## Extracting ads from sbazar.cz

Never open sbazar in a fresh browser — Seznam's consent-or-pay wall blocks it and has no free "reject" option. Plain HTTP works (no cookies):

```bash
scripts/sbazar_fetch.py https://www.sbazar.cz/<username>   # list profile ad URLs
scripts/sbazar_fetch.py <ad-url> --download DIR            # ad JSON + photos as JPEG
```

Ad data lives in the ad page's `application/ld+json` Product block; locality sits next to "Lokalita nabídky". Photo gotchas (script handles them): the CDN accepts only the exact signed `?fl=...` query from the page — any edit returns an HTML error; files are WebP despite `.jpeg` names; they carry a small sbazar watermark, so offer to use the user's original photos instead.

## Posting on bazos.cz

1. Go to the section subdomain: `https://<section>.bazos.cz/pridat-inzerat.php` (deti, pc, elektro, auto, ...; full list on www.bazos.cz/pridat-inzerat.php).
2. Cookie banner: click "Odmítám".
3. First visit shows the phone-verification gate — checkpoints 1 and 2 above.
4. Fill the form (`#formpridani`): Kategorie (select), Nadpis, Text, Cena, PSČ, photos, Jméno, Telefon, E-mail, Heslo.
   - PSČ is an autocomplete: type slowly, then click the suggestion row — a plain fill does not register.
   - Photos: click "Přidej obrázky" → file chooser → upload. Playwright MCP only accepts paths under `/home/dev` — copy photos to `~/.playwright-mcp/` first, delete after.
   - Heslo is a per-ad edit/delete password ("zadejte cokoliv"): use the default from Seller defaults above (generate a fresh one with `openssl rand -hex 4` only if the user wants a different one, and report it). Never ask for or enter a real account password.
5. Submit only after checkpoint 3. Success page says "Inzerát byl vložen" (active within 10 min); collect ad URLs via `document.querySelectorAll('a[href*="/inzerat/"]')`.
6. Skip the "topování" upsell — it is a paid purchase.
7. Contact fields stay pre-filled for further ads in the same session.

## Posting on sbazar.cz (not yet battle-tested)

Requires a logged-in Seznam account → use claude-in-chrome with the user's own Chrome, not Playwright. Start at www.sbazar.cz, find "Vložit inzerát", discover the form via snapshots. Update this section after the first real run.

## Browser setup

- Prefer claude-in-chrome; when the extension is not connected, fall back to Playwright MCP and resize to 1920×1080.
- Playwright error "Browser is already in use for ~/.cache/ms-playwright-mcp/..." → a stale headless Chrome holds the profile: `pgrep -af ms-playwright-mcp`, kill the main PID, retry.

## Gotchas

| Symptom | Fix |
|---|---|
| Redirect to cmp.seznam.cz ("Abyste mohli pokračovat…") | Do not accept; fetch over plain HTTP instead |
| Photo CDN returns a tiny HTML file | Use the exact signed `?fl=` query from the page |
| "File access denied … outside allowed roots" on upload | Copy files under `/home/dev` (e.g. `~/.playwright-mcp/`) |
| PSČ field ignored on submit | Type slowly + click the suggestion row |
| Submit button ref stale after photo upload | Re-snapshot `#formpridani`, then click |
