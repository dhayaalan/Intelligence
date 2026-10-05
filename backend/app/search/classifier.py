import re
import ipaddress

class TargetClassifier:
    """Classifies search target inputs automatically into structured intelligence entity types."""
    
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,20}$")
    DOMAIN_REGEX = re.compile(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")
    URL_REGEX = re.compile(r"^https?://[^\s]+$")
    MD5_REGEX = re.compile(r"^[a-fA-F0-9]{32}$")
    SHA1_REGEX = re.compile(r"^[a-fA-F0-9]{40}$")
    SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")

    @classmethod
    def classify(cls, query: str) -> str:
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
            
        # Check Hashes
        if cls.SHA256_REGEX.match(q) or cls.SHA1_REGEX.match(q) or cls.MD5_REGEX.match(q):
            return "hash"
            
        # Check Phone
        if cls.PHONE_REGEX.match(q) and any(c.isdigit() for c in q) and len(re.sub(r"\D", "", q)) >= 8:
            return "phone"
            
        # Check Domain / Subdomain
        if cls.DOMAIN_REGEX.match(q):
            parts = q.split(".")
            if len(parts) > 2 and parts[-2] not in ["co", "com", "org", "gov", "edu"]:
                return "subdomain"
            return "domain"
            
        # Default to Username or Keyword
        if " " not in q and len(q) >= 3:
            return "username"
            
        return "keyword"

target_classifier = TargetClassifier()
