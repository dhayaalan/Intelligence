# Regional Social & Narrative Intelligence Architecture Design

**Repository**: `/home/songoku/Pictures/Intelligence`  
**Standard**: Multi-Source Regional Corroboration & Cross-Border Narrative Intelligence  
**Document Status**: Architectural Specification  

---

## 1. Architectural Vision & Objective

Investigators investigating sensitive cross-border scenarios, narrative campaigns, or public safety emergencies require more than a generic single-query search. They must understand **how a narrative spreads, how it is framed across distinct geopolitical regions, what language variants exist, and what evidence supports or refutes specific assertions.**

This design establishes a high-assurance **Regional Social Intelligence & Narrative Comparison Engine**.

```
                           INVESTIGATOR SEED INPUTS
         ┌───────────────────────────────────────────────────────────┐
         │ Article URL | Social Post | Image Media | Entity | Keyword│
         └─────────────────────────────┬─────────────────────────────┘
                                       │
                                       ▼
                   REGION-AWARE ORCHESTRATION PIPELINE
         ┌───────────────────────────────────────────────────────────┐
         │  Query Expansion: Transliterations | Aliases | Terminology│
         │  Egress Policy: Profile Route Verification | Fail-Closed  │
         └─────────────────────────────┬─────────────────────────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                ▼                      ▼                      ▼
         [Region: South India]  [Region: North India]  [Region: Pakistan]
         - Tamil / Malayalam    - Hindi / English      - Urdu / English
         - Regional Wire Desks  - National Wire Desks  - Regional Outlets
         - Localized Trending   - Localized Trending   - Localized Trending
                │                      │                      │
                └──────────────────────┼──────────────────────┘
                                       │
                                       ▼
                       REGIONAL NARRATIVE COMPARATOR
         ┌───────────────────────────────────────────────────────────┐
         │  • Side-by-Side Framing & Wording Comparison              │
         │  • Cross-Language Claim Alignment (Original + Translated) │
         │  • Evidence Corroboration vs Amplification Tracking       │
         │  • Sample Size & Collection Limitations Disclosure        │
         └───────────────────────────────────────────────────────────┘
```

---

## 2. Seed Ingestion & Multi-Input Processing

The engine accepts heterogeneous investigative seeds:
1. **News Article URL**: Automatically resolves canonical URL, parses title/body, extracts named entities, and generates regional queries.
2. **Social Media Post URL**: Retrieves public post text, hashtags, timestamps, and author handles.
3. **Image / Media Artifact**: Computes cryptographic (SHA-256) and perceptual hashes (dHash/pHash), extracts EXIF metadata, and prepares visual pivot tokens.
4. **Keywords / Entity Identifiers**: Identifies public figures, military units, organizations, or hashtags.

---

## 3. Region-Aware Search Orchestration

### 3.1 Regional Geographies & Lexicon Mapping
Investigations can select multiple target regions to contrast. Built-in geographic profiles include:
- **South India**: Includes English, Tamil, Telugu, Kannada, Malayalam wire services, regional state press releases, and southern district coverage.
- **North India**: Includes English, Hindi, Punjabi national wire bureaus, gazettes, and northern regional publishers.
- **Other Indian Regions**: North-East (Assamese, Bengali, Meitei), Western (Marathi, Gujarati), and Eastern belts.
- **Pakistan**: Federal wire wires (APP), English dailies (Dawn, The News, Express Tribune), Urdu publications (Jang, Dunya), and regional dispatches.
- **Bangladesh**: National press, English dailies (Daily Star), and Bengali wire releases.
- **International**: Global news agencies (Reuters, AP, BBC, AFP, Al Jazeera).

