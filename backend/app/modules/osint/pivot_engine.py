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

        # 0. Direct Identifier Component Pivots (e.g. Email -> Domain, Email -> Username handle)
        clean_orig = original_query.split(":", 1)[-1].strip()
        if ("@" in clean_orig and not clean_orig.startswith("@")) or actual_target_type == "email":
            if "@" in clean_orig:
                parts = clean_orig.split("@", 1)
                u_part, d_part = parts[0].strip(), parts[1].strip()
                if d_part and d_part.lower() not in seen_queries and "." in d_part:
                    pivots.append(
                        PivotCandidate(
                            pivot_id=f"pvt_emldom_{hashlib.md5(d_part.encode()).hexdigest()[:8]}",
                            pivot_query=d_part,
                            pivot_target_type="DOMAIN",
                            pivot_type="infrastructure_osint",
                            target_modules=["threat_intelligence", "osint"],
                            relationship="USES_DOMAIN",
                            parent_entity_value=clean_orig,
                            parent_entity_type="EMAIL",
                            confidence=0.95,
                            recommended_action=f"Perform DNS, WHOIS, and infrastructure reconnaissance on email domain '{d_part}'.",
                            why_it_matters=f"Email identifier '{clean_orig}' is hosted on domain infrastructure '{d_part}'.",
                            sources=["Email Normalization"]
                        )
                    )
                    seen_queries.add(d_part.lower())
                if u_part and u_part.lower() not in seen_queries and len(u_part) >= 3:
                    pivots.append(
                        PivotCandidate(
                            pivot_id=f"pvt_emlusr_{hashlib.md5(u_part.encode()).hexdigest()[:8]}",
                            pivot_query=u_part,
                            pivot_target_type="USERNAME",
                            pivot_type="social_recon",
                            target_modules=["social_media_intelligence", "osint"],
                            relationship="USES_HANDLE",
                            parent_entity_value=clean_orig,
                            parent_entity_type="EMAIL",
                            confidence=0.8,
                            recommended_action=f"Check username alias '{u_part}' across social networks and public repositories.",
                            why_it_matters=f"Username '{u_part}' extracted from local part of email '{clean_orig}'.",
                            sources=["Email Normalization"]
                        )
                    )
                    seen_queries.add(u_part.lower())

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

            # 8. Location / Jurisdiction Pivot -> Geospatial Intelligence & Regional News
            elif e_type in ["location", "geo", "jurisdiction", "place", "city", "country"] and val_lower != original_query.lower() and len(val) >= 2:
                pivots.append(
                    PivotCandidate(
                        pivot_id=f"pvt_{hashlib.md5(val.encode()).hexdigest()[:8]}",
                        pivot_query=val,
                        pivot_target_type="LOCATION",
                        pivot_type="geospatial_intelligence",
                        target_modules=["geo_intelligence", "news_intelligence"],
                        relationship="RESOLVES_TO" if str(parent_type).upper() in ["PHONE", "IP", "VEHICLE"] else "LOCATED_AT",
                        parent_entity_value=parent_val,
                        parent_entity_type=parent_type,
                        confidence=confidence,
                        recommended_action=f"Correlate geographic observations, boundaries, and regional news in '{val}'.",
                        why_it_matters="Identifies spatial presence, regional incident reports, and jurisdictional boundaries.",
                        sources=sources or ["Geographic Intelligence"]
                    )
                )
                seen_queries.add(val_lower)

            # 9. Vehicle Registration Plate Pivot -> RTO Jurisdiction & Location
            elif e_type in ["vehicle", "vehicle_plate"]:
                jurisdiction = meta.get("jurisdiction") or meta.get("region")
                if jurisdiction and jurisdiction.lower() not in seen_queries and len(jurisdiction) >= 3:
                    pivots.append(
                        PivotCandidate(
                            pivot_id=f"pvt_vjur_{hashlib.md5(jurisdiction.encode()).hexdigest()[:8]}",
                            pivot_query=jurisdiction,
                            pivot_target_type="LOCATION",
                            pivot_type="geospatial_intelligence",
                            target_modules=["geo_intelligence", "news_intelligence"],
                            relationship="REGISTERED_IN_JURISDICTION",
                            parent_entity_value=val,
                            parent_entity_type="VEHICLE",
                            confidence=0.9,
                            recommended_action=f"Inspect regional transport authority records and local news in jurisdiction '{jurisdiction}'.",
                            why_it_matters=f"Vehicle '{val}' is attributed to regional transport authority jurisdiction '{jurisdiction}'.",
                            sources=sources or ["Vehicle Registration Recon"]
                        )
                    )
                    seen_queries.add(jurisdiction.lower())

            # 10. Social Media URL / Post Pivot -> Author Handle & Content Forensics
            elif e_type in ["social_url", "post", "social_post"]:
                author = meta.get("author") or meta.get("author_id")
                if author and str(author).strip().lower() not in seen_queries and len(str(author).strip()) >= 3:
                    clean_author = str(author).strip().lstrip("@")
                    pivots.append(
                        PivotCandidate(
                            pivot_id=f"pvt_auth_{hashlib.md5(clean_author.encode()).hexdigest()[:8]}",
                            pivot_query=clean_author,
                            pivot_target_type="USERNAME",
                            pivot_type="handle_reconnaissance",
                            target_modules=["social_media_intelligence", "osint"],
                            relationship="AUTHORED",
                            parent_entity_value=val,
                            parent_entity_type="POST",
                            confidence=0.9,
                            recommended_action=f"Investigate author profile and account footprint for handle '@{clean_author}'.",
                            why_it_matters=f"Discovered author handle of social media dispatch '{val}'.",
                            sources=sources or ["Social Media Intelligence"]
                        )
                    )
                    seen_queries.add(clean_author.lower())

            # 11. Image / Video / Media Pivot -> Channel / Author or Cryptographic Hash
            elif e_type in ["image", "video", "media"]:
                channel = meta.get("channel") or meta.get("author")
                if channel and str(channel).strip().lower() not in seen_queries and len(str(channel).strip()) >= 3:
                    clean_chan = str(channel).strip()
                    pivots.append(
                        PivotCandidate(
                            pivot_id=f"pvt_chan_{hashlib.md5(clean_chan.encode()).hexdigest()[:8]}",
                            pivot_query=clean_chan,
                            pivot_target_type="PERSON",
                            pivot_type="person_reconnaissance",
                            target_modules=["social_media_intelligence", "news_intelligence", "osint"],
                            relationship="VIDEO_PUBLISHED_BY_CHANNEL" if e_type == "video" else "AUTHORED",
                            parent_entity_value=val,
                            parent_entity_type="MEDIA",
                            confidence=0.85,
                            recommended_action=f"Correlate creator / channel intelligence for '{clean_chan}'.",
                            why_it_matters=f"Media asset '{val}' is published or authored by '{clean_chan}'.",
                            sources=sources or ["Media Extraction"]
                        )
                    )
                    seen_queries.add(clean_chan.lower())

            # 12. News Article Pivot -> Publisher / Outlet Intelligence
            elif e_type in ["article", "news"]:
                publisher = meta.get("publisher")
                if publisher and str(publisher).strip().lower() not in seen_queries and len(str(publisher).strip()) >= 3:
                    clean_pub = str(publisher).strip()
                    pivots.append(
                        PivotCandidate(
                            pivot_id=f"pvt_pub_{hashlib.md5(clean_pub.encode()).hexdigest()[:8]}",
                            pivot_query=clean_pub,
                            pivot_target_type="ORGANIZATION",
                            pivot_type="corporate_intelligence",
                            target_modules=["news_intelligence", "osint"],
                            relationship="PUBLISHED",
                            parent_entity_value=val,
                            parent_entity_type="ARTICLE",
                            confidence=0.85,
                            recommended_action=f"Examine editorial coverage and source independence for publisher '{clean_pub}'.",
                            why_it_matters=f"Article reporting '{val}' originates from publisher outlet '{clean_pub}'.",
                            sources=sources or ["News Intelligence"]
                        )
                    )
                    seen_queries.add(clean_pub.lower())

        # Sort by confidence descending and limit
        pivots.sort(key=lambda p: p.confidence, reverse=True)
        return [p.dict() for p in pivots[:max_pivots]]


pivot_engine = PivotDiscoveryEngine()
query_pivot_engine = pivot_engine
