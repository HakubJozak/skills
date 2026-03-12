---
name: fio-api
description: "Fio Bank API reference for Czech banking operations. This skill should be used when writing code that interacts with the Fio Bank API — submitting domestic CZK payments, reading account transactions/statements, or checking balances. Covers authentication, endpoints, XML payment schemas, error handling, and rate limits."
---

# Fio Bank API

Reference skill for the Fio Bank REST API (v1.9, fioapi.fio.cz). Load `references/api_reference.md` for full endpoint details, XML schemas, and examples.

## When to Use

- Writing code to send domestic CZK payments via Fio
- Reading account transactions or statements from Fio
- Building scripts that interact with the Fio banking API
- Debugging Fio API errors (409, 500, 422)

## Quick Reference

### Authentication

Every request uses a 64-character API token passed in the URL path (GET) or as a form parameter (POST). Tokens are generated in Fio internetbanking under Settings > API. Two token types:

- **Read-only** — export transactions/statements only
- **Read+write** — export AND submit payment orders

Token validity: 180 days, auto-renewed on each internetbanking/Smartbanking login.

### Rate Limiting

**Minimum 30 seconds between requests** on the same token, regardless of format. Violating this returns HTTP 409 Conflict.

### Base URL

`https://fioapi.fio.cz`

### Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/v1/rest/periods/{token}/{from}/{to}/transactions.{format}` | Transactions by date range |
| GET | `/v1/rest/last/{token}/transactions.{format}` | Transactions since last download |
| GET | `/v1/rest/by-id/{token}/{year}/{id}/transactions.{format}` | Official statement by ID |
| GET | `/v1/rest/set-last-id/{token}/{id}/` | Set download cursor by transaction ID |
| GET | `/v1/rest/set-last-date/{token}/{date}/` | Set download cursor by date |
| GET | `/v1/rest/lastStatement/{token}/statement` | Last statement number |
| POST | `/v1/rest/import/` | Submit payment orders |

Date format: `YYYY-MM-DD`. Supported export formats: `json`, `xml`, `csv`, `gpc`, `html`, `ofx`.

### Submitting Payments

POST to `/v1/rest/import/` with `multipart/form-data`:

| Parameter | Required | Values |
|-----------|----------|--------|
| token | Yes | 64-char API token |
| type | Yes | `xml`, `abo`, `pain001_xml`, `pain008_xml` |
| file | Yes | The payment file |
| lng | No | `cs`, `sk`, `en` (response language) |

After successful upload, the payment batch must be **authorized via push notification / SMS** in internetbanking or Smartbanking. Without authorization, payments are not processed.

### Error Handling

Import response (always XML):

| errorCode | Meaning |
|-----------|---------|
| 0 | Order accepted |
| 1 | Errors found during order check |
| 2 | Warning — some values don't match (e.g. currency) but order accepted |
| 11 | Syntax error |
| 12 | Empty import — no orders in file |
| 13 | File too large (max 2 MB) |
| 14 | Empty file |

Status values: `ok`, `error`, `warning`, `fatal`.

HTTP errors: 404 (bad URL), 409 (rate limit — 30s), 500 (invalid/inactive token), 422 (historical data >90 days not unlocked).

## Implementation Notes

- For Ruby, use `Net::HTTP` with multipart POST or a gem like `multipart-post`. No official Fio Ruby SDK exists.
- JSON is the most convenient format for reading transactions in Ruby (`JSON.parse`).
- To build the domestic payment XML, use string interpolation or a simple XML builder — the schema is straightforward. See `references/api_reference.md` for the full XML example.
- Always respect the 30-second rate limit between API calls.
