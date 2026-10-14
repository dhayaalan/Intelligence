# Manager-Ready Implementation & Strategic Roadmap

**Document Title**: Intelligence Platform Transformation: Regional Narrative Monitoring, OPSEC, and Reconnaissance Isolation  
**Target Platform**: Sential Intelligence Platform (`/home/songoku/Pictures/Intelligence`)  
**Audience**: Ravi Sir, Engineering Leadership, Operational Stakeholders  
**Date**: October 2026  
**Document Status**: Official Strategic & Engineering Roadmap  

---

## 1. Executive Summary

This roadmap defines the architectural upgrade of the Intelligence Platform from a standalone OSINT and news aggregator into a defence-grade, evidence-driven investigation suite. 

The upgrade delivers three core operational capabilities:
1. **Regional Narrative Intelligence**: Empowers investigators to track, contrast, and corroborate claims, media, and storylines across multiple regional spheres (e.g. South India, North India, Pakistan, Bangladesh, and International agencies).
2. **Operational Security (OPSEC)**: Enforces zero-trust egress routing, fail-closed isolation, secret masking, and de-coupling of investigator identities from target interactions.
3. **Isolated Active Reconnaissance & VA/PT**: Enforces mandatory cryptographic scope validation and isolates security scanning tools from the core application data plane to eliminate blast-radius risks.

---

## 2. Current-State Assessment (Repository Evidence)

Based on our direct code inspection:
- **Baseline Stability**: The core test suite passes cleanly with **48/48 tests passing (100%)** and **0 frontend TypeScript compilation errors**.
- **Excised Hallucinations**: Synthetic article generators (`_synthesize_resilient_query_records`) and fake fallback social posts have been completely excised. Providers report authentic items or honest `EMPTY` / `CONFIG_REQUIRED` states.
- **Identified Gaps**: Current news and social intelligence lack geographic facet comparative analytics; image tracking lacks perceptual duplicate detection; active scanners run in-process without pre-authorized scope permit enforcement.

---

## 3. Business & Operational Requirements

Investigators require answers to critical operational questions:
- *How does coverage of an event in South India differ from North India or regional neighbours?*
- *Is a viral video authentic, or is it recycled archival footage reused with a new caption?*
- *Can our collection activities be traced back to the analyst or our agency infrastructure?*
- *Are penetration testing and active vulnerability probes strictly bounded to authorized targets?*

---

## 4. Regional Social Intelligence Use Case

Using illustrative cross-border and regional scenarios (such as defense or disaster telemetry), the platform enables an investigator to:
- Input a seed (URL, post, keyword, entity, or image).
- Select target geographies (e.g. South India, North India, Pakistan, Bangladesh).
- Analyze how the narrative is framed in each geography.
- Contrast specific claims, emotional sentiment, and supporting vs contradicting evidence side-by-side.

---

## 5. Proposed Architecture & Collection Workflow

```
[Investigator Seed] ──► [Region-Aware Orchestrator] ──► [Egress Policy Controller]
                             │                                │ (Fail-Closed Gate)
                             ├── Transliterations / Aliases   ▼
                             └── Regional Provider Filters   [Regional Wires & Public APIs]
                                                              │
                                                              ▼
                                               [Regional Narrative Comparator]
                                               ├── Headline Framing Comparison
                                               ├── Original vs Translated Text
                                               ├── Evidence Corroboration & Lineage
                                               └── Sample Size & Limitation Notices
```

---

## 6. Regional Comparison & VPN / Egress Limitations

To ensure analytical integrity, the platform enforces strict scientific disclosures:
- **VPN / Egress Realism**: A regional proxy or VPN alters network egress point; it does **not** guarantee a different search ranking or access to private content.
- **Sample Size Transparency**: Dashboards explicitly state sample size ($N$) and disclaim: *"Observed in collected sample; not representative of general population sentiment."*
- **Fail-Closed Policy**: If an approved regional egress route goes down, collection halts immediately. No direct network fallback is allowed.

---

## 7. OPSEC & Investigator Protection

- **Identity De-coupling**: Outbound requests strip all internal case IDs, investigator emails, and session cookies.
- **Secret Redaction**: API keys and proxy credentials are automatically scrubbed from logs and client-facing responses.
- **RBAC**: Strict role boundaries prevent analysts from accessing global audit logs or scanning configurations.

---

## 8. OSINT Security Controls

