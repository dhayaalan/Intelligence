from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
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
    return await news_retrieval_engine.extract_article(payload.url)
