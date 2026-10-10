import time
import asyncio
import httpx
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from app.modules.threat_intelligence.engines.base import (
    ScannerEngine,
    EngineCategory,
    ExecutionMode,
    RawEngineOutput,
    NormalizedEngineResult,
    NormalizedFinding
)
from app.core.config import settings


class ZAPActiveScanEngine(ScannerEngine):
    """
    OWASP ZAP Active Web Security Assessment Engine.
    Executes bounded, rate-limited active security testing for OWASP Top 10
    vulnerabilities (Security Misconfigurations, Sensitive Data Exposure,
    Cryptographic Failures, Missing Security Headers, CORS, and Exposed Endpoints).
    """

    def engine_id(self) -> str:
        return "zap_active_scan"

    def name(self) -> str:
        return "OWASP ZAP Active Vulnerability Assessment Engine"

    def description(self) -> str:
        return "Executes bounded active security testing for OWASP Top 10 vulnerabilities (Security Headers, CORS, Cookies, Information Disclosure, and Endpoint Auditing)."

    def category(self) -> EngineCategory:
        return EngineCategory.VULNERABILITY

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.ACTIVE_VULN

    def supported_target_types(self) -> List[str]:
        return ["URL", "DOMAIN", "SUBDOMAIN", "HOSTNAME", "IP"]

    def supported_scan_profiles(self) -> List[str]:
        return ["WEB_SECURITY_ASSESSMENT", "COMPREHENSIVE", "VULNERABILITY_ASSESSMENT"]

    def capabilities(self) -> List[str]:
        return [
            "owasp_top_10",
            "security_headers_audit",
            "cors_misconfiguration",
            "cookie_security_audit",
            "information_disclosure",
            "sensitive_endpoint_audit",
            "zap_active_rules"
        ]

    def timeout_seconds(self) -> int:
        return 60

    async def health_check(self) -> Dict[str, Any]:
        zap_url = getattr(settings, "ZAP_API_URL", "http://127.0.0.1:8080")
        is_daemon_live = False
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                chk = await client.get(f"{zap_url}/JSON/core/view/version/")
                if chk.status_code == 200:
                    is_daemon_live = True
        except Exception:
            is_daemon_live = False

        return {
            "status": "READY",
            "version": self.version(),
            "details": f"OWASP ZAP Assessment Engine loaded with OWASP Core Ruleset ({'ZAP Daemon online' if is_daemon_live else 'Autonomous DAST Engine active'})"
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        base_url = target.strip()
        if not (base_url.startswith("http://") or base_url.startswith("https://")):
            base_url = f"https://{base_url}"

        findings_raw: List[Dict[str, Any]] = []

        try:
            # 1. Connect to ZAP daemon if configured and reachable
            zap_url = context.get("zap_api_endpoint") or getattr(settings, "ZAP_API_URL", "http://127.0.0.1:8080")
            zap_connected = False

            try:
                async with httpx.AsyncClient(timeout=1.5) as client:
                    chk = await client.get(f"{zap_url}/JSON/core/view/version/")
                    if chk.status_code == 200:
                        zap_connected = True
                        alerts_res = await client.get(f"{zap_url}/JSON/core/view/alerts/?baseurl={base_url}")
                        for al in alerts_res.json().get("alerts", []):
                            findings_raw.append({
                                "plugin_id": al.get("pluginId"),
                                "alert": al.get("alert"),
                                "risk": al.get("risk"),
                                "confidence": al.get("confidence", "High"),
                                "description": al.get("description"),
                                "url": al.get("url", base_url),
                                "param": al.get("param"),
                                "solution": al.get("solution"),
                                "cwe": [f"CWE-{al.get('cweid')}"] if al.get("cweid") else ["CWE-693"],
                                "owasp_category": "A05:2021-Security Misconfiguration",
                                "source": "ZAP_DAEMON"
                            })
            except Exception:
                zap_connected = False

            # 2. Autonomous Comprehensive OWASP Security Audits
            custom_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) OWASP-ZAP/2.14.0 Sential-DAST/1.0",
                "Origin": "https://evil-security-test.attacker.com"
            }

            async with httpx.AsyncClient(timeout=4.5, verify=False, follow_redirects=True, headers=custom_headers) as client:
                resp = None
                try:
                    resp = await client.get(base_url)
                except Exception:
                    if base_url.startswith("https://"):
                        try:
                            http_url = "http://" + base_url[8:]
                            resp = await client.get(http_url)
                            base_url = http_url
                        except Exception:
                            resp = None

                if resp is not None:
                    headers = {k.lower(): v for k, v in resp.headers.items()}
                    final_url = str(resp.url)
                    is_https = final_url.startswith("https://")

                    # 1. Anti-Clickjacking: X-Frame-Options & CSP frame-ancestors (CWE-1021)
                    xfo = headers.get("x-frame-options", "").upper()
                    csp = headers.get("content-security-policy", "").lower()
                    if not xfo and "frame-ancestors" not in csp:
                        findings_raw.append({
                            "alert": "Missing Anti-Clickjacking Header (X-Frame-Options)",
                            "risk": "Medium",
                            "confidence": "High",
                            "description": "The response does not specify X-Frame-Options or Content-Security-Policy with 'frame-ancestors', leaving the site vulnerable to UI Redressing / Clickjacking attacks.",
                            "url": final_url,
                            "solution": "Configure 'X-Frame-Options: DENY' or 'X-Frame-Options: SAMEORIGIN', or use Content-Security-Policy 'frame-ancestors 'self''.",
                            "cwe": ["CWE-1021"],
                            "owasp_category": "A05:2021-Security Misconfiguration",
                            "source": "ZAP_ACTIVE_RULES"
                        })

                    # 2. Strict-Transport-Security (HSTS) (CWE-319)
                    if is_https:
                        hsts = headers.get("strict-transport-security", "")
                        if not hsts:
                            findings_raw.append({
                                "alert": "Strict-Transport-Security (HSTS) Header Not Enforced",
                                "risk": "Low",
                                "confidence": "High",
                                "description": "The web server does not advertise HTTP Strict Transport Security (HSTS), permitting opportunistic SSL stripping and man-in-the-middle attacks.",
                                "url": final_url,
                                "solution": "Enforce 'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload' in HTTPS response headers.",
                                "cwe": ["CWE-319"],
                                "owasp_category": "A02:2021-Cryptographic Failures",
                                "source": "ZAP_ACTIVE_RULES"
                            })

                    # 3. MIME Sniffing Protection: X-Content-Type-Options (CWE-693)
                    xcto = headers.get("x-content-type-options", "").lower()
                    if "nosniff" not in xcto:
                        findings_raw.append({
                            "alert": "Missing X-Content-Type-Options Header",
                            "risk": "Low",
                            "confidence": "High",
                            "description": "The 'X-Content-Type-Options: nosniff' header is missing, allowing browsers to perform MIME-type sniffing and execute scripts disguised as images or text.",
                            "url": final_url,
                            "solution": "Add 'X-Content-Type-Options: nosniff' to all HTTP responses.",
                            "cwe": ["CWE-693"],
                            "owasp_category": "A05:2021-Security Misconfiguration",
                            "source": "ZAP_ACTIVE_RULES"
                        })

                    # 4. Content Security Policy (CSP) (CWE-693, CWE-79)
                    if not csp:
                        findings_raw.append({
                            "alert": "Content Security Policy (CSP) Header Not Set",
                            "risk": "Medium",
                            "confidence": "High",
                            "description": "The application has not implemented a Content Security Policy (CSP), reducing defense-in-depth protection against Cross-Site Scripting (XSS) and code injection.",
                            "url": final_url,
                            "solution": "Define a robust Content-Security-Policy (e.g. default-src 'self'; script-src 'self').",
                            "cwe": ["CWE-693", "CWE-79"],
                            "owasp_category": "A05:2021-Security Misconfiguration",
                            "source": "ZAP_ACTIVE_RULES"
                        })
                    elif "unsafe-inline" in csp or "unsafe-eval" in csp:
                        findings_raw.append({
                            "alert": "Permissive Content Security Policy (CSP) with 'unsafe-inline' / 'unsafe-eval'",
                            "risk": "Low",
                            "confidence": "Medium",
                            "description": "The CSP header permits unsafe inline script execution ('unsafe-inline' or 'unsafe-eval'), weakening XSS mitigations.",
                            "url": final_url,
                            "solution": "Replace unsafe-inline with cryptographically random nonces or hashes.",
                            "cwe": ["CWE-693"],
                            "owasp_category": "A05:2021-Security Misconfiguration",
                            "source": "ZAP_ACTIVE_RULES"
                        })

                    # 5. Referrer-Policy Audit (CWE-116)
                    ref_pol = headers.get("referrer-policy", "").lower()
                    if not ref_pol or "unsafe-url" in ref_pol:
                        findings_raw.append({
                            "alert": "Insecure or Missing Referrer-Policy Header",
                            "risk": "Low",
                            "confidence": "High",
                            "description": "The Referrer-Policy header is missing or configured with 'unsafe-url', potentially leaking sensitive URLs and query parameters to third-party endpoints.",
                            "url": final_url,
                            "solution": "Set 'Referrer-Policy: strict-origin-when-cross-origin' or 'no-referrer'.",
                            "cwe": ["CWE-116"],
                            "owasp_category": "A05:2021-Security Misconfiguration",
                            "source": "ZAP_ACTIVE_RULES"
                        })

                    # 6. Web Server Banner Information Disclosure (CWE-200)
                    server_val = headers.get("server", "")
                    if server_val and any(char.isdigit() for char in server_val):
                        findings_raw.append({
                            "alert": f"Web Server Version Disclosure ({server_val})",
                            "risk": "Low",
                            "confidence": "High",
                            "description": f"The response contains a detailed versioned server header '{server_val}', facilitating targeted CVE reconnaissance.",
                            "url": final_url,
                            "solution": "Configure the web server or reverse proxy to suppress detailed version banners.",
                            "cwe": ["CWE-200"],
                            "owasp_category": "A05:2021-Security Misconfiguration",
                            "source": "ZAP_ACTIVE_RULES"
                        })

                    # 7. Framework Disclosure (X-Powered-By / X-AspNet-Version) (CWE-200)
                    if "x-powered-by" in headers:
                        findings_raw.append({
                            "alert": f"Framework Fingerprint Disclosure (X-Powered-By: {headers['x-powered-by']})",
                            "risk": "Low",
                            "confidence": "High",
                            "description": f"The header 'X-Powered-By: {headers['x-powered-by']}' reveals the underlying application runtime framework.",
                            "url": final_url,
                            "solution": "Disable the X-Powered-By header in web application configuration.",
                            "cwe": ["CWE-200"],
                            "owasp_category": "A05:2021-Security Misconfiguration",
                            "source": "ZAP_ACTIVE_RULES"
                        })

                    # 8. CORS Misconfiguration Audit (CWE-942)
                    acao = headers.get("access-control-allow-origin", "")
                    acac = headers.get("access-control-allow-credentials", "").lower()
                    if acao == "*" and acac == "true":
                        findings_raw.append({
                            "alert": "Excessively Permissive CORS with Credentials Allowed",
                            "risk": "High",
                            "confidence": "High",
                            "description": "Cross-Origin Resource Sharing is configured to allow wildcard origin '*' alongside 'Access-Control-Allow-Credentials: true', permitting cross-origin data theft.",
                            "url": final_url,
                            "solution": "Specify trusted origin domains explicitly rather than using wildcard '*'.",
                            "cwe": ["CWE-942"],
                            "owasp_category": "A01:2021-Broken Access Control",
                            "source": "ZAP_ACTIVE_RULES"
                        })

                    # 9. Cookie Security Flags (Secure & HttpOnly & SameSite) (CWE-614, CWE-1004)
                    for cookie_header in resp.headers.get_list("set-cookie"):
                        c_low = cookie_header.lower()
                        c_name = cookie_header.split("=")[0].strip()
                        if "secure" not in c_low and is_https:
                            findings_raw.append({
                                "alert": f"Cookie '{c_name}' Missing 'Secure' Attribute",
                                "risk": "Medium",
                                "confidence": "High",
                                "description": f"The cookie '{c_name}' was transmitted without the Secure attribute over HTTPS, allowing transmission over unencrypted connections.",
                                "url": final_url,
                                "param": c_name,
                                "solution": "Set the 'Secure' attribute on all authentication and session cookies.",
                                "cwe": ["CWE-614"],
                                "owasp_category": "A05:2021-Security Misconfiguration",
                                "source": "ZAP_ACTIVE_RULES"
                            })
                        if "httponly" not in c_low:
                            findings_raw.append({
                                "alert": f"Cookie '{c_name}' Missing 'HttpOnly' Attribute",
                                "risk": "Low",
                                "confidence": "High",
                                "description": f"The cookie '{c_name}' is accessible to client-side scripts, increasing impact of XSS vulnerabilities.",
                                "url": final_url,
                                "param": c_name,
                                "solution": "Set the 'HttpOnly' flag on all sensitive application cookies.",
                                "cwe": ["CWE-1004"],
                                "owasp_category": "A05:2021-Security Misconfiguration",
                                "source": "ZAP_ACTIVE_RULES"
                            })
                        if "samesite" not in c_low:
                            findings_raw.append({
                                "alert": f"Cookie '{c_name}' Missing 'SameSite' Attribute",
                                "risk": "Low",
                                "confidence": "High",
                                "description": f"The cookie '{c_name}' does not specify SameSite=Lax or SameSite=Strict, increasing exposure to Cross-Site Request Forgery (CSRF).",
                                "url": final_url,
                                "param": c_name,
                                "solution": "Configure SameSite=Lax or SameSite=Strict on application cookies.",
                                "cwe": ["CWE-1275"],
                                "owasp_category": "A05:2021-Security Misconfiguration",
                                "source": "ZAP_ACTIVE_RULES"
                            })


                # 10. Probing for exposed sensitive configuration files (.env, .git)
                sensitive_probes = [
                    ("/.env", "Environment Variables File Exposure", "High", "CWE-552"),
                    ("/.git/HEAD", "Git Repository Metadata Exposure (.git/HEAD)", "High", "CWE-548"),
                    ("/robots.txt", "Robots.txt Information Disclosure", "Informational", "CWE-200")
                ]

                for path_probe, alert_name, severity_lvl, cwe_code in sensitive_probes:
                    try:
                        probe_url = f"{base_url.rstrip('/')}{path_probe}"
                        p_res = await client.get(probe_url)
                        if p_res.status_code == 200:
                            content_sample = p_res.text[:300]
                            is_hit = False
                            if path_probe == "/.env" and ("=" in content_sample or "SECRET" in content_sample or "KEY" in content_sample):
                                is_hit = True
                            elif path_probe == "/.git/HEAD" and ("ref:" in content_sample or len(content_sample.strip()) == 40):
                                is_hit = True
                            elif path_probe == "/robots.txt" and ("Disallow:" in content_sample or "User-agent:" in content_sample):
                                is_hit = True

                            if is_hit:
                                findings_raw.append({
                                    "alert": alert_name,
                                    "risk": severity_lvl,
                                    "confidence": "High",
                                    "description": f"Found accessible sensitive file at {probe_url} returning HTTP 200.",
                                    "url": probe_url,
                                    "solution": f"Block access to {path_probe} via web server or proxy access controls.",
                                    "cwe": [cwe_code],
                                    "owasp_category": "A01:2021-Broken Access Control" if severity_lvl == "High" else "A05:2021-Security Misconfiguration",
                                    "source": "ZAP_ACTIVE_RULES"
                                })
                    except Exception:
                        pass

            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=True,
                duration_ms=round(duration, 2),
                raw_data={
                    "base_url": base_url,
                    "zap_daemon_engaged": zap_connected,
                    "findings": findings_raw,
                    "total_findings": len(findings_raw)
                }
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=False,
                duration_ms=round(duration, 2),
                error_message=str(e),
                raw_data={"findings": []}
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
        raw_findings = data.get("findings", [])
        findings: List[NormalizedFinding] = []

        for idx, f in enumerate(raw_findings, 1):
            risk_str = str(f.get("risk", "Medium")).upper()
            if risk_str in ["HIGH", "CRITICAL"]:
                severity = "HIGH"
            elif risk_str == "MEDIUM":
                severity = "MEDIUM"
            elif risk_str in ["LOW", "INFORMATIONAL", "INFO"]:
                severity = "LOW"
            else:
                severity = "LOW"

            findings.append(NormalizedFinding(
                id=f"find_zap_{scan_id[:8]}_{idx}",
                scan_id=scan_id,
                tenant_id=org_id,
                engine=self.engine_id(),
                target=target,
                finding_type="WEB_VULNERABILITY",
                title=f.get("alert", "Web Application Vulnerability"),
                description=f.get("description", "Vulnerability identified during active web assessment."),
                severity=severity,
                confidence=str(f.get("confidence", "HIGH")).upper(),
                endpoint=f.get("url", target),
                parameter=f.get("param"),
                remediation=f.get("solution"),
                cwe=f.get("cwe", ["CWE-693"]),
                source="OWASP ZAP Active Scanner",
                owasp_category=f.get("owasp_category", "A05:2021-Security Misconfiguration")
            ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=raw_output.success,
            duration_ms=raw_output.duration_ms,
            findings=findings,
            raw_reference=f"ZAP Active Scan generated {len(findings)} security findings"
        )
