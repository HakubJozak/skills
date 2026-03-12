# Fio Bank API — Full Reference

Source: Fio API Bankovnictvi v1.9 (16.10.2025), https://www.fio.cz/docs/cz/API_Bankovnictvi.pdf

## 1. Authentication

- 64-character unique token per account
- Generated in internetbanking: Settings > API > "Pridat novy token"
- Token creation requires strong authorization (SMS/push)
- If multiple people have authorization on the account, all must sign the token
- Token is usable 5 minutes after authorization
- Two permission levels:
  - Read-only (export only)
  - Read+write (export + import payment orders)
- Validity: 180 days, auto-extended on each login to internetbanking/Smartbanking

## 2. Communication

All communication over HTTPS with minimum 128-bit SSL encryption.

- **GET** — read transactions, statements, set cursors
- **POST** — submit payment orders

### Rate Limit

Minimum **30 seconds** between requests on the same token. Returns **HTTP 409 Conflict** if violated.

### Data Older Than 90 Days

Requires additional strong authorization in internetbanking (Settings > API > unlock icon). After authorization, historical data is accessible for 10 minutes.

## 3. Export Endpoints (GET)

### 3.1 Transactions by Date Range

```
GET https://fioapi.fio.cz/v1/rest/periods/{token}/{date_from}/{date_to}/transactions.{format}
```

- `date_from`, `date_to`: `YYYY-MM-DD`
- `format`: `json`, `xml`, `csv`, `gpc`, `html`, `ofx`

### 3.2 Official Statements

```
GET https://fioapi.fio.cz/v1/rest/by-id/{token}/{year}/{id}/transactions.{format}
```

- `year`: `YYYY`
- `id`: statement number
- `format`: `json`, `xml`, `csv`, `gpc`, `html`, `ofx`, `pdf`, `mt940`, `cba_xml`, `sba_xml`

### 3.3 Transactions Since Last Download

```
GET https://fioapi.fio.cz/v1/rest/last/{token}/transactions.{format}
```

Automatically advances the cursor (last downloaded ID) on each successful response.

### 3.4 Set Cursor

By last downloaded transaction ID:
```
GET https://fioapi.fio.cz/v1/rest/set-last-id/{token}/{id}/
```

By date:
```
GET https://fioapi.fio.cz/v1/rest/set-last-date/{token}/{YYYY-MM-DD}/
```

### 3.5 Last Statement Number

```
GET https://fioapi.fio.cz/v1/rest/lastStatement/{token}/statement
```

## 4. JSON Response Structure

### Account Info (accountStatement.info)

```json
{
  "accountStatement": {
    "info": {
      "accountId": "1234562",
      "bankId": "2010",
      "currency": "CZK",
      "iban": "CZ7820100000002111111111",
      "bic": "FIOBCZPPXXX",
      "openingBalance": 7356.22,
      "closingBalance": 7321.22,
      "dateStart": "2012-07-01+02:00",
      "dateEnd": "2012-07-31+02:00",
      "yearList": null,
      "idList": null,
      "idFrom": 1147608196,
      "idTo": 1147608197,
      "idLastDownload": null
    },
    "transactionList": {
      "transaction": [...]
    }
  }
}
```

### Transaction Fields (in JSON, keyed by column ID)

| Column ID | Name | Description | Example |
|-----------|------|-------------|---------|
| 22 | ID pohybu | Unique transaction ID | 1158152824 |
| 0 | Datum | Transaction date | 2012-07-27+02:00 |
| 1 | Objem | Amount (negative = debit) | -15.00 |
| 14 | Mena | Currency (ISO 4217) | CZK |
| 2 | Protiucet | Counter-account number | 2212-2000000699 |
| 3 | Kod banky | Counter-account bank code | 2010 |
| 12 | Nazev banky | Bank name | Fio banka, a.s. |
| 4 | KS | Constant symbol | 0558 |
| 5 | VS | Variable symbol | 1234567890 |
| 6 | SS | Specific symbol | 1234567890 |
| 7 | Uzivatelska identifikace | User identification | |
| 16 | Zprava pro prijemce | Message for recipient | |
| 8 | Typ | Transaction type | Platba prevodem uvnitr banky |
| 9 | Provedl | Executed by | Novak, Jan |
| 10 | Upresneni | Clarification | 15.90 EUR |
| 25 | Komentar | Comment | |
| 26 | BIC | Counter-account BIC | UNCRITMMXXX |
| 17 | ID pokynu | Order ID | 2102382863 |
| 18 | Reference platce | Payer reference | 2000000003 |

## 5. Import Endpoint (POST)

### URL

```
POST https://fioapi.fio.cz/v1/rest/import/
```

### Parameters (multipart/form-data)

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| token | Yes | | 64-char API token |
| type | Yes | `xml`, `abo`, `pain001_xml`, `pain008_xml` | Import format |
| file | Yes | | File with payment data |
| lng | No | `cs`, `sk`, `en` | Response language |

### cURL Example

