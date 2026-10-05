from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class EngineCategory(str, Enum):
    DNS = "DNS"
    NETWORK = "NETWORK"
    PORT_SERVICE = "PORT_SERVICE"
    HTTP = "HTTP"
    TECHNOLOGY = "TECHNOLOGY"
    TLS = "TLS"
    CRAWLER = "CRAWLER"
    API_DISCOVERY = "API_DISCOVERY"
    VULNERABILITY = "VULNERABILITY"
    THREAT_INTEL = "THREAT_INTEL"
    ATTACK_SURFACE = "ATTACK_SURFACE"
    CLOUD_SECURITY = "CLOUD_SECURITY"
    CONTAINER_SECURITY = "CONTAINER_SECURITY"
    CODE_SECURITY = "CODE_SECURITY"
    SECRET_DISCOVERY = "SECRET_DISCOVERY"
    ENDPOINT_SECURITY = "ENDPOINT_SECURITY"
    WEB_SECURITY = "WEB_SECURITY"


class ExecutionMode(str, Enum):
    PASSIVE = "PASSIVE"
    SAFE = "SAFE"
    SAFE_ACTIVE = "SAFE_ACTIVE"
    CONTROLLED_ACTIVE = "CONTROLLED_ACTIVE"
    ACTIVE_VULN = "ACTIVE_VULN"


class EngineHealthStatus(str, Enum):
    READY = "READY"
    NOT_INSTALLED = "NOT_INSTALLED"
    DISABLED = "DISABLED"
    DEGRADED = "DEGRADED"


class PreflightResult(BaseModel):
    ready: bool = True
    error_message: Optional[str] = None
    target_canonical: Optional[str] = None


class NormalizedFinding(BaseModel):
    id: str
    scan_id: str
    tenant_id: str = "org_cyber_command"
    engine: str
    engine_version: str = "1.0.0"
    target: str
    asset_id: Optional[str] = None
    finding_type: str
    title: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL
    confidence: str = "HIGH"  # HIGH, MEDIUM, LOW
    status: str = "OPEN"
    evidence: Dict[str, Any] = Field(default_factory=dict)
    endpoint: Optional[str] = None
    method: Optional[str] = None
    parameter: Optional[str] = None
    cwe: List[str] = Field(default_factory=list)
    cve: List[str] = Field(default_factory=list)
    owasp_category: Optional[str] = None
    cvss_score: Optional[float] = None
    remediation: Optional[str] = None
    source: str
    raw_reference: Optional[str] = None
    fingerprint: Optional[str] = None
    first_seen: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DiscoveredService(BaseModel):
    host: str
    port: int
    protocol: str = "tcp"
    state: str = "open"
    service: str = "unknown"
    product: Optional[str] = None
    version: Optional[str] = None
    banner: Optional[str] = None
    tls_enabled: bool = False


class DiscoveredEndpoint(BaseModel):
    url: str
    method: str = "GET"
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    parameters: List[str] = Field(default_factory=list)
    forms: List[Dict[str, Any]] = Field(default_factory=list)
    source_engine: str = "web_crawler"


class DiscoveredTechnology(BaseModel):
    name: str
    category: str
    version: Optional[str] = None
    confidence: str = "HIGH"
    icon: Optional[str] = None
    evidence: Optional[str] = None


class RawEngineOutput(BaseModel):
    engine_id: str
    success: bool
    duration_ms: float
    raw_data: Any = None
    error_message: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None


class NormalizedEngineResult(BaseModel):
    engine_id: str
    category: EngineCategory = EngineCategory.ATTACK_SURFACE
    execution_mode: ExecutionMode = ExecutionMode.PASSIVE
    success: bool = True
    duration_ms: float = 0.0
    findings: List[NormalizedFinding] = Field(default_factory=list)
    services: List[DiscoveredService] = Field(default_factory=list)
    endpoints: List[DiscoveredEndpoint] = Field(default_factory=list)
    technologies: List[DiscoveredTechnology] = Field(default_factory=list)
    dns_records: List[Dict[str, Any]] = Field(default_factory=list)
    certificates: List[Dict[str, Any]] = Field(default_factory=list)
    subdomains: List[str] = Field(default_factory=list)
    ip_hosts: List[Dict[str, Any]] = Field(default_factory=list)
    indicators: List[Dict[str, Any]] = Field(default_factory=list)
    raw_reference: Optional[str] = None
    error_message: Optional[str] = None


class ScannerEngine(ABC):
    """
    Abstract Base Class for all Sentinel Security & Threat Intelligence Scanning Engines.
    """

    @abstractmethod
    def engine_id(self) -> str:
        """Unique identifier (e.g. 'dns_engine', 'nmap_network', 'zap_spider')."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Human-readable display name."""
        pass

    @abstractmethod
    def description(self) -> str:
        """Detailed description of engine discovery capabilities."""
        pass

    @abstractmethod
    def category(self) -> EngineCategory:
        """Engine classification category."""
        pass

    @abstractmethod
    def execution_mode(self) -> ExecutionMode:
        """Execution mode: PASSIVE, SAFE_ACTIVE, or ACTIVE_VULN."""
        pass

    @abstractmethod
    def supported_target_types(self) -> List[str]:
        """List of target types supported (DOMAIN, IP, URL, IP_RANGE, etc.)."""
        pass

    @abstractmethod
    def supported_scan_profiles(self) -> List[str]:
        """Profiles that can trigger this engine."""
        pass

    def requires_active_authorization(self) -> bool:
        """Returns True if the engine performs active probing or testing."""
        return self.execution_mode() in [ExecutionMode.SAFE_ACTIVE, ExecutionMode.ACTIVE_VULN]

    def is_destructive(self) -> bool:
        """Guaranteed False across all Sentinel engines."""
        return False

    def version(self) -> str:
        return "1.0.0"

    def capabilities(self) -> List[str]:
        return []

    def is_installed(self) -> bool:
        return True

    def is_enabled(self) -> bool:
        return True

    def timeout_seconds(self) -> int:
        return 30

    async def preflight(self) -> bool:
        """Optional pre-execution check."""
        return True

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Returns real-time engine availability:
        {"status": "READY" | "NOT_INSTALLED" | "DISABLED", "version": "...", "details": "..."}
        """
        pass

    @abstractmethod
    async def execute(
        self,
        target: str,
        target_type: str,
        context: Dict[str, Any]
    ) -> RawEngineOutput:
        """Executes the specialized engine logic and produces raw output."""
        pass

    @abstractmethod
    def normalize(
        self,
        raw_output: RawEngineOutput,
        target: str,
        target_type: str,
        scan_id: str,
        org_id: str
    ) -> NormalizedEngineResult:
        """Parses and normalizes raw engine output into the common findings model."""
        pass

    async def cancel(self, scan_id: str):
        """Optional hook to terminate running subprocess or connection."""
        pass

    async def cleanup(self):
        """Cleanup temporary files or resources."""
        pass