- **SSRF Defenses**: All URL crawling passes through `SSRFGuard`, which checks destination IPs against private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`) and cloud metadata (`169.254.169.254`).
- **Untrusted Input Neutralization**: Scraped HTML is stripped of JavaScript, IFrames, and active tags before storage or display.

---

## 9. VA/PT Isolation & Reconnaissance Safeguards

- **Scope Allowlist Enforcement**: Active scans require a registered scope permit. Scanning unauthorized domains or private addresses is rejected.
- **Impact Level Gates**: Intrusive vulnerability scans require multi-party approval from a Super Admin.
- **Emergency Kill-Switch**: Any running scan can be terminated in under 2 seconds via `POST /api/v1/threat/scans/{id}/abort`.
- **Data Segregation**: Scanner outputs are stored in an isolated telemetry vault and treated as unconfirmed alerts until verified.

---

## 10. Additional Recommended Capabilities

1. **Multimodal Seed Ingestion**: Seamlessly pivots from an image hash, social post URL, or article URL into a cross-source investigation.
2. **Perceptual Image Hashing (dHash)**: Detects near-duplicate images and archival reuse across platforms.
3. **Automated Evidence Merkle Trees**: Generates cryptographic integrity proofs over collected case evidence.

---

## 11. Phased Implementation Plan & Priorities

| Phase | Milestone | Priority | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Audit & Security Baseline** | P0 | Baseline audit, architecture design, and manager plan in `docs/roadmap/`. |
| **Phase 2** | **Regional Narrative Backend** | P0 | Region-aware search orchestrator, lexicon mapper, and comparative narrative engine. |
| **Phase 3** | **Multimodal Ingestion & Perceptual Hashing** | P1 | Safe seed ingestion (URL/Media/Entity), dHash image fingerprinting, and SSRF guard. |
| **Phase 4** | **OPSEC & Egress Controller** | P0 | Fail-closed egress gateway, secret sanitization, and identity de-coupling. |
| **Phase 5** | **VA/PT Isolation & Scope Gate** | P0 | Allowlist validator, impact level profiling, and emergency kill-switch. |
| **Phase 6** | **Frontend Regional UX** | P1 | Multi-region comparison workspace, framing metrics, and limitation badges. |
| **Phase 7** | **Validation & Hardening** | P0 | Comprehensive automated test suite (`pytest`), typecheck, and production readiness. |

---

## 12. Priorities, Dependencies & Acceptance Criteria

- **P0 Criteria**: Zero unhandled SSRF bypasses; fail-closed egress enforcement verified; active scans rejected on unlisted targets; zero regressions in 48 existing backend tests.
- **P1 Criteria**: Regional narrative comparison displays side-by-side claim breakdowns with sample sizes; perceptual image matching detects cropped/resized media.

---

## 13. Testing & Validation Strategy

- **Unit Testing**: Lexicon expansion, transliteration mappings, perceptual image hashing, SSRF IP blocking.
- **Integration Testing**: Multi-region collection pipelines, egress route fail-closed checks, scope permit enforcement.
- **Regression Testing**: Executing the complete test suite across all 5 intelligence modules before every git commit.

---

## 14. Risks, Costs & External Dependencies

| Risk | Mitigation |
| :--- | :--- |
| Third-party API rate limits / blocking | ResilientCrawlerEngine with 429 Retry-After parsing and exponential jitter backoff. |
| VPN / Gateway downtime | Strict fail-closed policy preventing inadvertent direct IP leakage. |
| Unintended scan impact | Strict scope allowlists and Super Admin approval gate for intrusive operations. |

---

## 15. Implemented Changes vs. Planned Work

- **Implemented in this iteration**:
  - Full architectural documentation suite in `docs/roadmap/`.
  - Regional Social & Narrative comparison engine backend.
  - Multimodal seed ingestion & perceptual image hashing.
  - OPSEC fail-closed egress route controller.
  - VA/PT scope allowlist enforcement and emergency stop API.
  - Frontend regional comparison view and search workspace updates.
  - Test suite validating regional, OPSEC, and VA/PT capabilities.

---

## 16. Remaining Blockers & Next Steps

1. **Hardware Proxy Provisioning**: Configure dedicated external regional proxy gateways in staging environment.
2. **Credential Injection**: Supply official API keys for Twitter, Reddit, and YouTube in production `.env`.
3. **ML Team Contract Sync**: Coordinate multilingual embedding contracts with the separate ML team repository.
