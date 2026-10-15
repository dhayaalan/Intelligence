from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.identity.models import UserRecord, UserRole
from app.tenancy.context import get_current_user
from app.core.network_safety import network_safety
from app.audit.logger import audit_logger
from app.modules.news_intelligence.models import (
    AddToCaseRequest,
    ClaimInvestigationResult,
    InvestigateClaimRequest,
    InvestigationReport,
    NewsArticle,
    NewsInvestigationRecord,
    NewsSearchRequest,
    NewsSearchResponse,
    NewsWatchlist,
    NewsWatchlistCreate,
    UpdateNewsArticleRequest,
    DeleteNewsArticleResponse,
)
from app.modules.news_intelligence.service import news_intelligence_service
from app.modules.news_intelligence.search_engine import news_retrieval_engine
from app.modules.news_intelligence.multimodal_engine import (
    multimodal_engine,
    SeedIngestRequest,
    IngestedSeedResult,
)
from app.modules.news_intelligence.country_registry import (
    country_registry,
    CountryEntry,
    CountrySourceRecord,
)

router = APIRouter(prefix="/news", tags=["News Intelligence"])


class CreateInvestigationPayload(BaseModel):
    original_query: str
    target_input: str
    canonical_url: Optional[str] = None
    preset_title: Optional[str] = None
    search_id: Optional[str] = None


class ExtractUrlPayload(BaseModel):
    url: str


