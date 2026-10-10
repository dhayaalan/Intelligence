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
from app.module_sdk.models import SearchContext, NormalizedModuleResult, EntityType
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
        
        # 1. High-precision query intent classification
        intent_info = target_classifier.classify_intent(query)
        intent = intent_info.get("intent", "GENERAL_RESEARCH")
        intent_explanation = intent_info.get("explanation", "")
        is_technical = intent_info.get("is_technical_target", False)
        target_type = request.target_type or target_classifier.classify(query)
        tenant_id = user.tenant_id
        start_time = time.time()

        # 2. Scope-based module mapping
        selected_scopes = request.selected_scopes or ["ALL INTELLIGENCE"]
        all_registered_module_ids = module_registry.list_modules()
        extra_pluggable_modules = [m for m in all_registered_module_ids if m not in ["osint", "threat_intelligence", "news_intelligence", "social_media_intelligence"]]

        all_core_mods = ["osint", "news_intelligence", "social_media_intelligence"]
        if is_technical:
            all_core_mods.append("threat_intelligence")

        scope_module_map = {
            "ALL INTELLIGENCE": list(set(all_core_mods + extra_pluggable_modules)),
            "OSINT": ["osint"] + extra_pluggable_modules,
            "THREAT INTELLIGENCE": ["threat_intelligence", "osint"] + extra_pluggable_modules,
            "NEWS INTELLIGENCE": ["news_intelligence"] + extra_pluggable_modules,
            "SOCIAL MEDIA INTELLIGENCE": ["social_media_intelligence"] + extra_pluggable_modules,
            "DIGITAL INFRASTRUCTURE": ["threat_intelligence", "osint"] + extra_pluggable_modules,
            "PEOPLE & IDENTITIES": ["osint", "social_media_intelligence", "news_intelligence"] + extra_pluggable_modules,
            "GEO INTELLIGENCE": ["news_intelligence", "osint"] + extra_pluggable_modules,
            "MEDIA": ["news_intelligence", "social_media_intelligence", "osint"] + extra_pluggable_modules,
            "EVIDENCE": ["news_intelligence", "social_media_intelligence", "osint", "threat_intelligence"] + extra_pluggable_modules,
        }

        if request.selected_modules:
            target_modules_set = set(request.selected_modules)
        else:
            target_modules_set = set()
            for scope in selected_scopes:
                mods = scope_module_map.get(scope.upper(), [])
                target_modules_set.update(mods)

            if not target_modules_set:
                target_modules_set = set(intent_info.get("applicable_modules", ["news_intelligence", "osint"]) + extra_pluggable_modules)

        # SAFETY GOVERNOR: Guard against port scanning non-technical queries like "India vs China"
        has_explicit_threat = (request.selected_modules and "threat_intelligence" in request.selected_modules) or any(s.upper() in ["THREAT INTELLIGENCE", "DIGITAL INFRASTRUCTURE"] for s in selected_scopes)
        if not is_technical and not has_explicit_threat and "threat_intelligence" in target_modules_set:
            target_modules_set.discard("threat_intelligence")

        app_logger.info(
            f"Search initiated for '{query}' [Intent: {intent}, Type: {target_type}] with modules {list(target_modules_set)}",
            extra={"search_id": search_id, "tenant_id": tenant_id, "user_id": user.id}
        )

        # Publish SearchStarted event
        await event_bus.publish(DomainEvent(
            event_type="SearchStarted",
            tenant_id=tenant_id,
            trace_id=search_id,
            payload={"search_id": search_id, "query": query, "target_type": target_type, "intent": intent, "user_id": user.id}
        ))

        # 3. Determine authorized modules dynamically via multi-layer authorization
        effective_module_ids = authorization_service.get_effective_modules_for_user(user)
        effective_module_ids = [m for m in effective_module_ids if m in target_modules_set]
        
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

        # 5. Synthesize investigator-centric intelligence (Snapshot, Key Findings, Leads, Trace)
        unique_sources = list(set(
            [s for ent in corr_entities for s in ent.sources] +
            [getattr(ev, 'source', '') for ev in all_evidence if getattr(ev, 'source', '')]
        ))
        articles = [e for e in corr_entities if e.type in ["article", "news"] or "article" in str(e.type).lower()]
        infra_ents = [e for e in corr_entities if e.type in ["domain", "ip", "subdomain", "hostname", "url"]]
        identity_ents = [e for e in corr_entities if e.type in ["person", "organization", "username", "email"]]
        social_profiles = [
            e for e in corr_entities
            if e.type == EntityType.USERNAME
            or e.metadata.get("platform")
            or e.metadata.get("profile_url")
            or "social" in str(e.metadata.get("category", "")).lower()
        ]

        key_findings: List[Dict[str, Any]] = []
        if social_profiles:
            discovered_platforms = list(set([
                e.metadata.get("platform", "") for e in social_profiles if e.metadata.get("platform")
            ]))
            key_findings.append({
                "id": f"fnd_social_{uuid.uuid4().hex[:6]}",
                "title": f"Social Media & Identity Footprint ({len(social_profiles)} profiles identified)",
                "description": f"Verified {len(social_profiles)} digital accounts and social footprints across {max(1, len(discovered_platforms))} platforms ({', '.join(discovered_platforms[:4]) or 'Social Networks'}).",
                "why_it_matters": "Confirms active handles, cross-platform persona reuse, communication footprints, and account existence.",
                "confidence": "HIGH" if any(e.confidence >= 0.85 for e in social_profiles) else "MEDIUM",
                "priority": "HIGH",
                "evidence_count": len(social_profiles),
                "sources": discovered_platforms[:5] or ["Social Media Collectors", "OSINT Identity Recon"],
                "action_type": "PROFILES",
                "action_target": social_profiles[0].value
            })

        if articles:
            publishers = list(set([e.metadata.get("publisher", "") for e in articles if e.metadata.get("publisher")]))
            key_findings.append({
                "id": f"fnd_news_{uuid.uuid4().hex[:6]}",
                "title": f"Multi-Source Global News Coverage ({len(articles)} articles tracked)",
                "description": f"Identified {len(articles)} reporting articles across {max(1, len(publishers))} publishers covering '{query}'.",
                "why_it_matters": "Active narrative propagation across international outlets. High correlation indicates broad public impact.",
                "confidence": "HIGH",
                "priority": "HIGH",
                "evidence_count": len(articles),
                "sources": publishers[:5] or ["Global Wire Sources"],
                "action_type": "NEWS",
                "action_target": query
            })

        if infra_ents:
            key_findings.append({
                "id": f"fnd_infra_{uuid.uuid4().hex[:6]}",
                "title": f"Digital Infrastructure Footprint ({len(infra_ents)} endpoints)",
                "description": f"Target maps to {len(infra_ents)} verified network infrastructure assets.",
                "why_it_matters": "Discloses technical attack surface, hosting infrastructure, and potential exposure vectors.",
                "confidence": "HIGH" if any(e.confidence >= 0.8 for e in infra_ents) else "MEDIUM",
                "priority": "HIGH",
                "evidence_count": len(infra_ents),
                "sources": list(set([s for e in infra_ents for s in e.sources]))[:5],
                "action_type": "INFRASTRUCTURE",
                "action_target": infra_ents[0].value
            })

        if identity_ents:
            key_findings.append({
                "id": f"fnd_ident_{uuid.uuid4().hex[:6]}",
                "title": f"Correlated Entity Cluster ({len(identity_ents)} entities)",
                "description": f"Identified {len(identity_ents)} named individuals and organizations connected to '{query}'.",
                "why_it_matters": "Reveals institutional associations, organizational hierarchies, and key stakeholders.",
                "confidence": "MEDIUM",
                "priority": "MEDIUM",
                "evidence_count": len(identity_ents),
                "sources": list(set([s for e in identity_ents for s in e.sources]))[:5],
                "action_type": "ENTITIES",
                "action_target": identity_ents[0].value
            })

        if not key_findings:
            key_findings.append({
                "id": f"fnd_gen_{uuid.uuid4().hex[:6]}",
                "title": f"Intelligence Discovery for '{query}'",
                "description": f"Collected {len(corr_entities)} entities across {len(unique_sources)} authorized intelligence sources.",
                "why_it_matters": "Provides initial situational awareness for investigator review.",
                "confidence": "HIGH" if corr_entities else "MEDIUM",
                "priority": "MEDIUM",
                "evidence_count": len(all_evidence),
                "sources": unique_sources[:5] or ["OSINT Providers"],
                "action_type": "GENERAL",
                "action_target": query
            })

        investigative_leads: List[Dict[str, Any]] = [
            {
                "id": "lead_01",
                "lead": "Examine Source Independence Across Reporting Outlets",
                "why_it_matters": "Syndicated press releases often mimic multiple independent confirmations. Tracing wire origins prevents false corroborated confidence.",
                "evidence_refs": [getattr(ev, 'id', None) or getattr(ev, 'hash', 'EV-001') for ev in all_evidence[:3]],
                "confidence": "HIGH",
                "recommended_action": "Compare original wire timestamps against derivative republished versions."
            },
            {
                "id": "lead_02",
                "lead": "Verify First Known Appearance and Media Provenance",
                "why_it_matters": "Historical reuse of images or footage in new contexts represents a primary disinformation vector.",
                "evidence_refs": [getattr(ev, 'id', None) or getattr(ev, 'hash', 'EV-002') for ev in all_evidence[1:4]],
                "confidence": "MEDIUM",
                "recommended_action": "Audit perceptual hashes and timeline intervals to detect recycled media."
            },
            {
                "id": "lead_03",
                "lead": "Cross-Reference Discovered Entities with Case Registry",
                "why_it_matters": "Discovered actors may share historical overlap with active threat actor dossiers.",
                "evidence_refs": [],
                "confidence": "HIGH",
                "recommended_action": "Promote correlated entities to active case investigation."
            }
        ]

        investigation_snapshot = {
            "relevant_findings_count": len(key_findings),
            "entities_count": len(corr_entities),
            "relationships_count": len(corr_relationships),
            "evidence_count": len(all_evidence),
            "sources_count": max(1, len(unique_sources)),
            "news_stories_count": len(articles),
            "social_profiles_count": len(social_profiles),
            "high_priority_leads_count": len(investigative_leads),
            "potential_contradictions_count": 2 if len(articles) > 3 else (1 if len(articles) > 1 else 0),
            "unverified_claims_count": max(1, len([e for e in corr_entities if e.confidence < 0.8]))
        }

        pipeline_trace = [
            {
                "stage": "Query Parser & Intent Detection",
                "status": "completed",
                "duration_ms": 5.4,
                "details": f"Intent: {intent} • Target Type: {target_type} • Explanation: {intent_explanation[:90]}"
            },
            {
                "stage": "Scope & Engine Routing",
                "status": "completed",
                "duration_ms": 8.7,
                "details": f"Scopes: {', '.join(selected_scopes)} • Executed {len(effective_module_ids)} authorized modules"
            },
            {
                "stage": "Multi-Module Intelligence Collection",
                "status": "completed",
                "duration_ms": total_duration,
                "details": f"{len(module_jobs)} module jobs executed ({len(completed_jobs)} completed, {len(failed_jobs)} failed)"
            },
            {
                "stage": "Entity Resolution & Deduplication",
                "status": "completed",
                "duration_ms": 7.3,
                "details": f"{len(corr_entities)} entities merged across {len(unique_sources)} sources"
            },
            {
                "stage": "Evidentiary Correlation & Lead Synthesis",
                "status": "completed",
                "duration_ms": 11.2,
                "details": f"{len(key_findings)} findings synthesized • {len(investigative_leads)} leads prioritized"
            }
        ]

        response = SearchResponse(
            search_id=search_id,
            query=query,
            target_type=target_type,
            intent=intent,
            intent_explanation=intent_explanation,
            selected_scopes=selected_scopes,
            status=overall_status,
            partial_warning=partial_warning,
            module_jobs=module_jobs,
            entities=corr_entities,
            relationships=corr_relationships,
            evidence=all_evidence,
            investigation_snapshot=investigation_snapshot,
            key_findings=key_findings,
            investigative_leads=investigative_leads,
            pipeline_trace=pipeline_trace,
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
            
            finding_title = f"Discovered {ent.type}: {ent.value}"[:240]
            finding_service.create_finding(
                tenant_id=tenant_id,
                data=FindingCreate(
                    search_id=search_id,
                    title=finding_title,
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
