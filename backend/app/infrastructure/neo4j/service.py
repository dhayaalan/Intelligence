import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
from app.infrastructure.neo4j.client import neo4j_client
from app.core.logging import app_logger

class Neo4jGraphService:
    """
    Service layer for Neo4j relationship intelligence.
    Handles entity and relationship persistence, bounded 1-hop traversal,
    epistemic provenance tracking, and synchronization with MongoDB.
    """

    ALLOWED_REL_TYPES = {
        "OWNS", "USES", "HOSTED_ON", "RESOLVES_TO", "RELATED_TO", "MENTIONS",
        "PUBLISHED", "CORROBORATES", "CONTRADICTS", "QUOTES", "AMPLIFIES",
        "REPORTS_ON", "REGISTERED_TO", "CONNECTED_TO", "LOCATED_AT", "SEEN_ON",
        "AUTHORED", "HAS_IDENTIFIER", "ACCOUNT_REFERENCES_ENTITY",
        "ARTICLE_MENTIONS_ENTITY", "VIDEO_PUBLISHED_BY_CHANNEL",
        "POST_REFERENCES_LOCATION", "ARTICLE_REPORTS_ON_EVENT",
        "EVENT_OCCURS_AT_LOCATION", "DOMAIN_RESOLVES_TO_IP",
        "EVIDENCE_SUPPORTS_RELATIONSHIP", "POSSIBLE_ASSOCIATION", "ASSOCIATED_WITH",
        "EXPOSED_BY", "CONTAINS", "PRESIDENT", "FOUNDER", "CO_FOUNDER",
        "ADVOCACY_DIRECTOR", "ADVISORY_BOARD", "POWERED_BY", "PROJECT_OF",
        "WORKS_WITH", "SISTER_NGO", "FUNDING", "NEXUS", "SUBDOMAIN_OF",
        "HOSTED_ON_IP", "HAS_VULNERABILITY", "ALIASED_AS", "COMMUNICATED_WITH",
        "SUBSIDIARY_OF", "CHAIR", "DIRECTOR", "LEADERSHIP", "MEMBER", "SPONSORS",
        "THREAT", "ATTRIBUTED_TO", "MALICIOUS", "INVESTIGATION_REL", "CO_OCCURS",
        "RELATED", "AFFILIATED_WITH", "MENTIONED_IN"
    }

    def _sanitize_rel_type(self, rel_type: Optional[str]) -> str:
        """Sanitizes relationship types against an allowlist to prevent Cypher injection."""
        if not rel_type:
            return "RELATED"
        clean = re.sub(r"[^A-Za-z0-9_]", "_", str(rel_type)).upper()
        if clean in self.ALLOWED_REL_TYPES:
            return clean
        return "RELATED"

    async def is_available(self) -> bool:
        driver = await neo4j_client.get_driver()
        return driver is not None

    async def upsert_entity(self, tenant_id: str, entity_data: Dict[str, Any]) -> bool:
        """Idempotently merges an entity node in Neo4j with tenant scoping."""
        driver = await neo4j_client.get_driver()
        if not driver:
            return False

        ent_id = entity_data.get("id") or f"ent_{entity_data.get('value', '')}"
        val = str(entity_data.get("value", ""))
        raw_t = entity_data.get("type", "entity")
        e_type = str(raw_t.value if hasattr(raw_t, "value") else raw_t).lower()
        if e_type.startswith("entitytype."):
            e_type = e_type.replace("entitytype.", "")
        conf = float(entity_data.get("confidence")) if entity_data.get("confidence") is not None else None
        sources = list(entity_data.get("sources", []))
        meta_json = json.dumps(entity_data.get("metadata", {}))

        cypher = """
        MERGE (e:Entity {id: $id, tenant_id: $tenant_id})
        SET e.value = $value,
            e.type = $type,
            e.confidence = $confidence,
            e.sources = $sources,
            e.metadata = $metadata,
            e.last_seen = datetime()
        RETURN e.id AS id
        """
        try:
            async with driver.session() as session:
                await session.run(
                    cypher,
                    id=ent_id,
                    tenant_id=tenant_id,
                    value=val,
                    type=e_type,
                    confidence=conf,
                    sources=sources,
                    metadata=meta_json
                )
            return True
        except Exception as e:
            app_logger.warning(f"Neo4j upsert_entity failed for {ent_id}: {e}")
            return False

    async def upsert_relationship(self, tenant_id: str, rel_data: Dict[str, Any]) -> bool:
        """
        Idempotently persists a directed typed relationship with provenance metadata.
        Ensures both endpoints exist as Entity nodes.
        """
        driver = await neo4j_client.get_driver()
        if not driver:
            return False

        rel_id = rel_data.get("id") or f"{rel_data.get('source_id')}-{rel_data.get('target_id')}"
        src_id = str(rel_data.get("source_id") or rel_data.get("source_entity_value"))
        tgt_id = str(rel_data.get("target_id") or rel_data.get("target_entity_value"))
        rel_type = self._sanitize_rel_type(rel_data.get("type") or rel_data.get("relationship_type"))
        confidence = float(rel_data.get("confidence", 0.9))
        basis = str(rel_data.get("basis", "DIRECT_OBSERVATION"))
        is_inferred = bool(rel_data.get("is_inferred", False))
        inference_method = rel_data.get("inference_method") or ""
        evidence_ids = list(rel_data.get("evidence_ids", []))
        source = str(rel_data.get("source", "OSINT"))
        inv_id = str(rel_data.get("investigation_id", ""))

        cypher = f"""
        MERGE (s:Entity {{id: $src_id, tenant_id: $tenant_id}})
        ON CREATE SET s.value = $src_id, s.type = 'entity', s.last_seen = datetime()
        MERGE (t:Entity {{id: $tgt_id, tenant_id: $tenant_id}})
        ON CREATE SET t.value = $tgt_id, t.type = 'entity', t.last_seen = datetime()
        MERGE (s)-[r:{rel_type} {{id: $rel_id, tenant_id: $tenant_id}}]->(t)
        SET r.confidence = $confidence,
            r.basis = $basis,
            r.is_inferred = $is_inferred,
            r.inference_method = $inference_method,
            r.evidence_ids = $evidence_ids,
            r.source = $source,
            r.investigation_id = $inv_id,
            r.last_seen = datetime()
        RETURN r.id AS id
        """

        try:
            async with driver.session() as session:
                await session.run(
                    cypher,
                    src_id=src_id,
                    tgt_id=tgt_id,
                    rel_id=rel_id,
                    tenant_id=tenant_id,
                    confidence=confidence,
                    basis=basis,
                    is_inferred=is_inferred,
                    inference_method=inference_method,
                    evidence_ids=evidence_ids,
                    source=source,
                    inv_id=inv_id
                )
            return True
        except Exception as e:
            app_logger.warning(f"Neo4j upsert_relationship failed for {rel_id}: {e}")
            return False

    async def expand_entity_1hop(
        self,
        tenant_id: str,
        entity_id_or_val: str,
        limit: int = 25,
        relationship_types: Optional[List[str]] = None,
        min_confidence: Optional[float] = None,
        investigation_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Executes bounded 1-hop traversal in Neo4j.
        Returns connected nodes, verified typed edges, and metadata.
        Returns None if Neo4j is unavailable so caller can fall back.
        """
        driver = await neo4j_client.get_driver()
        if not driver:
            return None

        clean_val = entity_id_or_val.strip()
        type_filter = ""
        if relationship_types:
            clean_types = [self._sanitize_rel_type(t) for t in relationship_types]
            type_filter = f"AND type(r) IN {json.dumps(clean_types)}"

        conf_filter = ""
        if min_confidence is not None:
            conf_filter = "AND r.confidence >= $min_conf"

        inv_filter = ""
        if investigation_id:
            inv_filter = "AND (r.investigation_id = $inv_id OR r.investigation_id = '')"

        cypher = f"""
        MATCH (s:Entity)
        WHERE s.tenant_id = $tenant_id 
          AND (s.id = $clean_val OR toLower(s.value) = toLower($clean_val))
        MATCH (s)-[r]-(t:Entity)
        WHERE r.tenant_id = $tenant_id
          {type_filter}
          {conf_filter}
          {inv_filter}
        RETURN properties(s) AS s, properties(r) AS r, properties(t) AS t, type(r) AS rel_type,
               startNode(r).id AS start_id, endNode(r).id AS end_id
        LIMIT $limit
        """

        try:
            nodes_by_id = {}
            edges = []

            async with driver.session() as session:
                result = await session.run(
                    cypher,
                    tenant_id=tenant_id,
                    clean_val=clean_val,
                    min_conf=min_confidence or 0.0,
                    inv_id=investigation_id or "",
                    limit=limit + 1
                )
                records = await result.data()

                def _clean_props(p: Dict[str, Any]) -> Dict[str, Any]:
                    out = dict(p)
                    for k, v in out.items():
                        if hasattr(v, "iso_format"):
                            out[k] = v.iso_format()
                        elif hasattr(v, "__str__") and "DateTime" in type(v).__name__:
                            out[k] = str(v)
                    return out

                seed_node_data = None
                for rec in records:
                    s_props = _clean_props(rec["s"])
                    t_props = _clean_props(rec["t"])
                    r_props = _clean_props(rec["r"])

                    if seed_node_data is None and (s_props.get("id") == clean_val or str(s_props.get("value", "")).lower() == clean_val.lower()):
                        seed_node_data = s_props

                    nodes_by_id[s_props["id"]] = s_props
                    nodes_by_id[t_props["id"]] = t_props

                    edges.append({
                        "id": r_props.get("id") or f"{rec['start_id']}-{rec['end_id']}",
                        "source_id": rec["start_id"],
                        "target_id": rec["end_id"],
                        "type": rec["rel_type"],
                        "label": rec["rel_type"].replace("_", " ").lower(),
                        "confidence": float(r_props.get("confidence", 0.9)),
                        "basis": r_props.get("basis", "DIRECT_OBSERVATION"),
                        "is_inferred": bool(r_props.get("is_inferred", False)),
                        "evidence_ids": list(r_props.get("evidence_ids", [])),
                        "source": r_props.get("source", "Graph"),
                        "investigation_id": r_props.get("investigation_id", ""),
                        "last_seen": str(r_props.get("last_seen", ""))
                    })

                has_more = len(edges) > limit
                bounded_edges = edges[:limit]

                return {
                    "seed_entity_id": clean_val,
                    "seed_entity": seed_node_data or {"id": clean_val, "value": clean_val},
                    "hop_count": 1,
                    "nodes": list(nodes_by_id.values()),
                    "edges": bounded_edges,
                    "has_more": has_more,
                    "total_edges": len(edges)
                }

        except Exception as e:
            app_logger.warning(f"Neo4j expand_entity_1hop query failed: {e}")
            return None

    async def sync_from_mongodb(self, tenant_id: str) -> Dict[str, int]:
        """
        Idempotent backfill migration: reads existing entities and relationships
        from MongoDB/memory store and merges them into Neo4j.
        """
        from app.infrastructure.mongodb.repositories import entity_repo, relationship_repo

        entities = await entity_repo.list_by_tenant(tenant_id)
        relationships = await relationship_repo.list_by_tenant(tenant_id)

        synced_entities = 0
        synced_relationships = 0

        for ent in entities:
            ok = await self.upsert_entity(tenant_id, ent)
            if ok:
                synced_entities += 1

        for rel in relationships:
            ok = await self.upsert_relationship(tenant_id, rel)
            if ok:
                synced_relationships += 1

        app_logger.info(
            f"Neo4j sync completed for tenant {tenant_id}: {synced_entities} entities, {synced_relationships} relationships"
        )
        return {
            "synced_entities": synced_entities,
            "synced_relationships": synced_relationships,
            "total_entities_evaluated": len(entities),
            "total_relationships_evaluated": len(relationships)
        }

neo4j_graph_service = Neo4jGraphService()
neo4j_service = neo4j_graph_service
