import re
import ipaddress
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

class TargetClassifier:
    """
    Universal, high-precision search target and intent classifier for investigative workflows.
    Classifies queries deterministically into actionable intelligence categories:
    PHONE, EMAIL, PERSON, ORGANIZATION, USERNAME, VEHICLE_PLATE, SOCIAL_MEDIA_URL,
    IMAGE, VIDEO, DOMAIN, IP, NEWS_ARTICLE, LOCATION, IOC, GENERAL_RESEARCH, UNKNOWN, AMBIGUOUS.
    Never silently defaults unknown or ambiguous queries to domain, phone, person, or keyword.
    """

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,20}$")
    DOMAIN_REGEX = re.compile(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")
    URL_REGEX = re.compile(r"^https?://[^\s]+$")
    MD5_REGEX = re.compile(r"^[a-fA-F0-9]{32}$")
    SHA1_REGEX = re.compile(r"^[a-fA-F0-9]{40}$")
    SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")
    CVE_REGEX = re.compile(r"^CVE-\d{4}-\d{4,8}$", re.IGNORECASE)
    COORDINATES_REGEX = re.compile(
        r"^\s*[-+]?([1-8]?\d(?:\.\d+)?|90(?:\.0+)?),\s*[-+]?(180(?:\.0+)?|(?:1[0-7]\d|\d{1,2})(?:\.\d+)?)\s*$"
    )
    VEHICLE_PLATE_REGEX = re.compile(
        r"^(?:[A-Z]{2}\s?[0-9]{1,2}\s?[A-Z]{0,3}\s?[0-9]{4}|[A-Z]{2}[0-9]{2}\s?[A-Z]{3}|[1-9A-Z]{1}[A-Z0-9]{4,6}|[A-Z]{1,3}\s?[A-Z]{1,2}\s?[0-9]{1,4})$",
        re.IGNORECASE
    )

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg", ".tiff"}
    VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".flv", ".m4v"}

    SOCIAL_DOMAINS = {
        "twitter.com", "x.com", "instagram.com", "youtube.com", "youtu.be",
        "reddit.com", "bsky.app", "t.me", "telegram.me", "facebook.com", "fb.com",
        "fb.watch", "tiktok.com", "linkedin.com", "mastodon.social", "threads.net"
    }

    NEWS_DOMAINS = {
        "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "cnn.com", "thehindu.com",
        "aljazeera.com", "bloomberg.com", "nytimes.com", "wsj.com", "theguardian.com",
        "timesofindia.indiatimes.com", "ndtv.com", "hindustantimes.com", "lemonde.fr",
        "spiegel.de", "kyivindependent.com", "japantimes.co.jp", "scmp.com"
    }

    EVENT_KEYWORDS = {
        "vs", "versus", "conflict", "war", "strike", "attack", "protest", "summit",
        "election", "treaty", "border", "clash", "tensions", "crisis", "deal", "talks",
        "sanctions", "ceasefire", "resolution", "investigation", "scandal", "leak",
        "explosion", "coup", "riot", "dispute", "alliance", "invasion"
    }

    GEOPOLITICAL_ENTITIES = {
        "india", "china", "usa", "us", "uk", "russia", "ukraine", "israel", "iran",
        "palestine", "taiwan", "japan", "germany", "france", "pakistan", "nato",
        "un", "eu", "brics", "asean", "middle east", "indo-pacific", "south china sea",
        "kyiv", "moscow", "beijing", "taipei", "washington", "london", "paris", "berlin",
        "tokyo", "new delhi", "chennai", "mumbai", "jerusalem", "tehran", "riyadh"
    }

    ORGANIZATION_INDICATORS = {
        "inc", "corp", "corporation", "llc", "ltd", "limited", "gmbh", "pvt", "private",
        "foundation", "group", "holdings", "agency", "interpol", "isro", "nasa", "bhel",
        "ongc", "tcs", "infosys", "reliance", "alphabet", "microsoft", "google", "apple",
        "amazon", "meta", "openai", "lockheed", "boeing", "raytheon", "unicef", "who"
    }

    PERSON_HONORIFICS = {
        "mr", "mrs", "ms", "dr", "president", "pm", "minister", "general", "senator",
        "chancellor", "governor", "judge", "director", "officer", "secretary"
    }

    @classmethod
    def classify(cls, query: str) -> str:
        """
        Determines the canonical target type string.
        Returns: phone, email, person, organization, username, vehicle, social_url,
        image, video, domain, subdomain, ip, cidr, article, location, hash, keyword, or unknown.
        """
        intent_info = cls.classify_intent(query)
        if intent_info.get("target_type"):
            return intent_info["target_type"]
        intent = intent_info.get("intent", "UNKNOWN")
        
        mapping = {
            "PHONE": "phone",
            "EMAIL": "email",
            "PERSON": "person",
            "ORGANIZATION": "organization",
            "USERNAME": "username",
            "VEHICLE_PLATE": "vehicle",
            "SOCIAL_MEDIA_URL": "social_url",
            "IMAGE": "image",
            "VIDEO": "video",
            "DOMAIN": "domain",
            "SUBDOMAIN": "subdomain",
            "IP": "ip",
            "INFRASTRUCTURE": "cidr" if "/" in query else "ip",
            "NEWS_ARTICLE": "article",
            "NEWS_TOPIC": "keyword",
            "EVENT": "keyword",
            "LOCATION": "location",
            "IOC": "hash",
            "GENERAL_RESEARCH": "keyword",
            "UNKNOWN": "unknown",
            "AMBIGUOUS": "unknown"
        }
        return mapping.get(intent, "unknown")

    @classmethod
    def classify_intent(cls, query: str) -> Dict[str, Any]:
        """
        Universal intent & classification engine for investigative targets.
        Preserves original, normalized value, source context, and honest categorization.
        """
        q = query.strip()
        if not q:
            return {
                "intent": "UNKNOWN",
                "category": "UNCLASSIFIED",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": True,
                "target_type": "unknown",
                "explanation": "Empty input string provided.",
                "clarification_guidance": "Please provide an investigator target such as a phone number, email, name, username, plate, URL, domain, IP, or location.",
                "recommended_scopes": [],
                "applicable_modules": []
            }

        q_lower = q.lower()
        tokens = [t.strip(",.:;!?") for t in q_lower.split() if t.strip(",.:;!?")]

        # =========================================================================
        # 0. Check Explicit Prefix Overrides (e.g. "phone:...", "plate:...", "image:...")
        # =========================================================================
        prefix_map = {
            "phone:": ("PHONE", "IDENTITY", "phone", ["osint"], ["PEOPLE & IDENTITIES", "OSINT"]),
            "tel:": ("PHONE", "IDENTITY", "phone", ["osint"], ["PEOPLE & IDENTITIES", "OSINT"]),
            "email:": ("EMAIL", "IDENTITY", "email", ["osint"], ["PEOPLE & IDENTITIES", "OSINT"]),
            "mailto:": ("EMAIL", "IDENTITY", "email", ["osint"], ["PEOPLE & IDENTITIES", "OSINT"]),
            "plate:": ("VEHICLE_PLATE", "ASSET", "vehicle", ["osint"], ["OSINT"]),
            "registration:": ("VEHICLE_PLATE", "ASSET", "vehicle", ["osint"], ["OSINT"]),
            "vehicle:": ("VEHICLE_PLATE", "ASSET", "vehicle", ["osint"], ["OSINT"]),
            "geo:": ("LOCATION", "GEOPOLITICAL_GEO", "location", ["geo_intelligence", "news_intelligence", "osint"], ["GEO INTELLIGENCE", "NEWS INTELLIGENCE", "OSINT"]),
            "location:": ("LOCATION", "GEOPOLITICAL_GEO", "location", ["geo_intelligence", "news_intelligence", "osint"], ["GEO INTELLIGENCE", "NEWS INTELLIGENCE", "OSINT"]),
            "coords:": ("LOCATION", "GEOPOLITICAL_GEO", "location", ["geo_intelligence", "news_intelligence", "osint"], ["GEO INTELLIGENCE", "NEWS INTELLIGENCE", "OSINT"]),
            "image:": ("IMAGE", "MEDIA", "image", ["osint", "social_media_intelligence"], ["OSINT", "MEDIA"]),
            "img:": ("IMAGE", "MEDIA", "image", ["osint", "social_media_intelligence"], ["OSINT", "MEDIA"]),
            "video:": ("VIDEO", "MEDIA", "video", ["social_media_intelligence", "news_intelligence", "osint"], ["MEDIA", "SOCIAL MEDIA INTELLIGENCE", "NEWS INTELLIGENCE"]),
            "vid:": ("VIDEO", "MEDIA", "video", ["social_media_intelligence", "news_intelligence", "osint"], ["MEDIA", "SOCIAL MEDIA INTELLIGENCE", "NEWS INTELLIGENCE"]),
            "article:": ("NEWS_ARTICLE", "NEWS", "article", ["news_intelligence", "osint"], ["NEWS INTELLIGENCE", "OSINT"]),
            "news:": ("NEWS_ARTICLE", "NEWS", "article", ["news_intelligence", "osint"], ["NEWS INTELLIGENCE", "OSINT"]),
            "user:": ("USERNAME", "IDENTITY", "username", ["osint", "social_media_intelligence"], ["PEOPLE & IDENTITIES", "OSINT", "SOCIAL MEDIA INTELLIGENCE"]),
            "username:": ("USERNAME", "IDENTITY", "username", ["osint", "social_media_intelligence"], ["PEOPLE & IDENTITIES", "OSINT", "SOCIAL MEDIA INTELLIGENCE"]),
            "person:": ("PERSON", "IDENTITY", "person", ["news_intelligence", "osint", "social_media_intelligence"], ["PEOPLE & IDENTITIES", "NEWS INTELLIGENCE", "OSINT"]),
            "name:": ("PERSON", "IDENTITY", "person", ["news_intelligence", "osint", "social_media_intelligence"], ["PEOPLE & IDENTITIES", "NEWS INTELLIGENCE", "OSINT"]),
            "org:": ("ORGANIZATION", "IDENTITY", "organization", ["osint", "news_intelligence", "threat_intelligence"], ["OSINT", "NEWS INTELLIGENCE", "THREAT INTELLIGENCE"]),
            "company:": ("ORGANIZATION", "IDENTITY", "organization", ["osint", "news_intelligence", "threat_intelligence"], ["OSINT", "NEWS INTELLIGENCE", "THREAT INTELLIGENCE"]),
            "domain:": ("DOMAIN", "INFRASTRUCTURE", "domain", ["threat_intelligence", "osint"], ["DIGITAL INFRASTRUCTURE", "OSINT", "THREAT INTELLIGENCE"]),
            "ip:": ("IP", "INFRASTRUCTURE", "ip", ["threat_intelligence", "osint"], ["DIGITAL INFRASTRUCTURE", "THREAT INTELLIGENCE"]),
            "cve:": ("IOC", "IOC", "hash", ["threat_intelligence"], ["THREAT INTELLIGENCE", "EVIDENCE"]),
            "hash:": ("IOC", "IOC", "hash", ["threat_intelligence"], ["THREAT INTELLIGENCE", "EVIDENCE"]),
        }

        for pfx, (intent, cat, ttype, mods, scopes) in prefix_map.items():
            if q_lower.startswith(pfx):
                clean_val = q[len(pfx):].strip()
                return {
                    "intent": intent,
                    "category": cat,
                    "target_type": ttype,
                    "is_technical_target": cat in ["INFRASTRUCTURE", "IOC"],
                    "is_unknown_or_ambiguous": False,
                    "normalized_value": clean_val,
                    "explanation": f"Explicit '{pfx.rstrip(':')}' prefix target identified: '{clean_val}'.",
                    "recommended_scopes": scopes,
                    "applicable_modules": mods
                }

        # =========================================================================
        # 1. Check GPS Coordinates (e.g. "13.0827, 80.2707" or "37.7749, -122.4194")
        # =========================================================================
        if cls.COORDINATES_REGEX.match(q):
            return {
                "intent": "LOCATION",
                "category": "GEOPOLITICAL_GEO",
                "target_type": "location",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": False,
                "explanation": f"Geographic GPS coordinate pair identified ({q}). Routing to geospatial timeline, boundary mapping, and regional incident correlation.",
                "recommended_scopes": ["GEO INTELLIGENCE", "NEWS INTELLIGENCE", "OSINT"],
                "applicable_modules": ["geo_intelligence", "news_intelligence", "osint"]
            }

        # =========================================================================
        # 2. Check URLs (Social, Image, Video, News Article, or Generic Web URL)
        # =========================================================================
        if cls.URL_REGEX.match(q):
            try:
                parsed = urlparse(q)
                netloc = parsed.netloc.lower()
                path = parsed.path.lower()
                clean_host = netloc.split(":")[0].lstrip("www.")

                # Check if it is a Video URL
                is_video_platform = any(clean_host == vp or clean_host.endswith(f".{vp}") for vp in ["youtube.com", "youtu.be", "vimeo.com", "dailymotion.com"])
                if is_video_platform or any(path.endswith(ext) for ext in cls.VIDEO_EXTENSIONS) or "/watch" in path or "/video/" in path or "watch" in path:
                    return {
                        "intent": "VIDEO",
                        "category": "MEDIA",
                        "target_type": "video",
                        "is_technical_target": False,
                        "is_unknown_or_ambiguous": False,
                        "explanation": f"Direct video media target ({clean_host}). Routing to video forensics, channel metadata, and audio/narrative extraction.",
                        "recommended_scopes": ["MEDIA", "SOCIAL MEDIA INTELLIGENCE", "NEWS INTELLIGENCE"],
                        "applicable_modules": ["social_media_intelligence", "news_intelligence", "osint"]
                    }

                # Check if it is an Image URL
                if any(path.endswith(ext) for ext in cls.IMAGE_EXTENSIONS):
                    return {
                        "intent": "IMAGE",
                        "category": "MEDIA",
                        "target_type": "image",
                        "is_technical_target": False,
                        "is_unknown_or_ambiguous": False,
                        "explanation": f"Direct image media target ({path.split('/')[-1]}). Routing to EXIF metadata inspection and visual intelligence.",
                        "recommended_scopes": ["OSINT", "MEDIA", "SOCIAL MEDIA INTELLIGENCE"],
                        "applicable_modules": ["osint", "social_media_intelligence"]
                    }

                # Check if it is a Social Media URL
                if any(clean_host == sd or clean_host.endswith(f".{sd}") for sd in cls.SOCIAL_DOMAINS if sd not in ["youtube.com", "youtu.be"]):
                    return {
                        "intent": "SOCIAL_MEDIA_URL",
                        "category": "SOCIAL_MEDIA",
                        "target_type": "social_url",
                        "is_technical_target": False,
                        "is_unknown_or_ambiguous": False,
                        "explanation": f"Direct social media URL target ({clean_host}). Routing to platform collector, author attribution, and post forensics.",
                        "recommended_scopes": ["SOCIAL MEDIA INTELLIGENCE", "OSINT", "MEDIA"],
                        "applicable_modules": ["social_media_intelligence", "osint"]
                    }

                # Check if it is a News Article URL
                if any(clean_host == nd or clean_host.endswith(f".{nd}") for nd in cls.NEWS_DOMAINS) or any(seg in path for seg in ["/news/", "/article/", "/world/", "/story/"]):
                    return {
                        "intent": "NEWS_ARTICLE",
                        "category": "NEWS",
                        "target_type": "article",
                        "is_technical_target": False,
                        "is_unknown_or_ambiguous": False,
                        "explanation": f"News reporting article URL ({clean_host}). Routing to claim extraction, publisher lineage, and event timeline.",
                        "recommended_scopes": ["NEWS INTELLIGENCE", "OSINT"],
                        "applicable_modules": ["news_intelligence", "osint"]
                    }

                # Generic Web URL Endpoint
                return {
                    "intent": "URL",
                    "category": "INFRASTRUCTURE",
                    "target_type": "url",
                    "is_technical_target": True,
                    "is_unknown_or_ambiguous": False,
                    "explanation": f"Web URL endpoint identified ({clean_host}). Routing to web reconnaissance and digital infrastructure analysis.",
                    "recommended_scopes": ["DIGITAL INFRASTRUCTURE", "OSINT", "THREAT INTELLIGENCE"],
                    "applicable_modules": ["osint", "threat_intelligence", "news_intelligence"]
                }
            except Exception:
                pass

        # =========================================================================
        # 3. Check IP Address and CIDR
        # =========================================================================
        try:
            ipaddress.ip_address(q)
            return {
                "intent": "IP",
                "category": "INFRASTRUCTURE",
                "target_type": "ip",
                "is_technical_target": True,
                "is_unknown_or_ambiguous": False,
                "explanation": "Direct IP address target. Activating infrastructure discovery, ASN geolocation, and threat telemetry.",
                "recommended_scopes": ["DIGITAL INFRASTRUCTURE", "THREAT INTELLIGENCE", "GEO INTELLIGENCE"],
                "applicable_modules": ["threat_intelligence", "osint"]
            }
        except ValueError:
            pass

        try:
            if "/" in q:
                ipaddress.ip_network(q, strict=False)
                return {
                    "intent": "INFRASTRUCTURE",
                    "category": "INFRASTRUCTURE",
                    "target_type": "ip",
                    "is_technical_target": True,
                    "is_unknown_or_ambiguous": False,
                    "explanation": "Network CIDR subnet block. Routing to ASN mapping and route analysis.",
                    "recommended_scopes": ["DIGITAL INFRASTRUCTURE", "THREAT INTELLIGENCE"],
                    "applicable_modules": ["threat_intelligence", "osint"]
                }
        except ValueError:
            pass

        # =========================================================================
        # 4. Check RFC Email Address
        # =========================================================================
        if cls.EMAIL_REGEX.match(q):
            return {
                "intent": "EMAIL",
                "category": "IDENTITY",
                "target_type": "email",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": False,
                "explanation": "Email identity identifier. Routing to breach databases, OSINT registries, and footprint correlation.",
                "recommended_scopes": ["PEOPLE & IDENTITIES", "OSINT"],
                "applicable_modules": ["osint"]
            }

        # =========================================================================
        # 5. Check Hashes / CVE / IOC
        # =========================================================================
        if cls.SHA256_REGEX.match(q) or cls.SHA1_REGEX.match(q) or cls.MD5_REGEX.match(q) or cls.CVE_REGEX.match(q):
            return {
                "intent": "IOC",
                "category": "IOC",
                "target_type": "hash",
                "is_technical_target": True,
                "is_unknown_or_ambiguous": False,
                "explanation": "Cryptographic file hash or CVE identifier. Routing to threat intelligence feeds and malware repositories.",
                "recommended_scopes": ["THREAT INTELLIGENCE", "EVIDENCE"],
                "applicable_modules": ["threat_intelligence"]
            }

        # =========================================================================
        # 6. Check Phone Number (Digit count >= 8, only telecom symbols)
        # =========================================================================
        if cls.PHONE_REGEX.match(q) and any(c.isdigit() for c in q) and len(re.sub(r"\D", "", q)) >= 8 and not any(c.isalpha() for c in q):
            return {
                "intent": "PHONE",
                "category": "IDENTITY",
                "target_type": "phone",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": False,
                "explanation": "Telecommunications number target. Routing to carrier registry and identity attribution.",
                "recommended_scopes": ["PEOPLE & IDENTITIES", "OSINT"],
                "applicable_modules": ["osint"]
            }

        # =========================================================================
        # 7. Check Vehicle Registration Plate (e.g. TN34MA8562, DL01AB1234, BD51 SMR)
        # =========================================================================
        clean_plate = re.sub(r"[\s\-_]", "", q.upper())
        if cls.VEHICLE_PLATE_REGEX.match(q) and any(c.isdigit() for c in clean_plate) and any(c.isalpha() for c in clean_plate) and len(clean_plate) <= 12:
            return {
                "intent": "VEHICLE_PLATE",
                "category": "ASSET",
                "target_type": "vehicle",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": False,
                "explanation": f"Vehicle registration number plate ({clean_plate}). Routing to vehicle intelligence and lawful registry verification.",
                "recommended_scopes": ["OSINT"],
                "applicable_modules": ["osint"]
            }

        # =========================================================================
        # 8. Check Domain / Subdomain (Single token, valid TLD)
        # =========================================================================
        if " " not in q and cls.DOMAIN_REGEX.match(q):
            parts = q.split(".")
            is_sub = len(parts) > 2 and parts[-2] not in ["co", "com", "org", "gov", "edu", "net"]
            return {
                "intent": "DOMAIN",
                "category": "INFRASTRUCTURE",
                "target_type": "subdomain" if is_sub else "domain",
                "is_technical_target": True,
                "is_unknown_or_ambiguous": False,
                "explanation": "Fully Qualified Domain Name (FQDN). Routing to DNS reconnaissance, SSL transparency, and host auditing.",
                "recommended_scopes": ["DIGITAL INFRASTRUCTURE", "OSINT", "THREAT INTELLIGENCE"],
                "applicable_modules": ["threat_intelligence", "osint", "news_intelligence"]
            }

        # =========================================================================
        # 9. Check Image File Path / Reference (e.g. "evidence/photo.jpg", "suspect.png")
        # =========================================================================
        if any(q_lower.endswith(ext) for ext in cls.IMAGE_EXTENSIONS):
            return {
                "intent": "IMAGE",
                "category": "MEDIA",
                "target_type": "image",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": False,
                "explanation": f"Image file target ({q}). Routing to EXIF metadata inspection and visual intelligence.",
                "recommended_scopes": ["OSINT", "MEDIA", "SOCIAL MEDIA INTELLIGENCE"],
                "applicable_modules": ["osint", "social_media_intelligence"]
            }

        # =========================================================================
        # 10. Check Video File Path / Reference (e.g. "footage.mp4", "cctv.webm")
        # =========================================================================
        if any(q_lower.endswith(ext) for ext in cls.VIDEO_EXTENSIONS):
            return {
                "intent": "VIDEO",
                "category": "MEDIA",
                "target_type": "video",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": False,
                "explanation": f"Video file target ({q}). Routing to video forensics and transcript correlation.",
                "recommended_scopes": ["MEDIA", "SOCIAL MEDIA INTELLIGENCE", "NEWS INTELLIGENCE"],
                "applicable_modules": ["social_media_intelligence", "news_intelligence", "osint"]
            }

        # =========================================================================
        # 11. Check Username Handle (@handle or single alphanumeric token)
        # =========================================================================
        if q.startswith("@") or (len(tokens) == 1 and not cls.DOMAIN_REGEX.match(q) and 3 <= len(q) <= 32 and q.isalnum() and q_lower not in cls.GEOPOLITICAL_ENTITIES and q_lower not in cls.ORGANIZATION_INDICATORS):
            clean_user = q.lstrip("@")
            return {
                "intent": "USERNAME",
                "category": "IDENTITY",
                "target_type": "username",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": False,
                "explanation": f"Social or platform username handle (@{clean_user}). Routing to public account profiling, social media intelligence, and footprint tracking.",
                "recommended_scopes": ["PEOPLE & IDENTITIES", "OSINT", "SOCIAL MEDIA INTELLIGENCE"],
                "applicable_modules": ["osint", "social_media_intelligence"]
            }

        # =========================================================================
        # 12. Check Unknown / Ambiguous Input (Punctuation soup, random symbols, invalid nonce)
        # =========================================================================
        # If the input contains purely non-alphanumeric punctuation or illegal characters
        alphanumeric_chars = sum(1 for c in q if c.isalnum())
        if alphanumeric_chars == 0 or (len(q) >= 4 and alphanumeric_chars <= 1 and not q.startswith("@")):
            return {
                "intent": "UNKNOWN",
                "category": "UNCLASSIFIED",
                "target_type": "unknown",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": True,
                "explanation": f"Input '{q}' contains only punctuation, non-alphanumeric symbols, or unparseable syntax.",
                "clarification_guidance": f"The query '{q}' could not be deterministically parsed into a valid intelligence target. Please specify a phone number, email, name, username, plate, URL, domain, IP, or location.",
                "recommended_scopes": [],
                "applicable_modules": []
            }

        # Check random ambiguous strings with zero semantic meaning (e.g. "?!~@#invalid-gibberish")
        has_symbol_soup = bool(re.search(r"[!@#$%^&*()_+=~`{}\[\]|\\:;\"'<>,?/]{3,}", q))
        if has_symbol_soup and not cls.URL_REGEX.match(q):
            return {
                "intent": "AMBIGUOUS",
                "category": "UNCLASSIFIED",
                "target_type": "unknown",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": True,
                "explanation": f"Input '{q}' contains ambiguous or contradictory syntax sequences.",
                "clarification_guidance": f"The query '{q}' contains mixed ambiguous symbols. Please clarify your intended target format.",
                "recommended_scopes": [],
                "applicable_modules": []
            }

        # =========================================================================
        # 13. Geopolitical, News & Event Queries ("India vs China", "Israel Iran conflict", etc.)
        # =========================================================================
        has_event_keyword = any(kw in tokens for kw in cls.EVENT_KEYWORDS)
        has_geopolitical_entity = any(geo in q_lower for geo in cls.GEOPOLITICAL_ENTITIES)
        has_vs_comparison = any(v in tokens for v in ["vs", "versus", "against", "and"])

        if (has_vs_comparison and len(tokens) >= 2) or (has_geopolitical_entity and has_event_keyword):
            return {
                "intent": "NEWS_TOPIC",
                "category": "GEOPOLITICAL_NEWS",
                "target_type": "keyword",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": False,
                "explanation": "Geopolitical event & multi-entity news topic. Port/network scanning disabled; routing to global news discovery, source lineage, and narrative verification.",
                "recommended_scopes": ["NEWS INTELLIGENCE", "OSINT", "SOCIAL MEDIA INTELLIGENCE", "GEO INTELLIGENCE", "MEDIA"],
                "applicable_modules": ["news_intelligence", "osint", "social_media_intelligence"]
            }

        if has_event_keyword:
            return {
                "intent": "EVENT",
                "category": "GEOPOLITICAL_NEWS",
                "target_type": "keyword",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": False,
                "explanation": "Event occurrence inquiry. Routing to temporal timelines, media verification, social narrative dispatches, and claim extraction.",
                "recommended_scopes": ["NEWS INTELLIGENCE", "OSINT", "SOCIAL MEDIA INTELLIGENCE", "GEO INTELLIGENCE", "MEDIA", "EVIDENCE"],
                "applicable_modules": ["news_intelligence", "osint", "social_media_intelligence"]
            }

        if has_geopolitical_entity and not any(kw in tokens for kw in cls.ORGANIZATION_INDICATORS):
            return {
                "intent": "LOCATION",
                "category": "GEOPOLITICAL_NEWS",
                "target_type": "location",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": False,
                "explanation": f"Geographic / nation-state intelligence target ({q}). Routing to geospatial context, regional news feeds, and entity intelligence.",
                "recommended_scopes": ["NEWS INTELLIGENCE", "GEO INTELLIGENCE", "OSINT", "SOCIAL MEDIA INTELLIGENCE"],
                "applicable_modules": ["geo_intelligence", "news_intelligence", "osint"]
            }

        # =========================================================================
        # 14. Check Organization Names (e.g. "Google LLC", "OpenAI Inc", "ISRO")
        # =========================================================================
        has_org_indicator = any(kw in tokens for kw in cls.ORGANIZATION_INDICATORS)
        if has_org_indicator or (len(tokens) in (1, 2) and q_lower in cls.ORGANIZATION_INDICATORS):
            return {
                "intent": "ORGANIZATION",
                "category": "IDENTITY",
                "target_type": "organization",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": False,
                "explanation": f"Corporate or institutional named entity ({q}). Routing to regulatory corporate filings (SEC EDGAR, GLEIF LEI), sanctions compliance, and news correlation.",
                "recommended_scopes": ["OSINT", "NEWS INTELLIGENCE", "THREAT INTELLIGENCE"],
                "applicable_modules": ["osint", "news_intelligence", "threat_intelligence"]
            }

        # =========================================================================
        # 15. Check Person Names (e.g. "Narendra Modi", "Joe Biden", "Dr. Jane Smith")
        # =========================================================================
        has_honorific = any(h in tokens for h in cls.PERSON_HONORIFICS)
        if has_honorific or (len(tokens) in (2, 3) and all(t.isalpha() for t in tokens) and not has_event_keyword and not has_org_indicator):
            return {
                "intent": "PERSON",
                "category": "IDENTITY",
                "target_type": "person",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": False,
                "explanation": f"Individual named entity inquiry ({q}). Routing to biographical intelligence, public profiles, media quotes, and public records.",
                "recommended_scopes": ["PEOPLE & IDENTITIES", "NEWS INTELLIGENCE", "OSINT", "SOCIAL MEDIA INTELLIGENCE"],
                "applicable_modules": ["news_intelligence", "osint", "social_media_intelligence"]
            }

        # =========================================================================
        # 16. General Research default for Multi-Word Inquiries
        # =========================================================================
        if len(tokens) >= 2:
            return {
                "intent": "GENERAL_RESEARCH",
                "category": "RESEARCH",
                "target_type": "keyword",
                "is_technical_target": False,
                "is_unknown_or_ambiguous": False,
                "explanation": f"General multi-word investigative query ({q}). Synthesizing across open sources, news intelligence, and social media dispatches.",
                "recommended_scopes": ["ALL INTELLIGENCE", "NEWS INTELLIGENCE", "OSINT", "SOCIAL MEDIA INTELLIGENCE"],
                "applicable_modules": ["news_intelligence", "osint", "social_media_intelligence"]
            }

        # Single word that matches no dictionary or pattern
        return {
            "intent": "UNKNOWN",
            "category": "UNCLASSIFIED",
            "target_type": "unknown",
            "is_technical_target": False,
            "is_unknown_or_ambiguous": True,
            "explanation": f"Single token '{q}' is ambiguous and does not match any recognized identifier, handle, or dictionary keyword.",
            "clarification_guidance": f"The token '{q}' is ambiguous. Please clarify if this is a username (e.g. '@{q}'), a domain, or provide additional context.",
            "recommended_scopes": [],
            "applicable_modules": []
        }

target_classifier = TargetClassifier()
