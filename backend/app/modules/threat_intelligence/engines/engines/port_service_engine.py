import time
import socket
import asyncio
from typing import Dict, Any, List, Optional
from app.modules.threat_intelligence.engines.base import (
    ScannerEngine,
    EngineCategory,
    ExecutionMode,
    RawEngineOutput,
    NormalizedEngineResult,
    DiscoveredService,
    NormalizedFinding
)


COMMON_PORTS = [
    (80, "tcp", "http"),
    (443, "tcp", "https"),
    (8080, "tcp", "http-proxy"),
    (8443, "tcp", "https-alt"),
    (22, "tcp", "ssh"),
    (21, "tcp", "ftp"),
    (25, "tcp", "smtp"),
    (53, "tcp", "domain"),
    (3306, "tcp", "mysql"),
    (5432, "tcp", "postgresql"),
    (6379, "tcp", "redis"),
    (27017, "tcp", "mongodb"),
    (3389, "tcp", "ms-wbt-server"),
]


class PortServiceDiscoveryEngine(ScannerEngine):
    """
    Port & Service Discovery Engine.
    Discovers open TCP ports, grabs service banners, identifies protocol versions, and maps perimeter surface.
    """

    def engine_id(self) -> str:
        return "port_service_discovery"

    def name(self) -> str:
        return "Port & Service Fingerprinting Engine"

    def description(self) -> str:
        return "Probes authorized TCP service ports, extracts protocol banners, and identifies running server daemon versions."

    def category(self) -> EngineCategory:
        return EngineCategory.PORT_SERVICE

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.SAFE_ACTIVE

    def supported_target_types(self) -> List[str]:
        return ["IP", "IP_RANGE", "HOSTNAME", "DOMAIN"]

    def supported_scan_profiles(self) -> List[str]:
        return ["SERVICE_DISCOVERY", "NETWORK_DISCOVERY", "COMPREHENSIVE"]

    def capabilities(self) -> List[str]:
        return ["tcp_port_discovery", "service_fingerprint", "banner_grabbing", "tls_detection"]

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "READY",
            "version": self.version(),
            "details": f"Multi-threaded asynchronous port prober active ({len(COMMON_PORTS)} profile ports)"
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        clean_target = target.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0].strip()
        open_services: List[Dict[str, Any]] = []

        try:
            loop = asyncio.get_event_loop()
            addr_info = await loop.run_in_executor(None, socket.getaddrinfo, clean_target, None)
            ip = addr_info[0][4][0] if addr_info else clean_target

            for port, proto, svc_hint in COMMON_PORTS:
                def _probe_port():
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1.2)
                    try:
                        s.connect((ip, port))
                        banner = ""
                        try:
                            s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                            banner = s.recv(512).decode("utf-8", errors="ignore").strip()
                        except Exception:
                            pass
                        s.close()
                        return True, banner
                    except Exception:
                        return False, ""

                is_open, banner_text = await loop.run_in_executor(None, _probe_port)
                if is_open:
                    open_services.append({
                        "host": clean_target,
                        "ip": ip,
                        "port": port,
                        "protocol": proto,
                        "state": "open",
                        "service": svc_hint,
                        "product": banner_text.splitlines()[0] if banner_text else svc_hint.upper(),
                        "banner": banner_text[:200] if banner_text else None,
                        "tls_enabled": port in [443, 8443, 993, 995]
                    })

            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=True,
                duration_ms=round(duration, 2),
                raw_data={"target": clean_target, "ip": ip, "services": open_services}
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=False,
                duration_ms=round(duration, 2),
                error_message=str(e),
                raw_data={"target": clean_target, "services": []}
            )

    def normalize(
        self,
        raw_output: RawEngineOutput,
        target: str,
        target_type: str,
        scan_id: str,
        org_id: str
    ) -> NormalizedEngineResult:
        data = raw_output.raw_data or {}
        svcs = data.get("services", [])
        services: List[DiscoveredService] = []
        findings: List[NormalizedFinding] = []

        for s in svcs:
            services.append(DiscoveredService(
                host=s["host"],
                port=s["port"],
                protocol=s["protocol"],
                state=s["state"],
                service=s["service"],
                product=s.get("product"),
                banner=s.get("banner"),
                tls_enabled=s.get("tls_enabled", False)
            ))

            # Flag clear-text or database services directly exposed to the internet
            if s["port"] in [21, 23, 3306, 5432, 6379, 27017]:
                findings.append(NormalizedFinding(
                    id=f"find_port_exp_{scan_id[:8]}_{s['port']}",
                    scan_id=scan_id,
                    tenant_id=org_id,
                    engine=self.engine_id(),
                    target=target,
                    finding_type="EXPOSED_DATABASE_SERVICE",
                    title=f"Direct Internet Exposure of Service on Port {s['port']} ({s['service']})",
                    description=f"Port {s['port']} ({s['service']}) is directly reachable from public IP space without VPN or firewall boundaries.",
                    severity="HIGH" if s["port"] in [3306, 5432, 6379, 27017] else "MEDIUM",
                    confidence="HIGH",
                    evidence={"port": s["port"], "service": s["service"], "host": s["host"]},
                    remediation=f"Restrict port {s['port']} access to internal VPC networks or trusted IP CIDR blocks.",
                    source="Port & Service Fingerprinting Engine",
                    cwe=["CWE-200", "CWE-284"]
                ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=raw_output.success,
            duration_ms=raw_output.duration_ms,
            findings=findings,
            services=services,
            raw_reference=f"Discovered {len(services)} open ports on target perimeter"
        )
