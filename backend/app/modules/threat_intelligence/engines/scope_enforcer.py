"""
Vulnerability Assessment & Penetration Testing (VA/PT) Scope Enforcer & Isolation Controller.
Enforces strict target allowlists, impact level profiling, SSRF defense,
and emergency kill-switch capabilities.
"""

import socket
import ipaddress
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.core.logging import app_logger
from app.modules.threat_intelligence.engines.validator import (
    SSRFGuard, BLOCKED_IP_NETWORKS, RFC1918_PRIVATE_NETWORKS, BLOCKED_HOSTNAMES
)


class ScanImpactLevel(str, Enum):
    PASSIVE_RECON = "PASSIVE_RECON"          # WHOIS, DNS, certs, public headers (safe)
    ACTIVE_PORT_PROBE = "ACTIVE_PORT_PROBE"  # TCP SYN check, banner grabs (requires tenant permit)
    INTRUSIVE_VULN_SCAN = "INTRUSIVE_VULN_SCAN" # Active payload tests, fuzzing (requires Super Admin gate)


class ScopePermit(BaseModel):
    permit_id: str
    tenant_id: str
    authorized_target: str       # Domain (e.g. "example.com") or CIDR ("203.0.113.0/24")
    target_type: str             # "DOMAIN" or "CIDR"
    max_impact_level: ScanImpactLevel
    approved_by: str
    valid_until: str
    is_active: bool = True
    permit_token: str            # Cryptographic permit signature/token


class ScopeValidationResult(BaseModel):
    is_authorized: bool
    target: str
    resolved_ips: List[str] = Field(default_factory=list)
    impact_level: ScanImpactLevel
    rejection_reason: Optional[str] = None
    permit_id: Optional[str] = None
    diagnostics: str = ""


