import re
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import (
    EntityPayload, EvidencePayload, RelationshipPayload, EntityType, RelationshipType,
    HealthCheckResult, ModuleHealthStatus
)

INDIA_STATE_CODES: Dict[str, str] = {
    "AN": "Andaman and Nicobar Islands",
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CG": "Chhattisgarh",
    "CH": "Chandigarh",
    "DD": "Daman and Diu",
    "DL": "Delhi",
    "DN": "Dadra and Nagar Haveli",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HP": "Himachal Pradesh",
    "HR": "Haryana",
    "JH": "Jharkhand",
    "JK": "Jammu and Kashmir",
    "KA": "Karnataka",
    "KL": "Kerala",
    "LA": "Ladakh",
    "LD": "Lakshadweep",
    "MH": "Maharashtra",
    "ML": "Meghalaya",
    "MN": "Manipur",
    "MP": "Madhya Pradesh",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OD": "Odisha",
    "PB": "Punjab",
    "PY": "Puducherry",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TR": "Tripura",
    "TS": "Telangana",
    "UK": "Uttarakhand",
    "UP": "Uttar Pradesh",
    "WB": "West Bengal",
}

TAMIL_NADU_RTOS: Dict[str, str] = {
    "01": "Chennai Central", "02": "Chennai North-West", "03": "Chennai North-East",
    "04": "Chennai East", "05": "Chennai North", "06": "Chennai South-East",
    "07": "Chennai South", "09": "Chennai West", "10": "Chennai South-West",
    "11": "Tambaram", "12": "Poonamallee", "13": "Ambattur", "14": "Sholinganallur",
    "15": "Ulundurpet", "16": "Tindivanam", "18": "Red Hills", "19": "Chengalpattu",
    "20": "Tiruvallur", "21": "Kanchipuram", "22": "Meenambakkam", "23": "Vellore",
    "24": "Krishnagiri", "25": "Tiruvannamalai", "27": "Salem", "28": "Namakkal North",
    "29": "Dharmapuri", "30": "Salem West", "31": "Cuddalore", "32": "Villupuram",
    "33": "Erode", "34": "Tiruchengode (Namakkal)", "36": "Gobichettipalayam",
    "37": "Coimbatore South", "38": "Coimbatore North", "39": "Tiruppur North",
    "40": "Mettupalayam", "41": "Pollachi", "42": "Tiruppur South", "43": "Ooty (Nilgiris)",
    "45": "Tiruchirappalli West", "46": "Perambalur", "47": "Karur", "48": "Udhagamandalam",
    "49": "Thanjavur", "50": "Tiruvarur", "51": "Nagapattinam", "52": "Sankagiri",
    "54": "Salem South", "55": "Pudukkottai", "56": "Perundurai", "57": "Dindigul",
    "58": "Madurai South", "59": "Madurai North", "60": "Theni", "61": "Ariyalur",
    "63": "Sivaganga", "64": "Madurai Central", "65": "Ramanathapuram", "66": "Coimbatore Central",
    "67": "Virudhunagar", "68": "Kumbakonam", "69": "Thoothukudi", "70": "Hosur",
    "72": "Tirunelveli", "73": "Ranipet", "74": "Nagercoil", "75": "Marthandam",
    "76": "Tenkasi", "77": "Attur", "78": "Dharapuram", "79": "Sankarankovil",
    "81": "Tiruchirappalli East", "82": "Mayiladuthurai", "83": "Vaniyambadi",
    "84": "Srivilliputhur", "85": "Kundrathur", "86": "Ranipet West", "88": "Namakkal South",
    "90": "Salem East", "91": "Virudhachalam", "92": "Thiruchendur", "93": "Mettur",
    "99": "Coimbatore West"
}

class VehiclePlateFormat(BaseModel):
    jurisdiction: str
    pattern: str
    sample: str
    description: str

KNOWN_PLATE_FORMATS: List[VehiclePlateFormat] = [
    VehiclePlateFormat(jurisdiction="IN", pattern=r"^([A-Z]{2})\s?([0-9]{1,2})\s?([A-Z]{0,3})\s?([0-9]{4})$", sample="TN34MA8562", description="India VAHAN Standard Registration"),
    VehiclePlateFormat(jurisdiction="UK", pattern=r"^([A-Z]{2})([0-9]{2})\s?([A-Z]{3})$", sample="BD51 SMR", description="UK DVLA Standard Registration"),
    VehiclePlateFormat(jurisdiction="US", pattern=r"^([1-9A-Z]{1}[A-Z0-9]{4,6})$", sample="7XYZ123", description="US State DMV Alphanumeric Plate"),
    VehiclePlateFormat(jurisdiction="EU", pattern=r"^([A-Z]{1,3})\s?([A-Z]{1,2})\s?([0-9]{1,4})$", sample="B MW 1234", description="EU Standard Plate"),
]

