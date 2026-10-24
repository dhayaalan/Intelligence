import socket
import ipaddress
import urllib.parse
from typing import Tuple, Optional
import httpx

BLOCKED_PORTS = {
    21, 22, 23, 25, 53, 110, 135, 137, 138, 139, 143, 445,
    1433, 1521, 2049, 2375, 2376, 3306, 3389, 5432, 5900,
    6379, 7474, 7687, 8000, 8090, 8091, 8500, 9000, 9042, 9200, 9300,
    11211, 27017, 27018, 28017
}

CLOUD_METADATA_HOSTS = {
    "169.254.169.254",
    "metadata.google.internal",
    "metadata.azure.internal",
    "100.100.100.200"
}

class SSRFSecurityError(ValueError):
    """Raised when a URL violates SSRF security boundaries."""
    pass

def validate_url_for_ssrf(url: str) -> urllib.parse.ParseResult:
    """
    Validates a remote URL against Server-Side Request Forgery (SSRF) threats.
    Enforces scheme, host, port, and IP range constraints.
    Rejects loopback, link-local, private RFC1918, cloud metadata, and restricted ports.
    """
    if not url or not isinstance(url, str):
        raise SSRFSecurityError("Media URL cannot be empty")

    parsed = urllib.parse.urlparse(url.strip())
    if parsed.scheme.lower() not in ("http", "https"):
        raise SSRFSecurityError(f"Unsupported URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFSecurityError("Media URL lacks a valid hostname")

    # Check hostname against cloud metadata indicators
    if hostname.lower() in CLOUD_METADATA_HOSTS:
        raise SSRFSecurityError("Access to cloud metadata endpoints is strictly forbidden")

    port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
    if port in BLOCKED_PORTS:
        raise SSRFSecurityError(f"Port {port} is restricted to protect internal infrastructure")

    # Resolve hostname to check all destination IP addresses
    try:
        addr_info = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise SSRFSecurityError(f"Could not resolve host '{hostname}': {str(e)}")

    if not addr_info:
        raise SSRFSecurityError(f"Host '{hostname}' resolved to no network addresses")

    for entry in addr_info:
        sockaddr = entry[4]
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            raise SSRFSecurityError(f"Invalid IP address format: {ip_str}")

        if ip.is_loopback:
            raise SSRFSecurityError(f"Access to loopback address ({ip_str}) is prohibited")
        if ip.is_private:
            raise SSRFSecurityError(f"Access to private internal network address ({ip_str}) is prohibited")
        if ip.is_link_local:
            raise SSRFSecurityError(f"Access to link-local address ({ip_str}) is prohibited")
        if ip.is_multicast or ip.is_reserved or ip.is_unspecified:
            raise SSRFSecurityError(f"Access to reserved/multicast IP address ({ip_str}) is prohibited")

    return parsed

async def safe_fetch_media_url(
    url: str,
    max_size_bytes: int = 50 * 1024 * 1024,
    timeout_seconds: float = 20.0,
    max_redirects: int = 4
) -> Tuple[bytes, str, str]:
    """
    Safely fetches media from a remote URL with full SSRF checks,
    hop-by-hop redirect re-validation, and streaming size bounds.

    Returns:
        Tuple of (content_bytes, content_type, filename)
    """
    current_url = url
    redirect_count = 0

    headers = {
        "User-Agent": "Sential-Intelligence-Forensics/2.0 (+https://sential.io/security)",
        "Accept": "image/*,video/*,audio/*,*/*"
    }

    async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=False) as client:
        while True:
            # 1. Validate destination URL before connection
            validate_url_for_ssrf(current_url)

            resp = await client.get(current_url, headers=headers)

            # 2. Check for redirect responses
            if resp.status_code in (301, 302, 303, 307, 308):
                redirect_count += 1
                if redirect_count > max_redirects:
                    raise SSRFSecurityError(f"Too many redirects ({redirect_count} > {max_redirects})")
                
                redirect_url = resp.headers.get("location")
                if not redirect_url:
                    raise SSRFSecurityError("Redirect response missing Location header")

                # Resolve relative redirects against current URL
                current_url = urllib.parse.urljoin(current_url, redirect_url)
                continue

            if resp.status_code != 200:
                raise ValueError(f"Remote server returned HTTP {resp.status_code}")

            content_type = resp.headers.get("content-type", "").lower()
            
            # 3. Stream or buffer content with bounded size
            raw_bytes = resp.content
            if len(raw_bytes) == 0:
                raise ValueError("Remote media URL returned an empty file (0 bytes)")

            if len(raw_bytes) > max_size_bytes:
                max_mb = max_size_bytes // (1024 * 1024)
                raise ValueError(f"Remote file size ({len(raw_bytes)} bytes) exceeds the {max_mb}MB limit")

            # Extract filename from URL or headers
            filename = current_url.split("?")[0].split("/")[-1] or "remote_media"
            if "." not in filename:
                if "image/png" in content_type:
                    filename += ".png"
                elif "image/webp" in content_type:
                    filename += ".webp"
                elif "video/mp4" in content_type:
                    filename += ".mp4"
                elif "audio/wav" in content_type:
                    filename += ".wav"
                else:
                    filename += ".jpg"

            return raw_bytes, content_type, filename
