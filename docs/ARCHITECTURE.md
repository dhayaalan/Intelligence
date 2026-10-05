# System Architecture

## 1. High-Level Architecture Overview

Sential Platform is structured on a strict boundary separation between **Platform Core**, **Independent Intelligence Modules**, and **External Provider Integrations**.

```text
                              CORE PLATFORM
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       │                            │                            │
    Identity                      Search                   Investigation
       │                            │                            │
   Tenancy                     Orchestrator                 Entity Vault
       │                            │                            │
   Security                 Module Registry               Evidence Vault
       │                            │                            │
       └──────────────────── Authorization ──────────────────────┘
                                    │
                             MODULE CONTRACT
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
            OSINT              THREAT INTEL         FUTURE MODULE
          (Isolated)            (Isolated)            (Isolated)
              │                     │                     │
              ▼                     ▼                     ▼
          Providers             Providers             Providers
         (Adapters)            (Adapters)            (Adapters)
```

## 2. Core Responsibilities

The Core Platform is responsible for:
* **Identity & Tenancy**: Organization isolation, authentication, user management.
* **Authorization**: Evaluating role permissions and tenant module entitlements.
* **Module Registry**: Managing lifecycle states, configuration schemas, and health diagnostics.
* **Search Orchestrator**: Module-agnostic query classification and concurrent job dispatching.
* **Core Correlation Engine**: Merging entities, inferring relationships, computing composite confidence.
* **Evidence Vault**: Tamper-proof evidence storage with SHA-256 provenance hashes.
* **Audit Logger**: Recording immutable security trace events.

The Core Platform **never** contains module-specific business logic or vendor-specific code.
