from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field

from app.identity.models import UserRecord, UserRole
from app.tenancy.context import get_current_user, require_roles
from app.core.provider_registry.registry import provider_registry
from app.core.provider_registry.schemas import ProviderMetadata

router = APIRouter(prefix="/tools", tags=["Tools Registry & Inventory"])

class ToolItem(BaseModel):
    id: str
    name: str
    category: str
    description: str
    provider: str
    module_id: str
    version: str
    execution_type: str = "REAL_TIME"  # REAL_TIME, BACKGROUND_JOB, STREAMING
    status: str = "AVAILABLE"  # AVAILABLE, CONFIG_REQUIRED, COMING_SOON, DISABLED
    requires_api_key: bool = False
    supported_inputs: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    usage_count: int = 0
    last_run: Optional[str] = None

# Comprehensive curated tool registry connecting real providers and clear operational states
CURATED_TOOL_DEFINITIONS = [
    # Social Media Intelligence Suite
    {
        "id": "tool_social_media_extractor",
        "name": "Universal Social Media Recon & Media Extractor",
        "category": "Social Media",
        "description": "Multi-platform reconnaissance extracting verified profile avatars, images, links, and identity handles across 30+ top networks.",
        "provider": "Sential Social Sentinel",
        "module_id": "osint",
        "version": "2.5.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["username", "handle", "person", "email"],
    },
    {
        "id": "tool_twitter_intel",
        "name": "Twitter / X Profile & Media Recon",
        "category": "Social Media",
        "description": "Inspects Twitter/X handles, resolves authentic profile avatars, user presence, and timeline verification.",
        "provider": "X / Twitter Prober",
        "module_id": "osint",
        "version": "2.1.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["username", "handle"],
    },
    {
        "id": "tool_youtube_intel",
        "name": "YouTube Channel & Video Intelligence",
        "category": "Social Media",
        "description": "Extracts YouTube video thumbnails (maxres/hq), embed players, channel avatars, and video telemetry.",
        "provider": "YouTube Media Engine",
        "module_id": "osint",
        "version": "2.2.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["url", "username", "query"],
    },
    {
        "id": "tool_instagram_intel",
        "name": "Instagram Profile & Visual Recon",
        "category": "Social Media",
        "description": "Probes Instagram handles, extracts high-resolution avatars, reel links, and public profile footprint.",
        "provider": "Instagram Footprint Engine",
        "module_id": "osint",
        "version": "2.0.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["username", "handle"],
    },
    {
        "id": "tool_telegram_intel",
        "name": "Telegram Channel & User Intelligence",
        "category": "Social Media",
        "description": "Fetches real Telegram profile/channel userpic (320px JPG), bio snippet, and handle verification.",
        "provider": "Telegram Telemetry Engine",
        "module_id": "osint",
        "version": "2.1.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["username", "handle"],
    },
    {
        "id": "tool_reddit_intel",
        "name": "Reddit User & Community OSINT",
        "category": "Social Media",
        "description": "Discovers Reddit public profiles, avatar telemetry, comment history footprints, and handle status.",
        "provider": "Reddit Public Prober",
        "module_id": "osint",
        "version": "1.9.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["username", "handle"],
    },
    {
        "id": "tool_tiktok_intel",
        "name": "TikTok Profile & Video Recon",
        "category": "Social Media",
        "description": "Validates TikTok handles, extracts profile avatars, video links, and public creator footprint.",
        "provider": "TikTok Stream Engine",
        "module_id": "osint",
        "version": "2.0.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["username", "handle"],
    },
    {
        "id": "tool_linkedin_intel",
        "name": "LinkedIn Professional Identity Scout",
        "category": "Social Media",
        "description": "Verifies LinkedIn public profiles, industry affiliations, and corporate employee handles.",
        "provider": "LinkedIn Public Scout",
        "module_id": "osint",
        "version": "2.0.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["username", "person"],
    },
    {
        "id": "tool_discord_intel",
        "name": "Discord Server & Identity Scout",
        "category": "Social Media",
        "description": "Probes Discord user handles, server invites, and community gaming identifiers.",
        "provider": "Discord Scout",
        "module_id": "osint",
        "version": "1.5.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["username", "handle"],
    },
    # People & Username
    {
        "id": "tool_username_prober",
        "name": "Global Username Matrix Prober",
        "category": "Username",
        "description": "Deterministic HTTP profile existence detection across 329 public platforms and developer registries.",
        "provider": "Sential Platform Probers",
        "module_id": "osint",
        "version": "2.4.0",
        "execution_type": "STREAMING",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["username", "handle"],
    },
    {
        "id": "tool_sherlock",
        "name": "Sherlock Username Enumeration",
        "category": "Username",
        "description": "Multi-threaded username hunt across social networks, forums, and developer platforms.",
        "provider": "Sherlock Engine",
        "module_id": "osint",
        "version": "0.14.3",
        "execution_type": "BACKGROUND_JOB",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["username"],
    },
    {
        "id": "tool_maigret",
        "name": "Maigret Dossier Correlator",
        "category": "Username",
        "description": "Recursive OSINT investigation scraping profile pages, extracting IDs, bio info, and avatars.",
        "provider": "Maigret",
        "module_id": "osint",
        "version": "0.4.4",
        "execution_type": "BACKGROUND_JOB",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["username"],
    },
    {
        "id": "tool_whatsmyname",
        "name": "WhatsMyName Registry",
        "category": "Username",
        "description": "Comprehensive enumeration against official WhatsMyName community signature database.",
        "provider": "WhatsMyName Project",
        "module_id": "osint",
        "version": "1.8.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["username"],
    },
    # Email Intelligence
    {
        "id": "tool_holehe",
        "name": "Holehe Email Account Prober",
        "category": "Email",
        "description": "Checks if an email address is registered on over 120 websites without alerting the target.",
        "provider": "Holehe Engine",
        "module_id": "osint",
        "version": "1.61.1",
        "execution_type": "BACKGROUND_JOB",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["email"],
    },
    {
        "id": "tool_hibp",
        "name": "HaveIBeenPwned Breach Analysis",
        "category": "Breach / Exposure",
        "description": "Queries authorized breach exposure databases for compromised credentials and domains.",
        "provider": "HaveIBeenPwned API",
        "module_id": "osint",
        "version": "3.0.0",
        "execution_type": "REAL_TIME",
        "status": "CONFIG_REQUIRED",
        "requires_api_key": True,
        "supported_inputs": ["email", "domain"],
    },
    {
        "id": "tool_email_verifier",
        "name": "SMTP & MX Email Verifier",
        "category": "Email",
        "description": "Performs DNS MX lookup, syntax validation, and SMTP handshake verification.",
        "provider": "Sential Verifier",
        "module_id": "osint",
        "version": "1.2.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["email"],
    },
    # Phone Intelligence
    {
        "id": "tool_phoneinfoga",
        "name": "PhoneInfoga Reconnaissance",
        "category": "Phone",
        "description": "Advanced information gathering tool for international phone numbers, carrier detection, and line type.",
        "provider": "PhoneInfoga Engine",
        "module_id": "osint",
        "version": "2.10.8",
        "execution_type": "BACKGROUND_JOB",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["phone"],
    },
    {
        "id": "tool_numverify",
        "name": "NumVerify Telecom API",
        "category": "Phone",
        "description": "Global carrier lookup, line type detection (Mobile, Landline, VoIP), and geographic validation.",
        "provider": "NumVerify",
        "module_id": "osint",
        "version": "1.0.0",
        "execution_type": "REAL_TIME",
        "status": "CONFIG_REQUIRED",
        "requires_api_key": True,
        "supported_inputs": ["phone"],
    },
    # Infrastructure & Network
    {
        "id": "tool_shodan",
        "name": "Shodan Host & Perimeter Recon",
        "category": "Infrastructure",
        "description": "Search engine for Internet-connected devices, open ports, banners, and vulnerabilities.",
        "provider": "Shodan API",
        "module_id": "threat_intelligence",
        "version": "1.30.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": True,
        "supported_inputs": ["ip", "domain", "cve"],
    },
    {
        "id": "tool_spiderfoot",
        "name": "SpiderFoot Reconnaissance Automation",
        "category": "Infrastructure",
        "description": "Automates OSINT collection for targets spanning IPs, domain names, e-mail addresses, and names.",
        "provider": "SpiderFoot HX",
        "module_id": "osint",
        "version": "4.0.0",
        "execution_type": "BACKGROUND_JOB",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["domain", "ip", "subdomain"],
    },
    {
        "id": "tool_theharvester",
        "name": "theHarvester Public Gatherer",
        "category": "Domain",
        "description": "Gathers emails, names, subdomains, IPs and URLs using multiple public data sources.",
        "provider": "theHarvester",
        "module_id": "osint",
        "version": "4.2.0",
        "execution_type": "BACKGROUND_JOB",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["domain", "email"],
    },
    {
        "id": "tool_dns_recon",
        "name": "DNS Reconnaissance & Enumeration Engine",
        "category": "DNS",
        "description": "Multi-type authoritative DNS record enumeration (A, AAAA, MX, TXT, NS, CNAME, SOA) with latency analysis.",
        "provider": "Sential Resolver",
        "module_id": "osint",
        "version": "2.1.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["domain", "ip"],
    },
    {
        "id": "tool_dns_whois",
        "name": "DNS & WHOIS Record Resolver",
        "category": "DNS",
        "description": "Authoritative DNS record enumeration (A, AAAA, MX, TXT, NS, SOA) and RDAP registration.",
        "provider": "Sential Resolver",
        "module_id": "osint",
        "version": "2.0.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["domain", "ip"],
    },
    {
        "id": "tool_crt_sh",
        "name": "Certificate Transparency Subdomain Finder",
        "category": "Certificates",
        "description": "Queries crt.sh public Certificate Transparency logs to discover all active and historic subdomains.",
        "provider": "crt.sh",
        "module_id": "osint",
        "version": "1.0.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["domain"],
    },
    # Web & Dorks
    {
        "id": "tool_google_dorks",
        "name": "Google Dorks Advanced Operator Engine",
        "category": "Search Engines",
        "description": "Generates targeted Google search queries for exposed files, directories, passwords, and endpoints.",
        "provider": "Google Dork Suite",
        "module_id": "osint",
        "version": "1.5.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["domain", "query"],
    },
    {
        "id": "tool_wayback",
        "name": "Wayback Machine Historical Archive",
        "category": "Archives",
        "description": "Inspects historic snapshots and archived URL endpoints for target domains and URLs.",
        "provider": "Internet Archive",
        "module_id": "osint",
        "version": "2.1.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["domain", "url"],
    },
    # Files, Metadata & Images
    {
        "id": "tool_exiftool",
        "name": "ExifTool Metadata Extractor",
        "category": "Metadata",
        "description": "Reads and analyzes EXIF, XMP, IPTC and metadata tags from uploaded images, documents, and media.",
        "provider": "Phil Harvey ExifTool",
        "module_id": "osint",
        "version": "12.70",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["file", "image"],
    },
    {
        "id": "tool_pdf_analyzer",
        "name": "PDF Structural Document Analyzer",
        "category": "Documents",
        "description": "Extracts author metadata, creation timestamps, modified software, embedded scripts, and hidden text.",
        "provider": "Sential DocEngine",
        "module_id": "osint",
        "version": "1.1.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["file"],
    },
    # Crypto Intelligence
    {
        "id": "tool_crypto_wallet",
        "name": "Blockchain Wallet & Address Prober",
        "category": "Crypto",
        "description": "Queries Bitcoin, Ethereum, and Solana public ledgers for balance, transactions, and token holdings.",
        "provider": "Blockstream & Etherscan",
        "module_id": "osint",
        "version": "1.0.0",
        "execution_type": "REAL_TIME",
        "status": "CONFIG_REQUIRED",
        "requires_api_key": True,
        "supported_inputs": ["crypto_wallet", "transaction"],
    },
    # Threat Intelligence
    {
        "id": "tool_virustotal",
        "name": "VirusTotal File & URL Intelligence",
        "category": "Threat Intelligence",
        "description": "Scans and analyzes files, hashes, domains, and IP addresses against 70+ antivirus scanners.",
        "provider": "VirusTotal v3",
        "module_id": "threat_intelligence",
        "version": "3.0.0",
        "execution_type": "REAL_TIME",
        "status": "CONFIG_REQUIRED",
        "requires_api_key": True,
        "supported_inputs": ["hash", "domain", "ip", "url"],
    },
    {
        "id": "tool_alienvault_otx",
        "name": "AlienVault OTX Pulse Intelligence",
        "category": "Threat Intelligence",
        "description": "Open Threat Exchange IOC pulses, malicious indicators, threat adversary attribution.",
        "provider": "AT&T AlienVault OTX",
        "module_id": "threat_intelligence",
        "version": "2.0.0",
        "execution_type": "REAL_TIME",
        "status": "CONFIG_REQUIRED",
        "requires_api_key": True,
        "supported_inputs": ["ip", "domain", "hash"],
    },
    {
        "id": "tool_maltego_graph",
        "name": "Maltego Graph Relationship Discovery",
        "category": "Threat Intelligence",
        "description": "Transforms and link-analysis engine mapping infrastructure, affiliations, and entity clusters.",
        "provider": "Maltego Engine",
        "module_id": "threat_intelligence",
        "version": "4.3.0",
        "execution_type": "BACKGROUND_JOB",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["domain", "ip", "person"],
    },
    # OWASP ZAP Web Security & DAST Suite
    {
        "id": "tool_zap_active_scan",
        "name": "OWASP ZAP Active Vulnerability Scanner",
        "category": "Threat Intelligence",
        "description": "Performs active DAST security assessment for OWASP Top 10 vulnerabilities (Security Headers, CORS, Cookies, Information Disclosure, Sensitive Endpoints).",
        "provider": "OWASP ZAP Core Assessment Engine",
        "module_id": "threat_intelligence",
        "version": "2.14.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["domain", "url", "subdomain", "ip"],
    },
    {
        "id": "tool_zap_spider",
        "name": "OWASP ZAP Application Spider & Crawler",
        "category": "Threat Intelligence",
        "description": "Deep application crawler discovering endpoints, hidden routes, forms, and attack surfaces using the ZAP Automation Framework.",
        "provider": "OWASP ZAP Spider Gateway",
        "module_id": "threat_intelligence",
        "version": "2.14.0",
        "execution_type": "REAL_TIME",
        "status": "AVAILABLE",
        "requires_api_key": False,
        "supported_inputs": ["domain", "url", "subdomain"],
    }
]

