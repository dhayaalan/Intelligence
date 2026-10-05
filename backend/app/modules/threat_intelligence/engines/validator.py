import re
import ipaddress
import socket
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from app.core.exceptions import AppException


class TargetType(str):
    DOMAIN = "DOMAIN"
    SUBDOMAIN = "SUBDOMAIN"
    IP = "IP"
    IP_RANGE = "IP_RANGE"
    URL = "URL"
    HOSTNAME = "HOSTNAME"
    ASN = "ASN"
    EMAIL = "EMAIL"
    HASH = "HASH"
    CVE = "CVE"
    USERNAME = "USERNAME"
    PERSON = "PERSON"
    KEYWORD = "KEYWORD"
    ORGANIZATION = "ORGANIZATION"
    IOC = "IOC"


BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("169.254.0.0/16"),    # Link-local / AWS / GCP / Azure metadata
    ipaddress.ip_network("0.0.0.0/8"),        # Current network
    ipaddress.ip_network("224.0.0.0/4"),      # Multicast
    ipaddress.ip_network("240.0.0.0/4"),      # Reserved
    ipaddress.ip_network("::1/128"),          # IPv6 Loopback
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link-local
    ipaddress.ip_network("fc00::/7"),         # IPv6 Unique Local
]

# Standard RFC1918 private ranges (blocked by default unless explicitly permitted in private network profile)
RFC1918_PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("100.64.0.0/10"),    # Carrier-grade NAT
]

BLOCKED_HOSTNAMES = [
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "instance-data",
    "metadata",
]


