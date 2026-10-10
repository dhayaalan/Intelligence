import time
import uuid
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import (
    HealthCheckResult, ModuleHealthStatus, EntityPayload, RelationshipPayload,
    EvidencePayload, EntityType, RelationshipType
)
from app.modules.threat_intelligence.engines.base import (
    ScannerEngine, RawEngineOutput, NormalizedEngineResult
)

class ThreatIntelEngineAdapter(ProviderAdapter):
    """
    Adapter that wraps any Sentinel Security Scanner Engine into a pluggable Sential ProviderAdapter.
    Exposes full preflight, real execution, finding normalization, and health checking without mock data.
    """

    def __init__(self, engine: ScannerEngine):
        self._engine = engine
        self._id = engine.engine_id()
        self._name = engine.name()
        self._category = engine.category().value
        self._supported_targets = [t.lower() for t in engine.supported_target_types()]
        self._capabilities = engine.capabilities() or [self._category.lower()]

    @property
    def provider_id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def category(self) -> str:
        return self._category

    @property
    def supported_targets(self) -> List[str]:
        return self._supported_targets

    @property
    def capabilities(self) -> List[str]:
        return self._capabilities

    @property
    def version(self) -> str:
        return self._engine.version()

    async def health_check(self) -> HealthCheckResult:
        try:
            res = await self._engine.health_check()
            st = res.get("status", "READY").upper()
            if st in ("READY", "VERIFIED", "HEALTHY"):
                status_enum = ModuleHealthStatus.HEALTHY
            elif st in ("NOT_INSTALLED", "DISABLED", "NOT_CONFIGURED"):
                status_enum = ModuleHealthStatus.DEGRADED
            else:
                status_enum = ModuleHealthStatus.DEGRADED
                
            return HealthCheckResult(
                status=status_enum,
                message=res.get("details", f"Engine {self._name} status: {st}")
            )
        except Exception as e:
            return HealthCheckResult(
                status=ModuleHealthStatus.UNAVAILABLE,
                message=f"Health check failed: {str(e)}"
            )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        target = request.query.strip()
        target_type = request.target_type.lower()
        context = {**request.config, **request.options}

        try:
            # Check preflight safely
            try:
                pre = await self._engine.preflight(target, target_type.upper())
                if hasattr(pre, "ready") and not pre.ready:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="skipped",
                        duration_ms=(time.time() - start_time) * 1000,
                        error=getattr(pre, "error_message", "Preflight skipped")
                    )
            except TypeError:
                try:
                    await self._engine.preflight()
                except Exception:
                    pass

            # Real execution of scanner engine
            raw_out: RawEngineOutput = await self._engine.execute(
                target=target,
                target_type=target_type.upper(),
                context=context
            )

            # Normalize output
            scan_id = f"scan_{uuid.uuid4().hex[:8]}"
            try:
                norm_res: NormalizedEngineResult = self._engine.normalize(
                    raw_out,
                    target,
                    target_type.upper(),
                    scan_id,
                    "tenant_sential"
                )
            except TypeError:
                norm_res: NormalizedEngineResult = self._engine.normalize(
                    raw_output=raw_out,
                    target=target,
                    target_type=target_type.upper(),
                    scan_id=scan_id
                )

            # Convert engine normalized results to Sential entities & evidence
            entities = []
            findings = []
            evidence = []

            # 1. Findings & Vulnerabilities
            for f in norm_res.findings:
                findings.append({
                    "title": f.title,
                    "description": f.description,
                    "severity": f.severity,
                    "finding_type": f.finding_type,
                    "cve": f.cve,
                    "cwe": f.cwe,
                    "remediation": f.remediation,
                    "endpoint": f.endpoint,
                    "owasp_category": f.owasp_category,
                    "source_engine": self.provider_id
                })
                # Emit first-class VULNERABILITY entity for intelligence graph and search results
                entities.append(EntityPayload(
                    type=EntityType.VULNERABILITY,
                    value=f.title,
                    confidence=0.92 if str(f.confidence).upper() == "HIGH" else 0.82,
                    sources=[self.provider_id],
                    metadata={
                        "severity": f.severity,
                        "finding_type": f.finding_type,
                        "endpoint": f.endpoint,
                        "cwe": f.cwe,
                        "cve": f.cve,
                        "remediation": f.remediation,
                        "owasp_category": f.owasp_category,
                        "description": f.description,
                        "source": self.name
                    }
                ).dict())

            # 2. Discovered Application Endpoints (from ZAP Spider & Crawlers)
            for ep in getattr(norm_res, "endpoints", []):
                entities.append(EntityPayload(
                    type=EntityType.URL,
                    value=ep.url,
                    confidence=0.90,
                    sources=[self.provider_id],
                    metadata={
                        "method": ep.method,
                        "status_code": ep.status_code,
                        "content_type": ep.content_type,
                        "source_engine": ep.source_engine
                    }
                ).dict())

            # 3. Discovered Subdomains
            for sub in norm_res.subdomains:
                if sub != target:
                    entities.append(EntityPayload(
                        type=EntityType.SUBDOMAIN,
                        value=sub,
                        confidence=0.95,
                        sources=[self.provider_id],
                        metadata={"parent_domain": target}
                    ).dict())

            # 4. Discovered Services & Ports
            for svc in norm_res.services:
                host_str = str(svc.host or target).strip()
                # Strictly reject multi-word queries or non-hosts from becoming domain entities
                if not host_str or " " in host_str or not ("." in host_str or ":" in host_str):
                    continue
                if svc.state != "open":
                    continue

                entities.append(EntityPayload(
                    type=EntityType.HOSTNAME,
                    value=f"{host_str}:{svc.port}",
                    confidence=0.90,
                    sources=[self.provider_id],
                    metadata={
                        "host": host_str,
                        "port": svc.port,
                        "protocol": svc.protocol,
                        "service": svc.service,
                        "product": svc.product,
                        "state": svc.state
                    }
                ).dict())

            # 5. Technologies
            for tech in norm_res.technologies:
                entities.append(EntityPayload(
                    type=EntityType.TECHNOLOGY,
                    value=tech.name,
                    confidence=0.92,
                    sources=[self.provider_id],
                    metadata={"category": tech.category, "version": tech.version}
                ).dict())

            # 5. Cryptographic Evidence
            evidence_str = f"{self.provider_id}:{target}:{len(findings)}:{len(entities)}"
            sha256 = hashlib.sha256(evidence_str.encode()).hexdigest()
            evidence.append({
                "source": self.provider_id,
                "provider": self.provider_id,
                "module": "threat_intelligence",
                "reference": f"Target: {target}",
                "confidence": 0.95,
                "raw_data": {"findings_count": len(findings), "assets_count": len(entities), "engine_category": self._category},
                "hash": sha256
            })

            duration_ms = (time.time() - start_time) * 1000
            return ProviderResponse(
                provider_id=self.provider_id,
                status="success" if raw_out.success else "error",
                raw_data={
                    "findings": findings,
                    "entities": entities,
                    "evidence": evidence,
                    "raw_output": raw_out.raw_data
                },
                error=raw_out.error_message,
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                error=str(e),
                duration_ms=duration_ms
            )