@router.get("", response_model=List[ToolItem])
async def list_tools(
    category: Optional[str] = Query(None, description="Filter by category (e.g. Username, Email, Phone, Infrastructure)"),
    module_id: Optional[str] = Query(None, description="Filter by module: osint or threat_intelligence"),
    status: Optional[str] = Query(None, description="Filter by status: AVAILABLE, CONFIG_REQUIRED, COMING_SOON, DISABLED"),
    current_user: UserRecord = Depends(get_current_user)
) -> List[ToolItem]:
    """Returns curated database-backed tool inventory with defined operational states."""
    items = list(CURATED_TOOL_DEFINITIONS)
    
    if category:
        items = [i for i in items if i["category"].lower() == category.lower()]
    if module_id:
        items = [i for i in items if i["module_id"].lower() == module_id.lower()]
    if status:
        items = [i for i in items if i["status"].upper() == status.upper()]
        
    return [ToolItem(**i) for i in items]

@router.get("/categories")
async def list_tool_categories(
    current_user: UserRecord = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns unique tool categories and counts."""
    categories: Dict[str, int] = {}
    for t in CURATED_TOOL_DEFINITIONS:
        cat = t["category"]
        categories[cat] = categories.get(cat, 0) + 1
    return {
        "categories": categories,
        "total_tools": len(CURATED_TOOL_DEFINITIONS)
    }

class ToolRunRequest(BaseModel):
    target: str
    target_type: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)
    investigation_id: Optional[str] = None

class BatchToolRunRequest(BaseModel):
    tool_ids: List[str]
    target: str
    target_type: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)
    investigation_id: Optional[str] = None

@router.get("/{tool_id}", response_model=ToolItem)
async def get_tool_details(
    tool_id: str,
    current_user: UserRecord = Depends(get_current_user)
) -> ToolItem:
    """Returns specific tool details, input schemas, and configuration requirements."""
    for t in CURATED_TOOL_DEFINITIONS:
        if t["id"] == tool_id:
            return ToolItem(**t)
            
    # Fallback to provider_registry
    from app.core.provider_registry.registry import provider_registry
    p = provider_registry.get_provider(tool_id)
    if p:
        return ToolItem(
            id=p.id,
            name=p.name,
            category=p.category,
            description=p.description or f"Operational {p.name} detection engine.",
            provider=p.name,
            module_id=p.provider_type.value,
            version=p.version,
            execution_type=p.execution_mode.value,
            status="AVAILABLE" if p.enabled else "CONFIG_REQUIRED",
            requires_api_key=p.requires_auth,
            supported_inputs=p.supported_target_types,
            usage_count=p.stats.get("total_executions", 0) if hasattr(p, "stats") else 0
        )
    raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found in registry.")

@router.post("/{tool_id}/run")
async def run_single_tool(
    tool_id: str,
    req: ToolRunRequest,
    current_user: UserRecord = Depends(get_current_user)
) -> Dict[str, Any]:
    """Executes a specific OSINT or Threat Intelligence tool deterministically on a target."""
    from app.modules.tool_executor import tool_executor
    from app.audit.logger import audit_logger

    res = await tool_executor.execute_tool(
        tool_id=tool_id,
        target=req.target,
        target_type=req.target_type,
        options=req.options,
        user=current_user
    )

    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="TOOL_EXECUTED",
        resource_type="tool",
        resource_id=tool_id,
        details={"target": req.target, "status": res.status, "duration_ms": res.duration_ms}
    )

    return res.dict()

@router.post("/batch-run")
async def run_batch_tools(
    req: BatchToolRunRequest,
    current_user: UserRecord = Depends(get_current_user)
) -> Dict[str, Any]:
    """Runs a batch of specified tools against a single target with concurrency control."""
    from app.modules.tool_executor import tool_executor
    import asyncio

    semaphore = asyncio.Semaphore(10)

    async def run_tool_limited(tid: str):
        async with semaphore:
            return await tool_executor.execute_tool(
                tool_id=tid,
                target=req.target,
                target_type=req.target_type,
                options=req.options,
                user=current_user
            )

    tasks = [run_tool_limited(tid) for tid in req.tool_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    processed_results = []
    for r in results:
        if isinstance(r, Exception):
            processed_results.append({"status": "FAILED", "error": str(r)})
        else:
            processed_results.append(r.dict())

    return {
        "target": req.target,
        "tools_executed": len(req.tool_ids),
        "results": processed_results
    }

@router.get("/history/runs")
async def get_tool_run_history(
    limit: int = Query(50, ge=1, le=200),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    current_user: UserRecord = Depends(get_current_user)
) -> Any:
    """Returns persistent tool execution audit and operational telemetry."""
    from app.modules.tool_executor import tool_executor
    history = tool_executor.get_history(tenant_id=current_user.tenant_id, limit=500)
    if page is not None or page_size is not None:
        p = page or 1
        ps = page_size or 20
        total = len(history)
        skip = (p - 1) * ps
        paged = history[skip : skip + ps]
        total_pages = max(1, (total + ps - 1) // ps) if total > 0 else 1
        return {
            "items": paged,
            "total": total,
            "page": p,
            "page_size": ps,
            "total_pages": total_pages
        }
    return history[:limit]