class SSRFGuard:
    """
    Enforces comprehensive Server-Side Request Forgery (SSRF) and DNS re-binding defenses.
    """

    @staticmethod
    def is_ip_blocked(ip_str: str, allow_private_ranges: bool = False) -> Tuple[bool, str]:
        """Checks whether an IP address is in a prohibited range."""
        try:
            ip_obj = ipaddress.ip_address(ip_str.strip())
        except ValueError:
            return True, f"Invalid IP address format: {ip_str}"

        # Loopback, link-local, cloud metadata are NEVER allowed
        for net in BLOCKED_IP_NETWORKS:
            if ip_obj in net:
                return True, f"Blocked special-use/cloud metadata IP: {ip_str} in {net}"

        if not allow_private_ranges:
            for net in RFC1918_PRIVATE_NETWORKS:
                if ip_obj in net:
                    return True, f"Blocked internal/private network IP: {ip_str} in {net}"

        return False, "IP address authorized"

    @staticmethod
    def validate_hostname_resolution(hostname: str, allow_private_ranges: bool = False) -> Tuple[bool, str, List[str]]:
        """
        Resolves hostname to IP addresses and verifies none resolve to prohibited SSRF ranges.
        """
        clean_host = hostname.strip().lower()
        if clean_host in BLOCKED_HOSTNAMES or clean_host.endswith(".local") or clean_host.endswith(".internal"):
            return False, f"Blocked prohibited hostname: {clean_host}", []

        try:
            addr_info = socket.getaddrinfo(clean_host, None)
            resolved_ips = list(set([item[4][0] for item in addr_info if item[4]]))
            if not resolved_ips:
                return False, f"Hostname {clean_host} could not be resolved to any IP address", []

            for ip in resolved_ips:
                blocked, reason = SSRFGuard.is_ip_blocked(ip, allow_private_ranges=allow_private_ranges)
                if blocked:
                    return False, f"Hostname {clean_host} resolves to prohibited IP {ip}: {reason}", resolved_ips

            return True, "Hostname safely resolved", resolved_ips
        except socket.gaierror:
            # If domain cannot be resolved immediately, we allow passive collection but reject active probing
            return True, "Hostname unresolvable in local DNS (passive intelligence permitted)", []
        except Exception as e:
            return False, f"Resolution error for {clean_host}: {str(e)}", []

    @staticmethod
    def validate_url(url_str: str, allow_private_ranges: bool = False) -> Tuple[bool, str]:
        """Validates URL scheme, host, and destination against SSRF."""
        try:
            parsed = urlparse(url_str.strip())
            if parsed.scheme.lower() not in ["http", "https"]:
                return False, f"Unsupported URL scheme '{parsed.scheme}'. Only HTTP/HTTPS allowed."

            if not parsed.hostname:
                return False, "URL contains no valid hostname."

            # Check if hostname is direct IP
            try:
                ip_obj = ipaddress.ip_address(parsed.hostname)
                blocked, reason = SSRFGuard.is_ip_blocked(str(ip_obj), allow_private_ranges)
                if blocked:
                    return False, reason
                return True, "URL IP authorized"
            except ValueError:
                pass

            # Resolve domain
            safe, reason, _ = SSRFGuard.validate_hostname_resolution(parsed.hostname, allow_private_ranges)
            if not safe:
                return False, reason

            return True, "URL destination authorized"
        except Exception as e:
            return False, f"URL parse failure: {str(e)}"

    @staticmethod
    def check_redirect_scope(
        original_url: str,
        redirect_url: str,
        allow_external_redirects: bool = False,
        allow_private_ranges: bool = False
    ) -> Tuple[bool, str]:
        """
        Prevents redirect-based scope bypasses and internal port pivoting.
        """
        orig_parsed = urlparse(original_url)
        redir_parsed = urlparse(redirect_url)

        if redir_parsed.scheme.lower() not in ["http", "https"]:
            return False, "OUT_OF_SCOPE_REDIRECT: Unsupported redirect protocol"

        safe, reason = SSRFGuard.validate_url(redirect_url, allow_private_ranges)
        if not safe:
            return False, f"OUT_OF_SCOPE_REDIRECT: {reason}"

        if not allow_external_redirects:
            # Check domain boundary
            orig_host = (orig_parsed.hostname or "").lower()
            redir_host = (redir_parsed.hostname or "").lower()
            if orig_host != redir_host and not redir_host.endswith("." + orig_host):
                return False, f"OUT_OF_SCOPE_REDIRECT: Redirect from {orig_host} to external {redir_host} not permitted"

        return True, "Redirect authorized"

    @classmethod
    def is_safe_target(cls, target: str, target_type: Optional[str] = None) -> Dict[str, Any]:
        """Convenience method returning dict status for tests and controllers."""
        valid, reason, _ = TargetValidator.validate(target, target_type)
        return {"safe": valid, "reason": reason}

    @classmethod
    def validate_redirect(
        cls,
        source_url: str,
        target_url: str,
        allowed_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Convenience method returning dict status for redirect verification."""
        safe, reason = cls.check_redirect_scope(
            original_url=source_url,
            redirect_url=target_url,
            allow_external_redirects=False
        )
        if safe and allowed_domains and "*" not in allowed_domains:
            parsed = urlparse(target_url)
            host = (parsed.hostname or "").lower()
            if not any(host == d.lower() or host.endswith("." + d.lower()) for d in allowed_domains):
                return {"safe": False, "reason": f"OUT_OF_SCOPE_REDIRECT: Host {host} not in allowed domains"}
        return {"safe": safe, "reason": reason}


class TargetValidator:
    """
    Validates and canonicalizes all security assessment target types.
    """

    DOMAIN_REGEX = re.compile(
        r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-_]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$"
    )
    CVE_REGEX = re.compile(r"^CVE-\d{4}-\d{4,7}$", re.IGNORECASE)
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    HASH_MD5_REGEX = re.compile(r"^[a-fA-F0-9]{32}$")
    HASH_SHA1_REGEX = re.compile(r"^[a-fA-F0-9]{40}$")
    HASH_SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")

    @classmethod
    def detect_target_type(cls, target: str) -> str:
        t = target.strip()
        if t.startswith("http://") or t.startswith("https://"):
            return TargetType.URL
        if "/" in t and not t.startswith("http"):
            try:
                ipaddress.ip_network(t, strict=False)
                return TargetType.IP_RANGE
            except ValueError:
                pass
        try:
            ipaddress.ip_address(t)
            return TargetType.IP
        except ValueError:
            pass
        if cls.CVE_REGEX.match(t):
            return TargetType.CVE
        if cls.EMAIL_REGEX.match(t):
            return TargetType.EMAIL
        if cls.HASH_SHA256_REGEX.match(t) or cls.HASH_MD5_REGEX.match(t) or cls.HASH_SHA1_REGEX.match(t):
            return TargetType.HASH
        if t.upper().startswith("AS") and t[2:].isdigit():
            return TargetType.ASN
        if cls.DOMAIN_REGEX.match(t):
            parts = t.split(".")
            if len(parts) > 2:
                return TargetType.SUBDOMAIN
            return TargetType.DOMAIN
        if t.startswith("@") or (re.match(r"^[a-zA-Z0-9_.-]+$", t) and "." not in t):
            return TargetType.USERNAME
        return TargetType.KEYWORD

    @classmethod
    def classify_target(cls, target: str) -> str:
        """Alias for detect_target_type."""
        return cls.detect_target_type(target)

    @classmethod
    def validate_target_syntax(cls, target: str, target_type: Optional[str] = None) -> Dict[str, Any]:
        """Convenience method returning dict validation status and canonical form."""
        t_clean = target.strip().lower()
        valid, reason, d_type = cls.validate(target, target_type)
        return {
            "valid": valid,
            "reason": reason,
            "target_type": d_type,
            "canonical": t_clean
        }

    @classmethod
    def validate(cls, target: str, target_type: Optional[str] = None) -> Tuple[bool, str, str]:
        """
        Validates target syntax and returns (is_valid, error_reason, canonical_target_type).
        """
        if not target or not target.strip():
            return False, "Target cannot be empty", ""

        cleaned = target.strip()
        detected_type = cls.detect_target_type(cleaned)
        actual_type = target_type.upper() if target_type else detected_type

        if actual_type == TargetType.URL:
            parsed = urlparse(cleaned)
            if parsed.scheme.lower() not in ["http", "https"]:
                return False, f"Unsupported URL scheme '{parsed.scheme}'. Only HTTP/HTTPS allowed.", actual_type
            safe, reason = SSRFGuard.validate_url(cleaned)
            if not safe:
                return False, reason, actual_type

        elif actual_type in [TargetType.DOMAIN, TargetType.SUBDOMAIN, TargetType.HOSTNAME]:
            clean_host = cleaned.split(":")[0].lower()
            if not cls.DOMAIN_REGEX.match(clean_host) and clean_host != "localhost":
                return False, f"Invalid domain/hostname format: {cleaned}", actual_type
            safe, reason, _ = SSRFGuard.validate_hostname_resolution(clean_host)
            if not safe:
                return False, reason, actual_type

        elif actual_type == TargetType.IP:
            try:
                ipaddress.ip_address(cleaned)
                blocked, reason = SSRFGuard.is_ip_blocked(cleaned)
                if blocked:
                    return False, reason, actual_type
            except ValueError:
                return False, f"Invalid IPv4/IPv6 address: {cleaned}", actual_type

        elif actual_type == TargetType.IP_RANGE:
            try:
                net = ipaddress.ip_network(cleaned, strict=False)
                if net.num_addresses > 256:
                    return False, f"IP Range too large ({net.num_addresses} hosts). Max /24 (256 hosts) permitted.", actual_type
                for net_block in BLOCKED_IP_NETWORKS:
                    if net.overlaps(net_block):
                        return False, f"IP Range overlaps with prohibited special network: {net_block}", actual_type
            except ValueError:
                return False, f"Invalid CIDR IP Range: {cleaned}", actual_type

        elif actual_type == TargetType.CVE:
            if not cls.CVE_REGEX.match(cleaned):
                return False, f"Invalid CVE format: {cleaned} (Expected CVE-YYYY-NNNN)", actual_type

        elif actual_type in [TargetType.USERNAME, TargetType.PERSON, TargetType.KEYWORD, TargetType.ORGANIZATION, TargetType.IOC]:
            if len(cleaned) < 1 or len(cleaned) > 256:
                return False, f"Invalid length for {actual_type}: {cleaned}", actual_type
            if any(c in cleaned for c in ["\x00", "\r", "\n"]):
                return False, "Prohibited control characters in target", actual_type

        return True, "Target validation passed", actual_type


class AuthorizationGate:
    """
    Validates scan permissions, tenant scope authorization, and active testing clearance.
    """

    @staticmethod
    def verify_scan_authorization(
        target: str,
        target_type: str,
        scan_profile: str,
        active_confirmed: bool,
        scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """
        Enforces strict authorization before launching scanner engines.
        """
        # 1. Target syntax & SSRF validation
        valid, reason, detected_type = TargetValidator.validate(target, target_type)
        if not valid:
            return False, f"SCAN_NOT_AUTHORIZED: {reason}"

        # 2. Check active scan requirements
        is_active_profile = scan_profile in [
            "SAFE_DISCOVERY",
            "SERVICE_DISCOVERY",
            "WEB_DISCOVERY",
            "NETWORK_DISCOVERY",
            "WEB_SECURITY_ASSESSMENT",
            "COMPREHENSIVE"
        ]

        if is_active_profile and not active_confirmed and scan_profile in ["WEB_SECURITY_ASSESSMENT", "COMPREHENSIVE"]:
            return False, "SCAN_NOT_AUTHORIZED: Active security assessment requires explicit authorization confirmation"

        # 3. Scope boundary validation
        if scope:
            excluded = [e.lower() for e in scope.get("excluded_targets", [])]
            t_low = target.lower().strip()
            if any(exc in t_low for exc in excluded):
                return False, f"SCAN_NOT_AUTHORIZED: Target '{target}' is explicitly listed in excluded targets"

        return True, "Scan authorized"

    @classmethod
    def verify_authorization(
        cls,
        target: str,
        target_type: str,
        scan_profile: str,
        scope: Optional[Dict[str, Any]] = None,
        is_active_authorized: bool = False
    ) -> Dict[str, Any]:
        """Convenience method returning dict status for tests and router endpoints."""
        auth, reason = cls.verify_scan_authorization(
            target=target,
            target_type=target_type,
            scan_profile=scan_profile,
            active_confirmed=is_active_authorized,
            scope=scope
        )
        return {"authorized": auth, "reason": reason}
