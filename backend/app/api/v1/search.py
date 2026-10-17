import json
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.search.schemas import SearchRequest, SearchResponse
from app.search.orchestrator import search_orchestrator
from app.core.database import db
from app.core.logging import app_logger
from app.audit.logger import audit_logger

router = APIRouter(prefix="/search", tags=["Search Orchestrator"])

@router.post("", response_model=SearchResponse)
async def execute_search(
    req: SearchRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """Executes a unified multi-module search with fault isolation and correlation."""
    response = await search_orchestrator.execute_search(req, current_user)
    
    # Automatically create/update an investigation for this search target
    try:
        from app.investigations.service import investigation_service
        from app.investigations.models import InvestigationCreateRequest
        from app.infrastructure.mongodb.repositories import investigation_repo, case_repo
        import hashlib
        query_val = req.query.strip()
        if response.target_type == "unknown" or response.validation_error:
            return response
        
        executed_mods = [j.module for j in response.module_jobs if j.status in ["completed", "partial"]]
        selected_modules = list(set(["osint", "threat_intelligence", "news_intelligence"] + executed_mods))

        existing = [
            inv for inv in investigation_service.list_investigations(current_user.tenant_id)
            if inv.target.lower() == query_val.lower()
        ]
        target_inv = None
        rel_dicts = [rel.dict() if hasattr(rel, "dict") else dict(rel) for rel in response.relationships]
        media_dicts = [m.model_dump() if hasattr(m, "model_dump") else (m.dict() if hasattr(m, "dict") else dict(m)) for m in (response.media or [])]
        findings_data = [f if isinstance(f, dict) else f.dict() for f in (response.key_findings or [])]
        leads_data = [l if isinstance(l, dict) else l.dict() for l in (response.investigative_leads or [])]
        pivots_data = [p if isinstance(p, dict) else p.dict() for p in (response.suggested_pivots or [])]
        
        inv_summary = {
            "key_findings": findings_data,
            "investigative_leads": leads_data,
            "suggested_pivots": pivots_data,
            "search_mode": response.search_mode,
            "intent": response.intent,
            "target_type": response.target_type,
            "media_count": len(response.media),
        }
        inv_health = {
            "evidence_coverage": "HIGH" if len(response.evidence) > 10 else "MEDIUM",
            "source_diversity": "HIGH" if len(response.module_jobs) > 1 else "MEDIUM",
            "entity_resolution": "HIGH",
            "temporal_coverage": "HIGH",
            "unresolved_questions_count": 0,
            "conflicting_claims_count": 0,
            "primary_source_coverage": "HIGH"
        }

        if existing:
            target_inv = existing[0]
            with db._lock:
                inv_data = db.investigations.get(target_inv.id)
                if inv_data:
                    curr_mods = set(inv_data.get("selected_modules", []))
                    curr_mods.update(selected_modules)
                    inv_data["selected_modules"] = list(curr_mods)
                    inv_data["search_id"] = response.search_id
                    if rel_dicts:
                        inv_data["relationships"] = rel_dicts
                    inv_data["investigative_summary"] = inv_summary
                    inv_data["investigation_health"] = inv_health
                    if media_dicts:
                        curr_m = inv_data.get("media", [])
                        seen_u = {m.get("url") for m in curr_m if isinstance(m, dict) and m.get("url")}
                        for md in media_dicts:
                            if md.get("url") and md.get("url") not in seen_u:
                                curr_m.append(md)
                                seen_u.add(md.get("url"))
                        inv_data["media"] = curr_m
                    investigation_repo._sync_write({"id": target_inv.id, "tenant_id": current_user.tenant_id}, inv_data)
                    case_repo._sync_write({"id": target_inv.id, "tenant_id": current_user.tenant_id}, inv_data)
        else:
            inv_desc = f"Automated intelligence investigation for target '{query_val}' synthesized across authorized engines."
            inv_req = InvestigationCreateRequest(
                title=f"Investigation: {query_val}",
                target=query_val,
                target_type=response.target_type,
                description=inv_desc,
                selected_modules=selected_modules,
                search_id=response.search_id,
                relationships=rel_dicts,
                investigative_summary=inv_summary,
                investigation_health=inv_health,
                media=media_dicts
            )
            target_inv = investigation_service.create_investigation(
                tenant_id=current_user.tenant_id,
                user_id=current_user.id,
                user_name=current_user.name,
                request=inv_req
            )
        
        if target_inv:
            response.investigation_id = target_inv.id
            from app.entities.service import entity_service
            from app.evidence.service import evidence_service
            import uuid

            from app.infrastructure.mongodb.repositories import relationship_repo, memory_cache
            from app.infrastructure.neo4j.service import neo4j_service

            # 1. Upsert and persist every entity to DB linked to target_inv.id
            for ent in response.entities:
                try:
                    saved_ent = entity_service.upsert_entity(current_user.tenant_id, ent, investigation_id=target_inv.id)
                    ent_id = getattr(saved_ent, "id", None) or getattr(ent, "id", None) or f"ent_{hashlib.md5(f'{ent.type}_{ent.value}'.encode()).hexdigest()[:10]}"
                    investigation_service.link_entity(current_user.tenant_id, target_inv.id, ent_id)
                    await neo4j_service.upsert_entity(current_user.tenant_id, {
                        "id": ent_id,
                        "value": ent.value,
                        "type": ent.type,
                        "confidence": ent.confidence,
                        "sources": ent.sources,
                        "metadata": ent.metadata or {}
                    })
                except Exception as ent_err:
                    app_logger.warning(f"Error persisting entity {ent}: {ent_err}")

            # 2. Store and persist every evidence payload to DB linked to target_inv.id
            for ev in response.evidence:
                try:
                    saved_ev = evidence_service.store_evidence(
                        tenant_id=current_user.tenant_id,
                        payload=ev,
                        investigation_id=target_inv.id,
                        search_id=response.search_id
                    )
                    ev_id = getattr(saved_ev, "id", None) or getattr(ev, "id", None) or getattr(ev, "hash", None)
                    if ev_id:
                        investigation_service.link_evidence(current_user.tenant_id, target_inv.id, ev_id)
                except Exception as ev_err:
                    app_logger.warning(f"Error persisting evidence {ev}: {ev_err}")

            # 2.5 Store and link media records to DB linked to target_inv.id
            for md in media_dicts:
                try:
                    investigation_service.link_media(current_user.tenant_id, target_inv.id, md)
                except Exception as m_err:
                    app_logger.warning(f"Error persisting media {md}: {m_err}")

            # 3. Store relationships, media, and summary on target_inv and persist to MongoDB & Neo4j
            with db._lock:
                inv_data = db.investigations.get(target_inv.id)
                if inv_data:
                    inv_data["relationships"] = rel_dicts
                    inv_data["investigative_summary"] = inv_summary
                    inv_data["investigation_health"] = inv_health
                    if media_dicts:
                        curr_m = inv_data.get("media", [])
                        seen_u = {m.get("url") for m in curr_m if isinstance(m, dict) and m.get("url")}
                        for md in media_dicts:
                            if md.get("url") and md.get("url") not in seen_u:
                                curr_m.append(md)
                                seen_u.add(md.get("url"))
                        inv_data["media"] = curr_m
                    investigation_repo._sync_write({"id": target_inv.id, "tenant_id": current_user.tenant_id}, inv_data)
                    case_repo._sync_write({"id": target_inv.id, "tenant_id": current_user.tenant_id}, inv_data)

            for rel_d in rel_dicts:
                try:
                    rel_d["investigation_id"] = target_inv.id
                    rel_d["tenant_id"] = current_user.tenant_id
                    await relationship_repo.save(current_user.tenant_id, rel_d)
                    await neo4j_service.upsert_relationship(current_user.tenant_id, rel_d)
                except Exception as r_err:
                    app_logger.warning(f"Error persisting relationship {rel_d}: {r_err}")

            # 4. Bridge News Intelligence into the investigation
            try:
                from app.modules.news_intelligence.service import news_intelligence_service
                from app.modules.news_intelligence.models import AddToCaseRequest
                existing_news = [
                    n for n in news_intelligence_service.list_investigations(current_user.tenant_id)
                    if n.original_query.lower() == query_val.lower()
                ]
                if not existing_news:
                    news_inv = await news_intelligence_service.create_investigation(
                        tenant_id=current_user.tenant_id,
                        user=current_user,
                        original_query=query_val,
                        target_input=f"Automated news intelligence investigation on target '{query_val}'",
                        preset_title=f"News Dossier: {query_val}",
                        search_id=response.search_id,
                    )
                    await news_intelligence_service.attach_to_case(
                        tenant_id=current_user.tenant_id,
                        user=current_user,
                        investigation_id=news_inv.id,
                        req=AddToCaseRequest(case_id=target_inv.id, analyst_notes="Linked from Universal Search orchestration")
                    )
            except Exception as news_bridge_err:
                app_logger.warning(f"Could not auto-bridge news investigation for '{query_val}': {news_bridge_err}")

    except Exception as e:
        app_logger.warning(f"Could not auto-create investigation for query '{req.query}': {e}")

    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="SEARCH_EXECUTED",
        resource_type="search",
        resource_id=response.search_id,
        details={"query": req.query, "target_type": response.target_type, "status": response.status}
    )
    
    return response

