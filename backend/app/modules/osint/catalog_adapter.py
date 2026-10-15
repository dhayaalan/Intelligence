import time
import httpx
import hashlib
import re
import urllib.parse
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import (
    HealthCheckResult, ModuleHealthStatus, EntityPayload, EvidencePayload, EntityType
)
from app.modules.osint.models import (
    ProfileExtractionResult, ExtractionStatus, ExtractedFieldProvenance,
    PublicAccountStatistics, ProfileArtifactItem
)


class OSINTPlatformAdapter(ProviderAdapter):
    """
    Genuine OSINT Platform Prober & Metadata Extractor Adapter.
    Performs verified profile resolution and rich metadata extraction across hundreds
    of public platforms without synthetic or fabricated mock records.
    Distinguishes profile validation from rich metadata extraction.
    """

    def __init__(self, raw: Dict[str, Any]):
        self._raw = raw
        self._platform_id = f"osint_{raw['platform_id']}"
        self._raw_platform_id = raw['platform_id']
        self._name = raw["name"]
        self._category = raw.get("category", "Other")
        self._profile_url_template = raw.get("profile_url_template", "")
        self._check_url_template = raw.get("check_url_template", self._profile_url_template)
        self._detection_method = raw.get("detection_method", "STATUS_CODE")
        self._method = raw.get("method", "GET")
        self._headers = raw.get("headers", {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Sential-OSINT/2.0"
        })
        self._expected_status = raw.get("expected_status", [200])
        self._not_found_status = raw.get("not_found_status", [404])
        self._not_found_keywords = raw.get("not_found_keywords", [])
        self._timeout = float(raw.get("timeout_seconds", 5.0))
        self._supported_targets = ["username", "person", "identity", "handle"]
        
        # Operational execution telemetry & health tracking
        self._last_execution: Optional[datetime] = None
        self._last_status: str = "HEALTH_CHECK_PENDING"
        self._execution_count: int = 0
        self._success_count: int = 0
        self._consecutive_failures: int = 0
        self._last_latency_ms: float = 0.0

    @property
    def provider_id(self) -> str:
        return self._platform_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def category(self) -> str:
        return self._category

    @property
    def supported_targets(self) -> List[str]:
        return self._supported_targets

    @property
    def capabilities(self) -> List[str]:
        return ["profile_lookup", "handle_detection", "metadata_extraction", "provenance_tracking"]

    @property
    def version(self) -> str:
        return "2.0.0"

    async def health_check(self) -> HealthCheckResult:
        """Bounded health check utilizing cached execution telemetry without hammering public websites."""
        if self._last_status == "RATE_LIMITED":
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                latency_ms=self._last_latency_ms,
                message=f"Platform prober '{self._name}' rate limited on recent requests"
            )
        elif self._last_status == "DEGRADED" or self._consecutive_failures >= 3:
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                latency_ms=self._last_latency_ms,
                message=f"Platform prober '{self._name}' experienced {self._consecutive_failures} consecutive connection failures"
            )
        elif self._last_status == "OPERATIONAL":
            return HealthCheckResult(
                status=ModuleHealthStatus.HEALTHY,
                latency_ms=self._last_latency_ms,
                message=f"Platform prober '{self._name}' verified operational ({self._execution_count} probes executed)"
            )
        # Bounded health check pending execution: prober configuration is valid and registered
        return HealthCheckResult(
            status=ModuleHealthStatus.HEALTHY,
            latency_ms=0.0,
            message=f"Platform prober '{self._name}' registered and configured for execution (telemetry pending)"
        )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        target = request.query.strip()
        target_type = request.target_type.lower()

        # Extract handle from domain or email if applicable
        clean_handle = target
        if target_type == "domain" and "." in target:
            clean_handle = target.split(".")[0]
        elif target_type == "email" and "@" in target:
            clean_handle = target.split("@")[0]

        # Clean handle characters
        clean_handle = clean_handle.replace(" ", "").strip()
        if not clean_handle:
            return ProviderResponse(
                provider_id=self.provider_id,
                status="skipped",
                duration_ms=(time.time() - start_time) * 1000
            )

        prof_url = self._profile_url_template.format(username=clean_handle)
        check_url = self._check_url_template.format(username=clean_handle)

        try:
            async with httpx.AsyncClient(headers=self._headers, timeout=self._timeout, follow_redirects=True) as client:
                resp = await client.request(self._method, check_url)
                duration_ms = (time.time() - start_time) * 1000

                # 1. Rate limiting
                if resp.status_code == 429:
                    self._last_status = "RATE_LIMITED"
                    self._consecutive_failures += 1
                    self._last_execution = datetime.now(timezone.utc)
                    self._last_latency_ms = duration_ms
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="skipped",
                        error="Platform rate limit triggered (HTTP 429)",
                        raw_data={
                            "found": False,
                            "status": ExtractionStatus.RATE_LIMITED.value,
                            "profile_url": prof_url
                        },
                        duration_ms=duration_ms
                    )

                # Track successful connectivity
                self._last_status = "OPERATIONAL"
                self._consecutive_failures = 0
                self._success_count += 1
                self._execution_count += 1
                self._last_execution = datetime.now(timezone.utc)
                self._last_latency_ms = duration_ms

                # 2. Access restriction / Auth required
                if resp.status_code in (401, 403):
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="success",
                        raw_data={
                            "found": False,
                            "status": ExtractionStatus.ACCESS_RESTRICTED.value,
                            "profile_url": prof_url,
                            "note": f"Source returned HTTP {resp.status_code}; requires elevated credentials or login."
                        },
                        duration_ms=duration_ms
                    )

                # 3. Check not found status
                if resp.status_code in self._not_found_status:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="success",
                        raw_data={
                            "found": False,
                            "status": ExtractionStatus.NOT_FOUND.value,
                            "profile_url": prof_url
                        },
                        duration_ms=duration_ms
                    )

                body_text = resp.text or ""
                body_lower = body_text.lower()

                # Extract HTML title if present for validation
                title_match = re.search(r'<title>([^<]+)</title>', body_text, re.I)
                page_title = title_match.group(1).strip().lower() if title_match else ""

                # 4. Check for URL redirects to login/auth/homepage
                parsed_check = urllib.parse.urlparse(check_url)
                parsed_final = urllib.parse.urlparse(str(resp.url))

                login_paths = ["/login", "/signin", "/sign-in", "/session/new", "/accounts/login", "/auth/login"]
                if any(ind in parsed_final.path.lower() for ind in login_paths):
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="success",
                        raw_data={
                            "found": False,
                            "status": ExtractionStatus.ACCESS_RESTRICTED.value,
                            "profile_url": prof_url,
                            "note": f"Redirected to authentication page: {resp.url}"
                        },
                        duration_ms=duration_ms
                    )

                if parsed_check.path.strip("/") and not parsed_final.path.strip("/") or parsed_final.path in ["/search", "/explore", "/home"]:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="success",
                        raw_data={
                            "found": False,
                            "status": ExtractionStatus.NOT_FOUND.value,
                            "profile_url": prof_url,
                            "note": f"Redirected to root or generic index page: {resp.url}"
                        },
                        duration_ms=duration_ms
                    )

                # 5. Bot Challenge / WAF wall detection
                challenge_indicators = ["attention required! | cloudflare", "just a moment...", "cf-browser-verification", "turnstile", "verify you are human"]
                if any(ind in body_lower for ind in challenge_indicators) and ("cloudflare" in body_lower or "captcha" in body_lower or "challenge" in body_lower):
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="success",
                        raw_data={
                            "found": False,
                            "status": ExtractionStatus.ACCESS_RESTRICTED.value,
                            "profile_url": prof_url,
                            "note": "Anti-bot challenge or verification wall encountered"
                        },
                        duration_ms=duration_ms
                    )

                # 6. Check for not found keywords in response body or title (Soft-404)
                soft_404_title_keywords = [
                    "page not found", "profile not found", "user not found", 
                    "account not found", "404 not found", "user does not exist",
                    "this page isn't available", "account suspended"
                ]
                if any(kw.lower() in body_lower for kw in self._not_found_keywords) or any(kw in page_title for kw in soft_404_title_keywords):
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="success",
                        raw_data={
                            "found": False,
                            "status": ExtractionStatus.NOT_FOUND.value,
                            "profile_url": prof_url
                        },
                        duration_ms=duration_ms
                    )

                # 7. Profile existence evaluation
                if resp.status_code in self._expected_status:
                    extracted_fields = []
                    field_provenance: Dict[str, ExtractedFieldProvenance] = {}
                    stats = PublicAccountStatistics()
                    artifacts: List[ProfileArtifactItem] = []
                    
                    display_name: Optional[str] = None
                    bio: Optional[str] = None
                    avatar_url: Optional[str] = None
                    location: Optional[str] = None
                    account_created_at: Optional[str] = None
                    native_id: Optional[str] = None
                    website_urls: List[str] = []

                    # Attempt structured JSON parsing if API endpoint or detection method is JSON_API
                    is_json_resp = False
                    json_data = None
                    if "application/json" in resp.headers.get("content-type", "").lower() or self._detection_method == "JSON_API":
                        try:
                            json_data = resp.json()
                            is_json_resp = True
                        except Exception:
                            is_json_resp = False

                    if is_json_resp and isinstance(json_data, dict):
                        # GitHub API
                        if self._raw_platform_id == "github":
                            native_id = str(json_data.get("id", "")) if json_data.get("id") else None
                            display_name = json_data.get("name")
                            bio = json_data.get("bio")
                            avatar_url = json_data.get("avatar_url")
                            location = json_data.get("location")
                            account_created_at = json_data.get("created_at")
                            if json_data.get("blog"):
                                website_urls.append(json_data["blog"])
                            stats.followers = json_data.get("followers")
                            stats.following = json_data.get("following")
                            stats.repositories_count = json_data.get("public_repos")
                            stats.custom_metrics["public_gists"] = json_data.get("public_gists")

                        # GitLab API
                        elif self._raw_platform_id == "gitlab" and isinstance(json_data, list) and len(json_data) > 0:
                            first_user = json_data[0]
                            native_id = str(first_user.get("id", ""))
                            display_name = first_user.get("name")
                            bio = first_user.get("bio")
                            avatar_url = first_user.get("avatar_url")
                            prof_url = first_user.get("web_url", prof_url)

                        # Dev.to API
                        elif self._raw_platform_id == "devto":
                            native_id = str(json_data.get("id", "")) if json_data.get("id") else None
                            display_name = json_data.get("name")
                            bio = json_data.get("summary")
                            avatar_url = json_data.get("profile_image")
                            location = json_data.get("location")
                            account_created_at = json_data.get("joined_at")

                        # Hacker News API
                        elif self._raw_platform_id == "hackernews":
                            native_id = json_data.get("id")
                            bio = json_data.get("about")
                            if json_data.get("created"):
                                account_created_at = datetime.fromtimestamp(json_data["created"], tz=timezone.utc).isoformat()
                            stats.custom_metrics["karma"] = json_data.get("karma")
                            stats.post_count = len(json_data.get("submitted", []))

                        # Chess.com API
                        elif self._raw_platform_id == "chess_com":
                            native_id = str(json_data.get("player_id", ""))
                            display_name = json_data.get("name")
                            avatar_url = json_data.get("avatar")
                            location = json_data.get("location")
                            stats.followers = json_data.get("followers")
                            if json_data.get("joined"):
                                account_created_at = datetime.fromtimestamp(json_data["joined"], tz=timezone.utc).isoformat()

                        # Generic JSON parser fallback
                        else:
                            display_name = json_data.get("name") or json_data.get("display_name") or json_data.get("username")
                            bio = json_data.get("bio") or json_data.get("description") or json_data.get("about") or json_data.get("summary")
                            avatar_url = json_data.get("avatar_url") or json_data.get("profile_image") or json_data.get("avatar")
                            location = json_data.get("location")
                            if json_data.get("followers") is not None and isinstance(json_data.get("followers"), int):
                                stats.followers = json_data["followers"]

                    elif not is_json_resp and body_text:
                        # Extract OpenGraph / Meta attributes from HTML
                        try:
                            # og:title
                            title_m = re.search(r'<meta[^>]+(?:property|name)=["\'](?:og:title|twitter:title)["\'][^>]+content=["\']([^"\']+)["\']', body_text, re.I)
                            if not title_m:
                                title_m = re.search(r'<title>([^<]+)</title>', body_text, re.I)
                            if title_m:
                                raw_title = title_m.group(1).strip()
                                # Clean up generic suffixes like " - Twitter" or " - Steam Community"
                                cleaned_title = re.sub(r'\s*[\-|•|—].*$', '', raw_title).strip()
                                if cleaned_title and len(cleaned_title) < 80:
                                    display_name = cleaned_title

                            # og:description
                            desc_m = re.search(r'<meta[^>]+(?:property|name)=["\'](?:og:description|twitter:description|description)["\'][^>]+content=["\']([^"\']+)["\']', body_text, re.I)
                            if desc_m:
                                desc_val = desc_m.group(1).strip()
                                if desc_val and len(desc_val) > 3 and not any(x in desc_val.lower() for x in ["sign in", "login", "enable javascript", "cookie policy"]):
                                    bio = desc_val[:400]

                            # og:image (genuine profile image only, ignore generic assets)
                            img_m = re.search(r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image|twitter:image:src)["\'][^>]+content=["\']([^"\']+)["\']', body_text, re.I)
                            if img_m:
                                cand_img = img_m.group(1).strip()
                                if not any(x in cand_img.lower() for x in ["logo", "default", "favicon", "placeholder", "sprite", "og-default"]):
                                    if cand_img.startswith("//"):
                                        avatar_url = f"https:{cand_img}"
                                    elif cand_img.startswith("http"):
                                        avatar_url = cand_img
                                    elif cand_img.startswith("/"):
                                        parsed_orig = urllib.parse.urlparse(prof_url)
                                        avatar_url = f"{parsed_orig.scheme}://{parsed_orig.netloc}{cand_img}"
                        except Exception:
                            pass

                    # Record extracted provenance
                    now_iso = datetime.now(timezone.utc).isoformat()
                    if display_name:
                        extracted_fields.append("display_name")
                        field_provenance["display_name"] = ExtractedFieldProvenance(
                            field_name="display_name",
                            value=display_name,
                            source_provider=self.provider_id,
                            source_path="json.name" if is_json_resp else "html.og:title",
                            is_inferred=not is_json_resp,
                            observed_at=now_iso,
                            confidence=0.95 if is_json_resp else 0.82
                        )
                    if bio:
                        extracted_fields.append("bio")
                        field_provenance["bio"] = ExtractedFieldProvenance(
                            field_name="bio",
                            value=bio,
                            source_provider=self.provider_id,
                            source_path="json.bio" if is_json_resp else "html.og:description",
                            is_inferred=not is_json_resp,
                            observed_at=now_iso,
                            confidence=0.95 if is_json_resp else 0.80
                        )
                    if avatar_url:
                        extracted_fields.append("avatar_url")
                        field_provenance["avatar_url"] = ExtractedFieldProvenance(
                            field_name="avatar_url",
                            value=avatar_url,
                            source_provider=self.provider_id,
                            source_path="json.avatar_url" if is_json_resp else "html.og:image",
                            is_inferred=not is_json_resp,
                            observed_at=now_iso,
                            confidence=0.98 if is_json_resp else 0.85
                        )
                    if location:
                        extracted_fields.append("location")
                        field_provenance["location"] = ExtractedFieldProvenance(
                            field_name="location",
                            value=location,
                            source_provider=self.provider_id,
                            source_path="json.location",
                            is_inferred=False,
                            observed_at=now_iso,
                            confidence=0.90
                        )
                    if stats.followers is not None:
                        extracted_fields.append("statistics.followers")
                    if stats.repositories_count is not None:
                        extracted_fields.append("statistics.repositories_count")

                    # Determine honest extraction status
                    if len(extracted_fields) >= 3 or (is_json_resp and len(extracted_fields) >= 2):
                        status = ExtractionStatus.METADATA_EXTRACTED
                    elif len(extracted_fields) > 0:
                        status = ExtractionStatus.PARTIAL_EXTRACTION
                    else:
                        # Genuine validation of account existence, without rich metadata
                        if clean_handle.lower() in body_lower or clean_handle.lower() in page_title:
                            status = ExtractionStatus.PROFILE_VALIDATED
                        else:
                            status = ExtractionStatus.UNVERIFIED

                    extraction_res = ProfileExtractionResult(
                        platform_id=self._raw_platform_id,
                        platform_name=self._name,
                        native_id=native_id,
                        username=clean_handle,
                        display_name=display_name,
                        canonical_url=prof_url,
                        submitted_url=prof_url,
                        bio=bio,
                        avatar_url=avatar_url,
                        website_urls=website_urls,
                        location=location,
                        category=self._category,
                        account_created_at=account_created_at,
                        statistics=stats,
                        artifacts=artifacts,
                        status=status,
                        first_seen_at=now_iso,
                        last_seen_at=now_iso,
                        fetched_at=now_iso,
                        is_cached=False,
                        source_endpoint=check_url,
                        extraction_method="JSON_API" if is_json_resp else "HTTP_PROBE",
                        fields_extracted=extracted_fields,
                        fields_unsupported=[],
                        field_provenance=field_provenance,
                        raw_preview={"status_code": resp.status_code, "content_type": resp.headers.get("content-type")}
                    )

                    if status == ExtractionStatus.UNVERIFIED:
                        return ProviderResponse(
                            provider_id=self.provider_id,
                            status="success",
                            raw_data={
                                "found": False,
                                "status": ExtractionStatus.UNVERIFIED.value,
                                "profile_url": prof_url,
                                "note": "HTTP 200 received but target handle could not be confirmed in page body or title."
                            },
                            duration_ms=duration_ms
                        )

                    conf_evidence = 0.95 if status == ExtractionStatus.METADATA_EXTRACTED else 0.85
                    conf_entity = 0.92 if status == ExtractionStatus.METADATA_EXTRACTED else 0.80

                    # Build evidence payload
                    sha256 = hashlib.sha256(f"{prof_url}:{resp.status_code}:{now_iso}".encode()).hexdigest()
                    evidence = [{
                        "source": self.provider_id,
                        "provider": self.provider_id,
                        "module": "osint",
                        "reference": prof_url,
                        "confidence": conf_evidence,
                        "raw_data": {
                            "url": prof_url,
                            "platform": self._name,
                            "category": self._category,
                            "status_code": resp.status_code,
                            "status": status.value,
                            "fields_extracted": extracted_fields
                        },
                        "hash": sha256
                    }]

                    # Build entity payload
                    entity = EntityPayload(
                        type=EntityType.USERNAME,
                        value=f"{clean_handle}@{self._name.lower().replace(' ', '')}",
                        confidence=conf_entity,
                        sources=[self.provider_id],
                        metadata={
                            "platform": self._name,
                            "category": self._category,
                            "profile_url": prof_url,
                            "status": status.value,
                            "status_code": resp.status_code,
                            "avatar_url": avatar_url,
                            "bio": bio,
                            "display_name": display_name,
                            "fields_extracted": extracted_fields,
                            "is_metadata_extracted": status in (ExtractionStatus.METADATA_EXTRACTED, ExtractionStatus.PARTIAL_EXTRACTION),
                        }
                    )

                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="success",
                        raw_data={
                            "found": True,
                            "platform": self._name,
                            "profile_url": prof_url,
                            "status": status.value,
                            "extraction_result": extraction_res.dict(),
                            "entities": [entity.dict()],
                            "evidence": evidence
                        },
                        duration_ms=duration_ms
                    )

                return ProviderResponse(
                    provider_id=self.provider_id,
                    status="success",
                    raw_data={
                        "found": False,
                        "status": f"HTTP_{resp.status_code}",
                        "profile_url": prof_url
                    },
                    duration_ms=duration_ms
                )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._consecutive_failures += 1
            if self._consecutive_failures >= 3:
                self._last_status = "DEGRADED"
            self._last_execution = datetime.now(timezone.utc)
            self._last_latency_ms = duration_ms
            return ProviderResponse(
                provider_id=self.provider_id,
                status="skipped",
                error=str(e),
                duration_ms=duration_ms
            )
