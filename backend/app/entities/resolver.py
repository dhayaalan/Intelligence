import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

from app.core.database import db
from app.entities.models import EntityRecord
from app.module_sdk.models import EntityType


class CanonicalEntity(BaseModel):
    canonical_id: str
    tenant_id: str
    type: EntityType
    canonical_value: str
    aliases: List[str] = Field(default_factory=list)
    linked_investigation_ids: List[str] = Field(default_factory=list)
    linked_entity_ids: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    modules_observed: List[str] = Field(default_factory=list)
    confidence_score: float = 1.0
    first_seen: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    multi_hop_neighbors: List[Dict[str, Any]] = Field(default_factory=list)
    cross_case_count: int = 1


class CrossModuleCorrelationResponse(BaseModel):
    tenant_id: str
    total_canonical_entities: int
    cross_case_correlations_count: int
    entities: List[CanonicalEntity]
    multi_hop_graph_edges: List[Dict[str, Any]] = Field(default_factory=list)


class EntityDisambiguationService:
    """
    Unified Cross-Module Entity Resolution & Disambiguation Service (CORR-01).
    Performs deterministic observable canonicalization and multi-hop correlation
    across OSINT, Threat Intelligence, Social Media, and News investigations
    while strictly preserving multi-tenant isolation boundaries.
    """

    @staticmethod
    def normalize_observable(entity_type: EntityType, value: str) -> str:
        """Deterministically canonicalizes observables according to standard RFC / conventions."""
        clean = (value or "").strip()
        type_str = entity_type.value if hasattr(entity_type, "value") else str(entity_type).lower()

        if type_str in ["domain", "url"]:
            # Strip scheme, www, and query/path
            clean = re.sub(r'^https?://', '', clean, flags=re.IGNORECASE)
            clean = re.sub(r'^www\.', '', clean, flags=re.IGNORECASE)
            clean = clean.split('/')[0].split('?')[0].split(':')[0]
            return clean.lower()

        elif type_str in ["ip", "ip_address", "ipv4", "ipv6"]:
            return clean.lower().split('/')[0]

        elif type_str in ["email"]:
            return clean.lower()

        elif type_str in ["username", "handle"]:
            return clean.lstrip('@').lower()

        elif type_str in ["cve", "vulnerability"]:
            return clean.upper()

        elif type_str in ["hash", "md5", "sha1", "sha256"]:
            return clean.lower()

        return clean.lower()

    @staticmethod
    def detect_module_origin(source: str) -> str:
        s = source.lower()
        if any(k in s for k in ["shodan", "whois", "dns", "subdomain", "crt.sh", "harvester", "osint"]):
            return "osint"
        if any(k in s for k in ["cve", "nvd", "epss", "kev", "threat", "cisa", "advisory", "vuln"]):
            return "threat_intelligence"
        if any(k in s for k in ["bluesky", "telegram", "reddit", "mastodon", "youtube", "social", "cib"]):
            return "social_media_intelligence"
        if any(k in s for k in ["wire", "news", "reuters", "article", "claim", "disinfolab", "press"]):
            return "news_intelligence"
        return "general"

    def correlate_entities(
        self,
        tenant_id: str,
        investigation_ids: Optional[List[str]] = None
    ) -> CrossModuleCorrelationResponse:
        """
        Scans all entity records for the tenant, groups identical canonical observables,
        links multi-investigation appearances, and extracts cross-module graph relationships.
        """
        with db._lock:
            raw_entities = [
                EntityRecord(**d) for d in db.entities.values()
                if d.get("tenant_id") == tenant_id
            ]

        if investigation_ids:
            inv_filter = set(investigation_ids)
            raw_entities = [
                e for e in raw_entities
                if e.investigation_id and e.investigation_id in inv_filter
            ]

        # Grouping by (type, canonical_value)
        grouped: Dict[str, List[EntityRecord]] = {}
        for ent in raw_entities:
            canon = self.normalize_observable(ent.type, ent.value)
            type_str = ent.type.value if hasattr(ent.type, "value") else str(ent.type)
            key = f"{type_str}:{canon}"
            grouped.setdefault(key, []).append(ent)

        canonical_entities: List[CanonicalEntity] = []
        cross_case_count = 0

        for key, records in grouped.items():
            primary = records[0]
            type_val = primary.type
            canon_val = self.normalize_observable(type_val, primary.value)

            # Aggregate investigation links
            inv_ids = sorted(list({r.investigation_id for r in records if r.investigation_id}))
            entity_ids = [r.id for r in records]
            aliases = sorted(list({r.value for r in records if r.value != canon_val}))

            # Aggregate sources and module origins
            sources_set: Set[str] = set()
            modules_set: Set[str] = set()
            for r in records:
                for s in r.sources:
                    sources_set.add(s)
                    modules_set.add(self.detect_module_origin(s))

            # Timestamps
            first_seen_dt = min(r.first_seen for r in records)
            last_seen_dt = max(r.last_seen for r in records)
            confidence = max(r.confidence for r in records)

            num_cases = len(inv_ids)
            if num_cases > 1:
                cross_case_count += 1

            canon_id = f"canon_{type_val.value if hasattr(type_val, 'value') else str(type_val)[:3]}_{canon_val.replace('.', '_')[:16]}"

            canonical_entities.append(CanonicalEntity(
                canonical_id=canon_id,
                tenant_id=tenant_id,
                type=type_val,
                canonical_value=canon_val,
                aliases=aliases,
                linked_investigation_ids=inv_ids,
                linked_entity_ids=entity_ids,
                sources=sorted(list(sources_set)),
                modules_observed=sorted(list(modules_set)) or ["osint"],
                confidence_score=round(confidence, 2),
                first_seen=first_seen_dt.isoformat(),
                last_seen=last_seen_dt.isoformat(),
                cross_case_count=num_cases,
            ))

        # Build multi-hop graph edges from verified stored relationships
        multi_hop_edges: List[Dict[str, Any]] = []
        canon_by_val: Dict[str, CanonicalEntity] = {}
        for ce in canonical_entities:
            canon_by_val[ce.canonical_value.lower()] = ce
            for alias in ce.aliases:
                canon_by_val[alias.lower()] = ce

        seen_edges: Set[str] = set()
        
        # Read verified relationships from database
        with db._lock:
            stored_rels = [
                r for r in db.relationships.values()
                if r.get("tenant_id") == tenant_id
            ]
            for inv in db.investigations.values():
                if inv.get("tenant_id") == tenant_id:
                    stored_rels.extend(inv.get("relationships", []))

        for rel in stored_rels:
            src_val = (rel.get("source_entity_value") or rel.get("source_id") or "").lower().strip()
            dst_val = (rel.get("target_entity_value") or rel.get("target_id") or "").lower().strip()
            src_ce = canon_by_val.get(src_val)
            dst_ce = canon_by_val.get(dst_val)
            if src_ce and dst_ce and src_ce.canonical_id != dst_ce.canonical_id:
                edge_key = f"{src_ce.canonical_id}->{dst_ce.canonical_id}"
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    rel_type = rel.get("relationship_type") or rel.get("type") or "CONNECTED_TO"
                    rel_type_str = rel_type.value if hasattr(rel_type, "value") else str(rel_type)
                    multi_hop_edges.append({
                        "id": rel.get("id") or f"edge_{src_ce.canonical_id}_{dst_ce.canonical_id}",
                        "source_canonical_id": src_ce.canonical_id,
                        "target_canonical_id": dst_ce.canonical_id,
                        "source_value": src_ce.canonical_value,
                        "target_value": dst_ce.canonical_value,
                        "relationship": rel_type_str,
                        "investigation_id": rel.get("investigation_id"),
                        "basis": rel.get("basis") or (rel.get("metadata") or {}).get("basis") or "DIRECT_OBSERVATION",
                        "is_inferred": bool(rel.get("is_inferred", False)),
                        "evidence_ids": rel.get("evidence_ids") or [],
                        "confidence": float(rel.get("confidence", 0.9)),
                        "weight": float(rel.get("confidence", 1.0)),
                    })

        return CrossModuleCorrelationResponse(
            tenant_id=tenant_id,
            total_canonical_entities=len(canonical_entities),
            cross_case_correlations_count=cross_case_count,
            entities=canonical_entities,
            multi_hop_graph_edges=multi_hop_edges[:100],
        )

    def resolve_observable(
        self,
        tenant_id: str,
        value: str,
        entity_type: Optional[EntityType] = None
    ) -> Optional[CanonicalEntity]:
        """Resolves an observable value to its canonical record within tenant boundary."""
        resp = self.correlate_entities(tenant_id)
        raw_val = value.strip().lower()
        for ce in resp.entities:
            norm_target = self.normalize_observable(ce.type, value)
            if (ce.canonical_value == norm_target or
                ce.canonical_value == raw_val or
                any(a.lower() == raw_val or a.lower() == norm_target for a in ce.aliases)):
                if entity_type is None or ce.type == entity_type:
                    return ce
        return None


entity_disambiguation_service = EntityDisambiguationService()
