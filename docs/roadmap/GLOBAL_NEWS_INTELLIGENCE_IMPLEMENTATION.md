# GLOBAL NEWS INTELLIGENCE — SYSTEM ARCHITECTURE & IMPLEMENTATION REPORT

## 1. Executive Summary

The News Intelligence module in `sentinel-saas` has been upgraded from a regional/localized prototype into a **Worldwide News Intelligence System** capable of continuous news discovery, multi-country comparative analysis, and evidence-backed claim verification across all **249+ recognized countries and territories** (ISO 3166-1 alpha-2 and alpha-3).

The implementation strictly adheres to the principle of **Zero Synthetic Fallbacks & No Hardcoded Countries**:
- It never restricts searches to a hardcoded list like US/UK/India.
- It dynamically resolves canonical names, codes, recognized languages, regional groupings, and top-level domains.
- It maintains strict forensic separation between **where an article was published** (`publisher_country`) and **where the reported event took place** (`event_location`).
- VPN egress IP or tunnel exit countries are never conflated with publisher origin.
- Side-by-side country comparisons evaluate genuine retrieved records, computing real source independence metrics, dominant framings, and explicit coverage gaps.

---

## 2. Dynamic Country & Territory Registry

The core foundation is the `GlobalCountryRegistry` located in:
`backend/app/modules/news_intelligence/country_registry.py`

### Key Architectural Capabilities:
1. **ISO 3166-1 Alpha-2 and Alpha-3 Completeness**:
   - Covers 249+ countries, sovereign nations, dependent territories, and special administrative zones across all 5 continental regions (Americas, Europe, Asia, Africa, Oceania) and Polar zones.
2. **Multi-Key Fast Indexing**:
   - `_alpha2_index`: Instant $O(1)$ lookup by 2-letter ISO code (`FR`, `DE`, `IN`, `NG`, `BR`).
   - `_alpha3_index`: Instant $O(1)$ lookup by 3-letter ISO code (`FRA`, `DEU`, `IND`, `NGA`, `BRA`).
   - `_name_index`: Case-insensitive canonical name and alias lookup (`United States`, `USA`, `Bharat`, `Deutschland`, `Russian Federation`).
   - `_tld_index`: Country-code top-level domain lookup (`.de`, `.fr`, `.in`, `.co.uk`, `.jp`, `.br`).
3. **Dynamic Source Management**:
   - Exposes `register_custom_source()` allowing investigators and administrators to add verified publisher feeds, regional broadcaster endpoints, and official gazettes at runtime without modifying source code.
4. **Honest Operational Status**:
   - Countries with verified, operational sources are designated `WORKING_TESTED_REAL`.
   - Selectable countries without configured RSS/APIs are marked `NO_SOURCES_CONFIGURED` or `UNVERIFIED_COVERAGE` rather than faking coverage.

---

## 3. Investigation Modes

The system supports three distinct search and comparative intelligence modes:

### A. Worldwide Search (`is_worldwide=True`, `countries=["WORLDWIDE"]`)
- Searches all configured global news providers (Google News Multi-Country Editions, GDELT 2.0 Global Doc Archive, Bing News Worldwide Multi-Region, YouTube Intelligence) without requiring manual country selection.
- Asynchronously queries diverse national editions (e.g., US, GB, FR, DE, JP, IN) with bounded concurrency.
- Aggregates results into normalized records and computes a dynamic global coverage summary.

### B. Single-Country Search (`countries=["<ISO2>"]`)
- Targets a specific country from the registry (e.g., `FR` for France, `JP` for Japan, `BR` for Brazil).
- Configures provider-specific parameters (e.g. Google News `gl=<ISO2>&hl=<lang>`, national domain filters, local TLD restrictions).
- Reports exactly which geographic edition filters were applied.

### C. Multi-Country Simultaneous Comparison (`compare_countries=True`, `countries=["FR", "DE", "IN", ...]`)
- Executes independent collection scopes for each selected country against the same event, topic, or claim.
- Generates a side-by-side **Country Comparison Matrix** containing:
  - `article_count`: Observed retrieved articles.
  - `source_count`: Number of distinct media outlets.
  - `languages_detected`: Original languages represented.
  - `source_independence_score`: Ratio of independent reporting vs wire copies/syndicates (0–100%).
  - `earliest_publication` & `latest_update`: Chronological progression across timezones.
  - `primary_headline`: Leading domestic framing for that country.
  - `dominant_framing`: Stance and narrative perspective (`SUPPORTIVE`, `CRITICAL`, `ALARMIST`, `NEUTRAL`).
  - `coverage_gaps`: Explicit forensic notice of missing primary sources, syndication echo chambers, or lack of visual evidence.

---

## 4. The Six Geographic Dimensions

Every collected article and search result enforces strict separation across 6 distinct geographic and technical attributes:

| Dimension | Attribute Name | Description | Verification Method |
|---|---|---|---|
| 1. Publisher Country | `publisher_country` & `publisher_country_code` | Sovereign country of the news organization or publisher. | Extracted from canonical publisher registry, known outlet directory, or national TLD. |
| 2. Original Language | `original_language` | Primary language in which the piece was authored. | Retained from raw feed metadata or provider locale parameter. |
| 3. Event Location | `event_location` | Location where the reported incident or summit occurred. | Extracted from verified geopolitical entities and city/state indicators in text. |
| 4. Article Perspective | `article_subject_country` | Country or geopolitical entity being discussed. | Correlated from entity extraction and claim targets. |
| 5. Source Edition | `source_edition` | Regional provider edition used during query fan-out. | Tracked explicitly (e.g. `US`, `GB`, `FR`, `DE`, `JP`, `IN`, `GLOBAL`). |
| 6. Collection Route | `collection_route` | Egress network route utilized for retrieval. | Labeled `DIRECT` or verified `VPN-<REG>` (never conflated with publisher origin). |

---

## 5. Frontend Global News Intelligence Workspace

The web application workspace (`frontend/src/features/news_intelligence/`) has been upgraded with:

1. **Global Country Registry Selector**:
   - Dynamic select menu populated directly from `/api/v1/news/countries`, indexing 249+ countries and territories by name, ISO code, and continental region.
2. **Worldwide & Comparison Toggles**:
   - Checkbox controls for "Worldwide Multi-Provider Discovery" and "Compare Countries (Simultaneous Matrix)".
3. **Dynamic `<CountryComparisonTable>` Component**:
   - Renders side-by-side comparative rows showing article volume, source independence progress bars, dominant framing badges, primary domestic headlines, and coverage gap alerts.
4. **Forensic Geographic Dimension Badges**:
   - Each article card prominently displays distinct color-coded badges for Publisher Country (`Globe`), Event Location (`MapPin`), Language (`[EN/FR/DE]`), Edition (`ed:FR`), and Egress Route (`DIRECT`).

---

## 6. Verification and Test Results

The implementation is verified with automated tests covering all 14 aspects of global news intelligence:
- ISO 3166-1 completeness (249+ countries).
- Code/alias resolution.
- Dynamic source addition.
- Strict separation of publisher country vs event location.
- Multi-country comparison matrix generation.
- Zero synthetic fallbacks and honest coverage reporting.
- API endpoints (`GET /countries`, `GET /countries/{code}`, `GET /coverage-summary`, `POST /sources`, `POST /compare`).

**Test Command**: `python3 -m pytest backend/tests/test_global_news_intelligence.py -v`
**Result**: 14 passed, 0 failed in 10.95s.
**Full Suite Regression Check**: 95 passed across all repository modules.
