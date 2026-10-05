# Role-Based Access Control (RBAC)

Sential supports exactly 4 distinct roles with strict permission boundaries:

| Role | Workspace | Privileges |
| :--- | :--- | :--- |
| **SUPER_ADMIN** | Platform Overview | Global platform management, tenant provisioning, module lifecycle toggles, all audit logs, system telemetry. |
| **TENANT_ADMIN** | Organization Overview | Tenant user onboarding (Analyst & User only), tenant-entitled module allocation, organization audit trail. |
| **ANALYST** | Search (Default) | Full search execution across authorized modules, case investigation management, evidence vaulting, timeline notes. |
| **USER** | Search (Default) | Search execution on assigned modules, view assigned investigations (read-only case findings). |

## Prohibited Behaviors
* No Role Switching: Users cannot switch their role in the UI; the authenticated JWT determines the workspace shell.
* Tenant Admin cannot create `SUPER_ADMIN` or another `TENANT_ADMIN`.
* Tenant Admin cannot allocate modules not entitled to their organization.