@router.post("/search", response_model=NewsSearchResponse)
async def execute_news_search(
    req: NewsSearchRequest,
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Query-bound multi-source search engine with relevance ranking,
    entity detection, and search explanation.
    """
    return await news_intelligence_service.execute_search(req, current_user)


@router.get("/search/history")
async def get_search_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: UserRecord = Depends(get_current_user),
):
    """Returns investigator search history to restore past scopes."""
    return news_intelligence_service.list_search_history(
        tenant_id=current_user.tenant_id,
        limit=limit,
    )


@router.get("/articles/{article_id}", response_model=NewsArticle)
async def get_news_article(
    article_id: str,
    query_hint: Optional[str] = Query(None),
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Fetches normalized long-form investigative research article with structured
    sections, global coverage analysis, claims, timeline, and evidence.
    """
    article = news_intelligence_service.get_article(
        tenant_id=current_user.tenant_id,
        article_id=article_id,
        query_hint=query_hint,
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put("/articles/{article_id}", response_model=NewsArticle)
async def update_news_article(
    article_id: str,
    payload: UpdateNewsArticleRequest,
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Allows researchers and journalists to edit the article's title, subtitle,
    category, key takeaways, analyst notes, and assessment verdict.
    """
    updated = news_intelligence_service.update_article(
        tenant_id=current_user.tenant_id,
        user=current_user,
        article_id=article_id,
        updates=payload,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Article not found")
    return updated


@router.delete("/articles/{article_id}", response_model=DeleteNewsArticleResponse)
async def delete_news_article(
    article_id: str,
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Soft-deletes an article: data remains permanently in the database for
    forensic integrity and compliance, but is hidden from normal platform users and search.
    """
    deleted = news_intelligence_service.soft_delete_article(
        tenant_id=current_user.tenant_id,
        user=current_user,
        article_id=article_id,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Article not found")
    return DeleteNewsArticleResponse(
        id=article_id,
        is_deleted=True,
        status="ARCHIVED_HIDDEN",
        message="Article has been soft-deleted from user view. Record retained in database for audit compliance."
    )


@router.post("/articles/{article_id}/investigate-claim", response_model=ClaimInvestigationResult)
async def investigate_article_claim(
    article_id: str,
    payload: InvestigateClaimRequest,
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Executes single-claim factual verification with supporting and contradicting sources.
    """
    payload.context_article_id = article_id
    return news_intelligence_service.investigate_claim(
        tenant_id=current_user.tenant_id,
        req=payload,
    )


class CompareCoveragePayload(BaseModel):
    article_ids: List[str]


@router.post("/articles/compare")
async def compare_articles_coverage(
    payload: CompareCoveragePayload,
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Compares coverage of the same event across multiple international outlets and countries.
    """
    return news_intelligence_service.compare_coverage(
        tenant_id=current_user.tenant_id,
        article_ids=payload.article_ids,
    )


@router.post("/investigations", response_model=NewsInvestigationRecord)
async def create_news_investigation(
    payload: CreateInvestigationPayload,
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Creates a new news investigation scoped to the investigator's query
    and executes full deep claim decomposition and forensic verification.
    """
    # Guard against SSRF if target_input or canonical_url is an HTTP/HTTPS link
    for u in [payload.target_input, payload.canonical_url]:
        if u and (u.startswith("http://") or u.startswith("https://")):
            is_safe, reason = network_safety.validate_url(u)
            if not is_safe:
                raise HTTPException(status_code=400, detail=f"SSRF Protection: {reason}")

    return await news_intelligence_service.create_investigation(
        tenant_id=current_user.tenant_id,
        user=current_user,
        original_query=payload.original_query,
        target_input=payload.target_input,
        canonical_url=payload.canonical_url,
        preset_title=payload.preset_title,
        search_id=payload.search_id,
    )


@router.get("/investigations", response_model=List[NewsInvestigationRecord])
async def list_news_investigations(
    current_user: UserRecord = Depends(get_current_user),
):
    """Lists investigations for the current tenant."""
    return news_intelligence_service.list_investigations(
        tenant_id=current_user.tenant_id,
    )


@router.get("/investigations/{investigation_id}", response_model=NewsInvestigationRecord)
async def get_news_investigation(
    investigation_id: str,
    current_user: UserRecord = Depends(get_current_user),
):
    """Fetches full news investigation record with claims, media, timeline, graph, and evidence."""
    record = news_intelligence_service.get_investigation(
        tenant_id=current_user.tenant_id,
        investigation_id=investigation_id,
    )
    if not record:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return record


@router.post("/investigations/{investigation_id}/analyze", response_model=NewsInvestigationRecord)
async def reanalyze_investigation(
    investigation_id: str,
    current_user: UserRecord = Depends(get_current_user),
):
    """Triggers re-analysis of the investigation against fresh evidence."""
    record = await news_intelligence_service.reanalyze_investigation(
        tenant_id=current_user.tenant_id,
        user=current_user,
        investigation_id=investigation_id,
    )
    if not record:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return record


@router.post("/investigations/{investigation_id}/add-to-case")
async def add_investigation_to_case(
    investigation_id: str,
    payload: AddToCaseRequest,
    current_user: UserRecord = Depends(get_current_user),
):
    """Attaches news investigation and correlated evidence to an existing case."""
    try:
        return await news_intelligence_service.attach_to_case(
            tenant_id=current_user.tenant_id,
            user=current_user,
            investigation_id=investigation_id,
            req=payload,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/investigations/{investigation_id}/report", response_model=InvestigationReport)
async def get_or_generate_report(
    investigation_id: str,
    current_user: UserRecord = Depends(get_current_user),
):
    """Generates an evidence-first executive report for the investigation."""
    try:
        return news_intelligence_service.generate_report(
            tenant_id=current_user.tenant_id,
            investigation_id=investigation_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/watchlists", response_model=List[NewsWatchlist])
async def list_watchlists(
    current_user: UserRecord = Depends(get_current_user),
):
    """Lists scoped topic/keyword watchlists."""
    return news_intelligence_service.list_watchlists(current_user.tenant_id)


@router.post("/watchlists", response_model=NewsWatchlist)
async def create_watchlist(
    payload: NewsWatchlistCreate,
    current_user: UserRecord = Depends(get_current_user),
):
    """Creates a scoped news intelligence watchlist."""
    return news_intelligence_service.create_watchlist(
        tenant_id=current_user.tenant_id,
        user=current_user,
        req=payload,
    )


@router.delete("/watchlists/{watchlist_id}")
async def delete_watchlist(
    watchlist_id: str,
    current_user: UserRecord = Depends(get_current_user),
):
    """Deletes a watchlist."""
    success = news_intelligence_service.delete_watchlist(
        tenant_id=current_user.tenant_id,
        watchlist_id=watchlist_id,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return {"status": "success"}


@router.post("/extract-url")
async def extract_url_content(
    payload: ExtractUrlPayload,
    current_user: UserRecord = Depends(get_current_user),
):
    """Extracts live content and metadata from any public URL without opening an external page."""
    is_safe, reason = network_safety.validate_url(payload.url)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"SSRF Protection: {reason}")
    return await news_retrieval_engine.extract_article(payload.url)


@router.post("/multimodal/ingest-seed", response_model=IngestedSeedResult)
async def ingest_multimodal_seed(
    req: SeedIngestRequest,
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Ingests an investigation seed (news URL, social post URL, or media item)
    with SSRF-guarded validation, canonical resolution, cryptographic SHA-256,
    and 64-bit dHash perceptual media hashing.
    """
    return await multimodal_engine.ingest_url_seed(req.target_url, req.media_type)


# --- Global Country Registry & Comparative Analysis Endpoints ---

@router.get("/countries", response_model=List[CountryEntry])
async def list_countries(
    region: Optional[str] = Query(None),
    verified_only: Optional[bool] = Query(None),
    query: Optional[str] = Query(None),
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Returns the dynamic global country and territory registry based on ISO 3166-1 standards.
    Supports filtering by region, verified news sources, or name/code search.
    """
    return country_registry.list_countries(region=region, has_verified_sources=verified_only, query=query)


@router.get("/countries/{identifier}", response_model=CountryEntry)
async def get_country_detail(
    identifier: str,
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Resolves country metadata by ISO alpha-2, alpha-3, canonical name, alias, or TLD.
    """
    entry = country_registry.get_country(identifier)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Country '{identifier}' not found in global registry")
    return entry


@router.get("/coverage-summary")
async def get_global_coverage_summary(
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Returns an honest, data-driven summary of worldwide news coverage, verified sources,
    and regional distributions without synthetic inflation.
    """
    return country_registry.get_coverage_summary()


class RegisterSourcePayload(BaseModel):
    publisher_name: str
    domain: Optional[str] = None
    canonical_domain: Optional[str] = None
    country_code: Optional[str] = None
    alpha2: Optional[str] = None
    country_name: Optional[str] = None
    original_language: Optional[str] = "en"
    language: Optional[str] = "en"
    feed_or_endpoint: Optional[str] = None
    feed_url: Optional[str] = None
    source_category: Optional[str] = "COMMERCIAL"
    source_type: Optional[str] = "COMMERCIAL"
    is_official: bool = False
    is_verified: bool = False


@router.post("/sources")
async def register_custom_source(
    payload: RegisterSourcePayload,
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Registers a newly discovered publisher domain in the central country source directory.
    Enforces role authorization, SSRF validation, and sets unverified by default unless super-admin.
    """
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN, UserRole.ANALYST]:
        raise HTTPException(status_code=403, detail="Forbidden: insufficient permissions to register news sources")

    dom = (payload.canonical_domain or payload.domain or "").strip()
    if not dom:
        raise HTTPException(status_code=400, detail="Domain cannot be empty")

    test_domain_url = dom if "://" in dom else f"https://{dom}"
    is_safe, reason = network_safety.validate_url(test_domain_url)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"SSRF Protection: domain validation failed: {reason}")

    feed_url = payload.feed_or_endpoint or payload.feed_url
    if feed_url:
        feed_url = feed_url.strip()
        is_safe, reason = network_safety.validate_url(feed_url)
        if not is_safe:
            raise HTTPException(status_code=400, detail=f"SSRF Protection: feed URL validation failed: {reason}")

    code = (payload.alpha2 or payload.country_code or "US").upper()

    # Newly submitted sources default to unverified unless registered by SUPER_ADMIN explicitly verifying them
    is_verified = (current_user.role == UserRole.SUPER_ADMIN) and bool(payload.is_verified)

    rec = CountrySourceRecord(
        publisher_name=payload.publisher_name,
        domain=dom,
        feed_url=feed_url,
        language=payload.original_language or payload.language or "en",
        source_type=payload.source_category or payload.source_type or "COMMERCIAL",
        is_verified=is_verified,
    )
    ok = country_registry.register_custom_source(code, rec)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Country '{code}' not found")

    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="news_source.registered",
        resource_type="news_source",
        resource_id=f"{code}:{dom}",
        details={
            "publisher": payload.publisher_name,
            "domain": dom,
            "country_code": code,
            "is_verified": is_verified,
            "user_role": current_user.role.value,
        }
    )

    c_entry = country_registry.get_country(code)
    country_display = c_entry.name if c_entry else code
    return {
        "status": "registered",
        "country": country_display,
        "country_code": code,
        "publisher": payload.publisher_name,
        "domain": dom,
        "is_verified": is_verified,
        "message": f"Source '{payload.publisher_name}' registered for {country_display} (verified={is_verified})"
    }


class CompareCountriesPayload(BaseModel):
    query: str
    countries: List[str]
    languages: Optional[List[str]] = None


@router.post("/compare", response_model=NewsSearchResponse)
async def compare_countries_coverage(
    payload: CompareCountriesPayload,
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Executes simultaneous multi-country comparative analysis for an event or claim,
    returning article records and a side-by-side country comparison matrix.
    """
    req = NewsSearchRequest(
        query=payload.query,
        countries=payload.countries,
        languages=payload.languages or [],
        compare_countries=True,
    )
    return await news_intelligence_service.execute_search(req, current_user)

