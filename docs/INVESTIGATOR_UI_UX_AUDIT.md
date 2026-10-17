# Investigator-First UI/UX Audit and Architecture

## 1. Investigator Persona and Cognitive Context

The primary users of the Sentinel Intelligence platform include intelligence analysts, fraud investigators, and law-enforcement personnel—many of whom are over 40 years old and prioritize:
- **Speed to Evidence**: Locating relevant names, phone numbers, addresses, and images with the fewest possible clicks.
- **High Readability**: Clear, comfortable typography (14–16px body copy) and high visual contrast, avoiding microscopic gray-on-gray developer text.
- **Truthful Statuses**: Obvious distinctions between verified facts, source claims, candidate matches, and unverified leads.
- **No Hidden Features**: Core intelligence categories (Images, Videos, Profiles, News) must be directly accessible from the main results header, not tucked away in nested sub-menus.

---

## 2. Key UI/UX Overhauls Implemented

### A. Concise 7-Metric Investigator Banner
Directly above the result workspace, a high-contrast executive summary presents the essential facts of the search run:

```
+---------------------------------------------------------------------------------------------------+
| TARGET TYPE | SOURCE RECORDS | EXECUTED PROV | RESTRICTED/UNAVAIL | ENTITIES | MEDIA | EV/LEADS   |
|   PHONE     |       14       |       6       |         1          |    12    | 4(3/1)| 14 / 3     |
+---------------------------------------------------------------------------------------------------+
```
- **Zero Conflation**: Provider count is kept strictly separate from discovered entity count and source evidence record count.
- **1-Click Jump**: Clicking the "Media" cell instantly activates the Images tab.

### B. Standardized Tab Hierarchy
The navigation bar conforms strictly to the master engineering specification:
1. `Overview`: High-level command center, key findings, and pipeline status.
2. `All Results`: Complete searchable entity ledger with card and table view modes.
3. `Profiles`: Discovered social media handles, developer profiles, and avatar cards.
4. `Images`: Visual intelligence extracted across all evaluated providers.
5. `Videos`: Video broadcasts and YouTube intelligence with embedded player support.
6. `News`: Curated news stories and wire reports with publisher provenance.
7. `Infrastructure & Threats`: Threat intelligence indicators, CVEs, and Shodan telemetry.
8. `Locations`: Geospatial coordinates plotted on an interactive map.
9. `Evidence`: Cryptographic SHA-256 evidence vault with 1-click hash copy.
10. `Graph`: Interactive link analysis knowledge graph.

### C. Accessibility & Ergonomics
- **Full Keyboard Navigation**: Media modal supports `Escape` and focus trapping.
- **Card and Table Dual Mode**: Investigators can switch between visual entity cards and high-density tabular spreadsheets.
- **Direct Linkouts**: Verified external sources link out in separate secure tabs with `rel="noopener noreferrer"`.
- **Zero Stale Data**: Executing a new search wipes all previous query states, preventing confusion between consecutive investigations.
