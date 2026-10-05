import hashlib
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from app.module_sdk.models import (
    EntityPayload, EntityType, EvidencePayload,
    RelationshipPayload, RelationshipType, NormalizedModuleResult
)

class ModuleSDK:
    """Internal SDK providing utilities for module developers."""
    
    @staticmethod
    def calculate_evidence_hash(raw_data: Any) -> str:
        """Calculates a deterministic SHA-256 hash for raw evidence to ensure cryptographic integrity."""
        if isinstance(raw_data, (dict, list)):
            serialized = json.dumps(raw_data, sort_keys=True, default=str)
        else:
            serialized = str(raw_data)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def create_entity(
        entity_type: EntityType,
        value: str,
        confidence: float = 1.0,
        sources: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EntityPayload:
        return EntityPayload(
            type=entity_type,
            value=value.strip(),
            confidence=max(0.0, min(1.0, confidence)),
            sources=sources or [],
            metadata=metadata or {}
        )

    @staticmethod
    def create_relationship(
        source_val: str,
        target_val: str,
        rel_type: RelationshipType,
        confidence: float = 1.0,
        sources: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RelationshipPayload:
        return RelationshipPayload(
            source_entity_value=source_val.strip(),
            target_entity_value=target_val.strip(),
            relationship_type=rel_type,
            confidence=max(0.0, min(1.0, confidence)),
            sources=sources or [],
            metadata=metadata or {}
        )

    @staticmethod
    def create_evidence(
        source: str,
        provider: str,
        module: str,
        raw_data: Any,
        reference: str = "",
        confidence: float = 1.0,
        collection_method: str = "automated"
    ) -> EvidencePayload:
        ev_hash = ModuleSDK.calculate_evidence_hash(raw_data)
        return EvidencePayload(
            source=source,
            provider=provider,
            module=module,
            raw_data=raw_data,
            reference=reference,
            confidence=confidence,
            collection_method=collection_method,
            hash=ev_hash,
            timestamp=datetime.utcnow()
        )
