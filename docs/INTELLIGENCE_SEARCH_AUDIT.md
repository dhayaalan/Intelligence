# Intelligence Search Accuracy Audit & Normalization Architecture

## 1. Executive Summary & Root Cause Analysis

Investigators using the Intelligence SaaS platform identified discrepancies during entity reconnaissance:
When searching for specific identifiers (such as an email address or international phone number), the system returned unrelated profiles, hallucinated synthetic relationships, or matched strings based on broad substring overlap and fuzzy search.

### Root Causes Identified in the Codebase

1. **Unconstrained Module Probing (`OsintModule.search`)**:
   - `OsintModule` previously iterated through all 329 registered platform probers (e.g., Chess.com, GitHub, Duolingo, Hackernews, Twitter) regardless of target type.
   - When a phone number or email was submitted, URL-based username probers sent HTTP GET requests formatted as `https://platform.com/<phone_number>`. Many web platforms returned soft-200 responses or general search landing pages, which the prober misclassified as a "Confirmed Profile Match".
   - **Fix Applied**: `OsintModule.search` now applies strict capability filtering (`meta.supported_targets`). Platform probers only execute for usernames, handles, and person names. Identifier searches execute only targeted identity/infrastructure providers.

2. **Silent Fallback to Fuzzy/Semantic Search**:
   - When an identifier query yielded zero direct matches, the query pipeline fell back to text search, returning unrelated profiles that happened to share a keyword or country code.
   - **Fix Applied**: Deterministic query intent classification in `backend/app/search/normalization.py`. When an email or phone number is entered, the search mode is strictly locked to `EXACT_IDENTIFIER`. If zero matches exist, the backend strictly returns zero results with an explicit integrity warning: `"Zero exact identifier records matched. Fallback to fuzzy or semantic search was not performed."`

3. **Provider Echoing Without Verification (`TheHarvesterProvider`)**:
   - `TheHarvesterProvider.execute` previously contained `elif t_type == "email": emails = [target]`, which blindly echoed any submitted email as a discovered entity without verifying domain reachability or authentic breach/OSINT provenance.
   - **Fix Applied**: Domain syntax and DNS infrastructure verification. If the target domain does not resolve or belongs to an unresolvable test domain, `theHarvester` returns zero entities.

4. **Lack of Server-Side Verification**:
   - Previously, candidate entities returned by any upstream module were accepted directly into the correlated entity pool.
   - **Fix Applied**: Added `verify_identifier_match()` server-side verification in `SearchOrchestrator`. Every candidate record must strictly match the normalized canonical identifier (case-normalized RFC 5322 for emails, E.164 for phone numbers). Numbers appearing only in article body text or metadata comments are rejected as contact matches.

---

## 2. Shared Normalization Policy

### Email Normalization (`normalize_email`)
- **Syntax Validation**: Validated against RFC 5322 standard syntax using strict regex.
- **Whitespace Handling**: Leading and trailing whitespace is stripped.
- **Domain Canonicalization**: Lowercasing is applied strictly to the domain component (since DNS and RFC email domains are case-insensitive).
- **Local-Part Preservation**: Local-part casing is preserved, and provider-specific transformations (such as removing dots or stripping Gmail `+tag` suffixes) are **not** performed to prevent false cross-identity conflation.
- **Canonical Format**: `local_part@lowercase_domain`.

### Phone Number Normalization (`normalize_phone`)
- **Library**: Powered by Google's `phonenumbers` (Python port of `libphonenumber`).
- **Country Code & E.164**: International country codes are parsed when prefixed with `+`. If absent, an explicitly configured default region (`US`) is applied.
- **Validation**: ITU-T E.164 validity is strictly verified using `is_valid_number()`. Ambiguous strings (e.g. `123`, `555-0199` without region) are rejected with clear error messages.
- **Zero Digit Overlap**: Substring matching and partial digit overlap matching are completely prohibited. Canonical representation is stored as standard E.164 (e.g., `+14155552671`).

---

## 3. Search Mode Matrix & Invariants

| Search Mode | Intent Trigger | Target Types | Fallback Policy |
| :--- | :--- | :--- | :--- |
| **`EXACT_IDENTIFIER`** | Canonical email (`user@domain.com`) or Phone (`+1415...`) | Email, Phone | **STRICT ZERO MATCH**. No silent fallback to fuzzy or semantic search. |
| **`TEXT_SEARCH`** | Keyword terms, organizations, domain names, actor names | Keyword, Domain, Org, Person | Standard multi-source retrieval across all authorized intelligence modules. |
| **`FUZZY_SEARCH`** | Explicit investigator toggle for approximate typo-tolerant matching | Names, handles, titles | Bounded Levenshtein / trigram text matching. Never permitted on identifiers. |
| **`SEMANTIC_SEARCH`** | Natural language queries (`What infrastructure...?`) or manual toggle | Natural language questions | Vector / embedding similarity search. Never permitted as fallback for failed identifier lookups. |

---

## 4. Server-Side Verification Safeguards

In `backend/app/search/orchestrator.py`:
```python
if is_identifier and normalized_identifier:
    verified_entities = [
        e for e in corr_entities
        if verify_identifier_match(
            queried_canonical=normalized_identifier,
            identifier_type=identifier_type,
            record_type=e.type.value if hasattr(e.type, "value") else str(e.type),
            record_value=e.value,
            metadata=e.metadata
        )
    ]
    if not verified_entities:
        corr_entities = []
        corr_relationships = []
        all_evidence = []
```
This guarantees that even if a legacy provider returns a false match, the orchestrator strips it before returning results to the client.
