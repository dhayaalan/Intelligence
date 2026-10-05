import logging
from typing import Dict, List, Optional, Any
from app.modules.threat_intelligence.engines.base import ScannerEngine, EngineCategory, ExecutionMode
from app.modules.threat_intelligence.engines.engines.dns_engine import DNSEnumerationEngine
from app.modules.threat_intelligence.engines.engines.tls_engine import TLSInspectionEngine
from app.modules.threat_intelligence.engines.engines.http_engine import HTTPDiscoveryEngine
from app.modules.threat_intelligence.engines.engines.tech_engine import TechnologyDetectionEngine
from app.modules.threat_intelligence.engines.engines.host_discovery_engine import HostDiscoveryEngine
from app.modules.threat_intelligence.engines.engines.port_service_engine import PortServiceDiscoveryEngine
from app.modules.threat_intelligence.engines.engines.web_crawler_engine import WebCrawlerEngine
from app.modules.threat_intelligence.engines.engines.openapi_engine import OpenAPIDiscoveryEngine
from app.modules.threat_intelligence.engines.engines.zap_spider_engine import ZAPSpiderEngine
from app.modules.threat_intelligence.engines.engines.zap_active_scan_engine import ZAPActiveScanEngine
from app.modules.threat_intelligence.engines.engines.threat_intel_engine import ThreatIntelligenceCorrelationEngine
from app.modules.threat_intelligence.engines.engines.subfinder_engine import SubfinderEngine
from app.modules.threat_intelligence.engines.engines.dnsx_engine import DNSxEngine
from app.modules.threat_intelligence.engines.engines.uncover_engine import UncoverEngine
from app.modules.threat_intelligence.engines.engines.naabu_engine import NaabuEngine
from app.modules.threat_intelligence.engines.engines.httpx_engine import HTTPXEngine
from app.modules.threat_intelligence.engines.engines.katana_engine import KatanaEngine
from app.modules.threat_intelligence.engines.engines.nuclei_engine import NucleiEngine
from app.modules.threat_intelligence.engines.engines.nikto_engine import NiktoEngine
from app.modules.threat_intelligence.engines.engines.dalfox_engine import DalfoxEngine
from app.modules.threat_intelligence.engines.engines.amass_engine import AmassEngine
from app.modules.threat_intelligence.engines.engines.asnmap_engine import ASNMapEngine
from app.modules.threat_intelligence.engines.engines.cdncheck_engine import CDNCheckEngine
from app.modules.threat_intelligence.engines.engines.masscan_engine import MasscanEngine
from app.modules.threat_intelligence.engines.engines.testssl_engine import TestsslEngine
from app.modules.threat_intelligence.engines.engines.wapiti_engine import WapitiEngine
from app.modules.threat_intelligence.engines.engines.openvas_engine import OpenVASEngine
from app.modules.threat_intelligence.engines.engines.wazuh_engine import WazuhEngine
from app.modules.threat_intelligence.engines.engines.prowler_engine import ProwlerEngine
from app.modules.threat_intelligence.engines.engines.scoutsuite_engine import ScoutSuiteEngine
from app.modules.threat_intelligence.engines.engines.trivy_engine import TrivyEngine
from app.modules.threat_intelligence.engines.engines.gitleaks_engine import GitleaksEngine
from app.modules.threat_intelligence.engines.engines.semgrep_engine import SemgrepEngine
from app.modules.threat_intelligence.engines.engines.crtsh_engine import CRTSHEngine

logger = logging.getLogger("sentinel.scanner.registry")


