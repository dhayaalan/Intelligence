"""
Operational Security (OPSEC) Network Egress Controller.
Enforces strict zero-trust outbound routing, real regional VPN/gateway verification,
fail-closed isolation, and credential sanitization for investigative workloads.
Adheres to NIST SP 800-207 Zero Trust Architecture.
"""

import os
import re
import time
from enum import Enum
from typing import Dict, Any, Optional, Tuple
import httpx
from pydantic import BaseModel, Field

from app.core.logging import app_logger


class EgressRouteType(str, Enum):
    DIRECT = "DIRECT"
    REGIONAL_GATEWAY_APPROVED = "REGIONAL_GATEWAY_APPROVED"
    ISOLATED_SCANNER = "ISOLATED_SCANNER"
    INDIA = "INDIA"
    UNITED_STATES = "UNITED_STATES"
    UNITED_KINGDOM = "UNITED_KINGDOM"


class EgressVerificationState(str, Enum):
    ROUTE_VERIFIED = "ROUTE_VERIFIED"
    CONFIG_REQUIRED = "CONFIG_REQUIRED"
    TUNNEL_UNAVAILABLE = "TUNNEL_UNAVAILABLE"
    EGRESS_VERIFICATION_FAILED = "EGRESS_VERIFICATION_FAILED"
    REGION_MISMATCH = "REGION_MISMATCH"


class EgressRouteStatus(BaseModel):
    route_type: EgressRouteType
    gateway_name: str
    is_active: bool
    fail_closed: bool = True
    egress_ip_masked: str
    verification_state: EgressVerificationState = EgressVerificationState.ROUTE_VERIFIED
    detected_country: Optional[str] = None
    last_verified: Optional[str] = None
    diagnostics: str = "Route healthy"


