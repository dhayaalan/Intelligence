# Entity Resolution & Evidentiary Provenance Architecture

## 1. Core Principles of Forensic Disambiguation

In real-world intelligence investigations, false positive entity merges are fatal errors. Merging two individuals because they share a common name, username handle, avatar, or proximate location leads to erroneous conclusions and legal liabilities.

Sential adheres to these strict rules:

1. **Anti-Hallucination Invariant**: Discovered clues are never linked by heuristic guess. Uncertainty is explicitly preserved.
2. **Deterministic Identifier Equality**: Emails, telephone numbers, and vehicle registration plates must match by exact canonical value. An email mentioning a name does not prove ownership of another record bearing the same name.
3. **Competing Identity Preservation**: When multiple profiles or identities share similar attributes, they are rendered as competing candidate nodes rather than merged into a single entity.
4. **Explicit Evidentiary Basis**: Every relationship payload requires an auditable justification and methodology tag.

---

## 2. Canonical Identifier Normalization Policies

| Clue Type | Normalization Policy | Comparison Standard | Prohibited Heuristics |
| :--- | :--- | :--- | :--- |
| **Email Address** | Trims whitespace; validates RFC 5322 syntax; lowercases domain; preserves local part casing. | Exact string equality of `canonical_email` (`local@domain.lower()`). | NEVER strips Gmail dots; NEVER strips plus-addressing suffixes (`+tag`); NEVER falls back to fuzzy match. |
| **Phone Number** | Formats into ITU-T E.164 via `phonenumbers` library (`+<country><national>`). | Exact E.164 equality. | NEVER performs partial suffix or digit overlap matching; NEVER assumes phone carrier implies subscriber device location. |
| **Vehicle Plate** | Strips spacing and hyphens; converts to uppercase; identifies jurisdiction format. | Exact plate equality within declared or detected jurisdiction. | NEVER scrapes restricted DMV records; NEVER assumes driver identity or home location from plate alone. |
| **Username / Handle** | Normalizes leading `@`; lowercase platform account identity. | Exact username within same platform domain. | NEVER merges accounts across platforms based on username handle collision alone. |
| **Domain / Hostname** | Lowercase FQDN; extracts registrable domain via PSL. | Exact hostname / domain match. | Incidental hyperlink mention does not imply infrastructure ownership. |

---

## 3. Relationship Basis Taxonomy

Every `RelationshipPayload` in the system declares an explicit evidentiary basis:

```python
class RelationshipBasis(str, Enum):
    DIRECT_OBSERVATION = "DIRECT_OBSERVATION"          # Observed directly in verified telemetry or file
    EXPLICIT_SOURCE_STATEMENT = "EXPLICIT_SOURCE_STATEMENT"  # Declared directly by publisher or official record
    MATCHING_IDENTIFIER = "MATCHING_IDENTIFIER"        # Confirmed via exact normalized identifier equality
    SOURCE_REPORTED = "SOURCE_REPORTED"                # Attributed to third-party reporting (subject to corroboration)
    MULTI_HOP_PIVOT_DISCOVERY = "MULTI_HOP_PIVOT_DISCOVERY" # Discovered via bounded secondary pivot exploration
    INFERRED_COORDINATION = "INFERRED_COORDINATION"    # Algorithmic pattern detection (e.g. CIB botnet synchronization)
    POSSIBLE_ASSOCIATION = "POSSIBLE_ASSOCIATION"      # Weak co-occurrence requiring investigator corroboration
    ANALYST_ASSERTION = "ANALYST_ASSERTION"            # Manually added by investigator with case notes
    CONTRADICTED = "CONTRADICTED"                      # Conflicting or disputed relationship
```

---

## 4. Evidentiary Traceability & Audit Vault

Every entity and relationship references its supporting `EvidencePayload`:

- **Evidence ID**: Unique identifier `ev_<hash>`.
- **Source Provider**: Authenticated provider name (e.g., `exif_metadata_extractor`, `rss_aggregator`).
- **Collection Timestamp**: Exact ISO 8601 UTC timestamp of retrieval.
- **Reference / URL**: Canonical web link or document reference.
- **Raw Data Artifact**: Unaltered raw payload preserved for chain-of-custody verification.
- **Confidence Score**: Quantitative score (0.0 to 1.0) derived strictly from source reliability and verification quality, never hardcoded.
