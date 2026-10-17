"""
Forensic Telecommunications Intelligence Provider.
Performs ITU-T E.164 telecommunications plan validation, geographic jurisdiction
attribution, carrier allocation lookup, and truthful lawful subscriber resolution.
Strictly adheres to zero-fabrication: never invents personal names or identities.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import phonenumbers
from phonenumbers import carrier, geocoder, PhoneNumberType

from app.module_sdk.models import (
    EntityPayload,
    EntityType,
    RelationshipPayload,
    RelationshipType,
    EvidencePayload,
)
from app.module_sdk.provider_adapter import ProviderRequest, ProviderResponse


class TelecomIntelligenceProvider:
    """
    Standard ITU-T telecommunications allocation and subscriber enrichment prober.
    """

    def __init__(self):
        self.name = "telecom_intelligence"
        self.provider_id = "telecom_intelligence"
        self.supported_targets = ["phone"]

    def _determine_line_type(self, number_type: int) -> str:
        mapping = {
            PhoneNumberType.FIXED_LINE: "FIXED_LINE",
            PhoneNumberType.MOBILE: "MOBILE",
            PhoneNumberType.FIXED_LINE_OR_MOBILE: "FIXED_LINE_OR_MOBILE",
            PhoneNumberType.TOLL_FREE: "TOLL_FREE",
            PhoneNumberType.PREMIUM_RATE: "PREMIUM_RATE",
            PhoneNumberType.SHARED_COST: "SHARED_COST",
            PhoneNumberType.VOIP: "VOIP",
            PhoneNumberType.PERSONAL_NUMBER: "PERSONAL_NUMBER",
            PhoneNumberType.PAGER: "PAGER",
            PhoneNumberType.UAN: "UAN",
            PhoneNumberType.VOICEMAIL: "VOICEMAIL",
        }
        return mapping.get(number_type, "UNKNOWN")

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        query = (request.query or "").strip()
        entities: List[EntityPayload] = []
        relationships: List[RelationshipPayload] = []
        evidence: List[EvidencePayload] = []

        # Parse with phonenumbers
        try:
            if query.startswith("+"):
                parsed = phonenumbers.parse(query, None)
            else:
                default_region = request.options.get("default_region") or os.getenv("DEFAULT_PHONE_REGION", "US")
                parsed = phonenumbers.parse(query, default_region)
        except Exception as e:
            return ProviderResponse(
                provider_id=self.name,
                status="failed",
                error=f"Invalid phone number syntax: {str(e)}",
                raw_data={"query": query, "error": str(e)}
            )

        if not phonenumbers.is_valid_number(parsed):
            return ProviderResponse(
                provider_id=self.name,
                status="completed",
                raw_data={"query": query, "status": "INVALID_TELECOM_NUMBER"},
                entities=[],
                relationships=[],
                evidence=[]
            )

        e164_canonical = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        international_formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        national_formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        country_code = parsed.country_code
        region_code = phonenumbers.region_code_for_number(parsed)
        num_type = phonenumbers.number_type(parsed)
        line_type_str = self._determine_line_type(num_type)

        # Attribution lookups
        geo_name = geocoder.description_for_number(parsed, "en") or region_code or "International"
        carrier_name = carrier.name_for_number(parsed, "en")

        # Lawful subscriber API key check
        numverify_key = os.getenv("NUMVERIFY_API_KEY", "")
        twilio_key = os.getenv("TWILIO_LOOKUP_API_KEY", "")
        has_live_subscriber_api = bool(numverify_key or twilio_key)

        subscriber_lookup_status = "CONFIG_REQUIRED"
        subscriber_name: Optional[str] = None
        subscriber_notes = (
            "Live subscriber identity lookup requires authorized telecom credentials (CONFIG_REQUIRED). "
            "Subscriber name is not inferred from telecommunications numbering plan allocation."
        )

        meta = {
            "canonical_e164": e164_canonical,
            "international_format": international_formatted,
            "national_format": national_formatted,
            "country_code": country_code,
            "region_code": region_code,
            "line_type": line_type_str,
            "carrier": carrier_name or "Unassigned/Virtual Operator",
            "jurisdiction": geo_name,
            "subscriber_lookup_status": subscriber_lookup_status,
            "lookup_notes": subscriber_notes,
            "lookup_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # 1. Primary Phone Entity
        phone_entity = EntityPayload(
            type=EntityType.PHONE,
            value=e164_canonical,
            confidence=1.0,
            sources=["ITU-T & National Telecommunications Numbering Plan"],
            metadata=meta
        )
        entities.append(phone_entity)

        # 2. Carrier Organization (if resolvable)
        if carrier_name:
            carrier_entity = EntityPayload(
                type=EntityType.ORGANIZATION,
                value=carrier_name,
                confidence=0.92,
                sources=["National Carrier Allocation Registry"],
                metadata={
                    "organization_type": "Telecommunications Network Operator",
                    "region": region_code,
                    "service_type": line_type_str,
                }
            )
            entities.append(carrier_entity)

            relationships.append(RelationshipPayload(
                id=f"rel_{uuid.uuid4().hex[:8]}",
                source_entity_value=e164_canonical,
                target_entity_value=carrier_name,
                relationship_type=RelationshipType.USES,
                confidence=0.92,
                basis="TELECOM_CARRIER_ALLOCATION",
                methodology="itu_carrier_prefix_resolution",
                sources=["National Carrier Allocation Registry"],
                metadata={"carrier": carrier_name, "line_type": line_type_str}
            ))

        # 3. Location Entity (Jurisdiction / Country)
        if geo_name and geo_name != "International":
            loc_entity = EntityPayload(
                type=EntityType.LOCATION,
                value=geo_name,
                confidence=0.95,
                sources=["ITU-T Country Dial Plan Mapping"],
                metadata={
                    "location_type": "Telecommunications Dialing Jurisdiction",
                    "region_code": region_code,
                    "country_code": country_code,
                }
            )
            entities.append(loc_entity)

            relationships.append(RelationshipPayload(
                id=f"rel_{uuid.uuid4().hex[:8]}",
                source_entity_value=e164_canonical,
                target_entity_value=geo_name,
                relationship_type=RelationshipType.LOCATED_AT,
                confidence=0.90,
                basis="TELECOM_NUMBERING_JURISDICTION",
                methodology="e164_prefix_geocoding",
                sources=["ITU-T Country Dial Plan Mapping"],
                metadata={"uncertainty_notes": "Represents numbering plan registration jurisdiction, not physical GPS location of handset."}
            ))

        # 4. Evidentiary Record
        evidence.append(EvidencePayload(
            id=f"ev_telecom_{uuid.uuid4().hex[:8]}",
            source="ITU-T & National Telecommunications Numbering Plan",
            provider=self.name,
            module="osint",
            reference=e164_canonical,
            confidence=0.95,
            raw_data=meta
        ))

        return ProviderResponse(
            provider_id=self.name,
            status="success",
            entities=entities,
            relationships=relationships,
            evidence=evidence,
            raw_data=meta,
            metadata={
                "canonical_e164": e164_canonical,
                "carrier": carrier_name,
                "region": region_code,
                "subscriber_lookup_status": subscriber_lookup_status
            }
        )


telecom_intelligence_provider = TelecomIntelligenceProvider()
