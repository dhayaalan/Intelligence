import ipaddress
import socket
import urllib.parse
from typing import Tuple, List, Optional
from app.core.logging import app_logger

# Disallowed private and sensitive IP networks (RFC 1918, RFC 3927, RFC 6890)
DISALLOWED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private RFC 1918
    ipaddress.ip_network("172.16.0.0/12"),    # Private RFC 1918
    ipaddress.ip_network("192.168.0.0/16"),   # Private RFC 1918
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local / Cloud Metadata (169.254.169.254)
    ipaddress.ip_network("0.0.0.0/8"),        # Current network
    ipaddress.ip_network("100.64.0.0/10"),    # Shared Address Space
    ipaddress.ip_network("192.0.0.0/24"),     # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),     # TEST-NET-1
    ipaddress.ip_network("198.18.0.0/15"),    # Benchmarking
    ipaddress.ip_network("198.51.100.0/24"),  # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),   # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),      # Multicast
    ipaddress.ip_network("240.0.0.0/4"),      # Reserved
    ipaddress.ip_network("::1/128"),          # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link-Local
]

BLOCKED_HOSTNAMES = {
    "localhost", "localhost.localdomain", "127.0.0.1", "::1",
    "metadata.google.internal", "metadata.internal"
}


class NetworkSafety:
    """Centralized Server-Side Request Forgery (SSRF) and destination validator."""

    @staticmethod
    def is_ip_disallowed(ip_str: str) -> bool:
        """Checks if an IP address belongs to private, loopback, or reserved networks."""
        try:
            ip = ipaddress.ip_address(ip_str)
            for net in DISALLOWED_NETWORKS:
                if ip in net:
                    return True
            return False
        except ValueError:
            return True

    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, str]:
        """
        Validates target URL scheme, hostname, and resolved IP addresses against SSRF risks.
        Returns: (is_safe: bool, reason: str)
        """
        if not url or not isinstance(url, str):
            return False, "Empty or invalid URL supplied"

        cleaned_url = url.strip()
        try:
            parsed = urllib.parse.urlparse(cleaned_url)
        except Exception:
            return False, "Malformed URL format"

        # 1. Scheme check (strictly HTTP/HTTPS)
        scheme = parsed.scheme.lower()
        if scheme not in ("http", "https"):
            return False, f"Unsupported URL scheme '{scheme}'. Only HTTP and HTTPS are permitted."

        hostname = parsed.hostname
        if not hostname:
            return False, "URL does not contain a valid hostname"

        hostname_clean = hostname.strip().lower()

        # 2. Blocklist hostnames
        if hostname_clean in BLOCKED_HOSTNAMES or hostname_clean.endswith(".local") or hostname_clean.endswith(".internal"):
            return False, f"Target hostname '{hostname_clean}' resolves to internal or restricted infrastructure"

        # 3. Direct IP address check
        try:
            direct_ip = ipaddress.ip_address(hostname_clean)
            if cls.is_ip_disallowed(str(direct_ip)):
                return False, f"Target IP address '{direct_ip}' belongs to a private or restricted network range"
            return True, ""
        except ValueError:
            # It is a domain name, proceed to DNS resolution check
            pass

        # 4. Resolve DNS and inspect all returned addresses
        try:
            addr_info = socket.getaddrinfo(hostname_clean, None, proto=socket.IPPROTO_TCP)
            resolved_ips = list(set([res[4][0] for res in addr_info if res[4]]))

            if not resolved_ips:
                return False, f"Hostname '{hostname_clean}' could not be resolved via DNS"

            for ip_cand in resolved_ips:
                if cls.is_ip_disallowed(ip_cand):
                    app_logger.warning(
                        f"SSRF block: Hostname '{hostname_clean}' resolved to private/restricted IP '{ip_cand}'"
                    )
                    return False, f"Hostname '{hostname_clean}' resolved to restricted IP address '{ip_cand}'"

            return True, ""
        except socket.gaierror:
            # Domain cannot be resolved
            return False, f"Could not resolve host '{hostname_clean}' via DNS"
        except Exception as e:
            return False, f"Error validating target host '{hostname_clean}': {str(e)}"

    @classmethod
    def enforce_safe_url(cls, url: str) -> None:
        """Raises ValueError if URL is determined to be unsafe or internal."""
        is_safe, reason = cls.validate_url(url)
        if not is_safe:
            raise ValueError(f"SSRF Protection: {reason}")


network_safety = NetworkSafety()
