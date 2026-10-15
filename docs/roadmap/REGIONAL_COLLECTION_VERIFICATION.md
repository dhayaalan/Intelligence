# Regional Collection & Egress Operational Verification

## 1. Scope & Objective
This report provides operational verification evidence for the regional intelligence pipelines, zero-trust network egress controls, profile extraction contracts, and multi-region source comparisons across India, the United States, and the United Kingdom.

---

## 2. Egress Route & Fail-Closed Testing

### Test 1: Direct Route
- **Profile**: `EgressRouteType.DIRECT`
- **Result**: `is_active: True`, `verification_state: ROUTE_VERIFIED`, `egress_ip_masked: "local_direct"`.
- **Verdict**: Permitted for general non-sensitive operations.

### Test 2: Fail-Closed Protection
- **Profile**: `EgressRouteType.REGIONAL_GATEWAY_APPROVED` targeting an unconfigured or disabled regional profile.
- **Result**: `is_ok: False`, `msg: "OPSEC_FAIL_CLOSED: ... Direct network fallback is prohibited."`
- **Verdict**: Request blocked at dispatch layer. Zero host IP de-anonymization.

### Test 3: Active Live Route Verification
- **Profile**: `EgressRouteType.INDIA` with `VPN_INDIA_PROXY`
- **Verification Strategy**: Live HTTPS egress probe through configured gateway.
- **Verification Result**: Verified GeoIP registration `IN`, masked IP assigned.

---

## 3. OSINT Extraction Status Verification

| Target Handle / Platform | Probed Endpoint | Observed Status | Extracted Attributes |
|---|---|---|---|
| `octocat` (GitHub) | `https://api.github.com/users/octocat` | `METADATA_EXTRACTED` | Name, Bio, Authentic Avatar, Location, Followers (14k+), Repositories (8) |
| `torvalds` (GitLab) | `https://gitlab.com/api/v4/users?username=torvalds` | `METADATA_EXTRACTED` | Name, Bio, Real Avatar, Web URL |
| `alice` (Bluesky) | `https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile` | `METADATA_EXTRACTED` | Display Name, Description, Avatar, Followers Count |
| Static Forum Profile | Heuristic HTTP 200 | `PROFILE_VALIDATED` | Handle existence confirmed; Synthetic avatars prohibited |
| Non-existent Account | HTTP 404 / Keyword | `NOT_FOUND` | `found: False`, No false positive match |

---

## 4. Regional News & Dynamic Framing Verification
- **Lexicon Transliteration**: Tested multi-script query vectors across Devanagari (`भारतीय वायु सेना`), Tamil (`விமானப்படை`), Urdu (`فضائیہ`), and Bengali (`ভারতীয় বিমানবাহিনী`).
- **Dynamic Derivation**: Verified that similarities and divergences are extracted dynamically from retrieved dispatches.
- **Zero-Result Honesty**: Verified that when zero records are returned, `sample_size = 0` is reported without synthesizing false events.
