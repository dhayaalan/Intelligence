from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.infrastructure.mongodb.repositories import (
    relationship_repo, entity_repo, evidence_repo, investigation_repo
)
from app.core.database import db

router = APIRouter(prefix="/graph", tags=["Relationship Graph Intelligence"])

class GraphExpandRequest(BaseModel):
    seed_node_ids: Optional[List[str]] = None
    entity_id: Optional[str] = None
    investigation_id: Optional[str] = None
    visible_node_ids: List[str] = Field(default_factory=list)
    visible_entity_ids: List[str] = Field(default_factory=list)
    visible_relationship_ids: List[str] = Field(default_factory=list)
    limit: int = Field(default=25, ge=1, le=100)
    relationship_types: Optional[List[str]] = None
    min_confidence: Optional[float] = None

class GraphExpandResponse(BaseModel):
    seed_node_ids: List[str]
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    new_nodes: List[Dict[str, Any]] = Field(default_factory=list)
    shared_nodes: List[Dict[str, Any]] = Field(default_factory=list)
    new_edges: List[Dict[str, Any]] = Field(default_factory=list)
    has_more: bool = False
    total_edges: int = 0

@router.get("/expand", response_model=Dict[str, Any])
async def expand_entity_1hop(
    entity_id: str = Query(..., description="Entity ID or value to expand"),
    investigation_id: Optional[str] = Query(None, description="Scope traversal to an investigation"),
    limit: int = Query(25, ge=1, le=50, description="Max relationships to return per hop"),
    relationship_types: Optional[List[str]] = Query(None, description="Filter by relationship types"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence threshold"),
    current_user: UserRecord = Depends(get_current_user)
):
    """
    State-aware 1-hop relationship expansion for an entity.
    Returns connected entities and verified typed edges while strictly enforcing tenant boundaries.
    """
    tenant_id = current_user.tenant_id

    # 1. Try Neo4j graph traversal first
    try:
        from app.infrastructure.neo4j.service import neo4j_graph_service
        neo4j_res = await neo4j_graph_service.expand_entity_1hop(
            tenant_id=tenant_id,
            entity_id_or_val=entity_id,
            limit=limit,
            relationship_types=relationship_types,
            min_confidence=min_confidence,
            investigation_id=investigation_id
        )
        if neo4j_res and neo4j_res.get("edges"):
            # Enrich nodes with MongoDB entity records for full metadata
            all_ents = await entity_repo.list_by_tenant(tenant_id, investigation_id=investigation_id)
            ent_lookup = {str(e.get("id", "")).lower(): e for e in all_ents}
            ent_lookup.update({str(e.get("value", "")).lower(): e for e in all_ents})

            enriched_nodes = []
            for n in neo4j_res["nodes"]:
                nid = str(n.get("id", "")).lower()
                nval = str(n.get("value", "")).lower()
                doc = ent_lookup.get(nid) or ent_lookup.get(nval)
                if doc:
                    merged = dict(doc)
                    merged.update(n)
                    enriched_nodes.append(merged)
                else:
                    enriched_nodes.append(n)
            neo4j_res["nodes"] = enriched_nodes
            return neo4j_res
    except Exception as e:
        from app.core.logging import app_logger
        app_logger.warning(f"Neo4j 1-hop traversal exception: {e}")

    # 2. Fallback to MongoDB / memory repository
    expansion = await relationship_repo.expand_entity_1hop(
        tenant_id=tenant_id,
        entity_id_or_val=entity_id,
        investigation_id=investigation_id,
        limit=limit,
        relationship_types=relationship_types,
        min_confidence=min_confidence
    )

    rels = expansion.get("relationships", [])
    
    # 2. Collect connected entity IDs / values
    connected_vals = set()
    for r in rels:
        src = r.get("source_id") or r.get("source_entity_value")
        tgt = r.get("target_id") or r.get("target_entity_value")
        if src and str(src).lower() != entity_id.lower():
            connected_vals.add(str(src))
        if tgt and str(tgt).lower() != entity_id.lower():
            connected_vals.add(str(tgt))

    # 3. Resolve connected entity objects from store
    connected_nodes: List[Dict[str, Any]] = []
    seen_nodes = set()
    all_ents = await entity_repo.list_by_tenant(tenant_id, investigation_id=investigation_id)
    ent_lookup = {}
    for e in all_ents:
        ent_lookup[str(e.get("id", "")).lower()] = e
        ent_lookup[str(e.get("value", "")).lower()] = e

    for cv in connected_vals:
        cv_clean = cv.lower()
        node_doc = ent_lookup.get(cv_clean)
        if node_doc:
            n_id = node_doc.get("id") or f"ent_{node_doc.get('value')}"
            if n_id not in seen_nodes:
                seen_nodes.add(n_id)
                connected_nodes.append(node_doc)
        else:
            # Fallback stub with clean type inference if entity document hasn't been individually created
            node_id = f"ent_stub_{cv.replace(' ', '_')[:24]}"
            if node_id not in seen_nodes:
                seen_nodes.add(node_id)
                connected_nodes.append({
                    "id": node_id,
                    "tenant_id": tenant_id,
                    "value": cv,
                    "type": "entity",
                    "confidence": 0.85,
                    "sources": ["relationship_graph"],
                    "metadata": {"is_stub": True}
                })

    seed_node = ent_lookup.get(entity_id.lower()) or {
        "id": entity_id,
        "value": entity_id,
        "type": "target",
        "confidence": 1.0,
        "sources": ["seed"]
    }
    all_nodes = [seed_node] + [n for n in connected_nodes if n.get("id") != seed_node.get("id")]

    return {
        "seed_entity_id": entity_id,
        "seed_entity": seed_node,
        "hop_count": 1,
        "nodes": all_nodes,
        "edges": rels,
        "has_more": expansion.get("has_more", False),
        "total_edges": expansion.get("total_count", len(rels))
    }

@router.post("/expand", response_model=GraphExpandResponse)
async def expand_graph_state_aware(
    req: GraphExpandRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Batch state-aware multi-branch graph expansion.
    Distinguishes newly arrived nodes from shared nodes already visible on canvas,
    preventing duplicate node rendering and ensuring clean branch collapses.
    """
    tenant_id = current_user.tenant_id
    seeds = req.seed_node_ids or ([req.entity_id] if req.entity_id else [])
    if not seeds:
        raise HTTPException(status_code=400, detail="Either entity_id or seed_node_ids must be specified")

    all_visible = set(req.visible_node_ids) | set(req.visible_entity_ids)
    visible_set = {str(vid).lower() for vid in all_visible}

    all_rels: List[Dict[str, Any]] = []
    seen_edge_ids = set()

    for seed_id in seeds:
        exp = await relationship_repo.expand_entity_1hop(
            tenant_id=tenant_id,
            entity_id_or_val=seed_id,
            investigation_id=req.investigation_id,
            limit=req.limit,
            relationship_types=req.relationship_types,
            min_confidence=req.min_confidence
        )
        for r in exp.get("relationships", []):
            rid = r.get("id") or f"{r.get('source_id')}-{r.get('target_id')}"
            if rid not in seen_edge_ids:
                seen_edge_ids.add(rid)
                all_rels.append(r)

    # Resolve all entities
    all_ents = await entity_repo.list_by_tenant(tenant_id, investigation_id=req.investigation_id)
    ent_lookup = {}
    for e in all_ents:
        ent_lookup[str(e.get("id", "")).lower()] = e
        ent_lookup[str(e.get("value", "")).lower()] = e

    new_nodes: List[Dict[str, Any]] = []
    shared_nodes: List[Dict[str, Any]] = []
    seen_node_ids = set()

    for r in all_rels:
        for endp in [r.get("source_id") or r.get("source_entity_value"), r.get("target_id") or r.get("target_entity_value")]:
            if not endp:
                continue
            endp_str = str(endp)
            endp_lower = endp_str.lower()
            if endp_lower in [s.lower() for s in seeds]:
                continue

            node_doc = ent_lookup.get(endp_lower) or {
                "id": f"ent_{endp_str}",
                "value": endp_str,
                "type": "entity",
                "confidence": 0.85,
                "sources": ["graph"]
            }
            n_id = node_doc.get("id", endp_str)
            if n_id in seen_node_ids:
                continue
            seen_node_ids.add(n_id)

            if endp_lower in visible_set or str(n_id).lower() in visible_set:
                shared_nodes.append(node_doc)
            else:
                new_nodes.append(node_doc)

    return GraphExpandResponse(
        seed_node_ids=seeds,
        nodes=new_nodes + shared_nodes,
        edges=all_rels[:req.limit],
        new_nodes=new_nodes,
        shared_nodes=shared_nodes,
        new_edges=all_rels[:req.limit],
        has_more=len(all_rels) > req.limit,
        total_edges=len(all_rels)
    )

@router.get("/relationships/{relationship_id}/evidence", response_model=Dict[str, Any])
async def get_relationship_evidence(
    relationship_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Exposes the supporting evidence and origin provenance for a specific relationship edge.
    """
    tenant_id = current_user.tenant_id
    rel = await relationship_repo.get_by_id(tenant_id, relationship_id)
    if not rel:
        with db._lock:
            cached_rel = db.relationships.get(relationship_id)
            if cached_rel and (not cached_rel.get("tenant_id") or cached_rel.get("tenant_id") in [tenant_id, "tenant_global", "global"]):
                rel = cached_rel
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship edge not found in tenant boundary")

    ev_ids = rel.get("evidence_ids", [])
    supporting_evidence = []
    all_ev = await evidence_repo.list_by_tenant(tenant_id)
    ev_map = {str(e.get("id", e.get("hash", ""))): e for e in all_ev}
    with db._lock:
        for eid in ev_ids:
            if str(eid) in db.evidence:
                ev_map[str(eid)] = db.evidence[str(eid)]
    for eid in ev_ids:
        if str(eid) in ev_map:
            supporting_evidence.append(ev_map[str(eid)])

    return {
        "relationship_id": relationship_id,
        "relationship": rel,
        "type": rel.get("type") or rel.get("relationship_type"),
        "evidence": supporting_evidence,
        "evidence_records": supporting_evidence,
        "basis": rel.get("basis", "DIRECT_OBSERVATION"),
        "is_inferred": rel.get("is_inferred", False),
        "inference_method": rel.get("inference_method"),
        "confidence": rel.get("confidence", 0.9)
    }

@router.post("/sync", response_model=Dict[str, Any])
async def sync_graph_store(
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Idempotently syncs/backfills entity and relationship records from MongoDB into Neo4j.
    """
    from app.infrastructure.neo4j.service import neo4j_graph_service
    res = await neo4j_graph_service.sync_from_mongodb(current_user.tenant_id)
    return {
        "status": "success",
        "tenant_id": current_user.tenant_id,
        "synced": res
    }

@router.get("/status", response_model=Dict[str, Any])
async def get_graph_status(
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Returns graph database status, engine version, and connectivity.
    """
    from app.infrastructure.neo4j.client import neo4j_client
    ping_res = await neo4j_client.ping()
    return {
        "neo4j": ping_res,
        "engine": "Neo4j Community 5.20.0" if ping_res.get("status") == "healthy" else "MongoDB In-Memory (Fallback)",
        "is_healthy": ping_res.get("status") == "healthy"
    }
