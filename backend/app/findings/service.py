import uuid
from typing import List, Optional, Dict
from datetime import datetime
from app.findings.models import FindingRecord, FindingCreate, FindingUpdate
from app.infrastructure.mongodb.repositories import finding_repo

class FindingService:
    def __init__(self):
        # tenant_id -> Dict[finding_id, FindingRecord]
        self._memory_store: Dict[str, Dict[str, FindingRecord]] = {}

    def _get_tenant_store(self, tenant_id: str) -> Dict[str, FindingRecord]:
        if tenant_id not in self._memory_store:
            self._memory_store[tenant_id] = {}
        return self._memory_store[tenant_id]

    def create_finding(self, tenant_id: str, data: FindingCreate) -> FindingRecord:
        finding_id = f"fnd_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()
        
        record = FindingRecord(
            id=finding_id,
            tenant_id=tenant_id,
            investigation_id=data.investigation_id,
            search_id=data.search_id,
            title=data.title,
            description=data.description,
            type=data.type,
            severity=data.severity,
            confidence=data.confidence,
            module_id=data.module_id,
            provider_id=data.provider_id,
            source=data.source or (data.provider_id or "OSINT Engine"),
            status=data.status,
            mitigation=data.mitigation,
            entity_ids=data.entity_ids,
            evidence_ids=data.evidence_ids,
            observed_at=now,
            created_at=now,
            metadata=data.metadata
        )
        
        r_dict = record.dict()
        store = self._get_tenant_store(tenant_id)
        store[finding_id] = record
        finding_repo._sync_write({"id": finding_id, "tenant_id": tenant_id}, r_dict)
        return record

    def list_findings(
        self,
        tenant_id: str,
        investigation_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[FindingRecord]:
        col = finding_repo.sync_collection
        if col is not None:
            q: Dict[str, Any] = {"tenant_id": tenant_id}
            if investigation_id:
                q["investigation_id"] = investigation_id
            if severity and severity != 'ALL':
                q["severity"] = severity.upper()
            if status and status != 'ALL':
                q["status"] = status.upper()
            try:
                docs = list(col.find(q, {"_id": 0}).sort("created_at", -1))
                if docs:
                    # Sync to memory store
                    store = self._get_tenant_store(tenant_id)
                    for d in docs:
                        store[d["id"]] = FindingRecord(**d)
                    if search:
                        s_lower = search.lower()
                        docs = [
                            d for d in docs
                            if s_lower in d.get("title", "").lower() or s_lower in d.get("description", "").lower() or s_lower in d.get("source", "").lower()
                        ]
                    return [FindingRecord(**d) for d in docs]
            except Exception:
                pass

        store = self._get_tenant_store(tenant_id)
        results = list(store.values())
        
        if investigation_id:
            results = [f for f in results if f.investigation_id == investigation_id]
        if severity and severity != 'ALL':
            results = [f for f in results if f.severity.upper() == severity.upper()]
        if status and status != 'ALL':
            results = [f for f in results if f.status.upper() == status.upper()]
        if search:
            q = search.lower()
            results = [
                f for f in results
                if q in f.title.lower() or q in f.description.lower() or q in f.source.lower()
            ]
            
        results.sort(key=lambda x: x.created_at, reverse=True)
        return results

    def get_finding(self, tenant_id: str, finding_id: str) -> Optional[FindingRecord]:
        store = self._get_tenant_store(tenant_id)
        if finding_id in store:
            return store[finding_id]
        col = finding_repo.sync_collection
        if col is not None:
            doc = col.find_one({"id": finding_id, "tenant_id": tenant_id}, {"_id": 0})
            if doc:
                rec = FindingRecord(**doc)
                store[finding_id] = rec
                return rec
        return None

    def update_finding(self, tenant_id: str, finding_id: str, update: FindingUpdate) -> Optional[FindingRecord]:
        store = self._get_tenant_store(tenant_id)
        fnd = self.get_finding(tenant_id, finding_id)
        if not fnd:
            return None
            
        updated_dict = fnd.dict()
        if update.title is not None:
            updated_dict["title"] = update.title
        if update.description is not None:
            updated_dict["description"] = update.description
        if update.severity is not None:
            updated_dict["severity"] = update.severity
        if update.confidence is not None:
            updated_dict["confidence"] = update.confidence
        if update.status is not None:
            updated_dict["status"] = update.status
        if update.mitigation is not None:
            updated_dict["mitigation"] = update.mitigation
            
        updated_record = FindingRecord(**updated_dict)
        store[finding_id] = updated_record
        finding_repo._sync_write({"id": finding_id, "tenant_id": tenant_id}, updated_dict)
        return updated_record

finding_service = FindingService()
