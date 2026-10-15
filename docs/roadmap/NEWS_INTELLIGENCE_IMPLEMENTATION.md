# Advanced News Intelligence & Claim Verification Architecture

## Overview
This document specifies the News Intelligence and Evidence Verification architecture implemented in `backend/app/modules/news_intelligence/`.

---

## 1. Verified Evidence States

The system strictly avoids manufactured confidence scores or synthetic claims. All claim evaluations adhere to the `ClaimMatrixStatus` enum:

| Evidence Tier | Code | Criteria |
| :--- | :--- | :--- |
| **Corroborated** | `CORROBORATED` | Independently verified across 2 or more distinct journalistic newsrooms with separate reporters. |
| **Contradicted** | `CONTRADICTED` | Explicitly debunked or contradicted by an IFCN-verified fact-checking organization (e.g. Snopes, PolitiFact) or primary investigative evidence. |
| **Disputed** | `DISPUTED` | Conflicting primary accounts between credible reporting publishers. |
| **Single-Source Repeated** | `SINGLE_SOURCE_REPEATED` | Multiple outlets repeating identical wire agency copy (e.g. AP, Reuters, AFP) without independent reporting. Wire syndication is explicitly not counted as independent corroboration. |
| **Unverified** | `UNVERIFIED` | Single-outlet report lacking secondary confirmation. |
| **Insufficient Evidence** | `INSUFFICIENT_EVIDENCE` | No verifiable publishers, wire dispatches, or archives found for the target claim. |

---

## 2. Fact-Checking Integration

### 2.1 Google Fact Check Tools API (`FactCheckService`)
- **Endpoint:** `https://factchecktools.googleapis.com/v1alpha1/claims:search`
- **Query Parameters:** Natural language claim or subject matter query.
- **Data Retrieved:**
  - Claimant entity and statement date
  - Reviewing publisher (e.g., *PolitiFact*, *The Washington Post Fact Checker*, *Lead Stories*)
  - Textual rating (*False*, *Misleading*, *Pants on Fire*, *True*)
  - Direct canonical fact-check article URL
- **Operational Status:**
  - When `GOOGLE_FACT_CHECK_API_KEY` is present: `WORKING_TESTED_REAL`
  - When key is omitted: Transparently reports `CONFIG_REQUIRED` without fabricating fake ratings.

---

## 3. Dynamic Multilingual Regional Analysis

- **Dynamic Regional Derivations:** Removed all static template strings. Regional framing, tone, and publisher perspective comparisons are dynamically computed from actual retrieved news articles and publisher origin metadata.
- **Fail-Closed Egress Verification:** If a search requests regional collection (e.g. `IN_MUMBAI` or `US_EAST`) and the verified egress route is inactive, the system fails closed rather than returning misleading local results from an unverified egress path.
