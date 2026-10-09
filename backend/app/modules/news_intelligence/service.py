import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.logging import app_logger
from app.evidence.service import evidence_service
from app.identity.models import UserRecord
from app.infrastructure.mongodb.repositories import case_repo, investigation_repo
from app.modules.news_intelligence.investigation_pipeline import news_investigation_pipeline
from app.modules.news_intelligence.models import (
    AddToCaseRequest,
    ClaimInvestigationResult,
    InvestigateClaimRequest,
    InvestigationReport,
    InvestigationStatus,
    NewsArticle,
    NewsInvestigationRecord,
    NewsSearchRequest,
    NewsSearchResponse,
    NewsWatchlist,
    NewsWatchlistCreate,
    UpdateNewsArticleRequest,
    DeleteNewsArticleResponse,
)
from app.modules.news_intelligence.repository import (
    news_investigation_repo,
    news_search_history_repo,
    news_watchlist_repo,
)
from app.modules.news_intelligence.search_engine import news_retrieval_engine
from app.module_sdk.models import EvidencePayload


class NewsIntelligenceService:
    """Core orchestration service for search-driven news intelligence investigations."""

    async def execute_search(self, req: NewsSearchRequest, user: UserRecord) -> NewsSearchResponse:
        """Executes multi-source query-bound retrieval and logs search history."""
        response = await news_retrieval_engine.search(req)

        # Record in search history
        search_history_entry = {
            "search_id": response.search_id,
            "tenant_id": user.tenant_id,
            "investigator_id": user.id,
            "investigator_name": user.name or user.email,
            "query": req.query,
            "search_mode": req.search_mode.value,
            "total_results": response.total_results,
            "category_counts": response.category_counts,
            "timestamp": response.timestamp,
        }
        news_search_history_repo.record_search(user.tenant_id, search_history_entry)
        return response

    def list_search_history(self, tenant_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        return news_search_history_repo.list_history(tenant_id, limit)

    def get_article(self, tenant_id: str, article_id: str, query_hint: Optional[str] = None) -> Optional[NewsArticle]:
        """Retrieves or synthesizes the complete long-form investigative research article."""
        return news_retrieval_engine.get_article(article_id, query_hint)

    def update_article(
        self,
        tenant_id: str,
        user: UserRecord,
        article_id: str,
        updates: UpdateNewsArticleRequest
    ) -> Optional[NewsArticle]:
        """Allows authorized researchers / journalists to edit report metadata, verdict, and takeaways."""
        return news_retrieval_engine.update_article(article_id, updates, user.email)

    def soft_delete_article(
        self,
        tenant_id: str,
        user: UserRecord,
        article_id: str
    ) -> Optional[NewsArticle]:
        """Soft-deletes an article from view while preserving the complete database record for compliance."""
        return news_retrieval_engine.soft_delete_article(article_id, user.email)

    def investigate_claim(self, tenant_id: str, req: InvestigateClaimRequest) -> ClaimInvestigationResult:
        """Executes scoped factual verification of an individual claim sentence."""
        return news_retrieval_engine.investigate_claim(req.claim_text, req.context_article_id)

    def compare_coverage(self, tenant_id: str, article_ids: List[str]) -> Dict[str, Any]:
        """Provides side-by-side comparative media analysis across outlets."""
        return news_retrieval_engine.compare_coverage(article_ids)

    async def create_investigation(
        self,
        tenant_id: str,
        user: UserRecord,
        original_query: str,
        target_input: str,
        canonical_url: Optional[str] = None,
        preset_title: Optional[str] = None,
        search_id: Optional[str] = None,
    ) -> NewsInvestigationRecord:
        """Creates a new news intelligence investigation and runs deep analysis."""
        inv_id = f"ninv_{uuid.uuid4().hex[:10]}"
        investigator_name = user.name or user.email

        record = await news_investigation_pipeline.execute_full_investigation(
            investigation_id=inv_id,
            tenant_id=tenant_id,
            investigator_id=user.id,
            investigator_name=investigator_name,
            original_query=original_query,
            target_input=target_input,
            canonical_url=canonical_url,
            preset_title=preset_title,
        )
        record.search_id = search_id

        # Persist investigation
        record_dict = record.dict()
        news_investigation_repo.save(record_dict)

        # Unify with platform evidence vault
        for ev in record.evidence_vault:
            try:
                payload = EvidencePayload(
                    id=ev.id,
                    source=ev.source,
                    timestamp=datetime.now(timezone.utc),
                    provider="news_intelligence",
                    module="news_intelligence",
                    collection_method="forensic_verification",
                    reference=ev.source_url or "",
                    confidence=ev.reliability_score / 100.0,
                    raw_data={
                        "claim_relationship": ev.claim_relationship,
                        "retrieval_reason": ev.retrieval_reason,
                        "text": ev.extracted_text,
                    },
                    hash=ev.hash_value,
                )
                evidence_service.store_evidence(
                    tenant_id=tenant_id,
                    payload=payload,
                    investigation_id=inv_id,
                    search_id=search_id,
                )
            except Exception as e:
                app_logger.warning(f"Failed to bridge evidence {ev.id} to core vault: {e}")

        return record

    def get_investigation(self, tenant_id: str, investigation_id: str) -> Optional[NewsInvestigationRecord]:
        doc = news_investigation_repo.get_by_id(tenant_id, investigation_id)
        if doc:
            return NewsInvestigationRecord(**doc)
        return None

    def list_investigations(self, tenant_id: str) -> List[NewsInvestigationRecord]:
        docs = news_investigation_repo.list_all(tenant_id)
        return [NewsInvestigationRecord(**d) for d in docs]

    async def reanalyze_investigation(
        self, tenant_id: str, user: UserRecord, investigation_id: str
    ) -> Optional[NewsInvestigationRecord]:
        existing = self.get_investigation(tenant_id, investigation_id)
        if not existing:
            return None

        updated = await news_investigation_pipeline.execute_full_investigation(
            investigation_id=existing.id,
            tenant_id=tenant_id,
            investigator_id=user.id,
            investigator_name=user.name or user.email,
            original_query=existing.original_query,
            target_input=existing.artifact.article_body or existing.artifact.title,
            canonical_url=existing.artifact.canonical_url,
            preset_title=existing.artifact.title,
        )
        updated.search_id = existing.search_id
        news_investigation_repo.save(updated.dict())
        return updated

    async def attach_to_case(
        self, tenant_id: str, user: UserRecord, investigation_id: str, req: AddToCaseRequest
    ) -> Dict[str, Any]:
        """Integrates News Intelligence with existing platform Case Management."""
        inv = self.get_investigation(tenant_id, investigation_id)
        if not inv:
            raise ValueError("News investigation not found")

        # Update case record if case repo exists
        case_doc = None
        if hasattr(case_repo, "get_by_id"):
            try:
                case_doc = await case_repo.get_by_id(tenant_id, req.case_id)
            except Exception:
                pass
        now_str = datetime.now(timezone.utc).isoformat()

        # Update investigation record with associated case id
        inv.associated_case_id = req.case_id
        news_investigation_repo.save(inv.dict())

        # Also link into investigations repo if case matches investigation id
        try:
            if hasattr(investigation_repo, "get_by_id"):
                core_inv = await investigation_repo.get_by_id(tenant_id, req.case_id)
                if core_inv:
                    ev_ids = set(core_inv.get("evidence_ids", []))
                    for ev in inv.evidence_vault:
                        ev_ids.add(ev.id)
                    core_inv["evidence_ids"] = list(ev_ids)
                    await investigation_repo.save(tenant_id, core_inv)
        except Exception as e:
            app_logger.debug(f"Case bridge note: {e}")

        return {
            "status": "attached",
            "case_id": req.case_id,
            "investigation_id": investigation_id,
            "evidence_attached_count": len(inv.evidence_vault),
            "attached_at": now_str,
        }

    def generate_report(self, tenant_id: str, investigation_id: str) -> InvestigationReport:
        inv = self.get_investigation(tenant_id, investigation_id)
        if not inv:
            raise ValueError("Investigation not found")
        return news_investigation_pipeline.generate_investigation_report(inv)

    # --- Watchlists ---

    def list_watchlists(self, tenant_id: str) -> List[NewsWatchlist]:
        docs = news_watchlist_repo.list_all(tenant_id)
        return [NewsWatchlist(**d) for d in docs]

    def create_watchlist(self, tenant_id: str, user: UserRecord, req: NewsWatchlistCreate) -> NewsWatchlist:
        w_id = f"nwt_{uuid.uuid4().hex[:8]}"
        watchlist = NewsWatchlist(
            id=w_id,
            tenant_id=tenant_id,
            created_by=user.name or user.email,
            topic_query=req.topic_query,
            monitored_entities=req.monitored_entities,
            monitored_domains=req.monitored_domains,
            check_interval_hours=req.check_interval_hours,
            is_active=True,
        )
        news_watchlist_repo.save(watchlist.dict())
        return watchlist

    def delete_watchlist(self, tenant_id: str, watchlist_id: str) -> bool:
        return news_watchlist_repo.delete(tenant_id, watchlist_id)


news_intelligence_service = NewsIntelligenceService()
