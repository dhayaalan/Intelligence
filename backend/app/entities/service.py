from typing import List, Optional
import uuid
from datetime import datetime
from app.core.database import db
from app.entities.models import EntityRecord
from app.module_sdk.models import EntityPayload, EntityType
from app.infrastructure.mongodb.repositories import entity_repo, investigation_repo

class EntityService:
    @staticmethod
    def upsert_entity(tenant_id: str, payload: EntityPayload, investigation_id: Optional[str] = None) -> EntityRecord:
        clean_val = payload.value.strip()
        type_str = payload.type.value if hasattr(payload.type, "value") else str(payload.type).lower()
        with db._lock:
            # Check for existing entity with same type, value, tenant
            for ent_id, data in db.entities.items():
                existing_type = data.get("type")
                existing_type_str = existing_type.value if hasattr(existing_type, "value") else str(existing_type).lower()
                if (data.get("tenant_id") == tenant_id and
                    existing_type_str == type_str and
                    data.get("value", "").lower() == clean_val.lower()):
                    
                    if investigation_id and not data.get("investigation_id"):
                        data["investigation_id"] = investigation_id

                    # Merge sources
                    existing_sources = set(data.get("sources", []))
                    existing_sources.update(payload.sources)
                    data["sources"] = list(existing_sources)
                    
                    # Update confidence if higher
                    data["confidence"] = max(data.get("confidence", 0.0), payload.confidence)
                    
                    # Merge metadata
                    meta = data.get("metadata", {})
                    meta.update(payload.metadata)
                    data["metadata"] = meta
                    data["last_seen"] = datetime.utcnow()
                    
                    entity_repo._sync_write({"id": ent_id, "tenant_id": tenant_id}, data)
                    return EntityRecord(**data)
                    
            # Create new entity record
            ent_id = payload.id or f"ent_{uuid.uuid4().hex[:12]}"
            record = EntityRecord(
                id=ent_id,
                tenant_id=tenant_id,
                investigation_id=investigation_id,
                type=payload.type,
                value=clean_val,
                confidence=payload.confidence,
                sources=payload.sources,
                metadata=payload.metadata,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow()
            )
            r_dict = record.dict()
            db.entities[ent_id] = r_dict
            entity_repo._sync_write({"id": ent_id, "tenant_id": tenant_id}, r_dict)
            return record

    @staticmethod
    def _hydrate_investigation_entities(tenant_id: str, investigation_id: Optional[str] = None):
        if not investigation_id:
            return
        if investigation_id not in db.investigations:
            inv_col = investigation_repo.sync_collection
            if inv_col is not None:
                try:
                    doc = inv_col.find_one({"id": investigation_id, "tenant_id": tenant_id}, {"_id": 0})
                    if doc:
                        db.investigations[investigation_id] = doc
                except Exception:
                    pass

        inv_data = db.investigations.get(investigation_id, {})
        linked_ids = set(inv_data.get("entity_ids", []))
        ent_col = entity_repo.sync_collection
        if ent_col is not None:
            try:
                q = {"tenant_id": tenant_id}
                if linked_ids:
                    q = {"tenant_id": tenant_id, "$or": [{"investigation_id": investigation_id}, {"id": {"$in": list(linked_ids)}}]}
                else:
                    q = {"tenant_id": tenant_id, "investigation_id": investigation_id}
                for edoc in ent_col.find(q, {"_id": 0}):
                    if edoc.get("id"):
                        db.entities[edoc["id"]] = edoc
            except Exception:
                pass

    @staticmethod
    def list_entities(tenant_id: str, investigation_id: Optional[str] = None) -> List[EntityRecord]:
        with db._lock:
            if investigation_id:
                EntityService._hydrate_investigation_entities(tenant_id, investigation_id)
            records = [EntityRecord(**d) for d in db.entities.values() if d.get("tenant_id") == tenant_id]
            if investigation_id:
                inv_data = db.investigations.get(investigation_id, {})
                linked_ids = set(inv_data.get("entity_ids", []))
                records = [r for r in records if r.investigation_id == investigation_id or r.id in linked_ids]
            return records

    @staticmethod
    def list_entities_paginated(
        tenant_id: str,
        investigation_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        type: Optional[str] = None
    ) -> dict:
        with db._lock:
            if investigation_id:
                EntityService._hydrate_investigation_entities(tenant_id, investigation_id)
            records = [EntityRecord(**d) for d in db.entities.values() if d.get("tenant_id") == tenant_id]
            if investigation_id:
                inv_data = db.investigations.get(investigation_id, {})
                linked_ids = set(inv_data.get("entity_ids", []))
                records = [r for r in records if r.investigation_id == investigation_id or r.id in linked_ids]
            if type and type.upper() != 'ALL':
                records = [r for r in records if r.type.value.upper() == type.upper() or r.type.upper() == type.upper()]
            if search:
                s = search.lower()
                records = [r for r in records if s in r.value.lower()]
            total = len(records)
            skip = (page - 1) * page_size
            paged = records[skip : skip + page_size]
            total_pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 1
            return {
                "items": paged,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }

    @staticmethod
    def get_entity(tenant_id: str, entity_id: str) -> Optional[EntityRecord]:
        with db._lock:
            data = db.entities.get(entity_id)
            if data and data.get("tenant_id") == tenant_id:
                return EntityRecord(**data)
        col = entity_repo.sync_collection
        if col is not None:
            doc = col.find_one({"id": entity_id, "tenant_id": tenant_id}, {"_id": 0})
            if doc:
                with db._lock:
                    db.entities[entity_id] = doc
                return EntityRecord(**doc)
        return None

entity_service = EntityService()
