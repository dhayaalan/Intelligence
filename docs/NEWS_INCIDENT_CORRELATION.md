# News Intelligence & Incident Correlation Architecture

## 1. Overview & Pipeline Integrity

The News Intelligence Investigation Engine correlates global public reporting, wire services, and multimedia evidence with investigated entities and incidents.

To prevent misattributing incidents to individuals or counting syndicated duplicates as independent corroborations, Sential enforces strict correlation invariants.

---

## 2. End-to-End Query Options Pass-Through

Search queries and UI filters pass directly through the orchestration pipeline into `NewsSearchRequest` rather than collapsing into fixed generic searches:

| Filter Parameter | Target Behavior in Search Engine |
| :--- | :--- |
| **Search Mode** | `SEMANTIC`, `EXACT`, `BOOLEAN`, `ENTITY`, `TEMPORAL`, `GEOGRAPHIC`. |
| **Date Range / Time Filter** | Temporal boundaries (`today`, `week`, `month`, or `YYYY-MM-DD..YYYY-MM-DD`). Articles outside the window are excluded. |
| **Event Location** | Geographic boundary for where the incident physically took place (distinct from the country of the publisher). |
| **Publisher / Source** | Filtering by specific wire services or media domains. |
| **Country & Language** | Multi-country comparative matrix and ISO 639-1 language routing. |
| **Min Relevance** | Numerical threshold (0-100%) filtering low-signal keyword occurrences. |

---

## 3. Evidentiary Incident Relationship Classification

When associating an article, claim, or incident with an investigated entity, the platform assigns one of five standardized relationship grades:

1. **`DIRECTLY_SUPPORTED`**: The article provides primary documentation, official records, or direct eyewitness observation corroborating the entity's participation or presence.
2. **`SOURCE_REPORTED`**: The relationship is asserted by a third-party journalist or news outlet. It is attributed to the publisher with byline provenance.
3. **`POSSIBLE_ASSOCIATION`**: The entity and incident co-occur in the same report, but the text does not assert direct causality or participation.
4. **`CONTRADICTED`**: Independent wire reporting or fact-checking investigations directly refute the claimed association.
5. **`INSUFFICIENT_EVIDENCE`**: Mentions exist but lack sufficient corroborating facts to draw an analytical conclusion.

> [!IMPORTANT]
> A person's name appearing in an article reporting on a crime or incident NEVER automatically proves their guilt, attendance, or participation. Sential preserves this distinction at the graph and relationship layer.

---

## 4. Syndication vs. Independent Source Corroboration

A major pitfall in automated open-source analysis is treating five syndicated copies of an AP or Reuters wire story as five independent confirmations.

Sential’s `SourceLineageEngine` resolves this:
- **Original Source**: The primary origin or wire agency that broke the reporting.
- **Syndicated Copies**: Outlets that reprinted the wire verbatim or near-verbatim.
- **Independence Score**: Syndicated reprints inherit the origin wire's evidence and are flagged as `is_duplicate_copy = True`. They contribute zero additional independent corroboration weight to confidence scores.

---

## 5. Article & Media Association Integrity

- **Deterministic 1-to-1 Image Binding**: Every article retains its own stable `article_id`, canonical URL, and verified OpenGraph / Twitter lead image extracted directly from the article's URL metadata.
- **Strict Prohibition of Array-Index Fallback**: Under no circumstances does the engine map an image to an article based on array index position.
- **Neutral Placeholder Rendering**: When an article lacks verified lead imagery or its OpenGraph image fails reachability validation, the system renders a clean, neutral SVG placeholder. It never reuses unrelated imagery from adjacent stories.
