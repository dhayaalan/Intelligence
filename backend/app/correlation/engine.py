from typing import Dict, List, Set, Tuple
from app.module_sdk.models import (
    EntityPayload, EntityType, NormalizedModuleResult,
    RelationshipPayload, RelationshipType, EvidencePayload
)

class CorrelationEngine:
    """Core correlation engine synthesizing normalized findings from independent intelligence modules."""
    
    @staticmethod
    def correlate_module_results(
        target_query: str,
        target_type: str,
        results: List[NormalizedModuleResult]
    ) -> Tuple[List[EntityPayload], List[RelationshipPayload], List[EvidencePayload]]:
        """Deduplicates, merges, and infers relationships across all participating modules."""
        
        entities_by_key: Dict[Tuple[str, str], EntityPayload] = {}
        relationships_by_key: Dict[Tuple[str, str, str], RelationshipPayload] = {}
        all_evidence: List[EvidencePayload] = []
        
        # 1. Ingest all module entities and merge identical ones
        for mod_res in results:
            if mod_res.status == "failed":
                continue
                
            for ent in mod_res.entities:
                key = (ent.type.value, ent.value.lower().strip())
                if key in entities_by_key:
                    existing = entities_by_key[key]
                    # Merge sources
                    merged_sources = list(set(existing.sources + ent.sources))
                    existing.sources = merged_sources
                    # Boost confidence when multiple independent modules/providers discover the same entity
                    existing.confidence = min(1.0, existing.confidence + 0.1)
                    # Merge module metadata
                    existing.metadata.update(ent.metadata)
                else:
                    entities_by_key[key] = EntityPayload(
                        id=ent.id,
                        type=ent.type,
                        value=ent.value.strip(),
                        confidence=ent.confidence,
                        sources=list(set(ent.sources)),
                        metadata=dict(ent.metadata)
                    )
            
            # Merge relationships
            for rel in mod_res.relationships:
                rel_key = (
                    rel.source_entity_value.lower().strip(),
                    rel.relationship_type.value,
                    rel.target_entity_value.lower().strip()
                )
                if rel_key in relationships_by_key:
                    existing_rel = relationships_by_key[rel_key]
                    existing_rel.sources = list(set(existing_rel.sources + rel.sources))
                    existing_rel.confidence = min(1.0, existing_rel.confidence + 0.05)
                    existing_rel.metadata.update(rel.metadata)
                else:
                    relationships_by_key[rel_key] = rel
                    
            # Ingest evidence
            all_evidence.extend(mod_res.evidence)
            
        # 2. Only infer root relationships between Target Query and top discovered entities if few real relationships exist
        correlated_entities = list(entities_by_key.values())
        if len(relationships_by_key) < 10:
            for ent in correlated_entities[:8]:
                if ent.value.lower().strip() == target_query.lower().strip():
                    continue
                    
                inferred_type = RelationshipType.DISCOVERED_FROM
                if target_type in ["domain", "subdomain"] and ent.type == EntityType.IP:
                    inferred_type = RelationshipType.RESOLVES_TO
                elif target_type in ["domain"] and ent.type == EntityType.SUBDOMAIN:
                    inferred_type = RelationshipType.CONTAINS
                elif ent.type in [EntityType.VULNERABILITY, EntityType.THREAT_INDICATOR]:
                    inferred_type = RelationshipType.EXPOSED_BY
                elif ent.type in [EntityType.PERSON, EntityType.EMAIL, EntityType.USERNAME]:
                    inferred_type = RelationshipType.ASSOCIATED_WITH
                    
                rel_key = (target_query.lower().strip(), inferred_type.value, ent.value.lower().strip())
                if rel_key not in relationships_by_key:
                    relationships_by_key[rel_key] = RelationshipPayload(
                        source_entity_value=target_query,
                        target_entity_value=ent.value,
                        relationship_type=inferred_type,
                        confidence=ent.confidence,
                        sources=ent.sources,
                        metadata={"inferred_by": "core_correlation_engine"}
                    )

        return (
            correlated_entities,
            list(relationships_by_key.values()),
            all_evidence
        )

correlation_engine = CorrelationEngine()