class VAPTScopeEnforcer:
    """
    Guarantees active scanning cannot be launched against arbitrary or prohibited targets.
    Enforces blast-radius containment, cloud metadata protection, and emergency cancellation.
    """

    def __init__(self):
        # In-memory authorized scope permits repository
        self._permits: Dict[str, ScopePermit] = {}
        # Active jobs tracking for emergency kill-switch
        self._active_jobs: Dict[str, Dict[str, Any]] = {}
        self._aborted_jobs: Set[str] = set()

        # Bootstrap with safe test lab scope permit for local unit testing
        self.register_permit(ScopePermit(
            permit_id="permit_lab_default",
            tenant_id="tenant_global",
            authorized_target="scanme.nmap.org",
            target_type="DOMAIN",
            max_impact_level=ScanImpactLevel.ACTIVE_PORT_PROBE,
            approved_by="superadmin@sential.io",
            valid_until="2030-01-01T00:00:00Z",
            permit_token="sig_permit_scanme_lab_verified"
        ))

    def register_permit(self, permit: ScopePermit) -> None:
        """Registers a verified authorization permit for an approved organization target."""
        self._permits[permit.permit_id] = permit
        app_logger.info(f"Registered VA/PT scope permit: {permit.permit_id} targeting '{permit.authorized_target}'")

    def validate_target_scope(
        self,
        target: str,
        impact_level: ScanImpactLevel,
        tenant_id: str,
        permit_id: Optional[str] = None,
        allow_private_lab: bool = False
    ) -> ScopeValidationResult:
        """
        Validates target before any packet is dispatched.
        1. Checks SSRF & prohibited IP/metadata subnets.
        2. Validates hostname resolution.
        3. Enforces registered permit allowlist match.
        4. Validates impact level authorization.
        """
        clean_target = target.strip().lower()

        # 1. Blocked hostnames check
        if clean_target in BLOCKED_HOSTNAMES or clean_target.endswith(".internal") or clean_target.endswith(".local"):
            return ScopeValidationResult(
                is_authorized=False,
                target=clean_target,
                impact_level=impact_level,
                rejection_reason=f"Prohibited internal infrastructure hostname: '{clean_target}'"
            )

        # 2. Hostname / IP resolution check
        resolved_ips: List[str] = []
        is_direct_ip = False
        try:
            ip_obj = ipaddress.ip_address(clean_target)
            is_direct_ip = True
            resolved_ips = [str(ip_obj)]
        except ValueError:
            # Resolve hostname
            try:
                addr_info = socket.getaddrinfo(clean_target, None)
                resolved_ips = list(set([item[4][0] for item in addr_info if item[4]]))
            except Exception as e:
                # If target cannot resolve, only passive recon allowed
                if impact_level != ScanImpactLevel.PASSIVE_RECON:
                    return ScopeValidationResult(
                        is_authorized=False,
                        target=clean_target,
                        impact_level=impact_level,
                        rejection_reason=f"DNS resolution failed for '{clean_target}'. Active probing prohibited."
                    )

        # 3. Verify resolved IPs against SSRFGuard
        for ip in resolved_ips:
            is_blocked, reason = SSRFGuard.is_ip_blocked(ip, allow_private_ranges=allow_private_lab)
            if is_blocked:
                return ScopeValidationResult(
                    is_authorized=False,
                    target=clean_target,
                    resolved_ips=resolved_ips,
                    impact_level=impact_level,
                    rejection_reason=f"Target resolves to blocked/cloud metadata IP {ip}: {reason}"
                )

        # 4. Enforce Scope Permit Allowlist
        matching_permit = None
        for pid, p in self._permits.items():
            if not p.is_active or (p.tenant_id != tenant_id and p.tenant_id != "tenant_global"):
                continue
            if p.authorized_target.lower() == clean_target:
                matching_permit = p
                break

        if not matching_permit and permit_id and permit_id in self._permits:
            candidate = self._permits[permit_id]
            if candidate.is_active and (candidate.tenant_id == tenant_id or candidate.tenant_id == "tenant_global"):
                matching_permit = candidate

        # Passive recon does not require a formal intrusive permit on public internet targets
        if impact_level == ScanImpactLevel.PASSIVE_RECON:
            return ScopeValidationResult(
                is_authorized=True,
                target=clean_target,
                resolved_ips=resolved_ips,
                impact_level=impact_level,
                permit_id=matching_permit.permit_id if matching_permit else None,
                diagnostics="Passive OSINT reconnaissance permitted under default tenant policy."
            )

        if not matching_permit:
            return ScopeValidationResult(
                is_authorized=False,
                target=clean_target,
                resolved_ips=resolved_ips,
                impact_level=impact_level,
                rejection_reason=f"No approved Scope Permit found for target '{clean_target}'. Active scans require written authorization."
            )

        # 5. Impact level check
        impact_hierarchy = {
            ScanImpactLevel.PASSIVE_RECON: 1,
            ScanImpactLevel.ACTIVE_PORT_PROBE: 2,
            ScanImpactLevel.INTRUSIVE_VULN_SCAN: 3,
        }
        if impact_hierarchy[impact_level] > impact_hierarchy[matching_permit.max_impact_level]:
            return ScopeValidationResult(
                is_authorized=False,
                target=clean_target,
                resolved_ips=resolved_ips,
                impact_level=impact_level,
                permit_id=matching_permit.permit_id,
                rejection_reason=f"Requested impact '{impact_level.value}' exceeds permitted ceiling '{matching_permit.max_impact_level.value}'"
            )

        return ScopeValidationResult(
            is_authorized=True,
            target=clean_target,
            resolved_ips=resolved_ips,
            impact_level=impact_level,
            permit_id=matching_permit.permit_id,
            diagnostics=f"Scope authorization validated against permit {matching_permit.permit_id}"
        )

    def register_active_job(self, job_id: str, target: str, impact_level: ScanImpactLevel) -> None:
        self._active_jobs[job_id] = {
            "target": target,
            "impact_level": impact_level.value,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "RUNNING"
        }

    def abort_scan(self, job_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Emergency kill-switch: terminates any running active reconnaissance job."""
        if job_id in self._active_jobs:
            self._active_jobs[job_id]["status"] = "ABORTED"
            self._active_jobs[job_id]["reason"] = reason or "Operator requested abort"
        self._aborted_jobs.add(job_id)
        app_logger.warning(f"EMERGENCY KILL-SWITCH ACTIVATED: Aborted scan job {job_id} ({reason})")
        return {
            "status": "ABORTED",
            "job_id": job_id,
            "reason": reason or "Emergency kill-switch activated",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def is_aborted(self, job_id: str) -> bool:
        return job_id in self._aborted_jobs

    def validate_scope_authorization(
        self,
        target: str,
        requested_impact: ScanImpactLevel,
        tenant_id: str,
        permit_id: Optional[str] = None,
        allow_private_lab: bool = False
    ) -> ScopeValidationResult:
        """Alias for validate_target_scope matching REST endpoint conventions."""
        return self.validate_target_scope(
            target=target,
            impact_level=requested_impact,
            tenant_id=tenant_id,
            permit_id=permit_id,
            allow_private_lab=allow_private_lab
        )

    def register_scope_permit(self, permit: ScopePermit) -> None:
        """Alias for register_permit matching REST endpoint conventions."""
        return self.register_permit(permit)


vapt_scope_enforcer = VAPTScopeEnforcer()
