import re
import ipaddress
from typing import Dict, Any, List

class TargetClassifier:
    """
    High-precision search target and intent classifier for investigative workflows.
    Classifies queries into actionable intelligence categories, distinguishes technical
    infrastructure targets from geopolitical events/persons/organizations, and prevents
    inappropriate tool execution (e.g. port scanning general text queries).
    """

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,20}$")
    DOMAIN_REGEX = re.compile(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")
    URL_REGEX = re.compile(r"^https?://[^\s]+$")
    MD5_REGEX = re.compile(r"^[a-fA-F0-9]{32}$")
    SHA1_REGEX = re.compile(r"^[a-fA-F0-9]{40}$")
    SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")
    CVE_REGEX = re.compile(r"^CVE-\d{4}-\d{4,8}$", re.IGNORECASE)

    # Known geopolitical, news & event keyword triggers
    EVENT_KEYWORDS = {
        "vs", "versus", "conflict", "war", "strike", "attack", "protest", "summit",
        "election", "treaty", "border", "clash", "tensions", "crisis", "deal", "talks",
        "sanctions", "ceasefire", "resolution", "investigation", "scandal", "leak",
        "explosion", "coup", "riot", "treaty", "dispute", "alliance", "invasion"
    }

    GEOPOLITICAL_ENTITIES = {
        "india", "china", "usa", "us", "uk", "russia", "ukraine", "israel", "iran",
        "palestine", "taiwan", "japan", "germany", "france", "pakistan", "nato",
        "un", "eu", "brics", "asean", "middle east", "indo-pacific", "south china sea"
    }

    PERSON_HONORIFICS = {"mr", "mrs", "ms", "dr", "president", "pm", "minister", "general", "senator", "chancellor"}

    @classmethod
    def classify(cls, query: str) -> str:
        """Legacy target type detection for backwards compatibility."""
        q = query.strip()
        if not q:
            return "unknown"

        # Check URL
        if cls.URL_REGEX.match(q):
            return "url"

        # Check IP address
        try:
            ipaddress.ip_address(q)
            return "ip"
        except ValueError:
            pass

        # Check CIDR
        try:
            ipaddress.ip_network(q, strict=False)
            if "/" in q:
                return "cidr"
        except ValueError:
            pass

        # Check Email
        if cls.EMAIL_REGEX.match(q):
            return "email"

        # Check Hashes / IOC
        if cls.SHA256_REGEX.match(q) or cls.SHA1_REGEX.match(q) or cls.MD5_REGEX.match(q) or cls.CVE_REGEX.match(q):
            return "hash"

        # Check Phone
        if cls.PHONE_REGEX.match(q) and any(c.isdigit() for c in q) and len(re.sub(r"\D", "", q)) >= 8:
            return "phone"

        # Check Domain / Subdomain (strictly requiring non-space and proper TLD)
        if " " not in q and cls.DOMAIN_REGEX.match(q):
            parts = q.split(".")
            if len(parts) > 2 and parts[-2] not in ["co", "com", "org", "gov", "edu", "net"]:
                return "subdomain"
            return "domain"

        # If it has spaces, it is an investigative keyword or multi-entity query
        if " " in q:
            return "keyword"

        # Check username handle (@username)
        if q.startswith("@") or (len(q) >= 3 and q.isalnum()):
            return "username"

        return "keyword"

    @classmethod
    def classify_intent(cls, query: str) -> Dict[str, Any]:
        """
        Classifies query intent into investigator-centric intelligence categories:
        PERSON, ORGANIZATION, DOMAIN, IP, EMAIL, USERNAME, LOCATION, EVENT,
        NEWS_TOPIC, IOC, INFRASTRUCTURE, GENERAL_RESEARCH, MULTI_ENTITY_QUERY.
        """
        q = query.strip()
        q_lower = q.lower()
        tokens = [t.strip(",.:;!?") for t in q_lower.split() if t.strip(",.:;!?")]

        # 1. Check URL
        if cls.URL_REGEX.match(q):
            return {
                "intent": "URL",
                "category": "INFRASTRUCTURE",
                "is_technical_target": True,
                "explanation": "Web URL endpoint identified. Routing to web reconnaissance and digital infrastructure analysis.",
                "recommended_scopes": ["DIGITAL INFRASTRUCTURE", "OSINT", "THREAT INTELLIGENCE"],
                "applicable_modules": ["osint", "threat_intelligence", "news_intelligence"]
            }

        # 2. Check IP Address
        try:
            ipaddress.ip_address(q)
            return {
                "intent": "IP",
                "category": "INFRASTRUCTURE",
                "is_technical_target": True,
                "explanation": "Direct IP address target. Activating infrastructure discovery, ASN geolocation, and threat telemetry.",
                "recommended_scopes": ["DIGITAL INFRASTRUCTURE", "THREAT INTELLIGENCE", "GEO INTELLIGENCE"],
                "applicable_modules": ["threat_intelligence", "osint"]
            }
        except ValueError:
            pass

        # 3. Check CIDR block
        try:
            if "/" in q:
                ipaddress.ip_network(q, strict=False)
                return {
                    "intent": "INFRASTRUCTURE",
                    "category": "INFRASTRUCTURE",
                    "is_technical_target": True,
                    "explanation": "Network CIDR subnet block. Routing to ASN mapping and route analysis.",
                    "recommended_scopes": ["DIGITAL INFRASTRUCTURE", "THREAT INTELLIGENCE"],
                    "applicable_modules": ["threat_intelligence", "osint"]
                }
        except ValueError:
            pass

        # 4. Check Email
        if cls.EMAIL_REGEX.match(q):
            return {
                "intent": "EMAIL",
                "category": "IDENTITY",
                "is_technical_target": False,
                "explanation": "Email identity identifier. Routing to breach databases, OSINT registries, and footprint correlation.",
                "recommended_scopes": ["PEOPLE & IDENTITIES", "OSINT"],
                "applicable_modules": ["osint"]
            }

        # 5. Check Hashes / IOC
        if cls.SHA256_REGEX.match(q) or cls.SHA1_REGEX.match(q) or cls.MD5_REGEX.match(q) or cls.CVE_REGEX.match(q):
            return {
                "intent": "IOC",
                "category": "IOC",
                "is_technical_target": True,
                "explanation": "Cryptographic file hash or CVE identifier. Routing to threat intelligence feeds and malware repositories.",
                "recommended_scopes": ["THREAT INTELLIGENCE", "EVIDENCE"],
                "applicable_modules": ["threat_intelligence"]
            }

        # 6. Check Phone Number
        if cls.PHONE_REGEX.match(q) and any(c.isdigit() for c in q) and len(re.sub(r"\D", "", q)) >= 8 and not any(c.isalpha() for c in q):
            return {
                "intent": "PHONE",
                "category": "IDENTITY",
                "is_technical_target": False,
                "explanation": "Telecommunications number target. Routing to carrier registry and identity attribution.",
                "recommended_scopes": ["PEOPLE & IDENTITIES", "OSINT"],
                "applicable_modules": ["osint"]
            }

        # 7. Check Domain / Subdomain (Single token, valid domain format)
        if " " not in q and cls.DOMAIN_REGEX.match(q):
            return {
                "intent": "DOMAIN",
                "category": "INFRASTRUCTURE",
                "is_technical_target": True,
                "explanation": "Fully Qualified Domain Name (FQDN). Routing to DNS reconnaissance, SSL transparency, and host auditing.",
                "recommended_scopes": ["DIGITAL INFRASTRUCTURE", "OSINT", "THREAT INTELLIGENCE"],
                "applicable_modules": ["threat_intelligence", "osint", "news_intelligence"]
            }

        # 8. Check Username Handle (@handle)
        if q.startswith("@") or (len(tokens) == 1 and not cls.DOMAIN_REGEX.match(q) and len(q) >= 3 and q.isalnum() and q_lower not in cls.GEOPOLITICAL_ENTITIES):
            return {
                "intent": "USERNAME",
                "category": "IDENTITY",
                "is_technical_target": False,
                "explanation": "Social or platform username handle. Routing to public account profiling and footprint tracking.",
                "recommended_scopes": ["PEOPLE & IDENTITIES", "OSINT"],
                "applicable_modules": ["osint"]
            }

        # 9. Multi-Entity / Geopolitical / Event Queries ("India vs China", "Israel Iran conflict", etc.)
        has_event_keyword = any(kw in tokens for kw in cls.EVENT_KEYWORDS)
        has_geopolitical_entity = any(geo in q_lower for geo in cls.GEOPOLITICAL_ENTITIES)
        has_vs_comparison = any(v in tokens for v in ["vs", "versus", "against", "and"])

        if (has_vs_comparison and len(tokens) >= 2) or (has_geopolitical_entity and has_event_keyword):
            return {
                "intent": "NEWS_TOPIC",
                "category": "GEOPOLITICAL_NEWS",
                "is_technical_target": False,
                "explanation": "Geopolitical event & multi-entity news topic. Port/network scanning disabled; routing to global news discovery, source lineage, and narrative verification.",
                "recommended_scopes": ["NEWS INTELLIGENCE", "OSINT", "GEO INTELLIGENCE", "MEDIA"],
                "applicable_modules": ["news_intelligence", "osint"]
            }

        if has_event_keyword:
            return {
                "intent": "EVENT",
                "category": "GEOPOLITICAL_NEWS",
                "is_technical_target": False,
                "explanation": "Event occurrence inquiry. Routing to temporal timelines, media verification, and claim extraction.",
                "recommended_scopes": ["NEWS INTELLIGENCE", "GEO INTELLIGENCE", "MEDIA", "EVIDENCE"],
                "applicable_modules": ["news_intelligence", "osint"]
            }

        if has_geopolitical_entity:
            return {
                "intent": "LOCATION",
                "category": "GEOPOLITICAL_NEWS",
                "is_technical_target": False,
                "explanation": "Geographic / nation-state intelligence target. Routing to geospatial context, regional news feeds, and entity intelligence.",
                "recommended_scopes": ["NEWS INTELLIGENCE", "GEO INTELLIGENCE", "OSINT"],
                "applicable_modules": ["news_intelligence", "osint"]
            }

        # 10. Check Person Names (e.g. "Narendra Modi", "Joe Biden")
        if any(h in tokens for h in cls.PERSON_HONORIFICS) or (len(tokens) in (2, 3) and all(t.isalpha() for t in tokens) and not has_event_keyword):
            return {
                "intent": "PERSON",
                "category": "IDENTITY",
                "is_technical_target": False,
                "explanation": "Public or private individual named inquiry. Routing to biographical intelligence, media quotes, and public footprint.",
                "recommended_scopes": ["PEOPLE & IDENTITIES", "NEWS INTELLIGENCE", "OSINT"],
                "applicable_modules": ["news_intelligence", "osint"]
            }

        # 11. General Research default
        return {
            "intent": "GENERAL_RESEARCH",
            "category": "RESEARCH",
            "is_technical_target": False,
            "explanation": "General investigative research query. Synthesizing across open sources, news intelligence, and entity registries.",
            "recommended_scopes": ["ALL INTELLIGENCE", "NEWS INTELLIGENCE", "OSINT"],
            "applicable_modules": ["news_intelligence", "osint"]
        }

target_classifier = TargetClassifier()
