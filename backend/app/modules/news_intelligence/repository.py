from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from app.infrastructure.mongodb.repositories import BaseMongoRepository
from app.core.database import db as memory_cache
from app.modules.news_intelligence.models import (
    NewsInvestigationRecord,
    NewsSearchResultItem,
    NewsWatchlist,
)


class NewsInvestigationRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("news_investigations")

    def get_by_id(self, tenant_id: str, investigation_id: str) -> Optional[Dict[str, Any]]:
        with memory_cache._lock:
            doc = memory_cache.news_investigations.get(investigation_id)
            if doc and doc.get("tenant_id") == tenant_id:
                return doc

        col = self.sync_collection
        if col is not None:
            doc = col.find_one({"id": investigation_id, "tenant_id": tenant_id}, {"_id": 0})
            if doc:
                with memory_cache._lock:
                    memory_cache.news_investigations[investigation_id] = doc
                return doc
        return None

    def list_all(self, tenant_id: str) -> List[Dict[str, Any]]:
        with memory_cache._lock:
            cached = [
                d for d in memory_cache.news_investigations.values()
                if d.get("tenant_id") == tenant_id
            ]

        col = self.sync_collection
        if col is not None:
            docs = list(col.find({"tenant_id": tenant_id}, {"_id": 0}))
            if docs:
                with memory_cache._lock:
                    for d in docs:
                        memory_cache.news_investigations[d["id"]] = d
                return sorted(docs, key=lambda x: x.get("created_at", ""), reverse=True)

        return sorted(cached, key=lambda x: x.get("created_at", ""), reverse=True)

    def save(self, record_data: Dict[str, Any]) -> None:
        inv_id = record_data["id"]
        tenant_id = record_data["tenant_id"]
        with memory_cache._lock:
            memory_cache.news_investigations[inv_id] = record_data
        self._sync_write({"id": inv_id, "tenant_id": tenant_id}, record_data)


class NewsSearchHistoryRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("news_searches")

    def record_search(self, tenant_id: str, search_data: Dict[str, Any]) -> None:
        s_id = search_data["search_id"]
        with memory_cache._lock:
            memory_cache.news_searches[s_id] = search_data
        self._sync_write({"search_id": s_id, "tenant_id": tenant_id}, search_data)

    def list_history(self, tenant_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with memory_cache._lock:
            cached = [
                d for d in memory_cache.news_searches.values()
                if d.get("tenant_id") == tenant_id
            ]

        col = self.sync_collection
        if col is not None:
            docs = list(col.find({"tenant_id": tenant_id}, {"_id": 0}).sort("timestamp", -1).limit(limit))
            if docs:
                return docs
        return sorted(cached, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]


class NewsWatchlistRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("news_watchlists")

    def list_all(self, tenant_id: str) -> List[Dict[str, Any]]:
        with memory_cache._lock:
            cached = [
                d for d in memory_cache.news_watchlists.values()
                if d.get("tenant_id") == tenant_id
            ]

        col = self.sync_collection
        if col is not None:
            docs = list(col.find({"tenant_id": tenant_id}, {"_id": 0}))
            if docs:
                return docs
        return cached

    def save(self, watchlist_data: Dict[str, Any]) -> None:
        w_id = watchlist_data["id"]
        tenant_id = watchlist_data["tenant_id"]
        with memory_cache._lock:
            memory_cache.news_watchlists[w_id] = watchlist_data
        self._sync_write({"id": w_id, "tenant_id": tenant_id}, watchlist_data)

    def delete(self, tenant_id: str, watchlist_id: str) -> bool:
        with memory_cache._lock:
            if watchlist_id in memory_cache.news_watchlists:
                del memory_cache.news_watchlists[watchlist_id]
        col = self.sync_collection
        if col is not None:
            col.delete_one({"id": watchlist_id, "tenant_id": tenant_id})
        return True


class NewsArticleRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("news_articles")

    def get_by_id(self, article_id: str, include_deleted: bool = False) -> Optional[Dict[str, Any]]:
        with memory_cache._lock:
            doc = memory_cache.news_articles.get(article_id)
            if doc:
                if not include_deleted and doc.get("is_deleted", False):
                    return None
                return doc

        col = self.sync_collection
        if col is not None:
            query = {"id": article_id}
            if not include_deleted:
                query["is_deleted"] = {"$ne": True}
            doc = col.find_one(query, {"_id": 0})
            if doc:
                with memory_cache._lock:
                    memory_cache.news_articles[article_id] = doc
                return doc
        return None

    def save(self, article_data: Dict[str, Any]) -> None:
        art_id = article_data["id"]
        with memory_cache._lock:
            memory_cache.news_articles[art_id] = article_data
        self._sync_write({"id": art_id}, article_data)

    def soft_delete(self, article_id: str, deleted_by: str) -> Optional[Dict[str, Any]]:
        doc = self.get_by_id(article_id, include_deleted=True)
        if not doc:
            return None
        doc["is_deleted"] = True
        doc["deleted_at"] = datetime.now(timezone.utc).isoformat()
        doc["deleted_by"] = deleted_by
        doc["investigation_status"] = "ARCHIVED_HIDDEN"
        self.save(doc)
        return doc


news_investigation_repo = NewsInvestigationRepository()
news_search_history_repo = NewsSearchHistoryRepository()
news_watchlist_repo = NewsWatchlistRepository()
news_article_repo = NewsArticleRepository()