@router.get("/recent")
async def list_recent_searches(
    limit: int = 20,
    current_user: UserRecord = Depends(get_current_user)
):
    with db._lock:
        searches = [
            s for s in db.searches.values()
            if s.get("tenant_id") == current_user.tenant_id
        ]
        return sorted(searches, key=lambda x: x["created_at"], reverse=True)[:limit]

@router.get("/stream")
async def stream_search_events(
    query: str = Query(...),
    target_type: Optional[str] = None,
    current_user: UserRecord = Depends(get_current_user)
):
    """Server-Sent Events (SSE) stream providing real-time module execution progress."""
    async def event_generator():
        yield f"data: {json.dumps({'event': 'started', 'query': query})}\n\n"
        await asyncio.sleep(0.1)
        
        req = SearchRequest(query=query, target_type=target_type)
        response = await search_orchestrator.execute_search(req, current_user)
        
        for job in response.module_jobs:
            yield f"data: {json.dumps({'event': 'module_completed', 'module': job.module, 'status': job.status, 'duration_ms': job.duration_ms})}\n\n"
            await asyncio.sleep(0.05)
            
        yield f"data: {json.dumps({'event': 'search_completed', 'search_id': response.search_id, 'status': response.status, 'entities_count': len(response.entities)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/geolocate")
