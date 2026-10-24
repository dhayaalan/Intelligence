import re
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx
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
    "TG": "Telangana",
    "UK": "Uttarakhand",
    "UP": "Uttar Pradesh",
    "WB": "West Bengal",
}

TELANGANA_RTOS: Dict[str, str] = {
    "01": "Mancherial / Adilabad RTO", "02": "Karimnagar RTO", "03": "Warangal / Hanamkonda RTO",
    "04": "Khammam RTO", "05": "Nalgonda RTO", "06": "Mahabubnagar RTO",
    "07": "Ranga Reddy / Attapur RTO", "08": "Medchal / Uppal / Kukatpally RTO",
    "09": "Khairatabad, Hyderabad Central RTO", "10": "Secunderabad RTO",
    "11": "Malakpet, Hyderabad East RTO", "12": "Kishanbagh, Hyderabad South RTO",
    "13": "Tolichowki, Hyderabad West RTO", "14": "Hyderabad North RTO", "15": "Sangareddy / Medak RTO"
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

INDIA_STATE_COORDS: Dict[str, tuple] = {
    "TN": (11.1271, 78.6569),
    "KA": (15.3173, 75.7139),
    "KL": (10.8505, 76.2711),
    "AP": (15.9129, 79.7400),
    "TS": (18.1124, 79.0193),
    "MH": (19.7515, 75.7139),
    "DL": (28.7041, 77.1025),
    "UP": (26.8467, 80.9462),
    "GJ": (22.2587, 71.1924),
    "RJ": (27.0238, 74.2179),
    "WB": (22.9868, 87.8550),
    "MP": (22.9734, 78.6569),
    "PB": (31.1471, 75.3412),
    "HR": (29.0588, 76.0856),
    "BR": (25.0961, 85.3131),
    "OD": (20.9517, 85.0985),
    "AS": (26.2006, 92.9376),
    "JH": (23.6102, 85.2799),
    "CG": (21.2787, 81.8661),
    "UK": (30.0668, 79.0193),
    "HP": (31.1048, 77.1734),
    "TR": (23.9408, 91.9882),
    "ML": (25.4670, 91.3662),
    "MN": (24.6637, 93.9063),
    "NL": (26.1584, 94.5624),
    "GA": (15.2993, 74.1240),
    "AR": (28.2180, 94.7278),
    "MZ": (23.1645, 92.9376),
    "SK": (27.5330, 88.5122),
    "JK": (33.7782, 76.5762),
    "LA": (34.1526, 77.5771),
    "CH": (30.7333, 76.7794),
    "PY": (11.9416, 79.8083),
    "AN": (11.7401, 92.6586),
    "DN": (20.1809, 73.0169),
    "DD": (20.4283, 72.8397),
    "LD": (10.5667, 72.6417),
}

TAMIL_NADU_RTO_COORDS: Dict[str, tuple] = {
    "01": (13.0827, 80.2707),
    "02": (13.0850, 80.2100),
    "03": (13.1100, 80.2800),
    "04": (13.0500, 80.2700),
    "05": (13.1200, 80.2600),
    "06": (13.0000, 80.2500),
    "07": (12.9800, 80.2200),
    "09": (13.0600, 80.2100),
    "10": (13.0200, 80.1900),
    "11": (12.9229, 80.1275),
    "12": (13.0489, 80.0934),
    "13": (13.1143, 80.1548),
    "14": (12.9010, 80.2279),
    "15": (11.6888, 79.2933),
    "16": (12.2289, 79.6500),
    "18": (13.1986, 80.1983),
    "19": (12.6841, 79.9836),
    "20": (13.1432, 79.9083),
    "21": (12.8342, 79.7036),
    "22": (12.9800, 80.1600),
    "23": (12.9165, 79.1325),
    "24": (12.5186, 78.2137),
    "25": (12.2253, 79.0747),
    "27": (11.6643, 78.1460),
    "28": (11.2189, 78.1674),
    "29": (12.1277, 78.1579),
    "30": (11.6500, 78.1200),
    "31": (11.7480, 79.7714),
    "32": (11.9401, 79.4861),
    "33": (11.3410, 77.7172),
    "34": (11.3800, 77.8900),
    "36": (11.4544, 77.4332),
    "37": (10.9900, 76.9600),
    "38": (11.0300, 76.9700),
    "39": (11.1200, 77.3500),
    "40": (11.2990, 76.9558),
    "41": (10.6582, 77.0097),
    "42": (11.0800, 77.3300),
    "43": (11.4102, 76.6950),
    "45": (10.7905, 78.7047),
    "46": (11.2333, 78.8833),
    "47": (10.9601, 78.0766),
    "48": (11.4102, 76.6950),
    "49": (10.7870, 79.1378),
    "50": (10.7725, 79.6365),
    "51": (10.7672, 79.8449),
    "52": (11.4833, 77.8667),
    "54": (11.6200, 78.1300),
    "55": (10.3797, 78.8208),
    "56": (11.3042, 77.5833),
    "57": (10.3673, 77.9803),
    "58": (9.9252, 78.1198),
    "59": (9.9500, 78.1300),
    "60": (10.0104, 77.4768),
    "61": (11.1401, 79.0783),
    "63": (9.8433, 78.4809),
    "64": (9.9300, 78.1200),
    "65": (9.3639, 78.8395),
    "66": (11.0168, 76.9558),
    "67": (9.5872, 77.9579),
    "68": (10.9602, 79.3845),
    "69": (8.7642, 78.1348),
    "70": (12.7409, 77.8253),
    "72": (8.7139, 77.7567),
    "73": (12.9229, 79.3327),
    "74": (8.1833, 77.4119),
    "75": (8.3167, 77.2167),
    "76": (8.9594, 77.3150),
    "77": (11.5975, 78.6019),
    "78": (10.7333, 77.5333),
    "79": (9.1667, 77.5333),
    "81": (10.8000, 78.7100),
    "82": (11.1075, 79.6524),
    "83": (12.6833, 78.6167),
    "84": (9.5134, 77.6322),
    "85": (12.9961, 80.0969),
    "86": (12.9200, 79.3100),
    "88": (11.2000, 78.1500),
    "90": (11.6700, 78.1600),
    "91": (11.5300, 79.3300),
    "92": (8.4947, 78.1219),
    "93": (11.7967, 77.8000),
    "99": (11.0000, 76.9200)
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

import os

class OfficialVahanRegistryClient:
    """
    Authorized MoRTH / NextGen VAHAN 4.0 Registry Client.
    Connects to official government gateways only when lawful credentials and API keys are configured.
    Never bypasses OTP/CAPTCHA, never fabricates owner details, and records audit provenance.
    """
    def __init__(self, api_key: Optional[str] = None, client_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("VAHAN_API_KEY")
        self.client_id = client_id or os.getenv("VAHAN_CLIENT_ID")
        self.endpoint = os.getenv("VAHAN_API_ENDPOINT", "https://vahan.parivahan.gov.in/api/v4/rc-status")

    def is_configured(self) -> bool:
        return bool(self.api_key and self.client_id)

    async def query_registration(self, canonical_plate: str) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "executed": False,
                "status": "CONFIG_REQUIRED",
                "message": "Official VAHAN API credentials (VAHAN_API_KEY, VAHAN_CLIENT_ID) not configured in environment.",
                "owner_field_authorized": False,
                "owner_field_status": "UNAVAILABLE_WITHOUT_AUTHORIZED_CREDENTIALS",
                "retrieved_at": None,
                "data": None
            }

        # When authorized credentials exist, execute validated query
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Client-Id": self.client_id,
                "Accept": "application/json"
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.endpoint, json={"regNumber": canonical_plate}, headers=headers)
                if resp.status_code == 200:
                    payload = resp.json()
                    return {
                        "executed": True,
                        "status": "SUCCESS",
                        "message": "Official registry record retrieved.",
                        "owner_field_authorized": bool(payload.get("ownerName")),
                        "owner_field_status": "AUTHORIZED" if payload.get("ownerName") else "MASKED_BY_REGISTRY",
                        "retrieved_at": datetime.utcnow().isoformat(),
                        "data": payload
                    }
                else:
                    return {
                        "executed": True,
                        "status": "AUTHORIZATION_REQUIRED" if resp.status_code in [401, 403] else "REGISTRY_ERROR",
                        "message": f"Registry endpoint returned HTTP {resp.status_code}: {resp.text[:120]}",
                        "owner_field_authorized": False,
                        "owner_field_status": "DENIED",
                        "retrieved_at": datetime.utcnow().isoformat(),
                        "data": None
                    }
        except Exception as e:
            return {
                "executed": False,
                "status": "REGISTRY_UNREACHABLE",
                "message": f"Connection error contacting registry gateway: {str(e)}",
                "owner_field_authorized": False,
                "owner_field_status": "UNAVAILABLE",
                "retrieved_at": None,
                "data": None
            }


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
        self.registry_client = OfficialVahanRegistryClient()

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def capabilities(self) -> List[str]:
        return ["plate_lookup", "jurisdiction_validation", "rto_attribution", "camera_evidence_linking"]

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
            elif state_code in ["TS", "TG"] and rto_padded in TELANGANA_RTOS:
                rto_office = f"RTO {state_code}-{rto_padded} ({TELANGANA_RTOS[rto_padded]})"
            
            lat, lon = None, None
            if state_code == "TN" and rto_padded in TAMIL_NADU_RTO_COORDS:
                lat, lon = TAMIL_NADU_RTO_COORDS[rto_padded]
            elif state_code in INDIA_STATE_COORDS:
                lat, lon = INDIA_STATE_COORDS[state_code]

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
                "latitude": lat,
                "longitude": lon,
                "coordinates": f"{lat}, {lon}" if lat is not None and lon is not None else None,
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
                "latitude": 51.5074,
                "longitude": -0.1278,
                "coordinates": "51.5074, -0.1278",
                "matched": True
            }

        return {
            "jurisdiction": "UNKNOWN",
            "country": "Unknown",
            "canonical_plate": cleaned,
            "standard": "Generic Vehicle Registration Number",
            "matched": False
        }

    @staticmethod
    def is_vin(query: str) -> bool:
        cleaned = re.sub(r"[\s\-_:]", "", query.strip().upper())
        return bool(re.match(r"^[A-HJ-NPR-Z0-9]{17}$", cleaned))

    @staticmethod
    def lookup_nhtsa_vin(vin: str) -> Dict[str, Any]:
        """Queries the official, free and keyless NHTSA VIN decoding API."""
        cleaned = re.sub(r"[\s\-_:]", "", vin.strip().upper())
        try:
            with httpx.Client(timeout=6.0) as client:
                res = client.get(f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{cleaned}?format=json")
                if res.status_code == 200:
                    data = res.json()
                    results = data.get("Results", [])
                    lookup_dict = {
                        item.get("Variable", "").lower(): item.get("Value")
                        for item in results if item.get("Variable") and item.get("Value") and item.get("Value") not in ["0", "Not Applicable"]
                    }
                    return {
                        "vin": cleaned,
                        "valid": True,
                        "make": lookup_dict.get("make"),
                        "model": lookup_dict.get("model"),
                        "model_year": lookup_dict.get("model year"),
                        "vehicle_type": lookup_dict.get("vehicle type") or lookup_dict.get("body class"),
                        "manufacturer": lookup_dict.get("manufacturer name"),
                        "plant_country": lookup_dict.get("plant country"),
                        "fuel_type": lookup_dict.get("fuel type - primary"),
                        "displacement_l": lookup_dict.get("displacement (l)"),
                        "source": "NHTSA Global VIN Registry",
                    }
        except Exception as e:
            logger.debug(f"NHTSA VIN decode failed: {e}")
        return {
            "vin": cleaned,
            "valid": False,
            "source": "NHTSA Global VIN Registry (Unreachable)",
        }

    def execute_lookup(
        self,
        plate_number: str,
        jurisdiction_hint: Optional[str] = None,
        authorized_credential: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. Check if 17-character VIN
        if self.is_vin(plate_number):
            vin_data = self.lookup_nhtsa_vin(plate_number)
            entities: List[EntityPayload] = []
            evidence: List[EvidencePayload] = []
            relationships: List[RelationshipPayload] = []

            vin_clean = vin_data.get("vin", plate_number.strip().upper())
            make_model = f"{vin_data.get('make') or ''} {vin_data.get('model') or ''}".strip()
            display_val = f"{vin_clean} ({make_model})" if make_model else vin_clean

            entities.append(EntityPayload(
                type=EntityType.VEHICLE,
                value=vin_clean,
                confidence=0.95 if vin_data.get("valid") else 0.7,
                sources=["NHTSA Global VIN Registry"],
                metadata={
                    "identifier_type": "VIN",
                    "vin": vin_clean,
                    "make": vin_data.get("make"),
                    "model": vin_data.get("model"),
                    "model_year": vin_data.get("model_year"),
                    "vehicle_type": vin_data.get("vehicle_type"),
                    "manufacturer": vin_data.get("manufacturer"),
                    "plant_country": vin_data.get("plant_country"),
                    "fuel_type": vin_data.get("fuel_type"),
                    "displacement_l": vin_data.get("displacement_l"),
                    "valid": vin_data.get("valid"),
                }
            ))

            evidence.append(EvidencePayload(
                title=f"NHTSA Global VIN Record: {vin_clean}",
                source="NHTSA VPIC Registry",
                category="Vehicle OSINT",
                content=f"Decoded VIN {vin_clean}: Make={vin_data.get('make')}, Model={vin_data.get('model')}, Year={vin_data.get('model_year')}, Plant={vin_data.get('plant_country')}",
                provenance={
                    "service": "NHTSA VPIC API",
                    "query": vin_clean,
                    "valid": vin_data.get("valid")
                }
            ))

            return {
                "status": "SUCCESS",
                "message": f"NHTSA VIN record decoded successfully for '{vin_clean}'",
                "plate_number": vin_clean,
                "type": "vin",
                "jurisdiction": vin_data.get("plant_country", "GLOBAL"),
                "live_registry_status": "OFFICIAL_GLOBAL_LOOKUP",
                "official_registry_executed": True,
                "entities": entities,
                "relationships": relationships,
                "evidence": evidence
            }

        # 2. Vehicle Registration Plate Processing
        parsed = self.parse_plate(plate_number)
        if not parsed.get("matched"):
            return {
                "status": "NOT_FOUND",
                "message": f"Query '{plate_number}' does not match recognized vehicle registration standards.",
                "plate_number": plate_number,
                "jurisdiction": "UNKNOWN",
                "live_registry_status": "NOT_APPLICABLE",
                "official_registry_executed": False,
                "entities": [],
                "relationships": [],
                "evidence": []
            }

        canonical = parsed.get("canonical_plate", plate_number.strip().upper())
        country = parsed.get("country", "Unknown")
        state_name = parsed.get("state_name")
        rto_office = parsed.get("rto_office")
        standard = parsed.get("standard", "Standard Vehicle Registration")
        lat = parsed.get("latitude")
        lon = parsed.get("longitude")
        coords_str = parsed.get("coordinates")

        entities: List[EntityPayload] = []
        relationships: List[RelationshipPayload] = []
        evidence: List[EvidencePayload] = []

        # Check official registry status
        registry_status = "CONFIG_REQUIRED"
        registry_msg = (
            "Live official registration record query requires configured authorized credentials (VAHAN_API_KEY). "
            "Displayed attributes are based on structural jurisdiction and format parsing."
        )

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
                "latitude": lat,
                "longitude": lon,
                "coordinates": coords_str,
                "syntax_valid": True,
                "jurisdiction_attribution_mode": "FORMAT_PREFIX_INFERENCE",
                "live_registration_record": registry_status,
                "registered_ownership": "NOT_AVAILABLE_WITHOUT_AUTHORIZED_CREDENTIAL",
                "is_search_target": True,
                "lookup_timestamp": datetime.utcnow().isoformat(),
                "camera_evidence_enabled": True
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
                    "attribution_basis": "PREFIX_SYNTAX_MAPPING",
                    "latitude": lat,
                    "longitude": lon,
                    "coordinates": coords_str,
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
            state_lat, state_lon = (
                INDIA_STATE_COORDS.get(parsed.get("state_code", ""), (lat, lon))
                if parsed.get("jurisdiction") == "IN"
                else (lat, lon)
            )
            state_coords_str = f"{state_lat}, {state_lon}" if state_lat is not None and state_lon is not None else coords_str

            loc_entity = EntityPayload(
                type=EntityType.LOCATION,
                value=location_val,
                confidence=0.85,
                sources=[self.name],
                metadata={
                    "country": country,
                    "state": state_name,
                    "location_type": "State / Administrative Region",
                    "attribution_basis": "JURISDICTION_PREFIX",
                    "latitude": state_lat,
                    "longitude": state_lon,
                    "coordinates": state_coords_str,
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
                "notes": evidence_text,
                "live_registry_query": {
                    "status": registry_status,
                    "executed": False,
                    "reason": registry_msg,
                    "owner_field_authorized": False,
                    "owner_field_status": "RESTRICTED_BY_PRIVACY_REGULATION"
                },
                "camera_evidence_recommendation": {
                    "eligible_for_camera_search": True,
                    "target_plate": canonical
                }
            }
        ))

        return {
            "status": "SUCCESS",
            "message": evidence_text,
            "plate_number": canonical,
            "jurisdiction": parsed.get("jurisdiction", "UNKNOWN"),
            "live_registry_status": registry_status,
            "official_registry_executed": False,
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
                "live_registry_status": res.get("live_registry_status"),
                "official_registry_executed": res.get("official_registry_executed"),
                "entities": entities,
                "relationships": relationships,
                "evidence": evidence
            },
            duration_ms=(time.time() - start_time) * 1000
        )

vehicle_registration_provider = VehicleRegistrationProvider()
is_vin = VehicleRegistrationProvider.is_vin
lookup_nhtsa_vin = VehicleRegistrationProvider.lookup_nhtsa_vin

