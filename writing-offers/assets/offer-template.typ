// Consulting offer (nabídka) template — extracted from the AgroPlan offer (02/2026).
// Fill the CONFIG block, keep the layout. Compile: typst compile offer.typ
//
//   CONFIG ──► helpers (format-price, ztable, info-box) ──► page/style ──► content
//   (numbers)   (reused in every section)                   (never edit)   (per client)

// ===== CONFIG =====
#let meta = (
  title: "Název projektu pro Klienta",
  client: "Klient s.r.o.",
  date: "1. září 2026",
  version: "1.0",
)

#let supplier = (
  name: "Jakub Hozák",
  address: "V Sedlci 249/4a, 160 00 Praha 6",
  ico: "76065260",
  phone: "+420 777 855 359",
  email: "jakub.hozak@gmail.com",
)

// Pricing is always derived: MD counts × rate. Never hardcode a Kč total.
#let md-rate = 16000

#let items = (
  (label: "Workshop / analýza",        md: 2),
  (label: "Realizace (POC)",           md: 5),
  (label: "Nastavení účtů, billing",   md: 0.5),
  (label: "Školení uživatelů",         md: 1),
  (label: "Intenzivní podpora 3 měsíce", md: 4),
)
#let total-md = items.map(i => i.md).sum()
#let total-price = total-md * md-rate

// Optional monthly running costs (third parties). Set to () to hide the section.
#let monthly = (
  (label: "AI API (Anthropic Claude)", min: 1000, max: 3000),
  (label: "VPS hosting (Hetzner)",     min: 2000, max: 4000),
)
#let monthly-min = monthly.map(m => m.min).sum(default: 0)
#let monthly-max = monthly.map(m => m.max).sum(default: 0)
// ===== END CONFIG =====

// ===== HELPERS =====
#let primary-color = rgb("#2c5f8d")
#let accent-color = rgb("#4a90e2")
#let light-bg = rgb("#f5f7fa")
#let success-color = rgb("#27ae60")

// 123456 → "123 456 Kč"
#let format-price(amount) = {
  let chars = str(calc.round(amount)).codepoints()
  let result = ()
  let count = 0
  for i in range(chars.len() - 1, -1, step: -1) {
    if count == 3 { result.push(" "); count = 0 }
    result.push(chars.at(i))
    count += 1
  }
  result.rev().join("") + " Kč"
}

// Zebra table with colored header. `highlight` = row indices to accent (e.g. totals).
#let ztable(columns: (1fr, auto), align: left, header: (), highlight: (), header-fill: primary-color, ..rows) = table(
  columns: columns,
  align: align,
  fill: (col, row) => if row == 0 { header-fill }
    else if row in highlight { accent-color.lighten(60%) }
    else if calc.rem(row, 2) == 0 { light-bg },
  stroke: 0.5pt + gray,
  inset: 10pt,
  table.header(..header.map(h => text(fill: white, weight: "bold")[#h])),
  ..rows,
)

#let info-box(title: none, body) = rect(
  width: 100%, fill: light-bg, stroke: 1pt + accent-color, radius: 4pt, inset: 12pt,
)[
  #if title != none [
    #text(weight: "bold", fill: primary-color, size: 10pt)[#title]
    #v(0.3em)
  ]
  #body
]
// ===== END HELPERS =====

// ===== PAGE & STYLE =====
#set document(title: meta.title, author: supplier.name)
#set page(
  paper: "a4",
  margin: (left: 2.5cm, right: 2.5cm, top: 3cm, bottom: 3cm),
  header: context {
    set text(size: 9pt, fill: gray)
    line(length: 100%, stroke: 0.5pt + gray)
    v(-0.3em)
    [#meta.title]
    h(1fr)
    [Datum: #meta.date | Verze: #meta.version]
    v(-0.8em)
  },
  footer: context {
    line(length: 100%, stroke: 0.5pt + gray)
    v(-0.3em)
    set text(size: 8pt, fill: gray.darken(20%))
    grid(
      columns: (1fr, auto),
      align(center)[
        Dodavatel: #supplier.name, #supplier.address, IČO: #supplier.ico, Plátce DPH \
        Tel: #supplier.phone, Email: #supplier.email \
        Všechny ceny jsou bez DPH
      ],
      align(right + horizon)[#counter(page).display("1 / 1", both: true)],
    )
  },
)
#set text(font: "Liberation Serif", lang: "cs", size: 11pt)
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.")
#show heading.where(level: 1): it => {
  set text(size: 16pt, fill: primary-color, weight: "bold")
  v(1em); it; v(-0.6em)
  line(length: 100%, stroke: 2pt + primary-color)
  v(0.5em)
}
#show heading.where(level: 2): it => {
  set text(size: 13pt, fill: accent-color, weight: "bold")
  v(0.8em); it; v(0.5em)
}

