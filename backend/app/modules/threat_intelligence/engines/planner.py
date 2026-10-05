import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.modules.threat_intelligence.engines.base import ScannerEngine, ExecutionMode
from app.modules.threat_intelligence.engines.registry import scanner_registry
from app.modules.threat_intelligence.engines.validator import AuthorizationGate, TargetValidator


class ScanPlan(BaseModel):
    scan_id: str
    target: str
    target_type: str
    scan_profile: str
    scope_id: Optional[str] = None
    is_active_authorized: bool = False
    engines: List[str] = Field(default_factory=list)
    stages: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_duration_seconds: int = 15

    def to_dict(self) -> Dict[str, Any]:
        return self.dict()


class ScanPlanner:
    """
    Constructs an intelligent, dependency-ordered execution plan for a security assessment target.
    """

    @classmethod
    def build_plan(
        cls,
        target: str,
        target_type: Optional[str] = None,
        scan_profile: str = "SAFE_DISCOVERY",
        scope_id: Optional[str] = None,
        scan_id: Optional[str] = None,
        is_active_authorized: bool = False,
        active_confirmed: Optional[bool] = None,
        selected_engines: Optional[List[str]] = None,
        scope: Optional[Dict[str, Any]] = None
    ) -> ScanPlan:
        sid = scan_id or f"ti_scan_{uuid.uuid4().hex[:10]}"
        is_active = is_active_authorized if active_confirmed is None else active_confirmed

        # 1. Detect & Canonicalize Target Type
        valid, reason, detected_type = TargetValidator.validate(target, target_type)
        if not valid:
            detected_type = target_type or TargetValidator.detect_target_type(target)

        # 2. Select Engines from Registry
        available_engines = scanner_registry.get_for_profile(scan_profile, detected_type)
        engine_ids = [eng.engine_id() for eng in available_engines]

        if selected_engines:
            engine_ids = [eid for eid in engine_ids if eid in selected_engines]

        # Prevent active vulnerability engine if not authorized/confirmed
        if not is_active and "zap_active_scan" in engine_ids:
            engine_ids.remove("zap_active_scan")

        # 3. Construct Topological Dependency Stages
        stages: List[Dict[str, Any]] = [
            {
                "stage_id": "passive_reconnaissance",
                "name": "Passive Reconnaissance & DNS/TLS Mapping",
                "parallel": True,
                "engines": [eid for eid in engine_ids if eid in ["dns_enumeration", "tls_inspection", "threat_intelligence_correlation"]]
            },
            {
                "stage_id": "network_perimeter",
                "name": "Network Reachability & Port Discovery",
                "parallel": True,
                "engines": [eid for eid in engine_ids if eid in ["host_discovery", "port_service_discovery"]]
            },
            {
                "stage_id": "web_discovery",
                "name": "HTTP Infrastructure & Technology Identification",
                "parallel": True,
                "engines": [eid for eid in engine_ids if eid in ["http_discovery", "technology_detection"]]
            },
            {
                "stage_id": "application_crawling",
                "name": "Deep Web Crawling & API Schema Discovery",
                "parallel": True,
                "engines": [eid for eid in engine_ids if eid in ["web_crawler", "openapi_discovery", "zap_spider"]]
            },
            {
                "stage_id": "active_assessment",
                "name": "Active Web Security Assessment",
                "parallel": False,
                "engines": [eid for eid in engine_ids if eid in ["zap_active_scan"]]
            },
            {
                "stage_id": "correlation_and_risk",
                "name": "Finding Normalization, Deduplication & Risk Scoring",
                "parallel": False,
                "engines": []
            }
        ]

        # Remove empty stages
        active_stages = [s for s in stages if s["engines"] or s["stage_id"] == "correlation_and_risk"]

        return ScanPlan(
            scan_id=sid,
            target=target,
            target_type=detected_type or "DOMAIN",
            scan_profile=scan_profile,
            scope_id=scope_id or (scope.get("id") if scope else None),
            is_active_authorized=is_active,
            engines=engine_ids,
            stages=active_stages,
            estimated_duration_seconds=max(5, len(engine_ids) * 2 + 3)
        )

    @classmethod
    def create_plan(
        cls,
        scan_id: str,
        target: str,
        target_type: Optional[str] = None,
        scan_profile: str = "COMPREHENSIVE",
        selected_engines: Optional[List[str]] = None,
        active_confirmed: bool = False,
        scope: Optional[Dict[str, Any]] = None
    ) -> ScanPlan:
        return cls.build_plan(
            target=target,
            target_type=target_type,
            scan_profile=scan_profile,
            scope_id=scope.get("id") if scope else None,
            scan_id=scan_id,
            is_active_authorized=active_confirmed,
            selected_engines=selected_engines,
            scope=scope
        )
