# Feature Mapping Inventory

## 1. Inventory of Features from Reference Application

| Ref # | Feature Name & Purpose | Source Files in Ref App | Target Location in Intelligence | Disposition | Dependencies & Security | Verification Test |
|---|---|---|---|---|---|---|
| **REF-01** | **SpiderFoot Adapter**<br>Autonomous OSINT scan lifecycle & module findings | `src/utils/collectors/external/spiderfoot.ts` | `backend/app/modules/osint/providers/spiderfoot.py`, `backend/app/modules/tool_executor.py` | **Adapt & Integrate** | HTTP client connecting to local/remote SpiderFoot server (`sf.py`), API key support, passive scan constraints | `tests/test_spiderfoot_provider.py` |
| **REF-02** | **theHarvester Adapter & Worker**<br>Domain email, host, IP and subdomain harvesting | `src/utils/collectors/external/theharvester.ts`, `osint-workers/theharvester/app.py` | `backend/app/modules/osint/providers/theharvester.py`, `osint-workers/theharvester/` | **Adapt & Integrate** | CLI wrapper, regex domain validation to prevent command injection, passive sources only | `tests/test_theharvester_provider.py` |
| **REF-03** | **Shodan InternetDB & Enrichment**<br>Keyless & keyed host IP reconnaissance | `src/utils/collectors/existing/shodan-internetdb.ts` | `backend/app/modules/osint/providers/shodan.py` | **Adapt & Integrate** | `internetdb.shodan.io` + `api.shodan.io/shodan/host`, safe IP validation | `tests/test_shodan_provider.py` |
| **REF-04** | **Google Dorks Engine**<br>Investigation search query generator & RSS executor | `src/utils/dorks.ts`, `src/utils/collectors/existing/dorks.ts` | `backend/app/modules/osint/providers/google_dorks.py` | **Adapt & Integrate** | News RSS parsing (executable) + Web dork link generator (no automated scraping of restricted targets) | `tests/test_google_dorks_provider.py` |
| **REF-05** | **Maltego Graph Export & Transform**<br>Export case graph to RFC-4180 CSV / Transform | `src/utils/maltego-export.ts` | `backend/app/modules/osint/providers/maltego.py`, `backend/app/api/v1/graph.py` | **Adapt & Integrate** | CSV export conforming to Maltego Table Import Wizard + Transform spec | `tests/test_maltego_provider.py` |
| **REF-06** | **Vehicle & VIN Intelligence**<br>NHTSA VIN decoding + Indian RTO plate mapping | `src/utils/vehicle-osint.ts` | `backend/app/modules/osint/providers/vehicle_intelligence.py` | **Adapt & Integrate** | NHTSA public API (keyless) + local RTO mapping database | `tests/test_vehicle_intelligence.py` |
| **REF-07** | **AI Object Detection & OCR Engine**<br>Computer Vision, Plate Detection & OCR | `ai-service/app/detect.py`, `ai-service/app/ocr.py` | `backend/app/modules/camera_evidence/anpr_service.py`, `backend/app/ml_contracts/client.py` | **Adapt & Integrate** | PyTorch / OpenCV / Tesseract OCR, confidence calibration, temporal tracking | `tests/test_master_vehicle_camera_anpr.py` |
| **REF-08** | **Image Forensics & EXIF Metadata**<br>Perceptual hash & metadata extraction | `ai-service/app/forensics.py` | `backend/app/modules/camera_evidence/forensics.py` | **Adapt & Integrate** | PIL / piexif, duplicate image detection across investigations | `tests/test_image_forensics.py` |

---

## 2. Detailed Technical Mapping

### 2.1 Provider Interface Standard (`CommonOSINTProvider`)
All five OSINT providers conform to a unified interface in `app/modules/osint/providers/base.py`:
- `id: str`
- `name: str`
- `category: str`
- `is_available() -> bool`
- `health_check() -> Dict[str, Any]`
- `execute(target: str, target_type: str, options: dict) -> ToolExecutionResponse`
- `normalize(raw_data: Any) -> List[NormalizedResult]`

This eliminates code duplication and ensures the investigation orchestrator invokes providers uniformly.