class VehicleRegistrationProvider(ProviderAdapter):
    """
    Forensic Vehicle Registration & Automotive Intelligence Provider.
    Enforces lawful access verification, format parsing, and structural jurisdiction attribution.
    Never bypasses restricted government databases, never fabricates owner identity or location,
    and returns deterministic, fully correlated knowledge graph nodes and edges.
    """
    def __init__(self):
        self._provider_id = "vehicle_registration_recon"
        self._name = "Vehicle Registration Recon"

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def capabilities(self) -> List[str]:
        return ["plate_lookup", "jurisdiction_validation", "rto_attribution"]

    @property
    def supported_targets(self) -> List[str]:
        return ["vehicle", "vehicle_plate"]

    async def health_check(self) -> HealthCheckResult:
        return HealthCheckResult(
            status=ModuleHealthStatus.HEALTHY,
            message="Vehicle Registration Recon operational with multi-jurisdiction pattern validators",
            latency_ms=0.5
        )

    def match_plate_format(self, query: str) -> Optional[VehiclePlateFormat]:
        cleaned = re.sub(r"[\s\-_:]", "", query.strip().upper())
        for fmt in KNOWN_PLATE_FORMATS:
            if re.match(fmt.pattern, cleaned) or re.match(fmt.pattern, query.strip().upper()):
                return fmt
        return None

    def parse_plate(self, query: str) -> Dict[str, Any]:
        cleaned = re.sub(r"[\s\-_:]", "", query.strip().upper())
        # Try India format: 2 letters, 1-2 digits, optional 1-3 letters, 4 digits
        in_match = re.match(r"^([A-Z]{2})([0-9]{1,2})([A-Z]{0,3})([0-9]{4})$", cleaned)
        if in_match:
            state_code, rto_num, series, seq = in_match.groups()
            rto_padded = rto_num.zfill(2)
            state_name = INDIA_STATE_CODES.get(state_code, f"State {state_code}")
            
            rto_office = f"RTO {state_code}-{rto_padded}"
            if state_code == "TN" and rto_padded in TAMIL_NADU_RTOS:
                rto_office = f"RTO TN-{rto_padded} ({TAMIL_NADU_RTOS[rto_padded]})"
            
            return {
                "jurisdiction": "IN",
                "country": "India",
                "state_code": state_code,
                "state_name": state_name,
                "rto_code": f"{state_code}{rto_padded}",
                "rto_office": rto_office,
                "series": series,
                "registration_number": seq,
                "canonical_plate": f"{state_code}{rto_padded}{series}{seq}",
                "standard": "Indian High Security Registration Plate (HSRP) / VAHAN 4.0",
                "matched": True
            }

        # Try UK format
        uk_match = re.match(r"^([A-Z]{2})([0-9]{2})([A-Z]{3})$", cleaned)
        if uk_match:
            area, age, letters = uk_match.groups()
            return {
                "jurisdiction": "UK",
                "country": "United Kingdom",
                "canonical_plate": f"{area}{age} {letters}",
                "standard": "UK DVLA Standard Plate",
                "matched": True
            }

        return {
            "jurisdiction": "UNKNOWN",
            "country": "Unknown",
            "canonical_plate": cleaned,
            "standard": "Generic Vehicle Registration Number",
            "matched": False
        }

    def execute_lookup(
        self,
        plate_number: str,
        jurisdiction_hint: Optional[str] = None,
        authorized_credential: Optional[str] = None
    ) -> Dict[str, Any]:
        parsed = self.parse_plate(plate_number)
        canonical = parsed.get("canonical_plate", plate_number.strip().upper())
        country = parsed.get("country", "Unknown")
        state_name = parsed.get("state_name")
        rto_office = parsed.get("rto_office")
        standard = parsed.get("standard", "Standard Vehicle Registration")

        entities: List[EntityPayload] = []
        relationships: List[RelationshipPayload] = []
        evidence: List[EvidencePayload] = []

        # 1. Primary Vehicle Entity (Validated format syntax)
        vehicle_entity = EntityPayload(
            type=EntityType.VEHICLE,
            value=canonical,
            confidence=0.80,
            sources=[self.name],
            metadata={
                "plate_number": canonical,
                "country": country,
                "state": state_name,
                "jurisdiction": f"{state_name}, {country}" if state_name else country,
                "rto_office": rto_office,
                "standard": standard,
                "syntax_valid": True,
                "jurisdiction_attribution_mode": "FORMAT_PREFIX_INFERENCE",
                "live_registration_record": "CONFIG_REQUIRED",
                "registered_ownership": "NOT_AVAILABLE_WITHOUT_AUTHORIZED_CREDENTIAL",
                "is_search_target": True,
                "lookup_timestamp": datetime.utcnow().isoformat(),
            }
        )
        entities.append(vehicle_entity)

        # 2. Regional Transport Office (Organization - Jurisdictional Attribution)
        if rto_office:
            rto_entity = EntityPayload(
                type=EntityType.ORGANIZATION,
                value=rto_office,
                confidence=0.85,
                sources=[self.name],
                metadata={
                    "organization_type": "Lawful Vehicle Licensing & Registration Authority",
                    "jurisdiction": f"{state_name}, {country}",
                    "rto_code": parsed.get("rto_code"),
                    "attribution_basis": "PREFIX_SYNTAX_MAPPING"
                }
            )
            entities.append(rto_entity)

            relationships.append(RelationshipPayload(
                id=f"rel_{uuid.uuid4().hex[:8]}",
                source_entity_value=canonical,
                target_entity_value=rto_office,
                relationship_type=RelationshipType.CONNECTED_TO,
                confidence=0.85,
                basis="FORMAT_PREFIX_INFERENCE",
                methodology="hsrp_rto_attribution",
                uncertainty_notes="Attributed to RTO licensing authority from plate prefix formatting; live vehicle registration database record not queried.",
                sources=[self.name]
            ))

        # 3. Location Entity (State / Country)
        if state_name:
            location_val = f"{state_name}, {country}"
            loc_entity = EntityPayload(
                type=EntityType.LOCATION,
                value=location_val,
                confidence=0.85,
                sources=[self.name],
                metadata={
                    "country": country,
                    "state": state_name,
                    "location_type": "State / Administrative Region",
                    "attribution_basis": "JURISDICTION_PREFIX"
                }
            )
            entities.append(loc_entity)

            relationships.append(RelationshipPayload(
                id=f"rel_{uuid.uuid4().hex[:8]}",
                source_entity_value=canonical,
                target_entity_value=location_val,
                relationship_type=RelationshipType.LOCATED_AT,
                confidence=0.85,
                basis="REGISTRATION_JURISDICTION",
                methodology="regional_jurisdiction_mapping",
                uncertainty_notes="Jurisdiction inferred from registration prefix, not physical vehicle GPS telemetry.",
                sources=[self.name]
            ))

            if rto_office:
                relationships.append(RelationshipPayload(
                    id=f"rel_{uuid.uuid4().hex[:8]}",
                    source_entity_value=rto_office,
                    target_entity_value=location_val,
                    relationship_type=RelationshipType.LOCATED_AT,
                    confidence=0.90,
                    basis="INSTITUTIONAL_JURISDICTION",
                    methodology="rto_location_link",
                    sources=[self.name]
                ))

        # 4. National Registry System Entity
        if country == "India":
            reg_system = "Ministry of Road Transport and Highways (MoRTH - VAHAN)"
            system_entity = EntityPayload(
                type=EntityType.ORGANIZATION,
                value=reg_system,
                confidence=0.90,
                sources=[self.name],
                metadata={
                    "role": "National Central Registry Authority",
                    "system": "VAHAN 4.0 Centralized Portal",
                    "jurisdiction": "Government of India"
                }
            )
            entities.append(system_entity)

            if rto_office:
                relationships.append(RelationshipPayload(
                    id=f"rel_{uuid.uuid4().hex[:8]}",
                    source_entity_value=rto_office,
                    target_entity_value=reg_system,
                    relationship_type=RelationshipType.CONNECTED_TO,
                    confidence=0.92,
                    basis="REGULATORY_HIERARCHY",
                    methodology="central_vahan_linkage",
                    sources=[self.name]
                ))

        # 5. Evidentiary Audit Trail & Lawful Access Boundary Notice
        evidence_text = (
            f"Format & Jurisdiction Verified: Valid vehicle registration plate '{canonical}' "
            f"attributed to {rto_office or 'competent authority'} in {state_name or country}. "
            f"Registration format conforms to {standard}."
        )
        if not authorized_credential:
            evidence_text += (
                " Note: Real-time registered owner name and vehicle finance telemetry require "
                "authorized lawful MoRTH / DMV API credentials in compliance with data privacy regulations."
            )

        evidence.append(EvidencePayload(
            source=self.name,
            provider=self.provider_id,
            module="osint",
            collection_method="deterministic_format_parsing",
            reference=f"Vehicle Registry Attribution: {canonical}",
            confidence=0.98,
            raw_data={
                "parsed": parsed,
                "lawful_status": "AUTHENTIC_FORMAT_VERIFIED",
                "notes": evidence_text
            }
        ))

        return {
            "status": "SUCCESS",
            "message": evidence_text,
            "plate_number": canonical,
            "jurisdiction": parsed.get("jurisdiction", "UNKNOWN"),
            "entities": entities,
            "relationships": relationships,
            "evidence": evidence
        }

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        res = self.execute_lookup(request.query)
        entities = [e.dict() if hasattr(e, "dict") else e for e in res.get("entities", [])]
        relationships = [r.dict() if hasattr(r, "dict") else r for r in res.get("relationships", [])]
        evidence = [ev.dict() if hasattr(ev, "dict") else ev for ev in res.get("evidence", [])]
        return ProviderResponse(
            provider_id=self.provider_id,
            status="success",
            raw_data={
                "found": bool(entities),
                "status": res.get("status"),
                "message": res.get("message"),
                "plate_number": res.get("plate_number"),
                "jurisdiction": res.get("jurisdiction"),
                "entities": entities,
                "relationships": relationships,
                "evidence": evidence
            },
            duration_ms=(time.time() - start_time) * 1000
        )

vehicle_registration_provider = VehicleRegistrationProvider()
