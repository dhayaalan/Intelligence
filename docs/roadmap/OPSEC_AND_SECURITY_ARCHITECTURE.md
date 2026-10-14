# OPSEC & Security Architecture Specification

**Repository**: `/home/songoku/Pictures/Intelligence`  
**Standard**: High-Assurance Investigative Environment & Zero-Trust Architecture (NIST SP 800-207)  
**Document Status**: Security Specification  

---

## 1. Zero-Trust Security Philosophy

Investigative operations conducted within defence-adjacent or sensitive public-interest domains operate under an adversarial threat model:
1. Target entities monitor inbound reconnaissance traffic, HTTP referrers, and network sources.
2. Web content collected from external publishers, social media, and paste sites may contain malicious payloads, exploits, or tracking beacons.
3. Compromise of an active scanner must never provide an adversary with a pivot into the core application database, tenant evidence, or internal infrastructure.

Adhering to **NIST SP 800-207 (Zero Trust Architecture)**, perimeter defense is insufficient. Security must be enforced on every transaction, request, egress route, and data persistence layer.

---

## 2. Investigator & Identity Protection

### 2.1 Complete Identity De-coupling
- **No Identity Leakage in Egress**: External HTTP requests made to news publishers, RSS wires, social media platforms, or target networks never contain investigator identifiers, session cookies, user emails, or internal case IDs in HTTP headers, User-Agents, or query strings.
- **Sanitized User-Agent Profile**: Inbound and outbound connections use uniform, standardized browser signatures (`Mozilla/5.0 ... SentinelIntel/2.0`) to prevent fingerprinting of individual analyst workstations.
- **Role-Based Least Privilege (RBAC)**:
  - `SUPER_ADMIN`: System-wide maintenance, tenant provisioning, audit log review.
  - `TENANT_ADMIN`: User management and module assignment within tenant.
  - `ANALYST`: Case creation, regional collection, evidence compilation.
  - `USER`: Read-only access to assigned cases.

### 2.2 Secret Sanitization & Audit Redaction
- All credentials (API keys, VPN credentials, proxy authorization headers) are automatically stripped before log writing.
- Debug outputs sanitize tokens matching regex patterns for JWTs, Bearer tokens, passwords, and private hashes.

---

## 3. Network Egress Policy & Fail-Closed Gateways

### 3.1 Network Egress Segregation
The application strictly segments outbound traffic into three isolated routing categories:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Outbound Traffic Classification                      │
├──────────────────────────┬─────────────────────────────┬───────────────┤
│ 1. Core Platform Egress  │ 2. Regional Collection      │ 3. Active     │
│    (Public RSS / DNS)    │    (Geographic Profiles)    │    Scanners   │
├──────────────────────────┼─────────────────────────────┼───────────────┤
│ • Direct gateway         │ • Approved regional gateway │ • Dedicated   │
│ • No geo-lock required   │ • Fail-Closed on disconnect │   isolated    │
│ • Standard rate limits   │ • Zero IP hopping           │   network     │
└──────────────────────────┴─────────────────────────────┴───────────────┘
```

### 3.2 Fail-Closed Guarantee
- If a collection job specifies a regional route (`REGIONAL_GATEWAY_APPROVED`) and that gateway experiences an outage, handshake failure, or DNS degradation:
  - **The job halts immediately with error code `EGRESS_UNAVAILABLE`.**
  - **Direct network fallback is strictly prohibited.**
- Prevents accidental deanonymization of collection nodes or leakage of local physical IP addresses.

### 3.3 No Evasive Scraping or IP Hopping
- Egress controls must never be used to bypass legal constraints, anti-bot mechanisms, or terms of service.
- IP rotation to bypass bans or rate limits is strictly forbidden; providers must be accessed through legitimate quotas and transparent rate throttling.

---

## 4. Defense Against Compromised Sources & Untrusted Content

Every third-party article, post, media file, and document is treated as hostile untrusted input.

### 4.1 Server-Side Request Forgery (SSRF) Hardening
All URL ingestion processes pass through `SSRFGuard`:
- Blocks loopback (`127.0.0.0/8`, `::1`), link-local metadata (`169.254.169.254`), and private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
- Resolves DNS prior to HTTP dispatch and re-validates the destination IP on every HTTP redirect hop.
- Rejects dangerous URI schemes (`file://`, `gopher://`, `ftp://`, `ldap://`), permitting only `http://` and `https://`.

### 4.2 Untrusted Content Neutralization
- **HTML Sanitization**: Scraped HTML is stripped of active elements (`<script>`, `<iframe>`, `<object>`, `<embed>`, inline event handlers).
- **Resource Constraints**: Parsing routines operate under strict bounds:
  - Max response body: 15 MB.
  - Connection timeout: 10s.
  - Total crawl budget per job: bounded memory allocation.
- **Media Safety**: Images and documents are parsed without shell command interpolation (`shell=False`).

---

## 5. Tamper-Evident Evidence Protection

1. **Cryptographic Hashing**: Every collected evidence item computes a SHA-256 digest at moment of capture.
2. **Immutable Audit Record**: Once written, evidence items and original source URLs cannot be modified in-place; analytical revisions generate new versioned assertions referencing the parent record.
3. **Distinction Between Integrity and Truth**: Cryptographic hash confirms the artifact has not been modified since collection; it does not validate that the external publisher's content is factually accurate.
4. **Time Provenance**: Clear separation between `source_published_at` (original publication timestamp) and `platform_collected_at` (moment of ingestion).
