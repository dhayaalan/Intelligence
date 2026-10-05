# SAAS_PLATFORM UI/UX REFERENCE & AUDIT DOCUMENTATION

## 1. Executive Summary
This document provides a comprehensive audit of the visual design system, UI components, layout structures, and user experience workflows in `/home/songoku/Pictures/saas_platform`. This audit serves as the authoritative blueprint for the exact UI/UX migration into `/home/songoku/Pictures/Sential_platform`.

---

## 2. Color System & Design Tokens

### Core Color Palette
| Token | Light Mode Value | Dark Mode Value | Semantic Role |
| :--- | :--- | :--- | :--- |
| `--background` | `#ffffff` | `#0b0f17` / `#090a0c` | Deep application background |
| `--surface` | `#ffffff` | `#0e131f` / `#121215` | Default card & container surface |
| `--surface-50` | `#fafafa` | `#18181b` | Elevated subtle background |
| `--surface-100` | `#f4f4f5` | `#1e2433` / `#27272a` | Hover states and inputs |
| `--surface-200` | `#e4e4e7` | `#2a3245` / `#3f3f46` | Active states and borders |
| `--border` | `#e4e4e7` | `#1e293b` / `#27272a` | Primary structural borders |
| `--border-subtle` | `#f4f4f5` | `rgba(255, 255, 255, 0.06)` | Inner card dividers |
| `--foreground` | `#09090b` | `#f8fafc` | Primary text |
| `--text-muted` | `#71717a` | `#94a3b8` / `#a1a1aa` | Secondary labels & timestamps |

### Brand & Semantic Accents
| Role | Color Value (Light / Dark) | Usage |
| :--- | :--- | :--- |
| **Brand Primary** | `#4f46e5` (`indigo-600`) | Logo badge, workspace active indicator, primary CTA |
| **Success / Verified** | `#10b981` (`emerald-500`) | SHA-256 validated, healthy engine, live telemetry dot |
| **Warning** | `#f59e0b` (`amber-500`) | Medium severity, pending investigations |
| **Danger / Critical** | `#f43f5e` / `#ef4444` (`rose-500`) | Critical finding, failed engine, security alert drawer |
| **Cyan / Intelligence** | `#06b6d4` (`cyan-500`) | Graph node highlighting, target classification |
| **Purple / Payload** | `#8b5cf6` (`violet-500`) | Malware payload indicators, forensic artifacts |

---

## 3. Typography & Spacing Language
- **Font Families**:
  - Sans-serif: `'Inter', system-ui, -apple-system, sans-serif` (Application shell, titles, forms, body)
  - Monospace: `'JetBrains Mono', monospace` (Entities, hashes, timestamps, badges, code snippets)
- **Hierarchy**:
  - Page Titles: `text-xl sm:text-2xl font-bold tracking-tight text-white`
  - Section Breadcrumb: `text-xs font-mono uppercase tracking-wider text-zinc-500`
  - Subheaders: `text-sm font-semibold text-slate-200`
  - Table Headers: `text-[10px] uppercase font-mono tracking-wider text-slate-400 font-bold`
  - Badges & Pills: `text-[10px] sm:text-[11px] font-mono font-bold px-2 py-0.5 rounded`
- **Layout Spacing**:
  - Navbar Height: `h-14` (`56px`) with sticky blur
  - Sidebar Width: `w-64` (`256px`) fixed left navigation
  - Main Content Offset: `md:ml-64 p-4 sm:p-6`
  - Grid Gaps: `gap-3` to `gap-4`

---

## 4. Authentication Experience (`LoginPage.tsx`)
- **Split Screen Layout**:
  - **Left 50% Panel**:
    - HTML5 Canvas rendering interactive real-time intelligence entity correlation graph with drifting nodes and glowing green connecting edges.
    - Top telemetry badge: `SENTINEL CORE PLATFORM` + `FABRIC 2.0 ACTIVE` pulsing dot.
    - Editorial copy: "Autonomous threat correlation, entity discovery, and evidentiary custody."
    - Metric strip: Module 01 OSINT Engine, Data Fabric TanStack Cache, Security SHA-256 Vault.
  - **Right 50% Panel**:
    - Clean form with email, password with eye toggle, and "Remember active workstation".
    - One-click "Demo Analyst Clearance" pre-fill pill.
    - Primary CTA: `Authenticate & Enter Workspace` with arrow icon.
    - Link to organization registration.

---

## 5. Application Shell & Navigation

### Top Navbar (`AppShell.tsx`)
- Left:
  - Shield icon inside indigo badge + uppercase `SENTINEL` branding.
  - Workspace selector dropdown (`Organization / Workspace`).
- Center:
  - Quick Search / Command Palette input (`Search intelligence... ⌘K`).
