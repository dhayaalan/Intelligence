from typing import Any, Dict, List
from app.module_sdk.models import (
    EntityPayload, EntityType, EvidencePayload,
    RelationshipPayload, RelationshipType
)
from app.module_sdk.sdk import ModuleSDK

class ThreatNormalizer:
    @staticmethod
    def normalize_dns(target: str, raw_data: Dict[str, Any]) -> List[EntityPayload]:
        entities = []
        records = raw_data.get("records", {})
        for ip in records.get("A", []):
            entities.append(ModuleSDK.create_entity(
                entity_type=EntityType.IP,
                value=ip,
                confidence=0.98,
                sources=["dns_intel"],
                metadata={"dns_record": "A"}
            ))
        for ns in records.get("NS", []):
            entities.append(ModuleSDK.create_entity(
                entity_type=EntityType.HOSTNAME,
                value=ns,
                confidence=0.9,
                sources=["dns_intel"],
                metadata={"dns_record": "NS"}
            ))
        return entities

    @staticmethod
    def normalize_vulnerabilities(target: str, raw_data: Dict[str, Any]) -> List[EntityPayload]:
        entities = []
        for v in raw_data.get("vulnerabilities", []):
            entities.append(ModuleSDK.create_entity(
                entity_type=EntityType.VULNERABILITY,
                value=v["cve_id"],
                confidence=0.95,
                sources=["vulnerability_intel"],
                metadata={
                    "cvss_score": v.get("cvss_score"),
                    "severity": v.get("severity"),
                    "description": v.get("description")
                }
            ))
        return entities

    @staticmethod
    def normalize_ioc(target: str, raw_data: Dict[str, Any]) -> List[EntityPayload]:
        entities = []
        for ind in raw_data.get("indicators", []):
            entities.append(ModuleSDK.create_entity(
                entity_type=EntityType.THREAT_INDICATOR,
                value=ind["indicator"],
                confidence=ind.get("confidence", 0.9),
                sources=["ioc_feed"],
                metadata={
                    "type": ind.get("type"),
                    "malware_family": ind.get("malware_family")
                }
            ))
        return entities

threat_normalizer = ThreatNormalizer()
