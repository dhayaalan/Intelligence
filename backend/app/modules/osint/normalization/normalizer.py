from typing import Any, Dict, List
from app.module_sdk.models import (
    EntityPayload, EntityType, EvidencePayload,
    RelationshipPayload, RelationshipType
)
from app.module_sdk.sdk import ModuleSDK

class OsintNormalizer:
    """Normalizes raw outputs from OSINT provider adapters into core intelligence representations."""
    
    @staticmethod
    def normalize_spiderfoot(target: str, raw_data: Dict[str, Any]) -> List[EntityPayload]:
        entities = []
        for item in raw_data.get("discovered", []):
            try:
                e_type = EntityType(item["type"].lower())
                entities.append(ModuleSDK.create_entity(
                    entity_type=e_type,
                    value=item["value"],
                    confidence=item.get("confidence", 0.8),
                    sources=["spiderfoot"],
                    metadata={"provider": "spiderfoot"}
                ))
            except Exception:
                pass
        return entities

    @staticmethod
    def normalize_shodan(target: str, raw_data: Dict[str, Any]) -> List[EntityPayload]:
        entities = []
        if raw_data.get("org"):
            entities.append(ModuleSDK.create_entity(
                entity_type=EntityType.ORGANIZATION,
                value=raw_data["org"],
                confidence=0.9,
                sources=["shodan"],
                metadata={"asn": raw_data.get("asn")}
            ))
        if raw_data.get("lat") is not None and raw_data.get("lng") is not None:
            entities.append(ModuleSDK.create_entity(
                entity_type=EntityType.IP,
                value=raw_data.get("ip", target),
                confidence=0.95,
                sources=["shodan"],
                metadata={
                    "asn": raw_data.get("asn"),
                    "isp": raw_data.get("isp"),
                    "org": raw_data.get("org"),
                    "city": raw_data.get("city"),
                    "country": raw_data.get("country"),
                    "countryCode": raw_data.get("country_code"),
                    "lat": raw_data.get("lat"),
                    "lng": raw_data.get("lng")
                }
            ))
        return entities

    @staticmethod
    def normalize_theharvester(target: str, raw_data: Dict[str, Any]) -> List[EntityPayload]:
        entities = []
        for email in raw_data.get("emails", []):
            entities.append(ModuleSDK.create_entity(
                entity_type=EntityType.EMAIL,
                value=email,
                confidence=0.85,
                sources=["theharvester"]
            ))
        for host in raw_data.get("hosts", []):
            entities.append(ModuleSDK.create_entity(
                entity_type=EntityType.SUBDOMAIN,
                value=host,
                confidence=0.9,
                sources=["theharvester"]
            ))
        return entities

    @staticmethod
    def normalize_image(target: str, raw_data: Dict[str, Any]) -> List[EntityPayload]:
        entities = []
        for ent in raw_data.get("entities", []):
            try:
                if isinstance(ent, dict):
                    entities.append(EntityPayload(**ent))
            except Exception:
                pass
        return entities

osint_normalizer = OsintNormalizer()
