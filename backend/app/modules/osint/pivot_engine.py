"""
Multi-Stage Query Pivoting & Discovery Traceability Engine (OSINT-01).
Extracts high-confidence secondary pivot targets from correlated intelligence entities
with verifiable provenance, parent-child link tracking, and deduplication.
"""

import hashlib
import ipaddress
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.module_sdk.models import EntityPayload, EntityType


class PivotCandidate(BaseModel):
    pivot_id: str
    pivot_query: str
    pivot_target_type: str
    pivot_type: Optional[str] = None
    target_modules: List[str] = Field(default_factory=list)
    relationship: str
    parent_entity_value: str
    parent_entity_type: str
    confidence: float
    recommended_action: str
    why_it_matters: str
    sources: List[str] = Field(default_factory=list)


class PivotDiscoveryEngine:
    """Automated entity-pivot generator for deep multi-hop reconnaissance."""

    @classmethod
    def generate_pivots(
        cls,
        original_query: str,
        arg2: Any = "domain",
        entities: Optional[List[Any]] = None,
        target_type: Optional[str] = None,
        max_pivots: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        if isinstance(arg2, (list, tuple, set)):
            actual_entities = list(arg2)
            actual_target_type = target_type or "domain"
        else:
            actual_target_type = str(arg2)
            actual_entities = entities or kwargs.get("entities") or []

        pivots: List[PivotCandidate] = []
        seen_queries = {original_query.strip().lower()}

        for ent in actual_entities:
            # Handle both EntityPayload/object and dict
            if isinstance(ent, dict):
                val = str(ent.get("value", "")).strip()
                raw_type = ent.get("type", "")
                confidence = float(ent.get("confidence", 1.0))
                sources = ent.get("sources", [])
            else:
                val = str(getattr(ent, "value", "")).strip()
                raw_type = getattr(ent, "type", "")
                confidence = float(getattr(ent, "confidence", 1.0))
                sources = getattr(ent, "sources", [])

            val_lower = val.lower()
            e_type = str(raw_type.value if hasattr(raw_type, "value") else raw_type).lower()

            # Skip self-queries or empty
            if not val or val_lower in seen_queries:
                continue

            # 1. IP Pivot -> Reverse DNS & Infrastructure Scan
            if e_type in ["ip", "ip_address", "ipv4", "ipv6"]:
                try:
                    ipaddress.ip_address(val)
                    pivots.append(
                        PivotCandidate(
                            pivot_id=f"pvt_{hashlib.md5(val.encode()).hexdigest()[:8]}",
                            pivot_query=val,
                            pivot_target_type="IP_ADDRESS",
                            pivot_type="ip_infrastructure",
                            target_modules=["osint", "threat_intelligence"],
                            relationship="HOSTED_ON_IP",
                            parent_entity_value=original_query,
                            parent_entity_type=actual_target_type.upper(),
                            confidence=confidence,
                            recommended_action=f"Execute Reverse DNS, ASN routing lookup, and Shodan banner scan on {val}.",
                            why_it_matters="Discover co-hosted virtual hosts, adjacent malicious infrastructure, and cloud provider tenancy.",
                            sources=sources or ["DNS Resolution"]
                        )
                    )
                    seen_queries.add(val_lower)
                except ValueError:
                    pass

            # 2. Subdomain / Hostname Pivot
            elif e_type in ["subdomain", "domain", "hostname"] and val_lower != original_query.lower():
                pivots.append(
                    PivotCandidate(
                        pivot_id=f"pvt_{hashlib.md5(val.encode()).hexdigest()[:8]}",
                        pivot_query=val,
                        pivot_target_type="DOMAIN",
                        pivot_type="subdomain_enumeration",
                        target_modules=["osint"],
                        relationship="SUBDOMAIN_OF",
                        parent_entity_value=original_query,
                        parent_entity_type=actual_target_type.upper(),
                        confidence=confidence,
                        recommended_action=f"Probe TLS certificate history, web technologies, and DNS zone on {val}.",
                        why_it_matters="Subdomains often expose staging, internal VPN endpoints, or outdated microservices with weaker security controls.",
                        sources=sources or ["Certificate Transparency"]
                    )
                )
                seen_queries.add(val_lower)

            # 3. Email Pivot -> Breaches, WHOIS & Identity Footprint
            elif e_type in ["email", "contact_email"]:
                if "@" in val and not val.endswith("@example.com"):
                    pivots.append(
                        PivotCandidate(
                            pivot_id=f"pvt_{hashlib.md5(val.encode()).hexdigest()[:8]}",
                            pivot_query=val,
                            pivot_target_type="EMAIL",
                            pivot_type="identity_footprint",
                            target_modules=["osint", "social_media_intelligence"],
                            relationship="REGISTERED_BY_EMAIL",
                            parent_entity_value=original_query,
                            parent_entity_type=actual_target_type.upper(),
                            confidence=confidence,
                            recommended_action=f"Search public repository commits, breach disclosures, and PGP keys for {val}.",
                            why_it_matters="Reveals employee identities, sysadmin accounts, and credential compromise exposures.",
                            sources=sources or ["WHOIS Data"]
                        )
                    )
                    seen_queries.add(val_lower)

            # 4. Username / Handle Pivot -> Cross-Platform Footprinting
            elif e_type in ["username", "handle", "account"]:
                clean_handle = val.lstrip('@')
                if len(clean_handle) >= 3:
                    pivots.append(
                        PivotCandidate(
                            pivot_id=f"pvt_{hashlib.md5(clean_handle.encode()).hexdigest()[:8]}",
                            pivot_query=clean_handle,
                            pivot_target_type="USERNAME",
                            pivot_type="handle_reconnaissance",
                            target_modules=["social_media_intelligence", "osint"],
                            relationship="ALIASED_AS",
                            parent_entity_value=original_query,
                            parent_entity_type=actual_target_type.upper(),
                            confidence=confidence,
                            recommended_action=f"Execute 300+ platform reconnaissance on handle '{clean_handle}'.",
                            why_it_matters="Adversaries and persons of interest routinely reuse aliases across social platforms, development repos, and darkweb forums.",
                            sources=sources or ["Social Media Intelligence"]
                        )
                    )
                    seen_queries.add(val_lower)

            # 5. CVE / Vulnerability Pivot -> Exploitability & Threat Actor Association
            elif e_type in ["vulnerability", "cve"]:
                cve_match = re.search(r'CVE-\d{4}-\d{4,7}', val, re.IGNORECASE)
                cve_val = cve_match.group(0).upper() if cve_match else val.upper()
                pivots.append(
                    PivotCandidate(
                        pivot_id=f"pvt_{hashlib.md5(cve_val.encode()).hexdigest()[:8]}",
                        pivot_query=cve_val,
                        pivot_target_type="VULNERABILITY",
                        pivot_type="vulnerability_intelligence",
                        target_modules=["threat_intelligence"],
                        relationship="HAS_VULNERABILITY",
                        parent_entity_value=original_query,
                        parent_entity_type=actual_target_type.upper(),
                        confidence=1.0,
                        recommended_action=f"Check CISA KEV and FIRST EPSS exploit probability for {cve_val}.",
                        why_it_matters="Identifies if the exposed flaw is actively exploited in the wild or weaponized in ransomware playbooks.",
                        sources=sources or ["Vulnerability Scan"]
                    )
                )
                seen_queries.add(cve_val.lower())

        # Sort by confidence descending and limit
        pivots.sort(key=lambda p: p.confidence, reverse=True)
        return [p.dict() for p in pivots[:max_pivots]]


pivot_engine = PivotDiscoveryEngine()
query_pivot_engine = pivot_engine
