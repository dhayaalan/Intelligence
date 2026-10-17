# Sential Intelligence — Clue-to-Clue Multi-Stage Investigation Execution Flow

**Document Version**: 2.0.0  
**Date**: October 17, 2026  
**Status**: Realization Complete & Verified  

---

## 1. Architectural Philosophy

An investigation is an evidence-driven progression from an initial observable seed to verified discoveries, candidate hypotheses, specialized multi-module pivots, and an interconnected topological graph:

```
Seed Observable (Phone/Email/Name/Plate/Domain/IP)
     │
     ▼
[Stage 1: Deterministic Syntax & Authority Validation]
     │
     ├── Invalidation ──► Truthful Zero-Match Rejection (No Hallucination)
     │
     └── Validation   ──► Canonical Normalized Identifier
                             │
                             ▼
                 [Stage 2: Primary Module Execution]
                             │
                             ▼
                 [Stage 3: Evidence Extraction & Provenance Attribution]
                             │
                             ▼
                 [Stage 4: Multi-Stage Pivot Queue Generation]
                             │
         ┌───────────────────┼───────────────────┬───────────────────┐
         ▼                   ▼                   ▼                   ▼
    [OSINT & Handle]   [Social & Media]     [Threat Intel]     [Geo & News]
    Username Probers    YouTube Discovery   Passive DNS/Certs   Map & Timeline
         │                   │                   │                   │
         └───────────────────┴───────────────────┴───────────────────┘
                             │
                             ▼
             [Stage 5: Evidentiary Edge & Node Dual-Persistence]
                  (MongoDB Repositories + Neo4j Graph)
                             │
                             ▼
             [Stage 6: Real-Time Investigator Workspace]
             (Graph Studio, Live Telemetry, Dossier Cards)
```

---

## 2. Investigation Stage Specifications

### Stage 1: Input Syntax & Root Identifier Validation
- **Phone Numbers**: Evaluated against ITU-T E.164 via Google's `phonenumbers` library. Parsed into canonical E.164 (`+<country_code><national_number>`). Strict rejection of digit-overlap, partial strings, or letters.
- **Email Addresses**: Evaluated against RFC 5322 syntax. Normalizes domain to lowercase while preserving local-part semantics.
- **Vehicle Plates**: Normalized against regional transport office alphanumeric formatting (e.g., standard Indian MoRTH / US DMV regex).
- **Domains & IPs**: Strict FQDN and RFC 791/2460 IP address validation.
- **Zero-Match Discipline**: If an exact identifier does not exist in authoritative provider registries or verified storage, the system returns an honest `ZERO_MATCHES` result. It **never** falls back to full-text or fuzzy search to fabricate an unrelated identity.

### Stage 2: Initial Module Execution
- Identifiers route to their authoritative validation provider (`telecom_intelligence` for phones, `vehicle_intelligence` for plates, passive DNS for domains).
- Seed entities are registered with `confidence=None` (or unassessed) and `sources=["search_query"]`. They **never** receive false 100% verification simply for being typed into the search bar.

### Stage 3: Child Entity Extraction & Provenance Preservation
When a provider yields findings, every discovered child entity retains explicit provenance:
- Canonical type (normalized to `PHONE`, `EMAIL`, `PERSON`, `ORGANIZATION`, `VEHICLE`, `DOMAIN`, `IP`, `LOCATION`, `ARTICLE`, `VIDEO`, `IMAGE`, `POST`, `EVIDENCE`, `THREAT_INDICATOR`, `KEYWORD`).
- Source provider ID and module ID.
- Parent entity value and type.
- Collection and publication timestamps.
- Supporting evidence records with cryptographic hashes.

### Stage 4: Multi-Stage Dynamic Pivot Queue
Rather than stopping at the first query or displaying speculative suggested links, the system schedules justified follow-up jobs:
1. **Discovered Organization** (e.g. `Reliance Jio Infocomm` or `Acme Corp`):
   - Enqueued to `news_intelligence` to locate corporate developments and reporting.
   - Enqueued to `threat_intelligence` for digital infrastructure footprint.
2. **Discovered Location / Jurisdiction** (e.g. `India` or coordinates):
   - Enqueued to `geo_intelligence` to pull verified geographic boundaries and location observations.
   - Enqueued to `news_intelligence` for regional incidents.
3. **Discovered Username / Candidate Handle** (e.g. `lead_analyst`):
   - Enqueued to `social_media_intelligence` for cross-platform public footprint and YouTube video discovery.
4. **Discovered Domain**:
   - Enqueued to `threat_intelligence` for passive DNS, certificate transparency logs, and IP mapping.

### Stage 5: Dual-Persistence with Graph Integrity
- **MongoDB**: Complete raw JSON payloads, evidence items, and tenant-scoped collection records.
- **Neo4j**: Normalized entity nodes with sanitized relationship types (`USES`, `RESOLVES_TO`, `CONNECTED_TO`, `HOSTED_ON_IP`, `LOCATED_AT`, `PUBLISHED`).
- Edges carry `evidence_ids`. Relationships without evidence are rejected from confirmed status.
- Shared nodes are preserved across branches during expansion and collapse.

---

## 3. Concrete Investigation Scenarios

| Initial Clue | Stage 1 (Validation) | Stage 2 (Primary) | Stage 3 (Discoveries) | Stage 4 (Follow-up Searches) | Final Topological Chain |
|---|---|---|---|---|---|
| `+442079460991` | Canonical E.164 Phone | OSINT Telecom | Carrier: `British Telecom`, Jurisdiction: `United Kingdom` | News & Geo search on `United Kingdom` and `British Telecom` | `Phone -> USES -> Carrier`, `Phone -> RESOLVES_TO -> UK Location` |
| `analyst@cyber-defense.corp` | RFC 5322 Email | OSINT Corporate | Domain: `cyber-defense.corp`, Handle: `analyst` | Threat Intel on domain, Social Recon on handle | `Email -> CONNECTED_TO -> Domain -> HOSTED_ON -> IP` |
| `c2-mesh-ingress.net` | FQDN Domain | Threat Intel | Resolved IP: `198.51.100.88`, SSL Cert | Reverse DNS on IP, Passive ASN attribution | `Domain -> HOSTED_ON_IP -> IP -> ROUTED_THROUGH -> ASN` |
| `MH12AB1234` | MoRTH Vehicle Plate | Vehicle Recon | RTO: `Pune, Maharashtra`, Class: `LMV` | Geo Intelligence on `Pune, Maharashtra` | `Plate -> REGISTERED_AT -> RTO -> LOCATED_AT -> Pune` |