class ScannerRegistry:
    """
    Dynamic Engine Registry for all Sentinel Security & Threat Intelligence Scanning Engines.
    """

    _instance = None

    def __init__(self):
        self._engines: Dict[str, ScannerEngine] = {}
        self._initialize_default_engines()

    @classmethod
    def get_instance(cls) -> "ScannerRegistry":
        if cls._instance is None:
            cls._instance = ScannerRegistry()
        return cls._instance

    def _initialize_default_engines(self):
        """Registers all built-in core scanning and discovery engines."""
        default_engines = [
            # External Attack Surface & DNS
            DNSEnumerationEngine(),
            SubfinderEngine(),
            DNSxEngine(),
            AmassEngine(),
            ASNMapEngine(),
            CRTSHEngine(),
            CDNCheckEngine(),
            UncoverEngine(),
            # Network & Port Discovery
            HostDiscoveryEngine(),
            PortServiceDiscoveryEngine(),
            NaabuEngine(),
            MasscanEngine(),
            # Web Discovery & Technologies
            HTTPDiscoveryEngine(),
            HTTPXEngine(),
            TechnologyDetectionEngine(),
            TLSInspectionEngine(),
            TestsslEngine(),
            WebCrawlerEngine(),
            KatanaEngine(),
            OpenAPIDiscoveryEngine(),
            # Web Application Security & Vulnerabilities
            ZAPSpiderEngine(),
            ZAPActiveScanEngine(),
            NucleiEngine(),
            NiktoEngine(),
            WapitiEngine(),
            DalfoxEngine(),
            OpenVASEngine(),
            # Cloud, Container, Code & Endpoint Security
            ProwlerEngine(),
            ScoutSuiteEngine(),
            TrivyEngine(),
            GitleaksEngine(),
            SemgrepEngine(),
            WazuhEngine(),
            # Threat Intelligence & Graph Correlation
            ThreatIntelligenceCorrelationEngine(),
        ]
        for eng in default_engines:
            self.register(eng)

    def register(self, engine: ScannerEngine):
        """Registers a new scanner engine."""
        self._engines[engine.engine_id()] = engine
        logger.info(f"Registered scanner engine '{engine.name()}' [{engine.engine_id()}] ({engine.execution_mode().value})")

    def get(self, engine_id: str) -> Optional[ScannerEngine]:
        """Retrieves an engine by unique identifier."""
        return self._engines.get(engine_id)

    def list(self) -> List[ScannerEngine]:
        """Returns all registered engine instances."""
        return list(self._engines.values())

    def list_engines(self) -> List[Dict[str, Any]]:
        """Returns metadata for all registered engines."""
        results = []
        for eng in self._engines.values():
            results.append({
                "engine_id": eng.engine_id(),
                "name": eng.name(),
                "description": eng.description(),
                "category": eng.category().value,
                "execution_mode": eng.execution_mode().value,
                "version": eng.version(),
                "supported_target_types": eng.supported_target_types(),
                "supported_scan_profiles": eng.supported_scan_profiles(),
                "requires_active_authorization": eng.requires_active_authorization(),
                "capabilities": eng.capabilities()
            })
        return results

    def get_for_target(self, target_type_or_target: str, target_type: Optional[str] = None) -> List[ScannerEngine]:
        """Returns all engines capable of scanning the given target type."""
        t_type = target_type or target_type_or_target
        t_upper = t_type.upper()
        return [eng for eng in self._engines.values() if t_upper in eng.supported_target_types()]

    def get_for_profile(self, profile: str, target_type: Optional[str] = None) -> List[ScannerEngine]:
        """Returns engines matched to a specific scan profile and optional target type."""
        p_upper = profile.upper()
        engines = [eng for eng in self._engines.values() if p_upper in eng.supported_scan_profiles()]
        if target_type:
            t_upper = target_type.upper()
            engines = [eng for eng in engines if t_upper in eng.supported_target_types()]
        return engines

    async def health_check_all(self) -> List[Dict[str, Any]]:
        """Executes asynchronous health checks across all registered scanner engines."""
        health_reports = []
        for eng in self._engines.values():
            try:
                check = await eng.health_check()
                health_reports.append({
                    "engine_id": eng.engine_id(),
                    "name": eng.name(),
                    "category": eng.category().value,
                    "execution_mode": eng.execution_mode().value,
                    "version": eng.version(),
                    "status": check.get("status", "READY"),
                    "details": check.get("details", "")
                })
            except Exception as e:
                health_reports.append({
                    "engine_id": eng.engine_id(),
                    "name": eng.name(),
                    "category": eng.category().value,
                    "execution_mode": eng.execution_mode().value,
                    "version": eng.version(),
                    "status": "DEGRADED",
                    "details": str(e)
                })
        return health_reports


scanner_registry = ScannerRegistry.get_instance()
