"""
Operational Security (OPSEC) Network Egress Controller.
Enforces strict zero-trust outbound routing, fail-closed isolation,
and credential sanitization for investigative workloads.
Adheres to NIST SP 800-207 Zero Trust Architecture.
"""

import os
import re
from enum import Enum
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

from app.core.logging import app_logger


class EgressRouteType(str, Enum):
    DIRECT = "DIRECT"
    REGIONAL_GATEWAY_APPROVED = "REGIONAL_GATEWAY_APPROVED"
    ISOLATED_SCANNER = "ISOLATED_SCANNER"


class EgressRouteStatus(BaseModel):
    route_type: EgressRouteType
    gateway_name: str
    is_active: bool
    fail_closed: bool = True
    egress_ip_masked: str
    last_verified: Optional[str] = None
    diagnostics: str = "Route healthy"


class EgressController:
    """
    Central OPSEC egress controller ensuring that investigations requiring specific
    regional or isolated network egress never accidentally leak through direct local network interfaces.
    """

    # Sensitive token masking regex patterns
    SECRET_PATTERNS = [
        re.compile(r'(?i)(bearer\s+)[a-zA-Z0-9_\-\.]{20,}'),
        re.compile(r'(?i)(api[_-]?key["\']?\s*[:=]\s*["\']?)[a-zA-Z0-9_\-]{16,}'),
        re.compile(r'(?i)(password["\']?\s*[:=]\s*["\']?)[^"\'\s]{8,}'),
        re.compile(r'(?i)(proxy[_-]?auth["\']?\s*[:=]\s*["\']?)[^"\'\s]{8,}'),
    ]

    def __init__(self):
        # Configured regional gateway endpoints (simulated or environment-injected)
        self._gateways: Dict[str, Dict[str, Any]] = {
            "south_asia_gateway": {
                "active": os.getenv("GATEWAY_SOUTH_ASIA_ACTIVE", "true").lower() == "true",
                "ip_masked": "103.xxx.xxx.42",
                "region": "South Asia"
            },
            "international_gateway": {
                "active": os.getenv("GATEWAY_INTERNATIONAL_ACTIVE", "true").lower() == "true",
                "ip_masked": "198.xxx.xxx.89",
                "region": "International"
            },
            "isolated_scanner_gateway": {
                "active": os.getenv("GATEWAY_SCANNER_ACTIVE", "true").lower() == "true",
                "ip_masked": "185.xxx.xxx.12",
                "region": "Isolated Scanner Net"
            }
        }

    def verify_egress_route(
        self,
        route_type: EgressRouteType,
        gateway_name: Optional[str] = None,
        fail_closed: bool = True
    ) -> Tuple[bool, str, EgressRouteStatus]:
        """
        Verifies that the requested egress route is operational.
        Enforces Fail-Closed: If an approved regional gateway is requested but inactive,
        the request is blocked immediately to prevent direct network deanonymization.
        """
        if route_type == EgressRouteType.DIRECT:
            return True, "Direct outbound connection authorized", EgressRouteStatus(
                route_type=route_type,
                gateway_name="local_default",
                is_active=True,
                fail_closed=False,
                egress_ip_masked="local_direct",
                diagnostics="Direct egress permitted for general non-sensitive retrieval"
            )

        gw_key = (gateway_name or "south_asia_gateway").lower()
        gw_info = self._gateways.get(gw_key)

        if not gw_info or not gw_info.get("active"):
            msg = f"Approved regional gateway '{gw_key}' is unavailable or inactive."
            if fail_closed:
                app_logger.warning(f"OPSEC FAIL-CLOSED: Blocked outbound dispatch. {msg}")
                return False, f"OPSEC_FAIL_CLOSED: {msg} Direct network fallback is prohibited.", EgressRouteStatus(
                    route_type=route_type,
                    gateway_name=gw_key,
                    is_active=False,
                    fail_closed=True,
                    egress_ip_masked="UNREACHABLE",
                    diagnostics="Halted by OPSEC fail-closed policy"
                )
            else:
                return True, "Permitted with warning (fail-open enabled)", EgressRouteStatus(
                    route_type=route_type,
                    gateway_name=gw_key,
                    is_active=False,
                    fail_closed=False,
                    egress_ip_masked="FALLBACK_DIRECT",
                    diagnostics="Operating in degraded fallback mode"
                )

        return True, "Approved regional egress route verified", EgressRouteStatus(
            route_type=route_type,
            gateway_name=gw_key,
            is_active=True,
            fail_closed=fail_closed,
            egress_ip_masked=gw_info.get("ip_masked", "masked_gateway_ip"),
            diagnostics="Route verified; investigator identity decoupled from target interaction"
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
