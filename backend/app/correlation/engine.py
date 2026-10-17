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
                    # Check for genuinely new independent sources
                    new_sources = set(ent.sources) - set(existing.sources)
                    existing.sources = list(set(existing.sources + ent.sources))
                    
                    # Boost confidence only when an independent source corroborates the entity
                    if new_sources:
                        existing.confidence = min(1.0, round(existing.confidence + 0.1, 2))
                    
                    # Merge module metadata without discarding valid corroboration
                    for m_key, m_val in ent.metadata.items():
                        if m_key in ("platform", "platforms"):
                            plat_list = existing.metadata.get("platforms")
                            if not plat_list:
                                orig_plat = existing.metadata.get("platform")
                                plat_list = [orig_plat] if orig_plat else []
                            if isinstance(m_val, list):
                                plat_list.extend(m_val)
                            elif m_val and m_val not in plat_list:
                                plat_list.append(m_val)
                            existing.metadata["platforms"] = list(set(plat_list))
                        elif m_key in ("profile_url", "profile_urls", "url", "urls"):
                            url_list = existing.metadata.get("profile_urls")
                            if not url_list:
                                orig_url = existing.metadata.get("profile_url") or existing.metadata.get("url")
                                url_list = [orig_url] if orig_url else []
                            if isinstance(m_val, list):
                                url_list.extend(m_val)
                            elif m_val and m_val not in url_list:
                                url_list.append(m_val)
                            existing.metadata["profile_urls"] = list(set(url_list))
                        elif m_key not in existing.metadata:
                            existing.metadata[m_key] = m_val

                    # Corroboration metrics
                    existing.metadata["corroborating_sources_count"] = len(existing.sources)
                    
                    # Preserve distinction: USERNAME_MATCH vs PROFILE_MATCH vs CONFIRMED_IDENTITY
                    if len(existing.sources) >= 3 and existing.metadata.get("profile_urls"):
                        existing.metadata["match_type"] = "CORROBORATED_PROFILE"
                    elif existing.type == EntityType.USERNAME:
                        existing.metadata.setdefault("match_type", "USERNAME_MATCH")
                    elif existing.type == EntityType.PERSON:
                        existing.metadata.setdefault("match_type", "PROFILE_MATCH")
                else:
                    initial_meta = dict(ent.metadata)
                    initial_meta["corroborating_sources_count"] = len(ent.sources)
                    if ent.type == EntityType.USERNAME:
                        initial_meta.setdefault("match_type", "USERNAME_MATCH")
                    elif ent.type == EntityType.PERSON:
                        initial_meta.setdefault("match_type", "PROFILE_MATCH")
                    elif ent.type in (EntityType.ORGANIZATION, EntityType.DOMAIN, EntityType.IP):
                        initial_meta.setdefault("match_type", "IDENTIFIER_MATCH")

                    entities_by_key[key] = EntityPayload(
                        id=ent.id,
                        type=ent.type,
                        value=ent.value.strip(),
                        confidence=ent.confidence,
                        sources=list(set(ent.sources)),
                        metadata=initial_meta
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
            
        # 2. Preserve genuine module relationships and set explicit provenance / basis
        correlated_entities = list(entities_by_key.values())
        for rel in relationships_by_key.values():
            if "basis" not in rel.metadata:
                rel.metadata["basis"] = "DIRECT_OBSERVATION"
                rel.metadata["is_inferred"] = False

        return (
            correlated_entities,
            list(relationships_by_key.values()),
            all_evidence
        )

correlation_engine = CorrelationEngine()
