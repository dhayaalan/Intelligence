# Vulnerability Assessment & Penetration Testing (VA/PT) Isolation Architecture

**Repository**: `/home/songoku/Pictures/Intelligence`  
**Standard**: Isolated Active Reconnaissance, Scope Enforcement, and Blast-Radius Containment  
**Document Status**: Security Specification  

---

## 1. Architectural Philosophy & Threat Model

Active vulnerability assessment and penetration testing (VA/PT) involves sending network probes, banner queries, port checks, and exploit payloads to remote targets. 

If executed within the primary application process without strict boundaries, VA/PT tools introduce grave risks:
1. **Pivot Threat**: A compromised or hijacked scanner engine could exploit local network access to attack the core application database, tenant evidence vaults, or adjacent cloud infrastructure.
2. **Accidental Collateral Damage**: An uncontrolled scanner could probe unauthorized third-party domains, internal Kubernetes services, or cloud metadata endpoints (`169.254.169.254`).
3. **Denial of Service**: Intensive scanning could exhaust core server memory, open file descriptors, or socket pools.

This design enforces **complete isolation between the Intelligence Platform data plane and active VA/PT scanning engines.**

---

## 2. Separate Execution Environments

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Core Application Data Plane                          │
│   FastAPI Server | Multi-Tenant Database | Evidence Vault | UI         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Restricted REST Task Dispatch
                                    │ (Signed Job Token with Scope)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  VA/PT Isolated Execution Worker                       │
│  • Non-root process container                                          │
│  • Bounded CPU / RAM / Execution Timeout                               │
│  • Zero Database Credentials (cannot query MongoDB or SQLite)          │
│  • Egress via dedicated scanning interface                             │
│  • Blocked from internal VPC subnets & cloud metadata                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
                          Target Network / Host
```

### 2.1 Least-Privilege Isolation Principles
- **No Database Access**: Scanning workers do not hold credentials to the core MongoDB, SQLite, or Redis databases. They receive jobs over a restricted queue/API and return structured telemetry only.
- **Resource Quotas**: Hard CPU limits (max 1 core), memory caps (max 512 MB per worker), and max execution timeouts (default 120s) ensure runaway tools are killed automatically.
- **Dedicated Network Interface**: Scanning traffic routes through a dedicated network interface, preventing target responses from entering the internal management plane.

---

## 3. Strict Scope Enforcement Engine (`VAPTScopeEnforcer`)

Every scan request must pass through a multi-stage authorization gate before any packet is dispatched.

### 3.1 Validation Criteria
1. **Scope Allowlist Match**: The target domain or IP must match a pre-authorized scope permit registered by an organization administrator.
2. **Explicit Exclusion Check**: Targets cannot match wildcards or IP exclusions (e.g. `*.internal`, `gov.in`, critical infrastructure).
3. **SSRF & Private CIDR Rejection**: All private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.169.254`) are strictly blocked unless a specific `PRIVATE_LAB_PERMIT` cryptographic token is supplied by a Super Admin.
4. **DNS Re-binding Protection**: The target hostname is resolved immediately before dispatch, and the resolved IP is re-verified against the allowlist.

### 3.2 Impact Level Profiling
Every tool and scan operation is assigned a strict impact level:

| Impact Level | Capabilities | Approval Gate | Rate Limit |
| :--- | :--- | :--- | :--- |
| **PASSIVE_RECON** | WHOIS, DNS records, public certificate transparency, search indexing. | Automatic with analyst role. | 60 requests/min |
| **ACTIVE_PORT_PROBE** | TCP SYN port checks, TLS handshake discovery, HTTP banner retrieval. | Tenant Admin verified scope permit. | 10 probes/sec |
| **INTRUSIVE_VULN_SCAN**| Active HTTP fuzzing, CVE signature tests, header injection tests. | Explicit Multi-Party Approval Gate (Super Admin). | Bounded bursts |

### 3.3 Emergency Stop (Kill-Switch)
- Any running active scan job can be instantly aborted via `POST /api/v1/threat/scans/{job_id}/abort`.
- Subprocesses are sent `SIGTERM`, followed by `SIGKILL` after 2.0 seconds if non-responsive.

---

## 4. Separation of Scanner Findings from Confirmed Evidence

- **Scanner Alerts are Untrusted Signals**: Raw scanner output is recorded as `SCAN_OBSERVATION` or `UNCONFIRMED_ALERT`.
- **Validation Pipeline**: An observation only becomes a confirmed vulnerability or case evidence after:
  1. Automated validation (re-running a secondary deterministic verification probe), OR
  2. Manual investigator review and attestation with documented proof.
- **Zero Hallucinated Severity**: Scanners cannot inflate severity without presenting the raw HTTP response code, banner, or CVE reference.

---

## 5. Containment and Preservation of Attack Telemetry

- **Quarantine Telemetry Store**: Logs, raw PCAPs, and HTTP request/response transcripts from scans are stored in a dedicated, read-only `scan_telemetry` table.
- **Active Payload Neutralization**: Captured payloads, exploit strings, or shell commands are stored base64-encoded and rendered as plain text. The dashboard never executes scripts or renders active HTML from scanner outputs.