```bash
curl -S -s -X POST \
  -F "token=YOUR_64_CHAR_TOKEN" \
  -F "type=xml" \
  -F "file=@payment.xml" \
  https://fioapi.fio.cz/v1/rest/import/ \
  > result.xml 2>error.log
```

### Response (always XML)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<responseImport>
  <result>
    <errorCode>0</errorCode>
    <idInstruction>12345</idInstruction>
    <status>ok</status>
    <sumDebit>100.00</sumDebit>
    <sumCredit>0.00</sumCredit>
  </result>
</responseImport>
```

| Element | Values | Description |
|---------|--------|-------------|
| errorCode | 0 | Order accepted |
| | 1 | Errors found during check |
| | 2 | Warning — values mismatch but accepted |
| | 11 | Syntax error |
| | 12 | Empty import — no orders |
| | 13 | File too large (>2 MB) |
| | 14 | Empty file — no orders |
| status | ok | Accepted |
| | error | Gross error, entire batch rejected |
| | warning | Some values mismatch, orders accepted |
| | fatal | Bank system error, all orders rejected |
| idInstruction | | Batch ID — unique identifier |
| sumDebit | 18d | Sum of debit items |
| sumCredit | 18d | Sum of credit items |

Response XSD: https://www.fio.cz/schema/responseImportIB.xsd

## 6. Domestic Payment XML (Platba v ramci CR)

Used for CZK payments between Czech bank accounts. Also works for foreign currency transfers within Fio.

### Schema

Import XSD: https://www.fio.cz/schema/importIB.xsd

### Fields

| Element | Required | Format | Description | Example |
|---------|----------|--------|-------------|---------|
| accountFrom | Yes | 16n | Source account number | 1234562 |
| currency | Yes | 3!x | Currency (ISO 4217) | CZK |
| amount | Yes | 18d | Amount | 100.00 |
| accountTo | Yes | 6n-10n | Recipient account number | 2212-2000000699 |
| bankCode | Yes | 4!n | Recipient bank code | 0300 |
| ks | No | 4n | Constant symbol | 0558 |
| vs | No | 10n | Variable symbol | 1234567890 |
| ss | No | 10n | Specific symbol | 1234567890 |
| date | Yes | YYYY-MM-DD | Payment date | 2013-04-25 |
| messageForRecipient | No | 140i | Message shown to recipient | Nanny payment |
| comment | No | 255i | Your note (not shown to recipient) | Weekly payment |
| paymentReason | No | 3!n | Payment title code (see section 6.3.4) | 110 |
| paymentType | No | 6!n | 431001=standard, 431005=priority, 431022=inkaso | 431001 |

### Complete XML Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Import xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:noNamespaceSchemaLocation="http://www.fio.cz/schema/importIB.xsd">
  <Orders>
    <DomesticTransaction>
      <accountFrom>1234562</accountFrom>
      <currency>CZK</currency>
      <amount>100.00</amount>
      <accountTo>2212-2000000699</accountTo>
      <bankCode>0300</bankCode>
      <ks>0558</ks>
      <vs>1234567890</vs>
      <ss>1234567890</ss>
      <date>2013-04-25</date>
      <messageForRecipient>Hracky pro deti v PENNY MARKET</messageForRecipient>
      <comment></comment>
      <paymentType>431001</paymentType>
    </DomesticTransaction>
  </Orders>
</Import>
```

### Multiple Payments in One Batch

Place multiple `<DomesticTransaction>` elements inside `<Orders>`. All transactions in one XML file must be the same type (domestic, euro, or foreign — do not mix).

```xml
<Import xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:noNamespaceSchemaLocation="http://www.fio.cz/schema/importIB.xsd">
  <Orders>
    <DomesticTransaction>
      <!-- payment 1 -->
    </DomesticTransaction>
    <DomesticTransaction>
      <!-- payment 2 -->
    </DomesticTransaction>
  </Orders>
</Import>
```

## 7. HTTP Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 404 | Bad URL | Check endpoint URL and parameters |
| 409 | Rate limit (30s between requests) | Wait and retry after 30 seconds |
| 413 | Too many items (max 50,000) | Narrow date range or set cursor |
| 422 | Historical data >90 days not unlocked | Unlock in internetbanking Settings > API |
| 500 | Invalid or inactive token | Verify token in internetbanking |

## 8. Security Notes

- API token grants full access to account data (and payments if read+write). Store securely.
- Never commit tokens to source control. Use environment variables.
- After submitting a payment via API, it **must be authorized** via push notification or SMS in internetbanking/Smartbanking. Without authorization, the payment is not processed.
- Store token only on trusted machines, not on publicly accessible servers.

## 9. Transaction Types (Typy pohybu)

Common types relevant for payment tracking:

| ID | Type |
|----|------|
| 1 | Incoming transfer within bank |
| 2 | Outgoing transfer within bank |
| 7 | Outgoing payment |
| 8 | Incoming payment |
| 9 | Cashless payment |
| 10 | Cashless incoming |
| 11 | Card payment |
| 25 | Transfer between own accounts (outgoing) |
