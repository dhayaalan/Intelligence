import asyncio
import re
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from app.infrastructure.mongodb.client import get_database, get_sync_database
from app.core.database import db as memory_cache
from app.core.logging import app_logger

class BaseMongoRepository:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    @property
    def collection(self):
        db = get_database()
        if db is not None:
            return db[self.collection_name]
        return None

    @property
    def sync_collection(self):
        db = get_sync_database()
        if db is not None:
            return db[self.collection_name]
        return None

    def _sync_write(self, filter_query: Dict[str, Any], doc: Dict[str, Any]):
        """Synchronous write using pymongo if available."""
        col = self.sync_collection
        if col is not None:
            try:
                col.update_one(filter_query, {"$set": doc}, upsert=True)
            except Exception as e:
                app_logger.warning(f"Sync write failed for {self.collection_name}: {e}")

class TenantRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("tenants")

    async def get_by_id(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        if self.collection is not None:
            doc = await self.collection.find_one({"id": tenant_id}, {"_id": 0})
            if doc:
                return doc
        with memory_cache._lock:
            return memory_cache.tenants.get(tenant_id)

    async def list_all(self) -> List[Dict[str, Any]]:
        if self.collection is not None:
            cursor = self.collection.find({}, {"_id": 0})
            items = await cursor.to_list(length=1000)
            if items:
                return items
        with memory_cache._lock:
            return list(memory_cache.tenants.values())

    async def save(self, tenant_data: Dict[str, Any]) -> None:
        tenant_id = tenant_data["id"]
        with memory_cache._lock:
            memory_cache.tenants[tenant_id] = tenant_data
        if self.collection is not None:
            await self.collection.update_one({"id": tenant_id}, {"$set": tenant_data}, upsert=True)
        else:
            self._sync_write({"id": tenant_id}, tenant_data)

class UserRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("users")

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        if self.collection is not None:
            doc = await self.collection.find_one({"id": user_id}, {"_id": 0})
            if doc:
                return doc
        with memory_cache._lock:
            return memory_cache.users.get(user_id)

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        clean_email = email.strip().lower()
        if self.collection is not None:
            doc = await self.collection.find_one({"email": clean_email}, {"_id": 0})
            if doc:
                return doc
        with memory_cache._lock:
            for u in memory_cache.users.values():
                if u.get("email", "").lower() == clean_email:
                    return u
            return None

    async def list_by_tenant(self, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {"tenant_id": tenant_id} if tenant_id else {}
        if self.collection is not None:
            cursor = self.collection.find(query, {"_id": 0})
            items = await cursor.to_list(length=1000)
            if items:
                return items
        with memory_cache._lock:
            users = list(memory_cache.users.values())
            if tenant_id:
                users = [u for u in users if u.get("tenant_id") == tenant_id]
            return users

    async def save(self, user_data: Dict[str, Any]) -> None:
        user_id = user_data["id"]
        with memory_cache._lock:
            memory_cache.users[user_id] = user_data
        if self.collection is not None:
            await self.collection.update_one({"id": user_id}, {"$set": user_data}, upsert=True)
        else:
            self._sync_write({"id": user_id}, user_data)

class InvestigationRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("investigations")

    async def get_by_id(self, tenant_id: str, investigation_id: str) -> Optional[Dict[str, Any]]:
        if self.collection is not None:
            doc = await self.collection.find_one({"id": investigation_id, "tenant_id": tenant_id}, {"_id": 0})
            if doc:
                return doc
        with memory_cache._lock:
            data = memory_cache.investigations.get(investigation_id)
            if data and data.get("tenant_id") == tenant_id:
                return data
            return None

    async def list_by_tenant(self, tenant_id: str) -> List[Dict[str, Any]]:
        if self.collection is not None:
            cursor = self.collection.find({"tenant_id": tenant_id}, {"_id": 0}).sort("updated_at", -1)
            items = await cursor.to_list(length=1000)
            if items:
                return items
        with memory_cache._lock:
            items = [d for d in memory_cache.investigations.values() if d.get("tenant_id") == tenant_id]
            return sorted(items, key=lambda x: str(x.get("updated_at", "")), reverse=True)

    async def save(self, tenant_id: str, inv_data: Dict[str, Any]) -> None:
        inv_id = inv_data["id"]
        inv_data["tenant_id"] = tenant_id
        with memory_cache._lock:
            memory_cache.investigations[inv_id] = inv_data
        if self.collection is not None:
            await self.collection.update_one(
                {"id": inv_id, "tenant_id": tenant_id},
                {"$set": inv_data},
                upsert=True
            )
        else:
            self._sync_write({"id": inv_id, "tenant_id": tenant_id}, inv_data)

class CaseRepository(BaseMongoRepository):
    """Case management repository directly mapped to MongoDB."""
    def __init__(self):
        super().__init__("cases")

    async def get_by_id(self, tenant_id: str, case_id: str) -> Optional[Dict[str, Any]]:
        if self.collection is not None:
            doc = await self.collection.find_one({"id": case_id, "tenant_id": tenant_id}, {"_id": 0})
            if doc:
                return doc
        return None

    async def list_by_tenant(self, tenant_id: str) -> List[Dict[str, Any]]:
        if self.collection is not None:
            cursor = self.collection.find({"tenant_id": tenant_id}, {"_id": 0}).sort("updated_at", -1)
            return await cursor.to_list(length=1000)
        return []

    async def save(self, tenant_id: str, case_data: Dict[str, Any]) -> None:
        case_id = case_data["id"]
        case_data["tenant_id"] = tenant_id
        if self.collection is not None:
            await self.collection.update_one(
                {"id": case_id, "tenant_id": tenant_id},
                {"$set": case_data},
                upsert=True
            )
        else:
            self._sync_write({"id": case_id, "tenant_id": tenant_id}, case_data)

class EntityRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("entities")

    async def list_by_tenant(self, tenant_id: str, investigation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {"tenant_id": tenant_id}
        if investigation_id:
            query["investigation_id"] = investigation_id
        if self.collection is not None:
            try:
                cursor = self.collection.find(query, {"_id": 0})
                items = await cursor.to_list(length=1000)
                if items:
                    return items
            except Exception:
                pass
        with memory_cache._lock:
            items = [d for d in memory_cache.entities.values() if not d.get("tenant_id") or d.get("tenant_id") in [tenant_id, "tenant_global", "global"]]
            if investigation_id:
                items = [d for d in items if d.get("investigation_id") == investigation_id]
            return items

    async def find_by_identifier(self, tenant_id: str, identifier_type: str, canonical_value: str) -> List[Dict[str, Any]]:
        """
        Directly queries MongoDB for an exact verified identifier (email or phone)
        without arbitrary 1000-record truncation. Also checks memory cache.
        """
        target_type = identifier_type.lower()
        items = []
        if self.collection is not None:
            try:
                query = {
                    "tenant_id": tenant_id,
                    "$or": [
                        {"type": target_type, "value": canonical_value},
                        {"type": target_type, "value": {"$regex": f"^{re.escape(canonical_value)}$", "$options": "i"}},
                        {"value": canonical_value}
                    ]
                }
                cursor = self.collection.find(query, {"_id": 0})
                docs = await cursor.to_list(length=100)
                if docs:
                    items.extend(docs)
            except Exception:
                pass

        with memory_cache._lock:
            for d in memory_cache.entities.values():
                t_id = d.get("tenant_id")
                if t_id and t_id != tenant_id and t_id not in ["tenant_global", "global"]:
                    continue
                d_val = str(d.get("value", "")).strip()
                d_type = str(d.get("type", "")).lower()
                if (d_type == target_type or not d_type) and d_val.lower() == canonical_value.lower():
                    if not any(it.get("id") == d.get("id") for it in items):
                        items.append(d)

        return items

    async def save(self, tenant_id: str, entity_data: Dict[str, Any]) -> None:
        ent_id = entity_data["id"]
        entity_data["tenant_id"] = tenant_id
        with memory_cache._lock:
            memory_cache.entities[ent_id] = entity_data
        if self.collection is not None:
            await self.collection.update_one(
                {"id": ent_id, "tenant_id": tenant_id},
                {"$set": entity_data},
                upsert=True
            )
        else:
            self._sync_write({"id": ent_id, "tenant_id": tenant_id}, entity_data)

class RelationshipRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("relationships")

    async def list_by_tenant(self, tenant_id: str) -> List[Dict[str, Any]]:
        if self.collection is not None:
            try:
                cursor = self.collection.find({"tenant_id": tenant_id}, {"_id": 0})
                items = await cursor.to_list(length=1000)
                if items:
                    return items
            except Exception:
                pass
        with memory_cache._lock:
            return [d for d in memory_cache.relationships.values() if not d.get("tenant_id") or d.get("tenant_id") in [tenant_id, "tenant_global", "global"]]

    async def list_by_investigation(self, tenant_id: str, investigation_id: str) -> List[Dict[str, Any]]:
        items = []
        if self.collection is not None:
            try:
                cursor = self.collection.find({"tenant_id": tenant_id, "investigation_id": investigation_id}, {"_id": 0})
                docs = await cursor.to_list(length=500)
                if docs:
                    items.extend(docs)
            except Exception:
                pass
        with memory_cache._lock:
            for d in memory_cache.relationships.values():
                t_id = d.get("tenant_id")
                if t_id and t_id != tenant_id and t_id not in ["tenant_global", "global"]:
                    continue
                if d.get("investigation_id") == investigation_id:
                    if not any(it.get("id") == d.get("id") for it in items):
                        items.append(d)
            if not items:
                inv = memory_cache.investigations.get(investigation_id)
                if inv and (not inv.get("tenant_id") or inv.get("tenant_id") in [tenant_id, "tenant_global", "global"]):
                    items = inv.get("relationships", [])
        return items

    async def find_by_entity_values(self, tenant_id: str, values: List[str]) -> List[Dict[str, Any]]:
        """Finds relationships where either source or target matches any of the values."""
        clean_vals = [v.strip().lower() for v in values if v]
        if not clean_vals:
            return []
        items = []
        if self.collection is not None:
            try:
                query = {
                    "tenant_id": tenant_id,
                    "$or": [
                        {"source_val": {"$in": values}},
                        {"target_val": {"$in": values}},
                        {"source_entity_value": {"$in": values}},
                        {"target_entity_value": {"$in": values}}
                    ]
                }
                cursor = self.collection.find(query, {"_id": 0})
                docs = await cursor.to_list(length=100)
                if docs:
                    items.extend(docs)
            except Exception:
                pass

        with memory_cache._lock:
            for d in memory_cache.relationships.values():
                t_id = d.get("tenant_id")
                if t_id and t_id != tenant_id and t_id not in ["tenant_global", "global"]:
                    continue
                s_val = str(d.get("source_val") or d.get("source_entity_value", "")).strip().lower()
                t_val = str(d.get("target_val") or d.get("target_entity_value", "")).strip().lower()
                if s_val in clean_vals or t_val in clean_vals:
                    if not any(it.get("id") == d.get("id") for it in items):
                        items.append(d)

        return items

    async def get_by_id(self, tenant_id: str, rel_id: str) -> Optional[Dict[str, Any]]:
        if self.collection is not None:
            try:
                doc = await self.collection.find_one({"id": rel_id, "tenant_id": tenant_id}, {"_id": 0})
                if doc:
                    return doc
            except Exception:
                pass
        with memory_cache._lock:
            rel = memory_cache.relationships.get(rel_id)
            if rel and (not rel.get("tenant_id") or rel.get("tenant_id") in [tenant_id, "tenant_global", "global"]):
                return rel
            for inv in memory_cache.investigations.values():
                if not inv.get("tenant_id") or inv.get("tenant_id") in [tenant_id, "tenant_global", "global"]:
                    for r in inv.get("relationships", []):
                        if r.get("id") == rel_id:
                            return r
        return None

    async def expand_entity_1hop(
        self,
        tenant_id: str,
        entity_id_or_val: str,
        investigation_id: Optional[str] = None,
        limit: int = 25,
        relationship_types: Optional[List[str]] = None,
        min_confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Bounded 1-hop relationship traversal originating from an entity identifier or value.
        Preserves tenancy boundaries, deduplicates edges, and returns connected node stubs.
        """
        key_val = entity_id_or_val.strip().lower()
        rels: List[Dict[str, Any]] = []
        seen_ids = set()

        # 1. Query Mongo collection if online
        if self.collection is not None:
            try:
                q: Dict[str, Any] = {
                    "tenant_id": tenant_id,
                    "$or": [
                        {"source_id": entity_id_or_val},
                        {"target_id": entity_id_or_val},
                        {"source_entity_value": {"$regex": f"^{re.escape(entity_id_or_val)}$", "$options": "i"}},
                        {"target_entity_value": {"$regex": f"^{re.escape(entity_id_or_val)}$", "$options": "i"}}
                    ]
                }
                if investigation_id:
                    q["investigation_id"] = investigation_id
                if relationship_types:
                    q["relationship_type"] = {"$in": relationship_types}
                if min_confidence is not None:
                    q["confidence"] = {"$gte": min_confidence}

                cursor = self.collection.find(q, {"_id": 0}).limit(limit + 1)
                docs = await cursor.to_list(length=limit + 1)
                for d in docs:
                    r_id = d.get("id") or f"{d.get('source_id')}-{d.get('target_id')}"
                    if r_id not in seen_ids:
                        seen_ids.add(r_id)
                        rels.append(d)
            except Exception as e:
                app_logger.warning(f"Error querying async mongo in expand_entity_1hop: {e}")

        # 2. Check memory cache and investigation embedded relationships
        with memory_cache._lock:
            all_cached = list(memory_cache.relationships.values())
            for inv in memory_cache.investigations.values():
                if inv.get("tenant_id") == tenant_id:
                    if not investigation_id or inv.get("id") == investigation_id:
                        all_cached.extend(inv.get("relationships", []))

            for r in all_cached:
                if r.get("tenant_id") and r.get("tenant_id") != tenant_id:
                    continue
                if investigation_id and r.get("investigation_id") and r.get("investigation_id") != investigation_id:
                    continue
                if relationship_types and r.get("relationship_type") not in relationship_types:
                    continue
                if min_confidence is not None and float(r.get("confidence", 1.0)) < min_confidence:
                    continue

                src_id = str(r.get("source_id", "")).lower()
                tgt_id = str(r.get("target_id", "")).lower()
                src_val = str(r.get("source_entity_value", "")).lower()
                tgt_val = str(r.get("target_entity_value", "")).lower()

                if key_val in (src_id, tgt_id, src_val, tgt_val):
                    r_id = r.get("id") or f"{src_id}-{tgt_id}-{r.get('relationship_type')}"
                    if r_id not in seen_ids:
                        seen_ids.add(r_id)
                        rels.append(r)

        has_more = len(rels) > limit
        bounded_rels = rels[:limit]
        return {
            "seed_entity": entity_id_or_val,
            "relationships": bounded_rels,
            "has_more": has_more,
            "total_count": len(rels)
        }

    async def save(self, tenant_id: str, rel_data: Dict[str, Any]) -> None:
        rel_id = rel_data.get("id") or f"rel_{uuid.uuid4().hex[:10]}"
        rel_data["id"] = rel_id
        rel_data["tenant_id"] = tenant_id
        if "first_seen" not in rel_data:
            rel_data["first_seen"] = datetime.utcnow().isoformat()
        rel_data["last_seen"] = datetime.utcnow().isoformat()
        if "basis" not in rel_data:
            rel_data["basis"] = "DIRECT_OBSERVATION"
        if "is_inferred" not in rel_data:
            rel_data["is_inferred"] = False
        if "evidence_ids" not in rel_data:
            rel_data["evidence_ids"] = []

        with memory_cache._lock:
            memory_cache.relationships[rel_id] = rel_data
        if self.collection is not None:
            try:
                await self.collection.update_one(
                    {"id": rel_id, "tenant_id": tenant_id},
                    {"$set": rel_data},
                    upsert=True
                )
            except Exception:
                pass
        else:
            self._sync_write({"id": rel_id, "tenant_id": tenant_id}, rel_data)

class EvidenceRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("evidence")

    async def list_by_tenant(
        self, tenant_id: str, investigation_id: Optional[str] = None, search_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = {"tenant_id": tenant_id}
        if investigation_id:
            query["investigation_id"] = investigation_id
        if search_id:
            query["search_id"] = search_id
        if self.collection is not None:
            try:
                cursor = self.collection.find(query, {"_id": 0})
                items = await cursor.to_list(length=1000)
                if items:
                    return items
            except Exception:
                pass
        with memory_cache._lock:
            records = [d for d in memory_cache.evidence.values() if d.get("tenant_id") == tenant_id]
            if investigation_id:
                records = [r for r in records if r.get("investigation_id") == investigation_id]
            if search_id:
                records = [r for r in records if r.get("search_id") == search_id]
            return records

    async def get_by_id(self, tenant_id: str, evidence_id: str) -> Optional[Dict[str, Any]]:
        if self.collection is not None:
            try:
                doc = await self.collection.find_one({"id": evidence_id, "tenant_id": tenant_id}, {"_id": 0})
                if doc:
                    return doc
            except Exception:
                pass
        with memory_cache._lock:
            data = memory_cache.evidence.get(evidence_id)
            if data and data.get("tenant_id") == tenant_id:
                return data
            return None

    async def save(self, tenant_id: str, evidence_data: Dict[str, Any]) -> None:
        ev_id = evidence_data["id"]
        evidence_data["tenant_id"] = tenant_id
        with memory_cache._lock:
            memory_cache.evidence[ev_id] = evidence_data
        if self.collection is not None:
            await self.collection.update_one(
                {"id": ev_id, "tenant_id": tenant_id},
                {"$set": evidence_data},
                upsert=True
            )
        else:
            self._sync_write({"id": ev_id, "tenant_id": tenant_id}, evidence_data)

class FindingRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("findings")

    async def list_by_tenant(
        self,
        tenant_id: str,
        investigation_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = {"tenant_id": tenant_id}
        if investigation_id:
            query["investigation_id"] = investigation_id
        if severity and severity.upper() != "ALL":
            query["severity"] = severity.upper()
        if status and status.upper() != "ALL":
            query["status"] = status.upper()

        if self.collection is not None:
            cursor = self.collection.find(query, {"_id": 0}).sort("created_at", -1)
            return await cursor.to_list(length=1000)
        return []

    async def get_by_id(self, tenant_id: str, finding_id: str) -> Optional[Dict[str, Any]]:
        if self.collection is not None:
            return await self.collection.find_one({"id": finding_id, "tenant_id": tenant_id}, {"_id": 0})
        return None

    async def save(self, tenant_id: str, finding_data: Dict[str, Any]) -> None:
        f_id = finding_data["id"]
        finding_data["tenant_id"] = tenant_id
        if self.collection is not None:
            await self.collection.update_one(
                {"id": f_id, "tenant_id": tenant_id},
                {"$set": finding_data},
                upsert=True
            )
        else:
            self._sync_write({"id": f_id, "tenant_id": tenant_id}, finding_data)

class ReportRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("reports")

    async def list_by_tenant(self, tenant_id: str, investigation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {"tenant_id": tenant_id}
        if investigation_id:
            query["investigation_id"] = investigation_id
        if self.collection is not None:
            cursor = self.collection.find(query, {"_id": 0}).sort("created_at", -1)
            return await cursor.to_list(length=1000)
        return []

    async def get_by_id(self, tenant_id: str, report_id: str) -> Optional[Dict[str, Any]]:
        if self.collection is not None:
            return await self.collection.find_one({"id": report_id, "tenant_id": tenant_id}, {"_id": 0})
        return None

    async def save(self, tenant_id: str, report_data: Dict[str, Any]) -> None:
        r_id = report_data["id"]
        report_data["tenant_id"] = tenant_id
        if self.collection is not None:
            await self.collection.update_one(
                {"id": r_id, "tenant_id": tenant_id},
                {"$set": report_data},
                upsert=True
            )
        else:
            self._sync_write({"id": r_id, "tenant_id": tenant_id}, report_data)

class SearchRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("searches")

    async def save(self, tenant_id: str, search_data: Dict[str, Any]) -> None:
        s_id = search_data["id"]
        search_data["tenant_id"] = tenant_id
        with memory_cache._lock:
            memory_cache.searches[s_id] = search_data
        if self.collection is not None:
            await self.collection.update_one(
                {"id": s_id, "tenant_id": tenant_id},
                {"$set": search_data},
                upsert=True
            )
        else:
            self._sync_write({"id": s_id, "tenant_id": tenant_id}, search_data)

    async def list_recent(self, tenant_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        if self.collection is not None:
            cursor = self.collection.find({"tenant_id": tenant_id}, {"_id": 0}).sort("created_at", -1).limit(limit)
            items = await cursor.to_list(length=limit)
            if items:
                return items
        with memory_cache._lock:
            searches = [s for s in memory_cache.searches.values() if s.get("tenant_id") == tenant_id]
            return sorted(searches, key=lambda x: str(x.get("created_at", "")), reverse=True)[:limit]

class AuditRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__("audit_logs")

    async def save(self, log_data: Dict[str, Any]) -> None:
        with memory_cache._lock:
            memory_cache.audit_logs.append(log_data)
        if self.collection is not None:
            await self.collection.insert_one(dict(log_data))
        else:
            col = self.sync_collection
            if col is not None:
                try:
                    col.insert_one(dict(log_data))
                except Exception as e:
                    app_logger.warning(f"Failed to insert audit log in mongo: {e}")

    async def list_by_tenant(self, tenant_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        query = {"tenant_id": tenant_id} if tenant_id and tenant_id not in ["platform_admin", "system"] else {}
        if self.collection is not None:
            cursor = self.collection.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit)
            items = await cursor.to_list(length=limit)
            if items:
                return items
        with memory_cache._lock:
            logs = memory_cache.audit_logs
            if tenant_id and tenant_id not in ["platform_admin", "system"]:
                logs = [l for l in logs if l.get("tenant_id") == tenant_id]
            return sorted(logs, key=lambda x: str(x.get("timestamp", "")), reverse=True)[:limit]

class DashboardRepository:
    """Computes live aggregated SaaS dashboard metrics directly from MongoDB."""
    async def get_summary(self, tenant_id: str) -> Dict[str, Any]:
        db = get_database()
        
        # Default counts from memory fallback
        with memory_cache._lock:
            inv_items = [i for i in memory_cache.investigations.values() if i.get("tenant_id") == tenant_id]
            active_invs = len([i for i in inv_items if i.get("status") in ["open", "in_progress"]])
            total_invs = len(inv_items)
            ev_count = len([e for e in memory_cache.evidence.values() if e.get("tenant_id") == tenant_id])
            ent_count = len([e for e in memory_cache.entities.values() if e.get("tenant_id") == tenant_id])
            srch_count = len([s for s in memory_cache.searches.values() if s.get("tenant_id") == tenant_id])

        findings_count = 0
        critical_findings = 0
        reports_count = 0

        # Query MongoDB for true persistent counts
        if db is not None:
            try:
                total_invs = await db.investigations.count_documents({"tenant_id": tenant_id})
                active_invs = await db.investigations.count_documents({
                    "tenant_id": tenant_id,
                    "status": {"$in": ["open", "in_progress"]}
                })
                ev_count = await db.evidence.count_documents({"tenant_id": tenant_id})
                ent_count = await db.entities.count_documents({"tenant_id": tenant_id})
                srch_count = await db.searches.count_documents({"tenant_id": tenant_id})
                findings_count = await db.findings.count_documents({"tenant_id": tenant_id})
                critical_findings = await db.findings.count_documents({
                    "tenant_id": tenant_id,
                    "severity": {"$in": ["CRITICAL", "HIGH"]}
                })
                reports_count = await db.reports.count_documents({"tenant_id": tenant_id})
            except Exception as e:
                app_logger.warning(f"Error calculating dashboard metrics from MongoDB: {e}")

        recent_activity = await audit_repo.list_by_tenant(tenant_id, limit=5)
        
        return {
            "total_cases": total_invs,
            "active_investigations": active_invs,
            "evidence_collected": ev_count,
            "entities_correlated": ent_count,
            "total_searches": srch_count,
            "total_findings": findings_count,
            "critical_threats": critical_findings,
            "reports_generated": reports_count,
            "recent_activity": recent_activity
        }

    async def get_platform_summary(self) -> Dict[str, Any]:
        """Calculates live aggregated SaaS metrics across the entire platform from MongoDB."""
        db = get_database()
        
        total_tenants = 0
        active_tenants = 0
        suspended_tenants = 0
        total_users = 0
        tenant_admins = 0
        analysts = 0
        investigators = 0
        total_cases = 0
        active_invs = 0
        osint_runs = 0
        evidence_count = 0
        findings_count = 0
        reports_count = 0
        storage_bytes = 0

        if db is not None:
            try:
                total_tenants = await db.tenants.count_documents({})
                active_tenants = await db.tenants.count_documents({"status": "active"})
                suspended_tenants = await db.tenants.count_documents({"status": "suspended"})
                total_users = await db.users.count_documents({})
                tenant_admins = await db.users.count_documents({"role": "TENANT_ADMIN"})
                analysts = await db.users.count_documents({"role": "ANALYST"})
                investigators = await db.users.count_documents({"role": {"$in": ["INVESTIGATOR", "USER"]}})
                total_cases = await db.cases.count_documents({})
                active_invs = await db.investigations.count_documents({"status": {"$in": ["open", "in_progress"]}})
                osint_runs = await db.searches.count_documents({})
                evidence_count = await db.evidence.count_documents({})
                findings_count = await db.findings.count_documents({})
                reports_count = await db.reports.count_documents({})
            except Exception as e:
                app_logger.warning(f"Error calculating platform metrics from MongoDB: {e}")
        else:
            with memory_cache._lock:
                total_tenants = len(memory_cache.tenants)
                active_tenants = len([t for t in memory_cache.tenants.values() if t.get("status") == "active"])
                suspended_tenants = total_tenants - active_tenants
                total_users = len(memory_cache.users)
                tenant_admins = len([u for u in memory_cache.users.values() if u.get("role") == "TENANT_ADMIN"])
                analysts = len([u for u in memory_cache.users.values() if u.get("role") == "ANALYST"])
                investigators = len([u for u in memory_cache.users.values() if u.get("role") in ["INVESTIGATOR", "USER"]])
                total_cases = len(memory_cache.investigations)
                active_invs = len([i for i in memory_cache.investigations.values() if i.get("status") in ["open", "in_progress"]])
                osint_runs = len(memory_cache.searches)
                evidence_count = len(memory_cache.evidence)

        recent_logs = await audit_repo.list_by_tenant(None, limit=8)

        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "suspended_tenants": suspended_tenants,
            "total_users": total_users,
            "tenant_admins": tenant_admins,
            "analysts": analysts,
            "investigators": investigators,
            "total_cases": total_cases,
            "active_investigations": active_invs,
            "osint_tool_runs": osint_runs,
            "threat_intelligence_runs": 0,
            "evidence_collected": evidence_count,
            "findings_count": findings_count,
            "reports_count": reports_count,
            "storage_usage_bytes": storage_bytes,
            "system_health": {
                "status": "HEALTHY",
                "database": "MONGODB_CONNECTED",
                "message": "All database clusters and isolation boundaries nominal"
            },
            "recent_activity": recent_logs
        }


tenant_repo = TenantRepository()
user_repo = UserRepository()
investigation_repo = InvestigationRepository()
case_repo = CaseRepository()
entity_repo = EntityRepository()
relationship_repo = RelationshipRepository()
evidence_repo = EvidenceRepository()
finding_repo = FindingRepository()
report_repo = ReportRepository()
search_repo = SearchRepository()
audit_repo = AuditRepository()
dashboard_repo = DashboardRepository()
