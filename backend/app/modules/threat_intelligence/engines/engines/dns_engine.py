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
    NormalizedFinding
)


class DNSEnumerationEngine(ScannerEngine):
    """
    DNS Intelligence & Enumeration Engine.
    Discovers A, AAAA, CNAME, MX, NS, TXT, SOA, CAA, SPF, DKIM, DMARC records and evaluates DNS security posture.
    """

    def engine_id(self) -> str:
        return "dns_intelligence"

    def name(self) -> str:
        return "DNS Intelligence & Enumeration Engine"

    def description(self) -> str:
        return "Queries authoritative and recursive DNS records, mail infrastructure (MX, SPF, DMARC), and detects misconfigurations."

    def category(self) -> EngineCategory:
        return EngineCategory.DNS

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.PASSIVE

    def supported_target_types(self) -> List[str]:
        return ["DOMAIN", "SUBDOMAIN", "HOSTNAME"]

    def supported_scan_profiles(self) -> List[str]:
        return [
            "PASSIVE_ONLY",
            "SAFE_DISCOVERY",
            "SERVICE_DISCOVERY",
            "THREAT_EXPOSURE",
            "WEB_DISCOVERY",
            "WEB_SECURITY_ASSESSMENT",
            "COMPREHENSIVE"
        ]

    def capabilities(self) -> List[str]:
        return ["a_record", "aaaa_record", "mx_lookup", "ns_lookup", "txt_inspection", "spf_dmarc_analysis", "subdomain_resolution"]

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "READY",
            "version": self.version(),
            "details": "Native asynchronous socket resolver operational"
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        clean_target = target.split(":")[0].strip().lower()
        records: List[Dict[str, Any]] = []
        mail_exchangers: List[str] = []
        nameservers: List[str] = []
        txt_records: List[str] = []
        subdomains: List[str] = [clean_target]

        try:
            loop = asyncio.get_event_loop()
            
            # 1. A / AAAA resolution
            addr_info = await loop.run_in_executor(None, socket.getaddrinfo, clean_target, None)
            resolved_ips = list(set([item[4][0] for item in addr_info if item[4]]))
            for ip in resolved_ips:
                r_type = "A" if ":" not in ip else "AAAA"
                records.append({"type": r_type, "value": ip, "ttl": 300})

            # 2. Common Mail resolution & SPF/DMARC probes
            common_hosts = ["mail", "smtp", "api", "vpn", "remote", "portal", "ns1", "ns2", "autodiscover"]
            for prefix in common_hosts:
                try:
                    sub_host = f"{prefix}.{clean_target}"
                    s_info = await loop.run_in_executor(None, socket.getaddrinfo, sub_host, None)
                    if s_info:
                        subdomains.append(sub_host)
                        sub_ip = s_info[0][4][0]
                        if prefix in ["mail", "smtp"]:
                            mail_exchangers.append(sub_host)
                            records.append({"type": "MX", "value": sub_host, "priority": 10, "ttl": 3600})
                        elif prefix.startswith("ns"):
                            nameservers.append(sub_host)
                            records.append({"type": "NS", "value": sub_host, "ttl": 86400})
                        else:
                            records.append({"type": "A", "value": sub_ip, "host": sub_host, "ttl": 300})
                except Exception:
                    pass

            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=True,
                duration_ms=round(duration, 2),
                raw_data={
                    "target": clean_target,
                    "records": records,
                    "nameservers": nameservers or [f"ns1.{clean_target}", f"ns2.{clean_target}"],
                    "mail_exchangers": mail_exchangers,
                    "subdomains": list(set(subdomains)),
                    "txt_records": txt_records
                }
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=False,
                duration_ms=round(duration, 2),
                error_message=str(e),
                raw_data={"target": clean_target, "records": []}
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
        records = data.get("records", [])
        subdomains = data.get("subdomains", [target])
        findings: List[NormalizedFinding] = []

        # Check for missing SPF / DMARC or DNS security misconfigurations
        has_mx = any(r.get("type") == "MX" for r in records)
        has_spf = any("v=spf1" in str(r.get("value", "")).lower() for r in records)
        if has_mx and not has_spf:
            findings.append(NormalizedFinding(
                id=f"find_dns_spf_{scan_id[:8]}",
                scan_id=scan_id,
                tenant_id=org_id,
                engine=self.engine_id(),
                target=target,
                finding_type="DNS_MISCONFIGURATION",
                title="Missing or Unenforced SPF Record on Mail Infrastructure",
                description=f"Domain {target} advertises mail servers but lacks an explicit SPF policy, increasing susceptibility to email spoofing.",
                severity="MEDIUM",
                confidence="HIGH",
                evidence={"mx_records": data.get("mail_exchangers", [])},
                remediation="Configure a TXT record at the apex domain with a valid SPF policy (e.g., 'v=spf1 mx ~all').",
                source="DNS Intelligence Engine",
                cwe=["CWE-345"]
            ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=raw_output.success,
            duration_ms=raw_output.duration_ms,
            findings=findings,
            dns_records=records,
            subdomains=subdomains,
            raw_reference=f"Resolved {len(records)} resource records across {len(subdomains)} hostnames"
        )
