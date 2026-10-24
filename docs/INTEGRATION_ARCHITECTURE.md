# Integration Architecture

## 1. System Overview

The Sential Intelligence Platform combines structured OSINT providers, threat intelligence sources, deep-learning and computer-vision pipelines, and graph relationship modeling into a single multi-tenant investigator workspace.

```mermaid
graph TD
    Client[React + Vite Frontend\nPort 3000] -->|REST / JWT| Backend[FastAPI Backend Core\nPort 8000]
    
    Backend -->|Primary Storage| Mongo[(MongoDB 7.0\nPort 27018/27017)]
    Backend -->|Graph Links| Neo4j[(Neo4j 5.20\nPort 7474/7687)]
    Backend -->|Caching & Jobs| Redis[(Redis 7\nPort 6379/6380)]
    Backend -->|Dynamic Scan| ZAP[OWASP ZAP\nPort 8091/8090]
    
    subgraph "OSINT Provider Layer"
        Backend --> P_SpiderFoot[SpiderFoot Provider / Local Worker]
        Backend --> P_TheHarvester[theHarvester Worker / CLI API]
        Backend --> P_Shodan[Shodan API & InternetDB]
        Backend --> P_Dorks[Google Dorks Query & News RSS]
        Backend --> P_Maltego[Maltego Graph Transform & CSV]
    end

    subgraph "Media & Vision Intelligence"
        Backend --> ANPR[ANPR & Video Ingestion Engine]
        ANPR --> OpenCV[OpenCV Preprocessing & Contours]
        ANPR --> OCR[Tesseract Dual-Pass OCR]
        ANPR --> Tracking[Temporal Cross-Frame Vehicle Tracker]
        ANPR --> Forensics[pHash & Metadata Extractor]
    end
```

---

## 2. OSINT Common Provider Interface

To maintain strict modularity and prevent vendor lock-in, all five OSINT tools implement the `BaseOSINTProvider` interface (`app/modules/osint/providers/base.py`):

```python
class BaseOSINTProvider(ABC):
    @property
    @abstractmethod
    def provider_id(self) -> str: ...

    @property
    @abstractmethod
    def display_name(self) -> str: ...

    @abstractmethod
    def check_availability(self) -> ProviderStatus: ...

    @abstractmethod
    async def execute_query(
        self, target: str, target_type: str, options: dict
    ) -> ToolExecutionResponse: ...

    @abstractmethod
    def normalize_results(self, raw_data: Any) -> List[NormalizedResult]: ...
```

### Provider Behavior Guidelines:
1. **SpiderFoot:**
   - Detects if `SPIDERFOOT_URL` is configured.
   - If configured: submits scan (`/startscan`), polls status (`/scanstatus`), retrieves results (`/scaneventresults`), and attributes module provenance to each event.
   - If not configured: returns `CONFIG_REQUIRED` status with clear configuration instructions. Never creates fake scans.
   - Passive profile enforced by default.
2. **theHarvester:**
   - Detects if `THEHARVESTER_URL` (worker) or local `theHarvester` binary is installed.
   - Restricts invocation to safe, validated domains (preventing shell injection).
   - Constrains data sources to passive providers (`crtsh`, `certspotter`, etc.).
   - Returns structured emails, hosts, IPs, and URLs normalized into `NormalizedResult` records.
3. **Shodan:**
   - Queries `internetdb.shodan.io` for keyless port, vuln, and CPE intelligence.
   - If `SHODAN_API_KEY` is provided, supplements with authoritative host data (`/shodan/host/{ip}`) including service banners and SSL certificates.
   - Strictly separates internet device metadata from video camera assumptions.
4. **Google Dorks:**
   - Generates investigator-curated search query strings using advanced Google operators (`site:`, `filetype:`, `intitle:`, `inurl:`, `OR`, `-exclude`).
   - For `scope="news"`: executes queries legitimately against Google News RSS, returning real parsed articles without violating search engine terms.
   - For `scope="web"`: delivers pre-compiled, syntax-highlighted search query links for the analyst to review directly in their browser.
5. **Maltego:**
   - Normalizes investigation graph nodes and edges into RFC-4180 CSV tables matching Maltego's Table Import wizard.
   - Maps platform entity types (`person`, `domain`, `ip`, `email`, `vehicle`, etc.) into native `maltego.*` entity taxonomy.
   - Exposes endpoint for live Maltego local Transform XML/JSON dispatch.

---

## 3. Media Ingestion & Computer Vision Pipeline

```mermaid
sequenceDiagram
    participant Analyst as Investigator
    participant API as /camera-evidence API
    participant Pipeline as ANPR & Media Pipeline
    participant CV as OpenCV Engine
    participant OCR as Tesseract OCR
    participant Store as MongoDB & Evidence Store

    Analyst->>API: Upload Video Footage (MP4/WebM)
    API->>API: Validate MIME, Size (<=50MB), Hash (SHA-256)
    API->>Pipeline: Decode Video & Sample Frames
    Pipeline->>CV: Aspect-Ratio Morphology & Edge Filtering
    CV-->>Pipeline: Candidate License Plate Crops
    Pipeline->>OCR: Run Dual-Pass PSM 7 & PSM 8 OCR
    OCR-->>Pipeline: Character Stream & Confidence Scores
    Pipeline->>Pipeline: Temporal Matching & Cross-Frame Deduplication
    Pipeline->>Store: Persist ANPRDetectionRecord with Timecodes & B64 Thumbnails
    Store-->>Analyst: Present Sightings for Human Verification
```

---

## 4. Security & Safety Architecture

1. **Subprocess Isolation:** theHarvester and external tools are invoked either via dedicated HTTP workers or strictly validated argument arrays (`subprocess.run(["theHarvester", "-d", clean_domain])`) with no shell interpolation (`shell=False`).
2. **SSRF Guard:** Media URLs and camera streams pass through `app/core/network_safety.py`, blocking RFC 1918 private IPs, loopbacks (`127.0.0.1`), link-local addresses (`169.254.169.254`), and internal cloud metadata endpoints.
3. **Audit Trail:** Every provider execution, video ingestion, and manual plate verification records tenant ID, user ID, timestamp, and target hash in MongoDB collection `audit_logs`.