async def geolocate_target(
    target: str = Query(...),
    current_user: UserRecord = Depends(get_current_user)
):
    """Performs real live IP geolocation lookup for an IP address or domain hostname."""
    import socket
    import ipaddress
    import httpx
    from datetime import datetime

    cleaned = target.strip().lower()
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        from urllib.parse import urlparse
        cleaned = urlparse(cleaned).netloc.split(":")[0]

    resolved_ip = None
    try:
        ipaddress.ip_address(cleaned)
        resolved_ip = cleaned
    except ValueError:
        try:
            loop = asyncio.get_event_loop()
            resolved_ip = await loop.run_in_executor(None, socket.gethostbyname, cleaned)
        except Exception:
            resolved_ip = None

    if not resolved_ip:
        raise HTTPException(status_code=404, detail=f"Target '{target}' could not be resolved to a routable IP address.")

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(f"http://ip-api.com/json/{resolved_ip}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success" and data.get("lat") is not None and data.get("lon") is not None:
                    isp = data.get("isp", "")
                    threat = "SUSPICIOUS" if any(w in isp.lower() for w in ["vpn", "proxy", "tor", "hosting", "cloud"]) else "BENIGN"
                    return {
                        "id": f"geo_{resolved_ip.replace('.', '_')}",
                        "name": f"{target} ({resolved_ip})",
                        "type": "Resolved IP Host" if resolved_ip == cleaned else "Domain Ingress",
                        "ip": resolved_ip,
                        "city": data.get("city", "Unknown City"),
                        "country": data.get("country", "Unknown Country"),
                        "countryCode": data.get("countryCode", ""),
                        "lat": data.get("lat"),
                        "lng": data.get("lon"),
                        "isp": isp,
                        "org": data.get("org", ""),
                        "asn": data.get("as", ""),
                        "threatLevel": threat,
                        "source": "ip-api.com",
                        "timestamp": datetime.utcnow().isoformat(),
                        "details": f"ISP: {isp} | ASN: {data.get('as', '')}"
                    }
    except Exception as e:
        pass

    raise HTTPException(status_code=502, detail=f"Unable to geolocate IP '{resolved_ip}'")

# -----------------------------------------------------------------------------
# SAVED SEARCHES REUSABLE ENDPOINTS (Section 18)
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field

class SavedSearchCreateRequest(BaseModel):
    name: str
    query: str
    target_type: Optional[str] = None
    tools: List[str] = Field(default_factory=list)
    filters: dict = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

class SavedSearchRecord(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    user_name: str
    name: str
    query: str
    target_type: Optional[str] = None
    tools: List[str] = Field(default_factory=list)
    filters: dict = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    created_at: str
    last_executed_at: Optional[str] = None

_saved_searches_store: List[dict] = []

@router.post("/saved", response_model=SavedSearchRecord)
async def create_saved_search(
    req: SavedSearchCreateRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """Creates and persists a saved intelligence search query for the tenant."""
    import uuid
    from datetime import datetime, timezone
    
    saved_id = f"saved_{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "id": saved_id,
        "tenant_id": current_user.tenant_id,
        "user_id": current_user.id,
        "user_name": current_user.name,
        "name": req.name.strip(),
        "query": req.query.strip(),
        "target_type": req.target_type,
        "tools": req.tools,
        "filters": req.filters,
        "tags": req.tags,
        "notes": req.notes,
        "created_at": now,
        "last_executed_at": None,
    }
    _saved_searches_store.insert(0, record)
    return SavedSearchRecord(**record)

@router.get("/saved", response_model=List[SavedSearchRecord])
async def list_saved_searches(
    current_user: UserRecord = Depends(get_current_user)
):
    """Returns all saved intelligence searches for the user's tenant."""
    results = [s for s in _saved_searches_store if s.get("tenant_id") == current_user.tenant_id]
    return [SavedSearchRecord(**s) for s in results]

@router.delete("/saved/{saved_id}")
async def delete_saved_search(
    saved_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    """Deletes a saved search belonging to the user's tenant."""
    global _saved_searches_store
    initial_len = len(_saved_searches_store)
    _saved_searches_store = [
        s for s in _saved_searches_store
        if not (s.get("id") == saved_id and s.get("tenant_id") == current_user.tenant_id)
    ]
    if len(_saved_searches_store) == initial_len:
        raise HTTPException(status_code=404, detail="Saved search not found or unauthorized.")
    return {"status": "deleted", "id": saved_id}

@router.post("/saved/{saved_id}/execute", response_model=SearchResponse)
async def execute_saved_search(
    saved_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    """Re-executes a saved intelligence search directly with the search orchestrator."""
    from datetime import datetime, timezone
    match = next(
        (s for s in _saved_searches_store if s.get("id") == saved_id and s.get("tenant_id") == current_user.tenant_id),
        None
    )
    if not match:
        raise HTTPException(status_code=404, detail="Saved search not found.")
    
    match["last_executed_at"] = datetime.now(timezone.utc).isoformat()
    req = SearchRequest(
        query=match["query"],
        target_type=match.get("target_type"),
        options=match.get("filters", {})
    )
    return await execute_search(req, current_user)


@router.post("/pivots")
async def extract_query_pivots(
    req: SearchRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    [OSINT-01] Generates traceable, high-confidence secondary pivot targets
    for a query or active investigation.
    """
    from app.modules.osint.pivot_engine import pivot_engine
    from app.search.classifier import target_classifier
    target_type = req.target_type or target_classifier.classify(req.query)

    from app.investigations.service import investigation_service
    existing = [
        inv for inv in investigation_service.list_investigations(current_user.tenant_id)
        if inv.target.lower() == req.query.strip().lower()
    ]
    entities = []
    if existing:
        entities = existing[0].entities or []

    pivots = pivot_engine.generate_pivots(
        original_query=req.query,
        target_type=target_type,
        entities=entities,
        max_pivots=10
    )
    return {
        "query": req.query,
        "target_type": target_type,
        "total_pivots": len(pivots),
        "pivots": pivots
    }