// Title banner
#rect(width: 100%, fill: primary-color, inset: 20pt)[
  #text(size: 22pt, fill: white)[#meta.title] \
  #text(size: 12pt, fill: white.transparentize(40%))[
    #supplier.name | #supplier.phone | #supplier.email
  ]
]
// ===== END PAGE & STYLE =====

// ===== CONTENT =====
= Úvod

Tato nabídka představuje ... pro #meta.client. Cílem je ...

#info-box[
  Řešení je navrženo s ohledem na:

  - *Bezpečnost dat* – ...
  - *Praktičnost* – ...
  - *Škálovatelnost* – ...
]

= FÁZE A: Název fáze

== Co dodáme

+ *Dodávka 1*
  - detail
+ *Nasazení a konfigurace*
  - detail
+ *Školení a předání*
  - Kompletní zdrojový kód řešení
  - Praktický kurz pro uživatele (½ dne)

== Proč varianta X a ne Y?

#ztable(
  columns: (auto, 1fr, 1fr),
  header: ([Kritérium], [Varianta X], [Varianta Y]),
  [*Počáteční investice*], [0 Kč], [...],
  [*Kvalita*], [...], [...],
  [*Údržba*], [Žádná], [Nutná],
)

*Závěr:* Doporučujeme ...

#if monthly.len() > 0 [
  == Očekávané měsíční náklady na služby třetích stran

  #ztable(
    columns: (1fr, auto),
    align: (left, right),
    header: ([Položka], [Měsíční náklad]),
    highlight: (monthly.len() + 1,),
    ..monthly.map(m => ([#m.label], [#format-price(m.min) – #format-price(m.max)])).flatten(),
    [*Celkem*], [*#format-price(monthly-min) – #format-price(monthly-max)/měsíc*],
  )

  _Pozn.: Náklady závisí na intenzitě používání._
]

== Cena Fáze A

#ztable(
  columns: (1fr, auto, auto),
  align: (left, center, right),
  header: ([Činnost], [MD], [Cena]),
  ..items.map(i => ([#i.label], [#i.md], [#format-price(i.md * md-rate)])).flatten(),
  table.hline(stroke: 2pt + primary-color),
  [#text(size: 12pt, weight: "bold")[CELKEM FÁZE A]],
  [#text(weight: "bold")[#total-md]],
  [#text(size: 12pt, weight: "bold")[#format-price(total-price)]],
)

_Sazba #format-price(md-rate) / MD._

= Podpora a garance

== Model podpory (zahrnut ve Fázi A)

#ztable(
  columns: (auto, 1fr),
  header: ([Období], [Použití]),
  [Měsíc 1], [Intenzivní podpora po spuštění, řešení připomínek],
  [Měsíc 2], [Ladění, optimalizace],
  [Měsíc 3], [Stabilizace, drobné úpravy],
)

== Garance
- *Minimální doba podpory: 3 měsíce* – intenzivní podpora po spuštění
- *Záruka 1 rok* – oprava zásadních chyb (nezahrnuje 24/7 monitoring ani řešení výpadků)
- *Reakce na kritické problémy: do 24 hodin* (pracovní dny, během 3měsíční podpory)

== Po 3měsíční podpoře

#info-box(title: "Dvě možnosti")[
  *Varianta A: Předání IT týmu* — dokumentace, handoff session, 1 rok záruka zůstává.

  *Varianta B: Kontinuální podpora* — monitoring, průběžné vylepšování, cena dle dohody.
]

= FÁZE B: Rozšíření (po úspěšné Fázi A)

#ztable(
  columns: (auto, 1fr),
  header: ([Funkce], [Popis]),
  [*Rozšíření 1*], [...],
  [*Rozšíření 2*], [...],
)

_Cena Fáze B bude stanovena po vyhodnocení Fáze A._

= Shrnutí

#ztable(
  columns: (1fr, auto),
  header: ([], [#text(size: 13pt)[Fáze A]]),
  header-fill: success-color,
  [*Cena*], [#text(size: 13pt, weight: "bold")[#format-price(total-price) bez DPH]],
  [*Měsíční provoz*], [#format-price(monthly-min) – #format-price(monthly-max)],
  [*Podpora*], [3 měsíce v ceně],
  [*Záruka*], [1 rok (oprava chyb)],
  [*Zdrojový kód*], [Kompletní předání],
  [*Doba realizace*], [2–3 týdny],
)

== Pro #meta.client
- *Přínos 1* – ...
- *Přínos 2* – ...

= Další kroky

+ *Odsouhlasení nabídky* – Vaše připomínky a úpravy
+ *Podpis smlouvy* – Standardní rámcová smlouva o dílo
+ *Termín zahájení* – workshop / předání přístupů
+ *Zahájení realizace*
