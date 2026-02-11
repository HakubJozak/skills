---
name: car-picker
description: "Research Czech car market for family cars. Use when you need to find used or new cars, compare prices, read reviews, check vehicle history, or get oriented in the Czech automotive market with focus on family segment (SUVs, estates, MPVs)."
allowed-tools:
  - WebFetch
  - WebSearch
  - Read
  - Write
---

# Czech Car Market - Family Cars Research

Research and navigate the Czech car market with focus on family-friendly vehicles: estates (kombi), SUVs, crossovers, and MPVs.

## When to Use This Skill

- Search for family cars on Czech market
- Compare prices across different platforms
- Research specific car models and their reliability
- Check current market prices and trends
- Find reviews and owner experiences in Czech context

## Key Czech Car Market Websites

### Car Listing Portals (for browsing and price research)

| Website | Description | Best For |
|---------|-------------|----------|
| **sauto.cz** | Largest Czech car portal | Most listings, market overview |
| **tipcars.cz** | Second largest portal | Good filters, price comparison |
| **aaaauto.cz** | Major dealer chain | Certified used cars, warranty |
| **autocaris.cz** | Aggregator | Cross-platform search |
| **cars.cz** | Seznam.cz portal | Quick search |
| **sbazar.cz/auta** | Classified ads | Private sellers, deals |
| **bazoš.cz** | Classified ads | Private sellers |

### Price Guides & Valuation

| Website | Description |
|---------|-------------|
| **cebia.cz** | Vehicle history check (VIN), price estimation |
| **autotrace.cz** | Mileage verification, stolen car check |
| **eurotax.cz** | Professional car valuation |

### Reviews & Information (Czech)

| Website | Description |
|---------|-------------|
| **auto.cz** | News, reviews, tests |
| **autoweb.cz** | Reviews, comparisons |
| **autorevue.cz** | Magazine with tests |
| **svetzenu.cz** | Women-focused car reviews |
| **autoforum.cz** | Discussion forums |

### International Resources (useful for reliability data)

| Website | Description |
|---------|-------------|
| **adac.de** | German reliability reports |
| **tuvreport.de** | TÜV failure statistics |
| **whatcar.com** | UK reviews and reliability |

## Family Car Segments in Czech Market

### 1. Estates (Kombi) - Most Popular Family Choice

**Škoda Octavia Combi** - Czech market leader
- Price range: 150,000 - 600,000 CZK (used)
- Pros: Huge boot (640L), reliable, cheap parts
- Cons: Common, can be ex-taxi/fleet

**Škoda Superb Combi** - Premium estate
- Price range: 250,000 - 900,000 CZK
- Pros: Massive space (660L), luxury feel
- Cons: Higher running costs

**VW Passat Variant** - Similar to Superb
**Ford Mondeo Combi** - Good value
**Peugeot 308/508 SW** - Stylish alternative

### 2. Compact SUVs / Crossovers

**Škoda Karoq** - Popular family SUV
- Price range: 400,000 - 800,000 CZK
- Pros: Practical, good boot, available 4x4
- Cons: Newer model, less depreciated

**Škoda Kodiaq** - 7-seat option
- Price range: 500,000 - 1,200,000 CZK
- Pros: 7 seats, huge space
- Cons: Expensive

**VW Tiguan** - Premium compact SUV
**Hyundai Tucson** - Good warranty
**Kia Sportage** - Value proposition

### 3. MPVs (Multi-Purpose Vehicles)

**Škoda Roomster** - Discontinued but available used
**VW Touran** - Popular family MPV
**Ford C-Max / S-Max** - Flexible seating
**Renault Scenic** - French alternative

## Price Research Strategy

### Step 1: Establish Market Price
```
1. Search sauto.cz for specific model
2. Filter by year, mileage, fuel type
3. Note price range (min/median/max)
4. Compare with tipcars.cz
```

### Step 2: Verify Vehicle History
```
1. Get VIN number from seller
2. Check cebia.cz for:
   - Origin and import history
   - Mileage verification
   - Accident history
   - Service records
3. Check autotrace.cz for stolen status
```

### Step 3: Compare Similar Listings
```
Key factors affecting Czech prices:
- First owner in CZ vs. import
- Service book (servisní knížka)
- STK validity (technical inspection)
- Winter tires included
- 4x4 vs. 2WD (especially for SUVs)
```

## Common Search Filters (Czech terms)

| Czech | English | Notes |
|-------|---------|-------|
| Rok výroby | Year | Model year |
| Najeto km | Mileage | Watch for "stočený" (rolled back) |
| Palivo | Fuel | Benzín, Nafta, Hybrid, Elektro |
| Převodovka | Transmission | Manuál, Automat, DSG |
| Pohon | Drive | Přední (FWD), Zadní (RWD), 4x4 |
| Výkon | Power | kW or HP |
| Objem | Engine size | ccm |
| STK | Technical inspection | Valid date |
| Karoserie | Body type | Kombi, SUV, MPV |
| Počet míst | Seats | 5, 7 |

## Red Flags When Buying in CZ

1. **Tachometr stočený** - Mileage rollback (very common with imports)
2. **Bez servisní knížky** - No service book
3. **STK brzy končí** - Technical inspection expiring soon
4. **Dovoz z Německa bez historie** - German import without history
5. **Příliš levné** - Too cheap for the spec (hidden issues)
6. **Hodně majitelů** - Too many previous owners

## Useful Czech Phrases for Research

- "recenze majitelů" - owner reviews
- "časté závady" - common problems
- "spotřeba" - fuel consumption
- "náklady na provoz" - running costs
- "pojištění" - insurance
- "daň z vozidla" - road tax

## Seasonal Considerations

- **Best time to buy**: January-February (after Christmas)
- **Worst time to buy**: Spring (everyone wants a car)
- **4x4 premium**: Higher in autumn before winter
- **Convertibles**: Cheaper in winter

## Example Research Workflow

When researching a specific car (e.g., "Škoda Octavia Combi 2018"):

1. **Price check**: Search sauto.cz with filters
2. **Reviews**: Search "Škoda Octavia 3 recenze majitelů"
3. **Common issues**: Search "Škoda Octavia 1.5 TSI problémy"
4. **Running costs**: Check "Škoda Octavia spotřeba zkušenosti"
5. **Compare**: Look at alternatives in same segment/price

## References

Store research findings in `~/skills/car-picker/references/`:
- `current_research.md` - Active car search notes
- `price_history.md` - Tracked prices over time
- `shortlist.md` - Cars under consideration