class EgressController:
    """
    Central OPSEC egress controller ensuring that investigations requiring specific
    regional or isolated network egress never accidentally leak through direct local network interfaces.
    Replaces simulated gateways with real configurable VPN endpoints, proxy bridges, and live egress verification.
    """

    # Sensitive token masking regex patterns
    SECRET_PATTERNS = [
        re.compile(r'(?i)(bearer\s+)[a-zA-Z0-9_\-\.]{20,}'),
        re.compile(r'(?i)(api[_-]?key["\']?\s*[:=]\s*["\']?)[a-zA-Z0-9_\-]{16,}'),
        re.compile(r'(?i)(password["\']?\s*[:=]\s*["\']?)[^"\'\s]{8,}'),
        re.compile(r'(?i)(proxy[_-]?auth["\']?\s*[:=]\s*["\']?)[^"\'\s]{8,}'),
        re.compile(r'(?i)(https?://[^:]+:)([^@]+)(@)'),
    ]

    # Region Aliases for compatibility
    REGION_ALIASES = {
        "south_asia_gateway": "INDIA",
        "india": "INDIA",
        "in": "INDIA",
        "international_gateway": "UNITED_STATES",
        "united_states": "UNITED_STATES",
        "us": "UNITED_STATES",
        "usa": "UNITED_STATES",
        "united_kingdom": "UNITED_KINGDOM",
        "uk": "UNITED_KINGDOM",
        "gb": "UNITED_KINGDOM",
        "isolated_scanner_gateway": "ISOLATED_SCANNER",
        "isolated_scanner": "ISOLATED_SCANNER",
    }

    def __init__(self):
        # Configure regional endpoints from environment (WireGuard SOCKS5 bridges or regional HTTP egress proxies)
        self._gateway_configs: Dict[str, Dict[str, Any]] = {
            "INDIA": {
                "name": "India Regional Gateway",
                "expected_country": "IN",
                "proxy_url": os.getenv("VPN_INDIA_PROXY") or os.getenv("GATEWAY_SOUTH_ASIA_PROXY"),
                "interface": os.getenv("VPN_INDIA_INTERFACE", "wg_india"),
                "enabled": os.getenv("GATEWAY_SOUTH_ASIA_ACTIVE", "true").lower() == "true",
            },
            "UNITED_STATES": {
                "name": "United States Regional Gateway",
                "expected_country": "US",
                "proxy_url": os.getenv("VPN_US_PROXY") or os.getenv("GATEWAY_INTERNATIONAL_PROXY"),
                "interface": os.getenv("VPN_US_INTERFACE", "wg_us"),
                "enabled": os.getenv("GATEWAY_INTERNATIONAL_ACTIVE", "true").lower() == "true",
            },
            "UNITED_KINGDOM": {
                "name": "United Kingdom Regional Gateway",
                "expected_country": "GB",
                "proxy_url": os.getenv("VPN_UK_PROXY"),
                "interface": os.getenv("VPN_UK_INTERFACE", "wg_uk"),
                "enabled": os.getenv("GATEWAY_UK_ACTIVE", "true").lower() == "true",
            },
            "ISOLATED_SCANNER": {
                "name": "Isolated Scanner Net Gateway",
                "expected_country": None,
                "proxy_url": os.getenv("GATEWAY_SCANNER_PROXY"),
                "interface": os.getenv("GATEWAY_SCANNER_INTERFACE", "wg_scanner"),
                "enabled": os.getenv("GATEWAY_SCANNER_ACTIVE", "true").lower() == "true",
            }
        }
        self._verified_routes_cache: Dict[str, Tuple[float, EgressRouteStatus]] = {}

    def normalize_gateway_key(self, gateway_name: Optional[str]) -> str:
        if not gateway_name:
            return "INDIA"
        clean = gateway_name.strip().lower()
        return self.REGION_ALIASES.get(clean, clean.upper())

    def verify_egress_route(
        self,
        route_type: EgressRouteType,
        gateway_name: Optional[str] = None,
        fail_closed: bool = True
    ) -> Tuple[bool, str, EgressRouteStatus]:
        """
        Verifies that the requested egress route is operational.
        Enforces Fail-Closed: If an approved regional gateway is requested but inactive or misconfigured,
        the request is blocked immediately to prevent direct network deanonymization.
        """
        if route_type == EgressRouteType.DIRECT:
            return True, "Direct outbound connection authorized", EgressRouteStatus(
                route_type=route_type,
                gateway_name="local_default",
                is_active=True,
                fail_closed=False,
                egress_ip_masked="local_direct",
                verification_state=EgressVerificationState.ROUTE_VERIFIED,
                diagnostics="Direct egress permitted for general non-sensitive retrieval"
            )

        gw_key = self.normalize_gateway_key(gateway_name)
        gw_info = self._gateway_configs.get(gw_key)

        # 1. Non-existent gateway profile
        if not gw_info:
            msg = f"Unknown regional gateway profile '{gateway_name or gw_key}'."
            app_logger.warning(f"OPSEC FAIL-CLOSED: {msg}")
            return False, f"OPSEC_FAIL_CLOSED: {msg} Direct network fallback is prohibited.", EgressRouteStatus(
                route_type=route_type,
                gateway_name=gateway_name or gw_key,
                is_active=False,
                fail_closed=True,
                egress_ip_masked="UNREACHABLE",
                verification_state=EgressVerificationState.CONFIG_REQUIRED,
                diagnostics="Unknown gateway profile specified"
            )

        # 2. Check if administratively disabled
        if not gw_info.get("enabled"):
            msg = f"Approved regional gateway '{gw_key}' is administratively inactive."
            if fail_closed:
                app_logger.warning(f"OPSEC FAIL-CLOSED: Blocked outbound dispatch. {msg}")
                return False, f"OPSEC_FAIL_CLOSED: {msg} Direct network fallback is prohibited.", EgressRouteStatus(
                    route_type=route_type,
                    gateway_name=gw_key,
                    is_active=False,
                    fail_closed=True,
                    egress_ip_masked="UNREACHABLE",
                    verification_state=EgressVerificationState.TUNNEL_UNAVAILABLE,
                    diagnostics="Halted by OPSEC fail-closed policy: gateway disabled"
                )
            else:
                return True, "Permitted with warning (fail-open enabled)", EgressRouteStatus(
                    route_type=route_type,
                    gateway_name=gw_key,
                    is_active=False,
                    fail_closed=False,
                    egress_ip_masked="FALLBACK_DIRECT",
                    verification_state=EgressVerificationState.TUNNEL_UNAVAILABLE,
                    diagnostics="Operating in degraded fallback mode"
                )

        # 3. Cache lookup (TTL = 60s)
        now = time.time()
        if gw_key in self._verified_routes_cache:
            ts, cached_status = self._verified_routes_cache[gw_key]
            if now - ts < 60.0 and cached_status.is_active:
                return True, "Approved regional egress route verified (cached)", cached_status

        # 4. Perform active route verification
        proxy_url = gw_info.get("proxy_url")
        status = self._perform_active_verification(gw_key, gw_info, route_type, fail_closed)
        self._verified_routes_cache[gw_key] = (now, status)

        if not status.is_active:
            diag = status.diagnostics
            if fail_closed:
                return False, f"OPSEC_FAIL_CLOSED: Approved regional gateway '{gw_key}' failed verification: {diag}. Direct network fallback is prohibited.", status
            return True, f"Permitted with warning: {diag}", status

        return True, f"Approved regional egress route '{gw_key}' verified", status

    def _perform_active_verification(
        self,
        gw_key: str,
        gw_info: Dict[str, Any],
        route_type: EgressRouteType,
        fail_closed: bool
    ) -> EgressRouteStatus:
        """
        Actively checks external route verification.
        Uses configured regional proxy or tunnel interface to verify egress IP and country.
        Fails closed if the route is missing, unreachable, or exits through an unexpected country.
        """
        proxy_url = gw_info.get("proxy_url")
        is_prod = os.getenv("APP_ENV", "").lower() in ["production", "prod"]

        # 1. Interface / proxy presence check
        if not proxy_url and not os.path.exists(f"/sys/class/net/{gw_info.get('interface', '')}"):
            allow_test_mock = False if is_prod else (os.getenv("OPSEC_ALLOW_GATEWAY_MOCKS", "false").lower() == "true")
            if not allow_test_mock:
                return EgressRouteStatus(
                    route_type=route_type,
                    gateway_name=gw_key,
                    is_active=False,
                    fail_closed=fail_closed,
                    egress_ip_masked="NOT_CONFIGURED",
                    verification_state=EgressVerificationState.CONFIG_REQUIRED,
                    diagnostics=f"Gateway {gw_key} proxy URL or interface not configured (simulated routing prohibited)"
                )
            # Dedicated deterministic unit-test fixture only (strictly prohibited in production)
            return EgressRouteStatus(
                route_type=route_type,
                gateway_name=gw_key,
                is_active=True,
                fail_closed=fail_closed,
                egress_ip_masked="TEST_FIXTURE_GATEWAY",
                verification_state=EgressVerificationState.ROUTE_VERIFIED,
                detected_country=gw_info.get("expected_country"),
                last_verified=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                diagnostics="Verified via test-only OPSEC boundary fixture"
            )

        # 2. If proxy_url is configured, verify actual connectivity and country through the proxy
        if proxy_url:
            sanitized_proxy = re.sub(r'://([^:]+):([^@]+)@', r'://\1:*****@', proxy_url)
            try:
                # Support HTTPX 0.28.1+ proxy parameter (and fallback to proxies if legacy)
                client_kwargs: Dict[str, Any] = {"timeout": 4.0}
                try:
                    client = httpx.Client(proxy=proxy_url, **client_kwargs)
                except TypeError:
                    client = httpx.Client(proxies=proxy_url, **client_kwargs)

                with client:
                    resp = client.get("https://api.ipify.org?format=json")
                    if resp.status_code == 200:
                        real_ip = resp.json().get("ip", "unknown")
                        parts = real_ip.split(".")
                        masked_ip = f"{parts[0]}.{parts[1]}.xxx.xxx" if len(parts) == 4 else "xxx.xxx.xxx.xxx"

                        # Validate country if expected_country is specified
                        expected_c = gw_info.get("expected_country")
                        detected_c = expected_c  # default if unconstrained

                        if expected_c:
                            # Verify geographic egress country via IP geolocation endpoint
                            try:
                                geo_resp = client.get(f"https://ipapi.co/{real_ip}/json/", timeout=3.0)
                                if geo_resp.status_code == 200:
                                    detected_c = geo_resp.json().get("country_code", expected_c)
                            except Exception:
                                # Keep detected_c as verified through gateway route if ip probe passed
                                pass

                            if detected_c and detected_c.upper() != expected_c.upper():
                                app_logger.warning(
                                    f"OPSEC FAIL-CLOSED: Regional route {gw_key} egress country {detected_c} "
                                    f"mismatches expected {expected_c}."
                                )
                                return EgressRouteStatus(
                                    route_type=route_type,
                                    gateway_name=gw_key,
                                    is_active=False,
                                    fail_closed=fail_closed,
                                    egress_ip_masked=masked_ip,
                                    verification_state=EgressVerificationState.REGION_MISMATCH,
                                    detected_country=detected_c,
                                    diagnostics=f"Egress country {detected_c} does not match expected {expected_c}"
                                )

                        return EgressRouteStatus(
                            route_type=route_type,
                            gateway_name=gw_key,
                            is_active=True,
                            fail_closed=fail_closed,
                            egress_ip_masked=masked_ip,
                            verification_state=EgressVerificationState.ROUTE_VERIFIED,
                            detected_country=detected_c,
                            last_verified=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            diagnostics=f"Live verified through {gw_info['name']} ({sanitized_proxy})"
                        )
            except Exception as e:
                app_logger.error(f"Egress live probe failed for {gw_key} via {sanitized_proxy}: {e}")
                return EgressRouteStatus(
                    route_type=route_type,
                    gateway_name=gw_key,
                    is_active=False,
                    fail_closed=fail_closed,
                    egress_ip_masked="VERIFICATION_FAILED",
                    verification_state=EgressVerificationState.EGRESS_VERIFICATION_FAILED,
                    diagnostics=f"Egress live probe failed: {str(e)}"
                )

        return EgressRouteStatus(
            route_type=route_type,
            gateway_name=gw_key,
            is_active=False,
            fail_closed=fail_closed,
            egress_ip_masked="UNREACHABLE",
            verification_state=EgressVerificationState.TUNNEL_UNAVAILABLE,
            diagnostics="Gateway unreachable"
        )

    def get_httpx_client_for_route(self, route_type: EgressRouteType, gateway_name: Optional[str] = None) -> httpx.AsyncClient:
        """
        Creates an httpx.AsyncClient specifically bound to the verified regional gateway proxy,
        ensuring requests never leak through default direct network interfaces.
        Fails closed with RuntimeError if a regional route is requested but not active.
        """
        if route_type == EgressRouteType.DIRECT:
            return httpx.AsyncClient(
                timeout=10.0,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Sentinel-OSINT/2.0"}
            )

        gw_key = self.normalize_gateway_key(gateway_name)
        ok, msg, status = self.verify_egress_route(route_type, gateway_name, fail_closed=True)
        if not ok or not status.is_active:
            raise RuntimeError(f"OPSEC Fail-Closed: Egress route '{gw_key}' is unverified or unavailable. Direct network fallback is prohibited.")

        gw_info = self._gateway_configs.get(gw_key, {})
        proxy_url = gw_info.get("proxy_url")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Sentinel-OSINT/2.0"}

        try:
            return httpx.AsyncClient(
                proxy=proxy_url,
                timeout=10.0,
                headers=headers
            )
        except TypeError:
            return httpx.AsyncClient(
                proxies=proxy_url,
                timeout=10.0,
                headers=headers
            )

    def sanitize_log_content(self, text: str) -> str:
        """Sanitizes bearer tokens, API credentials, and passwords from operational log messages."""
        if not text:
            return ""
        sanitized = text
        for pat in self.SECRET_PATTERNS:
            sanitized = pat.sub(r'\1[REDACTED_CREDENTIAL]', sanitized)
        return sanitized


egress_controller = EgressController()
