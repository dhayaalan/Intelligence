# Sential Intelligence — Graph Persistence, Schema, and Entity Types

**Document Version**: 2.0.0  
**Date**: October 17, 2026  
**Status**: Realization Complete & Verified  

---

## 1. Unified Canonical Entity Category Taxonomy

To eliminate the defect where phone numbers, accounts, or keywords defaulted silently to `DOMAIN`, all frontend components and backend persistence models adhere to an explicit, normalized taxonomy:

| Canonical Category | Supported Raw Types & Aliases | Color Token | SVG Icon Representation |
|---|---|---|---|
| **`PHONE`** | `PHONE`, `TELEPHONE`, `MSISDN`, `CELL`, `MOBILE`, `PHONE_NUMBER`, `TEL` | Sky (`#0284c7`) | Telephone handset |
| **`EMAIL`** | `EMAIL`, `MAILBOX`, `EMAIL_ADDRESS` | Teal (`#0d9488`) | Mail envelope |
| **`PERSON`** | `PERSON`, `NAME`, `USERNAME`, `ACCOUNT`, `THREAT_ACTOR`, `AUTHOR`, `ACTOR`, `PROFILE`, `USER`, `INDIVIDUAL` | Amber (`#f59e0b`) | User silhouette |
| **`ORGANIZATION`** | `ORGANIZATION`, `ORG`, `COMPANY`, `GROUP`, `NGO`, `FOUNDATION`, `TERROR_GROUP`, `GOVERNMENT`, `AUTHORITY`, `REGISTRY`, `ENTERPRISE` | Indigo (`#6366f1`) | Corporate building |
| **`VEHICLE`** | `VEHICLE`, `CAR`, `AUTOMOBILE`, `PLATE`, `VEHICLE_PLATE`, `ASSET` | Purple (`#8b5cf6`) | Motor vehicle |
| **`DOMAIN`** | `DOMAIN`, `SUBDOMAIN`, `HOSTNAME`, `FQDN`, `WEBSITE`, `URL`, `URI`, `VHOST` | Slate (`#64748b`) | Network globe with meridians |
| **`IP`** | `IP`, `IPV4`, `IPV6`, `IP_ADDRESS`, `CIDR`, `SUBNET` | Blue (`#2563eb`) | Server rack nodes |
| **`LOCATION`** | `LOCATION`, `GEO`, `COORDINATES`, `PLACE`, `CITY`, `COUNTRY`, `STATE`, `REGION`, `ADDRESS`, `JURISDICTION` | Cyan (`#06b6d4`) | Map pin marker |
| **`ARTICLE`** | `ARTICLE`, `NEWS`, `DOCUMENT`, `REPORT`, `PUBLICATION` | Emerald (`#10b981`) | Document sheet with text lines |
| **`VIDEO`** | `VIDEO`, `YOUTUBE_VIDEO`, `CHANNEL` | Red (`#ef4444`) | Video player rectangle with play glyph |
| **`IMAGE`** | `IMAGE`, `PHOTO`, `AVATAR`, `PICTURE` | Pink (`#ec4899`) | Camera / photo frame |
| **`POST`** | `POST`, `TWEET`, `STATUS`, `SOCIAL_POST`, `THREAD`, `COMMENT` | Lime (`#84cc16`) | Chat message bubble |
| **`EVIDENCE`** | `EVIDENCE`, `RECORD`, `CERTIFICATE`, `PROOF` | Teal (`#14b8a6`) | Shield with checkmark |
| **`THREAT_INDICATOR`** | `VULNERABILITY`, `CVE`, `THREAT_INDICATOR`, `MALWARE`, `THREAT`, `EXPLOIT`, `IOC`, `ATTACK_VECTOR` | Rose (`#f43f5e`) | Alert shield with exclamation point |
| **`HASH`** | `HASH`, `SHA256`, `MD5`, `SHA1` | Purple (`#a855f7`) | Cryptographic digest symbol |
| **`KEYWORD`** | `KEYWORD`, `TAG`, `SEARCH_TERM`, `QUERY`, `TOPIC` | Zinc (`#71717a`) | Hash tag / metadata tag |
| **`UNKNOWN`** | *Any unmapped or unrecognized value* | Gray (`#94a3b8`) | Dashed circle with node center |

> [!IMPORTANT]
> `getEntityCategory()` strictly returns `'UNKNOWN'` for any unrecognized type. It **never** falls back to `'DOMAIN'`.

---

## 2. Dual-Persistence Architecture

### MongoDB Collections (`sential_db`)
1. **`entities`**: Authoritative entity catalog keyed by unique `id` and `tenant_id`. Stores canonical value, type, calibrated confidence, verified source citations, and extended metadata.
2. **`relationships`**: Directional edges (`source_entity_value` -> `target_entity_value`). Must carry `evidence_ids`. Identity relationships (`OWNS`, `SUBSCRIBER_OF`) without evidence are rejected from confirmed status.
3. **`evidence`**: Raw payloads, provider identifiers, references, and cryptographic hashes (`ev_<id>`).
4. **`investigations`**: Case dossiers, timelines, snapshot telemetry, and key findings.

### Neo4j Graph Database
- **Nodes**: Labeled `(:Entity {id, value, type, tenant_id, confidence, sources, metadata})`.
- **Relationship Types**: Sanitized allowlist (`USES`, `RESOLVES_TO`, `CONNECTED_TO`, `HOSTED_ON_IP`, `LOCATED_AT`, `PUBLISHED`, `OWNS`, `AFFILIATED_WITH`).
- **Index Constraints**: Uniqueness constraints on `Entity(id, tenant_id)` ensure idempotent merges.

---

## 3. Graph Studio & Expansion Semantics

1. **1-Hop Bounded Expansion**:
   - `GET /api/v1/entities/{id}/expand?limit=50`: Traverses immediate verified relationships in Neo4j/MongoDB.
   - Preserves shared nodes: expanding entity A and entity B which both connect to entity C displays C as a shared nexus node.
2. **Branch Collapse Without Orphan Deletion**:
   - Collapsing branch A removes nodes introduced uniquely by A.
   - Any node that also connects to an uncollapsed branch (degree >= 2 in active view) is preserved on the canvas.
3. **Inspector Dossier Verification**:
   - `Unassessed Seed Input` (amber badge): Raw query seed with source `search_query`.
   - `Uncorroborated Graph Lead` (slate badge): Discovered via graph traversal without direct primary evidence.
   - `Registry Corroborated` (green badge): Confirmed by national telecom numbering plan or database record.

