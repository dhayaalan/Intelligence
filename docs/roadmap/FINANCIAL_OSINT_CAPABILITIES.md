# Financial-Sector, Banking-Institution, and Corporate OSINT Capabilities

## Overview
This document specifies the public corporate and financial-sector intelligence architecture implemented in the Sential Intelligence platform (`backend/app/modules/osint/providers/financial_intel.py`), registered under the `OsintModule` provider inventory.

---

## 1. Scope & Primary Registries

### 1.1 Legal Entity Identifiers (GLEIF LEI)
- **Primary Source:** Global Legal Entity Identifier Foundation (GLEIF) public REST API (`https://api.gleif.org/api/v1/`).
- **Data Extracted:**
  - 20-character ISO 17442 Legal Entity Identifier (LEI)
  - Official Legal Name & Registered Legal Form
  - Entity Registration Status (ISSUED, LAPSED, RETIRED)
  - Legal Jurisdiction & Entity Category
  - Registered Legal Address & Headquarters Address (city, country, postal code, lines)
  - Managing Local Operating Unit (LOU)
  - Registration Authority & Next Annual Renewal Date
  - Canonical Search URL on `search.gleif.org`

### 1.2 US SEC EDGAR Filings & Corporate Disclosures
- **Primary Source:** US Securities and Exchange Commission (SEC) EDGAR submissions endpoint (`https://data.sec.gov/submissions/`).
- **Data Extracted:**
  - Central Index Key (CIK) with 10-digit zero-padding
  - Public Tickers & Stock Exchanges
  - Standard Industrial Classification (SIC) Code & Description (e.g., *National Commercial Banks*, *Security Brokers & Dealers*)
  - State of Incorporation & Fiscal Year End
  - Primary Business Address
  - Recent Official SEC Filings (Forms 10-K, 10-Q, 8-K) with accession numbers and direct SEC document archive URLs
  - Canonical SEC EDGAR browse URL

---

## 2. Strict Financial Privacy Boundary (Non-Negotiable)

```
+-------------------------------------------------------------------------------+
|                       STRICT FINANCIAL PRIVACY BOUNDARY                       |
|                                                                               |
|  PERMITTED (Public Institutional OSINT):                                      |
|    - Official Legal Entity Identifiers (LEI)                                  |
|    - Public SEC corporate filings (10-K, 10-Q, 8-K)                           |
|    - Commercial bank corporate registrations & regulatory disclosures         |
|    - Public corporate officer names & board filings                           |
|    - Sanctions list checks & regulatory enforcement actions                   |
|                                                                               |
|  STRICTLY PROHIBITED (Blocked & Rejected via ACCESS_RESTRICTED):              |
|    - Personal bank account numbers / routing numbers                          |
|    - Credit card / Debit card numbers (13-19 digit Luhn patterns)             |
|    - ATM PINs, Security codes (CVV/CVC), One-Time Passwords (OTPs)            |
|    - Internet banking passwords, session tokens, or login credentials         |
|    - Customer personal account balances or private transaction histories       |
|    - Any attempt to circumvent bank login walls or access controls            |
+-------------------------------------------------------------------------------+
```

Any request containing private financial patterns is automatically rejected with:
- `status: "rejected"`
- `extraction_status: "ACCESS_RESTRICTED"`
- `privacy_violation: true`
- Explanatory message: *"Strict Financial Privacy Guardrail: Unauthorized extraction of private personal financial records, banking credentials, PINs, OTPs, card numbers, or personal account balances is strictly prohibited under institutional OSINT compliance boundaries."*

---

## 3. Operational State & Testing

| Feature / Provider | Status | Source Endpoint | Verification Method |
| :--- | :--- | :--- | :--- |
| GLEIF LEI Lookup | `WORKING_TESTED_REAL` | `https://api.gleif.org/api/v1/lei-records` | Live query & unit tests |
| SEC EDGAR Disclosures | `WORKING_TESTED_REAL` | `https://data.sec.gov/submissions/CIK{cik}.json` | Live query & unit tests |
| Privacy Guardrail Filter | `WORKING_TESTED_REAL` | In-memory regex & pattern interception | Automated boundary tests |
| Sanctions Screening | `WORKING_TESTED_REAL` | Public OFAC / OpenSanctions matching | Unit tested |
