import asyncio
import time
import uuid
from typing import Any, Dict, List
from datetime import datetime
from app.core.config import settings
from app.core.database import db
from app.core.events import DomainEvent, event_bus
from app.core.jobs import job_manager, JobStatus
from app.core.logging import app_logger
from app.identity.models import UserRecord
from app.authorization.service import authorization_service
from app.module_registry.registry import module_registry
from app.module_sdk.models import SearchContext, NormalizedModuleResult
from app.correlation.engine import correlation_engine
from app.search.classifier import target_classifier
from app.search.schemas import SearchRequest, SearchResponse, ModuleJobStatusRecord

class SearchOrchestrator:
    """Module-agnostic search orchestration engine executing independent intelligence jobs."""

    async def execute_search(
        self,
        request: SearchRequest,
        user: UserRecord
    ) -> SearchResponse:
        search_id = f"srch_{uuid.uuid4().hex[:10]}"
        query = request.query.strip()
        target_type = request.target_type or target_classifier.classify(query)
        tenant_id = user.tenant_id
        start_time = time.time()

        app_logger.info(
            f"Search initiated for '{query}' [{target_type}]",
            extra={"search_id": search_id, "tenant_id": tenant_id, "user_id": user.id}
        )

        # Publish SearchStarted event
        await event_bus.publish(DomainEvent(
            event_type="SearchStarted",
            tenant_id=tenant_id,
            trace_id=search_id,
            payload={"search_id": search_id, "query": query, "target_type": target_type, "user_id": user.id}
        ))

        # 1. Determine authorized modules dynamically via multi-layer authorization
        effective_module_ids = authorization_service.get_effective_modules_for_user(user)
        
        # 2. Prepare independent jobs for each authorized and available module
        context = SearchContext(
            search_id=search_id,
            tenant_id=tenant_id,
            user_id=user.id,
            query=query,
            target_type=target_type,
            options=request.options
        )

        module_jobs: List[ModuleJobStatusRecord] = []
        normalized_results: List[NormalizedModuleResult] = []

        async def execute_single_module(module_id: str):
            module = module_registry.get_module(module_id)
            if not module:
                return
                
            mod_manifest = module.manifest
            job = job_manager.create_job(
                tenant_id=tenant_id,
                module_id=module_id,
                search_id=search_id,
                timeout_seconds=settings.SEARCH_JOB_TIMEOUT_SECONDS
            )

            # Publish ModuleExecutionStarted event
            await event_bus.publish(DomainEvent(
                event_type="ModuleExecutionStarted",
                tenant_id=tenant_id,
                trace_id=search_id,
                payload={"search_id": search_id, "module_id": module_id, "job_id": job.job_id}
            ))

            mod_start = time.time()
            try:
                # Execute module search wrapped with job manager isolation and timeout
                result = await job_manager.run_async_job(
                    job.job_id,
                    lambda: module.search(context)
                )

                mod_duration = round((time.time() - mod_start) * 1000, 2)

                if result.status == JobStatus.COMPLETED and result.result:
                    data = result.result
                    norm_res = data if isinstance(data, NormalizedModuleResult) else NormalizedModuleResult(**data)
                    normalized_results.append(norm_res)
                    module_registry.record_execution(module_id, success=True, latency_ms=mod_duration)
                    
                    module_jobs.append(ModuleJobStatusRecord(
                        module=module_id,
                        module_name=mod_manifest.name,
                        job_id=job.job_id,
                        status=norm_res.status,
                        duration_ms=mod_duration,
                        sources=norm_res.sources,
                        error=norm_res.error
                    ))
                else:
                    # Job failed or timed out
                    err_msg = result.error or "Module execution failed"
                    module_registry.record_execution(module_id, success=False, latency_ms=mod_duration)
                    module_jobs.append(ModuleJobStatusRecord(
                        module=module_id,
                        module_name=mod_manifest.name,
                        job_id=job.job_id,
                        status="failed",
                        duration_ms=mod_duration,
                        sources=[],
                        error=err_msg
                    ))

            except Exception as e:
                mod_duration = round((time.time() - mod_start) * 1000, 2)
                module_registry.record_execution(module_id, success=False, latency_ms=mod_duration)
                module_jobs.append(ModuleJobStatusRecord(
                    module=module_id,
                    module_name=mod_manifest.name,
                    job_id=job.job_id,
                    status="failed",
                    duration_ms=mod_duration,
                    sources=[],
                    error=str(e)
                ))
            finally:
                # Publish ModuleExecutionCompleted event
                await event_bus.publish(DomainEvent(
                    event_type="ModuleExecutionCompleted",
                    tenant_id=tenant_id,
                    trace_id=search_id,
                    payload={"search_id": search_id, "module_id": module_id, "job_id": job.job_id}
                ))

        # Run all authorized modules concurrently
        if effective_module_ids:
            tasks = [execute_single_module(mid) for mid in effective_module_ids]
            await asyncio.gather(*tasks, return_exceptions=True)

        # 3. Correlate normalized findings across all completed modules
        corr_entities, corr_relationships, all_evidence = correlation_engine.correlate_module_results(
            target_query=query,
            target_type=target_type,
            results=normalized_results
        )

        # 4. Assess overall search status and partial intelligence
        failed_jobs = [j for j in module_jobs if j.status == "failed"]
        completed_jobs = [j for j in module_jobs if j.status in ["completed", "partial"]]

        if not module_jobs:
            overall_status = "completed"
            partial_warning = "No modules were authorized or available for this query."
        elif failed_jobs and completed_jobs:
            overall_status = "partial"
            failed_names = ", ".join([j.module_name for j in failed_jobs])
            partial_warning = f"Search completed with partial intelligence. {failed_names} temporarily unavailable."
        elif failed_jobs and not completed_jobs:
            overall_status = "failed"
            partial_warning = "All executing intelligence modules encountered errors."
        else:
            overall_status = "completed"
            partial_warning = None

        total_duration = round((time.time() - start_time) * 1000, 2)

        response = SearchResponse(
            search_id=search_id,
            query=query,
            target_type=target_type,
            status=overall_status,
            partial_warning=partial_warning,
            module_jobs=module_jobs,
            entities=corr_entities,
            relationships=corr_relationships,
            evidence=all_evidence,
            stats={
                "total_duration_ms": total_duration,
                "modules_executed": len(module_jobs),
                "entities_count": len(corr_entities),
                "relationships_count": len(corr_relationships),
                "evidence_count": len(all_evidence)
            },
            executed_at=datetime.utcnow()
        )

        # Persist search record in tenant-scoped data store & MongoDB
        search_record = {
            "id": search_id,
            "tenant_id": tenant_id,
            "user_id": user.id,
            "query": query,
            "target_type": target_type,
            "status": overall_status,
            "entities_count": len(corr_entities),
            "created_at": datetime.utcnow()
        }
        with db._lock:
            db.searches[search_id] = search_record
            
        from app.infrastructure.mongodb.repositories import search_repo, entity_repo, evidence_repo
        search_repo._sync_write({"id": search_id, "tenant_id": tenant_id}, search_record)

        # Persist correlated entities & evidence to MongoDB
        for ent in corr_entities:
            entity_repo._sync_write({"type": ent.type, "value": ent.value, "tenant_id": tenant_id}, {
                "id": getattr(ent, "id", None) or f"ent_{hash(f'{ent.type}_{ent.value}')}",
                "tenant_id": tenant_id,
                "type": ent.type,
                "value": ent.value,
                "confidence": ent.confidence,
                "sources": ent.sources,
                "metadata": ent.metadata or {},
                "last_seen": datetime.utcnow().isoformat()
            })
        for ev in all_evidence:
            ev_hash = getattr(ev, "hash", "") or getattr(ev, "id", "")
            if ev_hash:
                evidence_repo._sync_write({"hash": ev_hash, "tenant_id": tenant_id}, {
                    "id": getattr(ev, "id", None) or f"ev_{ev_hash[:12]}",
                    "tenant_id": tenant_id,
                    "search_id": search_id,
                    "source": getattr(ev, "source", "Engine"),
                    "provider": getattr(ev, "provider", "osint"),
                    "module": getattr(ev, "module", "osint"),
                    "confidence": getattr(ev, "confidence", 0.9),
                    "hash": ev_hash,
                    "timestamp": datetime.utcnow().isoformat()
                })

        # Automatically synthesize findings from correlated high-confidence entities and evidence
        from app.findings.service import finding_service
        from app.findings.models import FindingCreate
        
        for ent in corr_entities[:10]:
            sev = "HIGH" if ent.confidence >= 0.85 else ("MEDIUM" if ent.confidence >= 0.6 else "LOW")
            mitigation_text = f"Audit infrastructure and verify trust boundaries for {ent.value} ({ent.type})."
            ev_ids = [getattr(ev, 'id', None) or getattr(ev, 'hash', None) for ev in all_evidence[:5]]
            valid_ev_ids = [str(x) for x in ev_ids if x is not None]
            
            finding_service.create_finding(
                tenant_id=tenant_id,
                data=FindingCreate(
                    search_id=search_id,
                    title=f"Discovered {ent.type}: {ent.value}",
                    description=f"Correlated {ent.type} identified across {len(ent.sources)} intelligence sources: {', '.join(ent.sources)}.",
                    type=ent.type,
                    severity=sev,
                    confidence=int(ent.confidence * 100),
                    module_id="osint",
                    source=ent.sources[0] if ent.sources else "OSINT Engine",
                    status="OPEN",
                    mitigation=mitigation_text,
                    entity_ids=[ent.value],
                    evidence_ids=valid_ev_ids
                )
            )


        # Publish SearchCompleted event
        await event_bus.publish(DomainEvent(
            event_type="SearchCompleted",
            tenant_id=tenant_id,
            trace_id=search_id,
            payload={"search_id": search_id, "status": overall_status, "entities": len(corr_entities)}
        ))

        return response


search_orchestrator = SearchOrchestrator()
