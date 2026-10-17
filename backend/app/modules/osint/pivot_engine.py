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
                meta = ent.get("metadata", {}) or {}
            else:
                val = str(getattr(ent, "value", "")).strip()
                raw_type = getattr(ent, "type", "")
                confidence = float(getattr(ent, "confidence", 1.0))
                sources = getattr(ent, "sources", [])
                meta = getattr(ent, "metadata", {}) or {}

            val_lower = val.lower()
            e_type = str(raw_type.value if hasattr(raw_type, "value") else raw_type).lower()

            # Skip self-queries or empty except when extracting sub-components from identifiers (e.g. domain/username from email)
            is_self_query = (val_lower in seen_queries)
            if not val or (is_self_query and e_type not in ["email", "contact_email"]):
                continue

            # Provenance: Determine the actual parent entity that introduced this candidate
            parent_val = meta.get("parent_entity") or original_query
            parent_type = meta.get("parent_entity_type") or actual_target_type.upper()

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
                            target_modules=["threat_intelligence", "osint"],
                            relationship="HOSTED_ON_IP",
                            parent_entity_value=parent_val,
                            parent_entity_type=parent_type,
                            confidence=confidence,
                            recommended_action=f"Execute Reverse DNS, ASN routing lookup, and Shodan banner scan on {val}.",
                            why_it_matters="Discover co-hosted virtual hosts, adjacent infrastructure, and cloud provider tenancy.",
                            sources=sources or ["DNS Resolution"]
                        )
                    )
                    seen_queries.add(val_lower)
                except ValueError:
                    pass

            # 2. Subdomain / Hostname / Domain Pivot -> Passive Threat Intel & Certificate Transparency
            elif e_type in ["subdomain", "domain", "hostname"] and val_lower != original_query.lower():
                pivots.append(
                    PivotCandidate(
                        pivot_id=f"pvt_{hashlib.md5(val.encode()).hexdigest()[:8]}",
                        pivot_query=val,
                        pivot_target_type="DOMAIN",
                        pivot_type="passive_domain_recon",
                        target_modules=["threat_intelligence", "osint"],
                        relationship="SUBDOMAIN_OF" if e_type == "subdomain" else "CONNECTED_TO",
                        parent_entity_value=parent_val,
                        parent_entity_type=parent_type,
                        confidence=confidence,
                        recommended_action=f"Inspect passive DNS, TLS certificate transparency, and WHOIS history for {val}.",
                        why_it_matters="Discloses technical attack surface, associated staging hosts, and domain registration indicators.",
                        sources=sources or ["Certificate Transparency"]
                    )
                )
                seen_queries.add(val_lower)

            # 3. Email Pivot -> Domain Infrastructure, Persona Handle & Identity Footprint
            elif e_type in ["email", "contact_email"]:
                if re.match(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$", val):
                    parts = val.split('@')
                    user_part, domain_part = parts[0].strip(), parts[1].strip()

                    # Domain component pivot
                    common_providers = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com", "icloud.com"}
                    if domain_part.lower() not in seen_queries and domain_part.lower() not in common_providers:
                        pivots.append(
                            PivotCandidate(
                                pivot_id=f"pvt_dom_{hashlib.md5(domain_part.encode()).hexdigest()[:8]}",
                                pivot_query=domain_part,
                                pivot_target_type="DOMAIN",
                                pivot_type="passive_domain_recon",
                                target_modules=["threat_intelligence", "osint"],
                                relationship="CONNECTED_TO",
                                parent_entity_value=val,
                                parent_entity_type="EMAIL",
                                confidence=confidence,
                                recommended_action=f"Inspect passive DNS and corporate web infrastructure for domain '{domain_part}'.",
                                why_it_matters=f"Reveals host infrastructure and enterprise ownership associated with {val}.",
                                sources=sources or ["Email Attribution"]
                            )
                        )
                        seen_queries.add(domain_part.lower())

                    # Username / persona handle component pivot
                    if len(user_part) >= 3 and user_part.lower() not in seen_queries:
                        pivots.append(
                            PivotCandidate(
                                pivot_id=f"pvt_usr_{hashlib.md5(user_part.encode()).hexdigest()[:8]}",
                                pivot_query=user_part,
                                pivot_target_type="USERNAME",
                                pivot_type="handle_reconnaissance",
                                target_modules=["social_media_intelligence", "osint"],
                                relationship="ALIASED_AS",
                                parent_entity_value=val,
                                parent_entity_type="EMAIL",
                                confidence=confidence * 0.9,
                                recommended_action=f"Investigate social media profiles and repositories for handle '{user_part}'.",
                                why_it_matters=f"Investigators frequently identify matching personas using the email username '{user_part}'.",
                                sources=sources or ["Email Attribution"]
                            )
                        )
                        seen_queries.add(user_part.lower())

                    # Direct email footprint (breach disclosure) if not self-query
                    if not is_self_query and val_lower not in seen_queries:
                        pivots.append(
                            PivotCandidate(
                                pivot_id=f"pvt_{hashlib.md5(val.encode()).hexdigest()[:8]}",
                                pivot_query=val,
                                pivot_target_type="EMAIL",
                                pivot_type="identity_footprint",
                                target_modules=["osint", "social_media_intelligence"],
                                relationship="REGISTERED_BY_EMAIL",
                                parent_entity_value=parent_val,
                                parent_entity_type=parent_type,
                                confidence=confidence,
                                recommended_action=f"Search public repository commits and breach disclosures for {val}.",
                                why_it_matters="Discloses associated persona handles, sysadmin accounts, and credential compromise exposures.",
                                sources=sources or ["WHOIS Data"]
                            )
                        )
                        seen_queries.add(val_lower)

            # 4. Username / Handle Pivot -> Cross-Platform Social Reconnaissance
            elif e_type in ["username", "handle", "account"]:
                clean_handle = val.split('@')[0].lstrip('@').strip()
                if 3 <= len(clean_handle) <= 32 and ' ' not in clean_handle and clean_handle.lower() != original_query.lower():
                    pivots.append(
                        PivotCandidate(
                            pivot_id=f"pvt_{hashlib.md5(clean_handle.encode()).hexdigest()[:8]}",
                            pivot_query=clean_handle,
                            pivot_target_type="USERNAME",
                            pivot_type="handle_reconnaissance",
                            target_modules=["social_media_intelligence", "osint"],
                            relationship="ALIASED_AS",
                            parent_entity_value=parent_val,
                            parent_entity_type=parent_type,
                            confidence=confidence,
                            recommended_action=f"Execute multi-platform profile reconnaissance on handle '{clean_handle}'.",
                            why_it_matters="Persons of interest routinely reuse handles across social platforms, development repos, and public forums.",
                            sources=sources or ["Social Media Intelligence"]
                        )
                    )
                    seen_queries.add(clean_handle.lower())

            # 5. Person / Name Pivot -> Social Media & News Intelligence Follow-up
            elif e_type in ["person", "name"] and val_lower != original_query.lower() and len(val) >= 3:
                pivots.append(
                    PivotCandidate(
                        pivot_id=f"pvt_{hashlib.md5(val.encode()).hexdigest()[:8]}",
                        pivot_query=val,
                        pivot_target_type="PERSON",
                        pivot_type="person_reconnaissance",
                        target_modules=["social_media_intelligence", "news_intelligence", "osint"],
                        relationship="ASSOCIATED_WITH",
                        parent_entity_value=parent_val,
                        parent_entity_type=parent_type,
                        confidence=confidence,
                        recommended_action=f"Cross-reference public profiles and recent reporting for '{val}'.",
                        why_it_matters="Corroborates individual associations, biographical presence, and reported statements.",
                        sources=sources or ["Identity Recon"]
                    )
                )
                seen_queries.add(val_lower)

            # 6. Organization Pivot -> News & Institutional Correlation
            elif e_type in ["organization", "company"] and val_lower != original_query.lower() and len(val) >= 3:
                pivots.append(
                    PivotCandidate(
                        pivot_id=f"pvt_{hashlib.md5(val.encode()).hexdigest()[:8]}",
                        pivot_query=val,
                        pivot_target_type="ORGANIZATION",
                        pivot_type="corporate_intelligence",
                        target_modules=["osint", "news_intelligence", "threat_intelligence"],
                        relationship="AFFILIATED_WITH",
                        parent_entity_value=parent_val,
                        parent_entity_type=parent_type,
                        confidence=confidence,
                        recommended_action=f"Audit corporate filings, subsidiaries, and news coverage for '{val}'.",
                        why_it_matters="Discloses corporate hierarchies, registered agents, and institutional relationships.",
                        sources=sources or ["Corporate Registry"]
                    )
                )
                seen_queries.add(val_lower)

            # 7. CVE / Vulnerability Pivot -> Threat Actor Association
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
                        parent_entity_value=parent_val,
                        parent_entity_type=parent_type,
                        confidence=1.0,
                        recommended_action=f"Check CISA KEV and FIRST EPSS exploit probability for {cve_val}.",
                        why_it_matters="Identifies if the exposed flaw is actively exploited in the wild.",
                        sources=sources or ["Vulnerability Scan"]
                    )
                )
                seen_queries.add(cve_val.lower())

        # Sort by confidence descending and limit
        pivots.sort(key=lambda p: p.confidence, reverse=True)
        return [p.dict() for p in pivots[:max_pivots]]


pivot_engine = PivotDiscoveryEngine()
query_pivot_engine = pivot_engine
