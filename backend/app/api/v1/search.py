import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.search.schemas import SearchRequest, SearchResponse
from app.search.orchestrator import search_orchestrator
from app.core.database import db
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
        import hashlib
        query_val = req.query.strip()
        existing = [
            inv for inv in investigation_service.list_investigations(current_user.tenant_id)
            if inv.target.lower() == query_val.lower()
        ]
        target_inv = None
        if existing:
            target_inv = existing[0]
        else:
            inv_req = InvestigationCreateRequest(
                title=f"Target Investigation: {query_val}",
                target=query_val,
                target_type=response.target_type,
                description=f"Automated intelligence investigation for target '{query_val}' synthesized across authorized engines.",
                search_id=response.search_id
            )
            target_inv = investigation_service.create_investigation(
                tenant_id=current_user.tenant_id,
                user_id=current_user.id,
                user_name=current_user.name,
                request=inv_req
            )
        
        if target_inv:
            response.investigation_id = target_inv.id
            for ent in response.entities:
                ent_id = getattr(ent, "id", None) or f"ent_{hashlib.md5(f'{ent.type}_{ent.value}'.encode()).hexdigest()[:10]}"
                investigation_service.link_entity(current_user.tenant_id, target_inv.id, ent_id)
            for ev in response.evidence:
                ev_id = getattr(ev, "id", None) or getattr(ev, "hash", None)
                if ev_id:
                    investigation_service.link_evidence(current_user.tenant_id, target_inv.id, ev_id)
    except Exception as e:
        from app.core.logger import app_logger
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
