# Relationship Graph UX Redesign & Interaction Model

## 1. Problem Diagnosis: Eliminating Graph Clutter

### Root Causes of Previous Visualization Clutter

Analysis of the initial Relationship Graph interface identified four core defects that made the canvas unreadable for OSINT investigators:

1. **Oversized Information Cards**:
   - Entities were rendered as bulky rectangular cards (250–320px wide) containing large circular avatars, multiple badge rows, full titles, and metadata tables.
   - When 20 to 70 entities were placed on canvas, the cards overlapped, blocked connecting relationship lines, and caused extreme visual fatigue.

2. **Hardcoded Mock Coordinates**:
   - The previous component contained arbitrary hardcoded coordinate dictionaries (`DISINFOLAB_COORDINATES`) that forced specific coordinates regardless of actual graph topology.

3. **Unlinked Entities Flooding the Main Canvas**:
   - An investigation with 71 nodes and only 18 genuine relationships forced 53 completely disconnected entities directly into the center of the graph canvas.
   - Investigators could not distinguish meaningful relationship clusters from isolated background records.

4. **Cluttered Controls & Competing Panels**:
   - An oversized minimap and static right-hand telemetry inspector permanently consumed canvas width.
   - Duplicate statistics badges cluttered the toolbars without differentiating total investigation entities from visible canvas nodes.

---

## 2. Redesigned Visual Architecture

### Compact Graph Nodes (`CompactGraphNode`)

The oversized cards have been replaced with **streamlined, compact graph nodes** tailored for network analysis:

- **Dimensions**: Lightweight pill shape (~140px to 180px wide, ~36px height).
- **Semantic Iconography**: Left-aligned circular pill displaying an icon corresponding to the entity category (User for Person, Building for Organization, Globe for Domain, Shield for Threat Indicator, Server for IP, Mail for Email).
- **Restrained Semantic Palette**:
  - `ORGANIZATION`: Indigo accents (`#6366f1`).
  - `PERSON`: Amber accents (`#f59e0b`).
  - `THREAT_INDICATOR`: Rose accents (`#f43f5e`).
  - `IP`: Blue accents (`#3b82f6`).
  - `EMAIL`: Teal accents (`#14b8a6`).
  - `DOMAIN` / `OTHER`: Neutral slate (`#64748b`).
- **Truncated Label**: Clear, single-line typography with text truncation and tooltip on hover for long names.
- **Root Entity Distinction**: Distinct halo ring (`ring-2 ring-indigo-500/30`), gold star, and `★ ROOT` indicator for the primary investigation target.
- **Active / Selected State**: High-contrast border and focus ring (`border-indigo-600 ring-2 ring-indigo-500/40 shadow-md scale-105`) without resizing surrounding nodes.
- **Connection Handles**: 4 multi-directional connection pins (Top, Bottom, Left, Right) enabling clean, non-crossing curved edge routing.

---

## 3. Focus-First Default Graph Layout

### Progressive Disclosure Model

The canvas operates on a **Focus-First** layout designed for investigative rigor:

1. **Seed Entity Centering**: The graph opens centered around the primary investigation target (or the entity with highest connection degree).
2. **Bounded 1-Hop Neighborhood**: Only entities with genuine, verified connections to the focus seed are initially rendered on the main canvas.
3. **Segregated Unlinked Entities**: Unconnected entities are filtered out of the main canvas by default. An explicit toggle button (`Unlinked (53)`) in the toolbar allows investigators to view isolated entities when needed without cluttering the active relationship topology.
4. **Stable Positions on Expansion**: Newly expanded nodes orbit around their parent node at a stable radial distance ($R=200\text{px}$) without triggering disruptive viewport jumps.

### Layout Options

The toolbar provides four deterministic layout modes derived from the underlying graph structure:

| Layout Mode | Description | Best For |
| :--- | :--- | :--- |
| **Focus (Default)** | Places the selected seed at the center with 1-hop and 2-hop connected neighbors arranged in clean concentric orbits. | Initial case analysis and direct association mapping. |
| **Radial** | Concentric circular rings around the selected entity with uniform angular spacing. | Visualizing broadcast hubs, C2 infrastructure, and influence networks. |
| **Network** | Distributed force-directed layout where connected clusters group naturally. | Large multi-cluster investigations with cross-cutting connections. |
| **Hierarchy** | Directional top-to-bottom tiers ordered by entity classification (Orgs $\to$ Actors $\to$ Infrastructure). | Command-and-control hierarchies and organizational structure. |

---

## 4. Canvas, Toolbar, and Inspector Design

### Streamlined Toolbar

The toolbar prioritizes investigator workflow:
- **Layout Switcher**: One-click toggles between `Focus`, `Radial`, `Network`, and `Hierarchy`.
- **Category Filter**: Dropdown to isolate specific entity types (e.g. show only Threat Indicators or IP addresses).
- **Unlinked Toggle**: Quick badge switch showing the count of isolated entities.
- **In-Graph Search**: Real-time filter highlighting matching nodes on the canvas.
- **Viewport Controls**: `Fit View` (auto-centers canvas with smooth animated transition) and `Minimap` toggle.
- **Visible vs Total Counters**: Explicitly displays visible nodes and edges vs total entities stored in the case (`18 nodes • 12 edges`).

### Collapsible & Context-Aware Inspector

- **Full Canvas Reclaim**: When the inspector is collapsed, the graph canvas seamlessly expands from 3 columns to the full 4-column width (100% viewport width).
- **Selected Node Inspector**:
  - Full unabbreviated entity name and type classification.
  - Verification status and analytic confidence score.
  - Correlated sources and provenance list.
  - Verified attributes list (filtering out `null`, `undefined`, and empty values).
  - Traversal controls: `Expand 1-Hop` with animated loading state, and `Collapse Branch`.
- **Selected Edge Inspector**:
  - Typed relationship direction (`Source --[OWNS]--> Target`).
  - Evidence basis tag (`DIRECT_OBSERVATION` vs `INFERRED`).
  - Confidence rating.
  - Clickable supporting evidence tags with IDs linking to the underlying MongoDB evidence vault.

---

## 5. Expansion & Collapse State Correctness

### Preservation of Shared Nodes

When expanding a branch:
1. The frontend queries `/api/v1/graph/expand?entity_id=...`.
2. New nodes are deduplicated against existing canvas entities using canonical IDs.
3. If a newly discovered edge connects to an entity already visible on canvas, the edge binds to the existing node rather than duplicating it.
4. The branch's added nodes and edges are recorded in `expandedBranches[branchKey]`.

When collapsing a branch:
1. The frontend checks all other active expanded branches.
2. If node $N$ was introduced by branch $A$ but is also referenced by branch $B$ (or was part of the initial focus seed), node $N$ is **preserved on the canvas**.
3. Only nodes exclusively belonging to the collapsed branch are removed.
4. Edge removals are strictly scoped to the collapsed branch.