- Right:
  - Notification center with active alert badge drawer (`Security Alerts & Drift`).
  - Admin console button (when role is authorized).
  - User initials avatar (`AT`, `SA`) and sign out button.

### Sidebars

#### 1. Investigator / Analyst Sidebar (`w-64`)
- Header: `Intelligence Workspace` (or `Investigator Workspace` for Admin users).
- Core Navigation Items:
  1. **Search** (`/workspace/search` - Lucide `Search`)
  2. **Investigations** (`/workspace/investigations` - Lucide `FolderGit2` with active counter badge)
  3. **Entities** (`/workspace/entities` - Lucide `Layers` with divider line)
  4. **Findings** (`/workspace/findings` - Lucide `ShieldAlert`)
  5. **Reports** (`/workspace/reports` - Lucide `FileText`)
  6. **Monitoring** (`/workspace/monitoring` - Lucide `Radio`)
- Footer:
  - `Access Clearance: Lead Analyst / Investigator`
  - Tenant isolation badge: `TENANT ISOLATION: ENFORCED`.

#### 2. Platform Administration Sidebar
- Header: `Platform Administration` (`ADMIN` badge).
- Items:
  1. **Dashboard** (`/admin/dashboard` - `BarChart3`)
  2. **Organizations** (`/admin/organizations` - `Building`)
  3. **Users** (`/admin/users` - `Users`)
  4. **Access & Modules** (`/admin/access` - `Layers`)
  5. **Audit Logs** (`/admin/audit` - `ShieldAlert`)
  6. **System Health** (`/admin/system-health` - `HeartPulse`)
  7. **Administration / Infrastructure** (`/admin/intelligence-infrastructure` - `Globe`)

---

## 6. Functional Module Specifications

### 1. Search Experience (`SearchPage.tsx` / `OsintSearchWorkspace.tsx`)
- Input bar with auto-detected target type, multi-select capability dropdown (Domain, IP, Username, Email, Breach, DNS, WHOIS).
- Progress indicator showing provider status.
- Highlighted token matching on results.
- Export to JSON/CSV and one-click "Add to Investigation".

### 2. Investigations (`InvestigationsPage.tsx` & `InvestigationDetailPage.tsx`)
- Grid and table view toggle.
- Status filters (`ALL`, `OPEN`, `IN_PROGRESS`, `CLOSED`) and Priority filters (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- Case detail tabs: Overview, Targets, Entities, Findings, Evidence Vault, Activity Timeline, Dossier Reports.

### 3. Findings (`FindingsPage.tsx`)
- Manifest of correlated security discoveries.
- Card items detailing:
  - Severity badge (`CRITICAL` rose, `HIGH` orange, `MEDIUM` amber).
  - Status badge (`OPEN`, `VERIFIED`, `MITIGATED`).
  - Analytic confidence percentage (`85% Analytic Confidence`).
  - Remediation Policy / Mitigation block.

### 4. Cryptographic Evidence Vault (`EvidencePage.tsx`)
- Chain-of-custody table/card list.
- Sealed SHA-256 cryptographic digest with copy button.
- "Audit Hash" modal verifying bitwise genesis match.
- Custody officer and sealed timestamp.

### 5. Intelligence Dossier Studio (`ReportsPage.tsx` & `ReportBuilderComponent.tsx`)
- Court-admissible dossier standards.
- Executive summary, correlated threat findings, extracted target entities, and evidence citations.
- Markdown generation preview with one-click copy and `.md` file download.

### 6. Normalized Entity Explorer (`EntitiesPage.tsx`)
- Entity search filter by value or identifier.
- Type dropdown (`ALL`, `DOMAIN`, `IP`, `THREAT_ACTOR`, `HASH`, `EMAIL`).
- Entity card showing risk score (out of 100), threat level, and creation date.

---

## 7. Migration Directives for Sential Platform
1. **Preserve Exact Visual Language**:
   - Recreate the exact `AppShell.tsx` with topbar workspace switcher, alerts drawer, and the authoritative `w-64` left navigation sidebar.
2. **First-Class Routing**:
   - Add first-class pages in Sential for:
     - `/workspace/search`
     - `/workspace/investigations`
     - `/workspace/investigations/:id`
     - `/workspace/entities`
     - `/workspace/findings`
     - `/workspace/reports`
     - `/workspace/monitoring`
3. **Backend Integration**:
   - Ensure Sential backend provides full MongoDB-backed endpoints for `/api/v1/findings`, `/api/v1/evidence`, `/api/v1/reports`, `/api/v1/investigations`, `/api/v1/entities`, `/api/v1/search`, `/api/v1/providers`, `/api/v1/modules`, `/api/v1/users`, `/api/v1/audit`.