### 3.2 Transliteration & Regional Terminology
The orchestrator maintains an expansion registry that maps core concepts into regional terms and transliterations:
- Example: IAF aircraft / emergency telemetry $\rightarrow$ mapped to Hindi (`वायु सेना`, `विमान`), Tamil (`விமானப்படை`, `விமானம்`), Urdu (`فضائیہ`, `طیارہ`), and Bengali (`বিমানবাহিনী`).
- Preserves exact quotation boundaries and regional aliases.

---

## 4. Regional Narrative Comparison Workflow

For each selected region, the engine normalizes findings and computes comparative telemetry:

| Comparative Dimension | What is Analyzed & Presented | Investigator Value |
| :--- | :--- | :--- |
| **Headline Framing** | Emotive vs neutral framing; loaded terms (e.g., "incursion" vs "patrol", "breach" vs "routine"). | Reveals institutional or state-level editorial alignment. |
| **Claim Breakdown** | Specific factual statements extracted from each regional cluster. | Distinguishes corroborated facts from unverified rhetoric. |
| **Language Lineage** | Original language text displayed side-by-side with translated text. | Prevents loss of nuance or mistranslation artifacts. |
| **Media Reuse** | Cryptographic & perceptual hash matching across regions. | Detects old footage recycled with new regional captions. |
| **Publication Timeline**| Earliest appearance per region with timezone synchronization. | Shows which geography published first and how the narrative migrated. |
| **Limitation Metric** | Sample count ($N$), provider reach, and collection gaps. | Prevents overgeneralizing a small sample to whole populations. |

### 4.1 Strict Scientific Cautions
- **No False Equivalencies**: The system displays: *"Based on $N$ collected public records in this sample; not representative of general population sentiment."*
- **No Co-occurrence Fallacy**: Ten accounts repeating an unverified claim are grouped as **1 narrative cluster with 9 echoes**, not 10 independent confirmations.

---

## 5. Cross-Language Intelligence Policy

1. **Preservation of Original Content**: Original language text is preserved immutably.
2. **Explicit Translation Attribution**: Every translated snippet records `source_language`, `target_language`, and `translation_engine: "deterministic_dictionary"` or future ML engine.
3. **No Silent Overwrites**: Translating a quote never replaces the original characters; both are stored and presented together.
4. **Translation Uncertainty**: Discrepancies between translated idioms are recorded as `linguistic_uncertainty`, not classified as intentional disinformation.

---

## 6. Regional Collection Profiles & Network Egress Control

### 6.1 Profile Model (`RegionalCollectionProfile`)
```python
class RegionalCollectionProfile(BaseModel):
    profile_id: str
    target_region: str
    allowed_providers: List[str]
    preferred_languages: List[str]
    egress_route: str  # "DIRECT", "REGIONAL_GATEWAY_APPROVED", "ISOLATED_SCANNER"
    rate_limit_per_minute: int
    fail_closed: bool = True
    last_verified_at: Optional[str] = None
```

### 6.2 Strict Egress Rules
- **Fail-Closed Guarantee**: If a regional profile specifies `REGIONAL_GATEWAY_APPROVED` and that route is unreachable, collection **aborts immediately** with `EGRESS_UNAVAILABLE`. Direct network leakage is strictly prevented.
- **Zero Stealth / Quota Bypassing**: The platform never uses IP rotation or CAPTCHA solvers to bypass platform terms of service. Egress selection is strictly for authorized geographic viewpoint verification.
- **Credential Segregation**: Regional tokens and gateway secrets are stored in encrypted vaults and never leaked into logs or UI payloads.

---

## 7. Distinguishing Regional Effects

The engine systematically isolates why a result differed between Region A and Region B:
1. **Publisher Geography**: The outlet is physically based in that country.
2. **Query Formulation**: The search terms used localized vocabulary.
3. **Content Availability**: The content was restricted or geo-blocked by the publisher.
4. **Ranking Variance**: The search engine returned different ordering for regional users.
5. **Timeline Variance**: Coverage emerged hours later due to time zones.

Every finding clearly flags which of these dimensions was controlled and which was uncontrolled.
