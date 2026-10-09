import logging
import uuid
from typing import Any, Dict, List
from app.module_sdk.contract import IntelligenceModule
from app.module_sdk.manifest import ModuleManifest
from app.module_sdk.models import (
    HealthCheckResult, ModuleHealthStatus, NormalizedModuleResult,
    SearchContext, EntityPayload, RelationshipPayload, EvidencePayload,
    EntityType, RelationshipType
)
from app.modules.news_intelligence.manifest import NEWS_INTELLIGENCE_MANIFEST
from app.modules.news_intelligence.service import news_intelligence_service
from app.modules.news_intelligence.models import NewsSearchRequest, SearchMode
from app.identity.models import UserRecord, UserRole, UserStatus

logger = logging.getLogger("sential.news_intelligence")

class NewsIntelligenceModule(IntelligenceModule):
    """
    Search-driven News Intelligence Investigation Engine module.
    Conforms to IntelligenceModule contract.
    """
    def __init__(self):
        self._manifest = NEWS_INTELLIGENCE_MANIFEST
        self._config: Dict[str, Any] = {}

    @property
    def manifest(self) -> ModuleManifest:
        return self._manifest

    async def initialize(self, config: Dict[str, Any]) -> None:
        self._config = config or {}
        logger.info("News Intelligence Investigation Engine initialized.")

    async def health_check(self) -> HealthCheckResult:
        return HealthCheckResult(
            module_id=self.manifest.id,
            status=ModuleHealthStatus.HEALTHY,
            latency_ms=1.5,
            message="News Intelligence Investigation Engine is operational.",
            details={"providers_active": len(self.manifest.providers)}
        )

    async def capabilities(self) -> List[str]:
        return list(self.manifest.capabilities)

    async def search(self, context: SearchContext) -> NormalizedModuleResult:
        """
        Executes query-bound search and converts to normalized module results.
        """
        req = NewsSearchRequest(
            query=context.query,
            search_mode=SearchMode.SEMANTIC
        )
        user = UserRecord(
            id=context.user_id or "system_user",
            email="investigator@sential.local",
            name="investigator",
            hashed_password="",
            role=UserRole.INVESTIGATOR,
            tenant_id=context.tenant_id or "default",
            status=UserStatus.ACTIVE
        )
        resp = await news_intelligence_service.execute_search(req=req, user=user)

        entities: List[EntityPayload] = []
        evidence: List[EvidencePayload] = []
        relationships: List[RelationshipPayload] = []

        # Target query entity
        entities.append(EntityPayload(
            type=EntityType.KEYWORD,
            value=context.query,
            confidence=1.0,
            sources=[self.manifest.id],
            metadata={"is_search_target": True}
        ))

        for item in resp.results:
            pub_name = item.publisher or item.source
            if pub_name:
                entities.append(EntityPayload(
                    type=EntityType.PUBLISHER,
                    value=pub_name,
                    confidence=item.relevance_score / 100.0,
                    sources=[self.manifest.id],
                    metadata={"source": item.source}
                ))

            if item.title:
                entities.append(EntityPayload(
                    type=EntityType.ARTICLE,
                    value=item.title,
                    confidence=item.relevance_score / 100.0,
                    sources=[self.manifest.id],
                    metadata={
                        "id": item.id,
                        "article_id": item.id,
                        "url": item.canonical_url,
                        "summary": item.summary,
                        "relevance": item.relevance_score,
                        "publisher": item.publisher,
                        "country": item.country,
                        "author": item.author,
                        "hero_image": item.hero_image,
                        "thumbnail_url": item.thumbnail_url,
                        "cluster_id": item.cluster_id,
                        "publication_date": item.publication_date,
                        "content_type": item.content_type,
                        "source_type": item.source_type,
                        "is_independent": item.is_independent,
                        "story_cluster": item.story_cluster.dict() if hasattr(item.story_cluster, "dict") else (item.story_cluster.model_dump() if hasattr(item.story_cluster, "model_dump") else item.story_cluster) if item.story_cluster else None,
                    }
                ))

            # Map detected entities
            for ent_name in item.detected_entities:
                entities.append(EntityPayload(
                    type=EntityType.KEYWORD,
                    value=ent_name,
                    confidence=item.relevance_score / 100.0,
                    sources=[self.manifest.id],
                    metadata={"query_root": resp.original_query}
                ))

            # Map evidence
            evidence.append(EvidencePayload(
                source=item.source,
                provider="news_intelligence",
                module=self.manifest.id,
                reference=item.canonical_url or "",
                confidence=item.relevance_score / 100.0,
                raw_data={
                    "title": item.title,
                    "summary": item.summary,
                    "published_at": item.publication_date,
                    "relevance": item.relevance_score,
                    "relevance_explanation": item.search_explanation,
                    "content_type": item.content_type
                }
            ))

            # Map relationships
            if pub_name and item.title:
                relationships.append(RelationshipPayload(
                    source_entity_value=pub_name,
                    target_entity_value=item.title,
                    relationship_type=RelationshipType.PUBLISHED,
                    confidence=0.95,
                    sources=[self.manifest.id]
                ))
            if item.title:
                relationships.append(RelationshipPayload(
                    source_entity_value=item.title,
                    target_entity_value=context.query,
                    relationship_type=RelationshipType.REPORTS_ON,
                    confidence=item.relevance_score / 100.0,
                    sources=[self.manifest.id]
                ))

        return NormalizedModuleResult(
            module=self.manifest.id,
            execution_id=context.search_id or f"exec_news_{uuid.uuid4().hex[:8]}",
            status="completed",
            entities=entities,
            relationships=relationships,
            evidence=evidence,
            sources=[self.manifest.id],
            metadata={"search_id": resp.search_id, "total_results": resp.total_results}
        )

    async def shutdown(self) -> None:
        logger.info("News Intelligence module shut down cleanly.")

news_intelligence_module = NewsIntelligenceModule()
